"""FastAPI dependencies for auth + project access (TDD §7.3 / §11.5)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth import sessions as session_module
from taskflow.auth.csrf import csrf_check
from taskflow.auth.permissions import Action, has_implicit_project_access, is_allowed
from taskflow.db.models.project import ProjectMembership
from taskflow.db.models.session import Session as SessionModel
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.db.session import get_db as _get_db_iter
from taskflow.errors import PermissionDeniedError
from taskflow.settings import settings


async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in _get_db_iter():
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]


class _UnauthenticatedError(PermissionDeniedError):
    """401-equivalent: no session or session invalid."""

    code = "UNAUTHENTICATED"
    status_code = 401


async def current_session(request: Request, db: DbDep) -> SessionModel:
    """Resolve, refresh, and return the active `sessions` row.

    Raises 401 (`UNAUTHENTICATED`) on missing/expired/idle/deleted-user.
    """
    raw = request.cookies.get(settings.session_cookie_name)
    if not raw:
        raise _UnauthenticatedError("Authentication required.")

    row = await session_module.lookup_session(db, raw)
    if row is None:
        raise _UnauthenticatedError("Authentication required.")
    return row


SessionDep = Annotated[SessionModel, Depends(current_session)]


async def current_user(db: DbDep, session: SessionDep) -> User:
    """Return the User behind the active session. Rejects deleted users (ADR 065)."""
    user = await db.scalar(select(User).where(User.id == session.user_id))
    if user is None or user.deleted_at is not None:
        raise _UnauthenticatedError("Authentication required.")
    return user


UserDep = Annotated[User, Depends(current_user)]


async def current_workspace(db: DbDep, user: UserDep) -> Workspace:
    """One-workspace-per-user (PRD §4.1)."""
    ws = await db.scalar(select(Workspace).where(Workspace.id == user.workspace_id))
    assert ws is not None  # FK guarantees existence
    return ws


WorkspaceDep = Annotated[Workspace, Depends(current_workspace)]


def require_action(
    action: Action,
) -> Callable[[User], Coroutine[Any, Any, None]]:
    """Factory: ensure the caller's role is allowed to perform `action`."""

    async def _check(user: UserDep) -> None:
        if not is_allowed(user.role, action):
            raise PermissionDeniedError(
                "You don't have permission to perform that action.",
                code="PERMISSION_DENIED",
            )

    return _check


def require_role(
    *roles: str,
) -> Callable[[User], Coroutine[Any, Any, None]]:
    """Factory: ensure the caller's role is in `roles` (TDD §11.5).

    Prefer `require_action(Action.X)` for endpoint gating — it stays correct if
    PRD §2.1 changes which roles can perform an action. `require_role` is the
    spec-named primitive for cases where you really do want a role floor.
    """
    allowed = frozenset(roles)

    async def _check(user: UserDep) -> None:
        if user.role not in allowed:
            raise PermissionDeniedError(
                "You don't have permission to perform that action.",
                code="PERMISSION_DENIED",
            )

    return _check


def require_project_access(
    project_id_param: str = "project_id",
) -> Callable[..., Coroutine[Any, Any, None]]:
    """Factory: ensure the caller has access to the project named in the path."""

    async def _check(request: Request, db: DbDep, user: UserDep) -> None:
        raw = request.path_params.get(project_id_param)
        if raw is None:
            raise PermissionDeniedError("Project id missing from path.", code="PROJECT_ID_REQUIRED")
        project_id = UUID(raw)

        if has_implicit_project_access(user.role):
            return

        membership = await db.scalar(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project_id,
                ProjectMembership.user_id == user.id,
            )
        )
        if membership is None:
            raise PermissionDeniedError(
                "You don't have access to this project.", code="PROJECT_ACCESS_DENIED"
            )

    return _check


async def verify_csrf(request: Request, session: SessionDep) -> None:
    """CSRF double-submit check on mutating methods (ADR 051)."""
    cookie = request.cookies.get(settings.csrf_cookie_name)
    header = request.headers.get(settings.csrf_header_name)
    if not csrf_check(request.method, header_token=header, cookie_token=cookie, session=session):
        raise PermissionDeniedError("CSRF check failed.", code="CSRF_INVALID")
