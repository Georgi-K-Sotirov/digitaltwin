from dataclasses import dataclass, field
from enum import Enum


class FaultSeverity(Enum):
    """
    Ниво на сериозност на откритото състояние.
    """

    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class FaultType(Enum):
    """
    Класове повреди, които могат разумно да бъдат
    идентифицирани с текущите сигнали.
    """

    THERMAL_OVERLOAD = "Thermal overload"
    COOLING_DEGRADATION = "Cooling degradation"
    ELECTRICAL_ANOMALY = "Electrical anomaly"
    SPEED_LOAD_ANOMALY = "Speed/load anomaly"
    SENSOR_OR_MODEL_INCONSISTENCY = "Sensor or model inconsistency"


@dataclass
class Fault:
    """
    Описание на изолирана вероятна повреда.
    """

    code: str
    fault_type: FaultType
    severity: FaultSeverity
    message: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class ResidualEvaluationResult:
    """
    Резултат от статистическата оценка на residual-ите.
    """

    scores: dict[str, float | None]
    abnormal: dict[str, bool]
    critical: dict[str, bool]
    ready: bool


@dataclass
class DetectionResult:
    """
    Резултат от Fault Detection.

    Този клас показва кои сигнали са устойчиво ненормални,
    без още да определя конкретната причина.
    """

    detected: bool
    active_signals: list[str] = field(default_factory=list)
    critical_signals: list[str] = field(default_factory=list)
    scores: dict[str, float | None] = field(default_factory=dict)


@dataclass
class DiagnosticResult:
    """
    Краен резултат от диагностичната система.
    """

    status: str
    alarms: list[str] = field(default_factory=list)
    model_alarms: list[str] = field(default_factory=list)
    system_alarms: list[str] = field(default_factory=list)
    faults: list[Fault] = field(default_factory=list)
    residual_scores: dict[str, float | None] = field(default_factory=dict)