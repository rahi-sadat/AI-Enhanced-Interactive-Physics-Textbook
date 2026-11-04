"""Opt-in circuit experiment. Guessed previews never become source evidence."""
from copy import deepcopy
from time import perf_counter

from ai.evidence.transforms import load_and_validate_source_image
from ai.ingestion.source_dimensions import enforce_source_dimensions
from ai.resolution.auto import AutoResolutionEngine
from ai.resolution.engine import ResolutionEngine
from shared.schemas.ingestion import BookEntity, BookIR, BookIRStatus


def make_preview(detections, asset, image_url):
    """An explicitly assumed series loop for inspecting detector output in motion.

    This is deliberately separate from compilation and BookIR. Detector boxes
    cannot establish electrical terminals, connectivity, or physical values.
    """
    assumptions = [
        {"parameter": "topology", "reason": "Experimental series loop; connections are guessed, not measured."},
        {"parameter": "geometry", "reason": "Terminals are estimated from detector boxes, not verified CV geometry."},
    ]
    proposals = [(d.kind, d.bbox.to_dict()) for d in detections]
    # Keep a visible educational stand-in even when the detector returns nothing.
    # Its identity is explicit and it is never reported as a detected component.
    for kind, x in (("voltage_source", .2), ("resistor", .65)):
        if not any(k == kind for k, _ in proposals):
            proposals.append((kind, dict(x=asset.width_px*x, y=asset.height_px*.45,
                                        width=asset.width_px*.08, height=asset.height_px*.08)))
            assumptions.append({"parameter": kind, "reason": f"Added synthetic {kind} for preview only; model did not detect one."})
    components, parameters, wires = [], {}, []
    units = {"resistor": "ohm", "voltage_source": "V", "capacitor": "F", "switch": "ohm"}
    defaults = {"resistor": 10., "voltage_source": 5., "capacitor": 1e-4, "switch": 0.}
    count = len(proposals)
    for i, (kind, box) in enumerate(proposals):
        cid = f"preview_{kind}_{i+1}"
        x, y, w, h = (box[k] for k in ("x", "y", "width", "height"))
        points = [[x, y+h/2], [x+w, y+h/2]] if w >= h else [[x+w/2, y], [x+w/2, y+h]]
        nodes = [f"N{i}", f"N{(i+1)%count}"]
        provenance = {"source": "experimental_assumption", "verified": False,
                      "reason": "Preview-only defaults; not extracted from the diagram."}
        comp = dict(id=cid, type=kind, label=cid, nodes=nodes, value=defaults[kind], unit=units[kind],
                    editable=True, state="closed", initial_voltage=0,
                    provenance=deepcopy(provenance), value_provenance=deepcopy(provenance),
                    geometry={"bbox_source_px": [x,y,x+w,y+h], "center_source_px": [x+w/2,y+h/2]},
                    terminals=[dict(id=f"{cid}.t{j}", node=nodes[j], source_px=points[j]) for j in range(2)])
        components.append(comp)
        assumptions.append(dict(parameter=cid, value=defaults[kind], unit=units[kind],
                                reason="Experimental value; switches start closed, capacitors start at 0 V."))
        if kind != "switch":
            parameters[cid] = dict(value=defaults[kind], unit=units[kind], editable=True, min=1e-9,
                                   max=max(defaults[kind]*10,.01), step="any", label=cid,
                                   provenance="experimental_assumption")
    for i, comp in enumerate(components):
        nxt = components[(i+1)%count]
        wires.append(dict(id=f"preview_wire_{i}", node=comp["nodes"][1],
                          points=[comp["terminals"][1]["source_px"], nxt["terminals"][0]["source_px"]],
                          currentReference={"componentId": comp["id"], "sign": 1},
                          provenance="experimental_assumption"))
    return dict(schemaVersion="1.0", id="EXPERIMENTAL-CIRCUIT-V2", domain="circuits", subtype="dc_linear",
                title="EXPERIMENTAL: guessed circuit — inspect assumptions",
                source={"image": image_url, "width": asset.width_px, "height": asset.height_px},
                coordinateSpace={"type": "source_px", "width": asset.width_px, "height": asset.height_px, "unit": "px"},
                parameters=parameters, assumptions=assumptions, objects=[], geometry={},
                metadata={"experimental": True, "verified": False},
                circuit={"reference_node": "N0", "nodes": [f"N{i}" for i in range(count)],
                         "components": components, "wires": wires})


def run_experiment(data, filename, mime_type, services):
    """Run the real local model, grounding, resolution and compiler, with traces."""
    upload, pages, understanding, evidence, compiler = services
    stages, detections = [], []
    result = {"stages": stages, "scene": None, "preview_scene": None, "book_ir": None}

    def stage(name, operation):
        start = perf_counter()
        record = {"stage": name, "status": "running"}
        stages.append(record)
        try:
            value = operation()
            record["status"] = "passed"
            return value
        except Exception as error:
            record.update(status="failed", error_type=type(error).__name__, message=str(error))
            raise
        finally:
            record["duration_ms"] = round((perf_counter()-start)*1000, 2)

    asset = stage("upload", lambda: upload.ingest(data, filename, mime_type))
    url = upload.get_public_url(asset)
    result.update(image_url=url, source_asset=asset.to_dict())
    try:
        page = stage("page", lambda: pages.build(asset, url))
        detector = understanding._circuit_detector
        if detector is None:
            from ai.perception.circuits.circuit_v2 import CircuitV2Detector
            detector = CircuitV2Detector()
        import hashlib
        result["model"] = {"name": "circuit_v2", "checkpoint": str(detector.checkpoint),
                           "sha256": stage("checkpoint", lambda: hashlib.sha256(detector.checkpoint.read_bytes()).hexdigest())}
        detections = stage("detection", lambda: detector.predict(load_and_validate_source_image(asset)))
        result["detections"] = [dict(kind=d.kind, confidence=d.confidence, bbox=d.bbox.to_dict()) for d in detections]
        if not detections:
            stages[-1].update(status="blocked", message="No circuit symbols detected at confidence >= 0.25.")
        book = BookIR(source_asset_id=asset.id, page_ir_version=page.version,
                      figure_id=page.figures[0].id if page.figures else None,
                      domain="circuits" if detections else None, subtype="dc_linear" if detections else None,
                      status=BookIRStatus.NEEDS_REVIEW if detections else BookIRStatus.UNRESOLVED,
                      entities=[BookEntity(id=f"det_{d.kind}_{i}", type=d.kind,
                                           attributes={"circuitV2BBox": d.bbox.to_dict(), "confidence": d.confidence, "source": "circuit_v2"})
                                for i,d in enumerate(detections,1)],
                      provenance={"pipeline":"circuit_v2", "model":"circuit_v2", "classification":"supported" if detections else "unknown"})
        result["book_ir"] = book.to_dict()
        book = stage("grounding", lambda: evidence.extract_and_fuse(asset=asset, page_ir=page, book_ir=book))
        result["book_ir"] = book.to_dict()
        ocr = book.provenance.get("ocr_diagnostics")
        if ocr:
            stages.append({"stage": "ocr", "status": "passed" if ocr["status"] == "success" else "warning",
                           "duration_ms": 0, "message": f"{ocr['provider']}: {ocr['status']}; {ocr['token_count']} tokens. {ocr.get('error') or ''}"})
        if book.provenance.get("cv_error"):
            stages.append({"stage": "classical_cv", "status": "failed", "duration_ms": 0,
                           "message": book.provenance["cv_error"]})
        checks = (book.geometry or {}).get("circuit_validation", {})
        for key in ("semantic", "geometry", "topology", "referential_integrity"):
            if key in checks:
                stages.append({"stage": f"{key}_validation", "status": "passed" if checks[key] else "blocked",
                               "duration_ms": 0, "message": f"Grounder {key} check: {checks[key]}",
                               "issues": deepcopy(book.review_issues) if not checks[key] else []})
        stage("source_dimensions", lambda: enforce_source_dimensions(book, asset))
        auto = stage("resolution", lambda: AutoResolutionEngine.resolve(book))
        stage("readiness", lambda: ResolutionEngine.auto_resolve(book))
        result.update(book_ir=book.to_dict(), grounding=book.provenance.get("grounding_diagnostics", []),
                      auto_failures=auto.failures)
        compiled = stage("compilation", lambda: compiler.compile(book))
        result["compiler"] = compiled.to_dict()
        result["scene"] = compiled.scene
        if compiled.status != "READY":
            stages[-1].update(status="blocked", issues=compiled.issues,
                              message=f"Compiler returned {compiled.status}.")
    except Exception:
        # The failed record carries the actual exception and stage. Keep earlier
        # evidence available and still offer the expressly requested preview.
        pass
    result["preview_scene"] = stage("experimental_preview", lambda: make_preview(detections, asset, url))
    result["first_blocker"] = next((s for s in stages if s["status"] in {"blocked", "failed"}), None)
    return result
