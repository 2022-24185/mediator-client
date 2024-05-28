from PyQt5.QtCore import pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class CollectorSignalManager(BaseSignalManager):
    data_aggregation_completed = pyqtSignal(dict)
    data_storage_completed = pyqtSignal(dict)
    data_ready_for_mediator = pyqtSignal(dict)
    new_mediator_fetched = pyqtSignal(dict) # serialized mediator
    collector_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.data_aggregation_completed,
            self.data_storage_completed, 
            self.data_ready_for_mediator,
            self.collector_error
        ]