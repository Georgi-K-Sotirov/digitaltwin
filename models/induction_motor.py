class InductionMotorModel:
    """
    Математически модел на трифазен асинхронен двигател.
    Използва се от Digital Twin Engine за прогнозиране
    на очакваното състояние на двигателя.
    """

    def __init__(self,
                 rated_power_kw=5.5,
                 rated_voltage=400,
                 frequency=50,
                 poles=4):

        self.rated_power_kw = rated_power_kw
        self.rated_voltage = rated_voltage
        self.frequency = frequency
        self.poles = poles

    def predict(self, load_percent):

        load = load_percent / 100

        synchronous_speed = 120 * self.frequency / self.poles

        slip = 0.015 + 0.035 * load

        rpm = synchronous_speed * (1 - slip)

        current = 2.2 + 9.5 * load

        temperature = 25 + 50 * load

        power = self.rated_power_kw * load

        efficiency = 0.78 + 0.16 * load

        torque = 35 * load

        return {
            "rpm": rpm,
            "current": current,
            "temperature": temperature,
            "power": power,
            "efficiency": efficiency,
            "torque": torque,
            "voltage": self.rated_voltage,
            "frequency": self.frequency
        }