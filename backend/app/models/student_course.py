"""StudentCourse — 学生与课程的多对多关联。"""
from app.extensions import db


class StudentCourse(db.Model):
    __tablename__ = "student_course"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("student_id", "course_id", name="uq_student_course"),)
