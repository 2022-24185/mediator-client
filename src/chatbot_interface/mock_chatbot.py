import logging
from src.interfaces.i_system_module import ISystemModule
from src.interfaces.i_chatbot_service import IChatbotService
    

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
