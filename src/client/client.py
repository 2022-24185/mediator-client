import sys
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.ui import UserInterface
from src.data_collection.collector import ClientDataCollector
from src.mediator_manager.manager import MediatorManagementModule
from src.network_handler.handler import NetworkHandler
from src.chatbot_interface.chatbot import ChatbotInterface, MockChatbot
from src.signals.chat_signal_manager import ChatSignalManager
from src.signals.mediator_signal_manager import MediatorSignalManager
from src.signals.gui_signal_manager import GUISignalManager
from src.signals.collector_signal_manager import CollectorSignalManager
from src.signals.API_signal_manager import APISignalManager
from src.interfaces.i_signal_manager import BaseSignalManager
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.signals.collector_signal_handler import CollectorSignalHandler
from src.signals.chat_signal_handler import ChatSignalHandler
from src.signals.mediator_signal_handler import MediatorSignalHandler
from src.signals.gui_signal_handler import GUISignalHandler
from src.signals.client_signal_handler import ClientSignalHandler
from src.user_interface.workers import *
import logging
from PyQt5.QtCore import QObject

from typing import List

class SignalManager(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.gui_signals = GUISignalManager()
        self.collector_signals = CollectorSignalManager()
        self.mediator_signals = MediatorSignalManager()
        self.chat_signals = ChatSignalManager()
        self.api_signals = APISignalManager()
        
    def get_signals(self) -> list[BaseSignalManager]: 
        return [
            self.chat_signals,
            self.gui_signals,
            self.collector_signals,
            self.mediator_signals,
            self.api_signals
        ]

class SignalHandler(QObject): 
    def __init__(self, signal_manager: 'SignalManager'): 
        super().__init__()
        self.signal_manager = signal_manager
        self.handlers : list[BaseSignalHandler] = []

    def add_handler(self, handler : BaseSignalHandler, main_class : ISystemModule):
        self.handlers.append(handler(self.signal_manager, main_class))

    def connect_signals(self):
        # not needed: this happens in the base signal handler constructor
        for handler in self.handlers: 
            handler.connect_signals()

class BackgroundTaskHandler(QThread):
    def __init__(self, data_collector, network_handler, mediator_manager):
        super().__init__()
        self.data_collector = data_collector
        self.network_handler = network_handler
        self.mediator_manager = mediator_manager

    def run(self):
        logging.info("Background tasks starting...")
        self.data_collector.start()
        self.network_handler.start()
        self.mediator_manager.start()

class Client(ISystemModule):
    def __init__(self):
        super().__init__()
        self.mode = None # "TEST"
        self.app = QApplication(sys.argv)  # Initialize QApplication in the main thread
        self.signal_manager = SignalManager()
        self.ui = UserInterface(self.signal_manager, self.app)
        self.ci = MockChatbot(self.signal_manager) if self.mode == "TEST" else ChatbotInterface(self.signal_manager)
        self.data_collector = ClientDataCollector(self.signal_manager)
        self.mediator_manager = MediatorManagementModule(self.signal_manager)
        self.network_handler = NetworkHandler()
        self.background_handler = BackgroundTaskHandler(self.data_collector, self.network_handler, self.mediator_manager)
        self.network_endpoint = "http://example.com/api"  # Placeholder endpoint

    def initialize(self):
        for component in self.get_components():
            logging.info(f"Initializing {component}...")
            component.initialize()
        
        # Dependency injection
        self.network_handler.set_mock_mode(self.mode == "TEST")
        self.data_collector.set_network_handler(self.network_handler)
        self.signal_manager.gui_signals.client_stop.connect(self.stop)
        self.signal_handler = SignalHandler(self.signal_manager)
        self.signal_handler.add_handler(CollectorSignalHandler, self.data_collector)
        self.signal_handler.add_handler(MediatorSignalHandler, self.mediator_manager)
        self.signal_handler.add_handler(ChatSignalHandler, self.ci)
        self.signal_handler.add_handler(GUISignalHandler, self.ui.get_gui())
        self.signal_handler.add_handler(ClientSignalHandler, self)
        # self.signal_handler.connect_signals() # not needed, happens in the base constructors

    def get_components(self) -> List[ISystemModule]:
        return [
            self.ui,
            self.ci,
            self.data_collector,
            self.mediator_manager,
            self.network_handler,
        ]

    def start(self):
        logging.info("Client is starting...")
        self.ui.start()  # Start the GUI in the main thread
        self.ci.start()  # Assuming this can also be initiated in the main thread
        self.is_running = True

    def start_background_modules(self): 
        self.background_handler.start()  # Start background tasks in a QThread

    def stop(self):
        logging.info("Client is stopping...")
        self.background_handler.quit()
        self.background_handler.wait()
        for component in self.get_components():
            component.stop()
        self.is_running = False

    def configure(self, config: dict):
        return super().configure(config)

    def reset(self):
        for component in self.get_components():
            component.reset()

    def update(self):
        for component in self.get_components():
            component.update()

    def status(self):
        return {component.status() for component in self.get_components()}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = Client()
    logging.warning("INITIALIZING CLIENT")
    client.initialize()
    logging.warning("STARTING CLIENT")
    client.start()
    sys.exit(client.app.exec_())
