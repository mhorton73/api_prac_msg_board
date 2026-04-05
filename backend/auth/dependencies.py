
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from .utils import decode_token

security = HTTPBearer()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    return decode_token(auth.credentials)