"""SQLAlchemy models — import all so Flask-Migrate discovers them."""

from app.models.user import User
from app.models.class_ import Class
from app.models.student import Student
from app.models.course import Course
from app.models.attendance import Attendance

__all__ = ["User", "Class", "Student", "Course", "Attendance"]
