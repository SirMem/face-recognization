"""Student — 学生模型。"""
from __future__ import annotations

from pydantic import BaseModel


class Student(BaseModel):
    id: int
    student_no: str
    name: str
    gender: str = ""
    class_id: int | None = None
    has_face: bool = False
    created_at: str | None = None
    updated_at: str | None = None
