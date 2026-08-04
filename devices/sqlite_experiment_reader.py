import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class SQLiteExperimentReader:
    """
    Reads recorded experiments from SQLite.

    Workflow:

        list_experiments()

        load_experiment(id)

        next_sample()

    Used by the Offline mode of the Digital Twin platform.
    """

    def __init__(
        self,
        db_path: str | Path = r"E:\Десертация\data\digital_twin.db",
        max_load_torque_nm: float = 50.0,
    ) -> None:

        self.db_path = Path(db_path)
        self.max_load_torque_nm = max_load_torque_nm

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"SQLite database not found: {self.db_path}"
            )

        self.connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.data: list[sqlite3.Row] = []

        self.index = 0

        self.playing = False

        self.speed = 1.0

        self.current_experiment = None

        self.offline_mode = True

        self.start_time = None
        self.pause_time = None
        self.duration = 0.0

    # ----------------------------------------------------------
    # Experiments
    # ----------------------------------------------------------

    def list_experiments(self) -> list[dict]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                experiment_name,
                description,
                created_at,
                duration_s,
                sample_count
            FROM experiments
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # ----------------------------------------------------------

    def experiment_duration(self):

        return self.duration

    def load_experiment(
        self,
        experiment_id: int,
    ) -> int:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *

            FROM raw_motor_data

            WHERE experiment_id = ?

            ORDER BY simulation_time
            """,
            (experiment_id,),
        )

        self.data = cursor.fetchall()
        if self.data:
            self.duration = float(
                self.data[-1]["simulation_time"]
            )
        else:
            self.duration = 0.0

        self.index = 0

        self.playing = False

        self.current_experiment = experiment_id

        return len(self.data)

    # ----------------------------------------------------------

    def update(self) -> dict[str, Any] | None:

        if not self.playing:
            return None

        # Първо проверяваме дали сме стигнали края
        if self.index >= len(self.data):
            self.playing = False
            return None

        elapsed = (
                          time.perf_counter() - self.start_time
                  ) * self.speed

        row = self.data[self.index]

        current_time = self._to_float(
            row["simulation_time"]
        )

        if elapsed < current_time:
            return None

        self.index += 1

        load_torque = self._to_float(
            row["load_torque_nm"]
        )

        load_percent = (
                load_torque
                / self.max_load_torque_nm
                * 100.0
        )

        load_percent = max(
            0.0,
            min(load_percent, 100.0),
        )

        print(
            self.index,
            "/",
            len(self.data)
        )

        return {
            "timestamp": datetime.now(),

            "simulation_time":
                current_time,

            "rpm":
                self._to_float(row["speed_rpm"]),

            "current":
                self._calculate_current(row),

            "torque":
                self._to_float(row["torque_nm"]),

            "power":
                self._to_float(row["active_power_kw"]),

            "temperature":
                self._to_float(row["temperature_c"]),

            "load_percent":
                load_percent,

            "voltage": 380.0,
            "frequency": 50.0,
            "efficiency": 0.92,

            "health":
                self._to_float(row["health_percent"]),

            "source":
                "Offline Experiment",
        }


    # ----------------------------------------------------------

    def reset(self):

        self.index = 0

    # ----------------------------------------------------------

    def finished(self) -> bool:

        return self.index >= len(self.data)

    # ----------------------------------------------------------

    def sample_count(self) -> int:

        return len(self.data)

    def play(self):

        if self.start_time is None:

            self.start_time = time.perf_counter()

        elif self.pause_time is not None:

            pause_duration = (
                    time.perf_counter() - self.pause_time
            )

            self.start_time += pause_duration

            self.pause_time = None

        self.playing = True

    def pause(self):

        self.playing = False

        self.pause_time = time.perf_counter()

    def stop(self):

        self.playing = False

        self.index = 0

        self.start_time = None

        self.pause_time = None

    def seek(self, index: int):

        self.index = max(
            0,
            min(index, len(self.data) - 1)
        )

    def set_speed(self, speed: float):

        self.speed = speed

    def progress(self) -> float:

        if not self.data:
            return 0.0

        return self.index / len(self.data)

    def is_playing(self):

        return self.playing

    # ----------------------------------------------------------

    @staticmethod
    def _calculate_current(row) -> float:

        ia = SQLiteExperimentReader._to_float(row["ia"])
        ib = SQLiteExperimentReader._to_float(row["ib"])
        ic = SQLiteExperimentReader._to_float(row["ic"])

        return ((ia ** 2 + ib ** 2 + ic ** 2) / 3.0) ** 0.5

    # ----------------------------------------------------------

    @staticmethod
    def _to_float(value: Any) -> float:

        try:
            return float(value)

        except (TypeError, ValueError):

            return 0.0

    # ----------------------------------------------------------

    def close(self):

        self.connection.close()