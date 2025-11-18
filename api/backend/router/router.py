from fastapi import FastAPI

from .dependencies import auth_router
from .routes import api_router

router = FastAPI()
router.include_router(auth_router)
router.include_router(api_router)
