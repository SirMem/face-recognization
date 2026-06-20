import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "face-recognition-secret-key-change-in-production")

    # Database
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "121223")
    DB_NAME = os.getenv("DB_NAME", "db_school")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7  # 7 days

    # File upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER",
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads"))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR",
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs"))

    # Face recognition
    FACE_MODEL_PATH = os.getenv(
        "FACE_MODEL_PATH",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                     "waiter-facerecognition-python", "model_data", "facenet_mobilenet.h5")
    )
    FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.9"))

    # Flask-Smorest
    API_TITLE = "人脸识别考勤系统 API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
