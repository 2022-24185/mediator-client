from PyQt5.QtCore import pyqtSlot
from functools import partial
from src.interfaces.i_signal_handler import BaseSignalHandler
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from src.data_collection.collector import ClientDataCollector
    from src.client.client import SignalManager

class CollectorSignalHandler(BaseSignalHandler):
    """Deals with incoming signals for the ClientDataCollector"""
    def __init__(self, signal_manager : 'SignalManager', collector):
        self.gui_signals = signal_manager.gui_signals
        self.mediator_signals = signal_manager.mediator_signals
        self.chat_signals = signal_manager.chat_signals
        self.collector : 'ClientDataCollector' = collector
        super().__init__(signal_manager, collector)

    def connect_signals(self):
        self.gui_signals.rating_changed.connect(self.handle_data_submission) # int, rating
        self.gui_signals.new_mediator_requested.connect(lambda data: self.handle_data_submission(data, True)) 

        self.mediator_signals.new_mediator_assigned.connect(self.handle_data_submission)
        self.mediator_signals.mediator_data_requested.connect(self.handle_data_requested)
        self.mediator_signals.mediator_requested.connect(lambda data: self.handle_data_submission(data, True))
        #self.chat_signals.secret_chatbot_msg_received.connect(self.handle_data_submission)
        self.chat_signals.dialogue_user_msg_received.connect(self.handle_data_submission)
        self.chat_signals.dialogue_chatbot_msg_received.connect(self.handle_data_submission)

    @pyqtSlot(dict)
    def handle_data_submission(self, data: dict, request_mediator = False):
        logging.info("\033[90mCollectorSignalHandler handle data submission\033[0m")
        logging.info(f"RESUESTING MEDIATOR?? {request_mediator}")
        logging.info(f"Received data: {data}")
        # remove entry "is_secret" from dict if it exists
        #if "is_secret" in data: 
            #data.pop("is_secret")
        self.collector.update_database(data)
        if request_mediator: 
            self.collector.request_mediator_with_stored_data()

    @pyqtSlot()
    def handle_data_requested(self):
        logging.info("\033[90mCollectorSignalHandler handle data requested\033[0m")
        self.collector.collect_data_for_mediator()
    