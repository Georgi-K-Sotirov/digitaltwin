from enum import Enum, auto


class FaultMode(Enum):
    THERMAL_OVERLOAD = auto()
    COOLING_FAILURE = auto()
    VOLTAGE_DROP = auto()
    CURRENT_SENSOR_OFFSET = auto()
    RPM_SENSOR_OFFSET = auto()
    EFFICIENCY_LOSS = auto()
    MECHANICAL_OVERLOAD = auto()


class FaultInjectionManager:

    def __init__(self):
        self.active_faults: set[FaultMode] = set()

    def enable(self, fault: FaultMode):
        self.active_faults.add(fault)

    def disable(self, fault: FaultMode):
        self.active_faults.discard(fault)

    def clear(self):
        self.active_faults.clear()

    def is_active(self, fault: FaultMode) -> bool:
        return fault in self.active_faults