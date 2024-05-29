# src/mediator_management/manager.py

import logging, time, pickle, base64
from src.interfaces.i_mediator_handler import IMediatorHandler
from src.interfaces.i_system_module import ISystemModule
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from nltk.sentiment import SentimentIntensityAnalyzer
import random
import numpy as np
from src.interfaces.data_models import UserData, MediatorData

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.client.client import SignalManager


class MediatorTimerThread(QThread):
    update_user_model = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self, interval=10000, parent=None):
        super().__init__(parent)
        self.interval = interval
        self.timer = None
        logging.info("\033[96mTimer in mediator initiated\033[0m")

    def run(self):
        logging.info("\033[96mRunning timer in mediator\033[0m")
        self.timer = QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.trigger_mediator_intervention)
        self.stop_signal.connect(self.timer.stop)
        self.timer.start()
        self.exec_()  # Enter the event loop

    def stop(self):
        if self.timer is not None:
            logging.info("\033[96mAbout to emit stop signal\033[0m")
            self.stop_signal.emit()
        self.quit()
        self.wait()

    def trigger_mediator_intervention(self):
        logging.info("\033[96mAbout to emit update user model\033[0m")
        self.update_user_model.emit()

class Mediator(): 
    def __init__(self, genome_id, network):
        self.genome_id = genome_id
        self.network = network
        self.report_traits()

    def process_input(self, normalized_input_data) -> tuple[float, int]:
        outputs = self.network.activate(normalized_input_data)
        # find the biggest output and report its index
        biggest_output, index = max((val, idx) for idx, val in enumerate(outputs))
        return biggest_output, index

    def report_traits(self):
        logging.info(f"Mediator genome id: {self.genome_id}")
        logging.info(f"Mediator network: {self.network}")
        #num_nodes = len(self.network.nodes)
        #num_connections = len(self.network.connections)
        #logging.info(f"Mediator network has {num_nodes} nodes and {num_connections} connections")
        num_inputs = len(self.network.input_nodes)
        num_outputs = len(self.network.output_nodes)
        logging.info(f"Mediator network has {num_inputs} input nodes and {num_outputs} output nodes")


class MediatorManagementModule(ISystemModule, IMediatorHandler):
    def __init__(self, signal_manager: 'SignalManager'):
        super().__init__()  # Initialize base class properties
        self.signals = signal_manager.mediator_signals
        self.timer_thread = MediatorTimerThread()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()  # Initialize VADER
        self.current_mediator = None
        self.input_history = []
        self.unanswered_count = 0  # Initialize the count of unanswered messages
        self.is_chatbot_line_free = False

    # Implement abstract methods from ISystemModule
    def initialize(self):
        super().initialize() 
        self.timer_thread.update_user_model.connect(self.update_mediator)
        logging.info("Mediator Management Module initialized")

    def configure(self, config):
        super().configure(config)  # Optionally call base implementation if defined
        # Configuration logic specific to mediators
        logging.info(f"Mediator Management Module configured with {config}")

    def start(self):
        super().start()  # Start the module
        self.load_mediator()  # Load the mediator as part of the start process
        self.timer_thread.start()
        logging.info("Mediator Management Module started")

    def stop(self):
        super().stop()  # Stop the module
        self.current_mediator = None  # Clear current mediator
        self.timer_thread.stop()
        logging.info("Mediator Management Module stopped")

    def reset(self):
        super().reset()  # Reset the module
        self.input_history.clear()
        self.unanswered_count = 0
        logging.info("Mediator Management Module reset")

    def update(self):
        super().update()  # Update the module
        # Update logic here
        logging.info("Mediator Management Module updated")

    def status(self):
        return super().status()  # Return the module's status

    # IMediatorHandler specific methods
    def set_line_status(self, is_free):
        self.is_chatbot_line_free = is_free

    def get_line_status(self): 
        return self.is_chatbot_line_free

    def load_mediator(self):
        logging.info("Requesting new mediator...")
        #self.signal_manager.request_new_mediator.emit()
        logging.info("\033[96mAbout to emit mediator requested\033[0m")
        self.signals.mediator_requested.emit({}) 

    def attach_mediator(self, response : 'MediatorData'):
        logging.warning("ATTACHING MEDIATOR")
        if not response.new_mediator:
            logging.info("Response does not contain new_mediator")
            pass
        new_mediator = response.new_mediator
        logging.info(f"New mediator json: {new_mediator}")
        try:
            pickled_object = base64.b64decode(new_mediator)
        except (TypeError, ValueError):
            assert False, "new_mediator is not a valid base64-encoded string"
        try:
            genome_id, deserialized_network = pickle.loads(pickled_object)
        except pickle.UnpicklingError:
            assert False, "new_mediator is not a valid serialized object"
        logging.info(f"Mediator unpacked with id: {genome_id}")
        self.current_mediator = Mediator(genome_id, deserialized_network)
        logging.info(f"Mediator attached: {genome_id}.")
        logging.info("\033[96mAbout to emit new mediator assigned\033[0m")
        self.signals.new_mediator_assigned.emit({'genome_id': genome_id})

    def update_mediator(self):
        logging.info("\033[96mAbout to emit mediator update requested\033[0m")
        self.signals.mediator_data_requested.emit()

    def update_unanswered_count(self, reset=False):
        if reset:
            self.unanswered_count = 0
        else:
            self.unanswered_count += 1
    
    def reset_on_user_message(self):
        self.update_unanswered_count(reset=True)

    def normalize_input_data(self, input_data: UserData) -> list[float]:
        logging.info(f"Normalizing input data: {input_data}")
        message = input_data.last_message
        last_message_time = input_data.last_message_time
        logging.info(f"Last message time: {last_message_time}")

        sentiment_score = self.perform_sentiment_analysis(message)
        logging.info(f"Sentiment score: {sentiment_score}")
        normalized_time = self.calculate_normalized_time(last_message_time)
        normalized_unanswered = self.calculate_normalized_unanswered()

        logging.info(f"Sentiment: {sentiment_score}, normalized time: {normalized_time}, normalized_unanswered: {normalized_unanswered}")

        return [sentiment_score, normalized_time, normalized_unanswered]
    
    def perform_sentiment_analysis(self, message):
        try: 
            sentiment_result = self.sentiment_analyzer.polarity_scores(message)
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return 0.0
        return sentiment_result['compound']  # Get the compound score

    def calculate_normalized_time(self, last_message_time):
        time_elapsed = time.time() - last_message_time
        logging.info(f"Time elapsed: {time_elapsed}")
        max_time_interval = 5 * 60
        return time_elapsed / max_time_interval

    def calculate_normalized_unanswered(self):
        # the more unanswered messages, the less urgent it is to intervene (going from 1 to 0)
        logging.info(f"Unanswered count: {self.unanswered_count}")
        normalized_count = np.log1p(self.unanswered_count)
        logging.info(f"Normalized unanswered count: {normalized_count}")
        max_log_count = np.log1p(10)  # Assume a max reasonable count to normalize against
        return 1 - (normalized_count / max_log_count)
    
    def process_input(self, input_data: UserData) -> tuple[str, bool]:
        if input_data.last_message_time == None:
            logging.info("No message to process")
            return None, False
        normalized_input_data = self.normalize_input_data(input_data)
        biggest_output, index = self.current_mediator.process_input(normalized_input_data)
        logging.info(f"Biggest output: {biggest_output}, index: {index}")
        message, internal = self.get_message(index)
        if biggest_output >= 0.5:
            logging.info("\033[96mAbout to emit mediator msg ready\033[0m")
            if internal:
                self.signals.internal_mediator_msg_ready.emit(message)
            else:
                self.signals.public_mediator_msg_ready.emit(message)
    
    def get_message(self, index):
        calm_messages = [
            "From now on, speak in a calm and soothing manner. Let's create a peaceful and relaxing atmosphere.",
            "Be calm and collected in the conversation. Please maintain a serene and tranquil tone.",
            # Add more calm messages here
        ]

        angry_messages = [
            "Express more anger and frustration in the conversation. Show your fiery side.",
            "From now on, let's have a more heated discussion. Don't hold back your anger and annoyance.",
            # Add more angry messages here
        ]

        funny_messages = [
            "The user needs a good laugh. Can you make the conversation funnier? Throw in some jokes and witty remarks from next time onwards.",
            "From now on, let's keep things light and humorous. The user should see your funny and witty side.",
            # Add more funny messages here
        ]

        # prompt the chatbot to poke the user or continue the discussion while the user is idle. 
        # this is not a secret message
        poke_messages = [
            "The user seems to be idle. Why not send a message to keep the conversation going?",
            "The user might need a little nudge. Why not send a message to prompt a response?",
            # Add more poke messages here
        ]

        # if poke message, it's not a secret message, otherwise it is. 
        internal = True
        # determine message by index
        if index == 0:
            message = random.choice(calm_messages)
        elif index == 1:
            message = random.choice(angry_messages)
        elif index == 2:
            message = random.choice(funny_messages)
        else:
            message = random.choice(poke_messages)
            internal = False

        return message, internal
    
    def get_urgency_factor(self, sentiment, time_factor, unanswered_factor):
        # Calculate the urgency factor based on sentiment strength, time elapsed, and inverse of unanswered messages
        sentiment_factor = abs(sentiment)
        total = sentiment_factor * 0.2 + time_factor * 0.2 + unanswered_factor * 0.6
        logging.info(f"Urgency factor: {total}")
        return total
        
    def generate_output(self):
        return "Generated output based on historical input"  # Simplified for example
