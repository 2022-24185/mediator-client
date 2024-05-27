from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class APISignalManager(QObject, BaseSignalManager):
    """ Deals with outgoing signals for the Chatbot API """
    chatbot_response_retrieved = pyqtSignal(str)
    api_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.chatbot_response_retrieved,
            self.api_error
        ]