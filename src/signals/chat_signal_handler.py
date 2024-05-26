from src.interfaces.i_signal_handler import BaseSignalHandler
from src.user_interface.workers import SendMessageToChatbotWorker

class ChatSignalHandler(BaseSignalHandler):
    def __init__(self, signal_manager, gui, chatbot_interface, start_background_modules):
        self.gui = gui
        self.chatbot_interface = chatbot_interface
        self.start_background_modules = start_background_modules
        super().__init__(signal_manager)

    def connect_signals(self):
        self.signal_manager.request_message_display.connect(self.handle_display_message)
        self.signal_manager.chatbot_response_retrieved.connect(self.handle_response_retrieved)
        self.signal_manager.request_message_submission.connect(self.handle_message_submission)
        self.signal_manager.first_message_submitted.connect(self.handle_first_message_submitted)

    def handle_display_message(self, message):
        self.gui.display_response(message)

    def handle_response_retrieved(self, response):
        self.chatbot_interface.handle_response_received(response)

    def handle_message_submission(self, message):
        self.thread = SendMessageToChatbotWorker(message, self.chatbot_interface, self.signal_manager)
        self.thread.start()

    def handle_first_message_submitted(self, is_submitted):
        self.start_background_modules()
