from collections import deque
from datetime import datetime

from core.motor_state import MotorState


class Historian:
    """
    Съхранява последните N измервания в оперативната памет.
    Използва се за графики в реално време.
    """

    def __init__(self, max_points=300):

        self.max_points = max_points
        self.history = deque(maxlen=max_points)

    def add(self, real_data, twin_data, diagnostics):
        """
        Приема както MotorState, така и речник (dict).
        """

        if isinstance(real_data, MotorState):
            real = real_data.to_dict()
        else:
            real = real_data

        if isinstance(twin_data, MotorState):
            twin = twin_data.to_dict()
        else:
            twin = twin_data

        self.history.append({

            "timestamp": datetime.now(),

            "rpm": real["rpm"],

            "current": real["current"],

            "temperature": real["temperature"],

            "torque": real["torque"],

            "power": real["power"],

            "health": twin.get("health", 100),

            "status": diagnostics["status"]

        })

    def get_history(self):

        return list(self.history)

    def clear(self):

        self.history.clear()