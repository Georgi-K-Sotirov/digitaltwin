from pathlib import Path

import cmath
import math


class MotorElectricalModel:
    """
    Steady-state per-phase equivalent-circuit model of a healthy
    three-phase induction motor.

    The model does NOT integrate rotor speed. It calculates a stable
    electrical operating point for a supplied slip value or finds the
    stable motoring slip corresponding to a requested load torque.

    All rotor quantities are referred to the stator.
    """

    def __init__(
        self,
        rated_power_kw: float = 5.5,
        rated_voltage_v: float = 400.0,
        rated_frequency_hz: float = 50.0,
        poles: int = 4,
        connection: str = "star",
        rated_speed_rpm: float = 1440.0,

        # Per-phase equivalent-circuit parameters at rated frequency
        stator_resistance_ohm: float = 0.80,
        rotor_resistance_ohm: float = 0.55,
        stator_leakage_reactance_ohm: float = 1.10,
        rotor_leakage_reactance_ohm: float = 1.10,
        magnetizing_reactance_ohm: float = 25.0,
        core_loss_resistance_ohm: float = 300.0,

        # Approximate mechanical no-load losses at rated speed
        mechanical_loss_w: float = 180.0,
    ) -> None:

        if rated_power_kw <= 0:
            raise ValueError("rated_power_kw must be positive.")

        if rated_voltage_v <= 0:
            raise ValueError("rated_voltage_v must be positive.")

        if rated_frequency_hz <= 0:
            raise ValueError("rated_frequency_hz must be positive.")

        if poles <= 0 or poles % 2 != 0:
            raise ValueError("poles must be a positive even integer.")

        connection = connection.lower().strip()

        if connection not in {"star", "delta"}:
            raise ValueError("connection must be 'star' or 'delta'.")

        self.rated_power_kw = float(rated_power_kw)
        self.rated_power_w = self.rated_power_kw * 1000.0
        self.rated_voltage_v = float(rated_voltage_v)
        self.rated_frequency_hz = float(rated_frequency_hz)
        self.poles = int(poles)
        self.pole_pairs = self.poles // 2
        self.connection = connection
        self.rated_speed_rpm = float(rated_speed_rpm)

        self.rs = float(stator_resistance_ohm)
        self.rr = float(rotor_resistance_ohm)
        self.x1_rated = float(stator_leakage_reactance_ohm)
        self.x2_rated = float(rotor_leakage_reactance_ohm)
        self.xm_rated = float(magnetizing_reactance_ohm)
        self.rc = float(core_loss_resistance_ohm)
        self.mechanical_loss_w = max(float(mechanical_loss_w), 0.0)

        for name, value in {
            "stator_resistance_ohm": self.rs,
            "rotor_resistance_ohm": self.rr,
            "stator_leakage_reactance_ohm": self.x1_rated,
            "rotor_leakage_reactance_ohm": self.x2_rated,
            "magnetizing_reactance_ohm": self.xm_rated,
            "core_loss_resistance_ohm": self.rc,
        }.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive.")

    def synchronous_speed_rpm(
        self,
        frequency_hz: float,
    ) -> float:
        return 120.0 * frequency_hz / self.poles

    def synchronous_speed_rad_s(
        self,
        frequency_hz: float,
    ) -> float:
        return (
            self.synchronous_speed_rpm(frequency_hz)
            * 2.0
            * math.pi
            / 60.0
        )

    def phase_voltage(
        self,
        line_voltage_v: float,
    ) -> float:
        if self.connection == "star":
            return line_voltage_v / math.sqrt(3.0)

        return line_voltage_v

    def line_current(
        self,
        phase_current_a: float,
    ) -> float:
        if self.connection == "star":
            return phase_current_a

        return math.sqrt(3.0) * phase_current_a

    def _frequency_scaled_reactances(
        self,
        frequency_hz: float,
    ) -> tuple[float, float, float]:

        ratio = frequency_hz / self.rated_frequency_hz

        return (
            self.x1_rated * ratio,
            self.x2_rated * ratio,
            self.xm_rated * ratio,
        )

    @staticmethod
    def _parallel(
        z_a: complex,
        z_b: complex,
    ) -> complex:
        denominator = z_a + z_b

        if abs(denominator) < 1e-12:
            raise ZeroDivisionError(
                "Invalid equivalent-circuit parallel impedance."
            )

        return z_a * z_b / denominator

    def calculate(
        self,
        slip: float,
        line_voltage_v: float | None = None,
        frequency_hz: float | None = None,
    ) -> dict:
        """
        Calculate one steady-state operating point.

        Valid for positive motoring slip:
            0 < slip <= 1
        """

        voltage = (
            self.rated_voltage_v
            if line_voltage_v is None
            else float(line_voltage_v)
        )

        frequency = (
            self.rated_frequency_hz
            if frequency_hz is None
            else float(frequency_hz)
        )

        if voltage <= 0:
            raise ValueError("line_voltage_v must be positive.")

        if frequency <= 0:
            raise ValueError("frequency_hz must be positive.")

        slip = float(slip)

        if not 0.0 < slip <= 1.0:
            raise ValueError("For motoring, slip must satisfy 0 < slip <= 1.")

        v_phase = self.phase_voltage(voltage)

        x1, x2, xm = self._frequency_scaled_reactances(
            frequency
        )

        z1 = complex(self.rs, x1)
        z2 = complex(self.rr / slip, x2)

        z_core = complex(self.rc, 0.0)
        z_magnetizing_inductor = complex(0.0, xm)

        z_m = self._parallel(
            z_core,
            z_magnetizing_inductor,
        )

        z_parallel = self._parallel(
            z_m,
            z2,
        )

        z_input = z1 + z_parallel

        i1 = v_phase / z_input
        air_gap_voltage = v_phase - i1 * z1
        i2 = air_gap_voltage / z2
        i_m = air_gap_voltage / z_m

        phase_current_a = abs(i1)
        line_current_a = self.line_current(phase_current_a)
        rotor_current_a = abs(i2)
        magnetizing_current_a = abs(i_m)

        input_complex_power_va = (
            3.0
            * v_phase
            * i1.conjugate()
        )

        input_power_w = max(
            input_complex_power_va.real,
            0.0,
        )

        reactive_power_var = (
            input_complex_power_va.imag
        )

        apparent_power_va = abs(
            input_complex_power_va
        )

        power_factor = (
            input_power_w / apparent_power_va
            if apparent_power_va > 1e-9
            else 0.0
        )

        stator_copper_loss_w = (
            3.0
            * phase_current_a ** 2
            * self.rs
        )

        rotor_copper_loss_w = (
            3.0
            * rotor_current_a ** 2
            * self.rr
        )

        core_loss_w = (
            3.0
            * abs(air_gap_voltage) ** 2
            / self.rc
        )

        air_gap_power_w = (
            3.0
            * rotor_current_a ** 2
            * self.rr
            / slip
        )

        converted_mechanical_power_w = (
            air_gap_power_w
            * (1.0 - slip)
        )

        shaft_power_w = max(
            converted_mechanical_power_w
            - self.mechanical_loss_w,
            0.0,
        )

        omega_sync_rad_s = (
            self.synchronous_speed_rad_s(
                frequency
            )
        )

        electromagnetic_torque_nm = (
            air_gap_power_w
            / omega_sync_rad_s
        )

        synchronous_rpm = (
            self.synchronous_speed_rpm(
                frequency
            )
        )

        rotor_rpm = synchronous_rpm * (1.0 - slip)

        rotor_omega_rad_s = (
            rotor_rpm
            * 2.0
            * math.pi
            / 60.0
        )

        shaft_torque_nm = (
            shaft_power_w / rotor_omega_rad_s
            if rotor_omega_rad_s > 1e-9
            else 0.0
        )

        total_loss_w = max(
            input_power_w - shaft_power_w,
            0.0,
        )

        efficiency = (
            shaft_power_w / input_power_w
            if input_power_w > 1e-9
            else 0.0
        )

        efficiency = max(
            0.0,
            min(efficiency, 1.0),
        )

        return {
            "slip": slip,
            "synchronous_rpm": synchronous_rpm,
            "rpm": rotor_rpm,

            "phase_current": phase_current_a,
            "current": line_current_a,
            "rotor_current": rotor_current_a,
            "magnetizing_current": magnetizing_current_a,

            "voltage": voltage,
            "frequency": frequency,

            "input_power": input_power_w / 1000.0,
            "power": shaft_power_w / 1000.0,
            "reactive_power_kvar": reactive_power_var / 1000.0,
            "apparent_power_kva": apparent_power_va / 1000.0,
            "power_factor": power_factor,
            "efficiency": efficiency,

            "electromagnetic_torque": electromagnetic_torque_nm,
            "torque": shaft_torque_nm,

            "stator_copper_loss": stator_copper_loss_w,
            "rotor_copper_loss": rotor_copper_loss_w,
            "core_loss": core_loss_w,
            "mechanical_loss": self.mechanical_loss_w,
            "total_loss": total_loss_w,
        }

    def rated_torque_nm(self) -> float:
        rated_omega_rad_s = (
            self.rated_speed_rpm
            * 2.0
            * math.pi
            / 60.0
        )

        return (
            self.rated_power_w
            / rated_omega_rad_s
        )

    def find_operating_point(
        self,
        load_percent: float,
        line_voltage_v: float | None = None,
        frequency_hz: float | None = None,
        minimum_slip: float = 0.0005,
        maximum_stable_slip: float = 0.20,
        scan_points: int = 500,
        tolerance_nm: float = 1e-4,
        max_iterations: int = 80,
    ) -> dict:
        """
        Find the low-slip stable motoring operating point where:

            electromagnetic torque = requested load torque
                                   + mechanical-loss torque

        A scan first locates the first sign change on the stable branch.
        Bisection then solves it without oscillating between states.
        """

        load_fraction = max(
            0.0,
            min(float(load_percent), 100.0),
        ) / 100.0

        requested_shaft_torque_nm = (
            self.rated_torque_nm()
            * load_fraction
        )

        voltage = (
            self.rated_voltage_v
            if line_voltage_v is None
            else float(line_voltage_v)
        )

        frequency = (
            self.rated_frequency_hz
            if frequency_hz is None
            else float(frequency_hz)
        )

        omega_sync = self.synchronous_speed_rad_s(
            frequency
        )

        mechanical_loss_torque_nm = (
            self.mechanical_loss_w
            / max(omega_sync, 1e-9)
        )

        required_electromagnetic_torque_nm = (
            requested_shaft_torque_nm
            + mechanical_loss_torque_nm
        )

        minimum_slip = max(
            float(minimum_slip),
            1e-6,
        )

        maximum_stable_slip = min(
            max(float(maximum_stable_slip), minimum_slip),
            0.999,
        )

        scan_points = max(
            int(scan_points),
            20,
        )

        def torque_error(slip_value: float) -> float:
            state = self.calculate(
                slip=slip_value,
                line_voltage_v=voltage,
                frequency_hz=frequency,
            )

            return (
                state["electromagnetic_torque"]
                - required_electromagnetic_torque_nm
            )

        previous_slip = minimum_slip
        previous_error = torque_error(previous_slip)

        bracket = None

        for index in range(1, scan_points + 1):

            fraction = index / scan_points

            current_slip = (
                minimum_slip
                + fraction
                * (
                    maximum_stable_slip
                    - minimum_slip
                )
            )

            current_error = torque_error(
                current_slip
            )

            if previous_error == 0.0:
                bracket = (
                    previous_slip,
                    previous_slip,
                )
                break

            if previous_error * current_error <= 0.0:
                bracket = (
                    previous_slip,
                    current_slip,
                )
                break

            previous_slip = current_slip
            previous_error = current_error

        if bracket is None:
            maximum_state = self.calculate(
                slip=maximum_stable_slip,
                line_voltage_v=voltage,
                frequency_hz=frequency,
            )

            raise RuntimeError(
                "No stable operating point was found. "
                "The requested load may exceed the motor capability "
                f"for {voltage:.1f} V and {frequency:.2f} Hz. "
                "Maximum torque on the searched stable branch is "
                f"approximately "
                f"{maximum_state['electromagnetic_torque']:.2f} Nm."
            )

        lower_slip, upper_slip = bracket

        if lower_slip == upper_slip:
            solved_slip = lower_slip

        else:
            lower_error = torque_error(lower_slip)

            solved_slip = (
                lower_slip
                + upper_slip
            ) / 2.0

            for _ in range(max_iterations):

                solved_slip = (
                    lower_slip
                    + upper_slip
                ) / 2.0

                middle_error = torque_error(
                    solved_slip
                )

                if abs(middle_error) <= tolerance_nm:
                    break

                if lower_error * middle_error <= 0.0:
                    upper_slip = solved_slip
                else:
                    lower_slip = solved_slip
                    lower_error = middle_error

        result = self.calculate(
            slip=solved_slip,
            line_voltage_v=voltage,
            frequency_hz=frequency,
        )

        result["load_percent"] = (
            load_fraction * 100.0
        )

        result["requested_load_torque"] = (
            requested_shaft_torque_nm
        )

        return result


