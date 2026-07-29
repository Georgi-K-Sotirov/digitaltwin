from core.fault_models import (
    DetectionResult,
    ResidualEvaluationResult,
)


class FaultDetection:
    """
    Открива устойчиви отклонения въз основа на
    нормализираните residual scores.

    Еднократното превишаване не се приема за повреда.
    Необходимо е отклонението да се задържи
    определен брой последователни цикли.
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
        warning_persistence: int = 6,
        critical_persistence: int = 20,
        clear_rate: int = 2,
    ):
        """
        При период 0.5 секунди:

        warning_persistence = 6
            приблизително 3 секунди;

        critical_persistence = 20
            приблизително 10 секунди.
        """

        if warning_persistence < 1:
            raise ValueError(
                "warning_persistence must be positive."
            )

        if critical_persistence < warning_persistence:
            raise ValueError(
                "critical_persistence must be greater than "
                "or equal to warning_persistence."
            )

        if clear_rate < 1:
            raise ValueError(
                "clear_rate must be positive."
            )

        self.warning_persistence = warning_persistence
        self.critical_persistence = critical_persistence
        self.clear_rate = clear_rate

        self.warning_counters = {
            signal: 0
            for signal in self.SIGNALS
        }

        self.critical_counters = {
            signal: 0
            for signal in self.SIGNALS
        }

    def detect(
        self,
        evaluation: ResidualEvaluationResult,
    ) -> DetectionResult:

        if not evaluation.ready:
            return DetectionResult(
                detected=False,
                scores=evaluation.scores,
            )

        active_signals: list[str] = []
        critical_signals: list[str] = []

        for signal in self.SIGNALS:
            is_abnormal = evaluation.abnormal.get(
                signal,
                False,
            )

            is_critical = evaluation.critical.get(
                signal,
                False,
            )

            if is_abnormal:
                self.warning_counters[signal] += 1
            else:
                self.warning_counters[signal] = max(
                    0,
                    self.warning_counters[signal]
                    - self.clear_rate,
                )

            if is_critical:
                self.critical_counters[signal] += 1
            else:
                self.critical_counters[signal] = max(
                    0,
                    self.critical_counters[signal]
                    - self.clear_rate,
                )

            if (
                self.warning_counters[signal]
                >= self.warning_persistence
            ):
                active_signals.append(signal)

            if (
                self.critical_counters[signal]
                >= self.critical_persistence
            ):
                critical_signals.append(signal)

        return DetectionResult(
            detected=bool(active_signals),
            active_signals=active_signals,
            critical_signals=critical_signals,
            scores=evaluation.scores,
        )

    def reset(self) -> None:
        """
        Нулира времевите броячи.
        """

        for signal in self.SIGNALS:
            self.warning_counters[signal] = 0
            self.critical_counters[signal] = 0