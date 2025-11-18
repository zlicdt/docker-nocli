"""Router package for docker-nocli backend."""
"""Other model use `from router import router` to get FastAPI, no need to set path anymore"""
from .router import router  # re-export FastAPI router

__all__ = ["router"]
