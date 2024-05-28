# src/data_collection/collector.py

import logging
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from src.interfaces.i_data_collector import IDataCollector
from src.interfaces.i_serializable import ISerializable
from src.interfaces.i_system_module import ISystemModule
from src.interfaces.data_models import UserData, ResponseModel
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.network_handler.handler import NetworkHandler
    from src.client.client import SignalManager
    from src.signals.collector_signal_manager import CollectorSignalManager


class ClientDataCollector(ISystemModule, IDataCollector, ISerializable):
    def __init__(self, signal_manager: 'SignalManager'):
        super().__init__()  # Initialize base class properties
        self.data_store = UserData(genome_id=0, time_since_startup=0.0, user_rating=0)  # Initialize the data store with a UserData instance
        self.network_handler : 'NetworkHandler' = None # type: ignore
        self.signals : 'CollectorSignalManager' = signal_manager.collector_signals
        self.is_running = False

    # Implement abstract methods from ISystemModule
    def initialize(self):
        super().initialize()  # Optionally call base implementation if defined
        logging.info("Client Data Collector initialized")

    def set_network_handler(self, network_handler):
        self.network_handler = network_handler

    def set_signal_holder(self, signal_holder):
        self.signal_holder = signal_holder

    def configure(self, config):
        super().configure(config)  # Optionally call base implementation if defined
        # Configuration logic specific to data collection
        logging.info(f"Client Data Collector configured with {config}")

    def start(self):
        super().start()  # Start the module
        self.is_running = True  # Set running status to True
        logging.info("Client Data Collector started")

    def stop(self):
        super().stop()  # Stop the module
        self.is_running = False  # Set running status to False
        logging.info("Client Data Collector stopped")

    def reset(self):
        super().reset()  # Reset the module
        self.data_store.clear()  # Clear data store on reset
        logging.info("Client Data Collector reset")

    def update(self):
        super().update()  # Update the module
        # Update logic here
        logging.info("Client Data Collector updated")

    def status(self):
        return super().status()  # Return the module's status
    
    def collect_data_for_mediator(self):
        data = self.get_data()
        data_for_transfer = data.model_dump()
        logging.info("\033[96mAbout to emit data ready for mediator\033[0m")
        self.signals.data_ready_for_mediator.emit(data_for_transfer)
    
    def get_data(self) -> UserData:
        return self.data_store  # Return a UserData instance

    def update_database(self, data):
        logging.info(f"Collecting data: {data}")
        try:
            logging.info(f"Data before update: {self.data_store}")
            self.data_store = self.data_store.model_copy(update=data)  # Update the data store with the new data
            logging.info(f"Data in storage: {self.data_store}")
            return True
        except Exception as e:
            logging.warning(e)
            return False

    def send_data(self):
        self.network_handler.send_data(self.data_store)
        
    def request_mediator_with_stored_data(self):
        logging.info("\033[31mCOLLECTOR FETCHING DATA\033[0m")
        """Tight coupling between network handler and data collector."""
        if not isinstance(self.data_store, UserData): 
            raise ValueError("Data store is not of type UserData")
        response = self.network_handler.request_mediator_swap(self.data_store)
        if response.status_code == 200:
            logging.info("\033[34mFETCHED IN COLLECTOR\033[0m")
            logging.info("\033[96mAbout to emit new mediator fetched\033[0m")
            self.signals.new_mediator_fetched.emit(response.json())
        else:
            logging.info(f"Failed to send data to server: {response.status_code}")
        
    # ISerializable specific methods
    def serialize(self, data):
        logging.info("Serializing data...")
        # Dummy serialization, converting list of data dicts to string representation
        return str(data)

    def deserialize(self, serialized_data):
        logging.info("Deserializing data...")
        # Dummy deserialization, converting string back to list
        return eval(serialized_data)