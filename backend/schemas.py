
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class MessageIn(BaseModel):
    text: str
    tags: List[str] = Field(default_factory=list)
    parent_id: int | None = None

class MessageOut(BaseModel):
    id: int
    parent_id: int | None
    text: str
    author: str
    timestamp: datetime
    tags: List[str] = Field(default_factory=list)

class MessageResponse(BaseModel):
    status: str
    data: MessageOut

class MessageListResponse(BaseModel):
    total: int
    page: int
    limit: int
    messages: List[MessageOut]

class UserIn(BaseModel):
    username: str
    password: str

class RegisterResponse(BaseModel):
    status: str
    username: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class CurrentUser(BaseModel):
    id: int
    username: str