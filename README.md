# Client Server

### Dev Usage Notes
* Ensure executable permissions:
```bash
chmod +x setup_dev.sh
chmod +x setup_deploy.sh
```
*Run scripts from project root:
```bash
./setup_dev.sh  # For development setup
./setup_deploy.sh  # For deployment
```
These scripts are designed to be robust and provide clear logging throughout the setup process. Modify paths and names as needed to match your specific project structure and requirements.


# ring 
Control and Automate various public LLMs -- a circle of helpful friends.

```py
chat = Bard(...)
chat.open() # load Bard in the browser
response = chat.query("Hello. Are you ready to answer some questions? Be laconic in your response.")
print(response)
```

Supports the following model hosts
* **ChatGPT 3.5, 4** (via web scraping)
* **Google Bard** (via web scraping)
* **Anthropic Claude** (via free api key)
* **HuggingFace Chats/Assistants** (via web scraping)
* **Cohere** (via free api key)
* **Together.ai** (via web scraping)

### Getting Started

Overview

* Install Vanilla [Chrome browser](https://www.google.com/chrome/)
* Optional: Install (usually just download) the appropriate [web driver](https://chromedriver.chromium.org/getting-started) of the exact same version. This is helpful if you have a slow internet connection. Otherwise, the driver is automatically downloaded every time your script starts. On a fast connection, this is not noticeable.
* Get Python
* Make sure the chrome executable is on your PATH (can be called from the command line) or specify the path in the py file (see below)
* MacOS: In your python file, specify the full path to the Chrome excecutable. It may be: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome`

Note: Chrome location is auto detected if on the system path, but this is usually not the case. So most folks will need to manually edit CHROME_PATH in each script. Use the `# manual` path and version block of code, not the `# automatic` one in this case.

Technical Steps

0) pip install -r requirements.txt
1) Edit the CHROME_PATH in `setup_logins.py` and the demo scripts `example.py` and `asktogther.py`
2) Run `setup_logins.py` once to establish session cookies for sites you need to log into. For the `example.py`, log into both Google and OpenAI
3) Run `example.py` to see ChatGPT and Bard talk to each other
4) Run `asktogether.py` to have a question/answer session with Llama 2 (or any model you have picked in the GUI)

Automatic chrome path discovery and driver downloading
```py
from backends.together import Together
from util.discover import get_chrome_path, get_chrome_version
CHROME_PATH = get_chrome_path()
CHROME_VER = get_chrome_version()
chat = Together(path=CHROME_PATH, driver_version=CHROME_VER)
```

Manual path specification and driver reuse (to skip downloading every time you start your script)
```py
from backends.together import Together
from util.discover import get_chrome_path, get_chrome_version
CHROME_PATH = "/home/user/GoogleChrome/chrome"
CHROME_VER = get_chrome_version(path=CHROME_PATH)
chat = Together(path=CHROME_PATH, driver_version=CHROME_VER, driver_executable_path='<your full path here>/chromedriver-linux64/chromedriver')
```


### ChatGPT-specific features
Currently, only the ChatGPT module supports session renaming and switching:
```py
#...
chat = ChatGPT(path=CHROME_PATH, driver_version=CHROME_VER)
# you can already start querying, but instead you could
# start a new named session, with a specific model version.
chat.new_chat(session_name="my session 1", model="GPT-3.5")
# query as usual
chat.open_chat(session_name="my other session")
# query as usual
```

### Known Issues
Sometimes, especially with ChatGPT, some errors occur "something happened" or "network error" Those are usually easy to automatically recover from, but that code has not been updated, because those screens and situations are somewhat rare, and I need to see the HTML to code an appropriate trigger. Please, if they happen, try to immediately save the HTML (CTRL+S, or COMMAND+S) before the entire application closes due to timeout. Then email it to me.

With Together.ai, the login cookie seems not to be persistent. So you have to log in every time starting your script.

Sometimes the session becomes corrupted or too large or something (I'm not sure) and it makes startup hang indefinitely. Just delete the `selenium_profile` directory that was created, and run the `setup_logins` script again before continuing.

### Todo
- [x] Allow `setup_logins.py` to skip services you don't need
- [x] Auto query chrome for version information
- [ ] Auto download chrome driver for chrome's version for correct OS
- [ ] Cleanup - move more CSS/XPATH strings into class-level constants

### Updating the Scraping Code
OpenAI and Google sometimes update their HTML, which breaks the scraping code.
You will find both XPATH and CSS selectors in the openai and google backend files.
Here are helpful tools and workflows to speed along the process.

**Chrome Plugins:**
* XPath Helper
* CSS Selector Tester

**XPATH** Use XPath Helper to identify and test XPATH expressions.

**CSS** Use either the CSS Selector Tester or the Developer Inspector and the Developer Console to discover if the selectors are working correctly. For example, you can use this command in the console to extract text from ChatGPT's most recent response block:
```
$$("main .group:nth-last-of-type(2) .items-start")[0].innerText
```

### Authors

* 
