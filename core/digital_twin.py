from models.induction_motor import InductionMotorModel


class DigitalTwin:
    """
    Digital Twin Engine.

    Получава реални измервания, използва математическия модел
    и сравнява прогнозните стойности с измерените.
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

        health = 100

        health -= abs(rpm_error) * 0.20
        health -= abs(current_error) * 2
        health -= abs(temperature_error) * 0.15

        health = max(0, min(100, health))

        self.last_prediction = {

            "expected": expected,

            "rpm_error": rpm_error,

            "current_error": current_error,

            "temperature_error": temperature_error,

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