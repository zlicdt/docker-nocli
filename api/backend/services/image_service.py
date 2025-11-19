from typing import List, Dict, Any

from docker.errors import APIError, NotFound


class ImageServiceError(Exception):
    """Base error for image service operations."""


class ImageNotFoundError(ImageServiceError):
    """Raised when the requested image cannot be found."""


class ImageInUseError(ImageServiceError):
    """Raised when an image cannot be deleted because it is in use."""


class ImageDeleteError(ImageServiceError):
    """Raised for other delete failures."""


def list_images_summary(cli) -> List[Dict[str, Any]]:
    """Return a summary of images with selected fields."""
    summary = []
    for image in cli.images.list():
        attrs = image.attrs
        repo_tag = (attrs.get("RepoTags") or ["<none>:<none>"])[0]
        if ":" in repo_tag:
            repository, tag = repo_tag.rsplit(":", 1)
        else:
            repository, tag = repo_tag, ""
        summary.append({
            "repository": repository,
            "tag": tag,
            "id": attrs.get("Id"),
            "created": attrs.get("Created"),
            "size": attrs.get("Size"),
        })
    return summary


def delete_image(cli, image_id: str) -> None:
    """Delete an image by id and normalize errors."""
    try:
        cli.images.remove(image_id)
    except NotFound as exc:
        raise ImageNotFoundError(f"Image {image_id} not found") from exc
    except APIError as exc:
        if getattr(exc, "status_code", None) == 409:
            raise ImageInUseError(exc.explanation or "Image is currently in use") from exc
        raise ImageDeleteError(exc.explanation or "Failed to delete image") from exc
