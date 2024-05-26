
# BASIC SERVICE
##############################################
# This section contains the code related to the basic service functionality.
# It includes the implementation of the BasicService class, which is a subclass of object.
# The BasicService class provides an interface for backends.
# The code in this section is responsible for defining the interface for backends.
##############################################
# src/backends/basic_service.py
##############################################

# specifies interface for backends
# * open (e.g. chat.openai.com)
# * get_models (e.g. ['gpt-3.5','gpt-4'])
# * new_chat (begins a new named chat)
# * query (submits a query, gets a response)
# * open_chat (opens a previously named chat)

class BasicService(object):


    def __init__(s, **kwargs):
        # settable options
        s.__dict__.update(kwargs)
        s.session_name = ""

    
    def get_service_name() -> str:
        """get human readable name of this service"""
        raise NotImplementedError()


    def get_models(s) -> list[str]:
        """get list of available models for the current backend"""
        raise NotImplementedError()


    def new_chat(s, name: str, model: str):
        """name is required for automation (recovery)"""
        raise NotImplementedError()


    def query(s, text: str) -> str:
        """queries the LLM, returns the result"""
        raise NotImplementedError()



# GEMINI BASE SECTION
##############################################
# This section contains the code related to the gemini base functionality.
# It includes the implementation of the Bard class, which is a subclass of SeleniumService.
# The Bard class provides methods for interacting with the chatbot service.
# The code in this section is responsible for opening and closing the chat service,
# retrieving available models, querying the chatbot, and managing chat sessions.
##############################################
# src/backends/gemini_base.py
##############################################


from src.backends.backend_setup.discover import get_chrome_version
from src.backends.backend_setup.google import Bard

bard = None
# add all the above code into a function callable from main.py in src
def open_chatbot():
    global bard
    
    # automatic
    CHROME_PATH = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
    CHROME_VER = get_chrome_version(path=CHROME_PATH)
    
    # init service & web driver
    bard = Bard(path=CHROME_PATH, driver_version=CHROME_VER)
    
    # open this service's page, if it has one
    bard.open()
    
    # create a new named session, can pass model='GPT-4'
    # messy, but it waits 4 seconds then renames the session
    # (hopefully) after openai names the session. This could be improved.
    bard.new_chat('imbard')
    
    prompt = 'Pretend to be a lonely robot with feeling, being greeted by another robot.\n'
    text = 'How are you today?'
    chat_response = bard.query(prompt+text)
    
    print("INIT:")
    print(text+'\n\n')
    #print("BARD:")
    #print(chat_response+'\n\n')
    
    return chat_response

def close_chatbot():
    # close up shop
    print('closing!')
    bard.close()
    
    # not technically necessary
    # closes driver/browser
    print('all done')

def user_input_to_chatbot(user_input):
    print("USER:", user_input+'\n')
    chat_response = bard.query(user_input)
    print("BARD:")
    print(chat_response+'\n\n') 
    return chat_response

#run_chatbot()

##############################################
# SELENIUM SERVICE
##############################################
# This section contains the code for the SeleniumService class.
# It adds the required interface for opening the chat service.
# The code in this section is responsible for opening the chat service,
# such as chat.openai.com.
##############################################

# src/backends/selenium_service.py
# adds required interface
# * open (e.g. opens chat.openai.com)
##############################################

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import undetected_chromedriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .basic_service import BasicService
import sys
import time
import os

CURRENT_PATH = os.getcwd()

# stupidly necessary because...
# web frameworks that replace subtrees
# (like React) often change things millisecond by millisecond
# and then the IDs change as a result, invalidating 
# any querying of the page for elements that we've done.
# So.. we try, try, try until successful... like Wifi or Ethernet!
def MustSucceed():
    error = True
    while error:
        try:
            yield None
            error = False
        except:
            error = True
        finally:
            pass


# get an instance through <chatService>.get_tab_manager()
# e.g.:
# chatgpt = ChatGPT()
# tabs = chatgpt.get_tab_manager()
# firstTab = tabs.get()
# newtab = tabs.new() # & switches to new tab
# tabs.goto(firstTab)
# tabs.goto(newtab)
# tabs.close(firstTab)
# tabs.close() # closes current tab
class Tabs:


    def __init__(s, driver):
        s.driver = driver


    def get(s):
        """current tabs"""
        return s.driver.current_window_handle


    def new(s):
        s.driver.switch_to.new_window('tab')
        return s.get()


    def goto(s, tab):
        s.driver.switch_to.window(tab)


    def close(s, tab):
        """closes a specified tab"""
        here = s.get()
        if tab == here:
            print("Error: not allowed to close the active tab")
            # this is because if you close the active tab, then
            # the "this tab" reference in Selenium seems to be lost
            # so to simplify the process and avoid telling the user
            # to always switch to a tab after closing, then we just
            # make sure they always close from another tab.
            return
        s.goto(tab)
        s.driver.close()
        s.goto(here)
      

class SeleniumService(BasicService):


    def __init__(s, **kwargs):
        """options:
        driver: an existing driver to use if you have multiple sessions going
        chrome_profile: default 'selenium_profile' in local
        driver_version: e.g. "113.0.5672.63" must be same as webdriver
        headless: bool, untested
        session_name: string, name for the chat session"""
        # settable options
        s.driver = None
        s.chrome_profile = 'selenium_profile' # a local ./dir 
        s.driver_version = '' # must be same as web driver you installed
        s.headless = False # use selenium headless (untested)
        s.__dict__.update(kwargs)
        s.session_name = ''
        if hasattr(s.driver, 'path'):
            s.path = s.driver.path
        if not s.driver and not s.driver_version:
            print('Error: need driver_version as string if first service')
            sys.exit(1)
        if not s.driver:
            s._init_driver()
            # shared ptr counter, when 0 on quit then delete
            s.driver.other_references = 0
        else:
            s.driver.other_references += 1
        if not s.path:
            print("Error: need valid path to the Chrome browser executable")
            sys.exit(1)
        BasicService.__init__(s, **kwargs)

    def _init_driver(s):
        profile_path = os.path.join(CURRENT_PATH, s.chrome_profile)
        if not os.path.isdir(profile_path):
            os.makedirs(profile_path)
        s.wdm=ChromeDriverManager(driver_version=s.driver_version).install()
        s.service=Service(s.wdm)
        options = undetected_chromedriver.ChromeOptions()
        options.headless = s.headless
        s.driver = undetected_chromedriver.Chrome(service=s, options=options, user_data_dir=profile_path, executable_path=s.path)
        pass


    def _load_page(s, url: str):
        """driver.get(url) then driver.implicitly_wait()"""
        s.driver.get(url)
        s.driver.implicitly_wait(10)
        time.sleep(3.0)


    # 2 flavors of finding & waiting css or xpath, pros & cons
    def _find_element_css(s, css: str):
        element = s.driver.find_element(By.CSS_SELECTOR,css)
        time.sleep(0.1)
        return element


    def _find_element_xpath(s, xpath: str):
        element = s.driver.find_element(By.XPATH,xpath)
        time.sleep(0.1)
        return element


    def _wait_until_css(s, css: str, wait_sec = 5, error_msg: str = "Error: could not find element by css.", safe: bool = True):
        wait = WebDriverWait(s.driver, wait_sec)
        if not safe:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        else:
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
                time.sleep(0.1)
            except:
                print(error_msg + f" css: '{css}'")
                sys.exit()


    def _wait_until_xpath(s, xpath: str, wait_sec = 5, error_msg: str = "Error: could not find element by xpath.", safe: bool = True):
        wait = WebDriverWait(s.driver, wait_sec)
        if not safe:
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        else:
            try:
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                time.sleep(0.1)
            except:
                print(error_msg + f" xpath: '{xpath}'")
                sys.exit()


    def get_driver(s):
        """get the existing driver shared by this agent"""
        s.driver.path = s.path
        return s.driver


    def open(s):
        """open interface page possibly for manual interaction, like logging in first time"""
        raise NotImplementedError()


    def close(s):
        """clean up resources"""
        if s.driver.other_references == 0:
            s.driver.close()
            s.driver.quit()
        else:
            s.driver.other_references -= 1


    ##
    ## tab & window management for multiple agents
    ##

    def get_tab_manager(s) -> Tabs:
        return Tabs(driver=s.driver)

##############################################
# DISCOVER
##############################################
# This section contains the code related to the discovery functionality.
# It includes the implementation of the discover function, which is responsible for finding the Chrome executable path and version.
# The code in this section is responsible for discovering the Chrome executable path and version.
##############################################
# src/backends/backend_setup/discover.py

import sys
import os
import subprocess

def _get_path(executable_name) -> str:
    """finds full path of an executable on the system PATH"""
    if sys.platform == 'win32' and not executable_name.lower().endswith('.exe'):
        executable_name += '.exe'
    path_dirs = os.environ['PATH'].split(os.pathsep)
    for path_dir in path_dirs:
        executable_path = os.path.join(path_dir, executable_name)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return ""


def get_chrome_path() -> str:
    chrome = ''
    if not chrome:
        chrome = _get_path('chrome')
    if not chrome:
        chrome = _get_path('google-chrome')
    if not chrome:
        print("Error: No Chrome executable path set and no Chrome executable found on system PATH")
        sys.exit(1)
    return chrome


def get_chrome_version(path = None) -> str:
    if path is None: path = get_chrome_path()
    try:
        result = subprocess.run(path + ' --version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if line.startswith('Google Chrome'):
                    version = line.split()[2]
                    return version
        else:
            error_message = result.stderr.strip()
            print(f"Error: {error_message}")
    except FileNotFoundError:
        print("Google Chrome not found on the PATH.")
    return None  # Chrome version not found

##############################################
# GOOGLE
##############################################
# This section contains the code related to the Google chatbot service.
# It includes the implementation of the Bard class, which is a subclass of Selenium
# Service and provides methods for interacting with the Google chatbot service.
##############################################
# src/backends/backend_setup/google.py
from src.backends.selenium_service import SeleniumService
from src.backends.selenium_service import MustSucceed
from selenium.common import exceptions as s_exceptions
from selenium.webdriver.common.action_chains import ActionChains

from collections import defaultdict
import sys # exit
import time
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


    def query(s, text: str) -> str:
        s._wait_until_css('rich-textarea')
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
        s.driver.execute_script(f'document.getElementsByTagName("rich-textarea")[0].getElementsByTagName("p")[0].innerText="{text} ";')
        # submit message
        send_button = s._find_element_css('div.send-button-container')
        try:
            send_button.click()
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

##############################################
# SETUP LOGINS
##############################################
# This section contains the code related to the setup logins functionality.
# It includes the implementation of the run function, which is responsible for setting up the logins for the chatbot services.
# The code in this section is responsible for setting up the logins for the chatbot services.
##############################################
# src/backends/backend_setup/setup_logins.py
from src.backends.backend_setup.discover import get_chrome_version

#from backends.basic_service import BasicService
from src.backends.gemini_base import Bard

# automatic
# CHROME_PATH = get_chrome_path()
# CHROME_VER = get_chrome_version(path=CHROME_PATH)
    
# manual 
CHROME_PATH = "/Applications/Google\ Chrome\ 2.app/Contents/MacOS/Google\ Chrome"
CHROME_VER = get_chrome_version(path=CHROME_PATH)

html_services = [Bard]
reusable_driver = None
open_services = list()

def get_response(question: str) -> str:
    while True:
        response = input(f"{question} (Y/n/x): ").strip().lower()  # Get user input and convert to lowercase
        if len(response) == 0:
            response = 'y'
        if response in ('y', 'n', 'x'):
            break 
        print("Invalid input. Please enter 'Y' or 'N' or 'x' for exit.")
    return response
  

from typing import Callable
def init_service(Service: Callable):
    global reusable_driver, open_services
    if reusable_driver is None:
        service = Service(path=CHROME_PATH, driver_version=CHROME_VER)
        reusable_driver = service.get_driver()
        open_services.append(service)
    else:
        service = Service(path=CHROME_PATH, driver=reusable_driver)
    service.open_login()


def close_services():
    for service in open_services:
        service.close()

def run():

    print(f"using chrome    path: {CHROME_PATH}")
    print(f"using chrome version: {CHROME_VER}")

    for service in html_services:
        response = get_response(f"Will you be using {service.get_service_name()}?")
        if response == 'y':
            init_service(service)
            input('Please now log in to the web site (Press Enter here when done)')
        elif response == 'x':
            break

    #close_services()

    print('Great! All logged in. Scripting should now work okay for this default profile dir "selenium_profile" that now exists')
    print("You'll need to do this again if you clear the profile or create a new one")

