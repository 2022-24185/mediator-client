from abc import ABC, abstractmethod
import logging

class ISystemModule(ABC):
    def __init__(self):
        self.is_running = False
        # make a custom logging setup for this module that colors it green
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

