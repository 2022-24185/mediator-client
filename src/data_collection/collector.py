# src/data_collection/collector.py

import logging
from typing import TYPE_CHECKING, Union

from pydantic import BaseModel, ValidationError

from src.interfaces.i_data_collector import IDataCollector
from src.interfaces.i_serializable import ISerializable
from src.interfaces.i_system_module import ISystemModule
from src.interfaces.data_models import UserData

if TYPE_CHECKING:
    from src.network_handler.handler import NetworkHandler
    from src.client.client import SignalManager
    from src.signals.collector_signal_manager import CollectorSignalManager


class ClientDataCollector(ISystemModule, IDataCollector, ISerializable):
    def __init__(self, signal_manager: "SignalManager"):
        super().__init__()
        self.data_store = UserData(genome_id=0, time_since_startup=0.0, user_rating=0)
        self.network_handler: "NetworkHandler" = None  # type: ignore
        self.signals: "CollectorSignalManager" = signal_manager.collector_signals
        self.is_running = False

    def initialize(self):
        super().initialize()
        logging.info("Client Data Collector initialized")

    def set_network_handler(self, network_handler: "NetworkHandler"):
        self.network_handler = network_handler

    def set_signal_holder(self, signal_holder: "SignalManager"):
        self.signal_holder = signal_holder

    def configure(self, config):
        super().configure(config)
        logging.info(f"Client Data Collector configured with {config}")

    def start(self):
        self._change_running_state(True, "started")

    def stop(self):
        self._change_running_state(False, "stopped")

    def reset(self):
        super().reset()
        self.data_store = UserData(genome_id=0, time_since_startup=0.0, user_rating=0)
        logging.info("Client Data Collector reset")

    def update(self):
        super().update()
        logging.info("Client Data Collector updated")

    def status(self):
        return super().status()

    def collect_data_for_mediator(self):
        data = self.get_data()
        data_for_transfer = self.to_dict(data)
        logging.info("About to emit data ready for mediator")
        self.signals.data_ready_for_mediator.emit(data_for_transfer)

    def get_data(self) -> UserData:
        return self.data_store

    def update_database(self, data: Union[dict, BaseModel]):
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

    def send_data(self):
        serialized_data = self.to_dict(self.data_store)
        self.network_handler.send_data(serialized_data)

    def request_mediator_with_stored_data(self):
        logging.info("COLLECTOR FETCHING DATA")
        self._ensure_data_store_type()
        response = self.network_handler.request_mediator_swap(self.data_store)
        self._handle_mediator_response(response)

    def to_dict(self, data: BaseModel) -> dict:
        logging.info("Serializing data...")
        return data.model_dump()

    def to_model(self, dictionary: dict) -> UserData:
        logging.info("Deserializing data...")
        return UserData.model_validate(dictionary)

    def _change_running_state(self, state: bool, action: str):
        self.is_running = state
        logging.info(f"Client Data Collector {action}")

    def _ensure_data_store_type(self):
        if not isinstance(self.data_store, UserData):
            raise ValueError("Data store is not of type UserData")

    def _handle_mediator_response(self, response):
        if response.status_code == 200:
            logging.info("FETCHED IN COLLECTOR")
            logging.info("About to emit new mediator fetched")
            self.signals.new_mediator_fetched.emit(response.json())
        else:
            logging.info(f"Failed to send data to server: {response.status_code}")
