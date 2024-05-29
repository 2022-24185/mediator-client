from PyQt5.QtCore import pyqtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.user_interface.workers import SendMessageToChatbotWorker
from typing import TYPE_CHECKING, Optional
from src.signals.chat_signal_manager import MessageType, ChatbotState
import logging

if TYPE_CHECKING:
    from src.chatbot_interface.chatbot import ChatbotInterface
    from src.signals.gui_signal_manager import GUISignalManager
    from src.signals.API_signal_manager import APISignalManager
    from src.signals.chat_signal_manager import ChatSignalManager
    from src.signals.mediator_signal_manager import MediatorSignalManager

class ChatSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the Chatbot Interface"""
    def __init__(self, signal_manager, chatbot_interface):
        self.chatbot_interface : 'ChatbotInterface' = chatbot_interface
        self.chat_signals : 'ChatSignalManager' = signal_manager.chat_signals
        self.gui_signals : 'GUISignalManager' = signal_manager.gui_signals
        self.api_signals : 'APISignalManager' = signal_manager.api_signals
        self.mediator_signals : 'MediatorSignalManager' = signal_manager.mediator_signals
        self.worker = None
        super().__init__(signal_manager, chatbot_interface)

    def connect_signals(self):
        self.gui_signals.message_submitted.connect(self.handle_message_submission)
        self.api_signals.chatbot_response_collected.connect(self.handle_response_retrieved)
        self.api_signals.api_error.connect(self.handle_api_error)
        self.mediator_signals.public_mediator_msg_ready.connect(self.handle_public_mediator_message)
        self.mediator_signals.internal_mediator_msg_ready.connect(self.handle_internal_mediator_message) 

    @pyqtSlot(str)
    def handle_response_retrieved(self, response: str):
        logging.info("\033[90mChatsignalHandler handle response received\033[0m")
        logging.info(f"Response received: {response}"[:50])
        self.chatbot_interface.process_response(response)

    @pyqtSlot(str)
    def handle_message_submission(self, message):
        logging.info(f"Message submitted: {message}"[:50])
        logging.info("\033[90mChatsignalHandler handle message submission\033[0m")
        self.chatbot_interface.start_message_queueing_thread(message, MessageType.USER)

    @pyqtSlot(str)
    def handle_api_error(self, error: str):
        logging.error(f"API Error: {error}")
        self.chatbot_interface.state_manager.update_state(ChatbotState.ERROR)

    def handle_public_mediator_message(self, message):
        logging.info("\033[90mChatsignalHandler handle mediator message\033[0m")
        logging.info(f"TODO: Mediator message received: {message}"[:50])
        self.chatbot_interface.start_message_queueing_thread(message, MessageType.MEDIATOR_PUBLIC)
        #self.chatbot_interface.send_message(message)

    def handle_internal_mediator_message(self, message):
        logging.info("\033[90mChatsignalHandler handle internal mediator message\033[0m")
        logging.info(f"TODO: Internal mediator message received: {message}"[:50])
        self.chatbot_interface.start_message_queueing_thread(message, MessageType.MEDIATOR_INTERNAL)