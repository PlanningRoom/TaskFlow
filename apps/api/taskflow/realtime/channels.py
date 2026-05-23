"""Channel-key helpers (TDD §10.1).

Three channel families:
  - `user:{user_id}`       — per-recipient (notifications, control messages)
  - `workspace:{ws_id}`    — workspace-wide (activity, settings)
  - `project:{project_id}` — per-project (tasks, comments, project-scope activity)
"""

from __future__ import annotations

from uuid import UUID


def user_channel(user_id: UUID) -> str:
    return f"user:{user_id}"


def workspace_channel(workspace_id: UUID) -> str:
    return f"workspace:{workspace_id}"


def project_channel(project_id: UUID) -> str:
    return f"project:{project_id}"
