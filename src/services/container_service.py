from typing import Any, Dict, List

from docker.errors import APIError, NotFound


class ContainerServiceError(Exception):
    """Base error for container service operations."""


class ContainerNotFoundError(ContainerServiceError):
    """Raised when a container cannot be found."""


class ContainerInUseError(ContainerServiceError):
    """Raised when a running container cannot be removed."""


class ContainerDeleteError(ContainerServiceError):
    """Raised for other container delete failures."""


class ContainerStopError(ContainerServiceError):
    """Raised when a container cannot be stopped."""


class ContainerStartError(ContainerServiceError):
    """Raised when a container cannot be started."""


def list_containers_summary(cli) -> List[Dict[str, Any]]:
    """Return a summary of containers with selected fields."""
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
    return summary


def delete_container(cli, container_id: str) -> None:
    """Delete a container by id and normalize Docker errors."""
    try:
        container = cli.containers.get(container_id)
    except NotFound as exc:
        raise ContainerNotFoundError(f"Container {container_id} not found") from exc

    try:
        container.remove()
    except APIError as exc:
        if getattr(exc, "status_code", None) == 409:
            raise ContainerInUseError(exc.explanation or "Container is running") from exc
        raise ContainerDeleteError(exc.explanation or "Failed to delete container") from exc


def stop_container(cli, container_id: str) -> None:
    """Stop a container by id while normalizing errors."""
    try:
        container = cli.containers.get(container_id)
    except NotFound as exc:
        raise ContainerNotFoundError(f"Container {container_id} not found") from exc

    try:
        container.stop()
    except APIError as exc:
        raise ContainerStopError(exc.explanation or "Failed to stop container") from exc


def start_container(cli, container_id: str) -> None:
    """Start a container by id while normalizing errors."""
    try:
        container = cli.containers.get(container_id)
    except NotFound as exc:
        raise ContainerNotFoundError(f"Container {container_id} not found") from exc

    try:
        container.start()
    except APIError as exc:
        raise ContainerStartError(exc.explanation or "Failed to start container") from exc
