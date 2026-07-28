from models.induction_motor import InductionMotorModel


class DigitalTwin:
    """
    Digital Twin Engine.

    Засега:
    - изчислява очакваните стойности;
    - residuals;
    - health.

    По-късно residuals и health ще бъдат отделени
    в самостоятелни класове.
    """

    def __init__(self):

        self.model = InductionMotorModel()

        self.last_prediction = {}

    def update(self, real_data):

        expected = self.model.predict(real_data["load_percent"])

        rpm_error = real_data["rpm"] - expected["rpm"]

        current_error = real_data["current"] - expected["current"]

        temperature_error = (
            real_data["temperature"]
            - expected["temperature"]
        )

        health = 100.0

        health -= abs(rpm_error) * 0.20
        health -= abs(current_error) * 2.0
        health -= abs(temperature_error) * 0.15

        health = max(0.0, min(100.0, health))

        self.last_prediction = {

            # Измерените стойности
            "rpm": real_data["rpm"],
            "current": real_data["current"],
            "voltage": real_data["voltage"],
            "frequency": real_data["frequency"],
            "torque": real_data["torque"],
            "temperature": real_data["temperature"],
            "power": real_data["power"],
            "efficiency": real_data["efficiency"],
            "load_percent": real_data["load_percent"],

            # Очакваните стойности
            "expected": expected,

            # Residuals
            "rpm_error": rpm_error,
            "current_error": current_error,
            "temperature_error": temperature_error,

            # Health
            "health": health,

            "status": self.get_status(health)

        }

        return self.last_prediction

    @staticmethod
    def get_status(health):

        if health >= 95:
            return "Healthy"

        elif health >= 80:
            return "Warning"

        return "Fault"