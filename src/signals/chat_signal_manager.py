from PyQt5.QtCore import pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class ChatSignalManager(BaseSignalManager):
    """ Deals with outgoing signals for the Chatbot API """
    mediator_msg_received = pyqtSignal(str, bool) 
    secret_chatbot_msg_received = pyqtSignal(dict) #msg as data
    dialogue_user_msg_received = pyqtSignal()
    dialogue_chatbot_msg_received = pyqtSignal(dict) #msg as data
    first_message_submitted = pyqtSignal()
    chatbot_error = pyqtSignal(str)
    is_line_free = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.signals = [
            self.mediator_msg_received,
            self.secret_chatbot_msg_received,
            self.dialogue_user_msg_received,
            self.dialogue_chatbot_msg_received,
            self.first_message_submitted,
            self.chatbot_error, 
            self.is_line_free
        ]