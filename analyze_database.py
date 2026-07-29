import sqlite3

connection = sqlite3.connect("data/digital_twin.db")
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM motor_history")
print("Rows:", cursor.fetchone()[0])

cursor.execute("""
SELECT
    MIN(timestamp),
    MAX(timestamp)
FROM motor_history
""")

print(cursor.fetchone())

connection.close()