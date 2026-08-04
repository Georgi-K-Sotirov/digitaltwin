import threading
import time

from devices.sqlite_motor_reader import SQLiteMotorReader
from core.digital_twin import DigitalTwin
from core.diagnostics import Diagnostics
from core.historian import Historian
from core.motor_state import MotorState
from database.database import Database
from core.residual_generator import ResidualGenerator
from core.calibration import CalibrationManager

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

    def __init__(self, reader=None):

        if reader is None:
            reader = SQLiteMotorReader()

        self.reader = reader
        self.offline_mode = getattr(reader, "offline_mode", False)
        self.twin = DigitalTwin()
        self.residual_generator = ResidualGenerator()
        self.diagnostics = Diagnostics()
        self.calibration = CalibrationManager()

        self.calibration_mode = False
        self.calibration_completed = False
        self.calibration_statistics = None
        self.historian = Historian()
        if self.offline_mode:

            self.historian.set_unlimited(True)

        else:

            self.historian.set_unlimited(False)
        self.database = Database()

        if not self.offline_mode:
            history = self.database.load_recent_history(
                self.historian.max_points
            )

            self.historian.load_history(history)

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
            real_dict = self.reader.update()

            if real_dict is None:

                if (
                        self.calibration_mode
                        and self.offline_mode
                        and self.reader.finished()
                ):
                    self._finish_calibration()

                time.sleep(0.001)
                continue

            real_state = MotorState.from_dict(
                real_dict,
                source=real_dict.get("source", "Unknown")
            )



            # -----------------------------
            # Digital Twin
            # -----------------------------
            twin_dict = self.twin.update(
                real_state.to_dict()
            )

            residual_state = self.residual_generator.calculate(
                real_state.to_dict(),
                twin_dict
            )

            if self.calibration_mode:
                self.calibration.collect(
                    residual_state
                )

            # -----------------------------
            # Diagnostics
            # -----------------------------
            diagnostic_data = self.diagnostics.evaluate(
                residual_state
            )

            # -----------------------------
            # Historian
            # -----------------------------
            self.historian.add(
                real_state,
                twin_dict,
                residual_state,
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
                    "residuals": residual_state,
                    "diagnostics": diagnostic_data
                }

    def get_snapshot(self):

        with self.lock:

            return self.last_snapshot

    def get_history(self):

        return self.historian.get_history()

    def increase_load(self):

        self.reader.increase_load()

    def decrease_load(self):

        self.reader.decrease_load()

    def set_fault(self, fault):

        self.reader.set_fault(fault)

    def start_calibration(self) -> bool:
        """
        Starts calibration using the currently loaded
        offline experiment.
        """

        if not self.offline_mode:
            return False

        if self.reader.sample_count() == 0:
            return False

        self.calibration.clear()

        self.calibration_mode = True
        self.calibration_completed = False
        self.calibration_statistics = None

        self.historian.clear()

        self.reader.stop()
        self.reader.reset()
        self.reader.play()

        return True

    def _finish_calibration(self) -> None:
        """
        Calculates and stores thresholds after the reference
        experiment has finished.
        """

        if not self.calibration_mode:
            return

        self.calibration_statistics = (
            self.calibration.compute_thresholds()
        )

        self.calibration.save()

        self.calibration_mode = False
        self.calibration_completed = True

        self.residual_generator.reload_calibration()

    def get_calibration_status(self) -> dict:
        return {
            "running": self.calibration_mode,
            "completed": self.calibration_completed,
            "statistics": self.calibration_statistics,
        }

    def shutdown(self):

        self.running = False

        if self.thread.is_alive():
            self.thread.join(timeout=2)

        self.reader.close()
        self.database.close()