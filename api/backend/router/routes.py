from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.encoders import jsonable_encoder

from dockerutil import utils
from .dependencies import require_auth
from services.image_service import (
    ImageDeleteError,
    ImageInUseError,
    ImageNotFoundError,
    delete_image as service_delete_image,
    list_images_summary,
)

api_router = APIRouter()
cli = utils.init()
"""
(_: str = Depends(require_auth)) equals to `require auth`
"""

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

@api_router.get("/cli/images/list/info")
def image_info(_: str = Depends(require_auth)):
    images = [image.attrs for image in cli.images.list()]
    return jsonable_encoder(images)

"""
The image services is included in `services/image_service.py`,
but others have not done yet. 
"""

@api_router.get("/cli/images/list")
def image_list(_: str = Depends(require_auth)):
    return jsonable_encoder(list_images_summary(cli))


@api_router.delete("/cli/images/{image_id}")
def delete_image(image_id: str, _: str = Depends(require_auth)):
    try:
        service_delete_image(cli, image_id)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ImageInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ImageDeleteError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return {"status": "deleted", "id": image_id}
