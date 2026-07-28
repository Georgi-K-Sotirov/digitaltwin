class Diagnostics:
    """
    Анализира остатъчните грешки (Residuals),
    генерирани от ResidualGenerator.
    """

    def __init__(self, parameters=None):

        self.parameters = parameters

    def analyze(self, real_data, residuals):

        alarms = []

        rpm = residuals.get("rpm_residual")
        current = residuals.get("current_residual")
        temperature = residuals.get("temperature_residual")

        if rpm is not None and abs(rpm) > 10:
            alarms.append("RPM deviation")

        if current is not None and abs(current) > 1.0:
            alarms.append("Current deviation")

        if temperature is not None and abs(temperature) > 5:
            alarms.append("Temperature deviation")

        if real_data["temperature"] > 70:
            alarms.append("High temperature")

        if real_data["current"] > 12:
            alarms.append("Motor overload")

        if len(alarms) == 0:
            status = "Normal"

        elif len(alarms) <= 2:
            status = "Warning"

        else:
            status = "Fault"

        return {

            "status": status,

            "alarms": alarms
        }