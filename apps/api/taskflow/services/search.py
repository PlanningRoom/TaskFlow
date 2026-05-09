"""Full-text search service (PRD §12.1, ADR 062)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.permissions import has_implicit_project_access
from taskflow.db.models.project import Project, ProjectMembership
from taskflow.db.models.task import Task
from taskflow.db.models.user import User

DEFAULT_LIMIT = 20


async def search_tasks(
    db: AsyncSession,
    *,
    user: User,
    query: str,
    include_cancelled: bool = False,
) -> list[tuple[Task, Project]]:
    """Return up to DEFAULT_LIMIT (Task, Project) pairs ranked by relevance."""
    q = (query or "").strip()
    if not q:
        return []

    tsquery = func.websearch_to_tsquery("english", q)
    rank = func.ts_rank_cd(Task.search_vector, tsquery)

    stmt = (
        select(Task, Project, rank.label("rank"))
        .join(Project, Project.id == Task.project_id)
        .where(
            Task.workspace_id == user.workspace_id,
            Task.search_vector.op("@@")(tsquery),
        )
    )
    if not include_cancelled:
        stmt = stmt.where(Task.status != "cancelled")
    if not has_implicit_project_access(user.role):
        stmt = stmt.join(
            ProjectMembership,
            (ProjectMembership.project_id == Project.id) & (ProjectMembership.user_id == user.id),
        )
    stmt = stmt.order_by(rank.desc(), Task.created_at.desc()).limit(DEFAULT_LIMIT)

    try:
        result = await db.execute(stmt)
    except (OperationalError, ProgrammingError):
        # `websearch_to_tsquery` is forgiving of malformed input, but defensive
        # in case of edge cases.
        return []

    return [(t, p) for t, p, _ in result.all()]
