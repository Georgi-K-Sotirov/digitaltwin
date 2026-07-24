import threading
import time

from devices.motor import MotorSimulator
from core.digital_twin import DigitalTwin
from core.diagnostics import Diagnostics
from core.historian import Historian
from database.database import Database


class DataCollector:
    """
    Фонов събирач на данни.

    Работи постоянно в отделен thread и обновява:
        - Motor Simulator
        - Digital Twin
        - Diagnostics
        - Historian
        - SQLite Database
    """

    def __init__(self):

        self.motor = MotorSimulator()
        self.twin = DigitalTwin()
        self.diagnostics = Diagnostics()
        self.historian = Historian()
        self.database = Database()

        self.last_snapshot = None

        self.running = True

        self.lock = threading.RLock()

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def _run(self):

        while self.running:

            real_data = self.motor.update()

            twin_data = self.twin.update(real_data)

            diagnostic_data = self.diagnostics.analyze(
                real_data,
                twin_data
            )

            self.historian.add(
                real_data,
                twin_data,
                diagnostic_data
            )

            self.database.save(
                real_data,
                twin_data
            )

            with self.lock:

                self.last_snapshot = {
                    "real": real_data,
                    "twin": twin_data,
                    "diagnostics": diagnostic_data
                }

            time.sleep(0.5)

    def get_snapshot(self):

        with self.lock:

            return self.last_snapshot

    def get_history(self):

        return self.historian.get_history()

    def increase_load(self):

        self.motor.increase_load()

    def decrease_load(self):

        self.motor.decrease_load()

    def shutdown(self):

        self.running = False

        if self.thread.is_alive():
            self.thread.join(timeout=2)

        self.database.close()