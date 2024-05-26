from src.backends.backend_setup.discover import get_chrome_version

#from backends.basic_service import BasicService
from src.backends.gemini_base import Bard
from src.backends.backend_setup.openai import ChatGPT

# automatic
# CHROME_PATH = get_chrome_path()
# CHROME_VER = get_chrome_version(path=CHROME_PATH)
    
# automatic
CHROME_PATH = "/Applications/Google\ Chrome\ 3.app/Contents/MacOS/Google\ Chrome"
CHROME_VER = get_chrome_version(path=CHROME_PATH)

html_services = [Bard, ChatGPT]
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
        service = Service(path=CHROME_PATH, driver_version=CHROME_VER, signal_holder=None)
        reusable_driver = service.get_driver()
        open_services.append(service)
    else:
        service = Service(path=CHROME_PATH, driver=reusable_driver)
    service.open_login()


def close_services():
    for service in open_services:
        service.close()

#def run():

print(f"using chrome    path: {CHROME_PATH}")
print(f"using chrome version: {CHROME_VER}")

for service in html_services:
    response = get_response(f"Will you be using {service.get_service_name()}?")
    if response == 'y':
        init_service(service)
        input('Please now log in to the web site (Press Enter here when done)')
    elif response == 'x':
        break

close_services()

print('Great! All logged in. Scripting should now work okay for this default profile dir "selenium_profile" that now exists')
print("You'll need to do this again if you clear the profile or create a new one")

