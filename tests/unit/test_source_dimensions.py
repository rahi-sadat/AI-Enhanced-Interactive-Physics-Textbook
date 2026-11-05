import pytest

from ai.ingestion.source_dimensions import SourceDimensionMismatch, enforce_source_dimensions
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.auto import AutoResolutionEngine
from shared.schemas.ingestion import BookEntity, BookIR, SourceAsset


def _asset(width=1537, height=984):
    return SourceAsset(id="source_1", sha256="abc", original_filename="arbitrary.png",
                       mime_type="image/png", byte_size=1, width_px=width,
                       height_px=height, storage_path="unused")


def test_decoded_dimensions_propagate_to_book_ir():
    book = BookIR(geometry={"pivot": {"x": 100, "y": 50}})
    enforce_source_dimensions(book, _asset())
    assert book.geometry["width"] == 1537
    assert book.geometry["height"] == 984
    assert book.geometry["pivot"] == {"x": 100, "y": 50}


@pytest.mark.parametrize("geometry", [
    {"width": 800, "height": 600},
    {"sourceWidth": 800, "height": 984},
    {"width": 1537, "source_height": 600},
])
def test_resized_cv_dimensions_are_rejected(geometry):
    book = BookIR(geometry=geometry)
    with pytest.raises(SourceDimensionMismatch):
        enforce_source_dimensions(book, _asset())


@pytest.mark.parametrize("width,height", [
    (393, 328), (800, 600), (1024, 1024), (1536, 1024), (720, 1200),
])
def test_source_asset_page_book_and_scene_dimensions_agree(width, height):
    asset = _asset(width, height)
    page = PageIRBuilder().build(asset, "/uploads/neutral-name.png")
    pivot = {"x": width * 0.4, "y": height * 0.15}
    bob = {"x": width * 0.48, "y": height * 0.75}
    book = BookIR(source_asset_id=asset.id, figure_id="figure_001",
                  domain="mechanics", subtype="pendulum", status="NEEDS_REVIEW",
                  geometry={"pivot": pivot, "bob_center": bob,
                            "string_length_px": ((bob["x"] - pivot["x"]) ** 2 +
                                                 (bob["y"] - pivot["y"]) ** 2) ** 0.5,
                            "bob_radius_px": width * 0.02},
                  entities=[
                      BookEntity(id="pivot", type="pivot", position_source_px=pivot, evidence_refs=["cv"]),
                      BookEntity(id="bob", type="bob", position_source_px=bob, evidence_refs=["cv"]),
                      BookEntity(id="string", type="string", position_source_px=pivot, evidence_refs=["cv"]),
                  ],
                  parameters={
                      "pivot": {**pivot, "provenance": {"source": "cv"}},
                      "bob_position": {**bob, "provenance": {"source": "cv"}},
                      "string_length_px": {"value": ((bob["x"] - pivot["x"]) ** 2 +
                                                    (bob["y"] - pivot["y"]) ** 2) ** 0.5,
                                           "unit": "px", "provenance": {"source": "cv"}},
                      "bob_radius_px": {"value": width * 0.02, "unit": "px",
                                        "provenance": {"source": "cv"}},
                  })
    enforce_source_dimensions(book, asset)
    AutoResolutionEngine.resolve(book)
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", compiled.issues
    assert page.source["width_px"] == book.geometry["width"] == compiled.scene["coordinateSpace"]["width"] == width
    assert page.source["height_px"] == book.geometry["height"] == compiled.scene["coordinateSpace"]["height"] == height
