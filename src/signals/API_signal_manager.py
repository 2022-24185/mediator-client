from PyQt5.QtCore import pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class APISignalManager(BaseSignalManager):
    """ Deals with outgoing signals for the Chatbot API """
    chatbot_response_collected = pyqtSignal(str)
    is_ready_to_go = pyqtSignal(bool)
    api_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.chatbot_response_collected,
            self.is_ready_to_go,
            self.api_error
        ]