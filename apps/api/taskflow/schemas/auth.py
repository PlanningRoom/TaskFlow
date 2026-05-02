"""Auth-endpoint Pydantic DTOs (TDD §11, ADR 042)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from taskflow.schemas.users import CurrentUser

PasswordField = Annotated[str, Field(min_length=8, max_length=128)]
NameField = Annotated[str, Field(min_length=1, max_length=120)]


class SignupRequest(BaseModel):
    email: EmailStr
    password: PasswordField
    display_name: NameField
    workspace_name: NameField


class SignupResponse(BaseModel):
    user: CurrentUser


class LoginRequest(BaseModel):
    email: EmailStr
    # No length constraint here — login authenticates against the stored hash;
    # rejecting short inputs at validation time would make wrong-password 422 instead of 401.
    password: str


class LoginResponse(BaseModel):
    user: CurrentUser


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: Annotated[str, Field(min_length=16, max_length=200)]
    new_password: PasswordField


class ChangePasswordRequest(BaseModel):
    current_password: PasswordField
    new_password: PasswordField


class UpdateProfileRequest(BaseModel):
    display_name: NameField


class DeleteAccountRequest(BaseModel):
    password: PasswordField


class AcceptInvitationRequest(BaseModel):
    token: Annotated[str, Field(min_length=16, max_length=200)]
    # Required only when the invited email has no existing account.
    password: PasswordField | None = None
    display_name: NameField | None = None


class AcceptInvitationResponse(BaseModel):
    user: CurrentUser


class OkResponse(BaseModel):
    ok: bool = True
