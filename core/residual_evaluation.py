import math
from dataclasses import dataclass

from core.fault_models import ResidualEvaluationResult
from core.residual_state import ResidualState


@dataclass
class RunningStatistics:
    """
    Изчислява средна стойност и стандартно отклонение
    онлайн чрез алгоритъма на Welford.
    """

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def update(self, value: float) -> None:
        self.count += 1

        delta = value - self.mean
        self.mean += delta / self.count

        delta2 = value - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 0.0

        return self.m2 / (self.count - 1)

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)


class ResidualEvaluation:
    """
    Оценява residual-ите статистически.

    Вместо фиксирани прагове в rpm, A или °C,
    остатъците се нормализират спрямо поведението
    на системата в нормален режим.
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

    def __init__(
        self,
        warmup_samples: int = 100,
        warning_z_score: float = 3.0,
        critical_z_score: float = 5.0,
        minimum_standard_deviation: float = 0.001,
    ):
        if warmup_samples < 2:
            raise ValueError(
                "warmup_samples must be at least 2."
            )

        if warning_z_score <= 0:
            raise ValueError(
                "warning_z_score must be positive."
            )

        if critical_z_score <= warning_z_score:
            raise ValueError(
                "critical_z_score must be greater "
                "than warning_z_score."
            )

        self.warmup_samples = warmup_samples
        self.warning_z_score = warning_z_score
        self.critical_z_score = critical_z_score

        self.minimum_standard_deviation = (
            minimum_standard_deviation
        )

        self.statistics = {
            signal: RunningStatistics()
            for signal in self.SIGNALS
        }

    def evaluate(
        self,
        residuals: ResidualState,
    ) -> ResidualEvaluationResult:

        scores: dict[str, float | None] = {}
        abnormal: dict[str, bool] = {}
        critical: dict[str, bool] = {}

        all_ready = True

        for signal in self.SIGNALS:
            value = getattr(residuals, signal, None)
            statistics = self.statistics[signal]

            if value is None:
                scores[signal] = None
                abnormal[signal] = False
                critical[signal] = False
                continue

            value = float(value)

            # Обучение на нормалното поведение
            if statistics.count < self.warmup_samples:
                statistics.update(value)

                scores[signal] = 0.0
                abnormal[signal] = False
                critical[signal] = False

                all_ready = False
                continue

            standard_deviation = max(
                statistics.standard_deviation,
                self.minimum_standard_deviation,
            )

            score = (
                value - statistics.mean
            ) / standard_deviation

            scores[signal] = score
            abnormal[signal] = (
                abs(score) >= self.warning_z_score
            )
            critical[signal] = (
                abs(score) >= self.critical_z_score
            )

            # Актуализираме нормалния модел само когато
            # измерването не е силно отклонено.
            #
            # Така повредата не се превръща постепенно
            # в ново "нормално" състояние.
            if abs(score) < self.warning_z_score:
                statistics.update(value)

        return ResidualEvaluationResult(
            scores=scores,
            abnormal=abnormal,
            critical=critical,
            ready=all_ready,
        )