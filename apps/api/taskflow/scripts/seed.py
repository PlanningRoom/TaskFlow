"""Idempotent seed script for the "Aurora Studio" demo workspace (ADR 066, TDD §15.3).

Run via `make seed` (or `python -m taskflow.scripts.seed` from inside the api container).
Re-running is a no-op — the workspace name is the idempotency key.

Layout produced:
- 1 workspace: "Aurora Studio"
- 5 users (owner / admin / 2 members / viewer)
- 8 labels (one per palette colour)
- 3 projects with varied access lists
- 30 tasks exercising every status, priority, label, and due-date state
- 10 comments — 3 with @mentions so notifications fire
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select

from taskflow.auth.passwords import hash_password
from taskflow.constants import LABEL_COLORS, TASK_PRIORITIES, TASK_STATUSES
from taskflow.db.models.label import Label
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.db.session import session_scope
from taskflow.services import comments as comment_service
from taskflow.services import labels as label_service
from taskflow.services import project_access as access_service
from taskflow.services import projects as project_service
from taskflow.services import tasks as task_service

logger = structlog.get_logger(__name__)

WORKSPACE_NAME = "Aurora Studio"
SEED_PASSWORD = "correct-horse-battery-staple"  # noqa: S105  # pragma: allowlist secret

# ─── Users ──────────────────────────────────────────────────────────────────
USERS = [
    ("owner@aurora.test", "Aurora Owens", "owner"),
    ("admin@aurora.test", "Adam Min", "admin"),
    ("dev1@aurora.test", "Dana Engineer", "member"),
    ("dev2@aurora.test", "Mason Code", "member"),
    ("viewer@aurora.test", "Vivian Watch", "viewer"),
]

# ─── Projects ───────────────────────────────────────────────────────────────
# (name, color, access_emails) — Owner+Admin have implicit access, listed
# only when also being granted explicit project access. `None` color falls
# back to the default in the service.
PROJECTS = [
    (
        "Mobile App Redesign",
        "purple",
        ["dev1@aurora.test", "dev2@aurora.test", "viewer@aurora.test"],
    ),
    ("API Migration", "blue", ["dev1@aurora.test"]),
    ("Marketing Site", "green", ["viewer@aurora.test"]),
]


def _today() -> date:
    return datetime.now(UTC).date()


def _due_buckets() -> dict[str, date | None]:
    today = _today()
    return {
        "overdue_a": today - timedelta(days=3),
        "overdue_b": today - timedelta(days=10),
        "today": today,
        "this_week_a": today + timedelta(days=2),
        "this_week_b": today + timedelta(days=4),
        "future_a": today + timedelta(days=14),
        "future_b": today + timedelta(days=30),
        "none": None,
    }


# ─── Tasks ─────────────────────────────────────────────────────────────────
# Each tuple: (project_index, title, description, status, priority, assignee_email,
# due_bucket, label_color_names)
TASKS: list[tuple[int, str, str, str, str, str | None, str, list[str]]] = [
    # Project 0 — Mobile App Redesign (broad access)
    (
        0,
        "Sprint planning review",
        "Review and finalise sprint scope.",
        "in_progress",
        "high",
        "dev1@aurora.test",
        "today",
        ["blue", "purple"],
    ),
    (
        0,
        "Audit current navigation",
        "Document existing nav patterns.",
        "done",
        "medium",
        "dev2@aurora.test",
        "none",
        ["blue", "green", "amber", "pink"],
    ),
    (
        0,
        "Tab bar redesign",
        "Iterate on the bottom-tab layout.",
        "in_progress",
        "high",
        "dev1@aurora.test",
        "this_week_a",
        ["purple", "pink"],
    ),
    (
        0,
        "Onboarding flow copy",
        "Refresh first-run welcome copy.",
        "todo",
        "medium",
        "dev2@aurora.test",
        "future_a",
        ["green"],
    ),
    (
        0,
        "Splash screen animation",
        "Add a subtle splash transition.",
        "backlog",
        "low",
        None,
        "none",
        ["pink"],
    ),
    (
        0,
        "Empty states pass",
        "Implement DRD §16 empty states.",
        "in_review",
        "medium",
        "dev1@aurora.test",
        "overdue_a",
        ["amber", "blue"],
    ),
    (
        0,
        "Dark mode tokens",
        "Define DRD §13 dark-mode tokens.",
        "backlog",
        "low",
        None,
        "future_b",
        ["purple"],
    ),
    (
        0,
        "Animation reduced-motion",
        "Honour prefers-reduced-motion.",
        "done",
        "low",
        "dev2@aurora.test",
        "none",
        ["amber"],
    ),
    (
        0,
        "Settings screen scaffolding",
        "Wire the new settings tabs.",
        "in_progress",
        "medium",
        "dev1@aurora.test",
        "this_week_b",
        ["blue"],
    ),
    (
        0,
        "Crash-on-launch (Android 12)",
        "Investigate startup crash.",
        "in_progress",
        "urgent",
        "dev2@aurora.test",
        "overdue_b",
        ["red"],
    ),
    # Project 1 — API Migration (dev1 access)
    (
        1,
        "Cutover plan draft",
        "Draft the cutover runbook.",
        "in_review",
        "high",
        "dev1@aurora.test",
        "this_week_a",
        ["blue", "red"],
    ),
    (
        1,
        "Auth endpoint shim",
        "Add temporary auth shim.",
        "done",
        "medium",
        "dev1@aurora.test",
        "none",
        ["green"],
    ),
    (
        1,
        "Workspace endpoint parity",
        "Diff legacy vs new responses.",
        "in_progress",
        "high",
        "dev1@aurora.test",
        "today",
        ["blue", "amber"],
    ),
    (
        1,
        "Deprecation notice copy",
        "Land the deprecation banner.",
        "todo",
        "low",
        None,
        "future_a",
        ["pink"],
    ),
    (
        1,
        "Performance regression sweep",
        "Re-run K6 against the new stack.",
        "backlog",
        "medium",
        "dev1@aurora.test",
        "future_b",
        ["orange"],
    ),
    (
        1,
        "Migrate webhooks",
        "Port webhook handlers.",
        "todo",
        "medium",
        "dev1@aurora.test",
        "future_a",
        ["orange", "blue"],
    ),
    (
        1,
        "Search reindex script",
        "One-shot to rebuild tsvector.",
        "in_progress",
        "urgent",
        "dev1@aurora.test",
        "overdue_a",
        ["red", "amber"],
    ),
    (
        1,
        "Schema diff doc",
        "Document the schema diff.",
        "done",
        "low",
        "dev1@aurora.test",
        "none",
        ["cyan"],
    ),
    (
        1,
        "Decommission timeline",
        "Confirm shutdown date.",
        "cancelled",
        "none",
        None,
        "none",
        ["cyan"],
    ),
    # Project 2 — Marketing Site (viewer access)
    (
        2,
        "New landing hero",
        "Replace the landing-page hero.",
        "in_progress",
        "high",
        None,
        "today",
        ["green", "purple"],
    ),
    (
        2,
        "Pricing page revamp",
        "Tighten the pricing copy.",
        "todo",
        "medium",
        None,
        "this_week_b",
        ["green"],
    ),
    (
        2,
        "Customer logos refresh",
        "Rotate the homepage logo strip.",
        "backlog",
        "low",
        None,
        "future_b",
        ["amber"],
    ),
    (2, "SEO meta cleanup", "Audit og: tags across pages.", "done", "low", None, "none", ["cyan"]),
    (
        2,
        "Blog template typography",
        "Refresh blog typography.",
        "in_review",
        "medium",
        None,
        "this_week_a",
        ["pink", "amber"],
    ),
    (
        2,
        "Accessibility audit",
        "Run axe across the site.",
        "backlog",
        "high",
        None,
        "future_a",
        ["red", "green"],
    ),
    (
        2,
        "Analytics events rename",
        "Standardise event names.",
        "in_progress",
        "medium",
        None,
        "overdue_a",
        ["orange"],
    ),
    (
        2,
        "Old screenshots removal",
        "Drop legacy product shots.",
        "cancelled",
        "none",
        None,
        "none",
        ["cyan"],
    ),
    (
        2,
        "Footer redesign",
        "Bring the footer in line with DRD §6.",
        "backlog",
        "low",
        None,
        "none",
        ["purple"],
    ),
    (
        2,
        "Lighthouse pass",
        "Score ≥ 90 across the board.",
        "done",
        "medium",
        None,
        "none",
        ["green", "amber"],
    ),
    (2, "404 page copy", "Friendlier 404 message.", "todo", "low", None, "future_a", ["pink"]),
]

# ─── Comments (with @mentions) ─────────────────────────────────────────────
# (task_title, author_email, body)
COMMENTS = [
    (
        "Sprint planning review",
        "owner@aurora.test",
        "Looks good — @dev1 can you confirm the new acceptance criteria?",
    ),
    ("Tab bar redesign", "admin@aurora.test", "@dev1 want to pair on this Friday afternoon?"),
    (
        "Workspace endpoint parity",
        "owner@aurora.test",
        "I'm seeing a diff in the `members` shape — @dev1 ping me.",
    ),
    (
        "Empty states pass",
        "dev2@aurora.test",
        "Most of these are wired; review when you have a moment.",
    ),
    ("Cutover plan draft", "admin@aurora.test", "Add a rollback section before we ship."),
    (
        "Search reindex script",
        "owner@aurora.test",
        "@dev1 prioritise this — it's blocking the migration.",
    ),
    ("New landing hero", "owner@aurora.test", "Copy is final — go ahead and ship."),
    (
        "Pricing page revamp",
        "admin@aurora.test",
        "@admin can you double-check the enterprise tier copy?",
    ),
    ("Accessibility audit", "owner@aurora.test", "We should run this against staging, not prod."),
    (
        "Analytics events rename",
        "admin@aurora.test",
        "Reminder: prod schema is frozen — change names downstream first.",
    ),
]


async def _existing_workspace(db) -> Workspace | None:
    return await db.scalar(select(Workspace).where(Workspace.name == WORKSPACE_NAME))


async def _seed_users(db, workspace_id: UUID) -> dict[str, User]:
    users: dict[str, User] = {}
    for email, name, role in USERS:
        user = User(
            workspace_id=workspace_id,
            email=email,
            name=name,
            role=role,
            password_hash=hash_password(SEED_PASSWORD),
        )
        db.add(user)
        users[email] = user
    await db.flush()
    return users


async def _seed_labels(db, workspace_id: UUID, owner: User) -> dict[str, Label]:
    labels: dict[str, Label] = {}
    for color in LABEL_COLORS:
        label = await label_service.create_label(
            db,
            workspace_id=workspace_id,
            actor=owner,
            name=color.capitalize(),
            color=color,
        )
        labels[color] = label
    return labels


async def _seed_projects_and_access(db, owner: User, users_by_email: dict[str, User]) -> list:
    projects = []
    for name, color, access_emails in PROJECTS:
        project = await project_service.create_project(
            db,
            actor=owner,
            name=name,
            description=None,
            color=color,
        )
        for email in access_emails:
            target = users_by_email[email]
            await access_service.grant_access(
                db, actor=owner, project=project, target_user_id=target.id
            )
        projects.append(project)
    return projects


async def _seed_tasks(
    db,
    owner: User,
    users_by_email: dict[str, User],
    labels_by_color: dict[str, Label],
    projects: list,
) -> dict[str, UUID]:
    """Returns title → task_id."""
    due_buckets = _due_buckets()
    title_to_id: dict[str, UUID] = {}

    for (
        project_index,
        title,
        description,
        status,
        priority,
        assignee_email,
        due_bucket,
        label_colors,
    ) in TASKS:
        assert status in TASK_STATUSES, status
        assert priority in TASK_PRIORITIES, priority
        assignee_id = users_by_email[assignee_email].id if assignee_email else None
        label_ids = [labels_by_color[c].id for c in label_colors]

        # `create_task` doesn't accept status directly (defaults to backlog) — use
        # change_status after creation for non-default states.
        task = await task_service.create_task(
            db,
            actor=owner,
            project_id=projects[project_index].id,
            title=title,
            description=description,
            status=None,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_buckets[due_bucket],
            label_ids=label_ids,
        )
        if status != "backlog":
            await task_service.change_status(db, actor=owner, task=task, new_status=status)
        title_to_id[title] = task.id
    return title_to_id


async def _seed_comments(
    db,
    users_by_email: dict[str, User],
    task_ids_by_title: dict[str, UUID],
) -> None:
    for task_title, author_email, body in COMMENTS:
        author = users_by_email[author_email]
        await comment_service.create_comment(
            db,
            actor=author,
            task_id=task_ids_by_title[task_title],
            body=body,
        )


async def seed() -> int:
    """Seed the database. Returns the number of tasks created (0 if already seeded)."""
    async with session_scope() as db:
        if await _existing_workspace(db) is not None:
            logger.info("seed.skipped", reason="already_seeded", workspace=WORKSPACE_NAME)
            return 0

        workspace = Workspace(name=WORKSPACE_NAME)
        db.add(workspace)
        await db.flush()

        users_by_email = await _seed_users(db, workspace.id)
        owner = users_by_email["owner@aurora.test"]
        workspace.created_by = owner.id

        labels_by_color = await _seed_labels(db, workspace.id, owner)
        projects = await _seed_projects_and_access(db, owner, users_by_email)
        task_ids = await _seed_tasks(db, owner, users_by_email, labels_by_color, projects)
        await _seed_comments(db, users_by_email, task_ids)

        await db.commit()
        logger.info(
            "seed.complete",
            workspace=WORKSPACE_NAME,
            users=len(users_by_email),
            projects=len(projects),
            tasks=len(task_ids),
            comments=len(COMMENTS),
        )
        return len(task_ids)


def main() -> int:
    created = asyncio.run(seed())
    return 0 if created >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
