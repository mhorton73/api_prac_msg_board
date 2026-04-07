
# start server with python -m uvicorn backend.main:app --reload (--port 800x if need be)
# netstat -ano | findstr :8000 to check the server status
# taskkill /PID <pid> /F to free up the port

# Goals
#
# add documentation
# Automated testing, input validation + constraints
# Deploy on Render

# Other things to look into at some point/ in future projects:
#
# Multi-tag filtering
# Move to PostgreSQL
# Image posting
# Migration with alembic?
# look into docker


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import forum, auth


app = FastAPI() 
Base.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forum.router)
app.include_router(auth.router)
