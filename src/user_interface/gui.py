# src/user_interface/gui.py
import logging
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtCore import pyqtSignal, QThread
import logging
from src.user_interface.widgets import InputField, StarRatingWidget, ChatMessageWidget
from src.user_interface.workers import AgentDataUpdateWorker
from src.interfaces.data_models import UserData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.mediator_manager.manager import MediatorManagementModule
    from src.client.client import SignalManager
    from src.backends.backend_setup.openai import ChatGPT


class ChatbotGUI(QWidget):
    # Define a signal that accepts a string, used for updating the display area from other threads
    message_submitted_gui = pyqtSignal(str)  # Define a signal that accepts a string
    submit_data_gui = pyqtSignal(int, float)
    external_rating_update_complete = pyqtSignal(bool)

    def __init__(self, app, signal_manager: 'SignalManager'):
        super().__init__()
        self.app = app
        self.init_ui()
        self.signal_manager = signal_manager
        self.start_time = time.time()  # Initialize start time
        #self.message_submitted_gui.connect(self.display_response)
        logging.info("GUI initialized")

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Input field
        self.input_field = InputField()
        self.input_field.enter_pressed.connect(self.submit_message)
        self.layout.addWidget(self.input_field)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.submit_message)
        self.layout.addWidget(self.send_button)

        # Display area
        self.message_list = QListWidget()
        self.message_list.setWordWrap(True)
        self.message_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.layout.addWidget(self.message_list)

        # Rating system
        self.rating_system = StarRatingWidget()
        self.rating_system.rating_changed.connect(self.submit_rating)
        self.layout.addWidget(self.rating_system)

        # Request new agent button
        self.new_agent_button = QPushButton("New Agent")
        self.new_agent_button.clicked.connect(self.request_new_mediator)
        self.layout.addWidget(self.new_agent_button)

        self.setLayout(self.layout)

    def append_message(self, text, sender):
        message_widget = ChatMessageWidget(text, sender, self)
        list_item = QListWidgetItem(self.message_list)
        list_item.setSizeHint(message_widget.sizeHint())
        self.message_list.addItem(list_item)
        self.message_list.setItemWidget(list_item, message_widget)
        self.message_list.scrollToBottom()  # Scroll to the latest message

    def submit_message(self):
        message = self.input_field.toPlainText().strip()
        if message:
            self.display_input_message(message)
            self.input_field.clear()
            self.signal_manager.request_message_submission.emit(message)

    def submit_rating(self, rating):
        elapsed_time = time.time() - self.start_time
        data = {
            'user_rating': rating, 
            'time_since_startup': elapsed_time
        }
        self.signal_manager.request_data_submission.emit(data)

    def display_response(self, response):
        self.append_message(response, "BARD")
        self.signal_manager.chatbot_response_displayed.emit(True)

    def display_input_message(self, message):
        self.append_message(message, "You")

    def make_rating_callback(self, rating):
        def callback():
            self.request_submit_rating(rating)
        return callback
    
    def request_new_mediator(self):
        # TODO: move responsibility for time keeping to data collector
        time_elapsed = time.time() - self.start_time
        self.signal_manager.request_new_mediator.emit()

    def _show_waiting_message(self):
        logging.info("Waiting for new agent to be available")
        self.message_list.clear()
        self.append_message("Requesting new agent, please wait...", "System")
        self._simulate_agent_setup_delay()

    def _simulate_agent_setup_delay(self):
        delay_thread = QThread()
        delay_thread.run = self.reset_interface
        delay_thread.finished.connect(lambda: self._cleanup_thread(delay_thread))
        self.threads.append(delay_thread)
        delay_thread.start()

    def handle_data_update_complete(self, success):
        self.worker_is_running = False
        if success:
            logging.info("Data update successful before resetting interface")
        else:
            logging.warning("Data update failed before resetting interface")

    def reset_interface(self):
        logging.info("Interface resetting")
        #self.signal_manager.request_data_aggregation.emit()

    def finalize_reset(self):
        logging.info("Interface resetting")
        self.message_list.clear()
        self.rating_system.set_rating(0)
        self.start_time = time.time()
        self.signal_manager.request_message_display.emit("New agent is available to chat.")
        self.app.processEvents()

    def reset_interface(self):
        # Reset the chat interface
        self.message_list.clear()
        self.rating_system.set_rating(0)
        self.start_time = time.time()  # Reset start time

    def closeEvent(self, event):
        event.accept()

# # Example usage of the ChatbotGUI
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     gui = ChatbotGUI(app)
#     gui.show()
#     sys.exit(app.exec_())
