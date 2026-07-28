from dataclasses import dataclass


@dataclass(frozen=True)
class MotorParameters:
    """
    Номинални и допустими параметри на асинхронния двигател.

    frozen=True не позволява стойностите да бъдат променяни
    случайно по време на работа.
    """

    # Идентификация
    manufacturer: str = "Generic"
    model: str = "Induction Motor"

    # Номинални електрически параметри
    rated_power_kw: float = 7.5
    rated_voltage_v: float = 400.0
    rated_current_a: float = 15.2
    rated_frequency_hz: float = 50.0
    rated_power_factor: float = 0.84
    rated_efficiency: float = 0.91

    # Номинални механични параметри
    rated_speed_rpm: float = 1460.0
    rated_torque_nm: float = 49.0

    # Температурни параметри
    insulation_class: str = "F"
    ambient_temperature_c: float = 25.0
    warning_temperature_c: float = 120.0
    critical_temperature_c: float = 145.0
    max_winding_temperature_c: float = 155.0

    # Допустими отклонения между реалния обект и Digital Twin
    max_current_residual_a: float = 1.5
    max_voltage_residual_v: float = 20.0
    max_speed_residual_rpm: float = 50.0
    max_torque_residual_nm: float = 5.0
    max_temperature_residual_c: float = 5.0
    max_power_residual_kw: float = 0.75
    max_efficiency_residual: float = 0.05

    # Събиране на данни
    sampling_period_s: float = 1.0