from models.induction_motor import InductionMotorModel


class DigitalTwin:

    def __init__(self):

        self.model = InductionMotorModel()

    def update(self, real_data):

        self.model.correct(real_data)

        expected = self.model.predict(
            load_percent=real_data["load_percent"],
            voltage=real_data["voltage"],
            frequency=real_data["frequency"],
            ambient_temperature=25.0,
            dt=0.05,
        )

        return expected