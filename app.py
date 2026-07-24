from core.data_collector import DataCollector


class DigitalTwinApplication:
    """
    Главен клас на приложението.

    Всички данни се събират от DataCollector,
    който работи във фонов thread.
    """

    def __init__(self):

        self.collector = DataCollector()

    def get_snapshot(self):

        return self.collector.get_snapshot()

    def get_history(self):

        return self.collector.get_history()

    def increase_load(self):

        self.collector.increase_load()

    def decrease_load(self):

        self.collector.decrease_load()

    def shutdown(self):

        self.collector.shutdown()