import json
from pathlib import Path
from statistics import mean, stdev


class CalibrationManager:
    """
    Automatic calibration of Digital Twin diagnostic thresholds.

    The calibration is performed using a reference
    experiment representing healthy machine operation.
    """

    def __init__(
        self,
        filename="data/calibration.json",
    ):

        self.filename = Path(filename)

        self.residual_history = {
            "rpm": [],
            "current": [],
            "torque": [],
            "power": [],
            "voltage": [],
            "frequency": [],
            "efficiency": [],
        }

    # --------------------------------------------------

    def collect(self, residuals):

        self.residual_history["rpm"].append(
            abs(residuals["rpm_error"])
        )

        self.residual_history["current"].append(
            abs(residuals["current_error"])
        )

        self.residual_history["torque"].append(
            abs(residuals["torque_error"])
        )

        self.residual_history["power"].append(
            abs(residuals["power_error"])
        )

        self.residual_history["voltage"].append(
            abs(residuals["voltage_error"])
        )

        self.residual_history["frequency"].append(
            abs(residuals["frequency_error"])
        )

        self.residual_history["efficiency"].append(
            abs(residuals["efficiency_error"])
        )

    # --------------------------------------------------

    def compute_thresholds(self):

        thresholds = {}

        statistics = {}

        for signal, values in self.residual_history.items():

            if len(values) < 2:

                continue

            mu = mean(values)

            sigma = stdev(values)

            threshold = mu + 3 * sigma

            thresholds[signal] = threshold

            statistics[signal] = {

                "mean": mu,

                "std": sigma,

                "threshold": threshold,

                "maximum": max(values),

            }

        return statistics

    # --------------------------------------------------

    def save(self):

        statistics = self.compute_thresholds()

        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.filename,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                statistics,
                f,
                indent=4
            )

        print(
            "Calibration saved:",
            self.filename
        )

    # --------------------------------------------------

    def load(self):

        if not self.filename.exists():

            return None

        with open(
            self.filename,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    # --------------------------------------------------

    def clear(self):

        for key in self.residual_history:

            self.residual_history[key].clear()