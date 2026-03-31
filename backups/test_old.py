
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

messages = []


class Message(BaseModel):
    text: str


@app.post("/messages")
async def add_message(message: Message):
    messages.append(message)
    return{"status": "added", "messages": messages}

@app.get("/messages")
async def get_messages():
    return {"messages": [m.text for m in messages]}

@app.get("/messages/{index}")
async def get_message(index: int):
    if 0 <= index < len(messages):
        return {"message": messages[index]}
    return {"error": "Message not found"}

@app.delete("/messages/{index}")
async def delete_message(index: int):
    if 0<= index < len(messages):
        removed = messages.pop(index)
        return{"status": "deleted", "message": removed}
    return{"error": "Message not found"}

@app.put("/messages/{index}")
async def delete_message(index: int, new_message: Message):
    if 0<= index < len(messages):
        messages[index] = new_message
        return{"status": "updated", "message": messages[index].text}
    return{"error": "Message not found"}
