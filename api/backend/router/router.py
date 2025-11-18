from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from dockerutil import utils
from . import auth

router = FastAPI()
cli = utils.init()
security = HTTPBearer()


class TokenRequest(BaseModel):
    username: str
    password: str


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

@router.get("/status")
def response():
    return {"status": "online"}


@router.post("/auth/token")
def response(payload: TokenRequest):
    token = auth.issue_token(payload.username, payload.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return {"token": token}

@router.get("/cli/info")
def response(_: str = Depends(require_auth)):
    return cli.info()

@router.get("/cli/containers/list/info")
def response(_: str = Depends(require_auth)):
    containers = [container.attrs for container in cli.containers.list()]
    return jsonable_encoder(containers)

@router.get("/cli/containers/list")
def response(_: str = Depends(require_auth)):
    container_list = []
    for container in cli.containers.list():
        attrs = container.attrs
        container_list.append({
            "id": attrs.get("Id"),
            "image": attrs.get("Config", {}).get("Image"),
            "command": attrs.get("Config", {}).get("Cmd"),
            "name": attrs.get("Name", "").lstrip("/"),
            "created": attrs.get("Created"),
            "status": attrs.get("State", {}).get("Status"),
            "ports": attrs.get("NetworkSettings", {}).get("Ports"),
        })
    return jsonable_encoder(container_list)
