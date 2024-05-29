from PyQt5.QtCore import pyqtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.interfaces.data_models import ReplyData
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.client.client import Client
    from src.client.client import SignalManager
    from src.signals.chat_signal_manager import ChatSignalManager
    from src.signals.mediator_signal_manager import MediatorSignalManager

class ClientSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the Client"""
    def __init__(self, signal_manager : 'SignalManager', client: 'Client'):
        self.client = client
        self.chatbot_signals : 'ChatSignalManager' = signal_manager.chat_signals
        super().__init__(signal_manager, client)

    def connect_signals(self):
        self.chatbot_signals.state_instructions_sent.connect(self.handle_instructions_delivered)

    def handle_instructions_delivered(self):
        logging.info("GUISignalHandler handle instructions delivered")
        self.client.start_background_modules()

