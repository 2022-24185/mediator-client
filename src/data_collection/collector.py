"""
collector.py

This module contains the ClientDataCollector class which is responsible 
for collecting and managing client data. 

The ClientDataCollector class inherits from ISystemModule, IDataCollector, 
and ISerializable interfaces. It uses a SignalManager instance to manage 
signals, a UserData instance to store client data, and a NetworkHandler 
instance to handle network-related tasks. 

The class provides methods to initialize, configure, start, stop, reset, 
and get the status of the data collector. It also provides methods to get, 
update, and send the collected data. The data can be serialized to a 
dictionary and deserialized from a dictionary to a UserData object.

Classes:
    - Recipient: An enumeration that represents the recipient of the data.
    - ClientDataCollector: A class that represents a client data collector.

Exceptions:
    - ValueError: Raised when an unsupported data type is provided for update 
    or an unsupported recipient type is provided for sending data.
"""
import logging
from typing import TYPE_CHECKING, Union
from enum import Enum

from pydantic import BaseModel, ValidationError

from src.interfaces.i_data_collector import IDataCollector
from src.interfaces.i_serializable import ISerializable
from src.interfaces.i_system_module import ISystemModule
from src.interfaces.data_models import UserData

if TYPE_CHECKING:
    from src.network_handler.handler import NetworkHandler
    from src.client.client import SignalManager
    from src.signals.collector_signal_manager import CollectorSignalManager

class Recipient(Enum):
    MEDIATOR = "mediator"
    NETWORK = "network"


class ClientDataCollector(ISystemModule, IDataCollector, ISerializable):
    """
    A class that represents a client data collector.

    This class is responsible for collecting and managing client data.

    Args:
        signal_manager (SignalManager): The signal manager instance.

    Attributes:
        data_store (UserData): The data store for client data.
        network_handler (NetworkHandler): The network handler instance.
        signals (CollectorSignalManager): The signal manager for collector signals.
        is_running (bool): A flag indicating whether the collector is running or not.
    """

    def __init__(self, signal_manager: "SignalManager"):
        super().__init__()
        self.data_store = UserData(genome_id=0, time_since_startup=0.0, user_rating=0)
        self.network_handler: "NetworkHandler" = None  # type: ignore
        self.signals: "CollectorSignalManager" = signal_manager.collector_signals
        self.is_running = False

    def initialize(self):
        """
        Initialize the client data collector.

        This method is called during the initialization of the collector.
        """
        super().initialize()
        logging.info("Client Data Collector initialized")

    def set_network_handler(self, network_handler: "NetworkHandler"):
        """
        Set the network handler for the client data collector.

        Args:
            network_handler (NetworkHandler): The network handler instance.
        """
        self.network_handler = network_handler

    def configure(self, config):
        """
        Configure the client data collector.

        Args:
            config: The configuration for the collector.
        """
        super().configure(config)
        logging.info(f"Client Data Collector configured with {config}")

    def start(self):
        """
        Start the client data collector.
        """
        self._change_running_state(True, "started")

    def stop(self):
        """
        Stop the client data collector.
        """
        self._change_running_state(False, "stopped")

    def reset(self):
        """
        Reset the client data collector.

        This method resets the data store and clears any collected data.
        """
        super().reset()
        self.data_store = UserData(genome_id=0, time_since_startup=0.0, user_rating=0)
        logging.info("Client Data Collector reset")

    def status(self):
        """
        Get the status of the client data collector.

        Returns:
            str: The status of the collector.
        """
        return super().status()

    def get_data(self) -> UserData:
        """
        Get the current client data.

        Returns:
            UserData: The current client data.
        """
        return self.data_store

    def update(self, data: Union[dict, BaseModel]):
        """
        Update the client data store with new data.

        Args:
            data (Union[dict, BaseModel]): The new data to update the store with.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        super().update()
        logging.info(f"Collecting data: {data}")
        try:
            if isinstance(data, BaseModel):
                data_dict = self.to_dict(data)
            elif isinstance(data, dict):
                data_dict = data
            else:
                raise ValueError("Unsupported data type for update")
            
            updated_data = self.data_store.model_copy(update=data_dict)
            self.data_store = updated_data
            logging.info(f"Data in storage: {self.data_store}")
            return True
        except (ValidationError, ValueError) as e:
            logging.warning(f"Failed to update data store: {e}")
            return False
        
    def send_data(self, recipient: Recipient):
        """
        Send the current data store to the specified recipient.

        Args:
            recipient (Recipient): The recipient type, either MEDIATOR or NETWORK.
        """
        if recipient == Recipient.MEDIATOR:
            user_data_dict = self.to_dict(self.data_store)
            self.signals.data_ready_for_mediator.emit(user_data_dict)
        elif recipient == Recipient.NETWORK:
            response = self.network_handler.request_mediator_swap(self.data_store)
            self._handle_mediator_response(response)
        else:
            raise ValueError("Unsupported recipient type")

    def to_dict(self, data: BaseModel) -> dict:
        """
        Serialize the given data object to a dictionary.

        Args:
            data (BaseModel): The data object to serialize.

        Returns:
            dict: The serialized data as a dictionary.
        """
        logging.info("Serializing data...")
        return data.model_dump()

    def to_model(self, dictionary: dict) -> UserData:
        """
        Deserialize the given dictionary to a UserData object.

        Args:
            dictionary (dict): The dictionary to deserialize.

        Returns:
            UserData: The deserialized UserData object.
        """
        logging.info("Deserializing data...")
        return UserData.model_validate(dictionary)

    def _change_running_state(self, state: bool, action: str):
        """
        Change the running state of the client data collector.

        Args:
            state (bool): The new running state.
            action (str): The action that triggered the state change.
        """
        self.is_running = state
        logging.info(f"Client Data Collector {action}")

    def _handle_mediator_response(self, response):
        """
        Handle the response from the mediator.

        Args:
            response: The response from the mediator.
        """
        if response.status_code == 200:
            logging.info("FETCHED IN COLLECTOR")
            logging.info("About to emit new mediator fetched")
            self.signals.new_mediator_fetched.emit(response.json())
        else:
            logging.info(f"Failed to send data to server: {response.status_code}")
