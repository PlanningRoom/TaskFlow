from fastapi import APIRouter

from taskflow.api.v1.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)

__all__ = ["api_router"]
