# src.chatbot_interface.chatbot.py
import logging, time, queue, os
from src.interfaces.i_chatbot_service import IChatbotService
from src.interfaces.data_models import ReplyData, MessageData
from src.backends.backend_setup.discover import get_chrome_version
from src.backends.gemini_base import Bard
from src.backends.backend_setup.openai import ChatGPT
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.workers import SendMessageToChatbotWorker, MessageQueue
from PyQt5.QtCore import QTimer, QEventLoop
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from src.client.client import SignalManager

class MockChatbot(ISystemModule, IChatbotService):
    def __init__(self, signal_manager):
        super().__init__()
        self.signal_manager = signal_manager

    def add_message_to_queue(self, message: str) -> str:
        # Simulate a response
        simulated_response = "Simulated response for: " + message
        logging.info(f"MockChatbot received: {message}")
        logging.info(f"MockChatbot responding with: {simulated_response}")
        logging.info("\033[96mAbout to emit request message display\033[0m")
        self.signal_manager.request_message_display.emit(simulated_response)
        return simulated_response

    def start(self):
        logging.info("MockChatbot started...")

    def stop(self):
        logging.info("MockChatbot stopped...")

    def get_status(self) -> dict:
        return {"connected": True}
    
    def initialize(self):
        logging.info("Initializing MockChatbot...")

    def reset(self):
        logging.info("Resetting MockChatbot...")

    def update(self):
        logging.info("Updating MockChatbot...")
    
    def close_connection(self):
        logging.info("MockChatbot connection closed.")

    def configure(self, config: dict):
        logging.info("Configuring MockChatbot...")

    def handle_chatbot_event(self, event: dict):
        logging.info(f"Handling event: {event}")

    def initialize_connection(self):
        logging.info("Initializing MockChatbot connection...")

    def update_settings(self, settings: dict):
        logging.info(f"Updating MockChatbot settings: {settings}")


class ChatbotInterface(ISystemModule, IChatbotService):

    def __init__(self, signal_manager : 'SignalManager'):
        super().__init__()
        self.bard = None
        self.chrome_path = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
        self.is_connected = False
        self.signal_manager = signal_manager
        self.signals = signal_manager.chat_signals
        self.worker = None
        self.message_queue = None
        self.is_first_message = True
        
    def initialize(self):
        self.is_running = False
        logging.info("Initializing ChatbotInterface module...")

    def configure(self, config: dict):
        logging.info("Configuring ChatbotInterface module...")

    def start(self):
        logging.info("Starting ChatbotInterface module...")
        self.initialize_connection()
        self.is_running = True
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "src/chatbot_interface/instructions.txt")
        with open(file_path, "r") as f:
            instructions = f.read()
        
        if not instructions:
            logging.info("No instructions found.")
            return
        instructions = instructions.replace('"', '\\"')
        logging.info("Sending instructions to Bard chatbot...")
        self.message_queue.add_message(instructions, True)

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

    def initialize_connection(self):
        """
        Establishes a connection to the Bard chatbot service by initializing the Bard instance.
        """
        use_openai = True

        logging.info("Initializing connection to Bard chatbot service...")
        try:
            chrome_version = get_chrome_version(path=self.chrome_path)
            logging.info(f"Detected Chrome version: {chrome_version}")
            if use_openai:
                self.bard = ChatGPT(self.signal_manager, path=self.chrome_path, driver_version=chrome_version)
                logging.info("Opening ChatGPT chatbot connection...")
                self.bard.open()
                logging.info("ChatGPT browser launched.")
                self.bard.new_chat('imgpt')
                self.is_connected = True
                logging.info("ChatGPT chatbot connection established.")
            else: 
                self.bard = Bard(path=self.chrome_path, driver_version=chrome_version)
                logging.info("Opening Gemini chatbot connection...")
                self.bard.open()
                logging.info("Gemini browser launched.")
                self.bard.new_chat('imgemini')
                self.is_connected = True
                logging.info("Gemini chatbot connection established.")
            self.message_queue = MessageQueue(self)
        except Exception as e:
            logging.error(f"Failed to initialize Bard chatbot connection: {e}")
            self.is_connected = False

    def close_connection(self):
        """
        Closes the connection to the Bard chatbot service.
        """
        logging.info("\033[31mTrying to close API connection...\033[0m")
        if self.bard and self.is_connected:
            logging.info('Closing API chatbot connection...')
            self.bard.close()
            self.is_connected = False
            logging.info("API chatbot connection closed.")
        else:
            logging.info("Bard chatbot connection is already closed or was never established.")

    def add_message_to_queue(self, message: str, is_secret=False) -> str:
        logging.info(f"Adding message to chatbot queue: {message[:30]}")
        if not self.is_connected:
            logging.warning("Bard chatbot is not connected. Initializing connection...")
            self.initialize_connection()
        
        if self.is_connected:
            self.message_queue.add_message(message, is_secret)
            # self.chat_signals.
            return "Message queued for processing."
        else:
            error_message = "Connection to Bard chatbot could not be established."
            logging.info("\033[96mAbout to emit error msg\033[0m")

            self.signals.dialogue_chatbot_msg_received.emit(error_message)
            return error_message
        
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
        logging.info("PROCESSING response...")
        is_secret = self.message_queue.get_state().get("is_secret")
        logging.info(f"Is secret? {is_secret}")
        reply = "BARD: " + reply
        reply_data = ReplyData(last_response=reply, last_response_time=time.time(), is_secret=is_secret)
        if not is_secret:
            logging.info("\033[96mAbout to emit chatbot msg received\033[0m")
            self.signals.dialogue_chatbot_msg_received.emit(reply_data.model_dump())
        else: 
            logging.info("\033[96mAbout to emit secret chatbot msg received\033[0m")
            self.signals.secret_chatbot_msg_received.emit(reply_data.model_dump())
        logging.info(f"Received response from chatbot API: {reply_data.last_response}"[:50])

    def start_message_queueing_thread(self, message: str, is_secret=False) -> str:
        if self.worker is not None: 
            logging.info("Waiting for handle message submission worker")
            self.worker.wait()
        self.worker = SendMessageToChatbotWorker(message, self)
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
