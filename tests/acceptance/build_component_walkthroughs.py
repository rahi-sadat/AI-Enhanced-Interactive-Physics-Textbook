"""Ordered, diagram-specific debugging manuals from existing live trace evidence.

Does not invoke a provider, detector, solver, or application. Expected behavior is
explicitly a repository contract or a qualitative reading of the original image.
"""
import html
import json
from pathlib import Path
from collections import defaultdict
import re
from build_pipeline_trace_report import ROOT, RAW, OUT, CASES, read, dump, link, delta

DEST=ROOT/'docs/reports/pipeline_walkthroughs_20261017'
UNKNOWN='EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS'
E=lambda x:html.escape(str(x))

SOURCE_EXPECTATIONS={
 'LENS':('optics / thin_lens',
  'A convex lens, horizontal principal axis, upright object to the left between F and 2F, inverted enlarged image to the right beyond 2F, focal markers and principal rays. Printed f=15 cm.',
  '15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.',
  'Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.',
  'At t=0 the object should occupy its printed arrow and the image/rays should be compared to the printed image/rays. The actual solver returns real_same_size from assumed u=2f, whereas the source depicts an enlarged image. This demonstrates an input/model mismatch, not an arithmetic failure.'),
 'CIRCUIT':('circuits / dc_linear',
  'A 12 V battery with polarity marks, an OPEN switch S, R1=10 Ω on the top branch, R2=20 Ω on the right vertical branch, connecting wires and a current-direction annotation.',
  '12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.',
  'Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.',
  'Compilation should remain blocked while topology/switch state is ungrounded. A hypothetical corrected ideal open-switch model would have no conducting loop, but that is not a solver output from this trace. Do not present a closed-switch 0.4 A result as actual output.'),
 'PENDULUM':('mechanics / pendulum',
  'A fixed mounting point on a horizontal support, a string to a bob displaced to the right, a vertical reference, and symbolic θ, L and m labels.',
  'The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.',
  'The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.',
  'At t=0 pivot and bob should register to their printed locations. Motion should pivot around that fixed point. No exact period can be asserted from the symbolic source alone.'),
 'PRISM':('optics / prism',
  'A triangular glass prism with A=60°, an incident ray, internal and emergent rays, face normals, and symbolic incidence/refraction/emergence/deviation angles.',
  '60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.',
  'Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.',
  'At t=0 the prism polygon and ray segments should be compared with the printed paths. If a physical model with assumed n disagrees with the schematic, expose that disagreement; do not claim the computed path is observed source geometry.')}

# Logical data-flow order, not profiler function-entry order. Parent functions may
# enclose several later stages and return only after their children finish.
STAGES=[
 ('upload','Browser selects the original diagram','event:SimulationOrchestrator.startWithFile',
  'An unchanged image File selected by the user. Identity is the recorded filename, byte count and SHA-256.',
  'One upload operation: first UPLOADING, then a response-governed final state. This outer async call spans the rest of the pipeline; it must not invent a scene locally.',
  'File → multipart request. The generic JS File snapshot is {}, so use multipart metadata and the byte-exact source, not {} as evidence of an empty file.'),
 ('http_in','HTTP request reaches /api/ingest','http',
  'POST multipart/form-data with the same image bytes and X-Physics-Trace-ID.',
  'A parsed UploadFile passed to ingestion. Request transport must not resize or re-encode the source.',
  'Browser transport → FastAPI handler. Handler parameter is opaque in the profiler; saved multipart bytes are the authoritative payload.'),
 ('asset','Upload persistence and dimension decoding','UploadService.ingest',
  'Original encoded JPEG bytes, filename and MIME type from the upload.',
  'SourceAsset with storage path/public URL, content hash, native decoded dimensions and original filename.',
  'Encoded bytes are persisted; metadata and an asset ID are added. This is not object detection.'),
 ('page','PageIR / whole-figure coordinate frame','PageIRBuilder.build',
  'The verified SourceAsset for this image.',
  'Full-image region/figure in source_px, width=1280, height=960, top-left origin. No invented crop or landmark coordinates.',
  'SourceAsset → PageIR. The whole image is user-supplied; confidence in that extent does not imply confidence in physics landmarks.'),
 ('vlm','Actual Gemini request and response','Models.generate_content|GeminiVisionProvider.analyze_diagram',
  'The same encoded image, semantic prompt, configured model and response schema. Credentials are redacted.',
  'Semantic classification, domain/subtype, entity roles and relationships. Numerical physical parameters and authoritative geometry must not originate here.',
  'Image → model response. SDK/provider-internal preprocessing and private tensors were not exposed; no transform is invented for them.'),
 ('semantic','Semantic validation, confidence caps and thresholds','validate_semantic_payload|PhysicsVisionAnalyzer._apply_thresholds|PhysicsVisionAnalyzer.analyze',
  'The actual raw provider response, including its confidence values and declared entity IDs.',
  'Supported domain/subtype pairing, native boolean isPhysics, bounded finite confidence and valid relationship references. Approximate VLM boxes remain non-authoritative.',
  'Raw semantic response → validated semantic representation. Compare raw_provider confidence with the capped accepted values.'),
 ('book','Initial semantic BookIR','BookUnderstandingPipeline._build_book_ir_from_result|BookUnderstandingPipeline.analyze',
  'Validated semantic result plus the SourceAsset/PageIR identity.',
  'BookIR with semantic entities and evidence references, but null authoritative positions/geometry until CV/OCR grounds them. Missing numbers remain missing.',
  'Semantic roles are assigned durable entity IDs. This BookIR is an intermediate hypothesis, not a runnable simulation.'),
 ('route','Evidence dispatch and source decode','GrounderRegistry.find_grounder|load_and_validate_source_image',
  'Supported domain/subtype, semantic BookIR, SourceAsset and PageIR.',
  'The matching subtype grounder and the unchanged native BGR image array; decoder dimensions must match the asset.',
  'The pipeline routes to the domain module. Other grounders may execute supports() checks; their ground() methods are not thereby executed.'),
 ('rapid','RapidOCR: first text/box observations','RapidOCRProvider.extract',
  'Native image array and source dimensions, with any region transform explicit.',
  'Observed strings, confidence, source-space polygons/boxes and recognizer metadata. Text recognition alone does not locate the physical component represented by a label.',
  'Image → text candidates. Inspect exact source boxes; a correct string can still have a box overlapping diagram geometry.'),
 ('easy','EasyOCR: independent OCR candidates','EasyOCRBanglaProvider.extract',
  'The same source image and dimensional contract.',
  'Independent text alternatives with confidence and source positions; uncertain alternatives should not silently overwrite stronger evidence.',
  'Alternative OCR supplies competing evidence. Its errors are distinct from whichever result the router actually selects.'),
 ('ocr','Symbol candidates, deduplication and final OCR','GreekSymbolVisualOCR.extract_symbols|PhysicsSymbolCandidateResolver.enrich_token|deduplicate_spatial_tokens|MultiOCRRouter.extract',
  'Provider token candidates, spatial overlap information and symbol alternatives.',
  'Merged tokens with retained provenance/alternatives. Preserve literal printed values and symbolic quantities. Do not turn L or m into a numerical length or mass.',
  'OCR alternatives → selected token set. PageIR text blocks are filled from these tokens inside the evidence pipeline.'),
 ('pre','Grayscale, blur and edge extraction','preprocess_diagram',
  'Native BGR array and actual Canny/blur settings.',
  'Grayscale/blur/edge arrays in the same 1280×960 source frame. Image processing may change intensities, but must not imply a spatial crop/scale that was not performed.',
  'Color/intensity information becomes an edge representation. Exact arrays are retained. OpenCV internal per-operation frames were not separately profiled.'),
 ('mask','OCR-region suppression before geometry detection','mask_out_text_regions',
  'Actual edge map, selected OCR boxes and margin_px.',
  'An edge map suppressing text while preserving relevant diagram boundaries/rays. This is the registration requirement; the implementation zeros the entire expanded rectangle without distinguishing text from geometry.',
  'Every pixel removed by the actual mask is shown in red on the original. A valid OCR box does not guarantee safe geometry suppression.'),
 ('cv','Domain CV: raw candidates → selected geometry','CV',
  'Image/edge evidence and OCR boxes in source pixels, with no hand-authored landmarks.',
  'Source-supported candidate lines/circles/polygons and selected geometry, with scores, rejection/selection diagnostics and unresolved ambiguity where evidence is insufficient.',
  'Candidate generation and selection are distinct. Compare all_candidates_overlay with selected output; inspect locals for fitted lines, rejected candidates and thresholds.'),
 ('sam','SAM2 segmentation prompted by CV','SAM2SegmentationProvider.segment',
  'Source image plus the actual CV-provided box/point prompts, with prompt provenance.',
  'Segmentation mask, score, centroid, area and source bbox. Segmentation only supports the prompted object; it cannot certify unrelated geometry.',
  'This active implementation invokes SAM2 only when a best_proposal.bob exists. Absence in optics/circuits is NOT EXECUTED, not a segmentation failure.'),
 ('ground','Semantic-to-spatial grounding and parameter binding','GROUND',
  'Semantic BookIR plus raw CV candidates, OCR result and optional segmentation result.',
  'Entities bound to supported source geometry; numeric OCR values attached to the correct entity with units/evidence; relationships still resolve after any entity changes. Unresolved evidence stays unresolved.',
  'This is where semantic roles become authoritative source coordinates. Inspect grounded_book_ir, diagnostics, candidate_parameters and associations separately.'),
 ('fused','Grounded BookIR and OCR-enriched PageIR','EvidenceExtractionPipeline.extract_and_fuse',
  'Original SourceAsset/PageIR and initial semantic BookIR at entry; child stages provide OCR, CV, SAM and grounder results.',
  'Grounded BookIR and PageIR text blocks with original source identity, native dimensions and evidence provenance intact.',
  'The wrapper returns after stages 8–16. Its entry record comes earlier in the profiler, but its output belongs here in the data-flow story.'),
 ('dimensions','Enforce authoritative source dimensions','enforce_source_dimensions',
  'Grounded BookIR and the actual source dimensions.',
  'Consistent source width/height/frame metadata. Existing landmark positions must not be rescaled to unrelated viewport dimensions.',
  'Metadata enforcement is not geometric validation. Mutation is recorded in locals_after when the function returns None.'),
 ('auto','Automatic resolution and explicit policy values','AutoResolutionEngine.resolve',
  'Grounded but possibly incomplete BookIR, including missing values and provenance.',
  'Resolutions/assumptions/failures with honest evidentiary sources. For this debugging objective, an assumed exploration value must not be mistaken for a source observation or a successful registration.',
  'Inspect field_changes.json for every addition/replacement. Auto-policy execution in this checkout may satisfy requirements without a human decision; that is observed behavior, not approval supplied during tracing.'),
 ('calibration','Resolution decisions, units and calibration','ResolutionEngine.apply_resolution|ResolutionEngine.auto_resolve|CalibrationEngine.derive_for_subtype|CalibrationEngine.derive_calibration',
  'Grounded values, policy resolutions, units and any supported pixel/physical-length pairs.',
  'Consistent resolved units and explicit calibration provenance. A scale derived using assumed physical length must remain assumption-derived; it is not measured ground truth.',
  'Several calls can occur inside auto-resolution. Exact invocation records are kept separately; null return can mean calibration was unavailable, not that a zero scale was measured.'),
 ('requirements','Requirement and ambiguity analysis','ResolutionAnalyzer.analyze|ResolutionAnalyzer._check_geometry_requirements|ResolutionAnalyzer._check_parameter_requirements|ResolutionAnalyzer._check_circuit_components',
  'Resolved BookIR and subtype-specific ModelRequirementSpec.',
  'Satisfied/missing requirements, issues, blockers and warnings consistent with available evidence. Visual correctness and mere field presence must be evaluated separately.',
  'The current analyzer checks required entities/parameters and ambiguity. It does not compare every proposed line or point to image pixels.'),
 ('readiness','Readiness decision','ReadinessEvaluator.evaluate',
  'BookIR, analyzer issues, parameter values, units/ranges and resolution provenance.',
  'READY_TO_COMPILE only when implemented invariants pass; missing/invalid topology should block. For faithful reconstruction, passing these invariants must not be interpreted as proof of source registration.',
  'All repeated evaluations are recorded. Use the final pre-compile decision as the gate, while retaining earlier decisions to see state changes.'),
 ('gate','PhysicsCompiler entry and gate','PhysicsCompiler.compile',
  'The actual resolved BookIR received by the compiler.',
  'A typed failure with scene=null when not ready, or a canonical PhysicsScene with source identity, units and provenance. Never manufacture an executable scene from a blocked case.',
  'The active compiler implementation is ai/ingestion/PhysicsCompiler.py. The scene_compiler module re-exports it.'),
 ('compile','Canonical scene construction and schema validation','PhysicsCompiler._build_canonical_scene|POPULATE|PhysicsCompiler._preserve_parameter_provenance|validate_canonical_scene',
  'Validated BookIR and an initially empty canonical scene structure.',
  'Domain scene objects, parameters and geometry that preserve evidence/provenance and source frame. If model geometry is reconstructed, distinguish it from observed geometry.',
  'Populate methods mutate scene in place and return None. Their real output is locals_after.scene and the enclosing compile result. None is not a failed scene.'),
 ('response','API response delivered to the browser','ingest_diagram',
  'Completed ingestion, evidence, resolution and compilation results.',
  'A response whose status, scene, BookIR and readiness agree, correlated to this source and trace. HTTP 200 does not itself mean a simulation is ready.',
  'This is the handler return, after nested work. Exact HTTP status/body are retained separately from the Python object.'),
 ('orchestrator','Frontend receives result and selects next state','event:SimulationOrchestrator._normalizeSceneBackground|event:SimulationOrchestrator._setState',
  'The actual API response for this upload, not the startup demo scene.',
  'Preserved source URL/frame and readiness-governed state. Needs-review cases should expose review issues without falsely activating an uploaded simulation.',
  'Only events after startWithFile for this trace are used here. Startup/demo events remain in the raw log but are excluded from this diagram’s runtime evidence.'),
 ('review','Review / explicit compile request branch','review_book_ir|compile_resolved|event:SimulationOrchestrator.compile',
  'A needs-review BookIR and subsequent actual browser review/compile requests, if any.',
  'Review should list blockers; compile must reject unresolved evidence and keep scene=null. No synthetic user corrections are supplied in this trace.',
  'This branch executes for the circuit. Its rejection is an expected backend gate; the unnecessary frontend compile attempt is a separate issue.'),
 ('figure','InteractiveFigure receives the compiled scene','event:InteractiveFigure.load',
  'The source-matched canonical scene approved by the backend.',
  'A figure bound to the original image, with the correct domain runtime and an initial rendered output. No unrelated demo geometry.',
  'load performs layout/runtime initialization internally. The t0 event immediately after load is an observed snapshot; exact child JS calls were not all instrumented.'),
 ('background','FigureViewport background and layout','event:FigureViewport.setBackground|event:FigureViewport.recalculate',
  'Original source URL, natural width/height and measured viewport bounds.',
  'The source image displayed with an aspect-preserving transform shared by its overlay. Letterboxing belongs to the viewport, not to native geometry.',
  'Preserve source_px. The measured image rectangle and mapper offsets are shown in the coordinate stage; CSS pixels are not substituted into BookIR.'),
 ('runtime','PhysicsRuntime normalization and adapter initialization','event:PhysicsRuntime.normalizeScene|event:PhysicsRuntime.load',
  'Source-matched scene and figure/container options.',
  'Validated normalized scene, resolved capabilities, matching adapter and initialized runtime. Normalization must not erase provenance or relocate source points.',
  'Registry/capability/adapter child calls are established by runtime source and captured boundary/output. Their independent entry/exit arguments were not recorded; they are not presented as new trace snapshots.'),
 ('solver','Domain solver and actual initial state','solver',
  'The actual scene-derived model parameters, source geometry and any explicit policy values.',
  'Mathematically consistent state/output for those inputs. Correct computation is separate from whether those inputs reconstruct this diagram.',
  'Scene/state/output are actual captures. Exact internal solver-call argument objects were not individually intercepted; no replay or hand-computed replacement is labeled as runtime evidence.'),
 ('mapper','CoordinateMapper: source → overlay → browser','mapper',
  'Native source coordinates, source dimensions, viewport dimensions, DPR and image rectangle.',
  'Invertible mapping with the same image/overlay scale and offsets. Applying viewToSource(sourceToView(p)) should recover the supplied point within floating-point precision.',
  'sourceToView includes viewport letterboxing; sourceToOverlay omits it because the overlay is already image-aligned. Browser coordinates add the measured image origin. Do not add letterboxing twice.'),
 ('render','Actual renderer at t=0 over the original','render',
  'Initialized runtime output, original background and the measured mapper/DOM geometry.',
  'The rendered source landmarks should coincide with the printed diagram at t=0. This requires correct upstream geometry as well as correct transforms.',
  'Overlay image is captured from the actual canvas/SVG and projected back using measured DOM-to-source ratios. No objects were manually repositioned.'),
 ('motion','Activation, motion and reset','event:SimulationOrchestrator.startSimulation|event:PhysicsRuntime.start|event:PhysicsRuntime.reset',
  'The initialized scene/state and actual Play/Pause/Reset control actions.',
  'Motion evolves runtime state only; reset restores initial compiled values. Exact 0.5 s / 1 s states cannot be asserted unless their saved timestamps say so.',
  'The executed main.js path automatically starts after a successful load. Later frames are saved at their actual times. Optics results are static ray solutions rather than pendulum-like time evolution.')]

JS_FILES={
 'upload':'apps/web/src/features/simulations/core/SimulationOrchestrator.js',
 'orchestrator':'apps/web/src/features/simulations/core/SimulationOrchestrator.js',
 'review':'apps/web/src/features/simulations/core/SimulationOrchestrator.js',
 'figure':'apps/web/src/components/InteractiveFigure.js',
 'background':'apps/web/src/components/FigureViewport.js',
 'runtime':'engine/core/PhysicsRuntime.js',
 'mapper':'engine/core/coordinateMapper.js',
 'render':'apps/web/src/components/InteractiveFigure.js',
 'motion':'apps/web/src/main.js'}

STYLE='''body{margin:0;background:#eef2f6;color:#172635;font:16px/1.55 system-ui}header,main{max-width:1320px;margin:auto;padding:24px}header{background:#132d43;color:white}header a{color:#b5e1ff}section{background:white;padding:24px;margin:22px 0;border:1px solid #cdd7e1;border-radius:8px}h1,h2,h3{line-height:1.2}h2{scroll-margin-top:16px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{min-width:0;border:1px solid #d8e0e8;padding:16px;border-radius:6px}.actual{background:#f2f8ff}.expected{background:#f6faf2}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.45 ui-monospace;max-height:450px;overflow:auto;background:#edf1f6;padding:12px}a{color:#1359a0;overflow-wrap:anywhere}img{max-width:100%;height:auto;border:1px solid #cdd7e1}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:9px;border:1px solid #cdd7e1;vertical-align:top;text-align:left}details{margin:12px 0}summary{cursor:pointer;font-weight:650}.status{padding:12px;border-left:5px solid #b47c15;background:#fff4d9}.fail{border-color:#bf3131;background:#fff0ef}.pass{border-color:#32865a;background:#edf8f0}.small{font-size:13px;color:#4e6070}nav ol{columns:2}code{overflow-wrap:anywhere}@media(max-width:800px){.pair{display:block}nav ol{columns:1}header,main{padding:12px}section{padding:16px}}@media print{body{background:white}details{display:block}pre{max-height:none}section{break-inside:auto}.pair{display:block}}'''

def show(v):return '<pre>'+E(json.dumps(v,ensure_ascii=False,indent=2))+'</pre>'
def md_json(v):return '```json\n'+json.dumps(v,ensure_ascii=False,indent=2)+'\n```'

def digest(v,depth=0):
    """Clearly labeled field preview; complete unmodified snapshots remain attached."""
    if isinstance(v,dict):
        if 'artifact' in v:return v
        if 'call' in v and ('value' in v or 'return_value' in v):
            return {k:digest(x,0) if k in ('value','return_value') else x for k,x in v.items()}
        if all(not isinstance(x,(dict,list)) for x in v.values()):return v
        preferred=['classification','is_physics','isPhysics','domain','subtype','status','ready','scene','book_ir','grounded_book_ir','source','source_asset','source_asset_id','geometry','parameters','resolutions','assumptions','failures','blockers','warnings','missing_requirements','satisfied_requirements','entities','relationships','tokens','model','contents','config','prompt','best_proposal','lens_center','lens_line','object_arrow','image_arrow','optical_axis','prism_polygon','base_line','incident_ray','wires','nodes','components','masks','calibration','state','output','mapper','transforms','mechanics','http_status','http_path','file','image_bgr','img_bgr','source_width','source_height','margin_px','edge_map']
        keys=list(v) if len(v)<=12 else [k for k in preferred if k in v]
        if not keys:keys=list(v)[:12]
        if depth>=4:
            values={k:x for k,x in v.items() if not isinstance(x,(dict,list)) or isinstance(x,dict) and 'x' in x and 'y' in x}
            return {**values,'_nested_fields_in_complete_snapshot':[k for k in v if k not in values]}
        d={k:digest(v[k],depth+1) for k in keys}
        if len(keys)<len(v):d['_other_fields_in_complete_snapshot']=[k for k in v if k not in keys]
        return d
    if isinstance(v,list):
        if len(v)>8:return {'count':len(v),'first_8_records':[digest(x,depth+1) for x in v[:8]],'complete_list':'See complete stage bundle / original artifact'}
        return [digest(x,depth+1) for x in v]
    if isinstance(v,str) and len(v)>600:return {'string_length':len(v),'complete_text':'See complete stage bundle / original artifact; not rewritten'}
    return v

def verdict(key,sid,c,executed):
    if not executed:return 'NOT EXECUTED','No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.'
    if sid in ('upload','http_in','asset','page','route'):return 'PASS','Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.'
    if sid in ('vlm','semantic','book'):return 'PASS WITH LIMITS','Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.'
    if sid in ('rapid','easy','ocr'):return 'OBSERVED / REVIEW ALTERNATIVES','Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. '+SOURCE_EXPECTATIONS[key][2]
    if sid=='pre':return 'FRAME PASS / LOSSY PROCESSING','Arrays preserve the source frame. Blur and Canny change image information; no detector correctness is inferred from shape alone.'
    if sid=='mask':
        if key=='LENS':return 'FAIL — FIRST PROVEN GEOMETRY LOSS','Object OCR bbox=(188,220,135,57); margin=4 removes incident-ray pixels adjacent to the label. The removed-edge overlay proves the loss. Its causal connection to the later missing vertical object arrow is not established.'
        if key=='PRISM':return 'FAIL — FIRST PROVEN GEOMETRY LOSS','A=60° bbox=(556,184,128,49); margin=4 removes prism-side pixels. Other masks remove angle/normal strokes. This is an earlier loss than the wrong base inference; it is not proven to be the sole cause of contour failure.'
        return 'NO EARLIER GEOMETRIC FAILURE DEMONSTRATED','Removed-edge overlay was inspected. No earlier failure explaining the later rail/pivot error is established by this mask capture.'
    if sid=='cv':return 'FAIL — PERCEPTION / SELECTION',c['cv_detail']
    if sid=='sam':return 'BOB SUPPORT ONLY',c['ground']
    if sid in ('ground','fused'):return 'FAIL / UPSTREAM DAMAGE PROPAGATES',c['ground']
    if sid=='dimensions':return 'FRAME PASS; GEOMETRY STILL WRONG','Source extent is enforced without correcting the already incorrect landmark/topology evidence.'
    if sid in ('auto','calibration'):return 'ASSUMPTIONS / UNRESOLVED EVIDENCE',c['auto']
    if sid in ('requirements','readiness'):return ('BLOCKS CORRECTLY' if key=='CIRCUIT' else 'RUNNABLE ≠ SOURCE-REGISTERED'),c['auto']+' The accepted requirement set and all blockers/warnings are in the actual outputs below.'
    if sid in ('gate','compile','response'):return ('SAFE NULL SCENE' if key=='CIRCUIT' else 'PROPAGATED / RECONSTRUCTED GEOMETRY'),c['compile']
    if sid in ('orchestrator','review'):return ('FRONTEND FLOW ISSUE' if key=='CIRCUIT' else 'SCENE ACCEPTED'),c['compile']
    if sid in ('figure','background','runtime'):return 'EXECUTED; UPSTREAM REGISTRATION FAILURE','The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.'
    if sid=='solver':return 'OUTPUT OBSERVED; NO NUMERICAL DEFECT PROVEN',c['runtime']
    if sid=='mapper':return 'MAPPING PASS FOR CAPTURED LANDMARKS','Actual sourceToView/sourceToOverlay and inverse results preserve supplied points. This does not validate the input coordinates against the source.'
    if sid=='render':return 'FAIL — T=0 SOURCE REGISTRATION',c['runtime']
    return 'ACTUAL STATE CAPTURED','Automatic activation is observed in this checkout. Later frame time is whatever the runtime snapshot records, not an invented exact timestamp.'

def main():
    DEST.mkdir(parents=True,exist_ok=True);index=[]
    for key,c in CASES.items():
        folder=next(RAW.glob('TRACE-'+key+'-*-NATIVE-RETRY-20261017'))
        outdir=DEST/key.lower();outdir.mkdir(exist_ok=True)
        bundles=outdir/'stage_data';bundles.mkdir(exist_ok=True)
        calls=[]
        for p in sorted((folder/'calls').iterdir()):
            loc=read(p/'location.json')
            if loc:calls.append({'path':p,'location':loc,'input':read(p/'actual_input.json'),'output':read(p/'actual_output.json'),'after':read(p/'locals_after.json',{})})
        events=read(folder/'15_browser/events.json',[])
        starts=[e['wallTime'] for e in events if e['component']=='SimulationOrchestrator.startWithFile' and e['phase']=='input']
        events=[e for e in events if not starts or e['wallTime']>=min(starts)]
        final=read(folder/'15_browser/final_state.json',{})
        audit=read(folder/'14_renderer/coordinate_audit.json',{})
        renderer=read(folder/'14_renderer/runtime_t0_capture.json',{})
        snapshot=audit.get('snapshot',renderer.get('snapshot',{}))
        original=folder/'00_source/original.png'
        runnable=bool(final.get('orchestrator',{}).get('compiledScene'))
        expected=SOURCE_EXPECTATIONS[key]
        intro=f'Trace ID: `{folder.name}`. These documents use the existing live native Windows request from 2026-10-17. No models, detectors or solvers were rerun while writing them. No production fixes were made.\n\nSource reference: {expected[1]}\n\nKnown and unknown evidence: {expected[2]}\n\nExpected geometry for this diagram: {expected[3]}\n\nExpected initial simulation: {expected[4]}\n\nExact expected coordinates/masks are unavailable: {UNKNOWN}. Expected behavior below is a contract or a qualitative source comparison, never a hand-drawn expected result.'
        md=[f'# {c["title"]}: complete component-by-component debugging walkthrough',intro,f'![Unchanged original diagram]({link(outdir,original)})','## How to read this document','Follow stages 01–34 in order. Every stage has actual input, expected input, actual output, expected output, verdict and downstream handoff. Summaries show selected recorded fields; the complete input/output bundle and original raw files remain linked. Empty/undefined returns are not automatically errors: in-place mutations and resulting state are shown separately.','The order is logical data flow. Parent call entry timestamps precede nested work; their outputs are explained only after that work. Repeated readiness/resolution calls remain distinct in stage bundles. Startup/demo frontend events before this request are excluded.','## Pipeline map',' → '.join(f'{i:02d} {s[1]}' for i,s in enumerate(STAGES,1))]
        body=[f'<p><b>Trace:</b> {E(folder.name)}</p><p>{E(intro)}</p><p><a href="WALKTHROUGH.md">Markdown document</a> · <a href="{link(outdir,folder/"TRACE_REPORT.html")}">Original forensic call index</a></p><img src="{link(outdir,original)}" alt="Unchanged original source">','<section><h2>How to use this document</h2><p>Read stages 01–34 in order. Blue panels show recorded data; green panels show expected contracts and source-specific requirements. Full snapshots are expandable. Mutation output is distinguished from a None/undefined function return. Earlier startup/demo events are excluded. A structural pass does not certify visual registration.</p><p>“NOT EXECUTED” means the branch did not run. “Not separately captured” means an internal operation was reached but its own call arguments were not intercepted. No expected pixels or runtime outputs have been invented.</p></section>','<nav><h2>Ordered pipeline</h2><ol>'+''.join(f'<li><a href="#stage-{i:02d}">{E(s[1])}</a></li>' for i,s in enumerate(STAGES,1))+'</ol></nav>']
        manifest=[]
        for i,(sid,title,selector,expect_in,expect_out,change) in enumerate(STAGES,1):
            selector=selector.replace('CV',c['cv']).replace('GROUND',{'LENS':'ThinLensGrounder.ground','CIRCUIT':'CircuitGrounder.ground','PENDULUM':'PendulumGrounder.ground','PRISM':'PrismGrounder.ground'}[key]).replace('POPULATE','PhysicsCompiler._populate_canonical_'+{'LENS':'lens','CIRCUIT':'circuits','PENDULUM':'pendulum','PRISM':'prism'}[key])
            names=selector.split('|');bc=[x for x in calls if x['location']['function'] in names]
            fe=[e for e in events if 'event:'+e['component'] in names]
            inputs=[];outputs=[];mutations=[];proof=[];images=[];image_labels={}
            for x in bc:
                loc=x['location'];inputs.append({'call':x['path'].name,'value':x['input']});outputs.append({'call':x['path'].name,'return_value':x['output']})
                if x['output'] is None:
                    selected={k:v for k,v in x['after'].items() if k in ('book_ir','scene','page_ir','result','readiness')}
                    if selected:mutations.append({'call':x['path'].name,'post_call_locals':selected})
                proof.append((x['location']['function']+' — exact input/output/locals/contract',x['path']/'STAGE.html'))
                for p in x['path'].glob('*source.png'):images.append(p)
                if sid=='cv' and (x['path']/'all_candidates_overlay.png').exists():images.append(x['path']/'all_candidates_overlay.png')
                if sid in ('pre','mask'):
                    def add_array_images(v,label):
                        if isinstance(v,dict):
                            if v.get('image') and v.get('artifact'):
                                image_path=RAW/v['image'];images.append(image_path);image_labels[image_path]=label
                            for name,child in v.items():add_array_images(child,label+'.'+name)
                        elif isinstance(v,list):
                            for number,child in enumerate(v):add_array_images(child,label+f'[{number}]')
                    add_array_images(x['input'],'Actual input');add_array_images(x['output'],'Actual output')
            for e in fe:
                (inputs if e['phase']=='input' else outputs).append(e)
            if fe:proof.append(('Original frontend events (includes startup events; this stage bundle filters them)',folder/'15_browser/events.json'))
            if sid=='upload':inputs=[{'original_file':read(folder/'00_source/file.json'),'metadata':read(folder/'00_source/metadata.json')},*inputs]
            if sid=='http_in':
                for p in sorted((folder/'http').glob('*_request.json')):
                    r=read(p)
                    if r.get('path')=='/api/ingest':inputs.append(r);proof.append(('Exact multipart body',p.with_name(p.name.replace('_request.json','_request_body.bin'))))
                outputs=[{'handler_input':next((x['input'] for x in calls if x['location']['function']=='ingest_diagram'),None),'note':'UploadFile is opaque in profiler; source and multipart bytes provide exact contents.'}]
            if sid in ('http_in','response','review'):
                for p in sorted((folder/'http').glob('*_response_body.json')):proof.append(('HTTP response '+p.name,p))
            if sid=='fused':
                for x in bc:mutations.append({'call':x['path'].name,'page_ir_after':x['after'].get('page_ir')})
            if sid=='auto':
                for x in bc:
                    if (x['path']/'field_changes.json').exists():proof.append(('Every changed field before/after',x['path']/'field_changes.json'))
            if sid=='runtime' and runnable:outputs.append({'actual_runtime_after_load':next((e['data']['figure'] for e in events if e['component']=='t0' and e['phase']=='snapshot'),None)})
            if sid in ('solver','mapper','render') and runnable:
                figure=snapshot.get('figure',{})
                if sid=='solver':inputs=[{'scene_used_by_runtime':figure.get('scene')}];outputs=[{'state':figure.get('state'),'output':figure.get('output'),'mechanics_internal_capture':audit.get('mechanics')}]
                if sid=='mapper':inputs=[{'mapper':audit.get('mapper'),'image_rect':audit.get('imageRect'),'browser':snapshot.get('browser')}];outputs=[{'landmarks':audit.get('landmarks'),'DOM_elements':snapshot.get('elements')}]
                if sid=='render':inputs=[{'runtime_output':figure.get('output'),'transforms':renderer.get('transforms')}];outputs=[{'captured_svg':renderer.get('svgs'),'browser_state':figure.get('state')}];images.append(folder/'14_renderer/runtime_t0_overlay.png')
                proof.extend([('Actual coordinate/landmark audit',folder/'14_renderer/coordinate_audit.json'),('Renderer snapshot',folder/'14_renderer/runtime_t0_capture.json')])
            if sid=='motion' and runnable:
                outputs.append({'after_play':read(folder/'15_browser/runtime_after_play.json')})
                proof.append(('Actual later browser frame',folder/'15_browser/runtime_after_play.png'))
            if sid=='background' and runnable:outputs.append({'measured_image_rect':audit.get('imageRect'),'mapper':audit.get('mapper')})
            if sid=='orchestrator':outputs.append({'final_orchestrator_state':final.get('orchestrator',{}).get('state'),'currentError':final.get('orchestrator',{}).get('currentError')})
            executed=bool(bc or fe or (sid=='http_in' and inputs) or (sid in ('solver','mapper','render') and runnable))
            if key=='CIRCUIT' and sid in ('figure','background','runtime','solver','mapper','render','motion'):executed=False;inputs=[];outputs=[];mutations=[];images=[]
            status,reason=verdict(key,sid,c,executed)
            if not executed:
                change='No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.'
                if sid=='sam':reason+=' The active segmentation trigger requires a best_proposal.bob; this domain did not produce that trigger.'
            actual_in={'records':inputs,'capture_note':'Exact available recorded inputs. File/DOM/library objects may be represented as opaque metadata; raw byte/array references remain authoritative.'}
            actual_out={'records':outputs,'in_place_outputs':mutations,'capture_note':'Return values are retained unchanged. captureError for JSON.stringify(undefined) is a recorder serialization limitation, not an application exception. Use observed resulting state for void methods.'}
            sources=[x['location'] for x in bc]
            if sid in JS_FILES:sources.append({'file':JS_FILES[sid],'capture':'Frontend boundary events and resulting state; source inspected. Internal children not individually intercepted.'})
            if sid=='solver':sources.append({'file':{'LENS':'engine/optics/thinLensEngine.js','PRISM':'engine/optics/prismEngine.js','PENDULUM':'engine/mechanics/MechanicsAdapter.js','CIRCUIT':'engine/circuits/CircuitsAdapter.js'}[key],'capture':'Boundary/runtime output observed; exact solver-call object not separately captured' if runnable else 'NOT EXECUTED'})
            diagram_expectation=expected[3] if sid in ('cv','sam','ground','fused','compile','render') else expected[4] if sid in ('solver','motion') else expected[2]
            if sid in ('vlm','semantic','book'):
                diagram_expectation='Expected accepted classification: supported; isPhysics=true; domain/subtype='+expected[0]+'. Expected semantic content: '+expected[1]+' These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.'
            local=f'{i:02d}_{sid}.json';bundle={'trace_id':folder.name,'logical_stage':i,'component':title,'execution':'EXECUTED' if executed else 'NOT EXECUTED','location_and_callers':sources,'upstream_stage':STAGES[i-2][1] if i>1 else 'User original file','downstream_stage':STAGES[i][1] if i<len(STAGES) else 'Final observed browser state','actual_input':actual_in,'expected_input':expect_in,'actual_output':actual_out,'expected_output_contract':expect_out,'expected_diagram':diagram_expectation,'status':status,'finding':reason,'change_or_loss':change}
            dump(bundles/local,bundle)
            # Each component's saved source is linked through captured call contracts;
            # frontend code is snapshotted now and explicitly labeled as code evidence.
            for loc in sources:
                src=Path(loc['file']);src=src if src.is_absolute() else ROOT/src
                if src.exists() and str(src).lower().startswith(str(ROOT).lower()):
                    dest=outdir/'contracts'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());proof.append(('Code: '+str(src.relative_to(ROOT)),dest))
            proof=list(dict.fromkeys((label,str(p)) for label,p in proof if Path(p).exists()))
            images=list(dict.fromkeys(p for p in images if p.exists()))
            view_in=digest(actual_in['records']);view_out=digest({'records':outputs,'in_place_outputs':mutations})
            md += [f'## {i:02d}. {title}',f'**Execution:** {bundle["execution"]}. **Verdict:** {status}.',f'**Upstream → downstream:** {bundle["upstream_stage"]} → this component → {bundle["downstream_stage"]}.',f'**What it receives — actual input (selected recorded fields):**\n\n{md_json(view_in)}',f'**What it should receive — expected input:** {expect_in}',f'**What it provides — actual output (selected recorded fields):**\n\n{md_json(view_out)}',f'**What it should provide — implemented contract:** {expect_out}',f'**What correct handling of THIS diagram requires:** {bundle["expected_diagram"]}',f'**Comparison / debugging conclusion:** {reason}',f'**Changes, provenance and possible information loss:** {change}',f'[Complete stage input/output bundle]({link(outdir,bundles/local)})',*['- ['+label+']('+link(outdir,Path(p))+')' for label,p in proof],*['!['+p.name+']('+link(outdir,p)+')' for p in images]]
            evidence=' · '.join(f'<a href="{link(outdir,Path(p))}">{E(label)}</a>' for label,p in proof)
            full='<details><summary>Complete recorded input (unabridged stage bundle)</summary>'+show(actual_in)+'</details><details><summary>Complete recorded output and in-place mutations</summary>'+show(actual_out)+'</details>'
            img_html=''.join(f'<figure><figcaption>{E(image_labels.get(p,p.name))} — '+('actual component array image; preprocessing representation, not an expected diagram' if p.parent.name=='arrays' else 'recorded geometry/pixels on unchanged source')+f'</figcaption><img loading="lazy" src="{link(outdir,p)}"></figure>' for p in images)
            color='fail' if 'FAIL' in status else 'pass' if status.startswith('PASS') or status.startswith('MAPPING PASS') else ''
            body.append(f'<section id="stage-{i:02d}"><h2>{i:02d}. {E(title)}</h2><p>{bundle["execution"]} · {E(bundle["upstream_stage"])} → this component → {E(bundle["downstream_stage"])}</p><div class="status {color}"><b>{E(status)}</b><br>{E(reason)}</div><div class="pair"><div class="card actual"><h3>Actual input received</h3><p class="small">Selected recorded fields; expand full snapshots below.</p>{show(view_in)}</div><div class="card expected"><h3>Expected input</h3><p>{E(expect_in)}</p></div></div><div class="pair"><div class="card actual"><h3>Actual output provided</h3>{show(view_out)}</div><div class="card expected"><h3>Expected output</h3><p>{E(expect_out)}</p><h3>For this diagram</h3><p>{E(bundle["expected_diagram"])}</p></div></div><h3>What changed and what may have been lost</h3><p>{E(change)}</p><p><a href="stage_data/{local}">Complete stage bundle</a></p><details><summary>Runtime location and actual callers</summary>{show(sources)}</details>{full}<p>{evidence}</p>{img_html}</section>')
            manifest.append({'stage':i,'title':title,'execution':bundle['execution'],'status':status,'bundle':'stage_data/'+local,'backend_calls':[x['path'].name for x in bc],'frontend_event_count':len(fe)})
        # Exact handoffs: no expected coordinates or repaired data are introduced.
        first={}
        for x in calls:first.setdefault(x['location']['function'],x)
        ground_name={'LENS':'ThinLensGrounder.ground','CIRCUIT':'CircuitGrounder.ground','PENDULUM':'PendulumGrounder.ground','PRISM':'PrismGrounder.ground'}[key]
        handoffs=[]
        def compare(label,a,b):
            raw_differences=delta(a,b)
            numeric_notation=[];differences=[]
            for d in raw_differences:
                x,y=d.get('before'),d.get('after')
                if type(x) in (int,float) and type(y) in (int,float) and x==y:
                    numeric_notation.append({**d,'before_python_decoder_type':type(x).__name__,'after_python_decoder_type':type(y).__name__})
                else:differences.append(d)
            handoffs.append({'handoff':label,'equal':not differences,'field_changes':differences,'numeric_notation_only':numeric_notation,'comparison_note':'JSON numbers such as 1280.0 and 1280 have identical numeric meaning across Python/JS. Their notation differences are listed separately, not treated as coordinate changes. Original snapshots remain unchanged.','actual_upstream_output':a,'actual_downstream_input':b})
        compare('UploadService output → PageIRBuilder asset input',first['UploadService.ingest']['output'],first['PageIRBuilder.build']['input']['asset'])
        compare('PageIRBuilder output → BookUnderstandingPipeline page input',first['PageIRBuilder.build']['output'],first['BookUnderstandingPipeline.analyze']['input']['page_ir'])
        compare('Semantic BookIR → EvidenceExtractionPipeline book input',first['BookUnderstandingPipeline.analyze']['output'],first['EvidenceExtractionPipeline.extract_and_fuse']['input']['book_ir'])
        compare('Final OCR output → Grounder OCR input',first['MultiOCRRouter.extract']['output'],first[ground_name]['input']['ocr_result'])
        compare('CV output → Grounder CV input',first[c['cv']]['output'],first[ground_name]['input']['cv_candidates'])
        if 'SAM2SegmentationProvider.segment' in first:compare('SAM2 output → Grounder segmentation input',first['SAM2SegmentationProvider.segment']['output'],first[ground_name]['input']['seg_result'])
        compare('Grounded BookIR → Evidence pipeline returned BookIR',first[ground_name]['output']['grounded_book_ir'],first['EvidenceExtractionPipeline.extract_and_fuse']['output'])
        compare('Evidence BookIR → AutoResolution input (dimension enforcement between)',first['EvidenceExtractionPipeline.extract_and_fuse']['output'],first['AutoResolutionEngine.resolve']['input']['book_ir'])
        compare('AutoResolution BookIR → Compiler input (resolution evaluation between)',first['AutoResolutionEngine.resolve']['output']['book_ir'],first['PhysicsCompiler.compile']['input']['book_ir'])
        norm=next((e for e in events if e['component']=='PhysicsRuntime.normalizeScene' and e['phase']=='input'),None)
        if runnable and norm:compare('Compiler scene → Runtime normalization input (API/frontend URL binding between)',first['PhysicsCompiler.compile']['output']['scene'],norm['data'][0])
        dump(outdir/'HANDOFFS.json',handoffs)
        handoff_rows=''.join('<tr><td>'+E(h['handoff'])+'</td><td>'+('IDENTICAL' if h['equal'] else 'CHANGED')+'</td><td>'+E(', '.join(d['path'] for d in h['field_changes']) or 'No field differences')+'</td></tr>' for h in handoffs)
        body.append('<section><h2>Handoff audit: what actually passes to the next component</h2><p>These are exact comparisons of recorded values. IDENTICAL means the next component received the same bad or good data; it does not certify correctness. CHANGED marks recorded field differences, including legitimate metadata/state changes. No differences have been repaired.</p><table><tr><th>Boundary</th><th>Comparison</th><th>Changed field paths</th></tr>'+handoff_rows+'</table><details><summary>Full before/after values and every changed field</summary>'+show(handoffs)+'</details><a href="HANDOFFS.json">Complete handoff JSON</a></section>')
        md+=['## Handoff audit: actual output → next actual input','IDENTICAL proves preservation of the supplied data, not correctness. CHANGED means differences were recorded; URL binding, dimension metadata and status changes may be legitimate. The complete JSON contains both values and every changed field.', '[Complete handoff comparison](HANDOFFS.json)','| Boundary | Result | Changed paths |','|---|---|---|']
        md.extend('| '+h['handoff']+' | '+('IDENTICAL' if h['equal'] else 'CHANGED')+' | '+(', '.join(d['path'] for d in h['field_changes']) or 'None')+' |' for h in handoffs)
        child_contracts=[
          ('validatePhysicsScene','Normalized canonical scene','Validation result / typed issues','Not separately intercepted; successful load shows continuation, not a saved validation-result object.'),
          ('SimulationCapabilityRegistry.resolve','Validated normalized scene','Interactive scene/capabilities','No separate before/after capture. Use PhysicsRuntime source and actual runtime boundary; do not assume its output equals its input.'),
          ('SolverRegistry.resolve','Interactive scene','Matching domain adapter','No separately serialized adapter return. Runtime domain/output and the executed load path establish the adapter route.'),
          ('Adapter.initialize','Interactive scene, container and options','Initialized adapter state','Initial runtime output/state is captured, but this child call’s exact argument object is not separately recorded.'),
          ('Domain solver','Adapter-derived model arguments','Physics solution/state','Actual solution/state is captured. Exact internal solver-call arguments are not a separate artifact.'),
          ('Renderer.render / PendulumSimulation.render','Runtime solution/state and mapper','SVG/canvas output','Actual SVG/canvas and DOM measurements are captured; per-draw-call arguments are not.')]
        child_rows=''.join('<tr><td>'+E(n)+'</td><td>'+E(a)+'</td><td>'+E(b)+'</td><td>'+E(note if runnable else 'NOT EXECUTED for this uploaded circuit; compiler returned no scene.')+'</td></tr>' for n,a,b,note in child_contracts)
        body.append('<section><h2>Runtime subcomponents and capture boundary</h2><p>These internal components are distinguished explicitly so a saved outer runtime result is not mistaken for six separate function traces.</p><table><tr><th>Component</th><th>Expected input</th><th>Expected output</th><th>Actual evidence / gap</th></tr>'+child_rows+'</table></section>')
        md+=['## Runtime subcomponents and capture boundary','| Component | Expected input | Expected output | Actual evidence / gap |','|---|---|---|---|']
        md.extend('| '+n+' | '+a+' | '+b+' | '+(note if runnable else 'NOT EXECUTED for this uploaded circuit.')+' |' for n,a,b,note in child_contracts)
        # Component ledger includes every profiled helper, including ones nested
        # inside a stage but not duplicated in the main explanatory narrative.
        grouped=defaultdict(list)
        for x in calls:grouped[x['location']['function']].append(x)
        ledger=[];md+=['## Appendix A. Every captured backend component and invocation','The main 34 stages group nested helpers by their role in the data flow. This ledger retains every captured function, including parsing, unit conversion, geometry helpers, registry checks and repeated evaluators. Each call page contains exact input/output/locals and that function’s source contract. Call numbers are entry order, not completed-stage order.']
        for name,items in grouped.items():
            links=' · '.join(f'<a href="{link(outdir,x["path"]/"STAGE.html")}">{x["location"]["sequence"]}</a>' for x in items)
            ledger.append(f'<tr><td>{E(name)}</td><td>{E(items[0]["location"]["file"])}</td><td>{len(items)}</td><td>{links}</td></tr>')
            md.append('- **'+name+'** ('+str(len(items))+' calls): '+', '.join(f'[{x["location"]["sequence"]}]({link(outdir,x["path"]/"STAGE.html")})' for x in items))
        conclusion=f'Last known good: {c["good"]}\n\nFirst suspicious: {c["suspicious"]}\n\nFirst definitive failure: {c["first"]}\n\nDownstream chain: {c["ground"]} {c["auto"]} {c["compile"]}\n\nSeparation of failure classes: preprocessing/perception is demonstrated upstream; a shared coordinate conversion error is not demonstrated; numerical solver failure is not established. The circuit never reaches a solver.'
        limits='No new run was performed. The recorder captured repository Python boundaries and GenAI model calls, not private neural-library/C internals. JS boundary events, normalized scenes, actual solver outputs and DOM captures exist; separate entry/exit snapshots for every registry/adapter/renderer child function do not. These gaps are labeled, not filled with reconstructed output. Several void JS returns appear as captureError because undefined is not JSON; resulting state is separately recorded. Two class-serialization errors exist in the historical recorder log; integrity verification found the required snapshot files present for every indexed call. No exact expected pixel dataset, mask or numerical physical state has been authored.'
        md+=['## Appendix B. First failure and propagation',conclusion,'## Appendix C. Capture limits',limits,f'[Original trace integrity checks]({link(outdir,OUT/"artifact_verification.json")})']
        body+=['<section><h2>Appendix A. Every captured backend component</h2><p>All helpers and repeated calls are retained. Numbers are profiler entry order. Open an invocation for exact source contract, inputs, returned values and post-call locals.</p><table><tr><th>Component</th><th>File</th><th>Count</th><th>All invocations</th></tr>'+''.join(ledger)+'</table></section>','<section><h2>Appendix B. First failure and propagation</h2><p>'+E(conclusion).replace('\n\n','</p><p>')+'</p></section>','<section><h2>Appendix C. Capture limits</h2><p>'+E(limits)+'</p></section>']
        (outdir/'WALKTHROUGH.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
        (outdir/'WALKTHROUGH.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>'+E(c['title']+' — complete pipeline walkthrough')+'</title><style>'+STYLE+'td,th{overflow-wrap:anywhere}table{table-layout:fixed}pre{font-family:Consolas,monospace}</style></head><body><header><h1>'+E(c['title']+' — from upload to simulation')+'</h1><p>Actual input · expected input · actual output · expected output · error propagation</p></header><main>'+''.join(body)+'</main></body></html>',encoding='utf-8')
        dump(outdir/'manifest.json',{'trace':folder.name,'stages':manifest,'backend_calls':len(calls),'backend_functions':len(grouped),'excluded_startup_events':len(read(folder/'15_browser/events.json',[]))-len(events)})
        index.append({'diagram':c['title'],'html':link(DEST,outdir/'WALKTHROUGH.html'),'markdown':link(DEST,outdir/'WALKTHROUGH.md'),'stages':len(STAGES),'calls':len(calls),'trace':folder.name})
    dump(DEST/'manifest.json',index)
    links='<table><tr><th>Diagram</th><th>Complete HTML</th><th>Markdown</th><th>Stages</th><th>Recorded calls</th></tr>'+''.join(f'<tr><td>{E(r["diagram"])}</td><td><a href="{r["html"]}">Read from beginning to end</a></td><td><a href="{r["markdown"]}">Document</a></td><td>{r["stages"]}</td><td>{r["calls"]}</td></tr>' for r in index)+'</table>'
    (DEST/'INDEX.html').write_text('<!doctype html><meta charset="utf-8"><title>Complete diagram pipeline debugging documents</title><style>'+STYLE+'</style><header><h1>Complete diagram pipeline debugging documents</h1></header><main><section><p>Each document follows one real upload through 34 ordered stages. Every stage shows actual input/output, expected contracts, source-specific expectations, evidence links and the downstream effect. Full captured data is expandable inside the document.</p>'+links+'</section></main>',encoding='utf-8')
    print(json.dumps(index,indent=2))

if __name__=='__main__':main()
