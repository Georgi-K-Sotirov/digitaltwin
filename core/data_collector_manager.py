from core.data_collector import DataCollector


class DataCollectorManager:

    _collector = None

    @classmethod
    def get_collector(cls):

        if cls._collector is None:
            cls._collector = DataCollector()

        return cls._collector

    @classmethod
    def set_fault(cls, fault):

        collector = cls.get_collector()
        collector.set_fault(fault)