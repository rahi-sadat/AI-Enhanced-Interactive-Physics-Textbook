# 1. Active Runtime Architecture

Real native Windows frontend at port 5173 → standard Vite proxy → native FastAPI at 8000 → existing direct Gemini SDK connection. No TLS tunnel. Four unique real browser upload requests on 2026-10-17; prior 2026-10-16 provider-503 runs are historical and do not describe these successful semantic runs.

`main.js → SimulationOrchestrator.startWithFile → SimulationApi.ingest → /api/ingest → UploadService.ingest → PageIRBuilder.build → asyncio.to_thread(BookUnderstandingPipeline.analyze → PhysicsVisionAnalyzer.analyze → GeminiVisionProvider.analyze_diagram → Models.generate_content) → EvidenceExtractionPipeline.extract_and_fuse → MultiOCRRouter.extract → domain CV → optional SAM2 bob segmentation → domain Grounder → enforce_source_dimensions → AutoResolutionEngine.resolve → ResolutionEngine.auto_resolve / ReadinessEvaluator.evaluate → ai/ingestion/PhysicsCompiler.py → response → orchestrator → InteractiveFigure.load → FigureViewport / PhysicsRuntime.normalizeScene / load → domain adapter → solver → actual renderer.`

`ai/scene_compiler/physics_compiler.py` is a re-export; compiler execution is in `ai/ingestion/PhysicsCompiler.py`. Mechanics uses MechanicsAdapter/PendulumSimulation; optics uses registry SVG renderers. main.js automatically calls startSimulation after successful load in this executed path. Circuit follows NEEDS_REVIEW → review API → an attempted compile → HTTP 400 → ERROR. No circuit solver runs.

Every backend call has file/function/caller/next observed calls, saved function contract and exact before/after artifacts in its STAGE.html. Frontend event boundaries and full actual DOM/runtime captures are linked per case.

# 2. Trace Results — Diagram 1: Convex lens

[TRACE-LENS-20261016-001-NATIVE-RETRY-20261017](../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/TRACE_REPORT.html)

Last known good: Source identity, semantic subtype and selected OCR focal-length text (15 cm).

First suspicious: Secondary OCR misreads the focal label; router retains the correct RapidOCR result. The Object OCR box (188,220,135,57) is valid text evidence, but its four-pixel expansion reaches adjacent ray geometry.

First definitive failure: OCR edge masking erases part of the incident ray beside the Object label; CV subsequently omits the printed object arrow and selects a partial lens centerline.

Returned lens_center=(641,432), lens_line=(641,423)→(641,189), object_arrow=null. The partial line becomes aperture_height_px=234. The original shows an object arrow and a full lens; the selected overlay exposes this loss.

Grounder retains the center/partial aperture and observes focal_length=0.15 m from OCR, but does not ground the object or printed focal-marker spacing.

_normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace.

Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

Thin-lens runtime returns u=234, v=234, magnification=−1. No numerical solver defect is established. The actual t=0 renderer makes already incorrect source geometry visible.

# 3. Trace Results — Diagram 2: Series DC circuit

[TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017](../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/TRACE_REPORT.html)

Last known good: Exact source, semantic dc_linear classification and OCR 12 V / 10 Ω / 20 Ω.

First suspicious: Raw line candidates include the current annotation shaft and open-switch arm as wire candidates.

First definitive failure: CV promotes fragmented evidence into full horizontal rails across source gaps and empty interior.

components=[]; branches_x=[231,992]; rails_y=[255,416,668]. Returned rails span x=231→992 at all three Y values. y=416 crosses empty circuit interior; y=255 bridges the open switch/components. The implementation accepts a span with more than ten edge pixels, without requiring continuous wire support.

CircuitGrounder creates R2 at (1149,416), with horizontal terminals (1115,416)/(1183,416), near the OCR label instead of the vertical resistor. It creates R1=(757,255), V1=(231,457), but nodes and component node lists are empty. Renaming semantic entity IDs to R1/R2/V1 leaves old relationship endpoints dangling. The switch is not grounded.

Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit.

Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

Circuit solver/MNA, uploaded-scene renderer and t=0 overlay NOT EXECUTED. Do not interpret startup/demo state as this uploaded circuit. No current result exists.

# 4. Trace Results — Diagram 3: Simple pendulum

[TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017](../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/TRACE_REPORT.html)

Last known good: Exact source, correct semantic pendulum roles and symbolic OCR; no printed numeric length/mass is claimed.

First suspicious: Selected visible string begins at (556,67), extending into the mounting hatch region.

First definitive failure: CV accepts a pivot above the detected support while reporting the disagreement in its own validation metadata.

Selected pivot=(562,79.23811193908072), bob=(841.3633806409911,649.0514992664916), radius=37.03476174228877. Method vertical_reference_intersection reports support_residual_px=16.761888060919276 yet is_geometrically_consistent=true. The consistency predicate checks vertical-reference and string residuals but omits support_residual. The source and selected overlay show the misplaced mounting point.

SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px.

Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale.

Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

MechanicsAdapter → PendulumKernel / PendulumSimulation. t=0 bob is source-aligned while pivot is above the printed support. No integration defect is established; physical time-scale accuracy has no numeric source ground truth.

# 5. Trace Results — Diagram 4: Glass prism

[TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017](../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/TRACE_REPORT.html)

Last known good: Exact source, correct prism semantics and OCR A=60°. Raw edges before OCR suppression retain the source boundaries.

First suspicious: The axis-aligned A=60° OCR box (556,184,128,49) and its four-pixel expansion intersect the slanted prism boundary. Later contour detection yields best_area=0; rays also includes body edges and normals.

First definitive failure: OCR edge masking erases prism-side pixels around A=60°; CV then infers an incorrect base from sloped-segment extents.

Fallback left_max_y=771 and right_max_y=743 yield base_y=(771+743)/2=757. Actual horizontal base candidates remain around y=766–773 in the same output. Returned vertices are (621.3,80.9),(229.2,757),(1003.9,757). The selected polygon visibly lies above the printed base. Incident segment (47,456)→(237,420) is retained correctly.

Grounder preserves polygon and incident ray, records OCR apex angle=60°, but does not ground internal/emergent ray entities. Raw detected ray segments remain in evidence, not constraints for the runtime solution.

A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray.

Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

Optics runtime reports incidence=40.842553023013416°, refraction=25.48353691375652°, deviation=39.754070946628936°, no TIR. Exact solver output and actual SVG are saved.

# 6. Coordinate Transformation Audit

Original JPEGs and lossless original.png are 1280×960, no EXIF orientation; source bytes match the upload and the SDK inline image for every request. Application geometry uses source_px, origin top-left, X right, Y down. No application crop/resize offset was introduced. Model-internal transforms remain unavailable.

Measured t=0 lens image/SVG rectangle=(139,227,800,600), mapper scale=.625. Pendulum image/canvas and prism image/SVG rectangle=(219,227,640,480), scale=.5. DPR=1; viewBox=0 0 1280 960 for optics. Source-to-overlay is (s*x,s*y); source-to-browser adds the measured image origin. Inverse mapping is captured by actual CoordinateMapper.viewToSource, with full precision per landmark in coordinate_audit.json. No manual alignment or changed solver coordinates.

Pendulum pivot stays (562,79.23811193908072) through CV, grounding, compiled scene and runtime. The runtime bob is (841.3629149366802,649.0505493762439); the original CV bob differs only by rounding the stored length. Lens center stays (641,432), while object base/tip are created by policy/compiler. Prism vertices stay unchanged from CV to scene to SVG. Circuit has no source-matched browser mapper/solver; no startup demo evidence is substituted.

The existing mapper correctly places the supplied points in all three runnable cases. This does not validate those points against the textbook. Private preprocessing tensors and native screen-pixel/browser-chrome coordinates: EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS.

# 7. First-Failure Table

| Diagram | First definitive component | Failure class | Downstream consequence |

|---|---|---|---|

| Lens | mask_out_text_regions, followed by ThinLensCVCandidateExtractor.extract | A preprocessing/perception, then assumption-based reconstruction | OCR margin erases ray pixels; CV misses object/partial aperture → assumed placement → wrong t=0 rays |

| Circuit | CircuitCVCandidateExtractor.extract | A perception/topology | False rails → misplaced component terminals / missing graph → readiness blocks |

| Pendulum | PendulumCVCandidateExtractor.extract_candidates | A perception | Pivot fails support agreement → copied into IR/scene → displaced mounting point |

| Prism | mask_out_text_regions, followed by PrismCVCandidateExtractor.extract | A preprocessing/perception, then model re-synthesis | OCR masking removes side pixels; side-extents inference shifts base; assumed n yields different ray |

# 8. Cross-Diagram Root Cause

No single shared CSS-coordinate defect is established. Lens and prism share demonstrated geometric edge loss in OCR masking. Masked-out pixels are shown directly on each original; causality from that loss to every later detector error is not established. Every case has domain-specific classical CV selection or reconstruction failure. The earliest demonstrated lens information loss is OCR edge masking, before those CV selections; its causal connection to the missing object arrow is not proven. Semantic classification succeeds for all four; these traces do not support blaming Gemini classification for the geometry. Grounding propagates weak geometry and, for circuits, introduces additional wrong placement and dangling relationship IDs.

Mechanics-only: support residual is recorded but excluded from pivot consistency. Optics-only: lens physical OCR focal length loses authority to an uncalibrated pixel policy; prism observed internal/emergent rays are not runtime constraints. Circuit-only: synthetic rails, empty topology, label-driven component placement and relationship mismatch.

Shared readiness weakness across the three runnable cases: checks concern required values, units/ranges, provenance and unresolved issues; they do not establish pixel registration. Auto-policy may satisfy requirements without human acceptance. Circuit topology is correctly blocked. Shared frontend issue observed: automatic simulation activation; circuit attempts compile after NEEDS_REVIEW and surfaces an error.

Compiler preserves already-wrong geometry or creates model geometry from assumptions. No independently proven C-class numerical solver defect. Source physical ground truth for mass/length/index is absent; behavior correctness cannot be inferred from animation alone.

# 9. Evidence

Full HTML reports above contain stage overlays, input/output JSON, arrays/masks, contracts, provenance, deltas, source SHA chains and actual runtime screenshots. Every new trace remains under `../20261016/<trace>-NATIVE-RETRY-20261017/`; date in directory is the recorder session root, not a claim that these requests ran on October 16.

Per trace: `00_source/original.jpg`, `original.png`, `metadata.json`; `calls/<sequence_component>/actual_input.json`, `actual_output.json`, `locals_after.json`, `contract_or_schema.txt`, `STAGE.html`, overlays; `arrays/*.npy`; `http/`; `15_browser/events.json`, final_state and runtime frames; `14_renderer/coordinate_audit.json`, actual SVG/canvas and runtime_t0_overlay.png where compiled. Auto-resolution has field_changes.json; compiler has ir_to_scene.json. Full stage_landmark_chain.json retains values before and after all key boundaries.

Coverage limitations: profiler did not intercept internal C/neural-library operations or every JS function. Original and application boundary arrays are preserved; unavailable private tensors and transforms are explicitly not reconstructed. Two recorder errors during class serialization are retained in the raw log; major stage I/O exists. No arbitrary expected diagram or numerical ground truth was authored. Later-frame timestamps are actual saved state, not exact requested 0.5/1.0 seconds. The source itself is the sole visual reference.

Verification: prior unchanged production working tree passed frontend 17 test commands and Python unit/integration 247 tests. Those were offline, separate from explicitly live acceptance traces. No production fix, parameter correction or physics algorithm change was made. Existing user changes remain untouched.

# 10. Root Cause Ranking

1. Strongest: CV output contradicted by source and/or its own candidates: circuit fabricated spans; pendulum ignored support residual; prism averaged side endpoints into an unsupported base; lens missing object/partial lens.

2. Strong: lens auto-policy reconstructs printed geometry; circuit grounding misplaces R2 and invalidates relationship references.

3. Strong: readiness admits complete, provenance-bearing values without a source-registration check.

4. Strong mechanism, limited physical ground truth: prism ray re-synthesis from assumed refractive index and incomplete observed constraints.

5. Downstream UX: circuit compile attempt despite NEEDS_REVIEW; automatic activation.

6. Not supported as root cause by these captures: shared CSS/mapper shift, DPR mismatch, Gemini domain misclassification, or numerical integrator/Snell/MNA implementation defect.

[Open the HTML evidence index](../../storage/generated/debug_traces/20261017/INDEX.html).
