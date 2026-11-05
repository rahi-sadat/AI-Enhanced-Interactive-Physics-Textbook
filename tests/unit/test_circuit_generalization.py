"""Real-image regressions with explicitly annotated semantic/OCR test doubles.

Coordinates below describe label boxes in test fixtures, never production rules.
Live model acceptance is a separate test; these cases isolate CV and resolution.
"""
from pathlib import Path
import json
from copy import deepcopy
import cv2
import pytest
from shared.schemas.ingestion import BookIR, BookEntity
from shared.schemas.evidence import OCRToken, SourceBBox, OCRExtractionResult, ExtractionStatus
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator
from ai.evidence.grounding.circuits import CircuitGrounder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.engine import ResolutionEngine
from ai.resolution.analyzer import ResolutionAnalyzer

ROOT = Path(__file__).parents[1]/"fixtures"/"circuit_generalization"
CASES = {
    "parallel_three_plate.jpeg": [
        ("V = 6 V", (25,590,195,70)), ("R1 = 10 Ω",(780,545,220,65)),
        ("R2 = 15 Ω",(1200,540,230,70)), ("Parallel Circuit",(440,60,570,195)),
        ("Battery",(28,510,190,70)), ("Fig 10 Parallel Circuit",(400,890,680,90)),
        ("I",(500,270,45,50))],
    "symbolic_single_loop.png": [
        ("R",(785,60,70,65)), ("Resistor",(705,270,220,55)),
        ("V",(165,520,60,65)), ("Battery",(460,520,245,60)), ("I",(1310,520,45,65))],
    "mixed_four_resistors.jpg": [
        ("R1 50 Ω",(450,42,195,62)), ("R2",(806,378,80,65)), ("150 Ω",(594,378,135,62)),
        ("R3",(995,378,80,65)), ("300 Ω",(1138,378,140,62)),
        ("R4",(465,682,80,60)), ("100 Ω",(435,815,140,65)), ("12 V",(48,424,120,60))],
}


def prepare(filename, *, rotate=False, scale=1, observed_ocr=False):
    image=cv2.imread(str(ROOT/filename))
    tokens=[OCRToken(id=f"text_{i}",raw_text=text,confidence=.95,bbox_source_px=SourceBBox(*box))
            for i,(text,box) in enumerate(CASES[filename])]
    if observed_ocr:
        observations=json.loads((ROOT/"observed_ocr.json").read_text(encoding="utf-8"))
        tokens=[OCRToken(id=f"text_{i}",raw_text=t["text"],confidence=t["confidence"],
                        bbox_source_px=SourceBBox(**t["bbox"]))
                for i,t in enumerate(observations["cases"][Path(filename).stem])]
    count = 4 if filename.startswith("mixed") else 2 if filename.startswith("parallel") else 1
    book=BookIR(source_asset_id=filename,figure_id="figure",domain="circuits",subtype="dc_linear",
                entities=[BookEntity(id=f"r{i}",type="resistor",label=f"R{i}") for i in range(1,count+1)]
                +[BookEntity(id="v",type="voltage_source",label="V")])
    if rotate:
        h=image.shape[0];image=cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
        for t in tokens:
            b=t.bbox_source_px;t.bbox_source_px=SourceBBox(h-b.y_max,b.x,b.height,b.width)
    if scale != 1:
        image=cv2.resize(image,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        for t in tokens:
            b=t.bbox_source_px;t.bbox_source_px=SourceBBox(b.x*scale,b.y*scale,b.width*scale,b.height*scale)
    h,w=image.shape[:2]
    candidates=CircuitCVCandidateExtractor().extract(image,source_width=w,source_height=h,
                                                    ocr_boxes=[t.bbox_source_px for t in tokens])
    checked=CircuitGeometryValidator().validate(image,candidates,source_asset_id=filename,figure_id="figure")
    result=CircuitGrounder().ground(book,checked,OCRExtractionResult(status=ExtractionStatus.SUCCESS,
                tokens=tokens,provider="annotated_test_double"),source_width=w,source_height=h)
    return result.grounded_book_ir,checked


@pytest.mark.parametrize("filename", list(CASES))
def test_supplied_drawings_ground_all_components(filename):
    book,checked=prepare(filename)
    assert book.geometry["circuit_validation"]["geometry"], (checked["validation_issues"],book.review_issues)
    assert book.geometry["circuit_validation"]["topology"], book.review_issues
    assert len(book.parameters["components"]) == len(book.entities)
    if filename.startswith("symbolic"):
        assert book.status == "NEEDS_REVIEW"
        assert PhysicsCompiler().compile(book).scene is None
        issues=ResolutionAnalyzer.analyze(book).to_dict()["issues"]
        assert {i["parameterName"] for i in issues if i["defaultPolicyId"]} >= {"component.v.value","component.r1.value"}
    else:
        assert PhysicsCompiler().compile(book).status == "READY", book.review_issues


def test_missing_values_default_or_manual_only_affect_selected_component():
    book,_=prepare("symbolic_single_loop.png")
    evidence=deepcopy(book.evidence)
    first=ResolutionEngine.apply_policy(book,"policy_standard_dc_voltage","component.v.value",True)
    assert first.success, first.error
    assert book.status == "NEEDS_REVIEW"
    resistor=next(c for c in book.parameters["components"] if c["id"]=="r1")
    assert resistor.get("value") is None
    second=ResolutionEngine.apply_resolution(book,dict(parameter_name="component.r1.value",
                resolved_value=2,canonical_unit="kΩ",resolution_source="user_supplied",user_accepted=True))
    assert second.success,second.error
    assert resistor["value"]==2000
    assert all(d["groundingState"]=="grounded" for d in book.provenance["grounding_diagnostics"])
    assert PhysicsCompiler().compile(book).status=="READY",book.review_issues
    assert book.evidence==evidence
    assert not ResolutionEngine.apply_policy(book,"policy_standard_dc_resistance","component.r1.value",True).success
    ResolutionEngine.remove_resolution(book,"component.r1.value")
    assert resistor.get("value") is None
    assert PhysicsCompiler().compile(book).scene is None
    assert ResolutionEngine.apply_policy(book,"policy_standard_dc_resistance","component.r1.value",True).success
    assert PhysicsCompiler().compile(book).status=="READY"


def test_defaults_never_replace_printed_values_or_unconfirmed_decisions():
    book,_=prepare("mixed_four_resistors.jpg")
    before=deepcopy(book.parameters)
    assert not ResolutionEngine.apply_policy(book,"policy_standard_dc_voltage","component.v.value",True).success
    assert book.parameters==before
    symbolic,_=prepare("symbolic_single_loop.png")
    assert not ResolutionEngine.apply_policy(symbolic,"policy_standard_dc_voltage","component.v.value",False).success
    assert not ResolutionEngine.apply_resolution(symbolic,dict(parameter_name="component.r1.value",
                resolved_value=-3,canonical_unit="Ω",resolution_source="user_supplied")).success


@pytest.mark.parametrize("filename", ["parallel_three_plate.jpeg","mixed_four_resistors.jpg"])
@pytest.mark.parametrize("options", [{"rotate":True},{"scale":.75},{"scale":1.25}])
def test_real_drawings_rotated_and_rescaled(filename, options):
    book,checked=prepare(filename,**options)
    assert PhysicsCompiler().compile(book).status=="READY", (checked["validation_issues"],book.review_issues)


def test_component_resolution_cannot_hide_value_tampering():
    from ai.resolution.evaluator import ReadinessEvaluator
    book,_=prepare("symbolic_single_loop.png")
    for cid,policy in [("v","policy_standard_dc_voltage"),("r1","policy_standard_dc_resistance")]:
        assert ResolutionEngine.apply_policy(book,policy,f"component.{cid}.value",True).success
    restored=BookIR.from_dict(book.to_dict())
    assert ReadinessEvaluator.evaluate(restored).ready
    restored.parameters["components"][0]["value"]*=2
    assert not ReadinessEvaluator.evaluate(restored).ready


@pytest.mark.parametrize("filename", list(CASES))
def test_actual_ocr_symbol_collisions_preserve_measured_geometry(filename):
    book,checked=prepare(filename,observed_ocr=True)
    assert book.geometry["circuit_validation"]["geometry"], checked["validation_issues"]
    assert book.geometry["circuit_validation"]["topology"], book.review_issues
    if filename.startswith("symbolic"):
        assert checked["ocr_symbol_conflicts"]
        assert all(c.get("value") is None for c in book.parameters["components"])
        result=ResolutionEngine.apply_resolution(book,dict(parameterName="component.r1.value",
            resolvedValue=100,canonicalUnit="ohm",resolutionSource="user_supplied",userAccepted=False))
        assert not result.success
    else:
        assert PhysicsCompiler().compile(book).status=="READY"
