from PyQt5.QtCore import pyqtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.interfaces.data_models import ReplyData
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.user_interface.gui import ChatbotGUI
    from src.client.client import SignalManager
    from src.signals.chat_signal_manager import ChatSignalManager
    from src.signals.mediator_signal_manager import MediatorSignalManager

class GUISignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the GUI"""
    def __init__(self, signal_manager : 'SignalManager', gui: 'ChatbotGUI'):
        self.gui = gui
        self.chatbot_signals : 'ChatSignalManager' = signal_manager.chat_signals
        self.mediator_signals : 'MediatorSignalManager' = signal_manager.mediator_signals
        self.worker = None
        super().__init__(signal_manager, gui)

    def connect_signals(self):
        self.chatbot_signals.public_chatbot_msg_received.connect(self.handle_chatbot_msg_received)

    @pyqtSlot(dict)
    def handle_chatbot_msg_received(self, reply_data: dict):
        logging.info(f"GUISignalHandler handle chatbot msg received")
        data = ReplyData.model_validate(reply_data)
        self.gui.display_response(data.last_response)

