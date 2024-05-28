from PyQt5.QtCore import pyqtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from src.interfaces.data_models import UserData, ResponseModel
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.client.client import SignalManager
    from src.mediator_manager.manager import MediatorManagementModule

class MediatorSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the MediatorManager"""
    def __init__(self, signal_manager : 'SignalManager', manager):
        self.chat_signals = signal_manager.chat_signals
        self.collector_signals = signal_manager.collector_signals
        self.manager : 'MediatorManagementModule' = manager
        super().__init__(signal_manager, manager)

    def connect_signals(self):
        self.chat_signals.is_line_free.connect(self.handle_is_line_free)
        self.collector_signals.data_ready_for_mediator.connect(self.handle_data_received)
        self.collector_signals.new_mediator_fetched.connect(self.handle_new_mediator_fetched)

    @pyqtSlot(bool)
    def handle_is_line_free(self, is_free : bool):
        logging.info("\033[90mMediatorSignalHandler handle is line free\033[0m")
        logging.info(f"Is line free: {is_free}")
        if is_free:
            self.manager.set_line_status(is_free)

    @pyqtSlot(dict)
    def handle_data_received(self, data : dict):
        logging.info("\033[90mMediatorSignalHandler handle data received\033[0m")
        mediator_data = UserData.model_validate(data)
        logging.info(f"Data received: {str(mediator_data.model_dump_json)}")
        self.manager.process_input(mediator_data)

    @pyqtSlot(dict)
    def handle_new_mediator_fetched(self, mediator : dict):
        logging.info("\033[90mMediatorSignalHandler handle new mediator fetched\033[0m")
        mediator_data = ResponseModel.model_validate(mediator)
        self.manager.attach_mediator(mediator_data)