"""Marshmallow schemas for class / course / student CRUD."""

from marshmallow import Schema, fields, validate


# ── Class ──────────────────────────────────────────────────────────────

class ClassSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    grade = fields.Str(load_default="", validate=validate.Length(max=32))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ClassQuerySchema(Schema):
    grade = fields.Str(required=False)


# ── Course ─────────────────────────────────────────────────────────────

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    teacher = fields.Str(load_default="", validate=validate.Length(max=64))
    schedule = fields.Str(load_default="", validate=validate.Length(max=256))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ── Student ────────────────────────────────────────────────────────────

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    student_no = fields.Str(required=True, validate=validate.Length(min=1, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    gender = fields.Str(load_default="", validate=validate.Length(max=8))
    class_id = fields.Int(load_default=None, allow_none=True)
    has_face = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StudentQuerySchema(Schema):
    class_id = fields.Int(required=False)
    has_face = fields.Bool(required=False)


# ── Student-Course ──────────────────────────────────────────────────────

class StudentCoursesSchema(Schema):
    course_ids = fields.List(fields.Int(), required=True)
