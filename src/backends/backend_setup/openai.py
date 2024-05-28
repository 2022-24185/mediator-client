from ..selenium_service import SeleniumService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from enum import Enum

from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

import sys # exit
import time
import datetime
import logging
from typing import Optional, TYPE_CHECKING
from selenium.webdriver.remote.webelement import WebElement
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import debugpy

if TYPE_CHECKING:
    from src.client.client import SignalManager

# Create a new logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handlers
info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter("\033[92m %(asctime)s - %(levelname)s: %(message)s \033[0m"))

warning_handler = logging.StreamHandler()
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(logging.Formatter("\033[93m %(asctime)s - %(levelname)s: %(message)s \033[0m"))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("\033[91m %(asctime)s - %(levelname)s: %(message)s \033[0m"))

# Add handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)

class Action(Enum):
    CLICK = "click"
    ENTER_TEXT = "enter text"
    ENTER_TEXT_BLOCK = "enter text block"
    RETRIEVE_TEXT = "retrieve text"

class Element(Enum):
    TXTFLD_PROMPT = "//textarea[@id='prompt-textarea']"
    BTN_SEND = "//button[@data-testid='fruitjuice-send-button']"
    TXT_RESPONSE_ITEMS = "((//div[contains(@class, 'agent-turn')])[last()]//button[contains(@class, 'text-token-text-secondary')])[last()]"
    TXT_RESPONSE_BLOCK = "(//div[@data-message-author-role='assistant' and contains(@class, 'text-message')])[last()]"
    BTN_PREFERENCES = "//button[contains(@class,'flex w-full')]"
    BTN_VERSION_SELECTOR = "//div[@aria-haspopup='menu']"
    BTN_NEW_CHAT = "//nav[@aria-label='Chat history']//button[contains(@class, 'h-10')]"
    BTN_NEW_CHAT_COLLAPSED = "//button[contains(@class, 'h-10') and contains(@class, 'rounded-lg')]"


class JSClickException(Exception):
    """Exception raised when a JavaScript click fails."""
    pass

class ElementLocatorWorker(QThread):
    element_found = pyqtSignal(object, str, str)  # E.g., (WebElement, locator, extra)
    error_occurred = pyqtSignal(str, str)  # E.g., (error_message, locator)

    def __init__(self, _parent: 'ChatGPT', driver, locator: Enum, extra=None):
        super().__init__()
        self.driver = driver
        self.locator = locator.value
        self.extra = extra
        self.is_secret = False
        self._parent = _parent
        logging.info("\033[94mElementLocatorWorker INITIALIZED\033[0m")

    def run(self):
        #debugpy.debug_this_thread()
        logging.info(f"\033[92mRunning Locator for: {self.locator}\033[0m")
        timeout = 100
        if self.locator == "//textarea[@id='prompt-textarea']":
            timeout = 20
        try:
            element = WebDriverWait(self.driver, timeout=timeout).until(
                EC.presence_of_element_located((By.XPATH, self.locator))
            )
            logging.info(f"Element located with locator: {self.locator}")
            #logging.info(f"Element: {element.get_attribute('outerHTML')}")
            logging.info("\033[96mAbout to emit element found\033[0m")
            self.element_found.emit(element, self.locator, self.extra)
            logging.info("Signal emitted from element locator")
        except TimeoutException:
            logging.info("\033[96mAbout to emit error occured\033[0m")
            self.error_occurred.emit("Timeout while locating element", self.locator)
        except Exception as e:
            logging.info("\033[96mAbout to emit error occured\033[0m")
            logging.error(str(e))
            self.error_occurred.emit(f"Exception: {str(e)}", self.locator)
        finally: 
            self.cleanup()

    def cleanup(self):
        # Disconnect all signals here
        self.element_found.disconnect(self._parent.handle_element_found)
        self.error_occurred.disconnect(self._parent.handle_error)
        logging.info("SIGNALS DISCONNECTED: LOCATOR")


class ActionExecutorWorker(QThread):
    action_completed = pyqtSignal(object, str)  # E.g., (action enum, message)
    error_occurred = pyqtSignal(str, str)  # E.g., (error_message, action)

    def __init__(self, _parent: 'ChatGPT', driver, element, action, value=None):
        super().__init__()
        self.driver = driver
        self.element = element
        self.action = action
        self.value = value
        self.is_secret = False
        self._parent = _parent
        logging.info("\033[94mActionExecutorWorker INITIALIZED\033[0m")

    def run(self):
        #debugpy.debug_this_thread()
        logging.info(f"\033[92mRunning Action: {self.action}\033[0m")
        self.success_msg = f"Action '{self.action}' completed successfully."
        try:
            if self.action == Action.CLICK:
                self.element.click()
            elif self.action == Action.ENTER_TEXT:
                self.element : WebElement
                self.element.clear()
                self.element.send_keys(self.value + Keys.ENTER)
            elif self.action == Action.ENTER_TEXT_BLOCK: 
                self.element : WebElement
                self.element.clear()
                self.driver.execute_script("arguments[0].value = arguments[1];", self.element, self.value)
                self.element.send_keys(Keys.ENTER)
                self.element.send_keys(Keys.ENTER)
            elif self.action == Action.RETRIEVE_TEXT:
                #logging.info(f"element is {self.element.get_attribute('outerHTML')}")
                text_content = self.element.get_attribute('textContent')
                text_content.strip()  # Strip to remove any leading/trailing whitespace
                self.success_msg = text_content
            logging.info(f"Action '{self.action}' completed successfully.")
            logging.info("\033[96mAbout to emit action completed\033[0m")
            self.action_completed.emit(self.action,self.success_msg)
            logging.info("Signal emitted from action worker")
        except Exception as e:
            logging.info("\033[96mAbout to emit error occured\033[0m")
            logging.error(str(e))
            self.error_occurred.emit(f"Exception: {str(e)}", self.action)
        finally: 
            self.cleanup()

    def cleanup(self):
        # Disconnect all signals here
        self.action_completed.disconnect(self._parent.handle_action_completed)
        self.error_occurred.disconnect(self._parent.handle_error)
        logging.info("SIGNALS DISCONNECTED: ACTION")

class ChatGPT(QObject, SeleniumService):
    TXTFLD_PROMPT = "//textarea[@id='prompt-textarea']"
    BTN_SEND = "//button[@data-testid='fruitjuice-send-button']"
    TXT_RESPONSE_ITEMS = "((//div[contains(@class, 'agent-turn')])[last()]//button[contains(@class, 'text-token-text-secondary')])[last()]"
    TXT_RESPONSE_BLOCK = "(//div[@data-message-author-role='assistant' and contains(@class, 'text-message')])[last()]"
    BTN_PREFERENCES = "//button[contains(@class,'flex w-full')]"
    BTN_VERSION_SELECTOR = "//div[@aria-haspopup='menu']"
    BTN_NEW_CHAT = "//nav[@aria-label='Chat history']//button[contains(@class, 'h-10')]"
    BTN_NEW_CHAT_COLLAPSED = "//button[contains(@class, 'h-10') and contains(@class, 'rounded-lg')]"

    def __init__(self, signal_manager : 'SignalManager', **kwargs):
        super().__init__(**kwargs)
        # set when opening a new session with a desired name
        # we have to wait until after the first query to
        # be able to name the session

        # default session name gets overridden if specified in ctor or new_chat
        # but we need one in case we need to reload the chat on error
        self.session_name = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
        self.session_needs_renaming = False
        self.is_ready = True
        self.is_first_message = True
        self.worker = None
        if signal_manager: 
            self.signals = signal_manager.api_signals

    def get_service_name():
        return "OpenAI's ChatGPT"

    def open_login(self):
        # deal with "who's using chrome?"
        try: 

            time.sleep(2)
            self._load_page('https://chatgpt.com/?oai-dm=1&temporary-chat=true')
        except: 
            logging.error("Error opening ChatGPT")

    def open(self):
        self._load_page('https://chatgpt.com/?oai-dm=1&temporary-chat=true')
        self._wait_until_xpath(Element.BTN_SEND.value) # PREFS is last thing to load

    def get_models(self) -> list[str]:
        return ['GPT-3.5', 'GPT-4o','GPT-4']
    
    def is_ready_for_next_message(self):
        return self.is_ready
    
    def query(self, text: str) -> str:
        try:
            self.is_ready = False
            self.enter_text(text)
        except Exception as e:
            logging.error(f"Error occurred in query: {e}")

    def enter_text(self, text):
        try:
            if self.worker is not None:
                logging.info("Waiting for worker to be freed")
                self.worker.wait()
                logging.info(f"num of workers: {1 if self.worker else 0}")
            self.worker = ElementLocatorWorker(self, self.driver, Element.TXTFLD_PROMPT, text)
            self.worker.element_found.connect(self.handle_element_found)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.start()
            logging.info("Waiting for input field to be located...")
        except Exception as e:
            logging.error(f"Error occurred in enter_text: {e}")
    
    def found_element_input_field(self, element, locator, text):
        logging.info("\033[95mChatGPT found element input field\033[0")
        try:
            if self.worker is not None:
                logging.info("Waiting for worker to be freed in input field located")
                self.worker.wait()
                logging.info(f"num of workers: {1 if self.worker else 0}")
            logging.info("Input field located.")
            cleansed_text = self.cleanse_input(text)
            self.worker = ActionExecutorWorker(self, self.driver, element, Action.ENTER_TEXT_BLOCK, cleansed_text)
            self.worker.action_completed.connect(self.handle_action_completed)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.start()
        except Exception as e:
            logging.error(f"Error occurred in handle_input_field_located: {e}")

    @pyqtSlot(object, str)
    def handle_action_completed(self, action, value):
        logging.info("\033[90mChatGPT handle action completed\033[0m")
        logging.info(f"Action '{action.value}' completed.")
        if (action == Action.ENTER_TEXT_BLOCK) or (action == Action.ENTER_TEXT):
            self.handle_text_entered(value)
        elif action == Action.RETRIEVE_TEXT:
            self.handle_text_retrieved(value)

    @pyqtSlot(object, str, str)
    def handle_element_found(self, element, locator, extra):
        logging.info("\033[90mChatGPT handle element found\033[0m")
        logging.info(f"Element '{locator}' completed.")
        if locator == Element.TXTFLD_PROMPT.value:
            self.found_element_input_field(element, locator, extra)
        elif locator == Element.TXT_RESPONSE_ITEMS.value:
            self.found_element_response_items(element, locator, extra)
        elif locator == Element.TXT_RESPONSE_BLOCK.value:
            self.found_element_response(element, locator, extra)
        
    def handle_text_entered(self, message):   
        logging.info("\033[95mChatGPT handle text entered\033[0m")
        logging.info(message)     
        self.retrieve_response()

    def cleanse_input(self, text: str) -> str:
        """Sanitize text to be entered into the input field to prevent issues with special characters."""
        replacements = {"\n": "\\r\\n", "\"": "\\\"", "\'": "\\\'"}
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def retrieve_response(self):
        if self.worker is not None:
            logging.info("Waiting for worker to be freed to retrieve response")
            self.worker.wait()
            logging.info(f"num of workers: {1 if self.worker else 0}")
        logging.info("Attempting to check for response...")
        # first wait for one second
        time.sleep(3)
        self.worker = ElementLocatorWorker(self, self.driver, Element.TXT_RESPONSE_ITEMS)
        self.worker.element_found.connect(self.handle_element_found)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def found_element_response_items(self, element, locator, extra):
        logging.info("\033[95mChatGPT found element response items\033[0m")
        if self.worker is not None:
            logging.info("Waiting for worker to be freed after done writing")
            self.worker.wait()
        self.worker = ElementLocatorWorker(self, self.driver, Element.TXT_RESPONSE_BLOCK)
        self.worker.element_found.connect(self.handle_element_found)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def found_element_response(self, element, locator, extra):
        logging.info("\033[95mChatGPT found element response\033[0m")
        if self.worker is not None:
            logging.info("Waiting for worker to be freed after response located")
            self.worker.wait()
            logging.info(f"num of workers: {1 if self.worker else 0}")
        self.worker = ActionExecutorWorker(self, self.driver, element, Action.RETRIEVE_TEXT)
        self.worker.action_completed.connect(self.handle_action_completed)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_text_retrieved(self, message):
        logging.info("\033[95mChatGPT handle text retrieved\033[0m")
        if self.worker is not None:
            logging.info("Waiting for worker to be freed after text retrieved")
            self.worker.wait()
            logging.info(f"num of workers: {1 if self.worker else 0}")
            logging.info("Worker freed after text retrieved")
        #logging.info(message)
        self.is_ready = True
        self.is_first_message = False
        self.worker = None
        logging.info("\033[96mAbout to emit response collected\033[0m")
        self.signals.chatbot_response_collected.emit(message)
        logging.info("\033[96mAbout to emit is ready to go\033[0m")
        self.signals.is_ready_to_go.emit(True)

    def refresh_and_retry(self):
        """Refresh the page and retry the operation."""
        try:
            logging.warning('Encountered an error, refreshing and retrying...')
            self.driver.refresh()
            self.open()  # Reopen the ChatGPT page to reset the state
        except WebDriverException as e:
            logging.critical(f"Failed to refresh and retry: {e}")
            self.save_error_and_exit()

    def save_error_and_exit(self):
        """Save the current page HTML when an unrecoverable error occurs and exit."""
        try:
            page_html = self.driver.page_source
            with open("error.html", "w", encoding="utf-8") as file:
                file.write(page_html)
            logging.critical('Fatal error encountered. Exiting. Please check error.html for more info.')
        except Exception as e:
            logging.critical(f"Failed to save error page: {e}")
        sys.exit(1)

    def open_chat(self, session_name: str):
        """Open a chat by finding a session with the given name and clicking on it."""
        try:
            logging.info(f"Attempting to open chat for session: {session_name}")
            # Wait for the preferences button to ensure the page is loaded
            if not self.wait_for_element(Element.BTN_PREFERENCES.value, timeout=10):
                logging.error("Preferences button not found.")
                raise NoSuchElementException("Preferences button not found.")
            logging.info("Preferences button found, continuing.")
            # Find the session button by its text
            session_xpath = f'//nav//ol//li[div//div[contains(text(), "{session_name}")]]'
            btn = self.wait_for_condition(EC.element_to_be_clickable, session_xpath, timeout=10, description="session button")
            
            if btn:
                btn.click()
                logging.info(f"Successfully opened chat for session: {session_name}")
            else:
                logging.error(f"Session button not found for: {session_name}")
                raise NoSuchElementException(f"Session button not found for: {session_name}")
        except NoSuchElementException as e:
            self.log_error(e, "Session not found or not clickable")
            raise
        except Exception as e:
            self.log_error(e, "Failed to open chat session")
            raise

    def new_chat(self, session_name: str, model: str = 'GPT-4o'):
        """Start a new chat session with the specified model."""
        try:
            #self.click_new_chat_button()
            #self.select_model(model)
            #self.set_session_name(session_name)
            logging.info(f"New chat initiated for model: {model}")
        except Exception as e:
            self.log_error(e, "Failed to start a new chat session")
            raise
    
    def click_new_chat_button(self):
        """Click the New Chat button."""
        try:
            btn_new_chat = self.wait_for_clickable(Element.BTN_NEW_CHAT.value, timeout=2)
            if btn_new_chat:
                    btn_new_chat.click()
            else:
                self.find_and_click(Element.BTN_NEW_CHAT_COLLAPSED.value)
                logging.info("Clicked on collapsed version of new chat button.")
        except Exception as e:
            self.log_error(e, "An unexpected error occurred while starting a new chat")
            raise

    def select_model(self, model: str):
        # Click the version selector to open the menu
        version_selector = self.find_and_click(Element.BTN_VERSION_SELECTOR.value)

        # Click the specific model
        model_xpath = f"//div[@role='menuitem' and contains(text(), '{model}')]"
        model_button = self.find_and_click(model_xpath)
        if not model_button:
            logging.info(f"Model '{model}' not found or could not be clicked. User is likely free user.")
            
        # Click the version selector again to check the temporary chat toggle
        if version_selector.get_attribute("aria-expanded") == True: 
            version_selector.click()

    def recover_from_error(self):
        """Handle recovery from errors by refreshing the chat interface."""
        self.worker.refresh_chat()

    def handle_error(self, error_type, message):
        """Handle different types of errors with appropriate UI feedback or recovery actions."""
        if error_type == "WebDriverException":
            logging.error(f"Critical error encountered: {message}. Attempting recovery.")
            self.recover_from_error()
        else:
            logging.error(f"{error_type} - {message}")

    def wait_for_element(self, locator, timeout=1) -> Optional[WebElement]:
        """Wait for an element to be present and visible on the page."""
        element = self.wait_for_condition(EC.presence_of_element_located, locator, timeout, "visible element")
        if element is None: 
            try: 
                element = self.driver.find_element(By.XPATH, locator)
            except NoSuchElementException:
                logging.error(f"Element not found with locator: {locator}")
        return element

    def wait_for_clickable(self, locator, timeout=1) -> Optional[WebElement]:
        """Wait for an element to be clickable and return it."""
        logging.info(f"Waiting for clickable element: {locator}")
        return self.wait_for_condition(EC.element_to_be_clickable, locator, timeout, "clickable element")
    
    def wait_for_condition(self, condition, locator, timeout=1, description="element") -> Optional[WebElement]:
        """Wait for a specified condition and handle timeouts."""
        try:
            element = WebDriverWait(self.driver, timeout, poll_frequency=0.05).until(
                condition((By.XPATH, locator))
            )
            logging.info(f"{description} found!!! returning...")
            return element
        except TimeoutException:
            logging.error(f"Timeout waiting for {description} with locator: {locator}")
            return None

    def find_and_click(self, locator) -> Optional[WebElement]:
        """Safely find and click an element, using JavaScript click as a fallback."""
        try:
            element = self.wait_for_clickable(locator, timeout=2)
            if element:
                element.click()
                logging.info(f"Clicked element with locator: {locator}")
                return element
        except (TimeoutException, ElementClickInterceptedException) as e:
            logging.error(f"Standard click failed for {locator}, attempting JavaScript click. Error: {e}")
            return self.js_click_fallback(locator)
        except Exception as e:
            logging.error(f"Unexpected error when attempting to click on {locator}. Error: {e}")
            return None

    def js_click_fallback(self, locator):
        """Attempt to click using JavaScript if standard methods fail."""
        try:
            element = self.driver.find_element(By.XPATH, locator)
            self.driver.execute_script("arguments[0].click();", element)
            logging.info(f"JavaScript click performed on {locator}")
            return element
        except NoSuchElementException as e:
            logging.error(f"No such element: {locator}. Error: {e}")
            return None
        except Exception as e:
            logging.error(f"JavaScript click failed for {locator}. Error: {e}")
            return None

    def log_error(self, e, message):
        """Log an exception with a custom message."""
        msg = f"{message}: {e}"
        logging.error(msg)

    def _rename_session(self):
        """Safely attempt to rename a session to avoid conflicts and ensure uniqueness."""
        try:
            # Wait and click the edit button to start renaming
            self.find_and_click("//nav ol li div button", "Edit session button")
            # Click the 'Rename' option in the dropdown
            self.find_and_click("div[role='menuitem']:nth-child(2)", "Rename menu item")
            # Clear the existing name and enter a new one
            name_field = self._find_element_css("nav ol li div div input")
            name_field.clear()
            name_field.send_keys(self.session_name + Keys.ENTER)
            self.session_needs_renaming = False
            logging.info(f"Session successfully renamed to {self.session_name}.")
        except Exception as e:
            logging.error(f"Failed to rename session: {e}")
            raise

    def close(self):
        # cleanup
        SeleniumService.close(self)