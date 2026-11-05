# PR-08 Engineering & Acceptance Report
## Interactive Evidence Review, Automatic Simulation Orchestration & Student-Facing Diagram-to-Simulation Flow

**Date**: 2026-10-07  
**Author**: Antigravity  
**Milestone**: PR-08  
**Status**: Completed  
**Branch**: `PR-08`  

---

## 1. Pre-Implementation Audit Summary

Prior to adding code for PR-08, an exhaustive audit was conducted across the codebase following the completion of PR-07. The key findings were:

1. **Where `/api/ingest` was called**: Previously in `apps/web/src/main.js`, uploaded images were sent to `/api/ingest` and the resulting `BookIR` was displayed inside a raw JSON debug drawer (`#ingest-json`), with an empty simulation placeholder.
2. **How BookIR reached the frontend**: The `multipart/form-data` response returned `{ book_ir: {...}, status: "NEEDS_REVIEW" | "READY_TO_COMPILE", metadata: {...} }`. The raw JSON was stored on `window.__lastBookIR`.
3. **How `NEEDS_REVIEW` was represented**: In backend Python dataclasses (`BookIRStatus.NEEDS_REVIEW`), accompanied by `readiness_report.blockers` and `review_state.issues`. In the frontend, it was only displayed as a text badge string `"Status: NEEDS_REVIEW"`.
4. **Exact PR-07 endpoint contracts**:
   - `POST /api/resolution/review`: Request `{ book_ir: {...} }`, Response `{ review_state: {...}, readiness_report: {...} }`
   - `POST /api/resolution/resolve`: Request `{ book_ir: {...}, decision: { parameter_name, action, ... } }`, Response `{ book_ir: {...}, review_state: {...}, readiness_report: {...} }`
   - `POST /api/resolution/evaluate`: Request `{ book_ir: {...} }`, Response `{ readiness_report: {...} }`
   - `POST /api/resolution/compile`: Request `{ book_ir: {...} }`, Response `{ physics_scene: {...}, book_ir: {...} }` (or HTTP 422 if not ready).
5. **Where compiled `PhysicsScene` enters the frontend**: In `apps/web/src/features/simulations/core/SimulationRuntime.js` via `runtime.initialize(scene)`.
6. **Which component renders embedded simulations**: `apps/web/src/components/InteractiveFigure.js`, which binds `FigureViewport.js`, `InteractiveStage.js`, and `ParameterPanel.js`.
7. **Coordinate mapping**: `engine/core/coordinateMapper.js` exports `sourceToView(x, y)` and `viewToSource(x, y)`. Native geometry in `PhysicsScene` and `BookIR` is strictly in `source_px`, while the canvas overlays use the mapper for display scaling.
8. **Modal/dialog infrastructure**: There was no existing generic modal system; UI relied on inline drawers (`#ingest-drawer`). PR-08 implemented an accessible, non-intrusive dialog (`PhysicsReviewModal.js`).
9. **Reusable components**: `SimulationRuntime.js`, `InteractiveFigure.js`, `CoordinateMapper.js`, `ParameterPanel.js`, and `PhysicsBodyFactory.js`.
10. **Files requiring modification**:
   - `apps/web/src/features/simulations/core/SimulationApi.js` (New)
   - `apps/web/src/features/simulations/core/SimulationOrchestrator.js` (New)
   - `apps/web/src/components/PhysicsReviewModal.js` (New)
   - `apps/web/src/components/physicsReviewModal.css` (New)
   - `apps/web/src/components/InteractiveFigure.js` (Modified)
   - `apps/web/src/main.js` (Modified)
   - `apps/web/src/style.css` (Modified)
   - `apps/web/package.json` (Modified)
   - `docs/ARCHITECTURE.md` (Modified)
   - `AGENTS.md` (Modified)

---

## 2. Final Architecture

```
                                 Browser Client
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   Student File Drop / Select                                                     │
│               │                                                                  │
│               ▼                                                                  │
│   SimulationOrchestrator.startWithFile(file)                                     │
│               │                                                                  │
│               ▼                                                                  │
│   SimulationApi.ingest(file) ──────────────┐                                    │
│                                            │ POST /api/ingest                    │
│                                            ▼                                     │
│                              FastAPI Backend (/api/ingest)                       │
│                                  PageIR → VLM → Grounding                        │
│                                            │                                     │
│               ┌────────────────────────────┘                                     │
│               ▼                                                                  │
│   BookIR (status: NEEDS_REVIEW)                                                  │
│               │                                                                  │
│               ▼                                                                  │
│   PhysicsReviewModal Opens                                                       │
│   - Detects missing gravity, mass, damping, or unconfirmed length                │
│   - Displays detected candidate "80 cm (88% confidence)"                        │
│   - Displays explicit modeling policies (Earth Gravity, Zero Damping)            │
│               │                                                                  │
│               ▼ Student clicks [Confirm] or [Apply Assumption]                   │
│   SimulationOrchestrator.confirmCandidate() / applyPolicy()                     │
│               │                                                                  │
│               ▼ POST /api/resolution/resolve                                     │
│   Backend applies resolution → evaluates readiness                               │
│               │                                                                  │
│               ▼ Returns updated BookIR + ReadinessReport                         │
│   If READY_TO_COMPILE:                                                           │
│   SimulationOrchestrator automatically calls SimulationApi.compile()             │
│               │                                                                  │
│               ▼ POST /api/resolution/compile                                     │
│   Canonical PhysicsScene returned (coordinateSpace = "source_px")                │
│   Orchestrator state becomes READY_TO_SIMULATE                                   │
│               │                                                                  │
│               ▼ PhysicsReviewModal shows "Simulation Ready"                      │
│   Student clicks [Start Simulation]                                              │
│               │                                                                  │
│               ▼ Orchestrator state becomes SIMULATING                            │
│   InteractiveFigure.loadScene(compiledPhysicsScene)                              │
│   - Canvas overlay activates over original diagram                               │
│   - CoordinateMapper maps source_px → CSS display pixels                         │
│   - ParameterPanel allows slider exploration                                     │
│   - "Reset to textbook values" restores baseline without mutating BookIR         │
│   - "Review Setup" button allows reopening review modal                          │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Explicit State Machine

The orchestration lifecycle is managed by `SimulationOrchestrator.js` using 12 deterministic states:

```
                  ┌─────────┐
                  │  IDLE   │
                  └────┬────┘
                       │ startWithFile()
                       ▼
                 ┌───────────┐
                 │ UPLOADING │
                 └─────┬─────┘
                       │ HTTP upload underway
                       ▼
                 ┌───────────┐
                 │ ANALYZING │
                 └─────┬─────┘
                       │ Ingestion returned
            ┌──────────┴──────────────┬──────────────────┐
            │ isPhysics === false     │ Needs review     │ Already ready
            ▼                         ▼                  ▼
     ┌─────────────┐           ┌──────────────┐   ┌──────────────────┐
     │ UNSUPPORTED │           │ NEEDS_REVIEW │   │ READY_TO_COMPILE │
     └─────────────┘           └──────┬───────┘   └────────┬─────────┘
                                      │                    │
              ┌───────────────────────┴────────┐           │
              │ applyPolicy() / confirm()      │           │
              ▼                                │           │
    ┌─────────────────────┐                    │           │
    │ APPLYING_RESOLUTION │                    │           │
    └─────────┬───────────┘                    │           │
              │                                │           │
              ▼                                │           │
        ┌────────────┐                         │           │
        │ EVALUATING │                         │           │
        └─────┬──────┘                         │           │
              │                                │           │
       Ready? ├────── No ──────────────────────┘           │
              │                                            │
              ▼ Yes                                        │
    ┌──────────────────┐ ◄─────────────────────────────────┘
    │ READY_TO_COMPILE │
    └─────────┬────────┘
              │ compile()
              ▼
        ┌───────────┐
        │ COMPILING │
        └─────┬─────┘
              │ Canonical PhysicsScene compiled
              ▼
    ┌───────────────────┐
    │ READY_TO_SIMULATE │
    └─────────┬─────────┘
              │ User clicks "Start Simulation"
              ▼
       ┌────────────┐
       │ SIMULATING │
       └────────────┘
```

### Stale Async Request & Race Condition Protection
Every asynchronous lifecycle operation increments a monotonic integer token (`_operationId`). When an asynchronous fetch completes, the orchestrator verifies that `token === this._operationId`. If the user cancelled, uploaded a new image, or reset to idle, stale server responses are discarded, preventing race conditions.

---

## 4. Endpoint Schema Alignment

`apps/web/src/features/simulations/core/SimulationApi.js` interfaces directly with FastAPI endpoints:

| Endpoint | Method | Input Payload | Output Payload | Error Handling |
| :--- | :--- | :--- | :--- | :--- |
| `/api/ingest` | `POST` | `multipart/form-data` (`file`) | `{ book_ir, status, metadata }` | Network errors mapped to `Backend offline` |
| `/api/resolution/review` | `POST` | `{ book_ir }` | `{ review_state, readiness_report }` | Returns human-readable issues & blockers |
| `/api/resolution/resolve` | `POST` | `{ book_ir, decision }` | `{ book_ir, review_state, readiness_report }` | Validates units and ranges; preserves superseding history |
| `/api/resolution/evaluate` | `POST` | `{ book_ir }` | `{ readiness_report }` | Invariant check for `READY_TO_COMPILE` |
| `/api/resolution/compile` | `POST` | `{ book_ir }` | `{ physics_scene, book_ir }` | Rejects with 422 `CompilationGatingError` if unready |

---

## 5. Student-Facing Review UX & Components

The review interface is implemented in `apps/web/src/components/PhysicsReviewModal.js` and styled with `physicsReviewModal.css`.

### Domain-Agnostic Parameter Presentation
Parameter keys are mapped to clear student-facing titles without hardcoding physics domains:
- `length` → **String Length**
- `gravity` → **Gravitational Acceleration**
- `launch_speed` → **Launch Speed ($v_0$)**
- `launch_angle_deg` → **Launch Angle ($\theta$)**
- `focal_length_px` → **Focal Length**
- `n1` → **Refractive Index ($n_1$)**
- `n2` → **Refractive Index ($n_2$)**
- `pixels_per_meter` → **Diagram Spatial Scale**

### Review Issue Cards
1. **Candidate Confirmation**: Displays detected value with confidence (e.g. `80 cm (Confidence: 88%)`). Clicking `[Confirm]` applies the candidate; clicking `[Correct]` reveals the inline manual editor.
2. **Explicit Modeling Policy Assumptions**: Policies are presented with their educational rationale and values (e.g., *Standard Earth Gravity (9.80665 m/s²)* — *Standard terrestrial gravitational acceleration*). Unrelated policies (such as optics refractive index for a pendulum) are excluded by the backend and never shown.
3. **Manual Entry Form**: Enables entering numeric values and selecting controlled units (`m`, `cm`, `deg`, `rad`, `m/s`, etc.).
4. **Resolved Items & Reversibility**: Resolved parameters are displayed in a collapsible summary with badges (`Confirmed`, `Corrected`, `Policy Assumption`). Each resolved parameter includes an `[Undo / Change]` button that calls `removeResolution()`, invalidating the compiled scene and reverting the state back to `NEEDS_REVIEW`.
5. **Ready to Simulate Banner**: When all blockers are satisfied, a green hero banner displays `"Simulation Ready: All requirements satisfied. Ready to launch."`, and the primary footer button changes to `"▶ Start Simulation"`.

---

## 6. Native Coordinate Preservation

Native diagram geometry strictly remains in `source_px` throughout the entire lifecycle:
- In `BookIR`: `entities[...].attributes["pivot_px"] = [250, 80]`, `string_length_px = 400.0`
- In compiled `PhysicsScene`: `coordinateSpace = "source_px"`, `bodies[0].position = [250, 80]`
- In `InteractiveFigure.js`: Viewport rendering uses `CoordinateMapper.sourceToView(x, y)` to compute canvas pixel coordinates.
- Neither `SimulationOrchestrator` nor `InteractiveFigure` modifies `source_px` coordinates or stores viewport CSS coordinates into `BookIR`.

---

## 7. Evidence Preservation vs. Simulation Experimentation

A strict distinction is maintained between **textbook source evidence** and **interactive simulation experimentation**:
- Upon compilation, `InteractiveFigure` caches `_sourceScene = JSON.parse(JSON.stringify(scene))`.
- When a student adjusts parameter sliders in `ParameterPanel` during simulation (e.g., changing length from $0.8\text{ m}$ to $1.5\text{ m}$), the change is applied solely to the live `PhysicsRuntime` instance.
- The underlying `BookIR` remains unmodified with its original source value ($0.8\text{ m}$).
- Clicking **"↺ Reset to textbook values"** resets the active simulation back to `_sourceScene.parameters`, cleanly restoring textbook values without re-ingesting or mutating the evidence base.
- If the student intends to permanently change the diagram evidence, they click **"✎ Review Setup"**, which reopens `PhysicsReviewModal` and routes through `/api/resolution/resolve`.

---

## 8. Test Verification Summary

All unit, integration, and acceptance tests pass with zero failures:

### Frontend Unit & Acceptance Suites (`npm test`)
```text
==============================================
  RUNNING PR-08 SIMULATION ORCHESTRATOR TESTS
==============================================
  ✓ 27 passed, 0 failed

==============================================
  RUNNING PR-08 REVIEW UI & INTERACTION TESTS
==============================================
  ✓ 33 passed, 0 failed

==============================================
  RUNNING PR-08 NO-FABRICATION FRONTEND TESTS
==============================================
  ✓ 14 passed, 0 failed

==============================================
  RUNNING PR-08 GOLDEN PATH ACCEPTANCE TESTS
==============================================
  ✓ 34 passed, 0 failed

Total PR-08 assertions: 108 passed, 0 failed
Total web suite assertions: 349 passed, 0 failed
```

### Backend Integration & Acceptance Suites (`pytest`)
```text
tests/integration/test_pr07_api.py .....                                 [ 83%]
tests/acceptance/test_pr07_real_pendulum_e2e.py .                        [100%]
======================= 6 passed, 36 warnings in 32.50s =======================
```

---

## 9. Real Pendulum End-to-End Walkthrough

Using the golden-path acceptance test fixture (`tests/fixtures/diagrams/bangla_pendulum_real.png`):

1. **Upload & Ingestion**:
   - Diagram uploaded via `SimulationOrchestrator.startWithFile()`.
   - VLM identifies `classification: "physics_diagram"`, `domain: "mechanics"`, `subtype: "pendulum"`.
   - SAM 2 and EasyOCR detect string length candidate `80 cm` (`0.8 m`), pivot `[250, 80]`, bob `[250, 480]`.
   - Initial status: `NEEDS_REVIEW`. Blockers: `length`, `gravity`, `mass`, `damping`.
2. **Review Dialog Opens**:
   - `PhysicsReviewModal` opens automatically.
   - Shows detected candidate: `80 cm (Confidence: 88%)`.
3. **Student Confirms Candidate**:
   - Student clicks `[Confirm 80 cm]`.
   - Request sent to `/api/resolution/resolve`.
   - Length blocker is satisfied; `pixels_per_meter` is derived as $500.0\text{ px/m}$.
4. **Student Applies Explicit Policies**:
   - Student clicks `[Use Assumption: Standard Earth Gravity (9.80665 m/s²)]`.
   - Student clicks `[Use Assumption: Standard Reference Mass (1.0 kg)]`.
   - Student clicks `[Use Assumption: Ideal Zero Damping (0.0 1/s)]`.
5. **Automatic Compilation Gating**:
   - All 4 blockers resolved.
   - Backend `ReadinessEvaluator` returns `is_ready: true`, transitioning `BookIR.status` to `READY_TO_COMPILE`.
   - Orchestrator automatically invokes `/api/resolution/compile`.
   - Backend returns canonical `PhysicsScene` with `coordinateSpace: "source_px"`.
   - Orchestrator state enters `READY_TO_SIMULATE`.
6. **User Starts Simulation**:
   - Student clicks `[▶ Start Simulation]`.
   - Modal closes, orchestrator enters `SIMULATING`.
   - Canvas overlay attaches over the diagram at exact source coordinates `pivot: (250, 80)` and `bob: (250, 480)`.
   - High-precision RK4 mechanics solver runs in real time.
7. **Simulation Experimentation**:
   - Student adjusts length slider to $1.5\text{ m}$. Simulation oscillation slows accordingly.
   - Student clicks "Reset to textbook values" → length returns to $0.8\text{ m}$.
   - Source BookIR remains strictly preserved at $0.8\text{ m}$.

---

## 10. Limitations

1. **Single Figure Session**: Current UI operates on one active uploaded figure at a time; does not yet segment multi-diagram textbook pages.
2. **Direct Browser Image Capture**: Ingest operates on image files (PNG/JPEG/WEBP); full PDF parsing is deferred to PR-09.
3. **Desktop & Tablet Optimized**: While `physicsReviewModal.css` is responsive, complex diagrams are best viewed at screen widths $\ge 768\text{ px}$.

---

## 11. PR-09 Recommendations

1. **Page Layout Analysis**: Ingest full multi-page PDF documents, detect multiple diagram regions on a single page, and isolate bounding boxes.
2. **Multi-Figure Session Management**: Instantiate independent `SimulationOrchestrator` instances for each detected figure on a page.
3. **Figure Caption Association**: Bind nearby Bengali/English textbook paragraphs to each figure session for enhanced OCR context.
