
# start server with python -m uvicorn backend.main:app --reload (--port 800x if need be)
# netstat -ano | findstr :8000 to check the server status
# taskkill /PID <pid> /F to free up the port

# Goals
# Add authentication + authorization
# Multi-tag filtering
# Input validation + constraints
# Split into multiple files

# Other things to look into at some point:
# Replace Dict with dict, List with list, then remove import from typing
# Cache-ability
# use a lock to fix global state 
# health check endpooint, partial update endpoint (patch), metadata, logging
# learn Depends from fastapi


from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone 
from sqlalchemy import asc, desc

from .database import SessionLocal, engine, Base
from .models import Message, Tag
from .schemas import MessageIn, MessageOut, MessageResponse, MessageListResponse



def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# -------- App -------- 

app = FastAPI() 
Base.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------- Endpoints -------- 

@app.post("/messages", response_model=MessageResponse, status_code=201) 
async def add_message(message: MessageIn, session = Depends(get_session)): 
    """Post a message with text, author and optional tags. Records timestamp and generates a unique id."""

    try:
        tag_objects = []
        for tag_name in set(message.tags):
            tag = session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            tag_objects.append(tag)

        new_message = Message(
            text = message.text, 
            author = message.author, 
            timestamp = datetime.now(timezone.utc), 
            tags = tag_objects
            ) 
    
        session.add(new_message)
        session.commit()
        session.refresh(new_message)

        response_data = MessageOut(
            id=new_message.id,
            text=new_message.text,
            author=new_message.author,
            timestamp=new_message.timestamp,
            tags=[tag.name for tag in new_message.tags]
        )
    except Exception:
        session.rollback()
        raise

    return MessageResponse(status = "added", data = response_data) 


@app.get("/messages", response_model=MessageListResponse) 
async def get_messages( 
        author: str = None, 
        tag: str = None, 
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
    if author:
        query = query.filter(Message.author.ilike(author))
    if tag:
        query = query.join(Message.tags).filter(Tag.name.ilike(tag))
    
    # --- Sorting ---

    column = getattr(Message, sort)
    if order.lower() == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    total = query.count()
    messages = query.offset((page-1)*limit).limit(limit).all()
    
    message_out = [
        MessageOut(
            id = msg.id,
            text=msg.text,
            author=msg.author,
            timestamp=msg.timestamp,
            tags=[tag.name for tag in msg.tags] 
        )
        for msg in messages
    ] 

    return MessageListResponse( 
        total = total, 
        page = page, 
        limit = limit, 
        messages = message_out 
    ) 


@app.get("/messages/{id}", response_model=MessageOut) 
async def get_message(id: int, session = Depends(get_session)): 
    """Retrieves the message with the specified id."""

    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageOut(
        id=message.id,
        text=message.text,
        author=message.author,
        timestamp=message.timestamp,
        tags=[t.name for t in message.tags]
    )

@app.delete("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def delete_message(id: int, session = Depends(get_session)): 
    """Deletes the message with the specified id."""

    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    deleted_message = MessageOut(
        id=message.id,
        text=message.text,
        author=message.author,
        timestamp=message.timestamp,
        tags=[t.name for t in message.tags]
    )
    old_tags = list(message.tags)

    session.delete(message)
    session.flush()

    for tag in old_tags:
        if not tag.messages:
            session.delete(tag)

    session.commit()

    return MessageResponse(status="deleted", data = deleted_message)
    



@app.put("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def edit_message(id: int, update: MessageIn, session = Depends(get_session)): 
    """Edits the message with the specified id."""


    message = session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.text = update.text
    message.author = update.author

    # --- Update tags ---
    tag_objects = []
    for tag_name in set(update.tags):
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            session.flush() 
        tag_objects.append(tag)
    old_tags = list(message.tags)
    message.tags = tag_objects  
    session.flush()

    new_tag_ids = {t.id for t in message.tags}
    for tag in old_tags:
        if tag.id not in new_tag_ids:
            if not tag.messages:
                session.delete(tag)

    session.commit()
    session.refresh(message)

    return MessageResponse(
        status="updated",
        data=MessageOut(
            id=message.id,
            text=message.text,
            author=message.author,
            timestamp=message.timestamp,
            tags=[t.name for t in message.tags]
        )
    )
