from typing import TYPE_CHECKING
from src.chatbot_interface.chatbot import ChatbotState
from src.signals.chat_signal_manager import ChatbotState

if TYPE_CHECKING:
    from src.client.client import SignalManager

class ChatStateManager():
    def __init__(self, signal_manager: 'SignalManager'):
        super().__init__()
        self.signals = signal_manager.chat_signals
        self.state = ChatbotState.INITIAL

    def update_state(self, new_state: ChatbotState):
        self.state = new_state
        self.emit_signal_for_state(new_state)
        print(f"State updated to: {new_state}")

    def emit_signal_for_state(self, state: ChatbotState):
        if state == ChatbotState.INITIAL:
            self.signals.state_initial.emit()
        elif state == ChatbotState.CONNECTING:
            self.signals.state_connecting.emit()
        elif state == ChatbotState.CONNECTED:
            self.signals.state_connected.emit()
        elif state == ChatbotState.SENDING_INSTRUCTIONS:
            self.signals.state_sending_instructions.emit()
        elif state == ChatbotState.INSTRUCTIONS_SENT:
            self.signals.state_instructions_sent.emit()
        elif state == ChatbotState.READYING_MESSAGE:
            self.signals.state_readying_message.emit()
        elif state == ChatbotState.API_BUSY:
            self.signals.state_api_busy.emit()
        elif state == ChatbotState.API_READY: 
            self.signals.state_api_ready.emit()
        elif state == ChatbotState.IDLE:
            self.signals.state_idle.emit()
        elif state == ChatbotState.ERROR:
            self.signals.state_error.emit()

    def is_state(self, state: ChatbotState) -> bool:
        return self.state == state
