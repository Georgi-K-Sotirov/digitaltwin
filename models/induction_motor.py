import cmath
import math


class InductionMotorModel:
    """
    Physics-based model of a healthy three-phase induction motor.

    Използва:
        - еднофазна заместваща схема;
        - комплексни импеданси;
        - реално приплъзване;
        - електромагнитен момент;
        - механично диференциално уравнение;
        - топлинно диференциално уравнение;
        - числено интегриране по метода на Euler.

    Повреди не се моделират тук.
    Те се добавят само в MotorSimulator.
    """

    def __init__(
        self,

        # Номинални данни
        rated_power_kw=5.5,
        rated_voltage=400.0,
        rated_frequency=50.0,
        poles=4,

        # Параметри на заместващата схема
        stator_resistance=0.90,
        rotor_resistance=1.20,

        stator_leakage_inductance=0.004,
        rotor_leakage_inductance=0.004,
        magnetizing_inductance=0.120,

        core_loss_resistance=250.0,

        # Механични параметри
        inertia=0.08,
        friction_coefficient=0.003,

        # Топлинни параметри
        thermal_capacity=18000.0,
        thermal_resistance=0.035,

        ambient_temperature=25.0,

        # Времева стъпка
        default_dt=0.5,
    ):

        # -----------------------------
        # Номинални параметри
        # -----------------------------

        self.rated_power_kw = rated_power_kw
        self.rated_power_w = rated_power_kw * 1000.0

        self.rated_voltage = rated_voltage
        self.rated_frequency = rated_frequency

        self.poles = poles
        self.pole_pairs = poles / 2.0

        # -----------------------------
        # Електрически параметри
        # -----------------------------

        self.rs = stator_resistance
        self.rr = rotor_resistance

        self.lls = stator_leakage_inductance
        self.llr = rotor_leakage_inductance
        self.lm = magnetizing_inductance

        self.rc = core_loss_resistance

        # -----------------------------
        # Механични параметри
        # -----------------------------

        self.inertia = inertia
        self.friction_coefficient = friction_coefficient

        # -----------------------------
        # Топлинни параметри
        # -----------------------------

        self.thermal_capacity = thermal_capacity
        self.thermal_resistance = thermal_resistance

        self.ambient_temperature = ambient_temperature

        self.default_dt = default_dt

        # -----------------------------
        # Начални състояния
        # -----------------------------

        synchronous_rpm = (
            120.0
            * rated_frequency
            / poles
        )

        initial_rpm = synchronous_rpm * 0.97

        self.omega = (
            initial_rpm
            * 2.0
            * math.pi
            / 60.0
        )

        self.temperature = ambient_temperature

    def correct(self, real_data):
        """
        Синхронизира вътрешното състояние на модела
        с реалното измерено състояние.
        """

        self.omega = (
                real_data["rpm"]
                * 2.0
                * math.pi
                / 60.0
        )

        self.temperature = real_data["temperature"]

    def _calculate_synchronous_speed(
        self,
        frequency
    ):

        electrical_omega = (
            2.0
            * math.pi
            * frequency
        )

        mechanical_omega_sync = (
            electrical_omega
            / self.pole_pairs
        )

        synchronous_rpm = (
            mechanical_omega_sync
            * 60.0
            / (2.0 * math.pi)
        )

        return (
            electrical_omega,
            mechanical_omega_sync,
            synchronous_rpm
        )

    def _calculate_equivalent_circuit(
        self,
        voltage,
        frequency,
        slip
    ):
        """
        Изчислява токове, мощности и момент чрез
        еднофазната заместваща схема на двигателя.
        """

        electrical_omega = (
            2.0
            * math.pi
            * frequency
        )

        phase_voltage = (
            voltage
            / math.sqrt(3.0)
        )

        slip = max(
            0.0001,
            min(slip, 1.0)
        )

        # Реактивни съпротивления
        xls = (
            electrical_omega
            * self.lls
        )

        xlr = (
            electrical_omega
            * self.llr
        )

        xm = (
            electrical_omega
            * self.lm
        )

        # Статорен импеданс
        z_stator = complex(
            self.rs,
            xls
        )

        # Намагнитващ клон
        z_magnetizing_inductance = complex(
            0.0,
            xm
        )

        z_core_loss = complex(
            self.rc,
            0.0
        )

        z_magnetizing = (
            z_core_loss
            * z_magnetizing_inductance
            / (
                z_core_loss
                + z_magnetizing_inductance
            )
        )

        # Роторен клон, приведен към статора
        z_rotor = complex(
            self.rr / slip,
            xlr
        )

        # Паралел на намагнитващия и роторния клон
        z_parallel = (
            z_magnetizing
            * z_rotor
            / (
                z_magnetizing
                + z_rotor
            )
        )

        total_impedance = (
            z_stator
            + z_parallel
        )

        # Статорен ток
        stator_current_complex = (
            phase_voltage
            / total_impedance
        )

        # Напрежение върху паралелния клон
        air_gap_voltage = (
            phase_voltage
            - stator_current_complex
            * z_stator
        )

        # Роторен ток
        rotor_current_complex = (
            air_gap_voltage
            / z_rotor
        )

        # Ток през намагнитващия клон
        magnetizing_current_complex = (
            air_gap_voltage
            / z_magnetizing
        )

        stator_current = abs(
            stator_current_complex
        )

        rotor_current = abs(
            rotor_current_complex
        )

        magnetizing_current = abs(
            magnetizing_current_complex
        )

        # -----------------------------
        # Входна активна мощност
        # -----------------------------

        input_power = (
            3.0
            * (
                phase_voltage
                * stator_current_complex.conjugate()
            ).real
        )

        # -----------------------------
        # Загуби
        # -----------------------------

        stator_copper_losses = (
            3.0
            * stator_current ** 2
            * self.rs
        )

        rotor_copper_losses = (
            3.0
            * rotor_current ** 2
            * self.rr
        )

        core_losses = (
            3.0
            * abs(air_gap_voltage) ** 2
            / self.rc
        )

        # Мощност през въздушната междина
        air_gap_power = (
            3.0
            * rotor_current ** 2
            * self.rr
            / slip
        )

        mechanical_internal_power = (
            air_gap_power
            * (1.0 - slip)
        )

        return {
            "stator_current": stator_current,
            "rotor_current": rotor_current,
            "magnetizing_current": magnetizing_current,

            "input_power": max(
                input_power,
                0.0
            ),

            "air_gap_power": max(
                air_gap_power,
                0.0
            ),

            "mechanical_internal_power":
                max(
                    mechanical_internal_power,
                    0.0
                ),

            "stator_copper_losses":
                max(
                    stator_copper_losses,
                    0.0
                ),

            "rotor_copper_losses":
                max(
                    rotor_copper_losses,
                    0.0
                ),

            "core_losses":
                max(
                    core_losses,
                    0.0
                ),
        }

    def predict(
        self,
        load_percent,
        voltage=None,
        frequency=None,
        ambient_temperature=None,
        dt=None
    ):

        voltage = (
            self.rated_voltage
            if voltage is None
            else float(voltage)
        )

        frequency = (
            self.rated_frequency
            if frequency is None
            else float(frequency)
        )

        ambient_temperature = (
            self.ambient_temperature
            if ambient_temperature is None
            else float(ambient_temperature)
        )

        dt = (
            self.default_dt
            if dt is None
            else max(float(dt), 0.001)
        )

        load_fraction = max(
            0.0,
            min(float(load_percent), 100.0)
        ) / 100.0

        (
            electrical_omega,
            synchronous_omega,
            synchronous_rpm
        ) = self._calculate_synchronous_speed(
            frequency
        )

        # -----------------------------
        # Приплъзване
        #
        # s = (ωsync - ωrotor) / ωsync
        # -----------------------------

        slip = (
            synchronous_omega
            - self.omega
        ) / max(
            synchronous_omega,
            0.001
        )

        slip = max(
            0.0001,
            min(slip, 1.0)
        )

        electrical = (
            self._calculate_equivalent_circuit(
                voltage=voltage,
                frequency=frequency,
                slip=slip
            )
        )

        # -----------------------------
        # Електромагнитен момент
        #
        # Te = Pgap / ωsync
        # -----------------------------

        electromagnetic_torque = (
            electrical["air_gap_power"]
            / max(
                synchronous_omega,
                0.001
            )
        )

        # -----------------------------
        # Номинален момент
        #
        # Tn = Pn / ωn
        # -----------------------------

        nominal_omega = (
            synchronous_omega
            * 0.95
        )

        rated_torque = (
            self.rated_power_w
            / max(
                nominal_omega,
                0.001
            )
        )

        load_torque = (
            rated_torque
            * load_fraction
        )

        friction_torque = (
            self.friction_coefficient
            * self.omega
        )

        # =====================================================
        # МЕХАНИЧНО ДИФЕРЕНЦИАЛНО УРАВНЕНИЕ
        #
        # J dω/dt = Te - TL - Bω
        #
        # dω/dt = (Te - TL - Bω) / J
        # =====================================================

        angular_acceleration = (
            electromagnetic_torque
            - load_torque
            - friction_torque
        ) / self.inertia

        # Числено интегриране:
        #
        # ω(t + dt) = ω(t) + ∫ α dt
        #
        # Euler:
        # ω_new = ω_old + α * dt

        self.omega += (
            angular_acceleration
            * dt
        )

        # Физически граници
        self.omega = max(
            0.0,
            min(
                self.omega,
                synchronous_omega * 0.9999
            )
        )

        rpm = (
            self.omega
            * 60.0
            / (2.0 * math.pi)
        )

        # -----------------------------
        # Изходна механична мощност
        # -----------------------------

        shaft_power = (
            load_torque
            * self.omega
        )

        shaft_power = max(
            shaft_power,
            0.0
        )

        mechanical_losses = (
            friction_torque
            * self.omega
        )

        total_losses = (
            electrical["stator_copper_losses"]
            + electrical["rotor_copper_losses"]
            + electrical["core_losses"]
            + mechanical_losses
        )

        # =====================================================
        # ТОПЛИННО ДИФЕРЕНЦИАЛНО УРАВНЕНИЕ
        #
        # Cth dT/dt =
        # Ploss - (T - Tambient) / Rth
        # =====================================================

        heat_dissipation = (
            self.temperature
            - ambient_temperature
        ) / self.thermal_resistance

        temperature_rate = (
            total_losses
            - heat_dissipation
        ) / self.thermal_capacity

        # Интегриране на температурата:
        #
        # T(t + dt) =
        # T(t) + ∫(dT/dt)dt

        self.temperature += (
            temperature_rate
            * dt
        )

        self.temperature = max(
            ambient_temperature,
            self.temperature
        )

        # -----------------------------
        # Ефективност
        # -----------------------------

        input_power = (
            electrical["input_power"]
        )

        if input_power > 1.0:

            efficiency = (
                shaft_power
                / input_power
            )

        else:

            efficiency = 0.0

        efficiency = max(
            0.0,
            min(efficiency, 1.0)
        )

        # Ново приплъзване след интегрирането
        final_slip = (
            synchronous_omega
            - self.omega
        ) / max(
            synchronous_omega,
            0.001
        )

        final_slip = max(
            0.0,
            min(final_slip, 1.0)
        )

        return {
            "rpm": rpm,

            "current":
                electrical["stator_current"],

            "voltage": voltage,

            "frequency": frequency,

            "torque":
                electromagnetic_torque,

            "load_torque":
                load_torque,

            "temperature":
                self.temperature,

            "power":
                shaft_power / 1000.0,

            "input_power":
                input_power / 1000.0,

            "efficiency":
                efficiency,

            "load_percent":
                load_percent,

            "slip":
                final_slip,

            "synchronous_rpm":
                synchronous_rpm,

            "stator_copper_losses":
                electrical[
                    "stator_copper_losses"
                ],

            "rotor_copper_losses":
                electrical[
                    "rotor_copper_losses"
                ],

            "core_losses":
                electrical[
                    "core_losses"
                ],

            "mechanical_losses":
                mechanical_losses,

            "total_losses":
                total_losses,
        }