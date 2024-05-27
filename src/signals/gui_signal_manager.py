from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class GUISignalManager(QObject):
    """ Handles outgoing signals emitted by the GUI """
    interface_reset_complete = pyqtSignal()
    rating_changed = pyqtSignal(int)
    message_submitted = pyqtSignal(str)
    new_mediator_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.signals = [
            self.interface_reset_complete,
            self.rating_changed,
            self.message_submitted,
            self.new_mediator_requested
        ]