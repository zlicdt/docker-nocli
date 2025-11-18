from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from dockerutil import utils

router = FastAPI()
cli = utils.init()

@router.get("/status")
def response():
    return {"status": "online"}

@router.get("/cli/info")
def response():
    return cli.info()

@router.get("/cli/containers/list/info")
def response():
    containers = [container.attrs for container in cli.containers.list()]
    return jsonable_encoder(containers)

@router.get("/cli/containers/list")
def response():
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
