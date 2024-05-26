
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
