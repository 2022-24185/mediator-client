# adds required interface
# * open (e.g. opens chat.openai.com)

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
