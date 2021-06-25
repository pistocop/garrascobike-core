from abc import ABCMeta
from abc import abstractmethod

from managers.data_manager import DataManager


class MLInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def preprocess(self, dm: DataManager) -> DataManager: raise NotImplementedError

    @abstractmethod
    def train(self, dm: DataManager) -> str: raise NotImplementedError

    @abstractmethod
    def store_model(self, output_path: str) -> None: raise NotImplementedError
