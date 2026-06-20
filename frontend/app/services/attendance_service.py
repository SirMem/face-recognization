"""AttendanceService — 考勤明细 + 统计。"""
from __future__ import annotations

from app.services.api_client import ApiClient, ApiResult
from app.core.store import store


class AttendanceService(ApiClient):

    def recognize(self, image_path: str, course_id: int = None) -> ApiResult:
        data = {}
        if course_id:
            data["course_id"] = str(course_id)
        return self._post_file("/face/recognize", data, image_path)

    def list_records(self, params: dict = None) -> ApiResult:
        return self._get("/attendance", params)

    def get_statistics(self, params: dict = None) -> ApiResult:
        result = self._get("/attendance/statistics", params)
        if result.ok:
            store.update_stats(result.data)
        return result


attendance_service = AttendanceService()
