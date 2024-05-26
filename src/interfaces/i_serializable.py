# src/interfaces/i_serializable.py

class ISerializable:
    def serialize(self, data):
        """Convert data into a format suitable for transmission or storage."""
        pass

    def deserialize(self, serialized_data):
        """Convert data back from the storage or transmission format to a usable format."""
        pass
