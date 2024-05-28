# src/network_handler/handler.py

import logging
import json
import requests
from src.interfaces.i_network_handler import INetworkHandler
from src.interfaces.i_system_module import ISystemModule
from src.interfaces.data_models import UserData, MediatorData

from requests.models import Response

class NetworkHandler(ISystemModule, INetworkHandler):
    """
    The `NetworkHandler` class is responsible for handling network-related operations within the system. It implements the `ISystemModule` and `INetworkHandler` interfaces, providing a standardized way to manage the network connection and data transmission.

    The class has the following key features:

    - Supports a mock mode to simulate network operations without actually connecting to a server.
    - Provides methods to send and receive data over the network, with support for JSON payloads.
    - Manages the connection status and allows connecting and disconnecting from the configured endpoint.
    - Implements the standard lifecycle methods (`initialize`, `configure`, `start`, `stop`, `reset`, `update`, `status`) to integrate with the overall system.

    The `send_data` method is the primary entry point for sending data over the network. It handles the logic of making the actual HTTP request, with support for both real and mock modes. The method returns the server's response as a dictionary.
    """

    def __init__(self):
        super().__init__()  # Initialize base class properties
        self.connection_status = False
        self.mock_mode = False  # Add mock mode flag
        self.endpoint = "http://127.0.0.1:8000"  # Add endpoint property

    def set_mock_mode(self, mock_mode):
        self.mock_mode = mock_mode

    # Implement abstract methods from ISystemModule
    def initialize(self):
        super().initialize()  # Optionally call base implementation if defined
        logging.info("Network Handler initialized")

    def configure(self, config):
        super().configure(config)  # Optionally call base implementation if defined
        # Configuration logic specific to network handling
        logging.info(f"Network Handler configured with {config}")

    def start(self):
        super().start()  # Start the module
        logging.info("Network Handler started")

    def stop(self):
        super().stop()  # Stop the module
        logging.info("Network Handler stopped")

    def reset(self):
        super().reset()  # Reset the module
        self.disconnect()  # Disconnect on reset
        logging.info("Network Handler reset")

    def update(self):
        super().update()  # Update the module
        # Update logic here
        logging.info("Network Handler updated")

    def status(self):
        return super().status()  # Return the module's status

    # INetworkHandler specific methods
    def send(self, data):
        logging.info(f"Sending data: {data}")
        # Simulate sending data
        return "Data sent"

    def request_mediator_swap(self, data: UserData) -> Response | dict:
        logging.info(f"Requesting mediator with data: {data} to {self.endpoint}")
        try:
            if self.mock_mode:
                # broken
                logging.info("Mock mode enabled - simulating server response")
                response = {"status": "success", "data": "Mock response"}
                logging.info(f"Mock response: {response}")
            else:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    self.endpoint + "/request_new_mediator", json=data.model_dump(), headers=headers
                )
                logging.info(f"Server response: {response.json()}"[:50])
            return response 
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
            return {"status_code": "error", "message": str(e)}

    def send_data(self, data):
        logging.info(f"Sending data: {data} to {self.endpoint}")
        try:
            if self.mock_mode:
                logging.info("Mock mode enabled - simulating server response")
                response = {"status": "success", "data": "Mock response"}
                logging.info(f"Mock response: {response}")
            else:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    self.endpoint + "/user_data", data=json.dumps(data), headers=headers
                )
                response = response.json()
                logging.info(f"Server response: {response}")

            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
            return {"status": "error", "message": str(e)}

    def receive(self):
        logging.info("Receiving data...")
        # Simulate receiving data
        return "Data received"

    def connect(self, endpoint):
        logging.info(f"Connecting to {endpoint}...")
        # Simulate establishing a connection
        self.connection_status = True
        return "Connected"

    def disconnect(self):
        logging.info("Disconnecting...")
        # Simulate disconnecting the connection
        self.connection_status = False
        return "Disconnected"
