import sqlite3
import time

DB = r"E:\Десертация\data\digital_twin.db"

last_time = None

while True:

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            recorded_at,
            simulation_time,
            speed_rpm,
            current_rms_a,
            active_power_kw,
            torque_nm,
            load_torque_nm,
            temperature_c,
            health_percent
        FROM motor_state
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row:

        if row[0] != last_time:

            last_time = row[0]

            print("--------------------------------")

            print(f"Time      : {row[0]}")
            print(f"Sim Time  : {row[1]:.2f}")
            print(f"RPM       : {row[2]:.1f}")
            print(f"Current   : {row[3]:.2f} A")
            print(f"Power     : {row[4]:.2f} kW")
            print(f"Torque    : {row[5]:.2f} Nm")
            print(f"Load      : {row[6]:.2f} Nm")
            print(f"Temp      : {row[7]:.2f} °C")
            print(f"Health    : {row[8]:.2f} %")

    time.sleep(0.1)