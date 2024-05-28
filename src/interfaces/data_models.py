"""
data_models.py

This module defines the data models used in the application. These models are used to structure the data that is 
sent and received over the network, as well as the data that is stored locally.

The module uses the Pydantic library to define the data models. Pydantic models are essentially Python classes 
that have type annotations on their attributes. Pydantic validates the data against these type annotations when 
a model is instantiated, ensuring that the data is of the correct type.

Classes:
    - UserData: Represents user data, including the genome ID of the mediator, the time since the mediator 
    started up, the user's rating of the mediator, the last message sent by the user, the time when the last message 
    by the user was sent, the last response received by the user, and the time when the last response was received.
    - MediatorData: Represents the data model for receiving a new mediator over the network, including the 
    new mediator (serialized) and the message associated with the mediator.
    - ReplyData: Represents the data model for a reply from the chatbot, including the last response received, 
    the time when the last response was received, and a flag indicating whether the reply should be hidden 
    from the user or not.
    - MessageData: Represents the data model for a message sent by the user, including the content of the last
    message from the user and the timestamp of the last message from the user.
"""
from typing import Optional
from pydantic import BaseModel

class UserData(BaseModel):
    """
    Represents user data.

    Attributes:
        genome_id (int): The genome ID of the mediator.
        time_since_startup (float): The time since the mediator started up.
        user_rating (int): The user's rating of the mediator.
        last_message (Optional[str], optional): The last message sent by the user. Defaults to None.
        last_message_time (Optional[float], optional): The time when the last message by the user was sent. Defaults to None.
        last_response (Optional[str], optional): The last response received by the user. Defaults to None.
        last_response_time (Optional[float], optional): The time when the last response was received. Defaults to None.
    """
    genome_id: int
    time_since_startup: float
    user_rating: int
    last_message: Optional[str] = None
    last_message_time: Optional[float] = None
    last_response: Optional[str] = None
    last_response_time: Optional[float] = None

class MediatorData(BaseModel):
    """
    Represents the data model for receiving a new mediator over the network.

    Attributes:
        new_mediator (str): The new mediator, serialized.
        message (str): The message associated with the mediator.
    """
    new_mediator: str
    message: str

class ReplyData(BaseModel):
    """
    Represents the data model for a reply from the chatbot.

    Attributes:
        last_response (str): The last response received.
        last_response_time (float): The time when the last response was received.
        is_secret (bool): Indicates whether the reply should be hidden from the user or not.
    """
    last_response: str
    last_response_time: float
    is_secret: bool

class MessageData(BaseModel):
    """
    Represents the data model for a message sent by the user.

    Attributes:
        last_message (str): The content of the last message from the user.
        last_message_time (float): The timestamp of the last message from the user.
    """
    last_message: str
    last_message_time: float
