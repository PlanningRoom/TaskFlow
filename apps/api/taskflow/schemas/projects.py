"""Project DTOs (PRD §5, screen inventory §5.1, §5.2)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from taskflow.schemas.users import UserSummary

NameField = Annotated[str, Field(min_length=1, max_length=120)]
DescriptionField = Annotated[str, Field(max_length=2000)]


class ProjectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    color: str | None
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime


class ListProjectsResponse(BaseModel):
    projects: list[ProjectDTO]


class CreateProjectRequest(BaseModel):
    name: NameField
    description: DescriptionField | None = None
    color: str | None = None


class UpdateProjectRequest(BaseModel):
    name: NameField | None = None
    description: DescriptionField | None = None
    color: str | None = None


class ProjectMemberDTO(BaseModel):
    user: UserSummary


class ListProjectAccessResponse(BaseModel):
    members: list[ProjectMemberDTO]


class GrantProjectAccessRequest(BaseModel):
    user_id: UUID


class GrantProjectAccessResponse(BaseModel):
    member: ProjectMemberDTO
