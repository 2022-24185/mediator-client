# ./tests/test_ui.py
import pytest
from PyQt5.QtWidgets import QApplication
from src.user_interface.ui import UserInterface

@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for all tests"""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def user_interface(qapp):
    """Fixture to create UserInterface with QApplication"""
    return UserInterface(app=qapp)

def test_handle_event_calls_subscribed_handler(mocker, user_interface):
    # Create a mocker spy to simulate an event handling function
    event_handler_mock = mocker.Mock(name='event_handler_mock')
    # Subscribe the mock handler to a specific event type
    user_interface.subscribe_to_event('click', event_handler_mock)
    # Trigger the event
    user_interface.handle_event('click', {'x': 10, 'y': 20})
    # Assert that the mock was called correctly
    event_handler_mock.assert_called_once_with({'x': 10, 'y': 20})

def test_subscribe_to_event_calls_handler_on_event(mocker, user_interface):
    event_type = 'keydown'
    handler_function = mocker.Mock(name='handler_function')
    # Subscribe the handler to the event
    user_interface.subscribe_to_event(event_type, handler_function)
    # Trigger the event
    user_interface.handle_event(event_type, {'key': 'Enter'})
    # Assert the handler was called with correct data
    handler_function.assert_called_with({'key': 'Enter'})
