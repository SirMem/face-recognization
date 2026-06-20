"""Face recognition service — Keras 3 compatible.

Builds the exact same architecture as the original FaceNet+Keras2 MobileNet,
then loads the pretrained .h5 weights by name.
"""

import json
import os
from pathlib import Path

import numpy as np
from loguru import logger
from PIL import Image

import keras
from keras import layers, models, ops


class FaceService:
    """High-level face operations — reuses original MobileNet architecture."""

    def __init__(self, model_path: str, threshold: float = 0.9):
        self.threshold = threshold
        self.input_shape = (160, 160, 3)
        self._model: keras.Model | None = None
        self._model_path = model_path
        logger.info("FaceService created (model={}, threshold={})", model_path, threshold)

    @property
    def model(self) -> keras.Model:
        if self._model is None:
            self._model = self._build_model()
        return self._model

    def _build_model(self) -> keras.Model:
        """Build MobileNet + L2-normalized embedding head, load pretrained weights."""
        if not os.path.exists(self._model_path):
            raise FileNotFoundError(f"FaceNet weights not found: {self._model_path}")

        from app.services.mobilenet import MobileNet

        # Build backbone (same architecture as original)
        inputs = keras.layers.Input(shape=self.input_shape)
        backbone = MobileNet(inputs, dropout_keep_prob=0.4)

        # L2 normalize → 128-dim unit vector
        outputs = layers.Lambda(
            lambda v: ops.normalize(v, axis=1),
            output_shape=lambda s: (s[0], 128),
            name="Embedding"
        )(backbone.output)

        model = models.Model(inputs, outputs, name="FaceNet_MobileNet")

        # Load pretrained weights (Keras 2 .h5 → Keras 3 compatible)
        model.load_weights(self._model_path, skip_mismatch=True)

        logger.info("FaceNet model loaded from {} (Keras {})", self._model_path, keras.__version__)
        return model

    # ── Image preprocessing ────────────────────────────────────────

    def _letterbox_image(self, image: Image.Image) -> Image.Image:
        """Resize with letterboxing, preserving aspect ratio."""
        iw, ih = image.size
        w, h = self.input_shape[1], self.input_shape[0]
        scale = min(w / iw, h / ih)
        nw = int(iw * scale)
        nh = int(ih * scale)

        image = image.resize((nw, nh), Image.BICUBIC)
        new_image = Image.new("RGB", (w, h), (128, 128, 128))
        new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))
        return new_image

    # ── Public API ─────────────────────────────────────────────────

    def extract_embedding(self, image: Image.Image) -> np.ndarray:
        """Extract 128-dim embedding from a face image."""
        processed = self._letterbox_image(image)
        arr = np.asarray(processed).astype(np.float64) / 255.0
        arr = np.expand_dims(arr, axis=0).astype(np.float32)
        embedding = self.model.predict(arr, verbose=0)
        return embedding[0]

    def compare(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Euclidean distance between two embeddings. Lower = more similar."""
        return float(np.sqrt(np.sum(np.square(emb1 - emb2))))

    def is_match(self, emb1: np.ndarray, emb2: np.ndarray) -> tuple[bool, float]:
        dist = self.compare(emb1, emb2)
        return (dist < self.threshold), dist


# ── Singleton ─────────────────────────────────────────────────────

_face_service: FaceService | None = None


def get_face_service(model_path: str, threshold: float = 0.9) -> FaceService:
    global _face_service
    if _face_service is None:
        _face_service = FaceService(model_path, threshold)
    return _face_service
