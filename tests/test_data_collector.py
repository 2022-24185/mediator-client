# tests/test_data_collector.py

import pytest
from src.data_collection.collector import ClientDataCollector

class TestDataCollector:
    def setup_method(self):
        self.collector = ClientDataCollector()

    def test_collect_data(self):
        data = {"event": "click", "details": {"x": 100, "y": 200}}
        self.collector.update_agent_data(data)
        assert data in self.collector.data_store

    def test_send_data(self):
        self.collector.update_agent_data({"event": "click", "details": {"x": 100, "y": 200}})
        serialized_data = self.collector.send_data()
        assert isinstance(serialized_data, str) and "event" in serialized_data

    def test_serialize_deserialize(self):
        data = [{"event": "click", "details": {"x": 100, "y": 200}}]
        serialized = self.collector.serialize(data)
        assert isinstance(serialized, str)
        deserialized = self.collector.deserialize(serialized)
        assert deserialized == data
