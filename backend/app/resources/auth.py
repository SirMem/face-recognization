"""Authentication resources: login & token refresh."""

import argon2
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required,
)
from flask_smorest import Blueprint, abort
from loguru import logger

from app.extensions import db, limiter
from app.models import User
from app.schemas import LoginSchema

blp = Blueprint("auth", __name__, url_prefix="/auth", description="管理员认证")

_ph = argon2.PasswordHasher()


@blp.route("/login", methods=["POST"])
@blp.arguments(LoginSchema)
@blp.response(200)
@limiter.limit("10/minute")
def login(data):
    """管理员登录，返回 JWT access + refresh token."""
    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        abort(401, message="用户名或密码错误")

    try:
        _ph.verify(user.password_hash, data["password"])
    except argon2.exceptions.VerifyMismatchError:
        abort(401, message="用户名或密码错误")

    # Re-hash if needed (argon2 recommends this)
    if _ph.check_needs_rehash(user.password_hash):
        user.password_hash = _ph.hash(data["password"])
        db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"roles": [user.role]},
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    logger.info("User '{}' logged in", user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }


@blp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@blp.response(200)
def refresh():
    """用 refresh token 换取新的 access token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return {"access_token": access_token}
