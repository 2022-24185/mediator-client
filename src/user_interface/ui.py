# src/user_interface/ui.py
from collections import defaultdict
import sys
from PyQt5.QtWidgets import QApplication
from src.interfaces.i_event_handler import IEventHandler
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.gui import ChatbotGUI
import logging


class UserInterface(ISystemModule, IEventHandler):
    def __init__(self, signal_manager, app=None):
        super().__init__()  # Initialize base class properties
        self.app = app if app is not None else QApplication(sys.argv)  # Use existing app or create new
        self.signal_manager = signal_manager
        self.gui : ChatbotGUI = None
        self.chatbot = None
        self.handlers = defaultdict(list)

    def initialize(self):
        super().initialize()
        self.gui = ChatbotGUI(self.app, self.signal_manager)  # Create GUI when initializing
        self.subscribe_to_event('message sent', self.handle_message_sent)
        logging.info("User Interface initialized")

    def start(self):
        super().start()
        self.gui.show()  # Make sure GUI operations are thread-safe

    def stop(self):
        super().stop()
        self.app.quit()  # Ensure the application event loop is stopped
        logging.info("User Interface stopped")

    def configure(self, config: dict):
        return super().configure(config)
    
    def get_gui(self):
        return self.gui

    def reset(self):
        super().reset()
        self.handlers.clear()
        logging.info("User Interface reset")

    def update(self):
        super().update()
        # Additional update logic here
        logging.info("User Interface updated")

    def status(self):
        return super().status()

    def subscribe_to_event(self, event_type, handler):
        self.handlers[event_type].append(handler)
        #logging.info(f"Subscribed to event {event_type}")

    def unsubscribe_from_event(self, event_type, handler):
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            logging.info(f"Unsubscribed from event {event_type}")

    def handle_event(self, event_type, event_data):
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(event_data)
        logging.info(f"Handled event: {event_type} with data {event_data}")

    def handle_message_sent(self, message):
        logging.info(f"Message sent: {message}")
        self.gui.display_input_message(message)
