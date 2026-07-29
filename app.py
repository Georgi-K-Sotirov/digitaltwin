from core.data_collector_manager import DataCollectorManager
from devices.fault_injection import FaultMode

class DigitalTwinApplication:
    """
    Главен клас на приложението.

    Всички данни се събират от DataCollector,
    който работи във фонов thread.
    """

    def __init__(self):

        self.collector = DataCollectorManager.get_collector()

    def get_snapshot(self):

        return self.collector.get_snapshot()

    def get_history(self):

        return self.collector.get_history()

    def increase_load(self):

        self.collector.increase_load()

    def decrease_load(self):

        self.collector.decrease_load()

    def set_fault(self, fault: FaultMode | None):
        self.collector.set_fault(fault)

    def shutdown(self):

        self.collector.shutdown()