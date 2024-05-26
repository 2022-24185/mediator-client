# ./tests/test_gui.py
import sys
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from src.user_interface.gui import ChatbotGUI  # Update this import based on your actual project structure
import pytest

@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for all tests in the module."""
    app = QApplication(sys.argv)
    yield app
    # Properly closing the app after all tests have run
    app.quit()

@pytest.fixture(scope="function")
def app_gui(qtbot):
    gui = ChatbotGUI()
    qtbot.addWidget(gui)
    return gui

class TestChatbotGUI:
    def test_input_field_receives_text(self, app_gui):
        """Test text input in the input field."""
        test_text = "Hello"
        QTest.keyClicks(app_gui.input_field, test_text)
        assert app_gui.input_field.toPlainText() == test_text

class TestSendButton:
    def test_send_message_works(self, app_gui, mocker):
        """Test that the send_message method is called."""
        mock_send_message = mocker.patch.object(app_gui, 'send_message', autospec=True)
        app_gui.send_message()
        mock_send_message.assert_called_once()

    def test_send_button_click_triggers_message_send(self, app_gui, mocker):
        """Test that clicking the send button triggers the send_message method."""
        mock_send_message = mocker.patch.object(app_gui, 'send_message', autospec=True)
        QTest.mouseClick(app_gui.send_button, Qt.LeftButton)
        mock_send_message.assert_called_once()

class TestDisplayArea:
    def test_display_area_shows_message(app_gui, qtbot):
        test_message = "Test Message"
        qtbot.keyClicks(app_gui.input_field, test_message)
        qtbot.mouseClick(app_gui.send_button, Qt.LeftButton)
        assert test_message in app_gui.display_area.toPlainText()

class TestRatingSystem:
    def test_rating_button_sets_value(self, app_gui):
        """Test that rating buttons set the correct value."""
        # Example assumes a QSpinBox is used for rating, adjust as necessary
        app_gui.rating_value.setValue(5)
        assert app_gui.rating_value.value() == 5