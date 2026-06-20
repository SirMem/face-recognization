"""Course + Class — 课程与班级模型。"""
from __future__ import annotations

from pydantic import BaseModel


class Course(BaseModel):
    id: int
    name: str
    teacher: str = ""
    schedule: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class Class(BaseModel):
    id: int
    name: str
    grade: str = ""
    created_at: str | None = None
    updated_at: str | None = None
