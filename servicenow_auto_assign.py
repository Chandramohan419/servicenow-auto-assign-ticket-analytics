import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import time
input("Press ENTER when login is complete and ticket list is visible...")
conn = sqlite3.connect("servicenow.db")

cursor = conn.cursor()

print("Connected to SQLite database")

# ======================================
# CONFIGURATION
# ======================================

MY_NAME = "Chandramohan"

# Replace with your ServiceNow queue URL
SERVICENOW_URL = "https://servicenow.com"
           

LOCATION_NAME = "Location"
ASSIGNMENT_GROUP = "Site Support"
REFRESH_INTERVAL = 600  # 5 minutes
# ======================================
# OPEN BROWSER
# ======================================

options = Options()

driver = webdriver.Edge(options=options)

driver.maximize_window()
print(type(SERVICENOW_URL))
print(repr(SERVICENOW_URL))
driver.get(SERVICENOW_URL)

print("\n=== PAGE CHECK ===")
print("Expected URL:")
print(SERVICENOW_URL)

print("\nActual URL:")
print(driver.current_url)

print("\nPage Title:")
print(driver.title)
print("==================")

print("Please login to ServiceNow.")
input("Press ENTER when login is complete and ticket list is visible...")

# ======================================
# COUNTERS
# ======================================

total_assigned = 0

# ======================================
# MAIN LOOP
# ======================================

while True:

    scan_assigned = 0
    scan_scanned = 0
    scan_skipped = 0


    try:

        print("\n==================================================")
        print(f"Starting scan at: {datetime.now()}")
        print("==================================================")
        print("\nCurrent URL before refresh:")
        print(driver.current_url)

        if "task_list.do" not in driver.current_url:
          print("WARNING: Not on the queue page!")
          print("Returning to queue...")
          driver.get(SERVICENOW_URL)
          time.sleep(5)


        driver.refresh()

        time.sleep(5)


        ticket_links = driver.find_elements(
            By.XPATH,
            "//table//a[contains(@class,'linked')]"
        )

        print(f"Tickets found in queue: {len(ticket_links)}")

        for i in range(len(ticket_links)):

            try:

                ticket_links = driver.find_elements(
                    By.XPATH,
                    "//table//a[contains(@class,'linked')]"
                )

                print("Opening link:")
                print(ticket_links[i].text)
                ticket_links[i].click()

                time.sleep(3)

                scan_scanned += 1

                # ======================================
                # DEBUG
                # ======================================

                current_url = driver.current_url.lower()

                print("\n=== TICKET OPENED ===")
                print(driver.current_url)
                print(driver.title)
                print("=====================")

                # Skip non-ticket pages
                if (
                    "incident.do" not in current_url
                    and "sc_task.do" not in current_url
                    and "sc_req_item.do" not in current_url
                    and "task.do" not in current_url
                ):
                    print("Not a ticket page. Skipping.")

                    driver.back()
                    time.sleep(2)

                    continue


                # ======================================
                # READ TICKET FIELDS
                # ======================================

        
                location = driver.find_element(
                    By.ID,
                    "sys_display.incident.location"
                ).get_attribute("value")

                state = driver.find_element(
                    By.ID,
                    "incident.state"
                ).get_attribute("value")

                try:
                    ticket_number = driver.find_element(
                        By.ID,
                        "incident.number"
                    ).get_attribute("value")
                except:
                    ticket_number = f"TICKET_{i+1}"

                state_value = state.strip().title()
                location_value = location.strip().title()

                state_value = state.strip()

                is_valid_state = state_value in ["1", "2"]

                is_location_match = (
                    location_value ==
                    LOCATION_NAME.lower().title()
                )
                 #=======================================
                 #insert records to sqllite
                 #=======================================
                                
                cursor.execute("""
                INSERT INTO tickets (
                 ticket_number,
                    state,
                      location,
                          assignment_group,
                     captured_at
                     )
                       VALUES (?, ?, ?, ?, ?)
                          """,
                          (
                         ticket_number,
                          state,
                              location,
                              ASSIGNMENT_GROUP,
                             datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                             )
                            )
                                
                conn.commit()
                cursor.execute(
                        "SELECT COUNT(*) FROM tickets"
                    )

                print(
                        "Rows in DB:",
                        cursor.fetchone()[0]
                    )
                      

                print("\n===== DEBUG =====")
                print(f"URL      : {driver.current_url}")
                print(f"Title    : {driver.title}")
                print(f"State    : {state_value}")
                print(f"Valid State : {is_valid_state}")
                print(f"Location Raw : {location}")
                print(f"Location : {location_value}")
                print(f"is_location_match : {is_location_match}")
                print("=================\n")


                # ======================================
                # CHECK MATCHING CONDITIONS
                # ======================================

                if (is_valid_state and is_location_match):

                    print("Matching ticket found.")

                    # ======================================
                    # CHECK IF ALREADY ASSIGNED 
                    # ======================================

                    assigned_to_value = driver.find_element(
                        By.ID,
                        "sys_display.incident.assigned_to"
                    ).get_attribute("value")

                    if assigned_to_value.strip():

                        print(
                            f"Already assigned to {assigned_to_value}. Skipping."
                        )

                        scan_skipped += 1

                        driver.back()
                        time.sleep(2)
                        print("\nReturned to:")
                        print(driver.current_url)

                        continue

                    # ======================================
                    # ASSIGN GROUP
                    # ======================================

                    assignment_group = driver.find_element(
                        By.ID,
                        "sys_display.incident.assignment_group"
                    )

                    assignment_group.clear()
                    assignment_group.send_keys(ASSIGNMENT_GROUP)

                    time.sleep(1)

                    # ======================================
                    # ASSIGN TO ME
                    # ======================================

                    assigned_to = driver.find_element(
                        By.ID,
                        "sys_display.incident.assigned_to"
                    )
                    assigned_to_value = assigned_to.get_attribute("value")

                    print(f"Assigned To Current Value: '{assigned_to_value}'")

                    # Only assign if blank
                    if assigned_to_value.strip() == "":

                        print("Assigned To is empty. Assigning to me...")

                         # Double-click Assigned To field
                        ActionChains(driver).double_click(assigned_to).perform()
                        time.sleep(1)
                        
                        assigned_to.clear()

                        assigned_to.send_keys(MY_NAME)

                        time.sleep(2)

                         # Select from autocomplete

                        assigned_to.send_keys(Keys.DOWN)
                        assigned_to.send_keys(Keys.ENTER)

                        time.sleep(2)

                        print(
                            "Assigned To After Entry:",
                            assigned_to.get_attribute("value")
                        )

                        #save ticket

                        update_btn = driver.find_element(
                            By.ID,
                            "sysverb_update"
                        )

                        update_btn.click()

                        time.sleep(5)
                        scan_assigned += 1
                        total_assigned += 1

                        print(f"SUCCESS: {ticket_number} assigned to {MY_NAME}")

                    else:

                        print(
                            f"Already assigned to {assigned_to_value}. Skipping."
                        )
                        driver.back()
                        continue

                    # ======================================
                    # LOG SUCCESS
                    # ======================================

                    with open(
                        "ticket_log.txt",
                        "a",
                        encoding="utf-8"
                    ) as log_file:

                        log_file.write(
                            f"{datetime.now()} | "
                            f"{ticket_number} | "
                            f"Assigned to {MY_NAME}\n"
                        )

                else:

                    print("Not a matching ticket.")

                driver.back()

                time.sleep(2)

            except Exception as e:

                print(f"Ticket Error: {e}")

                try:
                    driver.back()
                except:
                    pass

                time.sleep(2)

        # ======================================
        # SUMMARY
        # ======================================

        print("\n================ SCAN SUMMARY ================")
        print(f"Tickets Scanned   : {scan_scanned}")
        print(f"Tickets Assigned  : {scan_assigned}")
        print(f"Tickets Skipped   : {scan_skipped}")
        print(f"Total Assigned    : {total_assigned}")

        if scan_assigned == 0:
            print("No new matching tickets found.")

            with open(
                "debug_page.html",
                "w",
                encoding="utf-8"
            ) as debug_file:
                debug_file.write(driver.page_source)

                debug_file.write(
                    f"{datetime.now()} | "
                    f"No new matching tickets found | "
                    f"Scanned={scan_scanned}\n"
                )

        print("==============================================\n")

        print(
            f"Waiting {REFRESH_INTERVAL // 360} minutes before next scan..."
        )

        time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:

        print("\nScript stopped by user.")

        driver.quit()

        break

    except Exception as e:

        print(f"Main Loop Error: {e}")

        time.sleep(60)