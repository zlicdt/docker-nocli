from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from dockerutil import utils
from .dependencies import require_auth

api_router = APIRouter()
cli = utils.init()


@api_router.get("/status")
def status():
    return {"status": "online"}


@api_router.get("/cli/info")
def cli_info(_: str = Depends(require_auth)):
    return cli.info()


@api_router.get("/cli/containers/list/info")
def container_info(_: str = Depends(require_auth)):
    containers = [container.attrs for container in cli.containers.list()]
    return jsonable_encoder(containers)


@api_router.get("/cli/containers/list")
def container_list(_: str = Depends(require_auth)):
    summary = []
    for container in cli.containers.list():
        attrs = container.attrs
        summary.append({
            "id": attrs.get("Id"),
            "image": attrs.get("Config", {}).get("Image"),
            "command": attrs.get("Config", {}).get("Cmd"),
            "name": attrs.get("Name", "").lstrip("/"),
            "created": attrs.get("Created"),
            "status": attrs.get("State", {}).get("Status"),
            "ports": attrs.get("NetworkSettings", {}).get("Ports"),
        })
    return jsonable_encoder(summary)
