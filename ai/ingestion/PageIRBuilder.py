"""PR-04 PageIRBuilder — constructs a PageIR from a SourceAsset.

Rules:
  - PageIR uses native source pixels exclusively.
  - Browser resizing must never change PageIR coordinates.
  - For PR-04, when the user uploads a single standalone diagram, we
    create one whole_image_region covering (0,0,width,height) and label
    it honestly as "whole image supplied by user" — NOT as "auto-detected".
  - We do NOT fabricate figure detections.  Figure detection (SAM2, CV)
    will populate this in future PRs.
"""
from __future__ import annotations

from shared.schemas.ingestion import (
    PageFigure,
    PageIR,
    PageRegion,
    SourceAsset,
)


class PageIRBuilder:
    """Builds a PageIR from a SourceAsset.

    For PR-04: single standalone diagram → one honest whole-image region + figure.
    Future PRs will add SAM2/CV multi-figure detection here.
    """

    PR04_VERSION = "1.0"

    def build(self, asset: SourceAsset, public_url: str) -> PageIR:
        """Build a PageIR for a single uploaded image.

        Args:
            asset:      The SourceAsset created by UploadService.
            public_url: The frontend-accessible URL for the image.

        Returns:
            PageIR in source_px coordinate space.
        """
        w = float(asset.width_px)
        h = float(asset.height_px)

        # One honest region covering the whole image.
        # Detection method is "user_supplied" — we are NOT claiming we detected it.
        whole_region = PageRegion(
            id="region_001",
            label="whole_image",
            x=0.0,
            y=0.0,
            width=w,
            height=h,
            confidence=1.0,
            detection_method="user_supplied",
            notes="Whole image supplied directly by user; no sub-figure detection performed yet.",
        )

        # One figure coextensive with the whole image.
        # Honest label: "whole image supplied by user"
        whole_figure = PageFigure(
            id="figure_001",
            region_id="region_001",
            page_x=0.0,
            page_y=0.0,
            width=w,
            height=h,
            detection_method="user_supplied",
            notes=(
                "Figure spans the full uploaded image. "
                "Automatic figure detection not yet applied."
            ),
        )

        page_ir = PageIR(
            version=self.PR04_VERSION,
            source={
                "assetId": asset.id,
                "width_px": asset.width_px,
                "height_px": asset.height_px,
                "mimeType": asset.mime_type,
                "url": public_url,
                "sha256": asset.sha256,
            },
            coordinate_space={
                "type": "source_px",
                "width": asset.width_px,
                "height": asset.height_px,
                "origin": "top_left",
            },
            regions=[whole_region],
            figures=[whole_figure],
            text_blocks=[],
            metadata={
                "pipeline": "PR-04-standalone-upload",
                "note": (
                    "Single-diagram upload. figure_001 is the entire image. "
                    "Multi-figure detection and OCR will be added in future PRs."
                ),
            },
        )
        return page_ir
