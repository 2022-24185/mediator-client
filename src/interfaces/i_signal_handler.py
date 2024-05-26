from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject

class BaseSignalHandler(QObject, ABC):
    def __init__(self, signal_manager):
        super().__init__()
        self.signal_manager = signal_manager
        self.connect_signals()

    @abstractmethod
    def connect_signals(self):
        pass