from core.fault_models import (
    DetectionResult,
    Fault,
    FaultSeverity,
    FaultType,
)
from core.motor_state import MotorState
from core.residual_state import ResidualState


class FaultIsolation:
    """
    Изолира вероятни класове повреди въз основа на:

        - устойчиво активни residual-и;
        - посоката на residual-а;
        - реалното натоварване;
        - комбинацията между сигналите.

    Не се опитва да диагностицира повреди,
    които не са наблюдаеми с наличните сигнали.
    """

    def __init__(
        self,
        rated_current: float = 12.0,
        overload_warning_ratio: float = 1.05,
        overload_critical_ratio: float = 1.15,
    ):
        if rated_current <= 0:
            raise ValueError(
                "rated_current must be positive."
            )

        self.rated_current = rated_current

        self.overload_warning_ratio = (
            overload_warning_ratio
        )

        self.overload_critical_ratio = (
            overload_critical_ratio
        )

    def isolate(
        self,
        real: MotorState,
        residuals: ResidualState,
        detection: DetectionResult,
    ) -> list[Fault]:

        if not detection.detected:
            return []

        faults: list[Fault] = []

        active = set(detection.active_signals)
        critical = set(detection.critical_signals)

        current_ratio = (
            real.current / self.rated_current
        )

        temperature_residual = (
            residuals.temperature
            if residuals.temperature is not None
            else 0.0
        )

        current_residual = (
            residuals.current
            if residuals.current is not None
            else 0.0
        )

        rpm_residual = (
            residuals.rpm
            if residuals.rpm is not None
            else 0.0
        )

        # -------------------------------------------------
        # Thermal overload
        # -------------------------------------------------

        if (
            current_ratio
            >= self.overload_warning_ratio
            and "temperature" in active
            and temperature_residual > 0
        ):
            severity = FaultSeverity.WARNING

            if (
                current_ratio
                >= self.overload_critical_ratio
                or "temperature" in critical
                or "current" in critical
            ):
                severity = FaultSeverity.CRITICAL

            confidence = 0.75

            if "current" in active:
                confidence += 0.10

            if "power" in active:
                confidence += 0.05

            faults.append(
                Fault(
                    code="FLT-THERMAL-001",
                    fault_type=(
                        FaultType.THERMAL_OVERLOAD
                    ),
                    severity=severity,
                    message=(
                        "Possible thermal overload: "
                        "the motor is operating above its "
                        "rated current and is hotter than "
                        "predicted by the Digital Twin."
                    ),
                    confidence=min(confidence, 0.95),
                    evidence=[
                        (
                            "Current ratio: "
                            f"{current_ratio:.2f}"
                        ),
                        (
                            "Temperature residual: "
                            f"{temperature_residual:.2f} °C"
                        ),
                        "Persistent temperature deviation",
                    ],
                )
            )

        # -------------------------------------------------
        # Cooling degradation
        # -------------------------------------------------

        if (
            "temperature" in active
            and temperature_residual > 0
            and current_ratio
            < self.overload_warning_ratio
        ):
            severity = FaultSeverity.WARNING

            if "temperature" in critical:
                severity = FaultSeverity.CRITICAL

            confidence = 0.78

            if "current" not in active:
                confidence += 0.08

            faults.append(
                Fault(
                    code="FLT-COOLING-001",
                    fault_type=(
                        FaultType.COOLING_DEGRADATION
                    ),
                    severity=severity,
                    message=(
                        "Possible cooling degradation: "
                        "the measured temperature remains "
                        "higher than predicted without a "
                        "corresponding electrical overload."
                    ),
                    confidence=min(confidence, 0.95),
                    evidence=[
                        (
                            "Temperature residual: "
                            f"{temperature_residual:.2f} °C"
                        ),
                        (
                            "Current ratio: "
                            f"{current_ratio:.2f}"
                        ),
                        "No proportional current overload",
                    ],
                )
            )

        # -------------------------------------------------
        # Electrical anomaly
        # -------------------------------------------------

        electrical_signals = {
            "current",
            "voltage",
            "frequency",
            "power",
        }

        active_electrical = (
            electrical_signals.intersection(active)
        )

        if active_electrical:
            severity = FaultSeverity.WARNING

            if electrical_signals.intersection(critical):
                severity = FaultSeverity.CRITICAL

            confidence = min(
                0.55 + 0.10 * len(active_electrical),
                0.90,
            )

            faults.append(
                Fault(
                    code="FLT-ELECTRICAL-001",
                    fault_type=(
                        FaultType.ELECTRICAL_ANOMALY
                    ),
                    severity=severity,
                    message=(
                        "Persistent electrical deviation "
                        "detected relative to the Digital "
                        "Twin prediction."
                    ),
                    confidence=confidence,
                    evidence=[
                        (
                            "Active electrical residuals: "
                            + ", ".join(
                                sorted(active_electrical)
                            )
                        ),
                        (
                            "Current residual: "
                            f"{current_residual:.2f} A"
                        ),
                    ],
                )
            )

        # -------------------------------------------------
        # Speed/load anomaly
        # -------------------------------------------------

        if "rpm" in active:
            severity = FaultSeverity.WARNING

            if "rpm" in critical:
                severity = FaultSeverity.CRITICAL

            evidence = [
                (
                    "RPM residual: "
                    f"{rpm_residual:.2f} rpm"
                ),
                "Persistent speed deviation",
            ]

            confidence = 0.60

            if "torque" in active:
                evidence.append(
                    "Torque deviation is also active"
                )
                confidence += 0.15

            if "power" in active:
                evidence.append(
                    "Power deviation is also active"
                )
                confidence += 0.10

            faults.append(
                Fault(
                    code="FLT-SPEED-001",
                    fault_type=(
                        FaultType.SPEED_LOAD_ANOMALY
                    ),
                    severity=severity,
                    message=(
                        "Persistent speed/load inconsistency "
                        "detected. The available signals are "
                        "not sufficient to identify a specific "
                        "bearing or rotor fault."
                    ),
                    confidence=min(confidence, 0.90),
                    evidence=evidence,
                )
            )

        # -------------------------------------------------
        # Sensor or model inconsistency
        # -------------------------------------------------

        if len(active) == 1:
            only_signal = next(iter(active))

            faults.append(
                Fault(
                    code="FLT-CONSISTENCY-001",
                    fault_type=(
                        FaultType
                        .SENSOR_OR_MODEL_INCONSISTENCY
                    ),
                    severity=FaultSeverity.INFO,
                    message=(
                        "An isolated signal inconsistency "
                        "was detected. This may indicate a "
                        "sensor issue, model mismatch or an "
                        "early local anomaly."
                    ),
                    confidence=0.45,
                    evidence=[
                        (
                            "Only active residual: "
                            f"{only_signal}"
                        )
                    ],
                )
            )

        return faults