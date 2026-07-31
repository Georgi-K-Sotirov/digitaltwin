from dataclasses import dataclass


@dataclass
class MotorState:

    time: float

    speed_rpm: float

    torque_nm: float

    active_power_kw: float

    load_torque: float

    ia: float
    ib: float
    ic: float