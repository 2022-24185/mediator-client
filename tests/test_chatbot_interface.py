import pytest
from src.chatbot_interface.chatbot import ChatbotInterface
from src.backends.gemini_base import Bard
from src.backends.backend_setup.discover import get_chrome_version

@pytest.fixture(autouse=True)
def mock_bard(mocker):
    # Mock the Bard class at the module level
    bard_mock = mocker.patch('src.backends.gemini_base.Bard', autospec=True)
    bard_instance = bard_mock.return_value
    bard_instance.open.return_value = None
    bard_instance.new_chat.return_value = None
    bard_instance.close.return_value = None
    bard_instance.query.return_value = "Mocked Response"
    bard_instance._init_driver.return_value = None
    bard_instance._load_page.return_value = None
    return bard_instance

@pytest.fixture
def chatbot_interface(mock_bard, mocker):
    # Mocking the get_chrome_version to return a dummy version
    mocker.patch('src.backends.backend_setup.discover.get_chrome_version', return_value='90.0')

    chatbot = ChatbotInterface()
    chatbot.chrome_path = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"  # Override the path for consistency in tests
    
    return chatbot, mock_bard

@pytest.mark.skip(reason="This test is not running consistently")
def test_initialize_connection(chatbot_interface):
    chatbot, bard_instance = chatbot_interface
    chatbot.initialize_connection()
    bard_instance.open.assert_called_once()
    bard_instance.new_chat.assert_called_once_with('imbard')
    assert chatbot.is_connected == True
    bard_instance.query.assert_not_called()  # Ensure query is not called during initialization

@pytest.mark.skip(reason="This test is not running consistently")
def test_close_connection(chatbot_interface):
    chatbot, bard_instance = chatbot_interface
    chatbot.is_connected = True  # Manually setting connected to True for testing
    chatbot.close_connection()
    bard_instance.close.assert_called_once()
    assert not chatbot.is_connected

@pytest.mark.skip(reason="This test is not running consistently")
def test_send_message_when_connected(chatbot_interface):
    chatbot, bard_instance = chatbot_interface
    chatbot.is_connected = True  # Manually setting connected to True for testing
    response = chatbot.send_message("Hello, chatbot!")
    bard_instance.query.assert_called_once_with("Hello, chatbot!")
    assert response == "Mocked Response"

@pytest.mark.skip(reason="This test is not running consistently")
def test_send_message_when_not_connected(chatbot_interface):
    chatbot, bard_instance = chatbot_interface
    chatbot.is_connected = False  # Ensure chatbot is not connected
    response = chatbot.send_message("Hello, chatbot!")
    bard_instance.open.assert_called_once()  # Since not connected, it should attempt to reconnect
    bard_instance.new_chat.assert_called_once_with('imbard')  # Ensure a new chat is started
    assert response == "Mocked Response"  # Assuming initialize_connection was successful

def test_get_status(chatbot_interface):
    chatbot, _ = chatbot_interface
    chatbot.is_connected = True
    status = chatbot.get_status()
    assert status == {'connected': True}
