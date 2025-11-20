from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import auth_router
from .routes import api_router

import os

router = FastAPI()
router.include_router(auth_router)
router.include_router(api_router)
router.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:" + os.getenv("WEB_PORT", "8192")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)