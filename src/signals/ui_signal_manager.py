from PyQt5.QtCore import QObject, pyqtSignal
from src.interfaces.i_signal_manager import BaseSignalManager

class UISignalManager(QObject):
    request_data_submission = pyqtSignal(dict)
    interface_reset_complete = pyqtSignal()
    rating_changed = pyqtSignal(int)
    enter_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.signals = [
            self.request_data_submission,
            self.interface_reset_complete,
            self.rating_changed,
            self.enter_pressed
        ]