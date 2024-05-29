# src.chatbot_interface.chatbot.py
import logging, time, queue, os
from src.interfaces.i_chatbot_service import IChatbotService
from src.interfaces.data_models import ReplyData, MessageData
from src.chatbot_interface.chat_state_manager import ChatStateManager
from src.backends.backend_setup.discover import get_chrome_version
from src.backends.gemini_base import Bard
from src.backends.backend_setup.openai import ChatGPT
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.workers import SendMessageToChatbotWorker, MessageQueue
from src.signals.chat_signal_manager import ChatbotState, MessageType
from PyQt5.QtCore import QTimer, QEventLoop
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from src.client.client import SignalManager

class ChatbotInterface(ISystemModule, IChatbotService):

    def __init__(self, signal_manager : 'SignalManager'):
        super().__init__()
        self.bard = None
        self.chrome_path = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
        self.is_connected = False
        self.signal_manager = signal_manager
        self.signals = signal_manager.chat_signals
        self.state_manager = ChatStateManager(signal_manager)
        self.current_mode = MessageType.MEDIATOR_INTERNAL
        self.worker = None
        self.message_queue = None
        
    def initialize(self):
        self.is_running = False
        logging.info("Initializing ChatbotInterface module...")

    def configure(self, config: dict):
        logging.info("Configuring ChatbotInterface module...")

    def start(self):
        logging.info("Starting ChatbotInterface module...")
        self.state_manager.update_state(ChatbotState.CONNECTING)
        self.initialize_connection()
        self.message_queue = MessageQueue(self)
        self.state_manager.update_state(ChatbotState.API_READY)
        self.is_running = True
        self.load_and_send_instructions()

    def load_and_send_instructions(self):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "src/chatbot_interface/instructions.txt")
        try:
            with open(file_path, "r") as f:
                instructions = f.read()
        except FileNotFoundError:
            logging.error("Instructions file not found.")
            self.state_manager.update_state(ChatbotState.ERROR)
            return
        if not instructions:
            logging.info("No instructions found.")
            return
        instructions = instructions.replace('"', '\\"')
        logging.info("Sending instructions to Bard chatbot...")
        self.message_queue.add_message(instructions, MessageType.MEDIATOR_INTERNAL)
        self.state_manager.update_state(ChatbotState.SENDING_INSTRUCTIONS)

    def stop(self):
        logging.info("Stopping ChatbotInterface module...")
        self.close_connection()
        self.is_running = False

    def reset(self):
        logging.info("Resetting ChatbotInterface module...")
        self.is_running = False

    def update(self):
        logging.info("Updating ChatbotInterface module...")

    def declare_line_free(self, is_ready: bool):
        logging.info(f"ChatbotInterface ready state changed to: {is_ready}")
        logging.info("\033[96mAbout to emit is line free\033[0m")
        self.signals.is_line_free.emit(is_ready)

    def set_mode(self, mode: MessageType):
        self.current_mode = mode

    def get_mode(self) -> MessageType:
        return self.current_mode

    def initialize_connection(self):
        logging.info("Initializing connection to the chatbot service...")
        self.state_manager.update_state(ChatbotState.CONNECTING)
        try:
            # TODO: add logic for Bard too
            chrome_version = get_chrome_version(path=self.chrome_path)
            self.bard = ChatGPT(self.signal_manager, self.state_manager, path=self.chrome_path, driver_version=chrome_version)
            logging.info("chatgpt initialilzed")
            self.bard.open()
            logging.info("open.")
            assert self.state_manager.is_state(ChatbotState.CONNECTED), "Failed to connect to Bard chatbot."
            self.bard.new_chat('chat_session')
        except Exception as e:
            logging.error(f"Failed to initialize connection: {e}")
            self.state_manager.update_state(ChatbotState.ERROR)

    def close_connection(self):
        logging.info("Closing chatbot connection...")
        if self.bard and self.is_connected:
            self.bard.close()
            self.state_manager.update_state(ChatbotState.INITIAL)
        else:
            logging.info("Chatbot connection is already closed or was never established.")

    def add_message_to_queue(self, message: str, message_type: MessageType):
        self.message_queue.add_message(message, message_type)
        
    def _send_message(self, message: str) -> str:
        try:
            self.bard.query(message)
            logging.info(f"Sent query to bard")
        except Exception as e: 
            logging.error("Error during Bard chatbot communication.")
            error_message = "Error communicating with Bard chatbot:" + str(e)
            logging.error(error_message)
            is_secret = self.message_queue.get_state().get("is_secret")
            if not is_secret:
                logging.info("\033[96mAbout to emit chatbot error\033[0m")
                self.signals.chatbot_error.emit(error_message)  # Emit the error message
            return error_message
    
    def try_process_next_message_in_queue(self):
        sending_instructions = self.state_manager.is_state(ChatbotState.SENDING_INSTRUCTIONS)
        api_ready = self.state_manager.is_state(ChatbotState.API_READY)

        if sending_instructions: 
            message, _ = self.message_queue.get_next_message()
            self.set_mode(MessageType.MEDIATOR_INTERNAL)
            if not message:
                raise Exception("No instructions to process.")
            self.process_message(message)
            return
        
        if not api_ready:
            logging.info("Chatbot not ready to process messages.")
            return
        
        self.state_manager.update_state(ChatbotState.READYING_MESSAGE)
        message_info = self.message_queue.get_next_message()
        if message_info:
            message, message_type = message_info
            self.set_mode(message_type)
            self.process_message(message)
        else:
            self.state_manager.update_state(ChatbotState.IDLE)
            logging.info("No messages to process. Waiting for new messages.")

    def process_message(self, message: str):
        try:
            self.bard.query(message)
            logging.info(f"Sent query to Bard: {message}"[:50])
        except Exception as e:
            logging.error(f"Error in sending or processing message: {e}"[:50])
            self.state_manager.update_state(ChatbotState.ERROR)
        
    def send_message_from_queue(self):
        self.message_queue.process_next_message()
        
    def update_first_message(self): 
        logging.info("Updating first message...")
        first = self.message_queue.get_state().get("is_first_message")
        if first: 
            logging.info("First message has been submitted.")
            self.message_queue.submitted_first_message()
            self.signals.first_message_submitted.emit()

    def process_response(self, reply):
        if self.state_manager.is_state(ChatbotState.SENDING_INSTRUCTIONS):
            self.state_manager.update_state(ChatbotState.INSTRUCTIONS_SENT)
        reply = "BARD: " + reply
        reply_data = ReplyData(last_response=reply, last_response_time=time.time(), message_mode = self.get_mode().value)
        should_display = (self.get_mode() == MessageType.MEDIATOR_PUBLIC) or (self.get_mode() == MessageType.USER)
        if should_display:
            self.signals.public_chatbot_msg_received.emit(reply_data.model_dump())
        else:
            self.signals.internal_chatbot_msg_received.emit(reply_data.model_dump())
        logging.info(f"Received response from chatbot API: {reply_data.last_response}"[:50])

    def start_message_queueing_thread(self, message, message_type: MessageType) -> str:
        if self.worker is not None: 
            logging.info("Waiting for handle message submission worker")
            self.worker.wait()
        self.worker = SendMessageToChatbotWorker(message, self, message_type)
        self.worker.start()
        message_data = MessageData.model_validate({"last_message": message, "last_message_time": time.time()})
        self.signals.dialogue_user_msg_received.emit(message_data.model_dump())
    
    def wait_for_bard(self):
        logging.info("Waiting for Bard to be ready...")
        loop = QEventLoop()
        check_interval = 500  # Check every 1000 milliseconds (1 second)

        def check_ready():
            if self.bard.is_ready_for_next_message():
                loop.quit()

        timer = QTimer()
        timer.timeout.connect(check_ready)
        timer.start(check_interval)

        loop.exec_()  # Block here until loop.quit() is called
        timer.stop()
        logging.info("Bard is now ready.")

    def handle_chatbot_event(self, event: dict):
        """
        Handles specific events from the Bard chatbot.
        """
        logging.info(f"Handling Bard chatbot event: {event}")
        # Event-specific logic goes here

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
            "connected": self.is_connected
        }
        logging.info(f"Bard chatbot status: {status}")
        return status
