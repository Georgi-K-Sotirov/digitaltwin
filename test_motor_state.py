from core.motor_state import MotorState


motor_data = {
    "rpm": 1460,
    "current": 12.5,
    "voltage": 400,
    "frequency": 50,
    "torque": 42.0,
    "temperature": 61.5,
    "power": 7.1,
    "efficiency": 0.91,
}

state = MotorState.from_dict(
    motor_data,
    source="Simulator",
)

print(state)
print()
print(state.to_dict())