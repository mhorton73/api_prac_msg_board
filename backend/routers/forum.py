

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone 
from sqlalchemy import asc, desc

from ..database import SessionLocal
from ..models import Message, Tag
from ..schemas import MessageIn, MessageOut, MessageResponse, MessageListResponse
from backend.forum.utils import serialize_message, create_tag_list, cleanup_orphaned_tags
from backend.auth.dependencies import get_current_user


def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

router = APIRouter(prefix="/forum", tags = ["forum"])

# -------- Endpoints -------- 

@router.post("/messages", response_model=MessageResponse, status_code=201) 
async def add_message(message: MessageIn, session = Depends(get_session), user = Depends(get_current_user)): 
    """Post a message with text, author and optional tags. Records timestamp and generates a unique id."""

    if message.parent_id:
        parent = session.get(Message, message.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent message not found")

    tag_list = create_tag_list(session, message.tags)

    new_message = Message(
        parent_id = message.parent_id,
        text = message.text, 
        author = user.username,
        timestamp = datetime.now(timezone.utc), 
        tags = tag_list
        ) 

    session.add(new_message)
    session.commit()
    session.refresh(new_message)

    return MessageResponse(status = "added", data = serialize_message(new_message)) 



@router.get("/messages", response_model=MessageListResponse, status_code=200) 
async def get_messages( 
        author: str = None, 
        tag: str = None, 
        parent_id = None,
        page: int = 1, 
        limit: int = 10, 
        sort: str = "timestamp", 
        order: str = "desc",
        session = Depends(get_session)
    ):
    """Lists all stored messages. Default sorted by most recent post. Can be sorted by author or text."""

    allowed_sorts = ["timestamp", "author", "text"] 
    if sort not in allowed_sorts: 
        raise HTTPException(status_code=400, detail="Invalid sort field") 
    

    query = session.query(Message)

    # --- Filtering ---
    if author is not None:
        query = query.filter(Message.author.ilike(author))
    if tag is not None:
        query = query.join(Message.tags).filter(Tag.name.ilike(tag)).distinct()
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    
    # --- Sorting ---

    column = getattr(Message, sort)
    if order.lower() == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    total = query.count()
    messages = query.offset((page-1)*limit).limit(limit).all()
    
    message_out = [
        serialize_message(msg)
        for msg in messages
    ] 

    return MessageListResponse( 
        total = total, 
        page = page, 
        limit = limit, 
        messages = message_out 
    ) 



@router.get("/messages/{id}", response_model=MessageOut, status_code=200) 
async def get_message(id: int, session = Depends(get_session)): 
    """Retrieves the message with the specified id."""

    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return serialize_message(message)



@router.delete("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def delete_message(id: int, session = Depends(get_session), user = Depends(get_current_user)): 
    """Deletes the message with the specified id."""

    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.author != user.username:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    deleted_message = serialize_message(message)           # copy the message before deleting
    old_tags = list(message.tags)

    session.delete(message)
    session.flush()

    cleanup_orphaned_tags(old_tags)

    session.commit()

    return MessageResponse(status="deleted", data = deleted_message)
    


@router.put("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def edit_message(id: int, update: MessageIn, session = Depends(get_session), user = Depends(get_current_user)): 
    """Edits the message with the specified id."""


    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.author != user.username:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    message.text = update.text

    # --- Update tags ---
    new_tag_list = create_tag_list(session, update.tags)
    old_tags = list(message.tags)
    message.tags = new_tag_list 
    session.flush()

    cleanup_orphaned_tags(session, old_tags)

    session.commit()
    session.refresh(message)

    return MessageResponse(
        status="updated",
        data=serialize_message(message)
    )