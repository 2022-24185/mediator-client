import pytest
from unittest.mock import patch

from src.chatbot_interface.chatbot import ChatbotInterface
from src.client.client import Client
from src.user_interface.ui import UserInterface
from src.data_collection.collector import ClientDataCollector
from src.mediator_manager.manager import MediatorManagementModule
from src.network_handler.handler import NetworkHandler

@pytest.fixture
def chatbot_interface(mocker):
    mocker.patch('src.backends.backend_setup.discover.get_chrome_version', return_value='90.0')
    bard_mock = mocker.patch('src.backends.gemini_base.Bard', autospec=True)
    bard_instance = bard_mock.return_value
    bard_instance.open.return_value = None
    bard_instance.new_chat.return_value = None
    chatbot = mocker.patch('src.chatbot_interface.chatbot.ChatbotInterface', autospec=True).return_value
    chatbot.bard = bard_instance  # Ensure bard instance is set correctly
    return chatbot, bard_instance

@pytest.fixture
def mock_components(mocker, chatbot_interface):
    mock_ui = mocker.patch('src.user_interface.ui.UserInterface', autospec=True).return_value
    mock_data_collector = mocker.patch('src.data_collection.collector.ClientDataCollector', autospec=True).return_value
    mock_mediator_manager = mocker.patch('src.mediator_manager.manager.MediatorManagementModule', autospec=True).return_value
    mock_network_handler = mocker.patch('src.network_handler.handler.NetworkHandler', autospec=True).return_value
    

    return {
        'ui': mock_ui,
        'ci': chatbot_interface[0],
        'data_collector': mock_data_collector,
        'mediator_manager': mock_mediator_manager,
        'network_handler': mock_network_handler
    }

def test_client_integration(mock_components):
    client = Client()
    client.components = mock_components

    event_type = "command"
    event_data = "fetch information"
    client.handle_event(event_type, event_data)

    mock_components['ui'].handle_event.assert_called_once_with(event_type, event_data)
