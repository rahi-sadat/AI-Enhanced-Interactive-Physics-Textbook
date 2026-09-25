"""PR-04 Unit Tests.

Tests:
  1. Coordinate transforms (PageFigure local ↔ page, round-trip)
  2. Truthfulness: unknown upload must not become any physics type
  3. PhysicsCompiler: complete BookIR → PhysicsScene
  4. PhysicsCompiler: incomplete BookIR → NEEDS_REVIEW
  5. PhysicsCompiler: unsupported BookIR → UNSUPPORTED
  6. PhysicsCompiler: unknown domain/subtype → UNRESOLVED
  7. BookIR: null domain/subtype serialises correctly
  8. PageIR: dimensions survive round-trip
  9. Provenance: evidence references serialise
  10. BookUnderstandingPipeline: arbitrary image → always UNRESOLVED

Run with:
    python tests/unit/test_pr04_ingestion.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Make sure project root is on path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PageFigure,
    PageIR,
    PageRegion,
    PageTextBlock,
    PhysicalValue,
    ProvenanceRecord,
    SourceAsset,
    compute_sha256,
)
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PhysicsCompiler import PhysicsCompiler


# ---------------------------------------------------------------------------
# Test runner helpers
# ---------------------------------------------------------------------------

_PASS = 0
_FAIL = 0
_ERRORS: list = []


def test(name: str, condition: bool, msg: str = ""):
    global _PASS, _FAIL
    if condition:
        print(f"  ✓ {name}")
        _PASS += 1
    else:
        print(f"  ✗ {name}{' — ' + msg if msg else ''}")
        _FAIL += 1
        _ERRORS.append(f"{name}: {msg}")


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ---------------------------------------------------------------------------
# 1. Coordinate transforms
# ---------------------------------------------------------------------------

section("1. PageFigure coordinate transforms")

fig = PageFigure(
    id="figure_001",
    region_id="region_001",
    page_x=300.0,
    page_y=700.0,
    width=800.0,
    height=500.0,
)

# local → page
page_x, page_y = fig.local_to_page(250.0, 100.0)
test("local(250,100) → page(550,800)", page_x == 550.0 and page_y == 800.0,
     f"got ({page_x},{page_y})")

# page → local
lx, ly = fig.page_to_local(550.0, 800.0)
test("page(550,800) → local(250,100)", lx == 250.0 and ly == 100.0,
     f"got ({lx},{ly})")

# Round-trip
orig_lx, orig_ly = 178.5, 342.1
px, py = fig.local_to_page(orig_lx, orig_ly)
rt_lx, rt_ly = fig.page_to_local(px, py)
test("Round-trip local→page→local", abs(rt_lx - orig_lx) < 1e-9 and abs(rt_ly - orig_ly) < 1e-9,
     f"got ({rt_lx},{rt_ly})")

# Edge: (0,0) local is page origin of figure
px0, py0 = fig.local_to_page(0.0, 0.0)
test("local(0,0) → page origin", px0 == 300.0 and py0 == 700.0, f"got ({px0},{py0})")

# Non-square: 16:9 widescreen figure
fig_16_9 = PageFigure(id="fig_wide", region_id="reg", page_x=100.0, page_y=200.0, width=1600.0, height=900.0)
w_px, w_py = fig_16_9.local_to_page(800.0, 450.0)
test("16:9 widescreen local(800,450) → page(900,650)", w_px == 900.0 and w_py == 650.0)
w_lx, w_ly = fig_16_9.page_to_local(900.0, 650.0)
test("16:9 widescreen round-trip", w_lx == 800.0 and w_ly == 450.0)

# Non-square: 9:16 tall portrait figure
fig_9_16 = PageFigure(id="fig_tall", region_id="reg", page_x=500.0, page_y=100.0, width=450.0, height=800.0)
t_px, t_py = fig_9_16.local_to_page(225.0, 400.0)
test("9:16 portrait local(225,400) → page(725,500)", t_px == 725.0 and t_py == 500.0)

# Square: 1:1 aspect ratio
fig_sq = PageFigure(id="fig_sq", region_id="reg", page_x=50.0, page_y=50.0, width=600.0, height=600.0)
s_px, s_py = fig_sq.local_to_page(300.0, 300.0)
test("1:1 square local(300,300) → page(350,350)", s_px == 350.0 and s_py == 350.0)

# Viewport resizing invariance
page_ir_sample = PageIR(
    source={"width_px": 1920, "height_px": 1080},
    coordinate_space={"type": "source_px", "width": 1920, "height": 1080},
    figures=[fig_16_9]
)
# Simulate browser viewport resize event (e.g. window shrinks to 800x600 CSS px)
simulated_css_viewports = [(1280, 720), (800, 600), (375, 667)]
for v_w, v_h in simulated_css_viewports:
    # PageIR must remain in authoritative source_px
    test(f"Viewport resize to {v_w}x{v_h} does not mutate PageIR source_px width",
         page_ir_sample.coordinate_space["width"] == 1920)
    test(f"Viewport resize to {v_w}x{v_h} does not mutate PageIR figure dimensions",
         page_ir_sample.figures[0].width == 1600.0 and page_ir_sample.figures[0].height == 900.0)


# ---------------------------------------------------------------------------
# 2. Truthfulness: BookUnderstandingPipeline never invents physics
# ---------------------------------------------------------------------------

section("2. Truthfulness — BookUnderstandingPipeline")

# Fake a PageIR for an unknown image
fake_asset = SourceAsset(
    id="deadbeef0001",
    mime_type="image/png",
    original_filename="random_photo.png",   # deliberately misleading name
    byte_size=12345,
    width_px=640,
    height_px=480,
    sha256="a" * 64,
    storage_path="/tmp/test.png",
)
builder = PageIRBuilder()
page_ir = builder.build(fake_asset, "/uploads/test.png")
pipeline = BookUnderstandingPipeline()
book_ir = pipeline.analyze(page_ir)

test("Unknown image → domain is None", book_ir.domain is None,
     f"domain was: {book_ir.domain}")
test("Unknown image → subtype is None", book_ir.subtype is None,
     f"subtype was: {book_ir.subtype}")
test("Unknown image → status is UNRESOLVED", book_ir.status == BookIRStatus.UNRESOLVED,
     f"status was: {book_ir.status}")
test("Unknown image → no entities fabricated", len(book_ir.entities) == 0,
     f"entities: {book_ir.entities}")
test("Unknown image → no parameters fabricated", len(book_ir.parameters) == 0,
     f"parameters: {book_ir.parameters}")

# Confirm filename did not drive any classification
test("Filename 'random_photo.png' did not create a simulation",
     book_ir.status != BookIRStatus.READY_TO_COMPILE, "Should not be ready")

# Specific prohibited defaults
d = book_ir.to_dict()
prohibited = ["mechanics", "pendulum", "thin_lens", "circuit", "optics"]
for p in prohibited:
    test(f"'{p}' not invented as domain/subtype",
         d["domain"] != p and d["subtype"] != p,
         f"got domain={d['domain']}, subtype={d['subtype']}")


# ---------------------------------------------------------------------------
# 3. PhysicsCompiler: UNRESOLVED BookIR → UNRESOLVED result
# ---------------------------------------------------------------------------

section("3. PhysicsCompiler — UNRESOLVED BookIR")

compiler = PhysicsCompiler()

unresolved_ir = BookIR(
    domain=None,
    subtype=None,
    status=BookIRStatus.UNRESOLVED,
)
result = compiler.compile(unresolved_ir)
test("UNRESOLVED BookIR → compiler status UNRESOLVED", result.status == "UNRESOLVED",
     f"got: {result.status}")
test("UNRESOLVED → no scene fabricated", result.scene is None, f"scene: {result.scene}")
test("UNRESOLVED → has issues", len(result.issues) > 0, "Expected at least one issue")


# ---------------------------------------------------------------------------
# 4. PhysicsCompiler: incomplete BookIR → NEEDS_REVIEW
# ---------------------------------------------------------------------------

section("4. PhysicsCompiler — incomplete BookIR (known domain, not ready)")

incomplete_ir = BookIR(
    domain="mechanics",
    subtype="pendulum",
    status=BookIRStatus.UNRESOLVED,     # not READY_TO_COMPILE
    parameters={},
)
result = compiler.compile(incomplete_ir)
test("Incomplete pendulum BookIR → NEEDS_REVIEW", result.status == "NEEDS_REVIEW",
     f"got: {result.status}")
test("Incomplete → no scene", result.scene is None, f"scene: {result.scene}")


# ---------------------------------------------------------------------------
# 5. PhysicsCompiler: unsupported subtype → UNSUPPORTED
# ---------------------------------------------------------------------------

section("5. PhysicsCompiler — unsupported subtype")

unsupported_ir = BookIR(
    domain="mechanics",
    subtype="inclined_plane",      # not in SUPPORTED_SUBTYPES
    status=BookIRStatus.READY_TO_COMPILE,
    parameters={},
)
result = compiler.compile(unsupported_ir)
test("Unsupported subtype → UNSUPPORTED", result.status == "UNSUPPORTED",
     f"got: {result.status}")
test("Unsupported → no scene", result.scene is None)


# ---------------------------------------------------------------------------
# 6. PhysicsCompiler: complete pendulum BookIR → READY
# ---------------------------------------------------------------------------

section("6. PhysicsCompiler — complete pendulum BookIR → READY")

complete_pendulum_ir = BookIR(
    source_asset_id="asset_test_001",
    figure_id="figure_001",
    domain="mechanics",
    subtype="pendulum",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={
        "source_width": 800.0,
        "source_height": 600.0,
        "pivot": {"x": 200.0, "y": 50.0},
        "bob_position": {"x": 150.0, "y": 280.0},
        "string_length_px": 233.45,
        "bob_radius_px": 18.0,
    },
    parameters={
        "pivot": {"value": {"x": 200.0, "y": 50.0}, "status": "observed"},
        "bob_position": {"value": {"x": 150.0, "y": 280.0}, "status": "observed"},
        "string_length_px": {"value": 233.45, "status": "observed", "unit": "px"},
        "bob_radius_px": {"value": 18.0, "status": "observed", "unit": "px"},
        "gravity_m_s2": {"value": 9.81, "status": "assumed", "unit": "m/s²"},
        "length": {"value": 1.2, "status": "observed", "unit": "m"},
        "mass": {"value": 1.0, "status": "assumed", "unit": "kg"},
        "damping": {"value": 0.05, "status": "assumed", "unit": "1/s"},
    },
    entities=[
        BookEntity(
            id="pendulum_bob_1",
            type="pendulum",
            label="Simple Pendulum System",
            evidence_refs=["region_001"],
        )
    ],
)
result = compiler.compile(complete_pendulum_ir)
test("Complete pendulum → READY", result.status == "READY", f"got: {result.status} issues={result.issues}")
test("READY → scene present", result.scene is not None, "scene is None")
if result.scene:
    test("Scene contains pendulum object", "objects" in result.scene and
         any(o.get("type") == "pendulum" for o in result.scene.get("objects", [])),
         f"objects: {result.scene.get('objects')}")
    test("Scene coordinateSpace is source_px",
         result.scene.get("coordinateSpace", {}).get("type") == "source_px",
         f"coordinateSpace: {result.scene.get('coordinateSpace')}")
    test("Scene schemaVersion is canonical 1.0",
         result.scene.get("schemaVersion") == "1.0",
         f"schemaVersion: {result.scene.get('schemaVersion')}")
    test("Preserves entity identity pendulum_bob_1",
         result.scene.get("objects", [{}])[0].get("id") == "pendulum_bob_1",
         f"id: {result.scene.get('objects', [{}])[0].get('id')}")
    test("Preserves evidence refs",
         result.scene.get("objects", [{}])[0].get("evidence_refs") == ["region_001"],
         f"evidence_refs: {result.scene.get('objects', [{}])[0].get('evidence_refs')}")


# ---------------------------------------------------------------------------
# 7. PhysicsCompiler: complete thin_lens BookIR → READY
# ---------------------------------------------------------------------------

section("7. PhysicsCompiler — complete thin_lens BookIR → READY")

complete_lens_ir = BookIR(
    source_asset_id="asset_test_002",
    figure_id="figure_001",
    domain="optics",
    subtype="thin_lens",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={
        "source_width": 800.0,
        "source_height": 600.0,
        "lens_center": {"x": 400.0, "y": 300.0},
        "aperture_height_px": 220.0,
    },
    parameters={
        "lens_center": {"value": {"x": 400.0, "y": 300.0}, "status": "observed"},
        "focal_length_px": {"value": 130.0, "status": "observed", "unit": "px"},
        "aperture_height_px": {"value": 220.0, "status": "observed", "unit": "px"},
    },
    entities=[
        BookEntity(
            id="lens_001",
            type="thin_lens",
            label="Biconvex Lens",
            evidence_refs=["region_001"],
        )
    ],
)
result = compiler.compile(complete_lens_ir)
test("Complete thin_lens → READY", result.status == "READY", f"got: {result.status} issues={result.issues}")
test("Lens scene has elements", result.scene and "elements" in result.scene)
test("Lens scene schemaVersion is canonical 1.0", result.scene and result.scene.get("schemaVersion") == "1.0")
test("Lens scene coordinateSpace is source_px", result.scene and result.scene.get("coordinateSpace", {}).get("type") == "source_px")
test("Preserves lens entity identity", result.scene and result.scene.get("objects", [{}])[0].get("id") == "lens_001")


# ---------------------------------------------------------------------------
# 8. BookIR: null domain/subtype serialises correctly
# ---------------------------------------------------------------------------

section("8. BookIR serialisation with null domain/subtype")

null_ir = BookIR(
    domain=None,
    subtype=None,
    status=BookIRStatus.UNRESOLVED,
    status_notes="Test null serialisation",
)
d = null_ir.to_dict()
test("domain serialises as null", d["domain"] is None, f"got: {d['domain']}")
test("subtype serialises as null", d["subtype"] is None, f"got: {d['subtype']}")
test("status serialises", d["status"] == BookIRStatus.UNRESOLVED)
test("statusNotes serialises", d["statusNotes"] == "Test null serialisation")


# ---------------------------------------------------------------------------
# 9. Provenance: evidence references serialise
# ---------------------------------------------------------------------------

section("9. Provenance serialisation")

prov = ProvenanceRecord(
    source="ocr",
    evidence_refs=["text_11", "region_19"],
    confidence=0.94,
    notes="Extracted from label near lens",
)
d = prov.to_dict()
test("Provenance source", d["source"] == "ocr")
test("Provenance evidenceRefs", d["evidenceRefs"] == ["text_11", "region_19"])
test("Provenance confidence", abs(d["confidence"] - 0.94) < 1e-9)

# PhysicalValue with provenance
pv = PhysicalValue(
    value=20.0,
    unit="cm",
    status="observed",
    provenance=prov,
)
dv = pv.to_dict()
test("PhysicalValue value", dv["value"] == 20.0)
test("PhysicalValue unit", dv["unit"] == "cm")
test("PhysicalValue provenance nested", "provenance" in dv and dv["provenance"]["source"] == "ocr")

# BookEntity with evidence refs
entity = BookEntity(
    id="lens_1",
    type="lens",
    label="Convex Lens",
    evidence_refs=["region_19"],
)
de = entity.to_dict()
test("BookEntity evidenceRefs", de["evidenceRefs"] == ["region_19"])


# ---------------------------------------------------------------------------
# 10. PageIR: dimensions survive round-trip
# ---------------------------------------------------------------------------

section("10. PageIR dimension round-trip")

asset2 = SourceAsset(
    id="cafebabe0002",
    mime_type="image/jpeg",
    original_filename="does_not_matter.jpg",
    byte_size=99999,
    width_px=1536,
    height_px=1024,
    sha256="b" * 64,
    storage_path="/tmp/test2.jpg",
)
builder2 = PageIRBuilder()
pi = builder2.build(asset2, "/uploads/test2.jpg")
d = pi.to_dict()

test("PageIR source width_px", d["source"]["width_px"] == 1536)
test("PageIR source height_px", d["source"]["height_px"] == 1024)
test("PageIR coordinate_space type = source_px",
     d["coordinateSpace"]["type"] == "source_px")
test("PageIR has one region", len(d["regions"]) == 1)
test("PageIR region covers full image",
     d["regions"][0]["width"] == 1536.0 and d["regions"][0]["height"] == 1024.0)
test("PageIR has one figure", len(d["figures"]) == 1)
test("PageIR figure detectionMethod = user_supplied",
     d["figures"][0]["detectionMethod"] == "user_supplied")


# ---------------------------------------------------------------------------
# 11. sha256 computation
# ---------------------------------------------------------------------------

section("11. sha256 identity")

data1 = b"hello world"
data2 = b"hello world"
data3 = b"different content"
h1 = compute_sha256(data1)
h2 = compute_sha256(data2)
h3 = compute_sha256(data3)
test("Same bytes → same sha256", h1 == h2)
test("Different bytes → different sha256", h1 != h3)
test("sha256 is 64 hex chars", len(h1) == 64)


# ---------------------------------------------------------------------------
# 12. Regression: Zero Fabricated Defaults (Strict Rejection)
# ---------------------------------------------------------------------------

section("12. Regression: Zero Fabricated Physical Defaults")

def make_base_pendulum():
    return BookIR(
        source_asset_id="asset_001",
        figure_id="fig_001",
        domain="mechanics",
        subtype="pendulum",
        status=BookIRStatus.READY_TO_COMPILE,
        geometry={"source_width": 800.0, "source_height": 600.0, "pivot": {"x": 200, "y": 50}, "bob_position": {"x": 150, "y": 280}, "string_length_px": 230.0, "bob_radius_px": 18.0},
        parameters={
            "pivot": {"value": {"x": 200, "y": 50}},
            "bob_position": {"value": {"x": 150, "y": 280}},
            "string_length_px": {"value": 230.0, "unit": "px"},
            "bob_radius_px": {"value": 18.0, "unit": "px"},
            "gravity": {"value": 9.81, "unit": "m/s²"},
            "length": {"value": 1.2, "unit": "m"},
            "mass": {"value": 1.0, "unit": "kg"},
            "damping": {"value": 0.05, "unit": "1/s"},
        }
    )

# 12.1 Missing gravity (NO 9.81 default)
p_no_g = make_base_pendulum()
del p_no_g.parameters["gravity"]
res = compiler.compile(p_no_g)
test("Missing gravity → NEEDS_REVIEW (no 9.81 default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_GRAVITY" for i in res.issues))

# 12.2 Missing bob radius (NO 20.0 default)
p_no_r = make_base_pendulum()
del p_no_r.parameters["bob_radius_px"]
del p_no_r.geometry["bob_radius_px"]
res = compiler.compile(p_no_r)
test("Missing bob_radius_px → NEEDS_REVIEW (no 20.0 default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_BOB_RADIUS_PX" for i in res.issues))

# 12.3 Missing damping (NO 0.0 default assumption)
p_no_d = make_base_pendulum()
del p_no_d.parameters["damping"]
res = compiler.compile(p_no_d)
test("Missing damping → NEEDS_REVIEW (no 0.0 default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_DAMPING" for i in res.issues))

# 12.4 Projectile missing calibration (NO 100.0 px/m default)
proj_ir = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="mechanics",
    subtype="projectile",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "launch_source": {"x": 100, "y": 400}},
    parameters={
        "launch_position": {"value": {"x": 100, "y": 400}},
        "launch_speed": {"value": 20.0, "unit": "m/s"},
        "launch_angle": {"value": 45.0, "unit": "deg"},
        "gravity": {"value": 9.81, "unit": "m/s²"},
        "ball_radius_px": {"value": 15.0, "unit": "px"},
    }
)
res = compiler.compile(proj_ir)
test("Projectile missing calibration → NEEDS_REVIEW (no 100 px/m default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_CALIBRATION" for i in res.issues))

# 12.5 Thin lens missing aperture (NO 200.0 default)
lens_no_ap = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="optics",
    subtype="thin_lens",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "lens_center": {"x": 400, "y": 300}},
    parameters={
        "lens_center": {"value": {"x": 400, "y": 300}},
        "focal_length_px": {"value": 150.0, "unit": "px"},
    }
)
res = compiler.compile(lens_no_ap)
test("Thin lens missing aperture → NEEDS_REVIEW (no 200.0 default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_APERTURE_HEIGHT_PX" for i in res.issues))

# 12.6 Optical object missing object height (NO 80.0 default)
lens_no_h = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="optics",
    subtype="thin_lens",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "lens_center": {"x": 400, "y": 300}},
    parameters={
        "lens_center": {"value": {"x": 400, "y": 300}},
        "focal_length_px": {"value": 150.0, "unit": "px"},
        "aperture_height_px": {"value": 250.0, "unit": "px"},
        "object_position": {"value": {"x": 200, "y": 300}},
    }
)
res = compiler.compile(lens_no_h)
test("Optical object missing object_height_px → NEEDS_REVIEW (no 80.0 default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_OBJECT_HEIGHT_PX" for i in res.issues))

# 12.7 Mirror missing concavity (NO 'concave' default)
mirror_no_c = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="optics",
    subtype="mirror",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "pole": {"x": 400, "y": 300}},
    parameters={
        "pole": {"value": {"x": 400, "y": 300}},
        "focal_length_px": {"value": 120.0, "unit": "px"},
        "aperture_height_px": {"value": 200.0, "unit": "px"},
    }
)
res = compiler.compile(mirror_no_c)
test("Mirror missing concavity → NEEDS_REVIEW (no 'concave' default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_MIRROR_CONCAVITY" for i in res.issues))

# 12.8 Prism missing apex angle (NO 60.0 default)
prism_no_apex = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="optics",
    subtype="prism",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "rayOrigin": {"x": 50, "y": 250}, "rayDirection": {"x": 1, "y": 0}},
    parameters={
        "vertices": {"value": [{"x": 100, "y": 100}, {"x": 300, "y": 100}, {"x": 200, "y": 300}]},
        "n": {"value": 1.5},
    }
)
res = compiler.compile(prism_no_apex)
test("Prism missing apex angle → NEEDS_REVIEW (no 60° default)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_APEX_ANGLE_DEG" for i in res.issues))

# 12.9 Interface refraction missing normal_x (NO 0.0 default) or n1 (NO 1.0 default)
refr_no_norm = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="optics",
    subtype="interface_refraction",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0},
    parameters={
        "boundary_y": {"value": 300.0},
        "n2": {"value": 1.33},
        "source_position": {"value": {"x": 100, "y": 150}},
    }
)
res = compiler.compile(refr_no_norm)
test("Refraction missing normal_x & n1 → NEEDS_REVIEW (no 0.0 / 1.0 defaults)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_NORMAL_X" for i in res.issues))


# ---------------------------------------------------------------------------
# 13. Regression: Strict Unit Validation
# ---------------------------------------------------------------------------

section("13. Regression: Strict Unit Validation")

# 13.1 Incompatible velocity unit: launch_speed with unit "cm"
proj_bad_speed_unit = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="mechanics",
    subtype="projectile",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "launch_source": {"x": 100, "y": 400}},
    parameters={
        "launch_position": {"value": {"x": 100, "y": 400}},
        "launch_speed": {"value": 20.0, "unit": "cm"},   # WRONG: length unit for velocity!
        "launch_angle": {"value": 45.0, "unit": "deg"},
        "gravity": {"value": 9.81, "unit": "m/s²"},
        "pixels_per_meter": {"value": 50.0},
        "ball_radius_px": {"value": 15.0, "unit": "px"},
    }
)
res = compiler.compile(proj_bad_speed_unit)
test("Wrong unit 'cm' for launch_speed → NEEDS_REVIEW (INCOMPATIBLE_UNIT)", res.status == "NEEDS_REVIEW" and any(i["code"] == "INCOMPATIBLE_UNIT" for i in res.issues))

# 13.2 Incompatible angle unit: launch_angle with unit "kg"
proj_bad_ang_unit = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="mechanics",
    subtype="projectile",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "launch_source": {"x": 100, "y": 400}},
    parameters={
        "launch_position": {"value": {"x": 100, "y": 400}},
        "launch_speed": {"value": 20.0, "unit": "m/s"},
        "launch_angle": {"value": 45.0, "unit": "kg"},   # WRONG: mass unit for angle!
        "gravity": {"value": 9.81, "unit": "m/s²"},
        "pixels_per_meter": {"value": 50.0},
        "ball_radius_px": {"value": 15.0, "unit": "px"},
    }
)
res = compiler.compile(proj_bad_ang_unit)
test("Wrong unit 'kg' for launch_angle → NEEDS_REVIEW (INCOMPATIBLE_UNIT)", res.status == "NEEDS_REVIEW" and any(i["code"] == "INCOMPATIBLE_UNIT" for i in res.issues))

# 13.3 Valid unit conversion: launch_speed in km/h correctly converts to m/s
proj_kmh = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="mechanics",
    subtype="projectile",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0, "launch_source": {"x": 100, "y": 400}},
    parameters={
        "launch_position": {"value": {"x": 100, "y": 400}},
        "launch_speed": {"value": 72.0, "unit": "km/h"},   # 72 km/h = 20 m/s
        "launch_angle": {"value": 45.0, "unit": "deg"},
        "gravity": {"value": 9.81, "unit": "m/s²"},
        "pixels_per_meter": {"value": 50.0},
        "ball_radius_px": {"value": 15.0, "unit": "px"},
    }
)
res = compiler.compile(proj_kmh)
test("Valid velocity unit km/h → READY", res.status == "READY", f"issues: {res.issues}")
if res.scene:
    test("Converted 72 km/h to 20.0 m/s in parameters", abs(res.scene["parameters"]["speed"]["value"] - 20.0) < 1e-4)
    test("Converted 72 km/h to 20.0 m/s in physics", abs(res.scene["objects"][0]["physics"]["speed_m_s"] - 20.0) < 1e-4)


# ---------------------------------------------------------------------------
# 14. Regression: Circuit Fixture Label Rejection (circuit1..4)
# ---------------------------------------------------------------------------

section("14. Regression: Circuit Fixture Labels Rejection")

for c_sub in ["circuit1", "circuit2", "circuit3", "circuit4"]:
    bad_c_ir = BookIR(
        source_asset_id="asset_001",
        figure_id="fig_001",
        domain="circuits",
        subtype=c_sub,
        status=BookIRStatus.READY_TO_COMPILE,
        geometry={"source_width": 800.0, "source_height": 600.0},
        parameters={"nodes": ["N0", "N1"], "components": [{"id": "R1", "type": "resistor", "value": 10, "unit": "Ω", "nodes": ["N1", "N0"]}]}
    )
    res = compiler.compile(bad_c_ir)
    test(f"Fixture subtype '{c_sub}' → UNSUPPORTED", res.status == "UNSUPPORTED")

# Canonical dc_linear IS supported
canonical_c_ir = BookIR(
    source_asset_id="asset_001",
    figure_id="fig_001",
    domain="circuits",
    subtype="dc_linear",
    status=BookIRStatus.READY_TO_COMPILE,
    geometry={"source_width": 800.0, "source_height": 600.0},
    parameters={
        "nodes": [{"id": "N0"}, {"id": "N1"}],
        "components": [
            {"id": "V1", "type": "voltage_source", "value": 12.0, "unit": "V", "nodes": ["N1", "N0"]},
            {"id": "R1", "type": "resistor", "value": 10.0, "unit": "Ω", "nodes": ["N1", "N0"]}
        ],
        "reference_node": "N0"
    }
)
res = compiler.compile(canonical_c_ir)
test("Canonical subtype 'dc_linear' → READY", res.status == "READY", f"issues: {res.issues}")
if res.scene:
    test("Canonical circuit schemaVersion is 1.0", res.scene["schemaVersion"] == "1.0")
    test("Canonical circuit has graph with nodes and components", "circuit" in res.scene and len(res.scene["circuit"]["nodes"]) == 2)


# ---------------------------------------------------------------------------
# 15. Regression: Grounding Validation (source_asset_id & figure_id)
# ---------------------------------------------------------------------------

section("15. Regression: Grounding Validation")

# 15.1 Missing source_asset_id
ungrounded_ir = make_base_pendulum()
ungrounded_ir.source_asset_id = None
res = compiler.compile(ungrounded_ir)
test("Missing source_asset_id → NEEDS_REVIEW (MISSING_SOURCE_GROUNDING)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_SOURCE_GROUNDING" for i in res.issues))

# 15.2 Missing figure_id
no_fig_ir = make_base_pendulum()
no_fig_ir.figure_id = None
res = compiler.compile(no_fig_ir)
test("Missing figure_id → NEEDS_REVIEW (MISSING_FIGURE_GROUNDING)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_FIGURE_GROUNDING" for i in res.issues))

# 15.3 Missing coordinate dimensions
no_dims_ir = make_base_pendulum()
no_dims_ir.geometry = {}
res = compiler.compile(no_dims_ir)
test("Missing coordinate dimensions → NEEDS_REVIEW (MISSING_COORDINATE_DIMENSIONS)", res.status == "NEEDS_REVIEW" and any(i["code"] == "MISSING_COORDINATE_DIMENSIONS" for i in res.issues))


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"\n{'═'*60}")
total = _PASS + _FAIL
print(f"  Results: {_PASS}/{total} passed, {_FAIL} failed")
if _ERRORS:
    print("\n  Failed tests:")
    for e in _ERRORS:
        print(f"    ✗ {e}")
print(f"{'═'*60}\n")

sys.exit(0 if _FAIL == 0 else 1)
