class Diagnostics:
    """
    Диагностика на състоянието на електродвигателя.

    Анализира отклоненията между реалните измервания
    и математическия модел.
    """

    def analyze(self, real_data, twin_data):

        alarms = []

        if abs(twin_data["rpm_error"]) > 10:
            alarms.append("RPM deviation")

        if abs(twin_data["current_error"]) > 1.0:
            alarms.append("Current deviation")

        if real_data["temperature"] > 70:
            alarms.append("High temperature")

        if real_data["current"] > 12:
            alarms.append("Motor overload")

        if twin_data["health"] < 80:
            alarms.append("Poor health index")

        if not alarms:
            status = "Normal"

        elif len(alarms) <= 2:
            status = "Warning"

        else:
            status = "Fault"

        return {

            "status": status,

            "alarms": alarms

        }