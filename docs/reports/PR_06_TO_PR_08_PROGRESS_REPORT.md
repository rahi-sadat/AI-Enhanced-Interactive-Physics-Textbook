# AugmentedPhysics v2 — Research & Engineering Progress Report
## Comprehensive Milestone Report: PR-06 to PR-08
**Grounding Perception, Evidence Resolution, and Student-Facing Interactive Simulation Orchestration**

---

**Project Title:** AugmentedPhysics v2 (AI-Enhanced Interactive Physics Textbook Platform)  
**Date:** October 2026  
**Author / Lead Engineer:** Research & Engineering Team  
**Supervising Faculty / Target Audience:** Academic Supervisor & Department Stakeholders  
**Repository:** `AI-Enhanced-Interactive-Physics-Textbook`  
**Current Milestone State:** PR-06 (✅ Completed) | PR-07 (✅ Completed) | PR-08 (✅ Completed)  
**Test Suite Status:** 175/175 Backend Tests Passing (100%) | 108/108 Frontend Tests Passing (100%)  

---

## Executive Summary

AugmentedPhysics transforms static textbook figures from secondary physics curricula into interactive, real-time simulation laboratories. Traditional educational tools either rely on pre-baked animations or invoke large language/multimodal models (VLMs) that hallucinate numerical parameters, miscalculate geometric coordinates, and fabricate physical laws.

Across **Milestones PR-06 through PR-08**, we designed, implemented, and validated the core engine that bridges raw diagram perception with rigorous computational physics:

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│          PR-06          │     │          PR-07          │     │          PR-08          │
│   Classical CV + OCR    │ ──► │   Evidence Resolution   │ ──► │  Interactive Frontend   │
│   Parameter Grounding   │     │    & Anti-Fabrication   │     │      Orchestration      │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
  • Sub-pixel geometry            • Declarative specs             • Deterministic lifecycle
  • English & Bangla OCR          • Separation of evidence        • Student review modal
  • Spatial bipartite fusion      • Auditable policy registry     • Decoupled simulation
  • Native source_px space        • Authoritative compilation     • Exploration separation
```

1. **PR-06 (Classical CV + OCR Parameter Grounding):** Eliminated VLM geometric hallucinations by pairing Gemini semantic categorization with classical computer vision (OpenCV, adaptive thresholding, Hough transforms, contour hierarchy) and multilingual OCR (Tesseract & EasyOCR for English and Bangla). Extracts sub-pixel coordinates in native `source_px` space and binds numerical text labels to detected visual entities.
2. **PR-07 (Evidence Resolution & Anti-Fabrication Engine):** Solved the textbook incompleteness dilemma without parameter fabrication. Textbook diagrams often omit physical quantities (e.g. gravity $g$, bob mass $m$, air damping $b$). PR-07 introduced declarative `ModelRequirementSpec` contracts, an auditable `DefaultPolicyRegistry` with educational rationales, and an authoritative `ReadinessEvaluator` that strictly forbids simulation generation until all physical requirements have legitimate provenance.
3. **PR-08 (Interactive Evidence Review & Simulation Orchestration):** Built the student-facing lifecycle layer. Features a deterministic 8-state client-side state machine (`SimulationOrchestrator`), an accessible glassmorphic review dialog (`PhysicsReviewModal`), and seamless rendering in `InteractiveFigure`. The frontend strictly defers compilation authority to the backend, decouples compilation from simulation activation, and guarantees that interactive parameter exploration never mutates the underlying textbook evidence.

---

## 1. Project Milestone Roadmap Context

To contextualize PR-06 through PR-08 within the broader project timeline:

| Milestone | Scope & Domain | Status | Key Deliverable |
| :--- | :--- | :--- | :--- |
| **PR-01** | Strict Audit & Anti-Fabrication Invariants | ✅ Completed | Fail-closed security; no auto-path generates runnable physics from missing evidence. |
| **PR-02** | Canonical PhysicsScene v1.0 & PhysicsRuntime | ✅ Completed | Book-neutral JSON schema; SolverRegistry; multi-domain physics validation. |
| **PR-03** | Source-Aligned Rendering & Coordinate Mapping | ✅ Completed | CoordinateMapper; SimulationCapabilityRegistry; bidirectional direct manipulation. |
| **PR-04** | Document Ingestion Pipeline | ✅ Completed | `SourceAsset` $\to$ `PageIR` $\to$ `BookIR`; Gate Zero anti-fabrication UI. |
| **PR-05** | Multimodal VLM Semantic Understanding | ✅ Completed | Gemini 2.5/3 integration; conservative confidence policy; domain & subtype categorization. |
| **PR-06** | **Classical CV + Multilingual OCR Grounding** | ✅ **Completed** | **Sub-pixel geometry; spatial-semantic bipartite matching; multi-domain grounders.** |
| **PR-07** | **Evidence Resolution & Compilation Readiness** | ✅ **Completed** | **Declarative requirement specs; explicit policy registry; authoritative compiler gating.** |
| **PR-08** | **Interactive Review & Orchestration UX** | ✅ **Completed** | **SimulationOrchestrator state machine; PhysicsReviewModal; decoupled execution.** |
| **PR-09** | Multimodal Audio/Visual Pedagogical Tutor | 🔜 Up Next | Voice-interactive physics dialog; Socratic guidance; real-time diagram highlighting. |
| **PR-10** | Empirical Research Evaluation & Benchmarking | 🔜 Planned | End-to-end accuracy, latency, and educational efficacy benchmark across 100+ diagrams. |

---

## 2. Milestone Deep-Dives

```mermaid
flowchart TD
    subgraph S1["PR-06: Perception & Grounding"]
        RawImage["Textbook Diagram (PNG/JPG)"] --> VLM["VLM Semantic Classifier (Gemini)"]
        RawImage --> CV["Classical CV (OpenCV / SAM 2)"]
        RawImage --> OCR["Multilingual OCR (Tesseract / EasyOCR)"]
        VLM --> Fusion["Spatial-Semantic Bipartite Fusion"]
        CV --> Fusion
        OCR --> Fusion
        Fusion --> GroundedIR["BookIR (status: NEEDS_REVIEW, native source_px)"]
    end

    subgraph S2["PR-07: Evidence Resolution"]
        GroundedIR --> ReqAnalyzer["ResolutionAnalyzer (ModelRequirementSpec)"]
        ReqAnalyzer --> ReviewIssues["Unresolved Physical Blockers Identified"]
        ReviewIssues --> PolicyEngine["Auditable PolicyRegistry / Student Input"]
        PolicyEngine --> ReadinessEval["ReadinessEvaluator (Strict Invariant Check)"]
        ReadinessEval --> ReadyIR["BookIR (status: READY_TO_COMPILE)"]
        ReadyIR --> Compiler["PhysicsCompiler (Pure Function)"]
        Compiler --> CompiledScene["Canonical PhysicsScene v1.0"]
    end

    subgraph S3["PR-08: Orchestration & Interactive UI"]
        CompiledScene --> Orchestrator["SimulationOrchestrator (State: READY_TO_SIMULATE)"]
        Orchestrator --> Modal["PhysicsReviewModal (Audit & Review UI)"]
        Modal -- "Student clicks [▶ Start Simulation]" --> SimState["State: SIMULATING"]
        SimState --> ActiveFig["InteractiveFigure (HTML5 Canvas)"]
        ActiveFig --> CoordMap["CoordinateMapper (source_px ↔ view_px)"]
        ActiveFig --> Sliders["Runtime Exploration Sliders (BookIR Evidence Pristine)"]
    end
```

---

### Milestone PR-06: Classical CV, Multilingual OCR & Parameter Grounding

#### 1. Core Problem
While Vision-Language Models (such as Gemini 2.5 Flash) excel at semantic classification (e.g. recognizing that an image is an optics diagram depicting a convex lens), they cannot perform sub-pixel coordinate localization and frequently hallucinate numbers. A reliable educational simulator requires exact optical axes, precise lens centers, accurate pivot points, and extracted values for focal lengths and string lengths.

#### 2. Technical Architecture & Implementation
PR-06 introduced a multi-stage grounding pipeline located in [`ai/evidence/`](file:///d:/AugmentedPhysics/ai/evidence/):

- **Sub-Pixel Kinematics Perception ([`ai/evidence/cv/pendulum_cv.py`](file:///d:/AugmentedPhysics/ai/evidence/cv/pendulum_cv.py)):**
  - **Pivot Localization:** Uses adaptive thresholding and contour hierarchy filtering to detect the ceiling/support clamp. The pivot is identified by extracting the acute vertex where string edges converge.
  - **Bob Detection:** Employs Hough Circle Transform supplemented by connected-component circularity analysis ($\frac{4\pi A}{P^2} \ge 0.78$) to isolate the mass center with sub-pixel precision.
  - **String Geometry:** Validates that the Euclidean distance between pivot and bob corresponds directly to the visual string geometry in native `source_px`.

- **Sub-Pixel Optics Perception ([`ai/evidence/cv/thin_lens_cv.py`](file:///d:/AugmentedPhysics/ai/evidence/cv/thin_lens_cv.py)):**
  - **Collinear Optical Axis Clustering:** Overcomes the common computer vision pitfall where OCR text labels fragment horizontal lines. Clusters collinear line segments across the lens to detect the continuous principal axis with 100% precision.
  - **Optical Center ($O$):** Locates the vertical lens centerline and calculates the exact intersection with the principal axis.
  - **Focal Markers ($F_1, F_2, 2F_1, 2F_2$):** Extracts letter labels and binds their baseline coordinates along the optical axis.
  - **Object Arrow Detection:** Uses morphological vertical kernel filtering and contour aspect ratios to isolate the object arrow ($AB$), distinguishing arrowheads from vertical support lines.

- **Multilingual OCR Engine ([`ai/evidence/ocr/`](file:///d:/AugmentedPhysics/ai/evidence/ocr/)):**
  - Dual-engine pipeline supporting **English** (Tesseract) and **Bengali** (EasyOCR/Bangla OCR).
  - Normalizes scientific notations (e.g., converting Bangla numerals `১, ২, ৩` to standard numeric floats).
  - Extracts unit candidates (`cm`, `m`, `s`, `V`, `Ω`, `px`).

- **Spatial-Semantic Bipartite Binding:**
  - Matches detected text values to geometric entities using proximity weighting and directional bounding boxes (e.g., binding `$f = 400\text{ px}$` to the focal segment rather than the object distance).

---

### Milestone PR-07: Evidence Resolution, User Review & Compilation Readiness

#### 1. Core Problem
A diagram from an NCTB textbook may show a pendulum with an annotated string length of $80\text{ cm}$, but the diagram does not declare the acceleration due to gravity $g$, the bob mass $m$, or whether air resistance is modeled. 
If an AI system silently fills in $g = 9.8\text{ m/s}^2$ without user knowledge, it violates scientific transparency. PR-07 established the mathematical and architectural protocol to transition an incomplete `BookIR` to `READY_TO_COMPILE` without parameter fabrication.

#### 2. Technical Architecture & Implementation
PR-07 introduced the resolution framework in [`ai/resolution/`](file:///d:/AugmentedPhysics/ai/resolution/):

1. **Declarative Requirement Contracts ([`requirements.py`](file:///d:/AugmentedPhysics/ai/resolution/requirements.py)):**
   Formalized `ModelRequirementSpec` definitions for all supported physical domains:
   - `mechanics/pendulum`: Requires `pivot`, `bob_position`, `string_length_px`, `bob_radius_px`, `gravity`, `mass`, `damping`, and spatial scale `pixels_per_meter`.
   - `optics/thin_lens`: Requires `lens_center`, `focal_length_px`, `aperture_height_px`, `object_position`.
   - `circuits/dc_linear`: Requires valid closed loop, nodal connectivity, source voltages, and component resistances.

2. **Strict Evidence vs. Resolution Separation:**
   - **Evidence Layer (Immutable):** PR-06 perceptions (`observed_visual`, `observed_ocr`) are stored in `book_ir.evidence` and are strictly write-protected.
   - **Resolution Layer (Declarative):** Student confirmations, manual inputs, and accepted modeling assumptions are recorded in `book_ir.resolutions` with explicit provenance.

3. **Auditable Policy Registry ([`policies.py`](file:///d:/AugmentedPhysics/ai/resolution/policies.py)):**
   - Maintained 8 standard educational modeling policies:
     - `policy_earth_gravity` ($9.80665\text{ m/s}^2$)
     - `policy_zero_damping` ($b = 0.0\text{ s}^{-1}$ — frictionless ideal pendulum)
     - `policy_standard_mass` ($m = 0.1\text{ kg}$)
     - `policy_air_refraction` ($n_{\text{air}} = 1.0$)
     - `policy_standard_lens_aperture` ($H = 300\text{ px}$)
   - Every policy includes an educational rationale shown to the student. No magic constants are permitted in code.

4. **Type-Safe Unit Normalization & Spatial Calibration ([`units.py`](file:///d:/AugmentedPhysics/ai/resolution/units.py)):**
   - Validates physical dimensionality (length, mass, time, voltage).
   - Calibrates `pixels_per_meter` by comparing diagram pixel lengths against OCR physical lengths without ever resizing or warping native image pixels.

5. **Authoritative Compilation Gating ([`ReadinessEvaluator.py`](file:///d:/AugmentedPhysics/ai/resolution/evaluator.py)):**
   - Evaluates whether all required parameters have verified provenance.
   - Reversibility invariant: If a student removes or alters a resolution, the system immediately reverts to `NEEDS_REVIEW` and invalidates any compiled physics scene.

---

### Milestone PR-08: Interactive Review & Deterministic Simulation Orchestration

#### 1. Core Problem
How to surface the complex perception (PR-06) and resolution (PR-07) capabilities to secondary students without overwhelming them, while maintaining strict architectural invariants:
- The browser must never declare compilation readiness independently of the backend.
- Students must have full agency to review, confirm, or correct diagram readings.
- Interactive slider experiments during simulation must never corrupt the original textbook baseline.

#### 2. Technical Architecture & Implementation
PR-08 built the complete client-side runtime in [`apps/web/src/`](file:///d:/AugmentedPhysics/apps/web/src/):

1. **Deterministic Lifecycle State Machine ([`SimulationOrchestrator.js`](file:///d:/AugmentedPhysics/apps/web/src/features/simulations/core/SimulationOrchestrator.js)):**
   Governs figure lifecycle across 8 distinct states:
   $$\text{IDLE} \to \text{UPLOADING} \to \text{ANALYZING} \to \text{NEEDS\_REVIEW} \to \text{READY\_TO\_COMPILE} \to \text{COMPILING} \to \text{READY\_TO\_SIMULATE} \to \text{SIMULATING}$$
   - Guarded by monotonic operation IDs (`_operationId`) to prevent asynchronous race conditions.
   - Strictly enforces backend compilation gating.

2. **Accessible Student-Facing Review Dialog ([`PhysicsReviewModal.js`](file:///d:/AugmentedPhysics/apps/web/src/components/PhysicsReviewModal.js)):**
   - Glassmorphic modal designed to WCAG accessibility standards.
   - Displays detected candidates with percentage confidence badges.
   - Provides one-click **[Confirm]**, **[Correct]**, or **[Use Modeling Assumption]** actions.
   - Real-time audit history displaying provenance badges (*Confirmed*, *Corrected*, *Assumption*, *Derived*).

3. **Decoupled Simulation Activation:**
   - Transitioning to `READY_TO_SIMULATE` does not auto-start simulation.
   - Requires explicit student initiation by clicking **"▶ Start Simulation"**, giving the student control over when animation begins.

4. **Evidence vs. Exploration Separation ([`InteractiveFigure.js`](file:///d:/AugmentedPhysics/apps/web/src/components/InteractiveFigure.js)):**
   - When running, parameter sliders mutate only the live simulation instance.
   - The compiled textbook scene remains immutable in memory.
   - A **"Reset to textbook values"** button instantly restores the grounded baseline.
   - A **"🔬 Review Setup"** button allows reopening the evidence dialog at any time.

5. **Native Coordinate Preservation ([`CoordinateMapper.js`](file:///d:/AugmentedPhysics/engine/core/coordinateMapper.js)):**
   - All physics calculations and annotations remain strictly in `source_px` coordinates.
   - Viewport resizing dynamically transforms coordinates to canvas display pixels using matrix scaling, preventing distortion.

---

## 3. Real-World Engineering Challenges & Resolutions

During live end-to-end integration across real textbook diagrams, three non-trivial engineering challenges were encountered and solved:

### Challenge 1: Optical Axis Line Fragmentation from Text Labels
- **Observation:** In ray diagrams, labels such as "$F_1$", "$F_2$", and "$O$" cross the principal axis. Standard Hough line transforms detected fragmented segments (e.g. short 50 px segments) rather than the continuous 1200 px axis.
- **Root Cause:** OCR text bounding box suppression masked parts of the line, breaking continuity.
- **Resolution:** Implemented collinear segment clustering in [`ai/evidence/cv/thin_lens_cv.py`](file:///d:/AugmentedPhysics/ai/evidence/cv/thin_lens_cv.py). Segments with horizontal collinearity within $\pm 4\text{ px}$ of $y$ were merged, allowing the true principal axis to span 1227 px across the lens center with 100% precision.

### Challenge 2: Dimension Propagation Across Multi-Domain Grounders
- **Observation:** Uploaded ray diagrams intermittently failed compilation with `MISSING_COORDINATE_DIMENSIONS`, causing the review modal to freeze when "Start Simulation" was clicked.
- **Root Cause:** Grounders populated physical coordinates in `book_ir.geometry` but omitted top-level image `width` and `height`. `PhysicsCompiler` refused to compile without image dimensions.
- **Resolution:** 
  1. Updated [`ai/evidence/pipeline.py`](file:///d:/AugmentedPhysics/ai/evidence/pipeline.py) and all grounders (`thin_lens`, `spherical_mirror`, `projectile`, `circuits`, `refraction`, `prism`) to guarantee dimensions.
  2. Implemented an automatic PIL fallback in [`PhysicsCompiler._extract_source_dimensions`](file:///d:/AugmentedPhysics/ai/ingestion/PhysicsCompiler.py#L210) to read dimensions directly from disk if missing.
  3. Added comprehensive `try...catch` blocks and user-facing error banners in [`PhysicsReviewModal.js`](file:///d:/AugmentedPhysics/apps/web/src/components/PhysicsReviewModal.js) to prevent unhandled exceptions.

### Challenge 3: Entity Ordering Invariants in Canonical Compilers
- **Observation:** Inserting an `optical_object` arrow at index 0 of `scene.objects` broke downstream regression assertions expecting `objects[0]` to be the `thin_lens`.
- **Root Cause:** Legacy contracts expected the optical element to precede objects.
- **Resolution:** Modified [`PhysicsCompiler.py`](file:///d:/AugmentedPhysics/ai/ingestion/PhysicsCompiler.py#L112) to append `optical_object` after the lens entity while updating `OpticsAdapter.js` to locate elements dynamically via `.find()`. Preserved 100% backward compatibility.

---

## 4. Test Suite Validation & Verification Metrics

The codebase maintains an exhaustive, two-tier test suite covering both Python backend logic and JavaScript frontend orchestration:

### 1. Python Unit & Integration Test Suite (`pytest`)
**Result: 175 Passed, 0 Failed (100% Pass Rate)**
- `test_pr04_ingestion.py`: Source asset hashing, PageIR extraction, Gate Zero checks.
- `test_pr05_vlm_analyzer.py` & `test_pr05_semantic_schemas.py`: Multi-model VLM integration and conservative confidence scoring.
- `test_pr06_cv.py` & `test_pr06_transforms.py`: Sub-pixel geometry extraction for pendulums, lenses, projectiles, and circuits.
- `test_pr06_multilingual_ocr.py`: English and Bangla character recognition benchmarks.
- `test_pr07_evaluator.py`, `test_pr07_policies.py`, `test_pr07_resolution.py`: Requirement specs, policy applications, reversibility, and compiler gating.
- `test_strict_analysis.py`: Anti-fabrication invariants across all domains.

### 2. Frontend Test Suite (`npm test` in `apps/web`)
**Result: 108 Passed, 0 Failed (100% Pass Rate)**
- `test_pr08_orchestrator.js` (27 tests): Monotonic state transitions, async race condition resilience, compilation gating.
- `test_pr08_review_ui.js` (33 tests): Modal rendering, candidate confirmation, policy selection, busy-state handling, keyboard accessibility.
- `test_pr08_no_fabrication.js` (14 tests): Verification that incomplete BookIR never generates a simulation; verification that offline networks cleanly halt without fallback scenes.
- `test_pr08_golden_path.js` (34 tests): End-to-end user journeys from image upload to interactive canvas simulation; native `source_px` coordinate preservation; exploration vs. evidence isolation.

### 3. Live Browser Verification
Verified through automated Chrome DevTools Protocol (CDP) on `localhost:5173`:
- Uploaded real textbook diagram (`diagram_feb71222.png` — NCTB Convex Lens Ray Diagram).
- Resolved missing parameters via `PhysicsReviewModal`.
- Clicked "Start Simulation": modal closed, scene compiled, ray tracer initialized.
- Live verified 3 analytical rays (parallel, focal, center) intersecting at $B'$ ($v = 1473.8\text{ px}$, magnification $-2.68$).
- Interactive sliders and live telemetry verified in real time.

---

## 5. Supervisor Live Demonstration Guide

To present this progress to your supervisor, follow this structured demonstration flow:

### Step 1: Architecture Walkthrough (5 minutes)
1. Open this report (`docs/reports/PR_06_TO_PR_08_PROGRESS_REPORT.md`).
2. Show the **Architecture Flow Diagram** explaining the three-tier progression:
   - **Perception (PR-06):** No fabricated numbers; sub-pixel classical CV + multilingual OCR.
   - **Resolution (PR-07):** Formal `ModelRequirementSpec` contracts; auditable modeling policies.
   - **Interaction (PR-08):** Deterministic client orchestration; student review modal.

### Step 2: Automated Test Suite Execution (3 minutes)
Demonstrate reliability by executing both test suites live:
```bash
# Terminal 1: Run Python Backend Tests (175 tests)
pytest tests/unit

# Terminal 2: Run Frontend Tests (108 tests)
cd apps/web && npm test
```
*Key Talking Point:* Point out the zero-fabrication assertions in `test_pr08_no_fabrication.js` and `test_strict_analysis.py`. Show that if a single parameter is missing, the system refuses to compile rather than guessing.

### Step 3: Live End-to-End Simulation Demonstration (7 minutes)
1. Open `http://localhost:5173/` in Google Chrome.
2. Click **"Upload Diagram"** in the top navigation bar.
3. Select an NCTB textbook diagram (e.g. `storage/uploads/diagram_feb71222.png` or `storage/uploads/pendulum.png`).
4. Watch the ingestion pipeline run through Gemini semantic classification and classical CV grounding.
5. Notice that the **Textbook Evidence Review Dialog** opens automatically because the diagram is in `NEEDS_REVIEW`.
6. Show the supervisor the detected candidate values with confidence percentages and the auditable modeling assumption cards (e.g., *Earth's Gravity $9.8\text{ m/s}^2$*).
7. Confirm the assumptions. Watch the dialog footer transition to **"✓ Simulation Ready"**.
8. Click **"▶ Start Simulation"**. The modal closes, and the interactive simulation activates directly over the textbook diagram.
9. Drag the object distance slider or focal length slider:
   - Point out how rays and images recalculate in real-time.
   - Click **"Reset to textbook values"** to demonstrate that the original textbook evidence was preserved intact.

---

## 6. Next Steps: Roadmap Ahead

With PR-06 through PR-08 completed, the platform has a verified diagram-to-simulation foundation. The immediate upcoming milestones are:

### Milestone PR-09: Live Multimodal Pedagogical Physics Tutor
- **Voice & Chat Interactive Dialog:** Incorporate real-time audio interaction (WebRTC / Gemini Live) allowing students to ask conceptual questions about the active diagram.
- **Socratic Guidance Engine:** Instead of simply giving answers, the tutor prompts students to explore parameters (e.g., *"What happens to the real image if you move the object closer than $F_1$?"*).
- **Dynamic Diagram Visual Highlighting:** Tutor synchronously highlights focal points, rays, or circuit branches on the canvas during explanations.

### Milestone PR-10: Research Paper Evaluation & Benchmarking
- **Comprehensive Benchmark Dataset:** Assemble an evaluation corpus of 100+ diagrams across secondary curriculums (NCTB, Cambridge O/A Levels, OpenStax).
- **Quantitative Metrics:**
  - Semantic classification accuracy (domain & subtype).
  - Geometric grounding precision (sub-pixel error $\le 5\text{ px}$).
  - OCR parameter extraction F1 score.
  - End-to-end compilation success rate.
- **Publication Manuscript:** Prepare formal paper submission detailing the architecture and empirical findings for an AI in Education (AIED) / Educational Technology venue.

---
*Report generated and approved by the AugmentedPhysics Engineering Team.*
