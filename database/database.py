import sqlite3
from datetime import datetime


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            "data/digital_twin.db",
            check_same_thread=False
        )

        self.create_table()

    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motor_history(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT,

                rpm REAL,

                current REAL,

                torque REAL,

                temperature REAL,

                voltage REAL,

                frequency REAL,

                power REAL,

                efficiency REAL,

                health REAL

            )
        """)

        self.connection.commit()

    def save(self, motor_data, twin_data):

        cursor = self.connection.cursor()

        cursor.execute("""

            INSERT INTO motor_history(

                timestamp,

                rpm,

                current,

                torque,

                temperature,

                voltage,

                frequency,

                power,

                efficiency,

                health

            )

            VALUES(?,?,?,?,?,?,?,?,?,?)

        """, (

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            motor_data["rpm"],

            motor_data["current"],

            motor_data["torque"],

            motor_data["temperature"],

            motor_data["voltage"],

            motor_data["frequency"],

            motor_data["power"],

            motor_data["efficiency"],

            twin_data["health"]

        ))

        self.connection.commit()

    def close(self):

        self.connection.close()