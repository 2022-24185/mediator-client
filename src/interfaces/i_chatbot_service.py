from abc import ABC, abstractmethod

class IChatbotService(ABC):
    @abstractmethod
    def initialize_connection(self):
        """
        Initializes the connection to the chatbot service.
        This method should handle any setup necessary for connecting to the chatbot.
        """
        pass

    @abstractmethod
    def close_connection(self):
        """
        Closes the connection to the chatbot service.
        This should ensure that all resources are cleanly released.
        """
        pass

    @abstractmethod
    def add_message_to_queue(self, message: str) -> str:
        """
        Sends a message to the chatbot and returns the response.
        :param message: str - The message to send to the chatbot.
        :return: str - The chatbot's response.
        This method should handle sending a message and receiving the response from the chatbot.
        """
        pass

    @abstractmethod
    def handle_chatbot_event(self, event: dict):
        """
        Handles specific events from the chatbot.
        :param event: dict - Event data from the chatbot.
        This could include handling session starts, errors, or other chatbot-specific events.
        """
        pass

    @abstractmethod
    def update_settings(self, settings: dict):
        """
        Updates settings or configurations for the chatbot.
        :param settings: dict - A dictionary of settings to apply to the chatbot service.
        This method allows dynamic adjustments to the chatbot's operation, such as changing thresholds or behaviors.
        """
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """
        Retrieves the current status of the chatbot.
        :return: dict - A dictionary representing the current status and any relevant metrics or states.
        This method provides insights into the chatbot's current operational state.
        """
        pass
