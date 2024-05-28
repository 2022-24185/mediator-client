# src/user_interface/workers.py
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import logging, time, queue
from src.interfaces.data_models import UserData, MediatorData
import debugpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.mediator_manager.manager import MediatorManagementModule
    from src.client.client import SignalManager
    from src.chatbot_interface.chatbot import ChatbotInterface
    from src.data_collection.collector import ClientDataCollector


class SendMessageToChatbotWorker(QThread):
    def __init__(self, message, chatbot, is_secret=False):
        super().__init__()
        self.message = message
        self.chatbot : 'ChatbotInterface' = chatbot
        self.is_secret = is_secret
        logging.info(f"\033[94mSendMessageToChatbotWorker INITIALIZED\033[0m")

    def run(self):
        #debugpy.debug_this_thread()
        # Long-running operation goes here
        logging.info("\033[91mSendMessageToChatbotWorker started\033[0m")
        try: 
            if self.message == "" or self.message is None:
                logging.info("Attempted to send an empty message, operation aborted.")
                return
            data = {
                "last_message_time": time.time(),
                "last_message": self.message
            }
            if self.is_secret: 
                self.chatbot.add_message_to_queue(self.message, is_secret = True)
            else: 
                self.chatbot.add_message_to_queue(self.message)
        finally: 
            self.cleanup()

    def cleanup(self):
        # Disconnect signal when the thread has finished its work
        logging.info("SendMessageToChatbotWorker cleanup")
        self.quit()

class MessageQueue(queue.Queue):
    message_processed = pyqtSignal(str)

    def __init__(self, chatbot):
        super().__init__()
        self.chatbot = chatbot
        self.state = {"is_secret": False, "is_first_message": True, "moving": True}
        logging.info(f"\033[94mMessageQueue initialized\033[0m")

    def submitted_first_message(self): 
        self.state.update({"is_first_message": False})

    def set_moving(self, line_is_free: bool): 
        """Set whether the queue can automatically process messages"""
        self.state.update({"moving": bool})

    def get_state(self): 
        return self.state

    def add_message(self, message: str, is_secret=False):
        logging.info(f"Adding message to queue: {message[:30]}")
        self.put((message, is_secret))
        first = self.state.get("is_first_message")
        moving = self.state.get("moving")
        if first:
            self.process_next_message()
            self.set_moving(False)
        elif moving: 
            self.process_next_message()
            self.set_moving(False)
    
    def process_next_message(self):
        if not self.empty():
            message, is_secret = self.get()
            self.state.update({"is_secret": is_secret})
            logging.info(f"\033[91mProcessing next message: {message[:30]}. Secret? {is_secret}\033[0m")
            worker = ProcessNextMessageInQueueWorker(self.chatbot, message)
            worker.start()
            worker.wait()  # Ensure sequential processing
            self.task_done()
            # Emit signal externally from chatbot_interface after processing
        else: 
            logging.warning("Mistakenly tried to process empty queue")

class ProcessNextMessageInQueueWorker(QThread): 
    result_signal = pyqtSignal(str)
    def __init__(self, chatbot: 'ChatbotInterface', message):
        super().__init__()
        self.message = message
        self.chatbot = chatbot
        logging.info(f"\033[94mProcessNextMessageInQueueWorker initialized with message: {self.message}\033[0m"[:50])
    
    def run(self):
        #debugpy.debug_this_thread()
        logging.info("\033[91mProcessNextMessageInQueueWorker started\033[0m")
        self.chatbot._send_message(self.message)
        self.finished.connect(self.cleanup)

    def cleanup(self):
        logging.info("ProcessNextMessageInQueueWorker cleanup")
        self.quit()

class AgentDataUpdateWorker(QThread):
    def __init__(self, data_collector, data, signal_manager):
        super().__init__()
        self.collector: 'ClientDataCollector' = data_collector # type: ignore
        self.data = data
        self.signal_manager : 'SignalManager' = signal_manager # type: ignore
        logging.info(f"\033[94mAgent Update Worker initialized with data {self.data}\033[0m")

    def run(self):
        #debugpy.debug_this_thread()
        logging.info(f"\033[91mAgent Update Worker started with data {self.data}\033[0m")
        success = self.collector.update_database(self.data)
        self.handle_external_update_complete(success)
        logging.info("Worker finished")

    @pyqtSlot(bool)
    def handle_external_update_complete(self, success):
        logging.info("\033[90mAgentUpdateWorker handle external update complete\033[0m")
        logging.info(f"Data update complete: {success}")
        try:
            logging.info("\033[96mAbout to emit data storage completed from agentupdate worker\033[0m")
            self.signal_manager.data_storage_completed.emit(True)
        except TypeError:
            pass
        self.quit()  # Stop the thread after completion

class MediatorSwitchWorker(QThread):
    def __init__(self, signal_manager, mediator_manager, new_mediator_response : dict):
        super().__init__()
        self.signal_manager : 'SignalManager' = signal_manager # type: ignore
        self.mediator_manager : 'MediatorManagementModule' = mediator_manager
        self.new_mediator_response = MediatorData.model_validate(new_mediator_response)
        logging.info(f"Mediator switch worker initialized with {self.new_mediator_response.message}"[:50])

    def run(self):
        #debugpy.debug_this_thread()
        logging.info("\033[91mMediator switch started\033[0m")
        self.mediator_manager.attach_mediator(self.new_mediator_response)

    @pyqtSlot(int)
    def handle_new_mediator_assigned(self, genome_id):
        logging.info("\033[90mMediatorSwitchWorker handle new mediator assigned\033[0m")
        logging.info(f"Mediator switch complete. New: {genome_id}")
        self.signal_manager.new_mediator_assigned.disconnect(self.handle_new_mediator_assigned)
        self.quit()

class MediatorProcessingWorker(QThread): 
    def __init__(self, data: UserData, mediator_manager, signal_manager: 'SignalManager'):
        super().__init__()
        self.data = data
        self.mediator_manager : 'MediatorManagementModule' = mediator_manager
        self.signals = signal_manager.mediator_signals
        self.signal_manager.mediator_processing_completed.connect(self.handle_mediator_processing_completed)
        logging.info(f"\033[94mMediator processing worker initialized with data {self.data}\033[0m"[:50])

    def run(self):
        #debugpy.debug_this_thread()
        logging.info("\033[91mMediator processing started\033[0m")
        if self.data:
            response, is_secret = self.mediator_manager.process_input(self.data)
            logging.info(f"Mediator processing complete: {response}, {is_secret}")
            if response: 
                logging.info("\033[98mAbout to emit mediator msg ready\033[0m")
                self.signals.mediator_msg_ready.emit(response, is_secret)
            else: 
                logging.info("No response from mediator")
                
    def handle_mediator_processing_completed(self, response):
        logging.info("\033[90mMediatorProcessingWorker handle mediator processing completed\033[0m")
        self.signal_manager.mediator_processing_completed.disconnect(self.handle_mediator_processing_completed)
        self.quit()