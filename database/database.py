import sqlite3
from datetime import datetime

from core.motor_state import MotorState


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
        """
        Записва данните в SQLite.

        Приема както MotorState, така и dict.
        """

        if isinstance(motor_data, MotorState):
            motor = motor_data.to_dict()
        else:
            motor = motor_data

        if isinstance(twin_data, MotorState):
            twin = twin_data.to_dict()
        else:
            twin = twin_data

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

            datetime.now().isoformat(timespec="microseconds"),

            motor["rpm"],

            motor["current"],

            motor["torque"],

            motor["temperature"],

            motor["voltage"],

            motor["frequency"],

            motor["power"],

            motor["efficiency"],

            twin.get("health", 100)

        ))

        self.connection.commit()

    def load_recent_history(self, limit=1000):
        """
        Зарежда последните N измервания от базата.

        Връща списък от речници, сортирани
        от най-старите към най-новите.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
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
            FROM motor_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        history = []

        # обръщаме реда, за да върви времето напред
        for row in reversed(rows):
            history.append({

                "timestamp": row[0],

                "rpm": row[1],

                "current": row[2],

                "torque": row[3],

                "temperature": row[4],

                "voltage": row[5],

                "frequency": row[6],

                "power": row[7],

                "efficiency": row[8],

                "health": row[9]

            })

        return history

    def close(self):

        self.connection.close()