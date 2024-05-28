# src/interfaces/i_serializable.py

class ISerializable:
    def to_dict(self, data):
        """Convert data into a format suitable for transmission or storage."""
        pass

    def to_model(self, serialized_data):
        """Convert data back from the storage or transmission format to a usable format."""
        pass
