"""PR-04 UploadService — validates and stores uploaded image bytes, creates SourceAsset.

Rules:
  - Accepts raw bytes from the HTTP multipart upload.
  - Writes bytes to storage/uploads/ with a UUID-based name (preserves original ext).
  - Copies to apps/web/public/uploads/ so Vite dev server can serve it.
  - Reads native dimensions via cv2.
  - Computes sha256 for identity/dedup (NOT for physics classification).
  - OriginalFilename is metadata only — never used for routing.
  - Returns SourceAsset; never raises on unknown MIME — only on corrupt images.
"""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from shared.schemas.ingestion import SourceAsset, compute_sha256

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
}

# Reasonable size limit: 50 MB
MAX_BYTE_SIZE = 50 * 1024 * 1024


class UploadValidationError(ValueError):
    """Raised when the uploaded file fails validation."""
    pass


class UploadService:
    """Validates image bytes and creates a SourceAsset.

    Args:
        storage_dir:  Where uploaded bytes are persistently stored.
        public_dir:   Where files are copied so the frontend can serve them.
    """

    def __init__(self, storage_dir: Path, public_dir: Path):
        self.storage_dir = storage_dir
        self.public_dir = public_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.public_dir.mkdir(parents=True, exist_ok=True)

    def ingest(
        self,
        data: bytes,
        original_filename: str,
        mime_type: str,
    ) -> SourceAsset:
        """Validate, store, and wrap image bytes as a SourceAsset.

        Args:
            data:              Raw image bytes.
            original_filename: User-supplied filename (metadata only).
            mime_type:         MIME type declared by the client.

        Returns:
            SourceAsset with native dimensions and sha256.

        Raises:
            UploadValidationError: For empty data, oversized files,
                                   unsupported MIME, or corrupt images.
        """
        # --- Byte-level validation ---
        if not data:
            raise UploadValidationError("Uploaded file is empty.")
        if len(data) > MAX_BYTE_SIZE:
            raise UploadValidationError(
                f"File is too large: {len(data)} bytes (max {MAX_BYTE_SIZE} bytes)."
            )

        # --- MIME validation ---
        # Normalise: some clients send 'image/jpg' instead of 'image/jpeg'
        normalised_mime = mime_type.lower().strip()
        if normalised_mime == "image/jpg":
            normalised_mime = "image/jpeg"
        ext = ALLOWED_MIME_TYPES.get(normalised_mime)
        if ext is None:
            raise UploadValidationError(
                f"Unsupported MIME type '{mime_type}'. "
                f"Allowed: {sorted(ALLOWED_MIME_TYPES.keys())}"
            )

        # Use original extension if MIME is ambiguous between jpg/jpeg
        orig_ext = Path(original_filename).suffix.lower()
        if orig_ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
            ext = orig_ext if orig_ext != ".jpeg" else ".jpg"

        # --- Decode image to get native dimensions ---
        arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise UploadValidationError(
                "Could not decode image — file may be corrupt or not a supported image format."
            )
        height_px, width_px = img.shape[:2]
        if width_px == 0 or height_px == 0:
            raise UploadValidationError("Image decoded with zero dimensions.")

        # --- Compute identity ---
        sha256 = compute_sha256(data)
        asset_id = uuid.uuid4().hex

        # --- Persist ---
        unique_name = f"diagram_{asset_id[:8]}{ext}"
        storage_path = self.storage_dir / unique_name
        public_path = self.public_dir / unique_name

        storage_path.write_bytes(data)
        shutil.copy2(storage_path, public_path)

        return SourceAsset(
            id=asset_id,
            mime_type=normalised_mime,
            original_filename=original_filename,
            byte_size=len(data),
            width_px=width_px,
            height_px=height_px,
            sha256=sha256,
            storage_path=str(storage_path),
        )

    def get_public_url(self, asset: SourceAsset) -> str:
        """Returns a frontend-accessible URL for the asset."""
        path = Path(asset.storage_path)
        return f"/uploads/{path.name}"
