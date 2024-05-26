from src.backends.selenium_service import SeleniumService
from src.backends.selenium_service import MustSucceed
from selenium.common import exceptions as s_exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from collections import defaultdict
import sys # exit
import time
import logging
import datetime


class Bard(SeleniumService):


    def __init__(s, **kwargs):
        # set when opening a new session with a desired name
        # we have to wait until after the first query to
        # be able to name the session

        # default session name gets overridden if specified in ctor or new_chat
        # but we need one in case we need to reload the chat on error
        s.session_name = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
        s.session_needs_renaming = False
        # forward args to basal classes
        SeleniumService.__init__(s, **kwargs)


    def get_service_name():
        return "Google's Bard"


    def open_login(s):
        s._load_page('https://bard.google.com')


    def open(s):
        s._load_page('https://bard.google.com')
        s._wait_until_css('rich-textarea')


    def close(s):
        # any cleanup here
        SeleniumService.close(s)


    def get_models(s) -> list[str]:
        return []
    
    def is_ready_for_next_message(s, is_first_message = False):
        if is_first_message: 
            logging.info("Bard is preparing for the first message.")
            try: 
                # Try to find the "send" icon
                s._find_element_css('rich-textarea')
                return True
                # If the "rich text area" is found, Bard is ready for the first message
            except s_exceptions.NoSuchElementException:
                # If the "rich text area" icon is not found, Bard is not ready for the next message
                return False
        else: 
            logging.info("Bard is preparing for the next message.")
            try:
                # Try to find the "thumb_up" icon
                s._find_element_css('.chat-history div.conversation-container:last-child model-response mat-icon[data-mat-icon-name="thumb_up"]')
                # If the "thumb_up" icon is found, Bard is ready for the next message
                return True
            
            except s_exceptions.NoSuchElementException:
                # If the "thumb_up" icon is not found, Bard is not ready for the next message
                return False
            
    def wait_and_click(self, selector, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
        except s_exceptions.TimeoutException:
            logging.error(f"Timeout waiting for element {selector}")
        except s_exceptions.ElementClickInterceptedException as e:
            logging.error(f"Element not clickable {selector}: {str(e)}")


    def query(s, text: str) -> str:
        logging.info(f"Querying Bard chatbot: {text}. Waiting for text area")
        s._wait_until_css('rich-textarea')
        logging.info("Found text area.")
        # cleanse the command
        text = text.replace("\n", "\\r\\n")
        text = text.replace("\"", "\\\"")
        text = text.replace("\'", "\\\'")

        # SPECIAL NOTE
        # set-text through js (fast, but does not count as 'input')
        # send-keys (slow, but enables the 'send' return key)
        # so we set-text with one extra character
        # then remove it with '\b' in send-keys

        # type in the text
        logging.info(f"Typing in text: {text}")
        s.driver.execute_script(f'document.getElementsByTagName("rich-textarea")[0].getElementsByTagName("p")[0].innerText="{text} ";')
        logging.info("Text typed.")
        # submit message
        send_button = s._find_element_css('div.send-button-container')
        logging.info("Found send button.")
        try:
            send_button.click()
            logging.info("Send button clicked.")
        except(s_exceptions.ElementClickInterceptedException):
            ActionChains(s.driver)\
                .move_to_element_with_offset(send_button, 0, 20)\
                .perform()
            print("ElementClickInterceptedException")
            send_button.click()
            
        
        #user_input.send_keys('\b\n')
        # wait for response to end
        s._wait_until_css('.chat-history div.conversation-container:last-child model-response mat-icon[data-mat-icon-name="thumb_up"]', wait_sec=20)

        block = s._find_element_css('.chat-history div.conversation-container:last-child message-content.model-response-text')


        # Bard has no way to save sessions like openai,
        # so we save it ourselves for record keeping
        filename = s.session_name + ".google.txt"
        with open(filename, 'a') as file:
            file.write('\n')
            file.write(block.text)

        return block.text


    def open_chat(s, session_name: str):
        print("not a Bard feature")


    def new_chat(s,session_name: str,  model: str = 'GPT-3.5'):
        BTN_NEW_CHAT = "//nav/a[contains(@class, 'flex')][1][contains(text(), 'New chat')]"
        BTN_RESET_CHAT = '//*[@id="app-root"]/main/side-navigation-v2/bard-sidenav-container/bard-sidenav/div/div/div[1]/div/expandable-button'
        s._wait_until_xpath(BTN_RESET_CHAT)
        for _ in MustSucceed():
            btn = s._find_element_xpath(BTN_RESET_CHAT)
            if btn.is_enabled():
                btn.click()
        # DLG_RESET = 'mat-dialog-container message-dialog mat-dialog-actions button:nth-child(2)'
        # DLG_RESET ='div.bottom-container.ng-tns-c220192929-1.ng-star-inserted > div.input-area-container.ng-tns-c220192929-1.ng-star-inserted > input-area-v2 > div > div'
        DIALOG_RESET = '//*[@id="app-root"]/main/side-navigation-v2/bard-sidenav-container/bard-sidenav/div/div/div[1]/div/expandable-button'
        s._wait_until_xpath(DIALOG_RESET)
        for _ in MustSucceed():
            btn = s._find_element_xpath(DIALOG_RESET)
            btn.click()
        s.session_name = session_name
