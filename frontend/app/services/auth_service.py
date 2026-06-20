"""AuthService — 管理员认证。"""
from __future__ import annotations

from app.core.store import store
from app.services.api_client import ApiClient, ApiResult


class AuthService(ApiClient):

    def login(self, username: str, password: str) -> ApiResult:
        result = self._post("/auth/login", {"username": username, "password": password})
        if result.ok:
            data = result.data
            store.token = data["access_token"]
            store.user = data["user"]
            self.set_token(data["access_token"])
        return result

    def refresh_token(self) -> ApiResult:
        result = self._post("/auth/refresh")
        if result.ok:
            new_token = result.data["access_token"]
            store.token = new_token
            self.set_token(new_token)
        return result

    def logout(self):
        store.token = None
        store.user = None
        self.set_token(None)


auth_service = AuthService()
