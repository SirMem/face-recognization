"""Attendance resources: query records & statistics."""

from datetime import datetime, date, timedelta

from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.models import Attendance, Student
from app.schemas import AttendanceQuerySchema, AttendanceRecordSchema, AttendanceStatsSchema, DashboardStatsSchema
from app.schemas.attendance import PaginatedAttendanceSchema

blp = Blueprint("attendance", __name__, url_prefix="/attendance", description="考勤记录查询与统计")


@blp.route("", methods=["GET"])
@jwt_required()
@blp.arguments(AttendanceQuerySchema, location="query")
@blp.response(200, PaginatedAttendanceSchema)
def list_attendance(args):
    """考勤记录列表。支持按课程/班级/学生/状态/日期范围筛选 + 分页。"""
    q = Attendance.query

    if args.get("course_id"):
        q = q.filter_by(course_id=args["course_id"])

    if args.get("student_id"):
        q = q.filter_by(student_id=args["student_id"])

    if args.get("status"):
        q = q.filter(Attendance.status == args["status"])

    if args.get("class_id"):
        q = q.join(Student, Attendance.student_id == Student.id).filter(Student.class_id == args["class_id"])

    if args.get("date_from"):
        dt_from = datetime.combine(args["date_from"], datetime.min.time())
        q = q.filter(Attendance.checkin_time >= dt_from)

    if args.get("date_to"):
        dt_to = datetime.combine(args["date_to"], datetime.max.time())
        q = q.filter(Attendance.checkin_time <= dt_to)

    # Pagination
    page = args.get("page", 1)
    per_page = args.get("per_page", 20)
    total = q.count()
    records = q.order_by(Attendance.checkin_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False,
    )

    return {
        "records": [r.to_dict() for r in records.items],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


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

    if args.get("status"):
        q = q.filter(Attendance.status == args["status"])

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


@blp.route("/dashboard", methods=["GET"])
@jwt_required()
@blp.response(200, DashboardStatsSchema)
def dashboard_stats():
    """Dashboard 面板数据：今日统计 + 趋势对比 + 近 7 天每日分布。"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    days = [today - timedelta(days=i) for i in range(7)]

    # ── Helper: count by status for a given date ──
    def _stats_for_day(d: date) -> dict:
        dt_from = datetime.combine(d, datetime.min.time())
        dt_to = datetime.combine(d, datetime.max.time())
        q = Attendance.query.filter(
            Attendance.checkin_time >= dt_from,
            Attendance.checkin_time <= dt_to,
        )
        total = q.count()
        present = q.filter(Attendance.status == "present").count()
        late = q.filter(Attendance.status == "late").count()
        absent = q.filter(Attendance.status == "absent").count()
        return {"total": total, "present": present, "late": late, "absent": absent}

    # ── Today's stats ──
    today_stats = _stats_for_day(today)

    # ── Trend (today vs yesterday) ──
    yesterday_stats = _stats_for_day(yesterday)

    def _trend_str(current: int, previous: int) -> str | None:
        if previous == 0:
            return None
        pct = round((current - previous) / previous * 100)
        if pct > 0:
            return f"+{pct}%"
        if pct < 0:
            return f"{pct}%"
        return "0%"

    present_trend = _trend_str(today_stats["present"], yesterday_stats["present"])
    absent_trend = _trend_str(today_stats["absent"], yesterday_stats["absent"])

    # ── Daily series (last 7 days) ──
    daily_series = []
    for d in reversed(days):
        s = _stats_for_day(d)
        daily_series.append({
            "date": str(d),
            "present": s["present"],
            "late": s["late"],
            "absent": s["absent"],
        })

    # ── Total expected = total attendance today (present + late + absent) ──
    total_expected = today_stats["total"]

    total_all = today_stats["total"]
    rate = round(today_stats["present"] / total_all * 100, 2) if total_all > 0 else 0.0

    return {
        "total_expected": total_expected,
        "present": today_stats["present"],
        "late": today_stats["late"],
        "absent": today_stats["absent"],
        "rate": rate,
        "present_trend": present_trend,
        "absent_trend": absent_trend,
        "daily_series": daily_series,
    }
