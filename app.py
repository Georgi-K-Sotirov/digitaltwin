from core.data_collector_manager import DataCollectorManager
from devices.fault_injection import FaultMode
from devices.sqlite_experiment_reader import SQLiteExperimentReader


class DigitalTwinApplication:
    """
    Главен клас на приложението.

    Поддържа:
        - Live режим
        - Offline режим
    """

    def __init__(self, reader=None):

        self.collector = DataCollectorManager.get_collector(
            reader
        )

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


    def load_experiment(self, experiment_id):
        reader = SQLiteExperimentReader()

        count = reader.load_experiment(
            experiment_id
        )

        self.collector = DataCollectorManager.create_collector(
            reader
        )

        return count

    def play(self):
        self.collector.reader.play()

    def stop(self):
        self.collector.reader.stop()

    def progress(self):
        return self.collector.reader.progress()

    def sample_info(self):
        reader = self.collector.reader

        return (
            reader.index,
            reader.sample_count()
        )

    def list_experiments(self):
        reader = SQLiteExperimentReader()

        experiments = reader.list_experiments()

        reader.close()

        return experiments

    def experiment_duration(self):
        reader = self.collector.reader

        if hasattr(reader, "experiment_duration"):
            return reader.experiment_duration()

        return None