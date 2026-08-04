from core.data_collector import DataCollector


class DataCollectorManager:

    _collector = None

    @classmethod
    def get_collector(cls, reader=None):

        if cls._collector is None:

            cls._collector = DataCollector(reader)

        return cls._collector

    @classmethod
    def reset(cls):

        if cls._collector is not None:

            cls._collector.shutdown()

            cls._collector = None

    @classmethod
    def set_fault(cls, fault):

        collector = cls.get_collector()

        collector.set_fault(fault)

    @classmethod
    def create_collector(cls, reader=None):

        cls.reset()

        cls._collector = DataCollector(reader)

        return cls._collector