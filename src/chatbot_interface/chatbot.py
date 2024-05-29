# src.chatbot_interface.chatbot.py
import logging, time, queue, os
from src.interfaces.i_chatbot_service import IChatbotService
from src.interfaces.data_models import ReplyData, MessageData
from src.chatbot_interface.chat_state_manager import ChatStateManager
from src.backends.backend_setup.discover import get_chrome_version
from src.backends.gemini_base import Bard
from src.backends.backend_setup.openai import ChatGPT
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.workers import AddMessageWorker, MessageQueue, ProcessMessageWorker, ProcessResponseWorker
from src.signals.chat_signal_manager import ChatbotState, MessageType
from PyQt5.QtCore import QThreadPool
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from src.client.client import SignalManager

class ChatbotInterface(ISystemModule, IChatbotService):

    def __init__(self, signal_manager : 'SignalManager'):
        super().__init__()
        self.bard = None
        self.chrome_path = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
        self.signal_manager = signal_manager
        self.signals = signal_manager.chat_signals
        self.state = ChatStateManager(signal_manager)
        self.current_mode = MessageType.MEDIATOR_INTERNAL
        self.thread_pool = QThreadPool()
        self.message_queue = MessageQueue(self)
        
    def initialize(self):
        self.is_running = False
        logging.info("Initializing ChatbotInterface module...")

    def configure(self, config: dict):
        logging.info("Configuring ChatbotInterface module...")

    def start(self):
        logging.info("Starting ChatbotInterface module...")
        self.state.update_state(ChatbotState.CONNECTING)
        self.connect_to_API()
        self.state.update_state(ChatbotState.API_READY)
        self.load_and_send_instructions()
        self.is_running = True

    def connect_to_API(self):
        logging.info("Initializing connection to the chatbot service...")
        try:
            # TODO: add logic for Bard too
            self._initialize_chatgpt()
            self._open_chatgpt_service()
            self._start_new_chat_session()
        except Exception as e:
            logging.error(f"Failed to initialize connection: {e}")
            self.state.update_state(ChatbotState.ERROR)

    def _initialize_chatgpt(self):
        chrome_version = get_chrome_version(path=self.chrome_path)
        self.bard = ChatGPT(self.signal_manager, self.state, path=self.chrome_path, driver_version=chrome_version)
        logging.info("ChatGPT initialized")

    def _open_chatgpt_service(self):
        self.bard.open()
        if not self.state.is_state(ChatbotState.CONNECTED):
            raise ConnectionError("Failed to connect to ChatGPT service.")

    def _start_new_chat_session(self):
        self.bard.new_chat('chat_session')

    def load_and_send_instructions(self):
        instructions = self._load_instructions()
        if instructions:
            self._send_instructions(instructions)

    def _load_instructions(self):
        file_path = os.path.join(os.getcwd(), "src/chatbot_interface/instructions.txt")
        try:
            with open(file_path, "r") as f:
                instructions = f.read()
                if not instructions:
                    logging.info("No instructions found.")
                    return None
                return instructions.replace('"', '\"')
        except FileNotFoundError:
            logging.error("Instructions file not found.")
            self.state.update_state(ChatbotState.ERROR)
            return None

    def _send_instructions(self, instructions):
        logging.info("Sending instructions to Bard chatbot...")
        self.add_message_to_queue(instructions, MessageType.MEDIATOR_INTERNAL)
        self.state.update_state(ChatbotState.SENDING_INSTRUCTIONS)

    def stop(self):
        logging.info("Stopping ChatbotInterface module...")
        self.close_connection()
        self.is_running = False

    def reset(self):
        logging.info("Resetting ChatbotInterface module...")
        self.is_running = False

    def update(self):
        logging.info("Updating ChatbotInterface module...")

    def set_mode(self, mode: MessageType):
        self.current_mode = mode

    def get_mode(self) -> MessageType:
        return self.current_mode

    def close_connection(self):
        logging.info("Closing chatbot connection...")
        if self.bard:
            self.bard.close()
            self.state.update_state(ChatbotState.INITIAL)
        else:
            logging.info("Chatbot connection is already closed or was never established.")

    def add_message_to_queue(self, message, message_type: MessageType) -> str:
        worker = AddMessageWorker(self, message, message_type)
        self.thread_pool.start(worker)
        message_data = MessageData.model_validate({"last_message": message, "last_message_time": time.time()})
        self.signals.dialogue_user_msg_received.emit(message_data.model_dump())

    def _add_message_to_queue_task(self, message: str, message_type: MessageType):
        self.message_queue.add_message(message, message_type)
        self.try_process_next_message_in_queue()
    
    def try_process_next_message_in_queue(self):
        if self._is_sending_instructions(): 
            self._process_instructions()
        elif self._is_ready_for_processing():
            self._process_next_message_in_queue()
        else:
            logging.info("Chatbot not ready to process messages.")

    def _process_next_message_in_queue(self):
        self.state.update_state(ChatbotState.READYING_MESSAGE)
        message_info = self.message_queue.get_next_message()
        if message_info:
            message, message_type = message_info
            self.set_mode(message_type)
            self.process_message(message)
        else:
            self.state.update_state(ChatbotState.IDLE)
            logging.info("No messages to process. Waiting for new messages.")

    def _is_sending_instructions(self):
        return self.state.is_state(ChatbotState.SENDING_INSTRUCTIONS)

    def _process_instructions(self):
        message, _ = self.message_queue.get_next_message()
        self.set_mode(MessageType.MEDIATOR_INTERNAL)
        if not message:
            raise Exception("No instructions to process.")
        self.process_message(message)

    def _is_ready_for_processing(self):
        return self.state.is_state(ChatbotState.API_READY) or self.state.is_state(ChatbotState.IDLE)

    def process_message(self, message: str):
        worker = ProcessMessageWorker(self, message)
        self.thread_pool.start(worker)

    def _process_message_task(self, message: str):
        try:
            self.bard.query(message)
            logging.info(f"Sent query to Bard: {message}"[:50])
        except Exception as e:
            logging.error(f"Error in sending or processing message: {e}"[:50])
            self.state.update_state(ChatbotState.ERROR)
        
    def process_response(self, reply): 
        worker = ProcessResponseWorker(self, reply)
        self.thread_pool.start(worker)     

    def _process_response_task(self, reply):
        self._update_state_after_sending_instructions()
        formatted_reply = self._format_reply(reply)
        reply_data = self._create_reply_data(formatted_reply)
        self._emit_reply_signal(reply_data)
        self.try_process_next_message_in_queue()
        logging.info(f"Received response from chatbot API: {reply_data.last_response}")

    def _update_state_after_sending_instructions(self):
        if self.state.is_state(ChatbotState.SENDING_INSTRUCTIONS):
            self.state.update_state(ChatbotState.INSTRUCTIONS_SENT)
            self.state.update_state(ChatbotState.API_READY)

    def _format_reply(self, reply):
        return "BARD: " + reply

    def _create_reply_data(self, reply):
        return ReplyData(last_response=reply, last_response_time=time.time(), message_mode = self.get_mode().value)

    def _emit_reply_signal(self, reply_data):
        should_display = (self.get_mode() == MessageType.MEDIATOR_PUBLIC) or (self.get_mode() == MessageType.USER)
        if should_display:
            self.signals.public_chatbot_msg_received.emit(reply_data.model_dump())
        else:
            self.signals.internal_chatbot_msg_received.emit(reply_data.model_dump())

    def update_settings(self, settings: dict):
        """
        Updates configuration settings for the Bard chatbot service.
        """
        logging.info(f"Updating Bard chatbot settings: {settings}")
        # Settings update logic goes here

    def get_status(self) -> dict:
        """
        Returns the current status of the Bard chatbot.
        """
        status = {
            "state": self.state.state.name
        }
        logging.info(f"Bard chatbot status: {status}")
        return status
