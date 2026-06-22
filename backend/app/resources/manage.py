"""Management resources: CRUD for classes, courses, students."""

from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from loguru import logger

from app.extensions import db
from app.models import Class, Course, Student, StudentCourse
from app.schemas import (
    ClassQuerySchema, ClassSchema,
    CourseSchema,
    StudentQuerySchema, StudentSchema,
    StudentCoursesSchema,
)
from app.decorators import role_required

blp = Blueprint("manage", __name__, url_prefix="", description="班级/课程/学生管理")


# ═════════════════════════════════════════════════════════════════════
#  Class
# ═════════════════════════════════════════════════════════════════════

@blp.route("/classes", methods=["GET"])
@jwt_required()
@blp.arguments(ClassQuerySchema, location="query")
@blp.response(200, ClassSchema(many=True))
def list_classes(args):
    """班级列表。支持按年级筛选。"""
    q = Class.query
    if args.get("grade"):
        q = q.filter_by(grade=args["grade"])
    return q.order_by(Class.id).all()


@blp.route("/classes", methods=["POST"])
@jwt_required()
@role_required("admin")
@blp.arguments(ClassSchema)
@blp.response(201, ClassSchema)
def create_class(data):
    """新增班级。"""
    cls = Class(**data)
    db.session.add(cls)
    db.session.commit()
    logger.info("Class created: {}", data["name"])
    return cls


@blp.route("/classes/<int:class_id>", methods=["GET"])
@jwt_required()
@blp.response(200, ClassSchema)
def get_class(class_id):
    """班级详情。"""
    cls = db.session.get(Class, class_id)
    if not cls:
        abort(404, message="班级不存在")
    return cls


@blp.route("/classes/<int:class_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
@blp.arguments(ClassSchema(partial=True))
@blp.response(200, ClassSchema)
def update_class(data, class_id):
    """修改班级信息。"""
    cls = db.session.get(Class, class_id)
    if not cls:
        abort(404, message="班级不存在")
    for k, v in data.items():
        setattr(cls, k, v)
    db.session.commit()
    logger.info("Class #{} updated", class_id)
    return cls


@blp.route("/classes/<int:class_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
@blp.response(204)
def delete_class(class_id):
    """删除班级（如果班内有学生则拒绝）。"""
    cls = db.session.get(Class, class_id)
    if not cls:
        abort(404, message="班级不存在")
    if cls.students.count() > 0:
        abort(409, message="该班级下还有学生，无法删除")
    db.session.delete(cls)
    db.session.commit()
    logger.info("Class #{} deleted", class_id)


# ═════════════════════════════════════════════════════════════════════
#  Course
# ═════════════════════════════════════════════════════════════════════

@blp.route("/courses", methods=["GET"])
@jwt_required()
@blp.response(200, CourseSchema(many=True))
def list_courses():
    """课程列表。"""
    return Course.query.order_by(Course.id).all()


@blp.route("/courses", methods=["POST"])
@jwt_required()
@role_required("admin")
@blp.arguments(CourseSchema)
@blp.response(201, CourseSchema)
def create_course(data):
    """新增课程。"""
    course = Course(**data)
    db.session.add(course)
    db.session.commit()
    logger.info("Course created: {}", data["name"])
    return course


@blp.route("/courses/<int:course_id>", methods=["GET"])
@jwt_required()
@blp.response(200, CourseSchema)
def get_course(course_id):
    """课程详情。"""
    course = db.session.get(Course, course_id)
    if not course:
        abort(404, message="课程不存在")
    return course


@blp.route("/courses/<int:course_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
@blp.arguments(CourseSchema(partial=True))
@blp.response(200, CourseSchema)
def update_course(data, course_id):
    """修改课程信息。"""
    course = db.session.get(Course, course_id)
    if not course:
        abort(404, message="课程不存在")
    for k, v in data.items():
        setattr(course, k, v)
    db.session.commit()
    logger.info("Course #{} updated", course_id)
    return course


@blp.route("/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
@blp.response(204)
def delete_course(course_id):
    """删除课程（如果有考勤记录则拒绝）。"""
    course = db.session.get(Course, course_id)
    if not course:
        abort(404, message="课程不存在")
    from app.models import Attendance
    if Attendance.query.filter_by(course_id=course_id).first():
        abort(409, message="该课程已有考勤记录，无法删除")
    db.session.delete(course)
    db.session.commit()
    logger.info("Course #{} deleted", course_id)


# ═════════════════════════════════════════════════════════════════════
#  Student
# ═════════════════════════════════════════════════════════════════════

@blp.route("/students", methods=["GET"])
@jwt_required()
@blp.arguments(StudentQuerySchema, location="query")
@blp.response(200, StudentSchema(many=True))
def list_students(args):
    """学生列表。支持按班级/是否有注册人脸筛选。"""
    q = Student.query
    if args.get("class_id"):
        q = q.filter_by(class_id=args["class_id"])
    if args.get("has_face") is True:
        q = q.filter(Student.face_embedding != "")
    elif args.get("has_face") is False:
        q = q.filter(Student.face_embedding == "")
    return q.order_by(Student.id).all()


@blp.route("/students", methods=["POST"])
@jwt_required()
@role_required("admin")
@blp.arguments(StudentSchema)
@blp.response(201, StudentSchema)
def create_student(data):
    """新增学生。"""
    existing = Student.query.filter_by(student_no=data["student_no"]).first()
    if existing:
        abort(409, message=f"学号 '{data['student_no']}' 已存在")
    student = Student(**data)
    db.session.add(student)
    db.session.commit()
    logger.info("Student created: {} ({})", data["name"], data["student_no"])
    return student


@blp.route("/students/<int:student_id>", methods=["GET"])
@jwt_required()
@blp.response(200, StudentSchema)
def get_student(student_id):
    """学生详情。"""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404, message="学生不存在")
    return student


@blp.route("/students/<int:student_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
@blp.arguments(StudentSchema(partial=True))
@blp.response(200, StudentSchema)
def update_student(data, student_id):
    """修改学生信息。"""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404, message="学生不存在")
    # If student_no is being changed, check uniqueness
    if "student_no" in data and data["student_no"] != student.student_no:
        existing = Student.query.filter_by(student_no=data["student_no"]).first()
        if existing:
            abort(409, message=f"学号 '{data['student_no']}' 已被使用")
    for k, v in data.items():
        setattr(student, k, v)
    db.session.commit()
    logger.info("Student #{} updated", student_id)
    return student


@blp.route("/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
@blp.response(204)
def delete_student(student_id):
    """删除学生。"""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404, message="学生不存在")
    from app.models import Attendance
    Attendance.query.filter_by(student_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    logger.info("Student #{} deleted", student_id)


# ── Student-Course enrollment ──────────────────────────────────────────


@blp.route("/students/<int:student_id>/courses", methods=["GET"])
@jwt_required()
@blp.response(200)
def get_student_courses(student_id):
    """获取学生已选课程 ID 列表。"""
    rows = StudentCourse.query.filter_by(student_id=student_id).all()
    return {"course_ids": [r.course_id for r in rows]}


@blp.route("/students/<int:student_id>/courses", methods=["POST"])
@jwt_required()
@role_required("admin")
@blp.arguments(StudentCoursesSchema)
@blp.response(200)
def set_student_courses(data, student_id):
    """设置学生已选课程（全量替换）。"""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404, message="学生不存在")

    StudentCourse.query.filter_by(student_id=student_id).delete()
    for cid in data["course_ids"]:
        course = db.session.get(Course, cid)
        if not course:
            abort(404, message=f"课程 #{cid} 不存在")
        db.session.add(StudentCourse(student_id=student_id, course_id=cid))
    db.session.commit()
    logger.info("Student #{} enrolled in {} courses", student_id, len(data["course_ids"]))
    return {"course_ids": data["course_ids"]}
