"""Permission table per PRD §2.1 / TDD §11.5.

Exhaustive: every (role × action) cell from PRD §2.1 is asserted.
"""

from __future__ import annotations

from taskflow.auth.permissions import Action, has_implicit_project_access, is_allowed

# Source of truth: PRD §2.1.
EXPECTED: dict[Action, dict[str, bool]] = {
    Action.UPDATE_WORKSPACE: {"owner": True, "admin": True, "member": False, "viewer": False},
    Action.INVITE_USERS: {"owner": True, "admin": True, "member": False, "viewer": False},
    Action.REMOVE_USERS: {"owner": True, "admin": False, "member": False, "viewer": False},
    Action.CHANGE_USER_ROLES: {"owner": True, "admin": True, "member": False, "viewer": False},
    Action.CREATE_PROJECT: {"owner": True, "admin": True, "member": True, "viewer": False},
    Action.MANAGE_PROJECT_SETTINGS: {
        "owner": True,
        "admin": True,
        "member": False,
        "viewer": False,
    },
    Action.MANAGE_PROJECT_ACCESS: {"owner": True, "admin": True, "member": False, "viewer": False},
    Action.CREATE_TASK: {"owner": True, "admin": True, "member": True, "viewer": False},
    Action.EDIT_TASK: {"owner": True, "admin": True, "member": True, "viewer": False},
    Action.CHANGE_TASK_STATUS: {"owner": True, "admin": True, "member": True, "viewer": False},
    Action.ADD_COMMENT: {"owner": True, "admin": True, "member": True, "viewer": False},
    Action.MANAGE_LABELS: {"owner": True, "admin": True, "member": False, "viewer": False},
    Action.VIEW_CONTENT: {"owner": True, "admin": True, "member": True, "viewer": True},
    Action.SEARCH: {"owner": True, "admin": True, "member": True, "viewer": True},
    Action.RECEIVE_NOTIFICATIONS: {"owner": True, "admin": True, "member": True, "viewer": True},
}


def test_every_role_action_cell_matches_prd() -> None:
    for action, by_role in EXPECTED.items():
        for role, expected in by_role.items():
            assert is_allowed(role, action) is expected, f"{role} × {action.value} = {expected}"


def test_unknown_role_is_denied_for_all_actions() -> None:
    for action in Action:
        assert is_allowed("intruder", action) is False


def test_implicit_project_access_only_for_owner_admin() -> None:
    assert has_implicit_project_access("owner") is True
    assert has_implicit_project_access("admin") is True
    assert has_implicit_project_access("member") is False
    assert has_implicit_project_access("viewer") is False
