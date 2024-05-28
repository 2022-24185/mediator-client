from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.client.client import SignalManager
    from src.interfaces.i_system_module import ISystemModule


class BaseSignalHandler(QObject):
    def __init__(self, signal_manager: 'SignalManager', main_class: 'ISystemModule'):
        super().__init__()
        self.signal_manager = signal_manager
        self.main_class = main_class
        self.connect_signals()

    @abstractmethod
    def connect_signals(self):
        pass