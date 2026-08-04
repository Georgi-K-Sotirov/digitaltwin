from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class MotorState:
    """
    Унифицирано моментно състояние на двигателя.

    Същата структура ще се използва за:
    - реални/симулирани измервания;
    - прогнозата на Digital Twin;
    - бъдещи източници като MATLAB, PLC или Modbus.
    """

    timestamp: datetime
    simulation_time: float

    rpm: float
    current: float
    voltage: float
    frequency: float
    torque: float
    temperature: float
    power: float
    efficiency: float
    load_percent: float

    source: str = "Unknown"

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразува MotorState в речник.

        Това ни позволява временно да запазим съвместимостта
        с Historian, Database и Dashboard.
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        source: str | None = None,
    ) -> "MotorState":
        """
        Създава MotorState от съществуващ речник.
        """

        raw_timestamp = data.get("timestamp")

        if isinstance(raw_timestamp, datetime):
            timestamp = raw_timestamp
        elif isinstance(raw_timestamp, str):
            try:
                timestamp = datetime.fromisoformat(raw_timestamp)
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        return cls(
            timestamp=timestamp,
            simulation_time=cls._to_float(
                data.get("simulation_time")
            ),
            rpm=cls._to_float(data.get("rpm")),
            current=cls._to_float(data.get("current")),
            voltage=cls._to_float(data.get("voltage")),
            frequency=cls._to_float(data.get("frequency")),
            torque=cls._to_float(data.get("torque")),
            temperature=cls._to_float(data.get("temperature")),
            power=cls._to_float(data.get("power")),
            efficiency=cls._to_float(data.get("efficiency")),
            load_percent=cls._to_float(data.get("load_percent")),
            source=source or str(data.get("source", "Unknown")),
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        """
        Преобразува стойност към float.

        При липсваща или невалидна стойност връща 0.0,
        за да не прекъсва потокът от данни.
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0