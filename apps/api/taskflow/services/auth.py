"""Auth service layer (TDD §11, PRD §3, ADR 011/047/048/049/065)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth import sessions as session_helpers
from taskflow.auth.audit import write_audit_log
from taskflow.auth.passwords import hash_password, verify_password
from taskflow.auth.tokens import generate_token, hash_token
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.password_reset_token import PasswordResetToken
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.errors import AppError, ConflictError, NotFoundError, PermissionDeniedError


class InvalidCredentialsError(PermissionDeniedError):
    code = "INVALID_CREDENTIALS"
    status_code = 401


class InvalidTokenError(AppError):
    code = "INVALID_TOKEN"
    status_code = 400


class InvitationExpiredError(AppError):
    code = "INVITATION_EXPIRED"
    status_code = 400


def _client_ip(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def _user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("user-agent")


# ──────────────────────────────────────────────────────────────────────────────
# Sign-up
# ──────────────────────────────────────────────────────────────────────────────


async def signup(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    display_name: str,
    workspace_name: str,
    request: Request | None = None,
) -> tuple[User, session_helpers.SessionTokens]:
    """Atomically create a workspace + Owner + initial session (PRD §3.1)."""
    # Pre-check for an existing live user with that email anywhere; one workspace per email
    # is enforced by the `(workspace_id, lower(email))` partial unique index.
    existing = await db.scalar(
        select(User).where(User.email.ilike(email), User.deleted_at.is_(None))
    )
    if existing is not None:
        raise ConflictError("That email is already registered.", code="EMAIL_TAKEN")

    workspace = Workspace(name=workspace_name)
    db.add(workspace)
    await db.flush()

    user = User(
        workspace_id=workspace.id,
        email=email,
        name=display_name,
        role="owner",
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()

    # Backfill workspaces.created_by now that the user exists.
    workspace.created_by = user.id

    tokens = await session_helpers.create_session(
        db,
        user_id=user.id,
        ip=_client_ip(request),
        user_agent=_user_agent(request),
    )

    await write_audit_log(
        db,
        event_type="auth.signup",
        actor_id=user.id,
        target_id=workspace.id,
        request=request,
        metadata={"workspace_name": workspace_name},
    )
    return user, tokens


# ──────────────────────────────────────────────────────────────────────────────
# Login / logout
# ──────────────────────────────────────────────────────────────────────────────


async def login(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    request: Request | None = None,
) -> tuple[User, session_helpers.SessionTokens]:
    user = await db.scalar(select(User).where(User.email.ilike(email), User.deleted_at.is_(None)))
    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        await write_audit_log(
            db,
            event_type="auth.login.failure",
            actor_id=user.id if user else None,
            request=request,
            metadata={"email": email},
        )
        raise InvalidCredentialsError("Invalid email or password.")

    tokens = await session_helpers.create_session(
        db,
        user_id=user.id,
        ip=_client_ip(request),
        user_agent=_user_agent(request),
    )
    await write_audit_log(
        db,
        event_type="auth.login.success",
        actor_id=user.id,
        request=request,
    )
    return user, tokens


async def logout(
    db: AsyncSession,
    *,
    raw_session_token: str,
    user_id: UUID,
    request: Request | None = None,
) -> None:
    await session_helpers.delete_session(db, raw_session_token)
    await write_audit_log(db, event_type="auth.logout", actor_id=user_id, request=request)


# ──────────────────────────────────────────────────────────────────────────────
# Password reset
# ──────────────────────────────────────────────────────────────────────────────


async def request_password_reset(
    db: AsyncSession,
    *,
    email: str,
    request: Request | None = None,
) -> tuple[User | None, str | None]:
    """Generate a reset token if the user exists; otherwise pretend we did.

    Returns (user, raw_token) so callers can dispatch the email; (None, None) on
    no-such-user (the endpoint should not enumerate; mailers must respect this).
    """
    user = await db.scalar(select(User).where(User.email.ilike(email), User.deleted_at.is_(None)))
    if user is None:
        return None, None

    # ADR 049: only the most recent token per user is valid — invalidate prior ones.
    now = datetime.now(UTC)
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw, token_hash = generate_token(32)
    db.add(
        PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=now + timedelta(hours=1),
        )
    )
    await write_audit_log(
        db,
        event_type="auth.password_reset.requested",
        actor_id=user.id,
        request=request,
    )
    return user, raw


async def confirm_password_reset(
    db: AsyncSession,
    *,
    raw_token: str,
    new_password: str,
    request: Request | None = None,
) -> User:
    token_hash = hash_token(raw_token)
    row = await db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    if row is None or row.used_at is not None or row.expires_at <= datetime.now(UTC):
        raise InvalidTokenError("Invalid or expired token.")

    user = await db.scalar(select(User).where(User.id == row.user_id, User.deleted_at.is_(None)))
    if user is None:
        raise InvalidTokenError("Invalid or expired token.")

    user.password_hash = hash_password(new_password)
    row.used_at = datetime.now(UTC)
    await session_helpers.delete_sessions_for_user(db, user.id)

    await write_audit_log(
        db, event_type="auth.password_reset.completed", actor_id=user.id, request=request
    )
    return user


# ──────────────────────────────────────────────────────────────────────────────
# Authenticated profile mutations
# ──────────────────────────────────────────────────────────────────────────────


async def update_profile(
    db: AsyncSession,
    *,
    user: User,
    display_name: str,
    request: Request | None = None,
) -> User:
    user.name = display_name
    await write_audit_log(db, event_type="auth.profile.updated", actor_id=user.id, request=request)
    return user


async def change_password(
    db: AsyncSession,
    *,
    user: User,
    current_password: str,
    new_password: str,
    current_session_id: bytes,
    request: Request | None = None,
) -> None:
    if not user.password_hash or not verify_password(current_password, user.password_hash):
        raise InvalidCredentialsError("Current password is incorrect.")

    user.password_hash = hash_password(new_password)
    # Revoke other sessions; keep the current one (TDD §11.2 / screen inventory §3.11).
    await session_helpers.delete_sessions_for_user(
        db, user.id, except_session_id=current_session_id
    )
    await write_audit_log(db, event_type="auth.password_changed", actor_id=user.id, request=request)


async def delete_account(
    db: AsyncSession,
    *,
    user: User,
    password: str,
    request: Request | None = None,
) -> None:
    """Self-deletion via in-place anonymization (ADR 065, TDD §11.7)."""
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Password is incorrect.")

    from taskflow.db.models.task import Task

    user.email = None
    user.name = None
    user.password_hash = None
    user.deleted_at = datetime.now(UTC)

    await session_helpers.delete_sessions_for_user(db, user.id)
    await db.execute(update(Task).where(Task.assignee_id == user.id).values(assignee_id=None))

    await write_audit_log(db, event_type="account.deleted", actor_id=user.id, request=request)


# ──────────────────────────────────────────────────────────────────────────────
# Invitation acceptance (PRD §3.3)
# ──────────────────────────────────────────────────────────────────────────────


async def accept_invitation(
    db: AsyncSession,
    *,
    raw_token: str,
    password: str | None,
    display_name: str | None,
    request: Request | None = None,
) -> tuple[User, session_helpers.SessionTokens]:
    token_hash = hash_token(raw_token)
    invitation = await db.scalar(select(Invitation).where(Invitation.token_hash == token_hash))
    if invitation is None or invitation.accepted_at is not None:
        raise InvalidTokenError("Invitation is invalid or already accepted.")
    if invitation.expires_at <= datetime.now(UTC):
        raise InvitationExpiredError("Invitation has expired.")

    # Existing user case: the email belongs to a live user in any workspace.
    existing = await db.scalar(
        select(User).where(User.email.ilike(invitation.email), User.deleted_at.is_(None))
    )
    if existing is not None:
        # Adding to a workspace == updating the user's workspace_id and role per the invitation.
        # PRD §4.1: one workspace per user. So we move them.
        existing.workspace_id = invitation.workspace_id
        existing.role = invitation.role
        invitation.accepted_at = datetime.now(UTC)

        tokens = await session_helpers.create_session(
            db,
            user_id=existing.id,
            ip=_client_ip(request),
            user_agent=_user_agent(request),
        )
        await write_audit_log(
            db,
            event_type="workspace.invitation.accepted",
            actor_id=existing.id,
            target_id=invitation.id,
            request=request,
        )
        return existing, tokens

    # New-user case: password + display_name required.
    if not password or not display_name:
        raise InvalidTokenError(
            "Display name and password are required to create a new account.",
            code="ACCOUNT_FIELDS_REQUIRED",
        )

    user = User(
        workspace_id=invitation.workspace_id,
        email=invitation.email,
        name=display_name,
        role=invitation.role,
        password_hash=hash_password(password),
    )
    db.add(user)
    invitation.accepted_at = datetime.now(UTC)
    await db.flush()

    tokens = await session_helpers.create_session(
        db,
        user_id=user.id,
        ip=_client_ip(request),
        user_agent=_user_agent(request),
    )
    await write_audit_log(
        db,
        event_type="workspace.invitation.accepted",
        actor_id=user.id,
        target_id=invitation.id,
        request=request,
    )
    return user, tokens


# Re-export common errors so endpoint files can import from one place.
__all__ = [
    "ConflictError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "InvitationExpiredError",
    "NotFoundError",
    "accept_invitation",
    "change_password",
    "confirm_password_reset",
    "delete_account",
    "login",
    "logout",
    "request_password_reset",
    "signup",
    "update_profile",
]
