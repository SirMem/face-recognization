"""Face recognition resources: register & check-in."""

import json
import os
import uuid
from pathlib import Path

import numpy as np
from flask import current_app
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from loguru import logger
from PIL import Image

from app.extensions import db
from app.models import Attendance, Student
from app.schemas import FaceResultSchema, RegisterFaceSchema, RecognizeFaceSchema
from app.services.face_service import get_face_service

blp = Blueprint("face", __name__, url_prefix="/face", description="人脸注册与识别打卡")


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def _save_upload(image_file) -> str:
    """Save uploaded file to uploads/ and return the absolute path."""
    ext = image_file.filename.rsplit(".", 1)[1].lower() if "." in image_file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    image_file.save(path)
    return path


def _embedding_to_str(emb: np.ndarray) -> str:
    return json.dumps(emb.tolist())


def _str_to_embedding(s: str) -> np.ndarray | None:
    if not s:
        return None
    try:
        return np.array(json.loads(s), dtype=np.float64)
    except (json.JSONDecodeError, TypeError):
        return None


# ── Register face ─────────────────────────────────────────────────────

@blp.route("/register", methods=["POST"])
@jwt_required()
@blp.response(200)
def register_face():
    """上传人脸照片，提取 embedding 并关联到学生。

    multipart/form-data:
      - student_id (int, form) — 学生ID
      - image (file) — 人脸照片
    """
    from flask import request

    # Parse form fields manually (Flask-Smorest doesn't mix form+files well)
    try:
        student_id = int(request.form.get("student_id", 0))
    except (TypeError, ValueError):
        abort(422, message="student_id 必须是整数")

    image_file = request.files.get("image")
    if not image_file:
        abort(422, message="请上传图片文件")

    student = db.session.get(Student, student_id)
    if not student:
        abort(404, message=f"学生 #{student_id} 不存在")

    if not _allowed_file(image_file.filename):
        abort(422, message="不支持的图片格式，仅支持 jpg/jpeg/png")

    # Save file
    image_path = _save_upload(image_file)

    # Extract embedding
    try:
        pil_img = Image.open(image_path).convert("RGB")
        face_svc = get_face_service(
            current_app.config["FACE_MATCH_THRESHOLD"],
        )
        embedding = face_svc.extract_embedding(pil_img)
        if embedding is None:
            if os.path.exists(image_path):
                os.remove(image_path)
            abort(422, message="未检测到人脸，请上传包含正脸的照片")
    except Exception as e:
        logger.error("Face embedding failed for student #{}: {}", student_id, e)
        # Clean up file on failure
        if os.path.exists(image_path):
            os.remove(image_path)
        abort(500, message=f"人脸特征提取失败: {str(e)}")

    # Persist
    student.face_image_path = image_path
    student.face_embedding = _embedding_to_str(embedding)
    db.session.commit()

    logger.info("Face registered for student #{} ({})", student_id, student.name)

    return {
        "message": "人脸注册成功",
        "student_id": student.id,
        "student_name": student.name,
        "image_path": image_path,
    }


# ── Recognize (check-in) ──────────────────────────────────────────────

@blp.route("/recognize", methods=["POST"])
@blp.response(200)
def recognize_face():
    """上传照片进行人脸识别打卡。自动匹配最相似的学生并记录考勤。

    multipart/form-data:
      - image (file) — 人脸照片
      - course_id (int, form, optional) — 课程ID
    """
    from flask import request

    image_file = request.files.get("image")
    if not image_file:
        abort(422, message="请上传图片文件")

    try:
        course_id = int(request.form.get("course_id")) if request.form.get("course_id") else None
    except (TypeError, ValueError):
        abort(422, message="course_id 必须是整数")

    if not _allowed_file(image_file.filename):
        abort(422, message="不支持的图片格式，仅支持 jpg/jpeg/png")

    # Save temp file
    image_path = _save_upload(image_file)
    pil_img = Image.open(image_path).convert("RGB")

    # Load face service
    face_svc = get_face_service(
        current_app.config["FACE_MATCH_THRESHOLD"],
    )

    # Extract input embedding
    try:
        input_emb = face_svc.extract_embedding(pil_img)
        if input_emb is None:
            if os.path.exists(image_path):
                os.remove(image_path)
            abort(422, message="未检测到人脸，请上传包含正脸的照片")
    except Exception as e:
        logger.error("Recognize embedding failed: {}", e)
        if os.path.exists(image_path):
            os.remove(image_path)
        abort(500, message=f"人脸特征提取失败: {str(e)}")

    # Brute-force match against all enrolled students
    students = Student.query.filter(Student.face_embedding != "").all()
    if not students:
        if os.path.exists(image_path):
            os.remove(image_path)
        abort(400, message="系统中尚无已注册人脸，请先注册")

    best_match = None
    best_distance = float("inf")

    for stu in students:
        stored_emb = _str_to_embedding(stu.face_embedding)
        if stored_emb is None or stored_emb.shape != input_emb.shape:
            continue
        dist = face_svc.compare(input_emb, stored_emb)
        if dist < best_distance:
            best_distance = dist
            best_match = stu

    # Clean up temp file
    if os.path.exists(image_path):
        os.remove(image_path)

    is_match = best_distance < face_svc.threshold

    if is_match and best_match:
        # confidence = 余弦相似度（对 L2 单位向量，等价于 1 - d²/2）
        cos_sim = 1.0 - (best_distance ** 2) / 2.0
        confidence = max(0.0, min(1.0, cos_sim))

        # Record attendance
        record = Attendance(
            student_id=best_match.id,
            course_id=course_id,
            status="present",
            confidence=round(confidence, 4),
        )
        db.session.add(record)
        db.session.commit()

        logger.info("Check-in: {} (student #{}) distance={:.4f}",
                     best_match.name, best_match.id, best_distance)

        return {
            "is_match": True,
            "student_id": best_match.id,
            "student_name": best_match.name,
            "student_no": best_match.student_no,
            "distance": round(best_distance, 4),
            "confidence": round(record.confidence, 4),
            "attendance_id": record.id,
            "checkin_time": record.checkin_time.isoformat(),
        }
    else:
        logger.info("No match found, best distance={:.4f}", best_distance)
        return {
            "is_match": False,
            "student_id": None,
            "student_name": None,
            "distance": round(best_distance, 4),
            "message": "未识别到匹配的人脸",
        }


# ── List registered students ──────────────────────────────────────────

@blp.route("/students", methods=["GET"])
@jwt_required()
@blp.response(200)
def list_registered():
    """获取已注册人脸的學生列表。"""
    students = Student.query.filter(Student.face_embedding != "").all()
    return [
        {"id": s.id, "student_no": s.student_no, "name": s.name, "class_id": s.class_id}
        for s in students
    ]
