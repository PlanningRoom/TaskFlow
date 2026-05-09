"""Label DTOs (PRD §7, DRD §2.9, screen inventory §3.10)."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# DRD §2.9 — eight palette colors. Stored as slugs; matches the migration
# `LABEL_COLORS` list used in the labels.color CHECK constraint.
LabelColor = Literal["blue", "green", "red", "purple", "amber", "pink", "cyan", "orange"]

NameField = Annotated[str, Field(min_length=1, max_length=64)]


class LabelDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color: LabelColor


class ListLabelsResponse(BaseModel):
    labels: list[LabelDTO]


class CreateLabelRequest(BaseModel):
    name: NameField
    color: LabelColor


class UpdateLabelRequest(BaseModel):
    name: NameField | None = None
    color: LabelColor | None = None
