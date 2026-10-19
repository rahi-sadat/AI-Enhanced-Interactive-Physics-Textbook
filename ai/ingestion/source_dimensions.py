"""Keep decoded SourceAsset dimensions authoritative across grounded BookIR."""
from __future__ import annotations

from shared.schemas.ingestion import BookIR, SourceAsset


class SourceDimensionMismatch(ValueError):
    pass


def enforce_source_dimensions(book_ir: BookIR, asset: SourceAsset) -> None:
    if asset.width_px <= 0 or asset.height_px <= 0:
        raise SourceDimensionMismatch("Decoded source dimensions must be positive.")
    if book_ir.geometry is None:
        book_ir.geometry = {}
    for axis, expected, aliases in (
        ("width", asset.width_px, ("width", "source_width", "sourceWidth")),
        ("height", asset.height_px, ("height", "source_height", "sourceHeight")),
    ):
        for key in aliases:
            present = book_ir.geometry.get(key)
            if present is not None and (isinstance(present, bool) or present != expected):
                raise SourceDimensionMismatch(
                    f"Source dimension mismatch: {key}={present}, decoded {axis}={expected}."
                )
        book_ir.geometry[axis] = expected
