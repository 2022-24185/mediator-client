from PyQt5.QtCore import pyQtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.user_interface.workers import SendMessageToChatbotWorker
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from src.chatbot_interface.chatbot import ChatbotInterface
    from src.signals.gui_signal_manager import GUISignalManager
    from src.signals.API_signal_manager import APISignalManager

class ChatSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the Chatbot Interface"""
    def __init__(self, signal_manager, chatbot_interface):
        self.chatbot_interface : 'ChatbotInterface' = chatbot_interface
        self.ui_signals : 'GUISignalManager' = signal_manager.ui_signals
        self.api_signals : 'APISignalManager' = signal_manager.api_signals
        super().__init__(signal_manager)

    def connect_signals(self):
        self.ui_signals.message_submitted.connect(self.handle_message_submission)
        self.api_signals.chatbot_response_retrieved.connect(self.handle_response_retrieved)
        self.api_signals.api_error.connect(self.handle_api_error)

    @pyQtSlot(str)
    def handle_response_retrieved(self, response: str):
        logging.info(f"Received response from chatbot API: {response}")
        self.signal_manager.charbot_response_received.emit(response)

    @pyQtSlot(str, Optional[bool])
    def handle_message_submission(self, message, first = False):
        self.thread = SendMessageToChatbotWorker(message, self.chatbot_interface, self.signal_manager)
        self.thread.start()

    @pyQtSlot(str)
    def handle_api_error(self, error: str):
        logging.error(f"API Error: {error}")