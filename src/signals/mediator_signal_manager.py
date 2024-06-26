from PyQt5.QtCore import pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class MediatorSignalManager(BaseSignalManager):
    """Deals with outgoing signals from the Mediator Manager"""
    mediator_requested = pyqtSignal(dict) # load new, pass old data
    mediator_data_requested = pyqtSignal() # fetch data
    public_mediator_msg_ready = pyqtSignal(str) # (msg) send to chatbot
    internal_mediator_msg_ready = pyqtSignal(str) # (msg) send to chatbot
    new_mediator_assigned = pyqtSignal(dict) # (mediator id) 
    mediator_intervention_completed = pyqtSignal(bool) 

    def __init__(self):
        super().__init__()
        self.signals = [
            self.mediator_requested,
            self.mediator_data_requested,
            self.public_mediator_msg_ready,
            self.internal_mediator_msg_ready,
            self.new_mediator_assigned,
            self.mediator_intervention_completed
       ]