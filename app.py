from devices.motor import MotorSimulator
from core.digital_twin import DigitalTwin
from core.diagnostics import Diagnostics
from database.database import Database
from core.historian import Historian

class DigitalTwinApplication:
    """
    Главен клас на приложението.

    Управлява:
    - източника на данни
    - Digital Twin
    - диагностиката
    - базата данни
    """

    def __init__(self):
        self.motor = MotorSimulator()

        self.twin = DigitalTwin()

        self.diagnostics = Diagnostics()

        self.historian = Historian()

        self.database = Database()


    def update(self):

        real_data = self.motor.update()

        twin_data = self.twin.update(real_data)

        diagnostic_data = self.diagnostics.analyze(
            real_data,
            twin_data
        )

        # Запис в Historian
        self.historian.add(
            real_data,
            twin_data,
            diagnostic_data
        )

        # Запис в базата
        self.database.save(
            real_data,
            twin_data
        )

        return {

            "real": real_data,

            "twin": twin_data,

            "diagnostics": diagnostic_data

        }

    def increase_load(self):

        self.motor.increase_load()

    def decrease_load(self):

        self.motor.decrease_load()

    def get_history(self):

        return self.historian.get_history()

    def shutdown(self):

        self.database.close()