from app.extensions import db


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_no = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(8), default="")
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=True)

    # Face data
    face_image_path = db.Column(db.String(512), default="")
    face_embedding = db.Column(db.Text, default="")  # JSON-serialized 128-dim array

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def has_face(self) -> bool:
        return bool(self.face_embedding)

    def to_dict(self):
        return {
            "id": self.id,
            "student_no": self.student_no,
            "name": self.name,
            "gender": self.gender,
            "class_id": self.class_id,
            "has_face": bool(self.face_embedding),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
