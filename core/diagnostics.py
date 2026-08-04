class Diagnostics:
    """
    Evaluates normalized residuals and calculates
    machine health and diagnostic status.
    """

    def __init__(self):

        self.weights = {
            "rpm_normalized": 0.25,
            "current_normalized": 0.25,
            "torque_normalized": 0.20,
            "power_normalized": 0.20,
            "voltage_normalized": 0.05,
            "frequency_normalized": 0.03,
            "efficiency_normalized": 0.02,
        }

    def evaluate(self, residuals):

        faults = []

        for name, value in residuals.items():

            if not name.endswith("_normalized"):
                continue

            if value >= 2.0:
                faults.append(
                    f"{name.replace('_normalized', '')} fault"
                )

            elif value >= 1.0:
                faults.append(
                    f"{name.replace('_normalized', '')} warning"
                )

        diagnostic_index = 0.0

        for name, weight in self.weights.items():

            value = residuals.get(name, 0.0)

            diagnostic_index += (
                weight
                * min(value, 1.0)
            )

        health = (
            100.0
            * (
                1.0
                - min(diagnostic_index, 1.0)
            )
        )

        maximum_residual = max(
            residuals.get(name, 0.0)
            for name in self.weights
        )

        if maximum_residual < 1.0:
            status = "Healthy"

        elif maximum_residual < 2.0:
            status = "Warning"

        else:
            status = "Fault"

        return {
            "faults": faults,
            "health": health,
            "status": status,
            "diagnostic_index": diagnostic_index,
        }