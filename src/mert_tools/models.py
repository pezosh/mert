from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NoteHit(BaseModel):
    path: str
    title: str
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)


class NoteSearchResult(BaseModel):
    query: str
    count: int
    hits: list[NoteHit]


class TaskRecord(BaseModel):
    id: str
    title: str
    due_at: datetime | None = None
    status: Literal["open", "done"] = "open"
    created_at: datetime


class VisionObservation(BaseModel):
    label: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)


class VisionResult(BaseModel):
    summary: str
    observations: list[VisionObservation]
    warnings: list[str] = []
