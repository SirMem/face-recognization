"""User — 管理员模型。"""
from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    role: str
    created_at: str | None = None
