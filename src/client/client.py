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
from src.user_interface.workers import *
import logging
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.user_interface.gui import ChatbotGUI


class SignalManager(QObject):
    # Signals emitted from Chatbot
    request_message_display = pyqtSignal(str)
    chatbot_response_retrieved = pyqtSignal(str) # Message, is_secret

    # Signals emitted from SignalHandler
    chatbot_response_displayed = pyqtSignal(bool)
    request_data_aggregation = pyqtSignal()
    interface_reset_complete = pyqtSignal()
    mediator_data_received = pyqtSignal(str)
    request_mediator_processing = pyqtSignal(str)
    request_data_for_mediator = pyqtSignal()
    request_mediator_message_submission = pyqtSignal(str, bool) # msg, is_secret

    # Signals emitted from Collector
    data_aggregation_started = pyqtSignal()
    data_aggregation_completed = pyqtSignal(dict)

    # Signals emitted from Manager
    request_mediator_intervention = pyqtSignal()

    # Signals emitted from GUI
    request_message_submission = pyqtSignal(str)
    request_data_submission = pyqtSignal(dict)
    request_new_mediator = pyqtSignal()

    # Signals emitted from Widgets
    rating_changed = pyqtSignal(int)
    enter_pressed = pyqtSignal()

    # Signals emitted from Workers
    secret_message_sent = pyqtSignal(bool)
    message_processed_completed = pyqtSignal(bool)
    data_storage_completed = pyqtSignal(bool)
    new_mediator_assigned = pyqtSignal(int) #genome id
    mediator_processing_completed = pyqtSignal(str, bool) # msg, is_secret
    mediator_intervention_completed = pyqtSignal(bool)
    first_message_submitted = pyqtSignal(bool)


class SignalHandler(QObject): 
    def __init__(self, signal_manager, chatbot_interface, data_collector, gui, mediator_manager, start_background_modules):
        super().__init__()
        self.signal_manager : SignalManager = signal_manager
        self.chatbot_interface : ChatbotInterface = chatbot_interface
        self.data_collector : ClientDataCollector = data_collector
        self.mediator_manager : MediatorManagementModule= mediator_manager
        self.gui : 'ChatbotGUI' = gui # type: ignore
        self.worker = None
        self.mediator_requested = False
        self.start_background_modules : function = start_background_modules
        self.connect_signals()

    def connect_signals(self):
        # Connect signals emitted from Chatbot
        self.signal_manager.request_message_display.connect(self.gui.display_response)
        self.signal_manager.chatbot_response_retrieved.connect(self.chatbot_interface.handle_response_received)


        # Connect signals emitted from Client
        self.signal_manager.chatbot_response_displayed.connect(self.handle_chatbot_response_displayed)
        self.signal_manager.request_data_aggregation.connect(self.aggregate_data)
        self.signal_manager.interface_reset_complete.connect(self.gui.finalize_reset)
        self.signal_manager.mediator_data_received.connect(self.signal_manager.request_mediator_processing.emit)
        self.signal_manager.request_mediator_processing.connect(self.handle_mediator_processing)
        self.signal_manager.request_data_for_mediator.connect(self.handle_data_retrieval)
        self.signal_manager.request_mediator_message_submission.connect(self.send_mediator_message)

        # Connect signals emitted from Collector
        self.signal_manager.data_aggregation_completed.connect(self.handle_data_aggregation_complete)

        # Connect signals emitted from Manager
        self.signal_manager.request_mediator_intervention.connect(self.handle_mediator_intervention_request)

        # Connect signals emitted from GUI
        self.signal_manager.request_message_submission.connect(self.process_message)
        self.signal_manager.request_data_submission.connect(self.submit_data)
        self.signal_manager.request_new_mediator.connect(self.assign_new_mediator)

        # Connect signals emitted from Widgets
        # self.signal_manager.rating_changed.connect(self.handle_rating_change)
        # self.signal_manager.enter_pressed.connect(self.handle_enter_pressed)

        # Connect signals emitted from Workers
        self.signal_manager.secret_message_sent.connect(self.handle_secret_message)
        self.signal_manager.message_processed_completed.connect(self.handle_message_processed)
        self.signal_manager.data_storage_completed.connect(self.handle_data_storage_completed)
        self.signal_manager.new_mediator_assigned.connect(self.handle_new_mediator_assignment)
        self.signal_manager.mediator_processing_completed.connect(self.signal_manager.request_mediator_message_submission.emit)
        self.signal_manager.mediator_intervention_completed.connect(self.handle_mediator_intervention_complete)
        self.signal_manager.first_message_submitted.connect(self.start_background_modules)
        

    def process_message(self, message):
        self.thread = SendMessageToChatbotWorker(message, self.chatbot_interface, self.signal_manager)
        self.thread.start()

    def handle_mediator_intervention_request(self):
        ready = self.chatbot_interface.bard.is_ready_for_next_message()
        q_free = self.chatbot_interface.message_queue.is_empty()
        logging.info(f"Ready: {ready}, Queue free: {q_free}")
        if ready and q_free:
            self.signal_manager.request_data_for_mediator.emit()

    def send_mediator_message(self, message: str, is_secret: bool):
        logging.info(f"Sending secret message: {message}")
        # check if message is empty string and if so do not send
        message = message.strip()
        if message is not None: 
            self.thread = SendMessageToChatbotWorker(message, self.chatbot_interface, self.signal_manager, is_secret)
            self.thread.start()
        else: 
            self.signal_manager.secret_message_sent.emit(False)

    def submit_data(self, data):
        # Implement the logic to submit the rating
        if self.worker is not None:
                logging.info("Waiting for worker A to be freed")
                self.worker.wait()  # Wait for the worker to finish
        self.worker = AgentDataUpdateWorker(self.data_collector, data, self.signal_manager)
        logging.info("Worker starting..")
        self.worker.start()

    def display_message(self, message):
        # Implement the logic to display the message
        self.signal_manager.chatbot_response_displayed.emit(True)

    def handle_data_storage_completed(self, success):
        if success:
            logging.info("Data storage completed successfully.")
            if self.mediator_requested:
                self.signal_manager.request_data_aggregation.emit()
            else:
                logging.info("No mediator requested.")
        else:
            logging.error("Data storage failed.")

    def aggregate_data(self):
        self.data_collector.send_data_to_server()
        # Implement the logic to aggregate data

    def assign_new_mediator(self, time_elapsed = 0.0):
        self.mediator_requested = True
        # add time_elapsed to the mediator assignment time
        data = {
            "time_elapsed": time_elapsed
        }
        self.signal_manager.request_data_submission.emit(data)

    def handle_data_aggregation_complete(self, response: dict):
        # After data aggregation, proceed with new mediator assignment
        logging.info("Data aggregation completed. Switching mediator...")
        if self.worker is not None:
            logging.info("Waiting for worker M to be freed")
            self.worker.wait()  # Wait for the worker to finish
        self.worker = MediatorSwitchWorker(self.signal_manager, self.mediator_manager, response)
        self.worker.start()

    def handle_new_mediator_assignment(self, genome_id):
        logging.info("New mediator assigned successfully. Resetting...")
        data = {
            'genome_id': genome_id
        }
        self.signal_manager.request_data_submission.emit(data)
        self.signal_manager.interface_reset_complete.emit()
        self.mediator_requested = False

    def handle_chatbot_response_displayed(self, displayed):
        if displayed:
            logging.info("Chatbot response was displayed successfully.")
        else:
            logging.error("Failed to display chatbot response.")

    def handle_data_retrieval(self):
        data = self.data_collector.get_data()
        logging.info("Data retrieval complete.")
        logging.info(data)
        if data:
            logging.info("Data retrieval completed successfully.")
            data = data.model_dump_json()
            self.signal_manager.mediator_data_received.emit(data)
        else:
            logging.error("Data retrieval failed.")

    def handle_mediator_processing(self, data: str):
        logging.info("Data collection complete. Processing in mediator...")
        data_obj = UserData.model_validate_json(data)
        if self.worker is not None:
            logging.info("Waiting for worker M to be freed")
            self.worker.wait()  # Wait for the worker to finish
        self.worker = MediatorProcessingWorker(data_obj, self.mediator_manager, self.signal_manager)
        self.worker.start()

    def handle_message_processed(self, success):
        if success:
            self.mediator_manager.reset_on_user_message()
            logging.info("Message processing completed successfully.")
        else:
            logging.error("Message processing failed.")

    def handle_secret_message(self, success): 
        if success:
            self.mediator_manager.update_unanswered_count()
            logging.info("SECRET message processing completed successfully.")
        else:
            logging.error("SECRET message processing failed.")

    def handle_mediator_intervention_complete(self, success):
        if success:
            logging.info("Mediator intervention completed successfully.")
        else:
            logging.error("Mediator intervention failed.")

class BackgroundTaskHandler(QThread):
    def __init__(self, components):
        super().__init__()
        self.data_collector = components['data_collector']
        self.network_handler = components['network_handler']
        self.mediator_manager = components['mediator_manager']

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
        self.components = {
            'ui': UserInterface(self.signal_manager, self.app),
            'ci': MockChatbot(self.signal_manager) if self.mode == "TEST" else ChatbotInterface(self.signal_manager),
            'data_collector': ClientDataCollector(),
            'mediator_manager': MediatorManagementModule(self.signal_manager),
            'network_handler': NetworkHandler()
        };
        self.background_handler = BackgroundTaskHandler(self.components)
        self.network_endpoint = "http://example.com/api"  # Placeholder endpoint

    def initialize(self):
        for name, component in self.components.items():
            logging.info(f"Initializing {name}...")
            component.initialize()
        
        # Dependency injection
        self.components['network_handler'].set_mock_mode(self.mode == "TEST")
        self.components['data_collector'].set_network_handler(self.components['network_handler'])
        self.components['data_collector'].set_signal_holder(self.signal_manager)
        self.signal_handler = SignalHandler(
            self.signal_manager,
            self.components['ci'],
            self.components['data_collector'],
            self.components['ui'].get_gui(),
            self.components['mediator_manager'],
            self.start_background_modules
        )
        # Connect the rating changed signal to a method in DataCollector
        #self.mediator_manager.set_data_collector(self.data_collector)
        #self.mediator_manager.set_network_handler(self.network_handler)

    def start(self):
        logging.info("Client is starting...")
        self.components['ui'].start()  # Start the GUI in the main thread
        self.components['ci'].start()  # Assuming this can also be initiated in the main thread
        self.is_running = True

    def start_background_modules(self): 
        self.background_handler.start()  # Start background tasks in a QThread

    def stop(self):
        logging.info("Client is stopping...")
        self.background_handler.quit()
        self.background_handler.wait()
        for component in self.components.values():
            component.stop()
        self.is_running = False

    def configure(self, config: dict):
        return super().configure(config)

    def reset(self):
        for component in self.components.values():
            component.reset()

    def update(self):
        for component in self.components.values():
            component.update()

    def status(self):
        return {name: component.status() for name, component in self.components.items()}

    # def handle_event(self, event_type, event_data):
    #     for component in self.components.values():
    #         if isinstance(component, IEventHandler):
    #             component.handle_event(event_type, event_data)

    def send_data_to_server(self, data):
        response = self.components['network_handler'].send_data(self.network_endpoint, data)
        logging.info(f"Response from server: {response}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = Client()
    client.initialize()
    client.start()
    sys.exit(client.app.exec_())
