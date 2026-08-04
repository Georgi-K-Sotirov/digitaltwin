import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class SQLiteMotorReader:
    """
    Чете текущото състояние на двигателя от SQLite базата,
    записвана от MATLAB/Simulink.
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
                f"SQLite базата не е намерена: {self.db_path}"
            )

        self.connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=5.0,
        )
        self.connection.row_factory = sqlite3.Row

        self.offline_mode = False

    def update(self) -> dict[str, Any] | None:
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """
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
                WHERE id = 1
                """
            )

            row = cursor.fetchone()

        except sqlite3.Error as error:
            print(f"Грешка при четене от SQLite: {error}")
            return None

        if row is None:
            return None

        load_torque = self._to_float(row["load_torque_nm"])

        if self.max_load_torque_nm > 0:
            load_percent = (
                load_torque / self.max_load_torque_nm
            ) * 100.0
        else:
            load_percent = 0.0

        load_percent = max(0.0, min(load_percent, 100.0))

        return {
            "timestamp": self._parse_timestamp(
                row["recorded_at"]
            ),
            "simulation_time": self._to_float(
                row["simulation_time"]
            ),
            "rpm": self._to_float(row["speed_rpm"]),
            "current": self._to_float(row["current_rms_a"]),
            "torque": self._to_float(row["torque_nm"]),
            "power": self._to_float(row["active_power_kw"]),
            "temperature": self._to_float(
                row["temperature_c"]
            ),
            "load_percent": load_percent,

            # Временни стойности, докато ги добавим в Simulink:
            "voltage": 380.0,
            "frequency": 50.0,
            "efficiency": 0.92,

            "health": self._to_float(
                row["health_percent"]
            ),
            "source": "Simulink",
        }

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass

        return datetime.now()

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def increase_load(self) -> None:
        pass

    def decrease_load(self) -> None:
        pass

    def set_fault(self, fault: Any) -> None:
        pass

    def close(self) -> None:
        self.connection.close()

    def progress(self):
        return 0.0

    def sample_count(self):
        return 0

    @property
    def index(self):
        return 0