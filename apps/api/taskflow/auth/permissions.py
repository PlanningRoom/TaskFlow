"""Permission table per PRD §2.1 / TDD §11.5.

Two-layer model:
- Workspace role: owner > admin > member > viewer.
- Project access: an explicit `project_memberships` row (owner/admin have
  implicit access to all projects in their workspace).

Each `Action` is allowed to a fixed set of roles. Some actions also require
project access; that's enforced separately by `require_project_access`.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Action(StrEnum):
    # Workspace-level
    UPDATE_WORKSPACE = "update_workspace"
    INVITE_USERS = "invite_users"
    REMOVE_USERS = "remove_users"
    CHANGE_USER_ROLES = "change_user_roles"
    # Project-level
    CREATE_PROJECT = "create_project"
    MANAGE_PROJECT_SETTINGS = "manage_project_settings"
    MANAGE_PROJECT_ACCESS = "manage_project_access"
    # Task / content
    CREATE_TASK = "create_task"
    EDIT_TASK = "edit_task"
    CHANGE_TASK_STATUS = "change_task_status"
    ADD_COMMENT = "add_comment"
    MANAGE_LABELS = "manage_labels"
    # Read access
    VIEW_CONTENT = "view_content"
    SEARCH = "search"
    RECEIVE_NOTIFICATIONS = "receive_notifications"


# PRD §2.1 mapped exhaustively. Truth table source:
#   Y = role permitted; absence = denied.
PERMISSIONS: Final[dict[Action, frozenset[Role]]] = {
    Action.UPDATE_WORKSPACE: frozenset({Role.OWNER, Role.ADMIN}),
    Action.INVITE_USERS: frozenset({Role.OWNER, Role.ADMIN}),
    Action.REMOVE_USERS: frozenset({Role.OWNER}),
    Action.CHANGE_USER_ROLES: frozenset({Role.OWNER, Role.ADMIN}),
    Action.CREATE_PROJECT: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER}),
    Action.MANAGE_PROJECT_SETTINGS: frozenset({Role.OWNER, Role.ADMIN}),
    Action.MANAGE_PROJECT_ACCESS: frozenset({Role.OWNER, Role.ADMIN}),
    Action.CREATE_TASK: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER}),
    Action.EDIT_TASK: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER}),
    Action.CHANGE_TASK_STATUS: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER}),
    Action.ADD_COMMENT: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER}),
    Action.MANAGE_LABELS: frozenset({Role.OWNER, Role.ADMIN}),
    Action.VIEW_CONTENT: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER, Role.VIEWER}),
    Action.SEARCH: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER, Role.VIEWER}),
    Action.RECEIVE_NOTIFICATIONS: frozenset({Role.OWNER, Role.ADMIN, Role.MEMBER, Role.VIEWER}),
}


def is_allowed(role: str, action: Action) -> bool:
    """Pure check against the role × action table. Project access is separate."""
    try:
        role_enum = Role(role)
    except ValueError:
        return False
    return role_enum in PERMISSIONS[action]


def has_implicit_project_access(role: str) -> bool:
    """Owner and Admin see every project in the workspace (PRD §5.2 / TDD §11.5)."""
    return role in (Role.OWNER.value, Role.ADMIN.value)
