import threading
import time

from devices.motor import MotorSimulator
from core.digital_twin import DigitalTwin
from core.diagnostics import Diagnostics
from core.historian import Historian
from core.motor_state import MotorState
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
            # -----------------------------
            # Реални данни
            # -----------------------------
            real_dict = self.motor.update()

            real_state = MotorState.from_dict(
                real_dict,
                source="Simulator"
            )

            # -----------------------------
            # Digital Twin
            # -----------------------------
            twin_dict = self.twin.update(
                real_state.to_dict()
            )

            # -----------------------------
            # Diagnostics
            # -----------------------------
            diagnostic_data = self.diagnostics.analyze(
                real_state.to_dict(),
                twin_dict
            )

            # -----------------------------
            # Historian
            # -----------------------------
            self.historian.add(
                real_state,
                twin_dict,
                diagnostic_data
            )

            # -----------------------------
            # Database
            # -----------------------------
            self.database.save(
                real_state,
                twin_dict
            )

            # -----------------------------
            # Snapshot
            # -----------------------------
            with self.lock:
                self.last_snapshot = {
                    "real": real_state.to_dict(),
                    "twin": twin_dict,
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