import pytest
from src.client.client import Client
from src.data_collection.collector import ClientDataCollector
from src.mediator_manager.manager import MediatorManagementModule
from src.network_handler.handler import NetworkHandler
from src.user_interface.ui import UserInterface

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

@pytest.fixture
def client_and_components(mocker, mock_components):
    client = Client()
    # Replace components with mocks using pytest-mocker
    client.components = mock_components
    return client

# when client file is started, all components should automatically initialize
def test_initialize_on_startup(client_and_components):
    client = client_and_components
    for component in client.components.values():
        component.initialize.assert_called_once()

def test_initialization(client_and_components):
    client = client_and_components
    client.initialize()

    for component in client.components.values():
        component.initialize.assert_called_once()

def test_configuration(client_and_components):
    client = client_and_components
    config = {name: {} for name in client.components.keys()}

    client.configure(config)

    for name, component in client.components.items():
        component.configure.assert_called_once_with(config[name])

def test_start(client_and_components):
    client = client_and_components
    client.start()

    for component in client.components.values():
        component.start.assert_called_once()

    assert client.is_running, "Client should be marked as running after start."

def test_stop(client_and_components):
    client = client_and_components
    client.stop()

    for component in client.components.values():
        component.stop.assert_called_once()

    assert not client.is_running, "Client should be stopped."

def test_reset(client_and_components):
    client = client_and_components
    client.reset()

    for component in client.components.values():
        component.reset.assert_called_once()
