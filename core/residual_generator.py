from typing import Any


class ResidualGenerator:
    """
    Изчислява остатъчните грешки между измерените стойности
    на двигателя и стойностите, прогнозирани от Digital Twin.

    Residual = measured - predicted
    """

    SIGNALS = (
        "rpm",
        "current",
        "voltage",
        "frequency",
        "torque",
        "temperature",
        "power",
        "efficiency",
    )

    def calculate(
        self,
        measured: dict[str, Any],
        predicted: dict[str, Any],
    ) -> dict[str, float | None]:
        """
        Връща residual за всеки наличен параметър.

        Липсващите или невалидните стойности се връщат като None,
        вместо приложението да прекъсне.
        """

        residuals: dict[str, float | None] = {}

        for signal in self.SIGNALS:
            measured_value = self._to_float(measured.get(signal))
            predicted_value = self._to_float(predicted.get(signal))

            key = f"{signal}_residual"

            if measured_value is None or predicted_value is None:
                residuals[key] = None
                continue

            residuals[key] = measured_value - predicted_value

        return residuals

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None