"""Flask application factory."""

import os

from flask import Flask
from loguru import logger

from app.config import Config
from app.core.log import setup_logging
from app.extensions import api, db, jwt, limiter, ma, migrate


def create_app(config_object: type[Config] | None = None) -> Flask:
    if config_object is None:
        config_object = Config

    app = Flask(__name__)
    app.config.from_object(config_object)

    # ── Logging (earliest possible) ──────────────────────────────────
    setup_logging(
        level=app.config.get("LOG_LEVEL", "INFO"),
        log_dir=app.config.get("LOG_DIR", "logs"),
    )

    # ── Extensions ──────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    api.init_app(app)
    limiter.init_app(app)

    # ── JWT callbacks ───────────────────────────────────────────────
    from flask_jwt_extended import get_jwt

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        # Simple in-memory / stateless approach: we don't blacklist by default.
        # For production, store jti in Redis with expiry matching token lifetime.
        return False

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, jwt_payload):
        return {"code": 401, "message": "Token 已过期"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"code": 401, "message": "Token 无效"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"code": 401, "message": "缺少认证 Token"}, 401

    # ── Blueprints ──────────────────────────────────────────────────
    from app.resources import attendance_blp, auth_blp, face_blp, manage_blp

    api.register_blueprint(auth_blp)
    api.register_blueprint(face_blp)
    api.register_blueprint(manage_blp)
    api.register_blueprint(attendance_blp)

    # ── Health check ────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return {"status": "ok"}

    # ── Global error handler ────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Unhandled exception: {}", str(e))
        return {"code": 500, "message": "服务器内部错误"}, 500

    logger.info("App created (env={})", os.getenv("FLASK_ENV", "development"))
    return app
