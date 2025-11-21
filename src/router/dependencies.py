from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from . import auth

security = HTTPBearer()
auth_router = APIRouter()


class TokenRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/auth/token")
def issue_token(payload: TokenRequest):
    token = auth.issue_token(payload.username, payload.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return {"token": token}

class SetupRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/auth/setup")
def setup_credentials(payload: SetupRequest):
    created = auth.create_credentials_if_absent(payload.username, payload.password)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credentials already exist",
        )
    return {"status": "created"}


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    if auth.verify_token(token):
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
