"""Attendance resources: query records & statistics."""

from datetime import datetime, timedelta

from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from sqlalchemy import func

from app.extensions import db
from app.models import Attendance, Course, Student
from app.schemas import AttendanceQuerySchema, AttendanceRecordSchema, AttendanceStatsSchema

blp = Blueprint("attendance", __name__, url_prefix="/attendance", description="考勤记录查询与统计")


@blp.route("", methods=["GET"])
@jwt_required()
@blp.arguments(AttendanceQuerySchema, location="query")
@blp.response(200, AttendanceRecordSchema(many=True))
def list_attendance(args):
    """考勤记录列表。支持按课程/班级/学生/日期范围筛选。"""
    q = Attendance.query

    if args.get("course_id"):
        q = q.filter_by(course_id=args["course_id"])

    if args.get("student_id"):
        q = q.filter_by(student_id=args["student_id"])

    if args.get("class_id"):
        # Join through student
        q = q.join(Student, Attendance.student_id == Student.id).filter(Student.class_id == args["class_id"])

    if args.get("date_from"):
        dt_from = datetime.combine(args["date_from"], datetime.min.time())
        q = q.filter(Attendance.checkin_time >= dt_from)

    if args.get("date_to"):
        dt_to = datetime.combine(args["date_to"], datetime.max.time())
        q = q.filter(Attendance.checkin_time <= dt_to)

    return q.order_by(Attendance.checkin_time.desc()).all()


@blp.route("/statistics", methods=["GET"])
@jwt_required()
@blp.arguments(AttendanceQuerySchema, location="query")
@blp.response(200)
def attendance_statistics(args):
    """考勤统计。返回出勤率汇总。

    无日期参数时，默认统计最近 7 天。
    """
    q = Attendance.query

    if args.get("course_id"):
        q = q.filter_by(course_id=args["course_id"])

    if args.get("class_id"):
        q = q.join(Student, Attendance.student_id == Student.id).filter(Student.class_id == args["class_id"])

    if args.get("student_id"):
        q = q.filter_by(student_id=args["student_id"])

    # Default: last 7 days
    date_from = args.get("date_from")
    if not date_from:
        date_from = (datetime.now() - timedelta(days=7)).date()
        dt_from = datetime.combine(date_from, datetime.min.time())
        q = q.filter(Attendance.checkin_time >= dt_from)
    else:
        dt_from = datetime.combine(date_from, datetime.min.time())
        q = q.filter(Attendance.checkin_time >= dt_from)

    if args.get("date_to"):
        dt_to = datetime.combine(args["date_to"], datetime.max.time())
        q = q.filter(Attendance.checkin_time <= dt_to)

    total = q.count()
    present = q.filter(Attendance.status == "present").count()
    late = q.filter(Attendance.status == "late").count()
    absent = q.filter(Attendance.status == "absent").count()
    rate = round(present / total * 100, 2) if total > 0 else 0.0

    return {
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "rate": rate,
        "date_from": str(date_from),
        "date_to": str(args.get("date_to", "")) if args.get("date_to") else str(datetime.now().date()),
    }
