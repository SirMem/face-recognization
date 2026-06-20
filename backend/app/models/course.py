from app.extensions import db


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    teacher = db.Column(db.String(64), default="")
    schedule = db.Column(db.String(256), default="")  # e.g. "周一 10:00-12:00"
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "teacher": self.teacher,
            "schedule": self.schedule,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
