from collections import deque
from datetime import datetime


class Historian:
    """
    Съхранява последните N измервания в оперативната памет.
    Използва се за графики в реално време.
    """

    def __init__(self, max_points=300):

        self.max_points = max_points

        self.history = deque(maxlen=max_points)

    def add(self, real_data, twin_data, diagnostics):
        self.history.append({

            "timestamp": datetime.now(),

            "rpm": real_data["rpm"],

            "current": real_data["current"],

            "temperature": real_data["temperature"],

            "torque": real_data["torque"],

            "power": real_data["power"],

            "health": twin_data["health"],

            "status": diagnostics["status"]

        })

    def get_history(self):

        return list(self.history)

    def clear(self):

        self.history.clear()