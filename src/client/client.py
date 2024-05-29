"""This module contains the main client class and related classes for 
a mediator-client application.

The Client class is the main entry point for the application. It manages 
the initialization, starting, stopping, and configuration of various system 
components such as the user interface, chatbot interface, data collector, 
mediator manager, and network handler.

The SignalManager class manages different signal managers for various components 
of the client. It holds instances of GUISignalManager, CollectorSignalManager, 
MediatorSignalManager, ChatSignalManager, and APISignalManager.

The SignalHandler class handles signals and connects them to signal handlers. It 
maintains a list of handlers and provides methods to add handlers and connect 
signals.

The BackgroundTaskHandler class is a QThread that handles background tasks in 
the client application. It starts the data collector, network handler, and 
mediator manager when the thread starts.

This module also imports necessary modules and classes from PyQt5 and other 
parts of the application. """

import sys
import logging
from typing import List
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject
from src.interfaces.i_system_module import ISystemModule
from src.user_interface.ui import UserInterface
from src.data_collection.collector import ClientDataCollector
from src.mediator_manager.manager import MediatorManagementModule
from src.network_handler.handler import NetworkHandler
from src.chatbot_interface.chatbot import ChatbotInterface
from src.chatbot_interface.mock_chatbot import MockChatbot
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



class SignalManager(QObject):
    """
    Manages different signal managers for various components of the client.

    Attributes:
        gui_signals (GUISignalManager): Signal manager for GUI-related signals.
        collector_signals (CollectorSignalManager): Signal manager for collector-related signals.
        mediator_signals (MediatorSignalManager): Signal manager for mediator-related signals.
        chat_signals (ChatSignalManager): Signal manager for chat-related signals.
        api_signals (APISignalManager): Signal manager for API-related signals.
    """

    def __init__(self) -> None:
        super().__init__()
        self.gui_signals = GUISignalManager()
        self.collector_signals = CollectorSignalManager()
        self.mediator_signals = MediatorSignalManager()
        self.chat_signals = ChatSignalManager()
        self.api_signals = APISignalManager()

    def get_signals(self) -> list[BaseSignalManager]:
        """
        Returns a list of all signal managers.

        Returns:
            list[BaseSignalManager]: A list of signal managers.
        """
        return [
            self.chat_signals,
            self.gui_signals,
            self.collector_signals,
            self.mediator_signals,
            self.api_signals,
        ]


class SignalHandler(QObject):
    """
    Handles signals and connects them to signal handlers.
    """

    def __init__(self, signal_manager: "SignalManager"):
        super().__init__()
        self.signal_manager = signal_manager
        self.handlers: list[BaseSignalHandler] = []

    def add_handler(self, handler: BaseSignalHandler, main_class: ISystemModule):
        """
        Adds a signal handler to the list of handlers.

        Args:
            handler (BaseSignalHandler): The signal handler to add.
            main_class (ISystemModule): The main class associated with the handler.
        """
        self.handlers.append(handler(self.signal_manager, main_class))

    def connect_signals(self):
        """
        Connects the signals to their respective signal handlers.
        """
        # not needed: this happens in the base signal handler constructor
        for handler in self.handlers:
            handler.connect_signals()


class BackgroundTaskHandler(QThread):
    """
    A class that handles background tasks in the client application.

    Args:
        data_collector (DataCollector): An instance of the DataCollector class.
        network_handler (NetworkHandler): An instance of the NetworkHandler class.
        mediator_manager (MediatorManager): An instance of the MediatorManager class.
    """

    def __init__(self, data_collector, network_handler, mediator_manager):
        super().__init__()
        self.data_collector = data_collector
        self.network_handler = network_handler
        self.mediator_manager = mediator_manager

    def run(self):
        """
        Starts the background tasks.

        This method is automatically called when the thread starts.
        It starts the data collector, network handler, and mediator manager.
        """
        logging.info("Background tasks starting...")
        self.data_collector.start()
        self.network_handler.start()
        self.mediator_manager.start()


class Client(ISystemModule):
    """
    The Client class represents the main client module of the mediator-client application.
    It manages the initialization, starting, stopping, and configuration of various system 
    components.

    Attributes:
        mode (str): The mode of the client. Can be "TEST" or None.
        app (QApplication): The QApplication instance for the GUI.
        signal_manager (SignalManager): The signal manager for handling signals.
        ui (UserInterface): The user interface module.
        ci (ChatbotInterface): The chatbot interface module.
        data_collector (ClientDataCollector): The data collector module.
        mediator_manager (MediatorManagementModule): The mediator management module.
        network_handler (NetworkHandler): The network handler module.
        background_handler (BackgroundTaskHandler): The background task handler module.
        network_endpoint (str): The endpoint for network communication.

    Methods:
        initialize(): Initializes the client and its components.
        get_components(): Returns a list of all the system components.
        start(): Starts the client by starting the GUI and chatbot interface.
        start_background_modules(): Starts the background modules in a separate thread.
        stop(): Stops the client by stopping all the components.
        configure(config: dict): Configures the client with the given configuration.
        reset(): Resets all the components.
        update(): Updates all the components.
        status(): Returns the status of all the components.

    """

    def __init__(self):
        super().__init__()
        self.mode = None  # "TEST"
        self.app = QApplication(sys.argv)  # Initialize QApplication in the main thread
        self.signal_manager = SignalManager()
        self.ui = UserInterface(self.signal_manager, self.app)
        self.ci = (
            MockChatbot(self.signal_manager)
            if self.mode == "TEST"
            else ChatbotInterface(self.signal_manager)
        )
        self.data_collector = ClientDataCollector(self.signal_manager)
        self.mediator_manager = MediatorManagementModule(self.signal_manager)
        self.network_handler = NetworkHandler()
        self.background_handler = BackgroundTaskHandler(
            self.data_collector, self.network_handler, self.mediator_manager
        )
        self.network_endpoint = "http://example.com/api"  # Placeholder endpoint

    def initialize(self):
        """
        Initializes the client and its components.
        """
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
        """
        Returns a list of all the system components.

        Returns:
            List[ISystemModule]: A list of system components.
        """
        return [
            self.ui,
            self.ci,
            self.data_collector,
            self.mediator_manager,
            self.network_handler,
        ]

    def start(self):
        """
        Starts the client by starting the GUI and chatbot interface.
        """
        logging.info("Client is starting...")
        self.ui.start()  # Start the GUI in the main thread
        self.ci.start()  # Assuming this can also be initiated in the main thread
        self.is_running = True

    def start_background_modules(self):
        """
        Starts the background modules in a separate thread.
        """
        self.background_handler.start()

    def stop(self):
        """
        Stops the client by stopping all the components.
        """
        logging.info("Client is stopping...")
        self.background_handler.quit()
        self.background_handler.wait()
        for component in self.get_components():
            component.stop()
        self.is_running = False

    def configure(self, config: dict):
        """
        Configures the client with the given configuration.

        Args:
            config (dict): The configuration dictionary.

        Returns:
            Any: The result of the configuration process.
        """
        return super().configure(config)

    def reset(self):
        """
        Resets all the components.
        """
        for component in self.get_components():
            component.reset()

    def update(self):
        """
        Updates all the components.
        """
        for component in self.get_components():
            component.update()

    def status(self):
        """
        Returns the status of all the components.

        Returns:
            dict: The status of all the components.
        """
        return {component.status() for component in self.get_components()}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = Client()
    logging.warning("INITIALIZING CLIENT")
    client.initialize()
    logging.warning("STARTING CLIENT")
    client.start()
    sys.exit(client.app.exec_())
