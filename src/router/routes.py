from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.encoders import jsonable_encoder
from dockerutil import utils
from .dependencies import require_auth
from .auth import get_credentials
from services.container_service import (
    ContainerDeleteError,
    ContainerInUseError,
    ContainerNotFoundError,
    ContainerStartError,
    ContainerStopError,
    delete_container as service_delete_container,
    list_containers_summary,
    start_container as service_start_container,
    stop_container as service_stop_container,
)
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

Image and container services live under `services/` to keep Docker logic reusable.
"""

@api_router.get("/status")
def status():
    user_status = True if (get_credentials() is not None) else False
    status = {
        "status": "online",
        "user_exist": user_status,
    }
    return jsonable_encoder(status)


@api_router.get("/cli/info")
def cli_info(_: str = Depends(require_auth)):
    return cli.info()


@api_router.get("/cli/containers/list/info")
def container_info(_: str = Depends(require_auth)):
    containers = [container.attrs for container in cli.containers.list()]
    return jsonable_encoder(containers)


@api_router.get("/cli/containers/list")
def container_list(_: str = Depends(require_auth)):
    return jsonable_encoder(list_containers_summary(cli))


@api_router.post("/cli/containers/{container_id}/start")
def start_container_route(container_id: str, _: str = Depends(require_auth)):
    try:
        service_start_container(cli, container_id)
    except ContainerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ContainerStartError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return {"status": "started", "id": container_id}


@api_router.post("/cli/containers/{container_id}/stop")
def stop_container_route(container_id: str, _: str = Depends(require_auth)):
    try:
        service_stop_container(cli, container_id)
    except ContainerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ContainerStopError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return {"status": "stopped", "id": container_id}


@api_router.delete("/cli/containers/{container_id}")
def delete_container_route(container_id: str, _: str = Depends(require_auth)):
    try:
        service_delete_container(cli, container_id)
    except ContainerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ContainerInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ContainerDeleteError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return {"status": "deleted", "id": container_id}

@api_router.get("/cli/images/list/info")
def image_info(_: str = Depends(require_auth)):
    images = [image.attrs for image in cli.images.list()]
    return jsonable_encoder(images)

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
