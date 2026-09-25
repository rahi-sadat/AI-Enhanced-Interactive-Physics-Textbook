"""PR-04 BookUnderstandingPipeline — clean boundary for future VLM/OCR/CV perception.

For PR-04:
  - Returns an honest UNRESOLVED BookIR.
  - Does NOT write fake heuristics just to make fields look populated.
  - Does NOT infer domain from filename, hash, or URL patterns.
  - Does NOT assume any specific physics type.

Future PRs will fill this with:
  - VLM semantic understanding
  - OCR parameter extraction
  - SAM2/CV entity detection

The clean boundary here is the contract: analyze(page_ir) → BookIR.
"""
from __future__ import annotations

from shared.schemas.ingestion import BookIR, BookIRStatus, PageIR


class BookUnderstandingPipeline:
    """Semantic physics understanding pipeline.

    PR-04 implementation: always returns UNRESOLVED with no invented content.
    No filename matching, no hash matching, no default physics fallback.
    """

    def analyze(self, page_ir: PageIR) -> BookIR:
        """Analyze a PageIR and return a BookIR.

        Args:
            page_ir: The PageIR constructed from the uploaded image.

        Returns:
            BookIR with status=UNRESOLVED when no semantic understanding
            is available (which is always the case in PR-04).
        """
        # Extract figure ref for traceability
        figure_id = page_ir.figures[0].id if page_ir.figures else None
        asset_id = page_ir.source.get("assetId")

        book_ir = BookIR(
            version="1.0",
            source_asset_id=asset_id,
            page_ir_version=page_ir.version,
            figure_id=figure_id,

            # domain and subtype are intentionally None.
            # PR-04 does not have VLM/OCR to determine these.
            domain=None,
            subtype=None,

            entities=[],
            relationships=[],
            parameters={},
            geometry={},
            assumptions=[],
            provenance={
                "pipeline": "BookUnderstandingPipeline",
                "pipeline_version": "PR-04-stub",
                "note": (
                    "No VLM, OCR, or CV analysis was performed. "
                    "Domain and subtype are unknown. "
                    "Automatic population will be implemented in future PRs."
                ),
            },
            confidence={
                "domain": 0.0,
                "subtype": 0.0,
                "overall": 0.0,
            },
            status=BookIRStatus.UNRESOLVED,
            status_notes=(
                "Image received and PageIR created. "
                "No physics concept was identified — BookUnderstandingPipeline "
                "returned UNRESOLVED (expected for PR-04). "
                "VLM/OCR/CV perception is not yet implemented."
            ),
        )
        return book_ir
