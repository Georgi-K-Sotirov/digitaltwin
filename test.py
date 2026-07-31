import sqlite3

db = r"E:\Десертация\data\digital_twin.db"

conn = sqlite3.connect(db)

cursor = conn.cursor()

cursor.execute("SELECT * FROM motor_state")

row = cursor.fetchone()

print(row)

conn.close()