"""Loguru-based logging setup that intercepts all standard library loggers."""

import logging
import sys
from pathlib import Path

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept standard library logging and route to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO", log_dir: str = "logs") -> None:
    """Configure Loguru with console and rotating file sinks.

    Must be called early in create_app(), before any other logging.
    """
    logger.remove()

    # Console sink (colored, human-readable)
    logger.add(
        sys.stdout,
        level=level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "{message}"
        ),
        enqueue=True,
    )

    # File sink (rotating, JSON-structured for production)
    log_path = Path(log_dir) / "app_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_path),
        level=level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        enqueue=True,
    )

    # Intercept all standard library loggers
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in ("werkzeug", "flask.app", "flask_jwt_extended", "sqlalchemy.engine"):
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False

    logger.info("Loguru initialized — level={}, log_dir={}", level, log_dir)
