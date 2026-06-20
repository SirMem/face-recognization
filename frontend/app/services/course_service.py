"""CourseService — 课程 CRUD + 班级查询（给其他模块用）。"""
from __future__ import annotations

from app.services.api_client import ApiClient, ApiResult
from app.core.store import store


class CourseService(ApiClient):

    def list(self) -> ApiResult:
        result = self._get("/courses")
        if result.ok:
            store.update_courses(result.data)
        return result

    def create(self, name: str, teacher: str = "", schedule: str = "") -> ApiResult:
        return self._post("/courses", {"name": name, "teacher": teacher, "schedule": schedule})

    def delete(self, course_id: int) -> ApiResult:
        return self._delete(f"/courses/{course_id}")


course_service = CourseService()
