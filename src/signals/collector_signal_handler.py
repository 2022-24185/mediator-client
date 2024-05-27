from PyQt5.QtCore import pyQtSlot
from src.interfaces.i_signal_handler import BaseSignalHandler
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from src.data_collection.collector import ClientDataCollector

class CollectorSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the ClientDataCollector"""
    def __init__(self, signal_manager, collector):
        self.collector : 'ClientDataCollector' = collector
        super().__init__(signal_manager)

    def connect_signals(self):
        self.signal_manager.rating_changed.connect(self.handle_data_submission)
        self.signal_manager.mediator_requested.connect(self.handle_data_submission)
        self.signal_manager.mediator_assigned.connect(self.handle_data_submission)
        self.signal_manager.secret_chatbot_msg_received.connect(self.handle_data_submission)
        self.signal_manager.dialogue_chatbot_msg_received(self.handle_data_submission)

    @pyQtSlot(dict, Optional[bool])
    def handle_data_submission(self, data: dict, send_data_to_server = False):
        logging.info(f"Received data: {data}")
        self.collector.update_database(data)
        if send_data_to_server: 
            self.collector.send_data_to_server()