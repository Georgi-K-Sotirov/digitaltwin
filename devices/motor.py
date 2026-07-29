import random

from devices.fault_injection import (
    FaultInjectionManager,
    FaultMode,
)


class MotorSimulator:
    """
    Симулатор на трифазен асинхронен двигател.

    По-късно този клас може да бъде заменен със:
    - Simulink модел
    - PLC
    - Modbus устройство
    - реален електродвигател
    """

    def __init__(self):
        self.rated_power_kw = 5.5
        self.rated_voltage_v = 400
        self.frequency_hz = 50
        self.poles = 4

        self.load_percent = 40.0
        self.temperature_c = 30.0

        self.faults = FaultInjectionManager()

    def increase_load(self):
        self.load_percent = min(self.load_percent + 5.0, 100.0)

    def decrease_load(self):
        self.load_percent = max(self.load_percent - 5.0, 0.0)

    def update(self):

        load_ratio = self.load_percent / 100.0

        # -----------------------------------------
        # Основен модел на двигателя
        # -----------------------------------------

        synchronous_speed = 120 * self.frequency_hz / self.poles

        slip = 0.015 + 0.035 * load_ratio
        rpm = synchronous_speed * (1 - slip)

        current_a = 2.2 + 9.5 * load_ratio
        torque_nm = 35.0 * load_ratio

        target_temperature = 25.0 + 50.0 * load_ratio
        self.temperature_c += (
            target_temperature - self.temperature_c
        ) * 0.05

        power_kw = self.rated_power_kw * load_ratio
        efficiency = 0.78 + 0.16 * load_ratio

        voltage = self.rated_voltage_v

        # -----------------------------------------
        # Fault Injection
        # -----------------------------------------

        if self.faults.is_active(FaultMode.MECHANICAL_OVERLOAD):
            torque_nm *= 1.25
            current_a *= 1.20
            rpm -= 20

        if self.faults.is_active(FaultMode.THERMAL_OVERLOAD):
            self.temperature_c += 0.40

        if self.faults.is_active(FaultMode.COOLING_FAILURE):
            self.temperature_c += 0.20

        if self.faults.is_active(FaultMode.VOLTAGE_DROP):
            voltage *= 0.90

        if self.faults.is_active(FaultMode.EFFICIENCY_LOSS):
            efficiency -= 0.08
            efficiency = max(efficiency, 0.50)

        # -----------------------------------------
        # Симулация на измервания
        # -----------------------------------------

        measured_rpm = rpm + random.uniform(-2.0, 2.0)
        measured_current = current_a + random.uniform(-0.15, 0.15)

        if self.faults.is_active(FaultMode.CURRENT_SENSOR_OFFSET):
            measured_current += 2.0

        if self.faults.is_active(FaultMode.RPM_SENSOR_OFFSET):
            measured_rpm += 25

        # -----------------------------------------
        # Резултат
        # -----------------------------------------

        return {
            "rpm": measured_rpm,
            "current": measured_current,
            "torque": torque_nm,
            "temperature": self.temperature_c,
            "voltage": voltage,
            "frequency": self.frequency_hz,
            "power": power_kw,
            "efficiency": efficiency,
            "load_percent": self.load_percent,
        }