from models.induction_motor import InductionMotorModel


class DigitalTwin:
    """
    Digital Twin Engine.

    Mathematical model of a healthy induction motor.

    Responsibilities:
        - predict expected behaviour
        - no diagnostics
        - no residual calculation
        - no health estimation
    """

    def __init__(self):

        self.model = InductionMotorModel()

        self.last_prediction = {}

    def update(self, real_data):

        expected = self.model.predict(
            real_data["load_percent"]
        )

        self.last_prediction = expected

        return expected