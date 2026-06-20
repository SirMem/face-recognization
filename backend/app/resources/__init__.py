"""Flask-Smorest Blueprints (resources)."""

from app.resources.auth import blp as auth_blp
from app.resources.face import blp as face_blp
from app.resources.manage import blp as manage_blp
from app.resources.attendance import blp as attendance_blp

__all__ = ["auth_blp", "face_blp", "manage_blp", "attendance_blp"]
