# src/user_interface/widgets.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from typing import List

class StarRatingWidget(QWidget):
    rating_changed: pyqtSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.layout: QHBoxLayout = QHBoxLayout()
        self.stars: List[QPushButton] = []
        self.current_rating: int = 0

        # Create 5 star buttons
        for i in range(1, 6):
            self.create_star_button(i)

        self.setLayout(self.layout)

    def create_star_button(self, index: int) -> None:
        """Create a star button and add it to the layout."""
        btn: QPushButton = QPushButton("☆")
        btn.setStyleSheet("font-size: 24px; color: gray;")  # Default style for unselected stars
        btn.clicked.connect(lambda _, i=index: self.set_rating(i))
        self.layout.addWidget(btn)
        self.stars.append(btn)

    def set_rating(self, rating):
        self.current_rating = rating
        for i, star in enumerate(self.stars, start=1):
            if i <= rating:
                star.setText("★")
                star.setStyleSheet("font-size: 24px; color: yellow;")  # Yellow color for selected stars
            else:
                star.setText("☆")
                star.setStyleSheet("font-size: 24px; color: gray;")  # Gray color for unselected stars
        self.rating_changed.emit(rating)

class ChatMessageWidget(QWidget):
    def __init__(self, text, sender, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)  # Add some padding around the text
        self.message_label = QLabel(text)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(self.get_style(sender))
        self.layout.addWidget(self.message_label)
        self.setLayout(self.layout)
        self.adjustSize()  # Ensure the widget size is adjusted to fit the content

    def get_style(self, sender):
        if sender == "BARD":
            return """
                QLabel { 
                    background-color: #D1E8E2; 
                    color: black; 
                    border-radius: 15px; 
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                }
            """
        else:
            return """
                QLabel { 
                    background-color: #FFEAD4; 
                    color: black; 
                    border-radius: 15px; 
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                }
            """

    def sizeHint(self):
        # Calculate the size based on the parent width and the content
        max_width = self.parent().width() - 40  # Adjust for padding
        self.message_label.setMaximumWidth(max_width)
        return self.message_label.sizeHint() + QSize(20, 10)  # Add padding to the size hint

class InputField(QTextEdit):
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)
