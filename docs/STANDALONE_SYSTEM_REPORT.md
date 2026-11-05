# AugmentedPhysics: standalone system report and GPT handoff

**Snapshot date:** 28 October 2026, Asia/Dhaka.

**Repository inspected:** `D:\AugmentedPhysics`, repository name `AI-Enhanced-Interactive-Physics-Textbook`.

**Checked-out branch and commit:** `main`, `e484676` — `feat(web): update simulation orchestrator state machine, review modal, and circuit visualization` (20 October 2026).

**Purpose:** Give a reader or GPT that cannot access the repository a sufficiently detailed account of the current system, its execution path, its contracts, and the constraints governing technical decisions.

This report describes the working-tree snapshot, including pre-existing uncommitted circuit/OCR changes. It distinguishes source inspection, test evidence, architectural requirements, and unresolved questions. It is a context package, not a guarantee that an unseen image will be interpreted correctly. A GPT using it must request the relevant image, response JSON, logs, or updated code when a decision depends on facts absent from this snapshot.

**Scope rule:** The primary subject is the current **real uploaded-file flow**, starting at `SimulationOrchestrator.startWithFile()` and `POST /api/ingest`. Preset demonstrations, older endpoints, compatibility wrappers, and the archived frontend are identified separately near the end. Their capabilities and fallback behavior must not be attributed to the current flow.

## 1. What the system is

AugmentedPhysics is a research and engineering platform that turns a static physics diagram into an interactive simulation attached to the original image. A learner uploads a cropped figure, the backend identifies the physical model, local image-processing tools measure the relevant visual evidence, and a compiler produces a structured scene. The browser runs the appropriate mathematical solver and draws an interactive overlay aligned with the uploaded picture.

For example, a pendulum drawing can become a moving bob and string anchored to the drawing's measured pivot. A lens figure can gain computed rays and an image arrow. A resistor network can gain node voltages, branch currents, switch interactions, and current-flow visualization.

The project is **book-agnostic**. Bangla/NCTB physics material is a demonstration and evaluation context, not the definition of the platform. The same generic solvers and scene contracts should work with another textbook when its figures can be grounded by the supported perception modules.

The intended learning value is the connection between the printed figure, physical quantities, mathematical consequences, and interactive changes. The distinguishing technical feature is the separation between what the system *thinks the picture means*, what it can *measure or verify*, what it *assumes for a model*, and what the solver *calculates*.

The current product is a diagram studio and simulation platform. A complete textbook reader, general conversational Bangla tutor, exam system, student database, and learning-management platform are broader goals, not established features of the inspected main flow.

## 2. What the current flow supports

The semantic vocabulary recognizes seven physical model subtypes across three domains:

| Domain | Canonical subtype | Current model |
|---|---|---|
| `mechanics` | `pendulum` | Planar nonlinear gravity pendulum with damping |
| `mechanics` | `projectile` | Ideal analytical projectile motion |
| `optics` | `thin_lens` | Thin-lens image formation and principal rays |
| `optics` | `spherical_mirror` | Concave/convex mirror image formation; engine also contains plane-mirror calculations |
| `optics` | `interface_refraction` | Refraction/reflection at a modeled interface, including total internal reflection |
| `optics` | `prism` | Polygonal ray tracing, refraction, reflection, and deviation |
| `circuits` | `dc_linear` | Grounded linear DC network and Modified Nodal Analysis |

“Supported” means the model has relevant implementation layers. It does **not** mean every drawing of that model can automatically become a correct simulation. Source quality, layout, symbol ambiguity, missing values, provider availability, and grounding failures still matter.

The normal input is **one cropped image containing one figure**. `PageIRBuilder` wraps the entire image as one user-supplied region and one figure. It does not currently locate multiple textbook figures automatically. PDFs, DOCX documents, full-book ingestion, and automatic page/chapter understanding are not the current entry path.

The upload service allows declared PNG, JPEG/JPG, GIF, WebP, and BMP MIME types, but an upload must also decode successfully through OpenCV. This is not a promise of animated-GIF processing or support for every encoding variation. The byte limit is 50 MiB.

## 3. The current end-to-end execution path

```text
Learner selects a real File/Blob and clicks Generate Simulation
    |
    v
apps/web/src/main.js
    -> SimulationOrchestrator.startWithFile(file)
    -> SimulationApi.ingest(file)
    -> POST /api/ingest, multipart field: file
    |
    v
FastAPI: apps/api/main.py
    1. Stream and bound uploaded bytes
    2. UploadService: validate, decode, save, identify SourceAsset
    3. PageIRBuilder: describe the one supplied figure in native pixels
    4. BookUnderstandingPipeline: VLM semantic interpretation
    5. EvidenceExtractionPipeline: OCR -> classical CV -> SAM 2 -> fusion
    6. Enforce actual SourceAsset dimensions
    7. AutoResolutionEngine + ResolutionEngine.auto_resolve
    8. PhysicsCompiler: gate, validate, compile, validate scene
    |
    v
JSON: source_asset + page_ir + book_ir + compiler + diagnostics
    |
    +-- unknown/provider failure -> unresolved/error handling
    +-- incomplete evidence      -> review/compile refusal
    +-- READY + scene           -> READY_TO_SIMULATE
                                  |
                                  v
                          InteractiveFigure.load(scene)
                                  |
                    FigureViewport + PhysicsRuntime
                                  |
             domain adapter -> mathematical solver -> runtime output
                                  |
                    renderer/Canvas/SVG + controls + telemetry
```

Each stage has a different responsibility. A failure must be diagnosed at its stage instead of “fixed” by changing a later solver or substituting a demonstration scene.

### 3.1 Upload and source identity

The API reads the upload in 64 KiB chunks and rejects it when accumulated bytes exceed the size limit. It then calls `ai/ingestion/UploadService.py`.

`UploadService` rejects empty data, oversized data, unsupported declared MIME types, and undecodable images. It obtains the image's native width and height, computes SHA-256, assigns a UUID, writes the bytes into `storage/uploads/`, and copies the file into `apps/web/public/uploads/`. Saved names resemble `diagram_<uuid-prefix>.png`.

The filename is metadata. The hash is identity/cache metadata. Neither is allowed to determine the physical domain, subtype, solver, or expected answer. Renaming a circuit image to `pendulum.png` must not turn it into a pendulum.

The resulting `SourceAsset` identifies the actual source. Its native dimensions are authoritative. The serialized response omits the internal storage path.

### 3.2 Page representation

`ai/ingestion/PageIRBuilder.py` constructs `PageIR` with:

- The source asset identity, dimensions, URL, MIME type, and hash.
- A `coordinateSpace` of `source_px`, with origin at the top left.
- `region_001`, covering the complete image and labeled `whole_image`.
- `figure_001`, coextensive with that region.
- Initially empty text blocks, which the evidence pipeline can populate from OCR.

The region is honestly labeled `user_supplied`. A confidence of 1.0 for this whole-image wrapper means the system knows the supplied image rectangle. It is not VLM confidence or proof of physics understanding.

The name “PageIR” anticipates future document processing. In this flow it describes one supplied crop, not a fully analyzed textbook page.

### 3.3 Semantic interpretation

`BookUnderstandingPipeline` calls `PhysicsVisionAnalyzer`, which reads the real stored bytes and delegates to a `VisionProvider`. Normal operation uses `GeminiVisionProvider`; offline tests inject `MockVisionProvider`.

The VLM determines broad meaning: whether this is physics, whether the model is supported, which domain/subtype applies, which semantic entities appear, and their rough relationships. It can report visible label text as **unverified semantic evidence**.

It must not produce authoritative physical values or measured geometry. Immediately after this stage:

```text
BookIR.parameters = {}
BookIR.geometry = {}
BookEntity.position_source_px = null
BookEntity.geometry = null
```

Any coarse VLM bounding box is isolated under `attributes["vlmApproxBBox"]`, with localization marked unverified. It can help orient interpretation; it is not a measured source landmark.

A clear supported semantic result initially produces `NEEDS_REVIEW`, because classification alone cannot authorize execution. Provider failure produces unresolved IR with a recorded error type and message; it does not silently switch to canned physics.

### 3.4 Evidence extraction and grounding

`ai/evidence/pipeline.py` supplies the current extraction orchestration. It skips grounding for non-physics, unknown, unsupported, or unidentified model results. For a supported model, it loads and checks the native image and selects the registered subtype grounder.

The extraction sequence is:

1. **OCR:** obtain text, positions, confidence, provider identity, and alternatives.
2. **Classical CV:** detect source-pixel geometry appropriate to the selected subtype.
3. **Segmentation:** use SAM 2 where prompted and available to corroborate an object mask.
4. **Fusion:** associate semantic entities, measured geometry, and textual quantities.

The result is a grounded `BookIR` with evidence records, parameter candidates, associations, and diagnostics. A text token becoming a number is not enough: the system must associate it with the right physical quantity or component.

Examples of the distinction:

- A circular region can be a bob candidate; it still needs the appropriate string/pivot context.
- A visible `20` may describe a length, angle, resistor, page number, or unrelated caption.
- A velocity arrow's direction can support an angle; its drawn length does not establish speed in metres per second.
- An OCR label's center is not the resistor body's center.
- Two crossing strokes do not automatically mean an electrical junction.

### 3.5 Resolution and compilation

The API next runs `AutoResolutionEngine.resolve()` and `ResolutionEngine.auto_resolve()`. These are distinct current components with different policies, described in Section 8.

`ReadinessEvaluator` checks whether the grounded/resolved IR actually satisfies its physical-model requirements. Only a sufficiently resolved IR may become `READY_TO_COMPILE`.

`PhysicsCompiler` then performs its own checks, re-evaluates readiness, builds a canonical `PhysicsScene`, and validates the emitted structure. A successful result is `READY` with a scene. Other compiler outcomes carry `scene: null`.

### 3.6 Browser execution

`SimulationOrchestrator` interprets the backend response. A compiled scene is passed to `InteractiveFigure`. That component installs the image, configures the viewport, creates the runtime, attaches appropriate rendering, displays parameter controls, and subscribes to solver state.

The canonical uploaded-file circuit runs through the **browser** `CircuitAdapter`, `CircuitCompiler`, and `CircuitSolver`. It does not automatically call the separate Python `/api/circuit/solve` endpoint. Likewise, having a Python solver or a p5 laboratory module somewhere in the repository does not establish that it participates in this path.

## 4. Data contracts: what each representation means

An IR is an *intermediate representation*: structured information passed between stages. An IR is not inherently executable.

| Representation | Meaning | Main contents | May authorize simulation by itself? |
|---|---|---|---|
| `SourceAsset` | The uploaded source identity | UUID, MIME type, original filename, byte size, dimensions, SHA-256, internal saved path | No |
| `PageIR` | What image/page regions and text blocks exist | Source reference, coordinate space, regions, figures, OCR text blocks | No |
| Semantic result | What kind of physics the image seems to depict | Classification, domain/subtype, confidence, roles, relationships, unverified labels | No |
| `BookIR` | Meaning plus evidence and resolution state for this figure | Entities, geometry, parameters, evidence, assumptions, provenance, decisions, review status | Only after backend checks, through compilation |
| `PhysicsCompilerResult` | Result of attempting compilation | `status`, `scene`, issues, BookIR status | Only `READY` with a valid scene is executable |
| Canonical `PhysicsScene` | Solver-facing physical model and presentation context | Version, domain, subtype, dimensions, parameter specs, objects, geometry, circuit graph if relevant | Subject to runtime validation |
| Runtime output | What the solver currently computes | State, geometry, telemetry, events, editable parameters | It is simulation state, not new source evidence |

### 4.1 Important BookIR fields

`BookIR` has `source_asset_id`, `page_ir_version`, `figure_id`, `domain`, `subtype`, `entities`, `relationships`, `parameters`, `geometry`, `assumptions`, `provenance`, `evidence`, `confidence`, `status`, and `status_notes`.

The resolution layer adds `resolutions`, `review_issues`, `parameter_provenance`, `calibration`, and an optional identifier. Python field names and serialized JSON names can differ: for example, a source reference may be `source_asset_id` in Python and `sourceAssetId` in BookIR JSON. API request envelopes still use `book_ir`.

`BookEntity` supplies an ID, semantic type, optional label, measured position/geometry when available, attributes, and evidence references. Entity identity must survive grounding and compilation. Renaming IDs to hide duplicates can break relationships and evidence ownership.

### 4.2 Physical values and provenance

A `PhysicalValue` carries a value, unit, status such as `observed`, `derived`, `assumed`, or `unknown`, and an optional `ProvenanceRecord`.

Illustrative value record, using the serializer's style:

```json
{
  "value": 0.8,
  "unit": "m",
  "status": "observed",
  "provenance": {
    "source": "ocr",
    "evidenceRefs": ["ev_ocr_length_label"],
    "confidence": 0.9,
    "notes": "Length label associated with the measured pendulum string."
  }
}
```

This is an explanatory fragment, not a complete runnable BookIR. Some structural parameters, including circuit node/component lists, are stored as lists with separate provenance rather than as scalar `PhysicalValue` objects. Consumers must not assume a uniform numeric-wrapper shape for every entry.

Provenance can additionally preserve policy ID/version, whether the user accepted a value, its superseded value, and the evidence from which it was derived. Relevant sources include OCR, CV, diagram measurement, derivation, user supply/confirmation/correction, author overrides, policy defaults, automatic policies, and student exploration.

Do not simplify a parameter to just a number when doing so discards its unit, evidence, or assumption status.

### 4.3 Evidence records and candidates

`shared/schemas/evidence.py` defines source points, bounding boxes, lines, polygons, OCR tokens/regions/candidates, parsed physical-value candidates, parameter associations, masks, evidence records, and grounding diagnostics.

An evidence record identifies its extraction method, source asset/figure, provider/model, confidence, verification flag, `source_px` coordinate frame, payload, and metadata. OCR regions can retain multiple engine outputs. This preserves disagreements instead of replacing one engine's raw text with another engine's guess.

A parameter association records the proposed target entity and physical quantity, value/unit, supporting evidence, checks, confidence, and an association state: associated, ambiguous, or rejected.

The important distinction is **candidate versus accepted parameter**. A plausible OCR candidate can remain in `provenance.candidate_parameters` without becoming trusted executable input.

### 4.4 Canonical scene shape

The active compiler emits `schemaVersion: "1.0"`. Its scene contains an ID, domain/subtype, source metadata, a `source_px` coordinate space, parameter specifications, geometry, objects, assumptions, and render metadata. Optics scenes also expose `elements` for compatibility. Circuits add a `circuit` graph.

The scene may contain `coordinateSystem` alongside `coordinateSpace` as a compatibility alias. That does not authorize a second independent coordinate transform.

Parameter keys are normalized for runtime consumption. Examples:

| BookIR quantity | Typical runtime scene key |
|---|---|
| `launch_speed` | `speed` |
| `launch_angle_deg` | `angle` |
| `focal_length_px` | `focalLength` |
| `object_height_px` | `objectHeight` |
| Pendulum measured/derived angle | `initialAngle` |
| Prism `n` | `refractiveIndex` |
| Prism `apex_angle_deg` | `apexAngle` |

Compiler provenance preservation runs after domain population and attaches the actual evidence source and an `evidenceProvenance` record where available. Initial literals inside a population helper are not necessarily the final emitted provenance.

Several schema generations coexist. `shared/schemas/physicsScene.schema.json` is the canonical v1 schema file; `physics_scene.json` and `physics_scene_full.json` describe other contracts. Dataclass versions, the API's `2.1` version, and a circuit contract's v3 label are different version systems. They must not be treated as one scene version.

## 5. Semantic decisions and provider behavior

### 5.1 Classification vocabulary

| Classification | Interpretation | Expected semantic domain/subtype |
|---|---|---|
| `supported` | Recognized physical model from the seven-model vocabulary | Valid domain/subtype pairing |
| `unsupported_physics` | Physics that has no supported automatic model | Both null |
| `non_physics` | Image does not depict a relevant physics scenario | Both null |
| `unknown` | Insufficient semantic certainty | No committed physical subtype; review/abstention |

`unsupported_physics` and `non_physics` are classifications, never subtype strings. `isPhysics` is a JSON boolean or null, never the strings `"true"` or `"false"`. Confidence must be finite and within [0, 1]. Relationships must refer to declared entities.

The Gemini provider discards relationships whose endpoint IDs do not resolve, records that loss, and then validates the remaining payload. It does not invent missing entities to repair dangling IDs.

### 5.2 Confidence thresholds and limits

`PhysicsVisionAnalyzer` defaults to these acceptance thresholds:

- Physics confidence: 0.80.
- Domain confidence: 0.70.
- Subtype confidence: 0.70.

Insufficient confidence downgrades interpretation and can retain the old interpretation as a candidate. Confidence is a semantic signal, not evidence of numerical correctness or a calibrated probability that the final simulation is correct.

The repository's required conservative policy limits VLM physics confidence to 0.99, domain to 0.98, subtype to 0.96, and entity/relationship/label/candidate confidence to 0.95. Supported-result overall confidence is the hierarchical minimum. A verified human/ground-truth value can legitimately have 1.0 where an unverified VLM value cannot.

**Implementation nuance:** the inspected semantic normalization clamps relevant values when they are `>= 1.0`; it does not universally clamp every intermediate value above the stated cap. For example, a provider value of 0.999 can escape a nominal 0.95 cap. Therefore, describe the caps as repository policy and partially implemented enforcement, not as a fully proven invariant.

### 5.3 Gemini configuration and retries

`GeminiVisionProvider` reads `GEMINI_API_KEY`. Model selection prioritizes an explicit constructor argument, then `GEMINI_MODEL`, then the code default `gemini-3.1-flash-lite`.

The fallback list in this snapshot additionally tries `gemini-3.1-flash-lite`, `gemini-3.8-flash`, and `gemini-3-flash-preview`, avoiding duplicates. It retries selected transient 502/503/504/unavailable failures once with a one-second delay before moving on; quota/rate-limit and missing-model errors move to a different model. Authentication failures are not treated as reasons to fabricate semantic output.

These are **model names configured in this checkout**, not a claim that every named model is currently available from the provider. `.env.example` currently selects `gemini-3.8-flash`, which differs from the constructor default. Confirm operational availability from actual provider responses when debugging deployment.

The provider requests JSON with a response schema and low temperature. It records used model, prompt version, timestamp, latency, and whether fallback/retry occurred. `available()` largely checks configuration presence; it does not prove a successful remote request.

`USE_MOCK_VISION=true` activates a fixed pendulum interpretation in the default pipeline. This is an offline development switch, not a universal offline classifier. Do not report its outputs as real image-recognition success.

## 6. How OCR, CV, and SAM 2 cooperate

### 6.1 OCR

The current default is `MultiOCRRouter`, combining:

- `RapidOCRProvider`, using local ONNX OCR, primarily for Latin text/digits and initial text regions.
- `EasyOCRBanglaProvider`, for Bengali/English recognition.
- Greek-symbol visual recognition and a physics-symbol candidate resolver.
- An optional formula-recognition interface.

The default formula recognizer is **unavailable**. An interface and mocks do not establish a deployed general LaTeX/formula model. Tesseract references in older prose do not make Tesseract the current default OCR backend.

The router preserves raw text and provider identity, alternatives, source bounds, and recognition metadata. Bengali Unicode and digits must survive normalization. Physics symbols such as theta, omega/ohm, and mu require contextual disambiguation; `Ω`, `O`, and `0` are not interchangeable facts.

The uncommitted EasyOCR change defaults to CPU unless `EASYOCR_USE_GPU` is enabled, with an attempted CPU retry after GPU extraction failure. This describes the inspected working tree, not the committed baseline alone.

The current evidence pipeline avoids treating repeated schematic glyphs such as zigzags recognized as `WWW` as ordinary OCR text. Circuit masking uses selected OCR boxes and connected-component suppression to avoid erasing adjacent wires. These mechanisms are heuristics and need negative-case evaluation.

### 6.2 Classical CV and grounders

Subtype-specific extractors live under `ai/evidence/cv/`; subtype-specific fusion lives under `ai/evidence/grounding/`. `GrounderRegistry` registers all seven model families.

The basic responsibilities are:

| Model | Visual evidence needed |
|---|---|
| Pendulum | Pivot, bob, connecting string/rod, measured length/radius, release geometry |
| Projectile | Launch body/origin, ground/trajectory context, direction or angle evidence |
| Thin lens | Lens center/axis, aperture, focal evidence, object evidence if printed |
| Spherical mirror | Pole/axis, mirror geometry/type, focal or curvature evidence |
| Interface refraction | Boundary, normal/incidence point, relevant ray geometry and optical quantities |
| Prism | Polygon vertices, angle/shape, incident-ray geometry if present |
| DC circuit | Actual component symbols, measured terminals, supported conductor paths, junctions, polarity and switch state |

Measured geometry can support derived quantities, but a textbook drawing is not automatically to physical scale. A pixel distance cannot be reported as centimetres without calibration. A ray angle in a schematic may support a diagram model while still requiring care about whether the source claims quantitative accuracy.

### 6.3 SAM 2

`SAM2SegmentationProvider` uses SAM 2.1 with the expected checkpoint `checkpoints/sam2.1_hiera_tiny.pt` and configuration `configs/sam2.1/sam2.1_hiera_t.yaml`. Loading is lazy, and missing dependencies/checkpoints yield an unavailable result rather than a substitute physics answer.

Prompts use candidate bounding boxes and measured positive points. Masks preserve source dimensions, bounds, centroids, polygon approximations, area, prompt provenance, and encoded pixels.

The provider caches a model/predictor and image embedding. The current cache signature includes full image-pixel content, shape, and predictor identity. A reentrant lock protects mutable predictor operations across concurrently offloaded requests.

For circuits, `segment_circuit_candidates()` treats masks as **corroboration**. It checks frame, region overlap, area, encoding, coverage of measured strokes, and swallowing of neighboring objects. A SAM mask does not create electrical connectivity, replace independently measured terminals, or supply resistor/voltage values.

## 7. Circuit grounding: the most active implementation area

This section describes the current `ai/evidence` circuit path, not the older `ai/perception/circuits` analyzer.

### 7.1 Symbol and path extraction

`CircuitCVCandidateExtractor` checks that it is operating in the decoded native source frame, estimates raster ink and stroke width, suppresses likely text glyphs, and calls `detect_symbols()`.

The current detector works on physical ink candidates for resistors, voltage-source plate symbols, and switches. It measures bounds, centers, orientation, symbol paths, and terminals. Semantic entity types can guide candidate handling; the current implementation specifically gates switch detection on the provided semantic types. This is semantic guidance, not permission to manufacture a symbol.

Detected component bodies are removed from a separate conductor raster before skeleton tracing. This prevents a resistor body or switch arm from being treated as an ordinary conducting wire.

`circuit_paths.py` traces continuous skeleton paths between endpoint/junction clusters. It prunes short skeleton spurs without intentionally bridging disconnected ink. At an unmarked four-way crossing it keeps opposite paths separate; a measured junction dot can join them. Thus electrical connectivity is not inferred simply from proximity or overlap on the page.

### 7.2 Geometry validation

`CircuitGeometryValidator` checks path bounds, raster support, gaps, and intersection with component bodies. In this snapshot a verified wire path requires support fraction at least 0.98 and maximum gap no larger than `max(1, stroke*0.4)`.

It separately checks each component's identity strokes, bounds, terminal placement, attachments to verified wire endpoints, switch state, and voltage-source polarity. Components can remain ambiguous even when their broad type is recognized.

The pre-existing working changes relax some component checks: symbol support from 0.95 to 0.80; endpoint search allowance to `max(stroke*8, 36)` plus switch-contact radius; connector support to 0.75, or a very short-distance allowance. These thresholds describe heuristics. They are not measurement-error guarantees.

### 7.3 Association and graph construction

`CircuitGrounder` clusters OCR text into component labels/values, associates semantic entity IDs with those labels, and performs one-to-one assignment to verified physical symbols using compatible type and spatial costs.

OCR can tell the grounder which measured symbol likely owns `R1 = 10 Ω`. It must not provide the symbol's authoritative terminals or center. VLM-visible numbers are not consumed as electrical values.

`build_conductor_graph()` unions verified paths through shared measured endpoint/junction identities. Only conductor islands attached to component terminals are retained. An isolated caption stroke or current arrow is not automatically a circuit wire.

The resulting graph has declared nodes, wires with source-pixel polylines, and components with two measured terminals connected to node IDs. Each physical component retains its semantic entity ID. Voltage-source terminal order reflects the verified polarity. The source's negative-side node can become the reference node.

### 7.4 Integrity and readiness

`validate_circuit_integrity()` checks malformed structures, duplicate/missing IDs, dangling entity relationships, missing physical symbols, missing terminals, inconsistent nodes, unresolved evidence references, invalid source coordinates, source/figure identity mismatches, unverified switch state, disconnected islands, and unfinished geometry/topology validation.

The BookIR can record separate `circuit_validation` flags for semantic, geometry, topology, referential integrity, and physics readiness. `circuit_topology.verified_connectivity` is a separate explicit condition. A list of components plus a successful linear solve is not enough to prove that the graph matches the original picture.

Compilation also requires an actual source, finite component values with compatible units, positive resistances, declared nodes, and a non-shorted voltage source. Missing resistor or voltage values are not automatically supplied by the current circuit auto-resolution path.

Circuit drawings use pixel geometry for registration and graph topology for electrical equations. **No `pixels_per_meter` is needed to solve a resistor network.** Introducing a mechanics-style spatial calibration into circuit readiness would confuse two independent concepts.

### 7.5 What remains uncertain in the working circuit repair

Eight relevant files were already modified before this report was requested; they are listed in Section 17. Some changes improve text suppression, symbol detection, and CPU fallback. Others broaden association acceptance and remove the previous near-equal-assignment ambiguity rejection.

That broadening is a concrete review risk: same-type components without decisive labels may be assigned even when their identities are interchangeable. Relaxed raster/attachment thresholds may recover real scans but can also accept false attachments. These are reasons to examine adversarial and real-image cases, not established claims that every such case fails.

A recorded-source replay test now skips when its replay helper is unavailable. A skipped replay must not be presented as a passed real-source validation.

## 8. Resolution, assumptions, and the meaning of “no fabrication”

### 8.1 Requirement catalog

`ai/resolution/requirements.py` defines `ModelRequirementSpec` and `ParameterRequirement`. A specification names required entity roles, required geometry, quantities, physical dimensions, allowed units/categories/ranges, alternatives, aliases, and allowed policies.

The current broad requirements are:

| Subtype | Required visual/model inputs |
|---|---|
| Pendulum | Pivot, bob position, string length in pixels, bob radius in pixels, gravity, mass, damping, and physical length or a pixel/metre calibration; initial state must also be available to the compiler/runtime |
| Projectile | Launch position, speed, angle, gravity, pixels per metre, and visual radius |
| Thin lens | Lens center, focal length in pixels, aperture; object position/distance and height must be complete when an object is included |
| Spherical mirror | Pole, focal length in pixels, concavity category, aperture |
| Interface refraction | Boundary and normal geometry, both refractive indices, and incident angle or ray-source position |
| Prism | Vertices, ray origin/direction, refractive index, apex angle |
| DC linear | Component and node graph, grounded component identities/terminals/values, valid connectivity and reference node |

This table summarizes the combined boundary. The requirement catalog alone is not the full compiler: compiler and adapter checks can impose additional conditions.

### 8.2 Resolution decisions

`ResolutionAnalyzer` identifies satisfied, missing, ambiguous, and conflicting requirements and generates review issues. Issues contain parameter/entity targeting, readable questions, candidate evidence, allowed actions, units, policies, help text, and blocking status. Some questions have Bangla text.

`ResolutionEngine` can accept a user-supplied quantity, confirm a candidate, correct a candidate, apply a named policy, or remove a previous decision. Decisions retain canonical and original values/units, evidence references, source, timestamp, policy metadata, user acceptance, and superseded values.

A correction should add a resolution layer while preserving raw OCR/CV observations. It should not erase the original text or overwrite its provider identity.

### 8.3 Two different automatic-resolution mechanisms

**`ResolutionEngine.auto_resolve()`** normalizes aliases, attempts evidence-based calibration, and applies policies only where the policy permits use without opt-in. It does not automatically confirm every high-confidence OCR candidate.

**`AutoResolutionEngine.resolve()`** is the current ingestion stage for additional disclosed modeling assumptions. After grounding checks it uses a restricted policy set and records `resolved_by="auto_policy"`, `user_accepted=false`, policy identity/version, and assumed values. The readiness evaluator contains an explicit allowance for this automatic-policy path.

These are different behaviors. A statement that *all policies always require a fresh user click* is inaccurate for this checkout.

### 8.4 Examples of current automatic assumptions

| Situation | Current behavior if prerequisites are met | Meaning |
|---|---|---|
| Grounded pendulum lacks gravity | Named standard-Earth policy: 9.80665 m/s² | Model assumption, not OCR evidence |
| Grounded pendulum lacks damping | Named zero-damping policy: 0 1/s | Ideal-model assumption |
| Grounded pendulum lacks mass | Named unit-mass policy: 1 kg | Energy-model setup; not measured bob mass |
| Grounded pendulum lacks physical length | Named standard-length policy: 1 m | Assumed physical scale, not a measured textbook length |
| Grounded projectile lacks quantities | Restricted policies can provide 20 m/s speed, 25 px/m scale, and standard gravity | Disclosed demonstration assumptions |
| Grounded prism lacks index | Crown-glass policy: 1.52 | Assumed material model |
| Measured lens aperture but no focal value | Focal-ratio policy can set focal length to half the aperture | Demonstration optical power, not a physical inference from lens silhouette |
| Lens/mirror has no printed object | Policies can create exploration distance/height based on focal length/aperture | Generated exploration object, not an observed arrow |
| Measured prism has no printed incident ray | A policy can generate a horizontal exploration ray toward the left face | Generated input ray, not an observed source ray |

The lens/mirror exploration distance is based on two focal lengths but is bounded by available source-image space; height is based on 35% of measured aperture. The code records assumptions instead of claiming these are printed facts.

**Important boundary:** the automatic prism helper writes the assumed ray into geometry as well as recording policy provenance. Therefore, geometry's mere presence is not proof that it was observed. Similarly, a focal-length field can be present because of an assumption. Always inspect provenance and `scene.assumptions`.

The registry contains other named policies, including standard optical media, apertures, and example circuit values. Registry presence does not mean each policy is allowed for each subtype or automatically applied. In particular, current DC circuit normalization requires measured/resolved electrical values rather than silently choosing the registry's example resistance or voltage.

### 8.5 Readiness and reversibility

`ReadinessEvaluator` combines requirement analysis with checks for physical units, finite/range-valid numbers, categories, geometry ambiguity, parameter-specific provenance, agreement between current values and recorded decisions, policy validity, and calibration.

If required evidence is removed or a decision conflicts with the current parameter, readiness must be revoked. A previously stored `READY_TO_COMPILE` string is not sufficient: compilation rechecks the actual IR.

The correct interpretation of “no fabrication” here is: VLM guesses cannot become facts, compiler omissions cannot be patched with hidden constants, and model assumptions must remain attributable. The automatic-assumption exceptions above mean the current product is **not** a pure “only source-observed values, always manually approved” system. Tightening that behavior would be a product/architecture change, not a documentation-only correction.

## 9. Status vocabularies and backend authority

Three related status systems coexist:

| Layer | States | Meaning |
|---|---|---|
| BookIR | `UNRESOLVED`, `NEEDS_REVIEW`, `UNSUPPORTED`, `READY_TO_COMPILE` | Understanding/evidence readiness |
| Compiler | `UNRESOLVED`, `NEEDS_REVIEW`, `UNSUPPORTED`, `READY` | Whether a runnable scene was emitted |
| Orchestrator | Twelve UI lifecycle states below | What the browser session is doing |

The twelve orchestrator states are:

```text
IDLE
UPLOADING
ANALYZING
NEEDS_REVIEW
APPLYING_RESOLUTION
EVALUATING
READY_TO_COMPILE
COMPILING
READY_TO_SIMULATE
SIMULATING
ERROR
UNSUPPORTED
```

The principal review loop is:

```text
NEEDS_REVIEW -> APPLYING_RESOLUTION -> EVALUATING
                    ^                    |
                    +--- still blocked --+
                                         |
                               READY_TO_COMPILE
                                         |
                                      COMPILING
                                         |
                                READY_TO_SIMULATE
                                         |
                                     SIMULATING
```

The frontend does not have authority to invent `READY_TO_COMPILE`, add missing physics values, or ignore compiler refusal. A monotonically increasing operation ID prevents stale async responses from replacing a newer session's results.

The ingestion response also exposes a normalized lowercase/hyphenated status, for example `needs-review`, while the nested compiler has `NEEDS_REVIEW`. Clients must normalize deliberately.

**Serialization nuance:** semantic `unsupported_physics` correctly gives BookIR `UNSUPPORTED` with null domain/subtype. The compiler checks unknown domain/subtype early and can emit `UNRESOLVED` for such IR. The orchestrator also checks BookIR status and can still show `UNSUPPORTED`. A downstream GPT must inspect the full envelope rather than assuming every status field always agrees.

## 10. Actual current browser behavior versus intended UX

The orchestrator's `startSimulation()` is a separate operation that requires a compiled scene. This is a useful lifecycle boundary. It does not, by itself, establish which visible user action invokes it.

In the inspected `main.js`, the uploaded-file **Generate Simulation** handler loads a successful scene, calls `orchestrator.startSimulation()`, and calls `activeFigure.play()`. Thus a ready upload can begin after Generate Simulation without an additional Start Simulation click.

When the orchestrator ends in `NEEDS_REVIEW`, that handler also attempts compilation. The backend can still reject it. Calling `compile()` is not evidence that the browser successfully bypasses backend readiness.

`PhysicsReviewModal` exists and supports candidate confirmation/correction, quantity entry, policy application, and explicit Start Simulation actions. Its current state-change handler does **not** automatically open the dialog. It renders when explicitly opened, such as through **Review Setup** on an active figure. Some internal geometry/scale issues are filtered out of the student-facing issue list.

Two source-level gaps matter for future decisions:

1. **Review response propagation:** `/api/resolution/review` returns an updated `book_ir`, but `SimulationApi.review()` currently returns a reduced object that omits it. The orchestrator has code to adopt a returned `book_ir`/`bookIR`, but that data is lost by this client wrapper. Review-time normalization can therefore diverge from the browser's retained IR.
2. **Ready-banner logic:** the modal can show a ready banner when its filtered unresolved issue list is empty, even if hidden geometry blockers remain. Backend compilation still provides the authoritative gate, but presentation can overstate readiness.

These observations concern the current flow. They should not be dismissed as archive behavior, and they should not be promoted to proven end-to-end failures without a reproducing response/browser case.

The orchestrator tracks time-to-ready, issue count, confirmations, corrections, manual entries, accepted policies, and failed resolutions. Upload progress is coarse client messaging around a request; it is not a server-streamed measurement of every extraction stage.

## 11. Source-pixel registration and physical calibration

### 11.1 Three coordinate concepts

1. **Source pixels:** native image positions, such as a pivot at `(240, 70)` in a 900-by-600 image.
2. **Viewport/CSS pixels:** where those positions appear in the current browser layout.
3. **Physical units:** metres, seconds, kilograms, volts, ohms, and so on.

They are distinct. Enlarging the browser does not lengthen the physical pendulum or change BookIR geometry.

### 11.2 CoordinateMapper

For source dimensions `Ws, Hs` and viewport dimensions `Wv, Hv`, aspect-preserving contain mapping is:

```text
s  = min(Wv/Ws, Hv/Hs)
ox = (Wv - s*Ws)/2
oy = (Hv - s*Hs)/2

x_view = ox + s*x_source
y_view = oy + s*y_source

x_source = (x_view - ox)/s
y_source = (y_view - oy)/s
```

Device-pixel ratio affects canvas backing resolution separately from CSS positions. Pointer input must be inverted through the mapper before updating source-coordinate interactions.

### 11.3 FigureViewport

`FigureViewport` owns image/overlay registration, sizing, resize observation, and mapping context. The image and overlay must occupy the same content rectangle. Renderers use its supplied context instead of inventing another contain offset.

An image-backed `InteractiveFigure` requires valid native dimensions and checks them through its loading path. Temporary constructor defaults such as 800-by-600 are scaffold sizes, not permission to replace a real image's dimensions.

Calibration-anchor reticles help inspect registration, but correct viewport registration does not prove that CV located the correct physical object. There are two independent errors: selecting the correct point in the image and displaying that point in the right place.

### 11.4 Physical calibration

`CalibrationEngine` can derive `pixels_per_meter` from grounded physical and visual lengths. A simple pendulum relationship is:

```text
pixels_per_meter = measured_string_length_px / resolved_length_m
```

If length is assumed under a policy, the resulting scale inherits that modeling assumption. It must not be described as a measured source scale.

Optical calculations can use consistent pixel distances without reporting SI lengths. Circuits use topology and electrical quantities; diagram scale does not enter Ohm's law or MNA.

## 12. PhysicsRuntime and interaction architecture

`engine/core/PhysicsRuntime.js` is the book-neutral runtime facade. It normalizes allowed legacy aliases, validates the canonical scene, resolves capabilities, selects a domain adapter through `SolverRegistry`, initializes it, subscribes to state, and exposes normalized output.

Its main operations are `load`, `start`/`play`, `pause`, `step`, `reset`, `updateParameter`, `getParameters`, `getState`, `getOutput`, `resize`, and `dispose`/`destroy`.

`SimulationAdapter` supplies the common lifecycle, original-scene snapshot, listeners, parameter override bookkeeping, and validated unit-aware parameter updates. Its reset restores the initial scene. Domain adapters implement their own model initialization, solving, state/output production, and reactions to parameter updates.

`SimulationCapabilityRegistry` decides what may be edited or dragged. It binds interactions to real object IDs and semantic roles. It must respect authored `editable: false` and must not create missing physical values merely to make a slider or drag handle available. Missing geometry can disable a drag handle while still allowing a valid scalar control.

`RendererRegistry` resolves presentation separately. The current canonical registry explicitly registers optics and circuit renderers; mechanics visual simulation is attached through its adapter/simulation implementation. Therefore, it is inaccurate to say every domain uses an identical separate renderer class.

The uploaded circuit renderer in `features/simulations/circuits/CircuitRenderer.js` builds an **SVG overlay**, with layers for wires, flow, nodes, switches, components, and handles. The optics renderer and mechanics views use their appropriate canvas/view implementations. “All current overlays are p5 canvases” would be incorrect.

Runtime output contains a domain/subtype, time, state, geometry, telemetry, events, and editable parameters. UI components render that output; they should not independently recompute authoritative physics results.

## 13. Mathematical behavior by domain

### 13.1 Pendulum

The current mechanics adapter validates physical length, gravity, initial angle, mass, damping, and visual geometry before initialization. Both headless execution and browser simulation use the pure `PendulumKernel` from `engine/mechanics/kernels.js`.

The differential equation is:

```text
d(theta)/dt = omega
d(omega)/dt = -(g/L)*sin(theta) - damping*omega
```

It integrates with fourth-order Runge–Kutta using substeps no larger than 1/240 second. The rendered bob position uses the measured pivot and visual string length, while the dynamics use physical `L` and `g`.

Computed energy is:

```text
speed = |omega*L|
PE = m*g*L*(1 - cos(theta))
KE = 0.5*m*speed^2
```

The familiar `T ≈ 2π*sqrt(L/g)` is the **small-angle** period approximation. The nonlinear integrator is not replaced by that approximation at large angles. Unit mass leaves ideal angular motion unchanged but changes reported energy, so an assumed mass must remain disclosed.

### 13.2 Projectile

`ProjectileKernel` implements ideal motion without drag:

```text
vx0 = v0*cos(theta)
vy0 = v0*sin(theta)
x(t) = vx0*t
y(t) = vy0*t - 0.5*g*t^2
vx(t) = vx0
vy(t) = vy0 - g*t
```

Physical upward displacement maps to decreasing source-image y. Speed and angle controls change the live model, not the source evidence.

Its built-in flight-time/range formulas assume landing at launch height:

```text
flight_time = 2*vy0/g
time_to_apex = vy0/g
max_height = vy0^2/(2*g)
range = vx0*flight_time
```

Do not promise arbitrary elevated-target/terrain collision from this model. A further edge case is that nonnegative gravity is accepted, while these derived formulas divide by `g`; zero-gravity behavior requires dedicated handling/verification before making correctness claims.

### 13.3 Thin lens

`solveThinLens()` uses object distance `u = lensX - objectX` and computes:

```text
v = f*u/(u - f)
m = -v/u
imageX = lensX + v
imageHeight = objectHeight*m
```

This convention corresponds to `1/f = 1/u + 1/v` with the chosen positive object-distance magnitude. Positive `f` is converging; negative `f` is diverging. The solver distinguishes real/virtual, upright/inverted, and relative image size, and creates principal rays and virtual extensions.

Near `u = f` it explicitly returns an image-at-infinity state. Runtime analytic infinity is different from accepting NaN/infinite uploaded physical parameters. UI/rendering must handle the special state without trying to draw an ordinary finite image coordinate.

Some historical prose mixes lens sign conventions. Preserve the implemented coordinate/sign convention when comparing a numerical answer; do not “correct” the engine based only on a mismatched textbook formula notation.

### 13.4 Mirrors

`solveMirror()` uses the same algebraic distance relation with mirror-specific placement. Concave focal length is positive, convex negative; `imageX = mirrorX - v`. A plane mirror uses `v = -u` and magnification +1. Principal-ray output distinguishes actual and virtual paths.

The presence of a plane-mirror branch in this numerical engine does not prove reliable automatic plane-mirror upload grounding. The canonical upload family remains `spherical_mirror`, and its requirements/grounding still apply.

### 13.5 Interface refraction

The governing relation is Snell's law:

```text
n1*sin(theta1) = n2*sin(theta2)
```

For passage from higher to lower refractive index, the critical angle is `asin(n2/n1)`. Above it, the model yields total internal reflection. Rays, normals, angle annotations, and telemetry should follow the same geometric model.

The current requirement catalog models a horizontal boundary and vertical normal through source-coordinate quantities such as `boundary_y` and `normal_x`. It should not be described as a general arbitrary curved-interface solver.

The automatic layer can derive incident angle from independently grounded indices and a refracted angle, rejecting an impossible sine value. Such a result is derived evidence, not a direct image measurement.

### 13.6 Prism

The prism engine intersects rays with polygon edges, computes surface normals, applies reflection/refraction, and constructs successive ray segments. It can report deviation and total internal reflection. For the usual triangular-prism geometry, `deviation = i1 + i2 - apex_angle`.

The minimum-deviation relation `n = sin((A + delta_min)/2)/sin(A/2)` applies under its usual symmetry assumptions. It is not a way to invent an index from an unlabeled arbitrary prism drawing. Current ingestion can instead use a disclosed material-index policy.

### 13.7 Linear DC circuits

The current browser circuit adapter compiles the circuit graph and solves it locally through `CircuitSolver.js` and `LinearSystem.js`. Modified Nodal Analysis solves `A*x = z`, where unknowns include non-reference node voltages and auxiliary currents for voltage constraints.

For a resistor between nodes i and j, conductance `G = 1/R` contributes:

```text
Aii += G; Ajj += G
Aij -= G; Aji -= G
```

A voltage source contributes an auxiliary current and the equation `Vi - Vj = Vs`. Ideal closed switches and ammeters can be represented by zero-volt constraints. Open switches omit their conducting branch. A voltmeter is a probe, not a resistive bridge added to the source graph.

The solver produces voltages, branch currents, power, and conservation-related telemetry. Changing a component value recompiles/resolves the live graph. Conventional-current visualization is derived from electrical results; particle animation speed is a display choice, not electron drift velocity.

A correct MNA solution is conditional on a correct graph and correct values. It cannot independently verify whether the image's wires were extracted correctly.

Python MNA, analytical series-RC, equation-generation, and SPICE modules also exist, but they are separate computational capabilities. RC transient and ngspice verification are not automatically part of the uploaded `dc_linear` browser path. Do not infer automatic AC/RLC/semiconductor support from their presence.

## 14. Evidence versus student exploration

There are three conceptually separate records:

1. **Raw/grounded evidence:** what OCR/CV extracted from this source.
2. **Resolved model:** user decisions and named assumptions that make the figure executable.
3. **Live experiment:** temporary slider/drag/switch changes in a running instance.

The current runtime keeps an initial scene snapshot and student overrides. `InteractiveFigure` also stores a source-scene copy. Frontend tests exercise the important invariant that changing a live pendulum length does not rewrite the BookIR length or the original compiled scene, and reset restores the starting values.

Reset restores the compiled baseline, which may include **assumptions**. It does not transform an assumed 1 m pendulum into an OCR-measured source value. “Textbook values” should be understood in that context.

The intended evidence immutability is an architectural discipline enforced through data flow and tests; the Python dataclasses are not universally frozen immutable types. A future edit can still violate the discipline if it mutates shared records carelessly.

## 15. Current API surface

The main entrypoint is `apps/api/main.py`, a FastAPI application. The current uploaded-file flow uses these routes:

| Method and route | Input | Output/responsibility |
|---|---|---|
| `POST /api/ingest` | Multipart image field `file` | Full source/IR/evidence/assumption/compiler envelope |
| `GET /api/ingest/health` | None | Pipeline capabilities, providers, OCR/segmentation information, grounders and resolution availability |
| `POST /api/resolution/review` | `{ "book_ir": ... }` | Structured review state, blocker/warning counts, readiness flag, updated BookIR |
| `POST /api/resolution/resolve` | BookIR plus one resolution action | Updated BookIR, result/readiness, `can_compile` |
| `POST /api/resolution/evaluate` | BookIR | Deterministic readiness report and updated status |
| `POST /api/resolution/compile` | BookIR | Gated compiler result, canonical scene, updated BookIR; refusal if not ready |
| `GET /api/health` | None | Basic process/SAM-import/device/version information |

Resolution actions use one of `resolution`, `policy_id` with an optional `parameter_name`, `confirm_candidate` with a parameter name, or `remove_parameter`.

Typical ingestion response fields are:

```text
success, pipeline, image_url, debug_overlay_url,
source_asset, page_ir, book_ir, compiler,
evidence, grounding, assumptions, auto_failures, failure_category,
debugId, debugTrace,
status, domain, scenario, scene, issues, width, height
```

`success: true` means the request/pipeline returned a structured response. It does not mean `compiler.status == READY`. A caller must inspect compiler status, BookIR, scene presence, and issues together.

The `pipeline` string can still say `PR-06` while the route also runs later resolution logic; it is historical labeling, not a complete current feature version.

The API serves stored images under `/uploads` and optional debug images under `/artifacts`. `EVIDENCE_DEBUG=true` requests an evidence overlay. It is a debugging artifact, not an alternative source image or automatically verified annotation.

### 15.1 Async work and remaining offloading gap

In `/api/ingest`, blocking semantic analysis, extraction, automatic resolution, and compilation are offloaded with `await asyncio.to_thread(...)`. This keeps those operations off the async event loop. SAM predictor locking separately protects its shared mutable state.

The review/resolve/evaluate/compile routes are declared async but perform their current resolution/compiler calls directly. Do not assume every expensive operation in every route is already offloaded. If those paths become heavy, they need the same event-loop review required by repository rule 17.

### 15.2 Session and storage assumptions

Resolution endpoints receive complete BookIR documents from the caller; this path does not demonstrate a server-side database of durable student sessions. Source bytes persist as files, and the browser retains the active orchestration state.

The inspected application has public static mounts and broad development CORS configuration. The main flow does not establish production authentication, per-user upload authorization, or a deployed multi-tenant storage model. A production-readiness decision needs evidence beyond a successful local build.

## 16. Where code belongs

All paths in this report are relative to `D:\AugmentedPhysics`. A GPT without the folder can use this map to request the correct source excerpts or assign bounded work.

| Responsibility | Current primary locations |
|---|---|
| API/bootstrap | `apps/api/main.py` |
| Real-file ingestion | `ai/ingestion/UploadService.py`, `PageIRBuilder.py`, `source_dimensions.py` |
| Semantic coordinator/provider | `ai/ingestion/BookUnderstandingPipeline.py`, `vision/analyzer.py`, `vision/gemini_provider.py`, `vision/mock_provider.py` |
| Current evidence orchestration | `ai/evidence/pipeline.py` |
| OCR and multilingual candidates | `ai/evidence/ocr/` |
| Current deterministic visual candidates | `ai/evidence/cv/` |
| SAM 2 and mask corroboration | `ai/evidence/segmentation/` |
| Evidence-to-entity/parameter fusion | `ai/evidence/grounding/` |
| Requirements, policies, review, units, calibration, readiness | `ai/resolution/` |
| Actual current compiler implementation | `ai/ingestion/PhysicsCompiler.py` |
| Compiler public re-export | `ai/scene_compiler/physics_compiler.py` |
| IR/evidence/resolution contracts | `shared/schemas/ingestion.py`, `semantic.py`, `evidence.py`, `resolution.py` |
| Canonical scene schema | `shared/schemas/physicsScene.schema.json` |
| Web application wiring | `apps/web/src/main.js` |
| Current HTTP client and lifecycle | `apps/web/src/features/simulations/core/SimulationApi.js`, `SimulationOrchestrator.js` |
| Figure/review/viewport UI | `apps/web/src/components/InteractiveFigure.js`, `PhysicsReviewModal.js`, `FigureViewport.js` |
| Debug inspection | `apps/web/src/features/simulations/core/IRDebugPanel.js` |
| Shared runtime and validation | `engine/core/PhysicsRuntime.js`, `SimulationAdapter.js`, `SolverRegistry.js`, `validation.js`, `units.js`, `capabilities.js` |
| Coordinate conversion | `engine/core/coordinateMapper.js` |
| Mechanics dynamics | `engine/mechanics/MechanicsAdapter.js`, `kernels.js`, pendulum/projectile simulation files |
| Optical calculations | `engine/optics/OpticsAdapter.js`, lens/mirror/interface/prism engines and `rayGeometry.js` |
| Current circuit runtime calculations | `engine/circuits/CircuitAdapter.js`, `CircuitCompiler.js`, `CircuitSolver.js`, `LinearSystem.js` |
| Current circuit presentation | `apps/web/src/features/simulations/circuits/CircuitRenderer.js` |
| Canonical renderer selection | `apps/web/src/features/simulations/core/RendererRegistry.js` |
| Demo content | `content/demo-books/`, `apps/web/public/scenes/` and related static assets |
| Tests | `tests/unit/`, `tests/integration/`, separately gated `tests/acceptance/` |
| Runtime data | `storage/uploads/`, `storage/generated/`, `storage/artifacts/`, `storage/cache/` |

**Compiler naming trap:** architecture prose calls `ai/scene_compiler/physics_compiler.py` canonical, but the inspected file re-exports `PhysicsCompiler` from `ai/ingestion/PhysicsCompiler.py`. It is not an independent competing implementation. Edit the implementation, not a re-export wrapper, when a compiler change is actually authorized.

**Router naming trap:** `engine/core/sceneRouter.js` currently exposes domain resolution and a retired `createSimulation()` that throws. Canonical execution is through `PhysicsRuntime` and `SolverRegistry`. Do not reconnect engine code to web controllers to restore the retired API.

## 17. Current working-tree state and documentation reliability

The snapshot started with these **pre-existing modified files**:

```text
ai/evidence/cv/circuit_geometry_validator.py
ai/evidence/cv/circuit_paths.py
ai/evidence/cv/circuit_symbols.py
ai/evidence/cv/circuits_cv.py
ai/evidence/grounding/circuits.py
ai/evidence/ocr/bangla.py
ai/evidence/pipeline.py
tests/unit/test_circuit_grounding_repair.py
```

Their initial diff was 284 insertions and 205 deletions across eight files. This report does not overwrite or complete that implementation work. Uncommitted changes are part of observed behavior but must not be described as merged, independently reviewed, or generally reliable.

Recent committed history relevant to this snapshot:

| Commit | Meaning |
|---|---|
| `e484676` | Current HEAD: orchestrator, review modal, circuit visualization |
| `0af4ed7` | Circuit integrity/compiler gating and vision retry changes |
| `96738be` | Continuous circuit paths, symbol validation, conductor-graph grounding |
| `f59652f` | Earlier benchmark/browser-matrix and architecture-boundary commit |

`PROJECT_CONTEXT.md` is useful historical context but contains old paths, old milestone states, and a header describing an earlier reset to `f59652f`. That is not the present HEAD. `docs/ARCHITECTURE.md` describes both intent and implementation, and its verification note predates the latest commits.

Several referenced documents were absent in the inspected checkout: root `context.md` and reports including the cited phase-progress/release/regression files. The available `docs/reports/PR_07_EVIDENCE_RESOLUTION_REPORT.md` explains an earlier milestone, but its policy counts and UX claims are not a substitute for current code inspection.

Consequently, a future GPT should prioritize current source and reproducible responses over historical completion checkmarks. It must not claim to have read absent reports or treat their quoted headline numbers as fresh measurements.

## 18. Verification evidence and its limits

This report was prepared by reading the current source, repository instructions, schemas, tests, current diff, and relevant history. It did not modify physics implementation or call live Gemini.

Verification for this snapshot:

| Check | Result |
|---|---|
| `npm test` from `apps/web` | Passed, exit code 0, across the 17 JavaScript test commands configured in `package.json` |
| `npm run build` from `apps/web` | Passed, exit code 0; Vite transformed 415 modules |
| Python unit/integration suite | Passed: 266 passed, 1 skipped, 8 warnings, exit code 0, in 171.67 seconds |
| Fresh live Gemini upload acceptance | Not run for this report |
| Manual browser inspection of all seven model families | Not run for this report |

The build produced a large-bundle warning: the main minified JavaScript bundle was approximately 1.62 MB before gzip. This is a packaging/performance observation, not a physics correctness failure.

The frontend suite covers optics mathematics, coordinate/registration mapping, circuit math, pendulum behavior, runtime/adapters, architecture boundaries, capabilities/rendering, ingestion client behavior, orchestration, review UI, no-fabrication cases, and a mocked golden path. A passing orchestration mock does not exercise every current real HTTP/client-wrapper interaction.

The Python unit/integration command used for this report is:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration -q -p no:cacheprovider --disable-warnings
```

The `pytest` package is a development/test requirement and is not declared in the main `requirements.txt`. The environment used here already has it.

The repository includes a 21-case image benchmark manifest. Its semantic labels are supplied through `MockVisionProvider`, so that benchmark measures downstream grounding/readiness/compilation under supplied semantic interpretation. It does not establish VLM classification accuracy. Some fixtures are synthetic or generated if absent; they must not be mislabeled as untouched real scans.

Historical notes mention a small live 7/7 semantic sample and earlier automatic/reviewed scene counts. Those are historical claims with limited sample scope, not current accuracy statistics for this snapshot. Browser-matrix scripts exist, but script existence does not prove a current successful run.

For credible future evaluation, report separately: semantic classification, geometry accuracy against independently annotated points, OCR and parameter ownership, circuit topology correctness, automatic-ready rate, successful reviewed completion, false-ready rate, runtime numerical correctness, and visual registration.

## 19. Running the current application

Use the repository root for Python and `apps/web` for the frontend. Current commands are:

```powershell
# Terminal 1: repository root
Set-Location D:\AugmentedPhysics
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2
Set-Location D:\AugmentedPhysics\apps\web
npm run dev
```

The usual development frontend is `http://localhost:5173`; API documentation is `http://127.0.0.1:8000/docs`. Vite proxies `/api` to port 8000. Uploaded images are copied into the frontend public directory, so do not assume the dev proxy also forwards `/uploads`.

The JavaScript app uses Vanilla JS/ES modules, Vite, and existing physics/view dependencies including Matter.js, p5, and poly-decomp. Dependency presence does not mean every current canonical model uses that library; the pendulum/projectile kernels are explicit numerical/analytical code.

Python dependencies include FastAPI/Uvicorn, multipart handling, NumPy/SciPy, OpenCV/scikit-image, Pillow, PyTorch, Google GenAI, RapidOCR/ONNX Runtime, and EasyOCR. SAM 2 installation/checkpoints and OCR model resources are additional operational prerequisites. Their existence and device availability must be checked in the actual environment.

Relevant configuration:

| Setting/resource | Purpose |
|---|---|
| `.env` | Local secrets/configuration; ignored by Git |
| `GEMINI_API_KEY` | Live semantic-provider authentication |
| `GEMINI_MODEL` | Preferred model identifier |
| `USE_MOCK_VISION` | Fixed mock semantic result for offline development; not a real classifier |
| `EVIDENCE_DEBUG` | Optional backend evidence-overlay artifact |
| `EASYOCR_USE_GPU` | Working-tree EasyOCR GPU opt-in |
| SAM checkpoint/config | Local segmentation model resources |

The older `VITE_ENABLE_DEMO_FALLBACK` switch belongs to the separate analyzer/preset compatibility route. It does not authorize the current uploaded-file orchestrator to substitute a fake scene after failure.

## 20. Decision guide for a GPT diagnosing a problem

Start with the actual request, source image, and full response. Identify the earliest failed boundary. Use this table to choose the relevant subsystem:

| Observation | First subsystem to inspect | Correct decision |
|---|---|---|
| Upload rejected before interpretation | MIME/byte validation and decoder | Fix the input/validation cause; do not change a solver |
| Domain/subtype absent with provider error | Gemini configuration/retry/provider logs | Treat as infrastructure/semantic failure, not unsupported physics |
| Clearly unsupported model | Semantic classification and support catalog | Abstain or plan an independent new domain/model; no nearest-solver substitution |
| Correct classification, no measured object | Current subtype CV/grounder diagnostics | Improve grounding or request review; do not turn a VLM bbox into precise geometry |
| OCR sees a number but parameter absent | OCR candidates and ownership association | Establish quantity/unit/target; high OCR confidence alone is insufficient |
| Circuit values correct but graph wrong | Symbol terminals, paths, junctions, graph construction | Repair perception/topology before touching MNA |
| Circuit graph correct but computed current wrong | Browser graph compilation/solver and units | Reproduce with a minimal explicit graph and compare analytical results |
| Backend says ready, browser says blocked | Full response and SimulationApi mapping | Check dropped BookIR, status normalization, stale operations, and response shape |
| Browser says ready, compiler refuses | Backend readiness/compiler issues | Backend wins; fix the misleading presentation or missing requirement |
| Overlay moves away on resize | FigureViewport and CoordinateMapper integration | Fix one shared registration transform; preserve native geometry |
| Overlay registered but anchored to wrong feature | CV/grounder measurement | Fix extracted geometry; CSS offsets cannot repair a wrong landmark |
| Slider changes original evidence | Runtime cloning and parameter-update path | Restore evidence/exploration separation |
| Reset restores unexpected value | Compiled baseline and assumption provenance | Determine whether it was assumed, reviewed, or observed before calling it a solver error |
| Server stalls during heavy work | Async route and offloading boundary | Offload blocking work; do not add a frontend fallback simulation |
| Only a preset works | Preset-versus-upload call path | Test the actual uploaded-file pipeline independently |

### 20.1 Minimum evidence to request when the folder is unavailable

A remote GPT should request only the artifacts needed for the decision:

- For an interpretation issue: the original image, native dimensions, semantic classification/confidence, and provider error metadata if any.
- For a grounding issue: BookIR geometry/entities, OCR tokens/candidates, grounding diagnostics, and an evidence overlay where available.
- For readiness: parameters with provenance, assumptions, resolutions, review state, readiness report, and compiler issues.
- For circuit correctness: measured component/terminal records, wire polylines, node graph, switch/polarity evidence, and actual solver outputs.
- For UI/state: the state transition sequence, relevant API request/response, and browser error.
- For registration: source dimensions, displayed image/overlay rectangles, mapper scale/offsets, device-pixel ratio, and the mismatched landmark.

Never request API keys or copy secrets into diagnostic reports.

### 20.2 Decision discipline

Keep these questions separate:

1. Does the image depict a supported model?
2. Is the relevant geometry grounded in this source?
3. Are values correctly identified and associated?
4. Which inputs are observed, derived, supplied, or assumed?
5. Does the backend authorize compilation?
6. Does the emitted scene pass runtime checks?
7. Does the numerical result agree with the intended model?
8. Does the display register with the image?
9. Does the student interaction preserve original evidence?

An affirmative answer at one boundary does not imply affirmative answers at the others. This is the basis for making precise decisions without guessing.

## 21. Rules for extending or changing this system

The repository's operational instructions are mandatory context for future work:

- Read `PROJECT_CONTEXT.md` and `docs/ARCHITECTURE.md` before architectural or cross-module changes, while accounting for their historical content.
- Preserve working physics algorithms and numerical integrators during UI work/refactors.
- Keep the system book-neutral; do not encode NCTB-specific values into generic solvers.
- Inspect Git status/diff before and after modifications. Preserve unrelated uncommitted work.
- Inspect history/blame before resolving discrepancies or touching high-collision files. Do not overwrite complete files to suppress conflicts.
- Keep scope bounded and commits atomic. No commit was requested or created for this report.
- Changes to `engine/core/`, `shared/schemas/`, and `apps/api/main.py` require explicit justification and coordination with owners.
- High-collision files include `apps/web/src/main.js`, `apps/web/index.html`, `apps/web/src/style.css`, `engine/core/sceneRouter.js`, and `apps/api/main.py`; follow the single-writer policy.
- Preserve comments, docstrings, evidence references, identity, and all parameter provenance.
- Modify generators rather than generated outputs. Never commit runtime uploads, generated scenes/debug images, weights, caches, or secrets.
- Keep VLMs semantic-only. Never accept their numerical guesses or coarse coordinates as grounded physics.
- Keep non-physics/unsupported flags out of subtype vocabulary. Enforce booleans, finite confidence, valid domain/subtype pairs, and relationship references.
- Automated unit/integration/CI tests must use deterministic mock semantic providers and no external API calls. Keep live-provider acceptance separate and gated.
- Offload heavy blocking work invoked from async handlers with `asyncio.to_thread`.

`.github/CODEOWNERS` assigns critical shared core/schemas/API review to both `@rahi-sadat` and `@THE-FOOL-T`. Mechanics is primarily assigned to `@rahi-sadat`, optics to `@THE-FOOL-T`, and circuits/shared integration to both. Confirm current ownership if the repository changes.

A new model needs a complete vertical integration: semantic vocabulary, contract and requirements, grounded perception/fusion, policy restrictions, compiler support, domain adapter/solver, capabilities, renderer/interaction, and offline negative/positive tests. Adding a dropdown label or exposing an old prototype does not complete support.

Repository rules mention registering new domains through `sceneRouter.js`; current execution is registry-based, and that file's old factory is retired. Respect the intended independent domain boundary and coordinate a change through the active registry path rather than blindly reviving the retired router.

## 22. Separate capabilities that must not be confused with the main flow

This section exists only to prevent accidental mixing. The current real-file execution described in Sections 3–15 remains the reference path.

| Separate path/module | What it represents | What must not be inferred |
|---|---|---|
| Preset scenes in `apps/web/public/scenes` selected by preset pills/domain buttons | Authored/precompiled demonstrations; some use `bootstrap()` and legacy web controllers | Preset success does not prove upload perception succeeded |
| `POST /api/upload-diagram` + `POST /api/analyze-diagram` | Older URL-oriented upload/analyzer surface still present in the API | These are not the current File -> `/api/ingest` orchestration entrypoint |
| `ai/perception/` and older scene builders | Existing perception/authoring modules used by other tools/routes | Their historical behavior is not automatically the current `ai/evidence` pipeline |
| Python `/api/circuit/analyze`, `/solve`, `/validate`, `/spice` | Separate circuit services and computational helpers | Browser `CircuitAdapter` does not automatically invoke these endpoints |
| `CircuitTutorBridge.js` and associated laboratory UI | Template-based bilingual circuit explanations around solver state | This is not evidence of a deployed general LLM tutor in the uploaded-file flow |
| Matter.js incline, spring, cradle/rigid-body demonstrations | Additional existing demo/runtime code | Canonical upload mechanics currently accepts pendulum/projectile; it explicitly rejects unsupported mechanics subtypes |
| `legacy/frontend-v1/` | Archived initial frontend | It is not the active web application |
| Historical `backend/server.py` and `simulation_frontend/...` paths in prose | Pre-migration locations | Do not use these as current startup instructions |

The broader roadmap includes full-page/PDF layout, multi-figure/caption binding, textbook navigation, a grounded Bangla conversational/voice tutor, assessments, personalized study planning, progress, notes, and teacher tools. These require new evidence of implementation before being described as shipped.

## 23. Priority conclusions for a future decision-maker

The current system has a coherent vertical architecture: real image bytes, semantic interpretation, local evidence grounding, auditable resolution, gated compilation, validated domain runtime, and source-aligned interaction. Its governing principle is traceability from source or disclosed assumption to executable quantity.

The main constraints on further decisions are grounding reliability, honest assumption handling, consistent backend/frontend state propagation, and real-image acceptance. The eight uncommitted circuit/OCR files make circuit conclusions especially snapshot-dependent.

A justified next engineering action should target a demonstrated failed boundary. Examples include restoring updated BookIR propagation in the review client, aligning ready-banner logic with backend blockers, validating circuit assignment ambiguity/threshold changes, and fully enforcing the stated confidence caps. These are source-inspection findings, not changes performed by this report.

Do not claim production readiness, arbitrary-diagram accuracy, universal automatic simulation, or a complete tutor based on the present test/build evidence. Do not remove readiness gates to improve the apparent ready rate.

## 24. Copyable briefing for another GPT

> You are assisting with AugmentedPhysics, a book-agnostic platform that converts one cropped physics-diagram image into a source-aligned interactive simulation. The snapshot is 28 October 2026, branch main, HEAD e484676, with eight pre-existing uncommitted circuit/OCR/test files listed in Section 17. Treat newer supplied evidence as authoritative over this snapshot.
>
> The CURRENT real-file path is main.js -> SimulationOrchestrator.startWithFile -> SimulationApi -> POST /api/ingest -> UploadService -> SourceAsset -> PageIRBuilder -> BookUnderstandingPipeline/Gemini semantic classification -> ai/evidence OCR/CV/SAM2 and subtype fusion -> source-dimension enforcement -> AutoResolutionEngine and ResolutionEngine -> ReadinessEvaluator -> PhysicsCompiler -> canonical schemaVersion 1.0 PhysicsScene -> InteractiveFigure/FigureViewport -> PhysicsRuntime/SolverRegistry/domain adapter -> solver/rendering. Do not substitute preset/legacy behavior for this path.
>
> Supported canonical subtypes are pendulum, projectile, thin_lens, spherical_mirror, interface_refraction, prism, and dc_linear. Classification is supported/unsupported_physics/non_physics/unknown; unsupported and non-physics results must not become physical subtype strings. The VLM only supplies semantic roles and unverified labels/coarse bboxes, never authoritative numerical parameters or geometry. Native source_px coordinates remain unchanged under browser resizing.
>
> BookIR is evidence/resolution data, not an executable scene. Only backend readiness and compilation authorize a scene. Current auto-policy logic can supply disclosed model assumptions, including mechanics defaults and some optical exploration setup. Inspect provenance, user acceptance, and assumptions; never call an assumed value measured. The compiler implementation is ai/ingestion/PhysicsCompiler.py; ai/scene_compiler/physics_compiler.py is a re-export.
>
> Circuit grounding uses measured symbols/terminals and continuous conductor paths; topology is distinct from page layout. The uploaded circuit runs the JS CircuitAdapter/CircuitCompiler/CircuitSolver locally. A SAM mask or a successful MNA calculation does not prove the extracted graph is correct. Do not invent electrical values or connections.
>
> Current UI wiring can start a ready upload after Generate Simulation, and the review modal is opened explicitly. SimulationApi.review currently drops the updated BookIR returned by the backend, and filtered review issues can create a misleading ready banner. Backend compile remains the gate. Distinguish these actual behaviors from older architectural prose.
>
> Preserve working physics and evidence provenance. Isolate changes by subsystem. Coordinate shared-core/schema/API/high-collision edits. Use deterministic offline tests, with live Gemini acceptance separate. Do not overwrite the pre-existing working changes or commit runtime data. If you lack the image, full IR/response, current code, or logs needed for a decision, identify that missing evidence and request it; do not invent an exact diagnosis.
