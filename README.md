# Forum API

**A FastAPI-based forum backend with user authentication, tagging, and message management.**

---

## Tech Stack
- **Backend:** Python, FastAPI  
- **Database:** SQLite (SQLAlchemy ORM)  
- **Authentication:** JWT (access + refresh tokens)  
- **Password Security:** Argon2 hashing via PassLib  
- **Testing / Dev Tools:** Postman, Pydantic for validation  

---

## Key Features
- **User Authentication:** Register, login, refresh tokens, and logout  
- **Messages:** Create, edit, delete, and retrieve messages  
- **Tags:** Attach multiple tags to messages, filter by tag or author  
- **Pagination & Sorting:** Supports page/limit, sort by timestamp, author, or text  
- **Token Management:** Refresh tokens stored in DB, expired tokens automatically removed  

---

## API Endpoints (Selected)
**Auth**  
- `POST /auth/register` – Register a new user  
- `POST /auth/login` – Login and receive access & refresh tokens  
- `POST /auth/refresh` – Issue a new access token using refresh token  
- `POST /auth/logout` – Revoke current refresh token  

**Forum**  
- `POST /forum/messages` – Add a message (requires authentication)  
- `GET /forum/messages` – Retrieve messages with optional filtering & pagination  
- `GET /forum/messages/{id}` – Get a single message by ID  
- `PUT /forum/messages/{id}` – Edit a message (author only)  
- `DELETE /forum/messages/{id}` – Delete a message (author only)  

---

## Example Request

**POST /forum/messages**  

```json
{
  "text": "Hello world!",
  "tags": ["intro", "firstpost"]
}
```
## Response:
```json
{
  "status": "added",
  "data": {
    "id": 1,
    "text": "Hello world!",
    "author": "alice",
    "timestamp": "2026-04-06T12:34:56Z",
    "tags": ["intro", "firstpost"]
  }
}
```
## Future Improvements
- Implement front-end interface
- Reply threading for messages
- Multi-tag filtering & advanced search
- Automated testing suite
- Optional migration to PostgreSQL for production
  Image posting capabilities
