"""Marshmallow schemas for face endpoints."""

from marshmallow import Schema, fields


class RegisterFaceSchema(Schema):
    student_id = fields.Int(required=True, metadata={"description": "学生ID"})
    image = fields.Raw(required=True, metadata={"type": "string", "format": "binary", "description": "人脸照片"})


class RecognizeFaceSchema(Schema):
    image = fields.Raw(required=True, metadata={"type": "string", "format": "binary", "description": "人脸照片"})
    course_id = fields.Int(required=False, load_default=None, metadata={"description": "课程ID（可选）"})


class FaceResultSchema(Schema):
    student_id = fields.Int()
    student_name = fields.Str()
    student_no = fields.Str()
    distance = fields.Float()
    is_match = fields.Bool()
