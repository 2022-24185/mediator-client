from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class MediatorSignalManager(QObject, BaseSignalManager):
    mediator_data_received = pyqtSignal(str)
    request_mediator_processing = pyqtSignal(str)
    request_data_for_mediator = pyqtSignal()
    request_mediator_message_submission = pyqtSignal(str, bool)
    request_mediator_intervention = pyqtSignal()
    new_mediator_assigned = pyqtSignal(int)
    mediator_processing_completed = pyqtSignal(str, bool)
    mediator_intervention_completed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.mediator_data_received,
            self.request_mediator_processing,
            self.request_data_for_mediator,
            self.request_mediator_message_submission,
            self.request_mediator_intervention,
            self.new_mediator_assigned,
            self.mediator_processing_completed,
            self.mediator_intervention_completed
       ]