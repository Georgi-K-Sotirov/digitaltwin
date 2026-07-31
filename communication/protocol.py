import json

from communication.motor_state import MotorState


def decode_packet(packet: str) -> MotorState:

    data = json.loads(packet)

    return MotorState(

        time=data["time"],

        speed_rpm=data["speed_rpm"],

        torque_nm=data["torque_nm"],

        active_power_kw=data["active_power_kw"],

        load_torque=data["load_torque"],

        ia=data["ia"],
        ib=data["ib"],
        ic=data["ic"]
    )