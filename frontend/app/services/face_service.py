"""FaceService — 人脸识别打卡 API。"""
from __future__ import annotations

from app.services.api_client import ApiClient, ApiResult


class FaceService(ApiClient):
    """人脸识别相关接口。"""

    def recognize(self, image_data: bytes, course_id: int = None) -> ApiResult:
        """上传人脸照片进行识别打卡。

        POST /face/recognize
        Args:
            image_data: 图片字节流（JPEG/PNG）。
            course_id:   可选课程 ID，打卡记录会关联该课程。
        """
        data = {}
        if course_id is not None:
            data["course_id"] = course_id
        try:
            resp = self._request(
                "POST", "/face/recognize", data=data,
                files={"image": ("face.jpg", image_data, "image/jpeg")},
                timeout=30,
            )
            return self._handle(resp)
        except Exception as e:
            return ApiResult(ok=False, message=str(e))


face_service = FaceService()
