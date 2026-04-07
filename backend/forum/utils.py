
from sqlalchemy.orm import Session

from ..schemas import MessageOut
from ..models import Message, Tag

def serialize_message(message: Message):
    return MessageOut(
        id=message.id,
        parent_id=message.parent_id,
        text=message.text,
        author=message.author,
        timestamp=message.timestamp,
        tags=[tag.name for tag in message.tags]
    )

def create_tag_list(session: Session, tag_names: list[str]):
    tags = []
    for tag_name in set(tag_names):
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            session.flush() 
        tags.append(tag)
    return tags

def cleanup_orphaned_tags(session, tags: list[Tag]):
    for tag in tags:
        if not tag.messages:
            session.delete(tag)