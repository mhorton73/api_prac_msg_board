
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
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
    author = Column(String)
    text = Column(String)
    timestamp = Column(DateTime, index=True)
    tags = relationship("Tag", secondary=message_tags, back_populates="messages")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    messages = relationship("Message", secondary=message_tags, back_populates="tags")