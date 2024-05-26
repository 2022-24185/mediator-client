# src.chatbot_interface.chatbot.py
import logging, time, queue, os
from src.interfaces.i_chatbot_service import IChatbotService
from src.backends.backend_setup.discover import get_chrome_version
from src.backends.gemini_base import Bard
from src.backends.backend_setup.openai import ChatGPT
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.workers import ProcessNextMessageInQueueWorker, WorkerQueue
import threading
from PyQt5.QtCore import QObject, pyqtSignal



class MockChatbot(ISystemModule, IChatbotService):
    def __init__(self, signal_manager):
        super().__init__()
        self.signal_manager = signal_manager

    def send_message(self, message: str) -> str:
        # Simulate a response
        simulated_response = "Simulated response for: " + message
        logging.info(f"MockChatbot received: {message}")
        logging.info(f"MockChatbot responding with: {simulated_response}")
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

    def __init__(self, signal_manager):
        super().__init__()
        self.bard = None
        self.chrome_path = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
        self.is_connected = False
        self.signal_holder = signal_manager
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
        # import this message from the instructions.txt file which contains many lines and some paragraphs. 
        # note that there are "" marks in there which may interfere with string operations
        # Print the current working directory
        current_dir = os.getcwd()
        logging.info(f"Current working directory: {current_dir}")

        # Construct the absolute path to the file
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
                self.bard = ChatGPT(signal_holder=self.signal_holder, path=self.chrome_path, driver_version=chrome_version)
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
            self.message_queue = WorkerQueue(self.bard, self.signal_holder)
        except Exception as e:
            logging.error(f"Failed to initialize Bard chatbot connection: {e}")
            self.is_connected = False

    def close_connection(self):
        """
        Closes the connection to the Bard chatbot service.
        """
        if self.bard and self.is_connected:
            logging.info('Closing Bard chatbot connection...')
            self.bard.close()
            self.is_connected = False
            logging.info("Bard chatbot connection closed.")
        else:
            logging.info("Bard chatbot connection is already closed or was never established.")

    def send_message(self, message: str, is_secret=False) -> str:
        logging.info(f"Sending message to Bard chatbot: {message[:30]}")
        if not self.is_connected:
            logging.warning("Bard chatbot is not connected. Initializing connection...")
            self.initialize_connection()
        
        if self.is_connected:
            self.message_queue.add_message(message, is_secret)
            return "Message queued for processing."
        else:
            error_message = "Connection to Bard chatbot could not be established."
            self.signal_manager.request_message_display.emit(error_message)
            return error_message
        
    def handle_response_received(self, response: str):
        logging.info(f"Received response from Bard chatbot: {response}")
        if self.message_queue: 
            self.message_queue.handle_response_received(response)

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
