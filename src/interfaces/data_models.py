# server/models.py
from pydantic import BaseModel
from typing import Optional

class UserData(BaseModel):
    genome_id: int
    time_since_startup: float
    user_rating: int
    last_message: Optional[str] = None
    last_message_time: Optional[float] = None
    last_response: Optional[str] = None
    last_response_time: Optional[float] = None

class ResponseModel(BaseModel):
    new_mediator: str
    message: str

class ReplyData(BaseModel):
    last_response: str
    last_response_time: float
    is_secret: bool

class MessageData(BaseModel): 
    last_message: str
    last_message_time: float
