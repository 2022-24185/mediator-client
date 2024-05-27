
from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class NetworkSignalManager(QObject, BaseSignalManager):
    """ Deals with outgoing signals for the Chatbot API """
    secret_user_msg_received = pyqtSignal()
    secret_chatbot_msg_received = pyqtSignal(str)
    dialogue_user_msg_received = pyqtSignal()
    dialogue_chatbot_msg_received = pyqtSignal(str)
    first_message_submitted = pyqtSignal()
    chatbot_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.request_message_display,
            self.chatbot_response_retrieved,
            self.chatbot_response_displayed,
            self.request_message_submission,
            self.first_message_submitted
        ]