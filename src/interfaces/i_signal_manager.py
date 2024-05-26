from PyQt5.QtCore import QObject, pyqtSignal
from typing import List


class BaseSignalManager(QObject):
    def __init__(self):
        super().__init__()
        self.signals : List[pyqtSignal] = None

    def get_signals_str(self): 
        """Return the list of names associated with the signals"""
        return [signal.name for signal in self.signals]

    def get_signals(self): 
        """Return the list of signals"""
        return self.signals