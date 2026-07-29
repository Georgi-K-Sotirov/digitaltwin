class ResidualGenerator:
    """
    Calculates residuals between
    measured values and Digital Twin predictions.
    """

    def calculate(self, measured, expected):

        residuals = {

            "rpm_error":
                measured["rpm"] - expected["rpm"],

            "current_error":
                measured["current"] - expected["current"],

            "temperature_error":
                measured["temperature"] - expected["temperature"],

            "voltage_error":
                measured["voltage"] - expected["voltage"],

            "frequency_error":
                measured["frequency"] - expected["frequency"],

            "torque_error":
                measured["torque"] - expected["torque"],

            "power_error":
                measured["power"] - expected["power"],

            "efficiency_error":
                measured["efficiency"] - expected["efficiency"],
        }

        return residuals