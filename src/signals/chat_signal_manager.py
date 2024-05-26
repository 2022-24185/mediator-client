from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class ChatSignalManager(QObject, BaseSignalManager):
    request_message_display = pyqtSignal(str)
    chatbot_response_retrieved = pyqtSignal(str)
    chatbot_response_displayed = pyqtSignal(bool)
    request_message_submission = pyqtSignal(str)
    first_message_submitted = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.request_message_display,
            self.chatbot_response_retrieved,
            self.chatbot_response_displayed,
            self.request_message_submission,
            self.first_message_submitted
        ]