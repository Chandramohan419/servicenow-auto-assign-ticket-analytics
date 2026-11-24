import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
input("Press ENTER when login is complete and ticket list is visible...")
conn = sqlite3.connect("servicenow.db")

cursor = conn.cursor()

print("Connected to SQLite database")

# ===================================
# CONFIGURATION
# ===================================

MY_NAME = "Chandramohan"
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
print(type(driver))
print(repr(driver))
driver.get(SERVICENOW_URL)
print(f"Opened ServiceNow URL check: {SERVICENOW_URL}")
print("\nPage title:", driver.title)
print("====================================")
input("Please log in to ServiceNow, open the ticket URL, and press Enter to continue...")

# ======================================
# COUNTERS
# ======================================
total_assigned = 0

# ======================================
# MAIN LOOP
# ======================================

while True:
    scan_assigned = 0
    scan_skipped = 0
    scan_scanned = 0

    try:
            print("\n====================================")
            print(f"Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            if "task_list.do" not in driver.current_url:
                print("WARNING: Not on the queue page. Opening the Task page.")
                driver.get(SERVICENOW_URL)
                time.sleep(7)
                driver.refresh()
                time.sleep(5)

            ticket_links = driver.find_elements(
                By.XPATH, "//table//a[contains(@class,'linked')]"
            )
            print(f"Found {len(ticket_links)} tickets on the page.")

            for i in range(len(ticket_links)):
                try:
                    ticket_links = driver.find_elements(
                                       By.XPATH,
                                       "//table//a[contains(@class,'linked')]"
                                   )
                    print("Opening link:")
                    print(ticket_links[i].text)
                    ticket_links[i].click()
                    time.sleep(2)
                    scan_scanned += 1

                      # ======================================
                      # DEBUG and Read ticket details
                      # ======================================
                    current_url = driver.current_url.lower()
                    print("\n=== TICKET OPENED ===")
                    print(driver.current_url)
                    print(driver.title)
                    print("=====================")
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


                    location_element = driver.find_element(By.ID, "sys_display.sc_task.location")
                    state_element = driver.find_element(By.ID, "sc_task.state")
                    ticket_number_element = driver.find_element(By.ID, "sc_task.number")

                    location = location_element.get_attribute("value")
                    state = state_element.get_attribute("value")
                    ticket_number = ticket_number_element.get_attribute("value")
                    

                    is_valid_state = state.strip() in ("1", "2")
                    is_valid_location = (location.strip().lower()== LOCATION_NAME.strip().lower())


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

                    print(f"DEBUG: Ticket number: {ticket_number}")
                    print(f"DEBUG: Ticket state: {state.strip()}")
                    print(f"DEBUG: Valid state: {is_valid_state}")
                    print(f"Location Raw      : '{location}'")
                    print(f"LOCATION_NAME     : '{LOCATION_NAME}'")
                    print(f"Location Compare  : '{location.strip().lower()}'")
                    print(f"Expected Compare  : '{LOCATION_NAME.strip().lower()}'")
                    print(f"Valid Location    : {is_valid_location}")
                    print(f"DEBUG: Ticket location: {location.strip()}")
                    print(f"DEBUG: Valid location: {is_valid_location}")
                    print("====================================")

                    if not (is_valid_state and is_valid_location):
                        scan_skipped += 1
                        driver.back()
                        time.sleep(2)
                        continue

                    assigned_to = driver.find_element(
                        By.ID, "sys_display.sc_task.assigned_to"
                    )
                    assigned_to_value = assigned_to.get_attribute("value") or ""

                    if assigned_to_value.strip():
                        print(f"Already assigned to {assigned_to_value.strip()}. Skipping.")
                        scan_skipped += 1
                        driver.back()
                        time.sleep(2)
                        continue

                    assignment_group = driver.find_element(
                        By.ID, "sys_display.sc_task.assignment_group"
                    )
                    assignment_group.clear()
                    assignment_group.send_keys(ASSIGNMENT_GROUP)
                    time.sleep(1)

                    ActionChains(driver).double_click(assigned_to).perform()
                    time.sleep(1)
                    assigned_to.clear()
                    assigned_to.send_keys(MY_NAME)
                    time.sleep(2)
                    assigned_to.send_keys(Keys.DOWN)
                    assigned_to.send_keys(Keys.ENTER)
                    time.sleep(2)

                    update_btn = driver.find_element(By.ID, "sysverb_update")
                    update_btn.click()
                    time.sleep(5)

                    scan_assigned += 1
                    total_assigned += 1
                    print(f"Assigned ticket {ticket_number} to {MY_NAME}")

                    with open("Ticket_log.txt", "a", encoding="utf-8") as log_file:
                        log_file.write(
                            f"{datetime.now()} | {ticket_number} | "
                            f"[Assigned to {MY_NAME}]\n"
                        )

                except Exception as ticket_error:
                    print(f"Error while processing ticket: {ticket_error}")
                    try:
                        driver.back()
                        time.sleep(2)
                    except Exception:
                        pass
                    continue

            print(f"Scan complete: scanned={scan_scanned}, assigned={scan_assigned}, skipped={scan_skipped}")
            print(f"Total assigned this session: {total_assigned}")
            print("===================================")
            print (f"Waiting {REFRESH_INTERVAL // 360} min before scan....")
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
         print("\nStopping ServiceNow auto-assignment.")
    except Exception as e:
         
        print(f"Main Loop Error: {e}")
         
        time.sleep(60)


        


           







