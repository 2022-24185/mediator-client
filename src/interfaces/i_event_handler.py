# src/interfaces/i_event_handler.py

from abc import ABC, abstractmethod


class IEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event_type, event_data):
        """Handle an event given its type and associated data."""
        pass

    @abstractmethod
    def subscribe_to_event(self, event_type, handler_function):
        """Subscribe to an event type with a handler function."""
        pass

    @abstractmethod
    def unsubscribe_from_event(self, event_type):
        """Unsubscribe to an event type."""
        pass