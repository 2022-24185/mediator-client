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