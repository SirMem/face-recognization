"""Marshmallow schemas for attendance queries."""

from marshmallow import Schema, fields


class AttendanceRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int()
    student_name = fields.Str(dump_only=True)
    course_id = fields.Int(allow_none=True)
    course_name = fields.Str(dump_only=True)
    checkin_time = fields.DateTime()
    status = fields.Str()
    confidence = fields.Float()
    created_at = fields.DateTime(dump_only=True)


class AttendanceQuerySchema(Schema):
    course_id = fields.Int(required=False)
    class_id = fields.Int(required=False)
    student_id = fields.Int(required=False)
    status = fields.Str(required=False)
    date_from = fields.Date(required=False, metadata={"description": "起始日期 YYYY-MM-DD"})
    date_to = fields.Date(required=False, metadata={"description": "结束日期 YYYY-MM-DD"})
    page = fields.Int(load_default=1, required=False)
    per_page = fields.Int(load_default=20, required=False)


class PaginatedAttendanceSchema(Schema):
    records = fields.List(fields.Raw())
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()


class AttendanceStatsSchema(Schema):
    total = fields.Int()
    present = fields.Int()
    late = fields.Int()
    absent = fields.Int()
    rate = fields.Float()


class DailySeriesItem(Schema):
    date = fields.Str()
    present = fields.Int()
    late = fields.Int()
    absent = fields.Int()


class DashboardStatsSchema(Schema):
    total_expected = fields.Int()
    present = fields.Int()
    late = fields.Int()
    absent = fields.Int()
    rate = fields.Float()
    present_trend = fields.Str(allow_none=True)
    absent_trend = fields.Str(allow_none=True)
    daily_series = fields.List(fields.Nested(DailySeriesItem))
