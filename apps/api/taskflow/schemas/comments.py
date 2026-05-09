"""Comment DTOs (PRD §11, screen inventory §4.1)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from taskflow.schemas.users import UserSummary

BodyField = Annotated[str, Field(min_length=1, max_length=10_000)]


class CommentDTO(BaseModel):
    id: UUID
    body: str
    author: UserSummary | None
    mentions: list[UserSummary]
    created_at: datetime
    updated_at: datetime


class ListCommentsResponse(BaseModel):
    comments: list[CommentDTO]


class CreateCommentRequest(BaseModel):
    body: BodyField


class UpdateCommentRequest(BaseModel):
    body: BodyField
