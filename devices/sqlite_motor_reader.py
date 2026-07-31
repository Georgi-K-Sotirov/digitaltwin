import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class SQLiteMotorReader:
    """
    Чете последното моментно състояние на двигателя,
    записано от Simulink в таблицата motor_state.
    """

    def __init__(
        self,
        db_path: str | Path = r"E:\Десертация\data\digital_twin.db",
        max_load_torque_nm: float = 50.0,
    ):
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

    def update(self) -> dict[str, Any] | None:
        """
        Връща последните данни във формат,
        съвместим с MotorState.from_dict().
        """

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                SELECT
                    timestamp,
                    simulation_time,
                    speed_rpm,
                    current_rms_a,
                    voltage_v,
                    frequency_hz,
                    torque_nm,
                    load_torque_nm,
                    temperature_c,
                    active_power_kw,
                    efficiency,
                    health_percent
                FROM motor_state
                WHERE id = 1
                """
            )

            row = cursor.fetchone()

        except sqlite3.OperationalError as error:
            print(f"Грешка при четене от SQLite: {error}")
            return None

        if row is None:
            return None

        load_percent = self._calculate_load_percent(
            row["load_torque_nm"]
        )

        return {
            "timestamp": self._read_timestamp(row["timestamp"]),
            "simulation_time": self._to_float(
                row["simulation_time"]
            ),
            "rpm": self._to_float(row["speed_rpm"]),
            "current": self._to_float(row["current_rms_a"]),
            "voltage": self._to_float(row["voltage_v"]),
            "frequency": self._to_float(row["frequency_hz"]),
            "torque": self._to_float(row["torque_nm"]),
            "temperature": self._to_float(
                row["temperature_c"]
            ),
            "power": self._to_float(row["active_power_kw"]),
            "efficiency": self._normalize_efficiency(
                row["efficiency"]
            ),
            "load_percent": load_percent,
            "health_percent": self._to_float(
                row["health_percent"]
            ),
            "source": "Simulink",
        }

    def _calculate_load_percent(self, load_torque_nm: Any) -> float:
        load_torque = self._to_float(load_torque_nm)

        if self.max_load_torque_nm <= 0:
            return 0.0

        load_percent = (
            load_torque / self.max_load_torque_nm
        ) * 100.0

        return max(0.0, min(load_percent, 100.0))

    @staticmethod
    def _normalize_efficiency(value: Any) -> float:
        """
        В Python приложението ефективността се използва
        като число между 0 и 1.

        При стойност 92 от Simulink я превръща в 0.92.
        При стойност 0.92 я оставя без промяна.
        """
        efficiency = SQLiteMotorReader._to_float(value)

        if efficiency > 1.0:
            efficiency /= 100.0

        return max(0.0, min(efficiency, 1.0))

    @staticmethod
    def _read_timestamp(value: Any) -> datetime:
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
        """
        Засега натоварването се управлява от Simulink.
        """
        pass

    def decrease_load(self) -> None:
        """
        Засега натоварването се управлява от Simulink.
        """
        pass

    def set_fault(self, fault: Any) -> None:
        """
        Fault Injection от стария MotorSimulator
        временно не се използва.
        """
        pass

    def close(self) -> None:
        self.connection.close()