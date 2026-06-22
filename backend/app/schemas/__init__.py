"""Marshmallow schemas for request/response validation."""

from app.schemas.auth import LoginSchema, TokenRefreshSchema
from app.schemas.face import RegisterFaceSchema, RecognizeFaceSchema, FaceResultSchema
from app.schemas.manage import (
    ClassSchema, ClassQuerySchema, CourseSchema,
    StudentSchema, StudentQuerySchema, StudentCoursesSchema,
)
from app.schemas.attendance import AttendanceRecordSchema, AttendanceQuerySchema, AttendanceStatsSchema, DashboardStatsSchema

__all__ = [
    "LoginSchema", "TokenRefreshSchema",
    "RegisterFaceSchema", "RecognizeFaceSchema", "FaceResultSchema",
    "ClassSchema", "ClassQuerySchema", "CourseSchema",
    "StudentSchema", "StudentQuerySchema", "StudentCoursesSchema",
    "AttendanceRecordSchema", "AttendanceQuerySchema", "AttendanceStatsSchema", "DashboardStatsSchema",
]
