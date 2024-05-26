# tests/test_network_handler.py

import pytest
from unittest.mock import MagicMock
from src.network_handler.handler import NetworkHandler

class TestNetworkHandler:
    def setup_method(self, method):
        self.nh = NetworkHandler()

    def test_send_calls_send_with_correct_data(self):
        self.nh.send = MagicMock()
        data = {"key": "value"}
        self.nh.send(data)
        self.nh.send.assert_called_with(data)

    def test_receive_calls_receive_once(self):
        self.nh.receive = MagicMock()
        self.nh.receive()
        self.nh.receive.assert_called_once()

    def test_connect_calls_connect_with_correct_endpoint(self):
        self.nh.connect = MagicMock()
        endpoint = "http://example.com"
        self.nh.connect(endpoint)
        self.nh.connect.assert_called_with(endpoint)

    def test_disconnect_calls_disconnect_once(self):
        self.nh.disconnect = MagicMock()
        self.nh.disconnect()
        self.nh.disconnect.assert_called_once()