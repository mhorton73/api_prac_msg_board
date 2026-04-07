
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

message_tags = Table(
    "message_tags",
    Base.metadata,
    Column("message_id", Integer, ForeignKey("messages.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    author = Column(String, index=True)
    text = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    tags = relationship("Tag", secondary=message_tags, back_populates="messages")
    

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    messages = relationship("Message", secondary=message_tags, back_populates="tags")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index = True)
    password_hash = Column(String)

    refresh_tokens = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime)
    
    user = relationship("User", back_populates="refresh_tokens")