"""Attendance — 考勤记录 + 统计模型。"""
from __future__ import annotations

from pydantic import BaseModel


class AttendanceRecord(BaseModel):
    id: int
    student_id: int
    student_name: str | None = None
    student_no: str | None = None
    course_id: int | None = None
    course_name: str | None = None
    checkin_time: str | None = None
    status: str = "present"
    confidence: float = 0.0
    created_at: str | None = None


class AttendanceStats(BaseModel):
    total: int = 0
    present: int = 0
    late: int = 0
    absent: int = 0
    rate: float = 0.0
    date_from: str | None = None
    date_to: str | None = None
