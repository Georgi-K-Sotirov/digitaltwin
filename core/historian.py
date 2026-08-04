from collections import deque
from datetime import datetime

from core.motor_state import MotorState


class Historian:
    """
    Stores recent measurements, Digital Twin predictions,
    residuals and diagnostics for real-time visualization.
    """

    def __init__(self, max_points=1000):

        self.max_points = max_points
        self.history = deque(maxlen=max_points)
        self.unlimited = False

    def add(self, real_data, twin_data, residuals, diagnostics):

        if isinstance(real_data, MotorState):
            real = real_data.to_dict()
        else:
            real = real_data

        if isinstance(twin_data, MotorState):
            twin = twin_data.to_dict()
        else:
            twin = twin_data

        self.history.append({

            "timestamp": datetime.now(),
            "simulation_time": real["simulation_time"],

            # Real measurements
            "rpm": real["rpm"],
            "current": real["current"],
            "temperature": real["temperature"],
            "torque": real["torque"],
            "power": real["power"],
            "voltage": real["voltage"],
            "frequency": real["frequency"],
            "efficiency": real["efficiency"],

            # Twin prediction
            "twin_rpm": twin["rpm"],
            "twin_current": twin["current"],
            "twin_temperature": twin["temperature"],
            "twin_torque": twin["torque"],
            "twin_power": twin["power"],
            "twin_voltage": twin["voltage"],
            "twin_frequency": twin["frequency"],
            "twin_efficiency": twin["efficiency"],

            # Residuals
            "rpm_error": residuals["rpm_error"],
            "current_error": residuals["current_error"],
            "voltage_error": residuals["voltage_error"],
            "frequency_error": residuals["frequency_error"],
            "torque_error": residuals["torque_error"],
            "power_error": residuals["power_error"],
            "efficiency_error": residuals["efficiency_error"],
            "rpm_normalized": residuals["rpm_normalized"],
            "current_normalized": residuals["current_normalized"],

            "torque_normalized":
                residuals["torque_normalized"],

            "power_normalized":
                residuals["power_normalized"],

            "voltage_normalized":
                residuals["voltage_normalized"],

            "frequency_normalized":
                residuals["frequency_normalized"],

            "efficiency_normalized":
                residuals["efficiency_normalized"],

            "diagnostic_index":
                diagnostics["diagnostic_index"],

            # Diagnostics
            "health": diagnostics["health"],
            "status": diagnostics["status"],
            "faults": diagnostics["faults"]



        })

    def load_history(self, history):

        self.history.clear()

        for item in history:

            self.history.append(item)

    def get_history(self):

        return list(self.history)

    def clear(self):

        self.history.clear()

    def set_unlimited(self, enabled: bool):

        self.unlimited = enabled

        if enabled and isinstance(self.history, deque):

            self.history = list(self.history)

        elif (not enabled) and isinstance(self.history, list):

            self.history = deque(
                self.history[-self.max_points:],
                maxlen=self.max_points
            )