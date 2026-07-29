from core.models.electrical_model import MotorElectricalModel

model = MotorElectricalModel()

print("-" * 70)

for load in [0, 10, 25, 50, 75, 100]:

    result = model.find_operating_point(load)

    print(
        f"Load: {load:3d}% | "
        f"RPM: {result['rpm']:.1f} | "
        f"I: {result['current']:.2f} A | "
        f"P: {result['power']:.2f} kW | "
        f"T: {result['torque']:.2f} Nm | "
        f"η: {result['efficiency']*100:.1f}% | "
        f"Slip: {result['slip']:.4f}"
    )

print("-" * 70)