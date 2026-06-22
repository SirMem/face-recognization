"""Face recognition service — InsightFace ArcFace.

Uses InsightFace's pre-trained ArcFace ResNet50 model (buffalo_l) for
face detection + alignment + 512-dim embedding extraction.
"""

from __future__ import annotations

import numpy as np
from loguru import logger
from PIL import Image


class FaceService:
    """High-level face operations backed by InsightFace ArcFace."""

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self._app = None
        logger.info("FaceService created (threshold={})", threshold)

    # ── Lazy init ───────────────────────────────────────────────────

    @property
    def app(self):
        if self._app is None:
            self._init_model()
        return self._app

    def _init_model(self):
        """Lazy-load insightface model (auto-downloaded on first use)."""
        from insightface.app import FaceAnalysis

        self._app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        self._app.prepare(ctx_id=-1)
        logger.info("InsightFace ArcFace loaded (buffalo_l)")

    # ── Public API ─────────────────────────────────────────────────

    def extract_embedding(self, image: Image.Image) -> np.ndarray | None:
        """Detect the largest face and return its 512-dim ArcFace embedding.

        Returns None if no face is detected.
        """
        import cv2

        img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        faces = self.app.get(img_bgr)

        if len(faces) == 0:
            logger.warning("No face detected")
            return None

        # 取检测置信度最高的脸
        face = max(faces, key=lambda f: f.det_score)
        logger.debug("Face detected score={:.3f}", face.det_score)

        emb = face.embedding.astype(np.float64)
        # L2 归一化 → 单位向量，便于欧氏距离比较
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb /= norm
        return emb

    def compare(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Euclidean distance between two L2-normalized embeddings."""
        return float(np.sqrt(np.sum(np.square(emb1 - emb2))))

    def is_match(self, emb1: np.ndarray, emb2: np.ndarray) -> tuple[bool, float]:
        dist = self.compare(emb1, emb2)
        return (dist < self.threshold), dist


# ── Singleton ─────────────────────────────────────────────────────

_face_service: FaceService | None = None


def get_face_service(threshold: float = 1.0) -> FaceService:
    global _face_service
    if _face_service is None:
        _face_service = FaceService(threshold)
    return _face_service
