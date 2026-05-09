"""Workspace DTOs (PRD §4.1, screen inventory §3.8)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

NameField = Annotated[str, Field(min_length=1, max_length=120)]


class WorkspaceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime


class UpdateWorkspaceRequest(BaseModel):
    name: NameField
