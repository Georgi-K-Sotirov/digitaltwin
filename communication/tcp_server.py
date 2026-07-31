from __future__ import annotations

import math
import socket
import struct
from dataclasses import dataclass

HOST = "127.0.0.1"
PORT = 5000

SUPPORTED_VERSION = 1

# Network byte order:
# 10 IEEE-754 doubles, 80 bytes in total.
STATE_STRUCT = struct.Struct("!10d")


@dataclass(frozen=True, slots=True)
class MotorState:
    protocol_version: int
    sequence_number: int
    simulation_time_s: float
    speed_rpm: float
    active_power_kw: float
    torque_nm: float
    load_torque_nm: float
    ia_a: float
    ib_a: float
    ic_a: float


def recv_exact(
    connection: socket.socket,
    size: int,
) -> bytes | None:
    """
    Receive exactly `size` bytes.

    Returns None when the peer performs an orderly disconnect.
    """
    buffer = bytearray(size)
    view = memoryview(buffer)
    received = 0

    while received < size:
        count = connection.recv_into(view[received:])

        if count == 0:
            return None

        received += count

    return bytes(buffer)


def decode_state(data: bytes) -> MotorState:
    if len(data) != STATE_STRUCT.size:
        raise ValueError(
            f"Incorrect record size: {len(data)} bytes; "
            f"expected {STATE_STRUCT.size}"
        )

    (
        version,
        sequence,
        simulation_time,
        speed,
        power,
        torque,
        load,
        ia,
        ib,
        ic,
    ) = STATE_STRUCT.unpack(data)

    version_int = int(version)
    sequence_int = int(sequence)

    if version != version_int:
        raise ValueError(
            f"Protocol version is not an integer: {version}"
        )

    if version_int != SUPPORTED_VERSION:
        raise ValueError(
            f"Unsupported protocol version {version_int}; "
            f"expected {SUPPORTED_VERSION}"
        )

    if sequence != sequence_int or sequence_int < 0:
        raise ValueError(
            f"Invalid sequence number: {sequence}"
        )

    numeric_fields = (
        simulation_time,
        speed,
        power,
        torque,
        load,
        ia,
        ib,
        ic,
    )

    if not all(math.isfinite(value) for value in numeric_fields):
        raise ValueError("Record contains NaN or infinity")

    return MotorState(
        protocol_version=version_int,
        sequence_number=sequence_int,
        simulation_time_s=simulation_time,
        speed_rpm=speed,
        active_power_kw=power,
        torque_nm=torque,
        load_torque_nm=load,
        ia_a=ia,
        ib_a=ib,
        ic_a=ic,
    )


class TCPStateServer:
    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
    ) -> None:
        self.host = host
        self.port = port

    def run(self) -> None:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as server:
            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server.bind((self.host, self.port))
            server.listen(1)

            print(f"Listening on {self.host}:{self.port}")
            print(
                f"State record size: "
                f"{STATE_STRUCT.size} bytes"
            )

            while True:
                connection, address = server.accept()

                with connection:
                    print(f"Connected: {address}")

                    previous_sequence: int | None = None

                    while True:
                        raw = recv_exact(
                            connection,
                            STATE_STRUCT.size,
                        )

                        if raw is None:
                            print("Client disconnected")
                            break

                        try:
                            state = decode_state(raw)
                        except ValueError as error:
                            print(f"Protocol error: {error}")
                            break

                        if previous_sequence is not None:
                            expected = previous_sequence + 1

                            if state.sequence_number != expected:
                                print(
                                    "Sequence discontinuity: "
                                    f"expected {expected}, received "
                                    f"{state.sequence_number}"
                                )

                        previous_sequence = state.sequence_number
                        print(state)


if __name__ == "__main__":
    TCPStateServer().run()
