from PyQt5.QtCore import pyqtSignal, QObject
from src.interfaces.i_signal_manager import BaseSignalManager
from enum import Enum, auto

class ChatbotState(Enum):
    INITIAL = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    SENDING_INSTRUCTIONS = auto()
    INSTRUCTIONS_SENT = auto()
    READYING_MESSAGE = auto()
    API_BUSY = auto()
    API_READY = auto()
    IDLE = auto()
    ERROR = auto()

class MessageType(Enum):
    USER = "user"
    MEDIATOR_PUBLIC = "mediator_public"
    MEDIATOR_INTERNAL = "mediator_internal"

class ChatSignalManager(BaseSignalManager):
    """ Deals with outgoing signals for the Chatbot API """
    mediator_msg_received = pyqtSignal(str, bool) 
    internal_chatbot_msg_received = pyqtSignal(dict) #msg as data
    dialogue_user_msg_received = pyqtSignal(dict)
    public_chatbot_msg_received = pyqtSignal(dict) #msg as data
    first_message_submitted = pyqtSignal()
    chatbot_error = pyqtSignal(str)
    is_line_free = pyqtSignal(bool)

    state_initial = pyqtSignal()
    state_connecting = pyqtSignal()
    state_connected = pyqtSignal()
    state_sending_instructions = pyqtSignal()
    state_instructions_sent = pyqtSignal()
    state_readying_message = pyqtSignal()
    state_api_busy = pyqtSignal()
    state_api_ready = pyqtSignal()
    state_idle = pyqtSignal()
    state_error = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.signals = [
            self.mediator_msg_received,
            self.internal_chatbot_msg_received,
            self.dialogue_user_msg_received,
            self.public_chatbot_msg_received,
            self.first_message_submitted,
            self.chatbot_error, 
            self.is_line_free
        ]