
# start server with python -m uvicorn backend.main:app --reload (--port 800x if need be)
# netstat -ano | findstr :8000 to check the server status
# taskkill /PID <pid> /F to free up the port

# Goals
# Multi-tag filtering
# Reply feature
# Image posting
# Move to PostgreSQL
# look into docker
# add README and documentation
# Migration with alembic?
# Automated testing, input validation + constraints
# Deploy on Render


# Other things to look into at some point:
# Replace access token function inputs with pydantic models instead of dicts
# Cache-ability
# use a lock to fix global state 
# health check endpoint, partial update endpoint (patch), metadata, logging
# learn more about Depends from fastapi

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
