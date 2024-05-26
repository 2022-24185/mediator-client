# src/user_interface/workers.py
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, QEventLoop
import logging, time, queue
from src.interfaces.data_models import UserData, ResponseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.mediator_manager.manager import MediatorManagementModule
    from src.client.client import SignalManager
    from src.backends.backend_setup.openai import ChatGPT
    from src.backends.backend_setup.google import Bard
    from src.data_collection.collector import ClientDataCollector


class SendMessageToChatbotWorker(QThread):
    def __init__(self, message, chatbot, signal_manager, is_secret=False):
        super().__init__()
        self.message = message
        self.chatbot = chatbot
        self.signal_manager : 'SignalManager' = signal_manager
        self.is_secret = is_secret

    def run(self):
        # Long-running operation goes here
        if self.message == "" or self.message is None:
            logging.info("Attempted to send an empty message, operation aborted.")
            return
        data = {
            "last_message_time": time.time(),
            "last_message": self.message
        }
        if self.is_secret: 
            self.chatbot.send_message(self.message, is_secret = True)
            self.signal_manager.secret_message_sent.emit(True)
        else: 
            self.chatbot.send_message(self.message)
            self.signal_manager.message_processed_completed.emit(True)
        self.signal_manager.request_data_submission.emit(data)
        self.finished.connect(self.cleanup)

    def cleanup(self):
        # Disconnect signal when the thread has finished its work
        logging.info("SendMessageToChatbotWorker cleanup")
        try:
            self.signal_manager.message_processed_completed.disconnect()
        except TypeError:
            pass
        self.quit()

class WorkerQueue(QThread):
    message_processed = pyqtSignal(str)

    def __init__(self, bard, signal_manager):
        super().__init__()
        self.message_queue = queue.Queue()
        self.bard : 'ChatGPT | Bard' = bard
        self.signal_manager = signal_manager
        self.is_first_message = True
        self.is_secret = False

    def submitted_first_message(self): 
        self.is_first_message = False
        self.bard.is_first_message = False
        self.signal_manager.first_message_submitted.emit(True)

    def add_message(self, message, is_secret=False):
        self.message_queue.put((message, is_secret))
        if not self.isRunning():
            self.start()
        
    def is_empty(self):
        return self.message_queue.empty()

    def run(self):
        while not self.message_queue.empty():
            message, is_secret = self.message_queue.get()
            logging.info(f"Processing message: {message}. Secret? {is_secret}")
            self.is_secret = is_secret
            worker = ProcessNextMessageInQueueWorker(message, is_secret, self.bard, self.signal_manager, self.is_first_message)
            worker.result_signal.connect(self.handle_worker_result)
            worker.start()
            worker.wait()  # Ensure sequential processing
            self.message_queue.task_done()

    def handle_worker_result(self, result):
        self.message_processed.emit(result)

    def handle_response_received(self, response):
        logging.info(f"Response received: {response}")
        logging.info(f"Is first message? {self.is_first_message}")
        if self.is_first_message: 
            self.submitted_first_message()
        logging.info(f"Is secret? {self.is_secret}")
        if not self.is_secret:
                response = "BARD: " + response
                self.signal_manager.request_message_display.emit(response)

class ProcessNextMessageInQueueWorker(QThread): 
    result_signal = pyqtSignal(str)
    def __init__(self, message, is_secret, bard, signal_manager, is_first_message):
        super().__init__()
        self.signal_manager : 'SignalManager' = signal_manager
        self.message = message
        self.is_secret = is_secret
        self.bard = bard
        self.is_first_message = is_first_message
    
    def run(self):
        logging.info("ProcessNextMessageInQueueWorker started")
        result = None
        try:
            if self.is_secret:
                self.message = "SECRET: " + self.message
            else:
                self.message = "USER: " + self.message

            # Wait until the chatbot is ready for the next message using QEventLoop
            if not self.bard.is_ready_for_next_message():
                self.wait_for_bard()

            logging.info("Bard chatbot is ready for next message.")
            self.bard.query(self.message)
            logging.info(f"Sent query to bard")

        except Exception as e:
            logging.error(f"Error during Bard chatbot communication: {e}")
            error_message = "Error communicating with Bard chatbot."
            if not self.is_secret:
                self.signal_manager.request_message_display.emit(error_message)  # Emit the error message

        self.finished.connect(self.cleanup)

    def wait_for_bard(self):
        logging.info("Waiting for Bard to be ready...")
        loop = QEventLoop()
        check_interval = 500  # Check every 1000 milliseconds (1 second)

        def check_ready():
            if self.bard.is_ready_for_next_message():
                loop.quit()

        timer = QTimer()
        timer.timeout.connect(check_ready)
        timer.start(check_interval)

        loop.exec_()  # Block here until loop.quit() is called
        timer.stop()
        logging.info("Bard is now ready.")

    def cleanup(self):
        logging.info("ProcessNextMessageInQueueWorker cleanup")
        self.quit()

class AgentDataUpdateWorker(QThread):
    def __init__(self, data_collector, data, signal_manager):
        super().__init__()
        self.collector: 'ClientDataCollector' = data_collector # type: ignore
        self.data = data
        self.signal_manager : 'SignalManager' = signal_manager # type: ignore
        logging.info(f"Agent Update Worker initialized with data {self.data}")

    def run(self):
        logging.info(f"Agent Update Worker started with data {self.data}")
        success = self.collector.update_database(self.data)
        self.handle_external_update_complete(success)
        logging.info("Worker finished")

    @pyqtSlot(bool)
    def handle_external_update_complete(self, success):
        logging.info(f"Data update complete: {success}")
        try:
            self.signal_manager.data_storage_completed.emit(True)
        except TypeError:
            pass
        self.quit()  # Stop the thread after completion

class MediatorSwitchWorker(QThread):
    def __init__(self, signal_manager, mediator_manager, new_mediator_response : dict):
        super().__init__()
        self.signal_manager : 'SignalManager' = signal_manager # type: ignore
        self.mediator_manager : 'MediatorManagementModule' = mediator_manager
        self.new_mediator_response = ResponseModel.model_validate(new_mediator_response)
        logging.info(f"Mediator switch worker initialized with {self.new_mediator_response.message}")

    def run(self):
        # process the new mediator
        logging.info("Mediator switch started")
        self.mediator_manager.attach_mediator(self.new_mediator_response)

    @pyqtSlot(int)
    def handle_new_mediator_assigned(self, genome_id):
        logging.info(f"Mediator switch complete. New: {genome_id}")
        self.signal_manager.new_mediator_assigned.disconnect(self.handle_new_mediator_assigned)
        self.quit()

class MediatorProcessingWorker(QThread): 
    def __init__(self, data: UserData, mediator_manager, signal_manager):
        super().__init__()
        self.data = data
        self.mediator_manager : 'MediatorManagementModule' = mediator_manager
        self.signal_manager = signal_manager
        self.signal_manager.mediator_processing_completed.connect(self.handle_mediator_processing_completed)

    def run(self):
        logging.info("Mediator processing started")
        # Fetch latest data
        if self.data:
            # Process data with the mediator
            response, is_secret = self.mediator_manager.process_input(self.data)
            logging.info(f"Mediator processing complete: {response}, {is_secret}")
            # Send the response to the chatbot
            if response: 
                self.signal_manager.mediator_processing_completed.emit(response, is_secret)
            else: 
                logging.info("No response from mediator")
                
    def handle_mediator_processing_completed(self, response):
        self.signal_manager.mediator_processing_completed.disconnect(self.handle_mediator_processing_completed)
        self.quit()