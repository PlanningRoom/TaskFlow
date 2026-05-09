from fastapi import APIRouter

from taskflow.api.v1.activity import router as activity_router
from taskflow.api.v1.auth import router as auth_router
from taskflow.api.v1.comments import router as comments_router
from taskflow.api.v1.dashboard import router as dashboard_router
from taskflow.api.v1.labels import router as labels_router
from taskflow.api.v1.notifications import router as notifications_router
from taskflow.api.v1.projects import router as projects_router
from taskflow.api.v1.search import router as search_router
from taskflow.api.v1.tasks import router as tasks_router
from taskflow.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(labels_router)
api_router.include_router(projects_router)
api_router.include_router(tasks_router)
api_router.include_router(comments_router)
api_router.include_router(activity_router)
api_router.include_router(notifications_router)
api_router.include_router(search_router)
api_router.include_router(dashboard_router)

__all__ = ["api_router"]
