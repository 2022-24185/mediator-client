# src/interfaces/i_network_handler.py

class INetworkHandler:
    def send(self, data):
        """Send data over the network."""
        pass

    def receive(self):
        """Receive data from the network."""
        pass

    def connect(self, endpoint):
        """Establish a connection to a network endpoint."""
        pass

    def disconnect(self):
        """Disconnect from the network endpoint."""
        pass
