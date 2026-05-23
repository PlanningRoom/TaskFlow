"""Auth endpoints (TDD §9.4 / §11)."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response

from taskflow.auth import sessions as session_helpers
from taskflow.auth.dependencies import (
    DbDep,
    SessionDep,
    UserDep,
    verify_csrf,
)
from taskflow.db.models.user import User
from taskflow.rate_limit import email_key_factory, ip_key, limiter
from taskflow.schemas.auth import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    ChangePasswordRequest,
    DeleteAccountRequest,
    LoginRequest,
    LoginResponse,
    OkResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    SignupRequest,
    SignupResponse,
    UpdateProfileRequest,
)
from taskflow.schemas.users import CurrentUser, current_user_dto
from taskflow.services import auth as auth_service
from taskflow.services.emails import send_password_reset_email
from taskflow.settings import settings

_login_email_key = email_key_factory("email")
_reset_email_key = email_key_factory("email")

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookies(response: Response, tokens: session_helpers.SessionTokens) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        tokens.session_token,
        max_age=settings.session_absolute_ttl_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        tokens.csrf_token,
        max_age=settings.session_absolute_ttl_days * 86400,
        httponly=False,  # readable by JS so the SPA can echo it (ADR 051)
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookies(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")


def _to_current_user(user: User) -> CurrentUser:
    return current_user_dto(
        user_id=user.id,
        email=user.email or "",
        name=user.name,
        role=user.role,
        workspace_id=user.workspace_id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Sign-up / login / logout
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/signup", response_model=SignupResponse)
@limiter.limit(settings.rate_limit_signup_per_ip, key_func=ip_key)
async def signup(
    body: SignupRequest, request: Request, response: Response, db: DbDep
) -> SignupResponse:
    user, tokens = await auth_service.signup(
        db,
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        workspace_name=body.workspace_name,
        request=request,
    )
    await db.commit()
    _set_session_cookies(response, tokens)
    return SignupResponse(user=_to_current_user(user))


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_login_per_ip, key_func=ip_key)
@limiter.limit(settings.rate_limit_login_per_email, key_func=_login_email_key)
async def login(
    body: LoginRequest, request: Request, response: Response, db: DbDep
) -> LoginResponse:
    user, tokens = await auth_service.login(
        db, email=body.email, password=body.password, request=request
    )
    await db.commit()
    _set_session_cookies(response, tokens)
    return LoginResponse(user=_to_current_user(user))


@router.post("/logout", response_model=OkResponse, dependencies=[Depends(verify_csrf)])
async def logout(
    request: Request,
    response: Response,
    db: DbDep,
    session: SessionDep,
    user: UserDep,
) -> OkResponse:
    raw = request.cookies.get(settings.session_cookie_name)
    if raw:
        await auth_service.logout(db, raw_session_token=raw, user_id=user.id, request=request)
    await db.commit()
    _clear_session_cookies(response)
    return OkResponse()


# ──────────────────────────────────────────────────────────────────────────────
# Password reset
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/password-reset/request", response_model=OkResponse)
@limiter.limit(settings.rate_limit_password_reset_per_ip, key_func=ip_key)
@limiter.limit(settings.rate_limit_password_reset_per_email, key_func=_reset_email_key)
async def password_reset_request(
    body: PasswordResetRequest,
    request: Request,
    background: BackgroundTasks,
    db: DbDep,
) -> OkResponse:
    user, raw = await auth_service.request_password_reset(db, email=body.email, request=request)
    await db.commit()
    if user is not None and raw is not None:
        background.add_task(send_password_reset_email, to=user.email or "", raw_token=raw)
    return OkResponse()


@router.post("/password-reset/confirm", response_model=OkResponse)
async def password_reset_confirm(
    body: PasswordResetConfirm, request: Request, db: DbDep
) -> OkResponse:
    await auth_service.confirm_password_reset(
        db, raw_token=body.token, new_password=body.new_password, request=request
    )
    await db.commit()
    return OkResponse()


# ──────────────────────────────────────────────────────────────────────────────
# /auth/me
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/me", response_model=CurrentUser)
async def read_me(user: UserDep) -> CurrentUser:
    return _to_current_user(user)


@router.patch("/me", response_model=CurrentUser, dependencies=[Depends(verify_csrf)])
async def update_me(
    body: UpdateProfileRequest, request: Request, db: DbDep, user: UserDep
) -> CurrentUser:
    await auth_service.update_profile(
        db, user=user, display_name=body.display_name, request=request
    )
    await db.commit()
    return _to_current_user(user)


@router.post(
    "/change-password",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf)],
)
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    session: SessionDep,
) -> OkResponse:
    await auth_service.change_password(
        db,
        user=user,
        current_password=body.current_password,
        new_password=body.new_password,
        current_session_id=session.id,
        request=request,
    )
    await db.commit()
    return OkResponse()


@router.delete(
    "/me",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf)],
)
async def delete_me(
    body: DeleteAccountRequest,
    request: Request,
    response: Response,
    db: DbDep,
    user: UserDep,
) -> OkResponse:
    await auth_service.delete_account(db, user=user, password=body.password, request=request)
    await db.commit()
    _clear_session_cookies(response)
    return OkResponse()


# ──────────────────────────────────────────────────────────────────────────────
# Invitation acceptance
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/accept-invitation", response_model=AcceptInvitationResponse)
async def accept_invitation(
    body: AcceptInvitationRequest, request: Request, response: Response, db: DbDep
) -> AcceptInvitationResponse:
    user, tokens = await auth_service.accept_invitation(
        db,
        raw_token=body.token,
        password=body.password,
        display_name=body.display_name,
        request=request,
    )
    await db.commit()
    _set_session_cookies(response, tokens)
    return AcceptInvitationResponse(user=_to_current_user(user))
