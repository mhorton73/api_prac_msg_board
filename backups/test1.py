
# start server with python -m uvicorn test:app --reload (--port 800x if need be)
# netstat -ano | findstr :8000 to check the server status
# taskkill /PID <pid> /F to free up the port


# Replace Dict with dict, List with list, then remove import from typing
# look into splitting into multiple files
# Cache-ability
# tie users to messages as owners, add authentication, etc
# add SQLite to save messages, moving to a database will help.
# learn to decode properly

# other potential options: normalize datetime handling, use a lock to fix global state, add validation constraints,
# health check endpooint, partial update endpoint (patch), metadata, logging


import json 
from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict 
from datetime import datetime, timezone 



# -------- Config -------- 

FILE_NAME = "messages.json" 



# -------- Data Models -------- 

class Message(BaseModel): 
    text: str 
    author: str 
    tags: List[str] = Field(default_factory=list)

class MessageOut(BaseModel): 
    id: int 
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
    
    
    
# -------- Storage -------- 
    
def load_messages(): 
    try: 
        with open(FILE_NAME, "r") as f: return json.load(f) 
    except FileNotFoundError: return [] 
    
def save_messages(messages): 
    with open(FILE_NAME, "w") as f:
        json.dump(messages, f, indent=4) 



# -------- Util -------- 

def get_next_id(messages):
    if not messages:
         return 0 
    return max(m["id"] for m in messages) + 1 

# Obsolete function 
# def get_message_index(messages, message_id): 
#     for i, m in enumerate(messages): 
#         if m["id"] == message_id: 
#             return i 
#     return None 

def get_message_or_404(messages: List[Dict], id: int) -> Dict: 
    for msg in messages: 
        if msg["id"] == id: 
            return msg 
    raise HTTPException(status_code=404, detail="Message not found") 
    


# -------- App -------- 

app = FastAPI() 
messages: List[Dict] = load_messages()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------- Endpoints -------- 

@app.post("/messages", response_model=MessageResponse, status_code=201) 
async def add_message(message: Message): 
    """Post a message with text, author and optional tags. Records timestamp and generates a unique id."""

    new_message = { 
        "id": get_next_id(messages), 
        "text": message.text, 
        "author": message.author, 
        "timestamp": datetime.now(timezone.utc).isoformat(), 
        "tags": message.tags 
        } 
    
    messages.append(new_message) 
    save_messages(messages) 
    
    response_data = MessageOut(**new_message) 
    return MessageResponse(status = "added", data = response_data) 


@app.get("/messages", response_model=MessageListResponse) 
async def get_messages( 
        author: str = None, 
        tag: str = None, 
        page: int = 1, 
        limit: int = 10, 
        sort: str = "timestamp", 
        order: str = "desc" 
    ):
    """Lists all stored messages. Default sorted by most recent post. Can be sorted by author or text."""

    filtered = messages.copy()
    allowed_sorts = ["timestamp", "author", "text"] 
    if sort not in allowed_sorts: 
        raise HTTPException(status_code=400, detail="Invalid sort field") 
    
    # --- Filtering --- 
    
    if author: 
        filtered = [m for m in filtered if m["author"].lower() == author.lower()] 

    if tag: 
        filtered = [m for m in filtered if tag.lower() in [t.lower() for t in m["tags"]]] 
        
    # --- Sorting --- 
    
    reverse = True if order == "desc" else False 
    
    if sort == "timestamp": 
        filtered = sorted( 
            filtered, 
            key = lambda m: datetime.fromisoformat(m["timestamp"]), 
            reverse = reverse
        ) 
    else: 
        filtered = sorted( 
            filtered, 
            key = lambda m: m[sort], 
            reverse = reverse 
        )
    
    # --- Pagination --- 
    
    start = (page-1)*limit 
    end = start + limit 

    message_out = [MessageOut(**m) for m in filtered[start:end]] 
    return MessageListResponse( 
        total = len(filtered), 
        page = page, 
        limit = limit, 
        messages = message_out 
    ) 


@app.get("/messages/{id}", response_model=MessageOut) 
async def get_message(id: int): 
    """Retrieves the message with the specified id."""

    message = get_message_or_404(messages, id) 
    return message 


@app.delete("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def delete_message(id: int): 
    """Deletes the message with the specified id."""

    message = get_message_or_404(messages, id) 
    messages.remove(message) 
    save_messages(messages) 

    return MessageResponse(status="deleted", data = MessageOut(**message)) 


@app.put("/messages/{id}", response_model=MessageResponse, status_code=200) 
async def edit_message(id: int, updated: Message): 
    """Edits the message with the specified id."""

    message = get_message_or_404(messages, id) 
    message["text"] = updated.text 
    message["author"] = updated.author 
    message["tags"] = updated.tags 
    save_messages(messages) 

    return MessageResponse(status="updated", data = MessageOut(**message))