# src/interfaces/i_data_collector.py

class IDataCollector:
    def update_agent_data(self, data):
        """Collect and store data."""
        pass

    def send_data(self):
        """Prepare and send collected data to a specified target or storage."""
        pass
