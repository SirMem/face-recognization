"""ApiClient — HTTP 基础封装。

处理 requests session、Token 注入、错误归一化。
各领域 Service 通过继承此类的 _get/_post/_put/_delete 发起请求。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class ApiResult:
    ok: bool
    data: Any = None
    message: str = ""
    code: int = 0


class ApiClient:
    """线程安全的 HTTP 客户端（需在 QThread 中调用以不阻塞 UI）。"""

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ── Token 管理 ─────────────────────────────────────────────────────

    @property
    def _headers(self) -> dict:
        return dict(self._session.headers)

    def set_token(self, token: str | None):
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"
        else:
            self._session.headers.pop("Authorization", None)

    # ── HTTP 方法 ──────────────────────────────────────────────────────

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", 10)
        return self._session.request(method, url, **kwargs)

    def _get(self, path: str, params: dict = None) -> ApiResult:
        return self._handle(self._request("GET", path, params=params))

    def _post(self, path: str, json: dict = None) -> ApiResult:
        return self._handle(self._request("POST", path, json=json))

    def _put(self, path: str, json: dict = None) -> ApiResult:
        return self._handle(self._request("PUT", path, json=json))

    def _delete(self, path: str) -> ApiResult:
        return self._handle(self._request("DELETE", path))

    def _post_file(self, path: str, data: dict, file_path: str) -> ApiResult:
        """上传文件的 POST 请求。"""
        try:
            with open(file_path, "rb") as f:
                resp = self._session.post(
                    f"{self.base_url}{path}",
                    data=data,
                    files={"image": ("face.jpg", f, "image/jpeg")},
                    timeout=30,
                )
            return self._handle(resp)
        except Exception as e:
            return ApiResult(ok=False, message=str(e))

    # ── 响应处理 ───────────────────────────────────────────────────────

    @staticmethod
    def _handle(resp: requests.Response) -> ApiResult:
        try:
            if resp.status_code in (200, 201):
                data = resp.json() if resp.content else None
                return ApiResult(ok=True, data=data, code=resp.status_code)
            if resp.status_code == 204:
                return ApiResult(ok=True, data=None, code=204)
            msg = resp.json().get("message", "请求失败") if resp.content else "请求失败"
            return ApiResult(ok=False, message=msg, code=resp.status_code)
        except requests.ConnectionError:
            return ApiResult(ok=False, message="无法连接到服务器，请确保后端已启动")
        except Exception as e:
            return ApiResult(ok=False, message=str(e))
