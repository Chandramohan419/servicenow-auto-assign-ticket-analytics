import sqlite3

conn = sqlite3.connect("servicenow.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    ticket_number TEXT,
    state TEXT,
    location TEXT,
    assignment_group TEXT,
    captured_at TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")