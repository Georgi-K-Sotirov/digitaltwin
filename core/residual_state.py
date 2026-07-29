from dataclasses import dataclass


@dataclass
class ResidualState:
    rpm: float = 0.0
    current: float = 0.0
    temperature: float = 0.0
    voltage: float = 0.0
    frequency: float = 0.0
    torque: float = 0.0
    power: float = 0.0
    efficiency: float = 0.0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            rpm=data.get("rpm_residual", 0.0),
            current=data.get("current_residual", 0.0),
            temperature=data.get("temperature_residual", 0.0),
            voltage=data.get("voltage_residual", 0.0),
            frequency=data.get("frequency_residual", 0.0),
            torque=data.get("torque_residual", 0.0),
            power=data.get("power_residual", 0.0),
            efficiency=data.get("efficiency_residual", 0.0),
        )

    def to_dict(self):
        return {
            "rpm_residual": self.rpm,
            "current_residual": self.current,
            "temperature_residual": self.temperature,
            "voltage_residual": self.voltage,
            "frequency_residual": self.frequency,
            "torque_residual": self.torque,
            "power_residual": self.power,
            "efficiency_residual": self.efficiency,
        }