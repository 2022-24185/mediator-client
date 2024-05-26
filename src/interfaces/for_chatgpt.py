from abc import ABC, abstractmethod

# src/interfaces/i_data_collector.py

class IDataCollector:
    def collect_data(self, data):
        """Collect and store data."""
        pass

    def send_data(self):
        """Prepare and send collected data to a specified target or storage."""
        pass

# src/interfaces/i_event_handler.py

from abc import ABC, abstractmethod


class IEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event_type, event_data):
        """Handle an event given its type and associated data."""
        pass

    @abstractmethod
    def subscribe_to_event(self, event_type, handler_function):
        """Subscribe to an event type with a handler function."""
        pass

    @abstractmethod
    def unsubscribe_to_event(self, event_type):
        """Unsubscribe to an event type."""
        pass

# src/interfaces/i_logger.py

class ILogger:
    def log_message(self, message):
        """Log a message."""
        pass

    def log_error(self, error):
        """Log an error."""
        pass

    def log_warning(self, warning):
        """Log a warning."""
        pass

# src/interfaces/i_mediator_handler.py

class IMediatorHandler:
    def load_mediator(self):
        """Load and initialize a mediator."""
        pass

    def update_mediator(self, update_info):
        """Update the mediator's logic or state based on given information."""
        pass

    def process_input(self, input_data):
        """Process input through the mediator and return the output."""
        pass

    def generate_output(self):
        """Generate output based on the mediator's current state and input history."""
        pass

# src/interfaces/i_model.py

class IModel:
    def load_model(self, model_path):
        """Load a pre-trained model from the given path."""
        pass

    def preprocess_input(self, input_data):
        """Preprocess input data before feeding it into the model."""
        pass

    def predict(self, preprocessed_data):
        """Run inference on the preprocessed data."""
        pass

    def postprocess_output(self, model_output):
        """Postprocess model output to make it human-readable."""
        pass

# src/interfaces/i_notifier.py

class INotifier:
    def send_notification(self, message):
        """Send a notification with the given message."""
        pass

# src/interfaces/i_plugin.py

class IPlugin:
    def load_plugin(self, plugin_path):
        """Load a plugin from the given path."""
        pass

    def initialize_plugin(self, config):
        """Initialize the loaded plugin with the provided configuration."""
        pass

    def run_plugin(self, data):
        """Execute the plugin logic on the given data."""
        pass

# src/interfaces/i_base_service.py
class IBaseService(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def status(self) -> bool:
        pass


class IChatbotService(IBaseService):
    @abstractmethod
    def initialize(self):
        """
        Initializes the chatbot service.
        This method should handle any setup necessary for the chatbot service.
        """
        pass


    @abstractmethod
    def start(self):
        """
        Starts the chatbot service.
        This method should start the chatbot service and make it ready to receive messages.
        """
        pass


    @abstractmethod
    def stop(self):
        """
        Stops the chatbot service.
        This method should stop the chatbot service and clean up any resources.
        """
        pass


    @abstractmethod
    def status(self) -> bool:
        """
        Returns the status of the chatbot service.
        :return: bool - True if the chatbot service is running, False otherwise.
        """
        pass


    @abstractmethod
    def send_message(self, message: str) -> str:
        """
        Sends a message to the chatbot and returns the response.
        :param message: str - The message to send to the chatbot.
        :return: str - The chatbot's response.
        This method should handle sending a message and receiving the response from the chatbot.
        """

        pass

    @abstractmethod
    def handle_chatbot_event(self, event: dict):
        """
        Handles specific events from the chatbot.
        :param event: dict - Event data from the chatbot.
        This could include handling session starts, errors, or other chatbot-specific events.
        """
        pass


    @abstractmethod
    def update_settings(self, settings: dict):
        """
        Updates settings or configurations for the chatbot.
        :param settings: dict - A dictionary of settings to apply to the chatbot service.
        This method allows dynamic adjustments to the chatbot's operation, such as changing thresholds or behaviors.
        """
        pass

# src/interfaces/i_storage.py

class IStorage:
    def connect(self, connection_string):
        """Connect to the storage using the provided connection string."""
        pass

    def store_data(self, data):
        """Store the given data in the connected storage."""
        pass

    def retrieve_data(self, query):
        """Retrieve data from the connected storage based on the query."""
        pass

    def disconnect(self):
        """Disconnect from the storage."""
        pass

# src/interfaces/i_system_module.py

from abc import ABC, abstractmethod
import logging

class ISystemModule(ABC):
    def __init__(self):
        self.is_running = False
        logging.basicConfig(level=logging.INFO)

    @abstractmethod
    def initialize(self):
        """Prepare the module for operation."""
        logging.info("Initializing module...")
        self.is_running = False

    @abstractmethod
    def configure(self, config: dict):
        """Set any necessary configuration parameters."""
        logging.info("Configuring module...")

    @abstractmethod
    def start(self):
        """Start the module."""
        try:
            logging.info("Starting module...")
            self.is_running = True
        except Exception as e:
            logging.error(f"Error starting module: {e}")

    @abstractmethod
    def stop(self):
        """Stop the module."""
        try:
            logging.info("Stopping module...")
            self.is_running = False
        except Exception as e:
            logging.error(f"Error stopping module: {e}")

    @abstractmethod
    def reset(self):
        """Reset the module to its initial state."""
        logging.info("Resetting module...")
        self.is_running = False

    @abstractmethod
    def update(self):
        """Perform any necessary updates on a regular basis."""
        logging.info("Updating module...")

    def status(self) -> bool:
        """Return the running status of the module."""
        logging.info("Checking status of the module...")
        return self.is_running

