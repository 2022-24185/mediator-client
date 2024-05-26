from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class CollectorSignalManager(QObject, BaseSignalManager):
    data_aggregation_started = pyqtSignal()
    data_aggregation_completed = pyqtSignal(dict)
    request_data_aggregation = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.signals = [
            self.data_aggregation_started,
            self.data_aggregation_completed,
            self.request_data_aggregation
        ]