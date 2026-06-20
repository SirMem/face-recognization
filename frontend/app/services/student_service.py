"""StudentService — 学生 CRUD + 人脸注册。"""
from __future__ import annotations

from app.services.api_client import ApiClient, ApiResult


class StudentService(ApiClient):

    def list(self, params: dict = None) -> ApiResult:
        return self._get("/students", params)

    def create(self, student_no: str, name: str, gender: str = "", class_id: int = None) -> ApiResult:
        return self._post("/students", {
            "student_no": student_no, "name": name,
            "gender": gender, "class_id": class_id,
        })

    def delete(self, student_id: int) -> ApiResult:
        return self._delete(f"/students/{student_id}")

    def register_face(self, student_id: int, image_path: str) -> ApiResult:
        return self._post_file("/face/register", {"student_id": str(student_id)}, image_path)

    def list_registered_faces(self) -> ApiResult:
        return self._get("/face/students")

    def list_classes(self) -> ApiResult:
        return self._get("/classes")

    def create_class(self, name: str, grade: str = "") -> ApiResult:
        return self._post("/classes", {"name": name, "grade": grade})

    def delete_class(self, class_id: int) -> ApiResult:
        return self._delete(f"/classes/{class_id}")


student_service = StudentService()
