# server/models.py
from pydantic import BaseModel
from typing import Optional

class UserData(BaseModel):
    genome_id: int
    time_since_startup: float
    user_rating: int
    last_message: Optional[str] = None
    last_message_time: Optional[float] = None

class ResponseModel(BaseModel):
    new_mediator: str
    message: str