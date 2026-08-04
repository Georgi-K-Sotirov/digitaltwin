from core.calibration import CalibrationManager


class ResidualGenerator:
    """
    Calculates absolute and normalized residuals between
    measured values and Digital Twin predictions.
    """

    def __init__(self):
        self.calibration = CalibrationManager()

        self.default_limits = {
            "rpm": 80.0,
            "current": 2.5,
            "torque": 20.0,
            "power": 2.0,
            "voltage": 15.0,
            "frequency": 1.0,
            "efficiency": 0.10,
        }

        self.reference_limits = {}

        self.reload_calibration()

    def reload_calibration(self) -> None:

        calibration_data = self.calibration.load()

        if not calibration_data:
            self.reference_limits = (
                self.default_limits.copy()
            )

            print(
                "Calibration file not found. "
                "Using default thresholds."
            )

            return

        loaded_limits = {}

        for signal, values in calibration_data.items():

            threshold = float(
                values.get("threshold", 0.0)
            )

            if threshold > 0:
                loaded_limits[signal] = threshold

        self.reference_limits = {
            **self.default_limits,
            **loaded_limits,
        }

        print("Calibration thresholds loaded.")

    def calculate(self, measured, expected):

        residuals = {
            "rpm_error":
                measured["rpm"] - expected["rpm"],

            "current_error":
                measured["current"] - expected["current"],

            "torque_error":
                measured["torque"] - expected["torque"],

            "power_error":
                measured["power"] - expected["power"],

            "voltage_error":
                measured["voltage"] - expected["voltage"],

            "frequency_error":
                measured["frequency"] - expected["frequency"],

            "efficiency_error":
                measured["efficiency"] - expected["efficiency"],
        }

        normalized = {
            "rpm_normalized":
                abs(residuals["rpm_error"])
                / self.reference_limits["rpm"],

            "current_normalized":
                abs(residuals["current_error"])
                / self.reference_limits["current"],

            "torque_normalized":
                abs(residuals["torque_error"])
                / self.reference_limits["torque"],

            "power_normalized":
                abs(residuals["power_error"])
                / self.reference_limits["power"],

            "voltage_normalized":
                abs(residuals["voltage_error"])
                / self.reference_limits["voltage"],

            "frequency_normalized":
                abs(residuals["frequency_error"])
                / self.reference_limits["frequency"],

            "efficiency_normalized":
                abs(residuals["efficiency_error"])
                / self.reference_limits["efficiency"],
        }

        return {
            **residuals,
            **normalized,
        }