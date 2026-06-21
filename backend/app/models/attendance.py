from app.extensions import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
    checkin_time = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    status = db.Column(db.String(16), nullable=False, default="present")  # present / late / absent
    confidence = db.Column(db.Float, default=0.0)  # recognition confidence
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    # relationships (lazy for performance)
    student = db.relationship("Student", lazy="joined")
    course = db.relationship("Course", lazy="joined")

    @property
    def student_name(self):
        return self.student.name if self.student else None

    @property
    def student_no(self):
        return self.student.student_no if self.student else None

    @property
    def course_name(self):
        return self.course.name if self.course else None

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "student_no": self.student.student_no if self.student else None,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else None,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "status": self.status,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
