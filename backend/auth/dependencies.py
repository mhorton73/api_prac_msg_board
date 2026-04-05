
# change to return user id instead of username

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from .utils import ALGORITHM, SECRET_KEY
from ..schemas import CurrentUser

security = HTTPBearer()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    token = auth.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return CurrentUser(id=user_id, username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")