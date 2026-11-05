# AugmentedPhysics v2 — Full System Architecture, Historical Evolution & Technical Deep Dive

**Repository:** [rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook](https://github.com/rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook)  
**Project:** AugmentedPhysics v2  
**Target:** Multimodal Physics Textbook Diagram Understanding, Analytical Simulation Synthesis, and Intelligent Pedagogical Tutoring  
**Scope:** Complete technical reference covering everything built from Day 1 to the present (PR-01 through PR-06), detailing what each component is, how it was engineered, why it was designed that way, the mathematical formulas used, and the problems resolved.  
**Date:** October 2026  
**Status:** PR-01 through PR-06 Merged to `main` (`849cc1b`) | 100% Test Pass Rate (116 Python / 241 Frontend)

---

## Table of Contents

1. [Project Inception, Motivation & Vision](#1-project-inception-motivation--vision)
2. [The Core Philosophy: The Zero-Fabrication Invariant](#2-the-core-philosophy-the-zero-fabrication-invariant)
3. [Chronological Milestone Journey (PR-01 through PR-06)](#3-chronological-milestone-journey-pr-01-through-pr-06)
   - [PR-01: Strict Audit, Invariant Formalization & De-Fabrication](#pr-01-strict-audit-invariant-formalization--de-fabrication)
   - [PR-02: Canonical PhysicsScene Schema v1.0 & PhysicsRuntime](#pr-02-canonical-physicsscene-schema-v10--physicsruntime)
   - [PR-03: Source-Aligned Rendering & Bidirectional Manipulation](#pr-03-source-aligned-rendering--bidirectional-manipulation)
   - [PR-04: Real-File Ingestion, Cryptographic Identity & Gate Zero](#pr-04-real-file-ingestion-cryptographic-identity--gate-zero)
   - [PR-05: Multimodal VLM Semantic Understanding (Gemini)](#pr-05-multimodal-vlm-semantic-understanding-gemini)
   - [PR-06: Classical CV + Multilingual OCR Parameter Grounding](#pr-06-classical-cv--multilingual-ocr-parameter-grounding)
4. [End-to-End Architectural Pipeline & Intermediate Representations](#4-end-to-end-architectural-pipeline--intermediate-representations)
   - [The Five Canonical Data Representations](#the-five-canonical-data-representations)
   - [Coordinate Spaces: source_px, view_px, and world_m](#coordinate-spaces-source_px-view_px-and-world_m)
   - [The Non-Negotiable Status Invariant Hierarchy](#the-non-negotiable-status-invariant-hierarchy)
5. [The Multi-Domain Physics Solvers (Mathematical Foundations)](#5-the-multi-domain-physics-solvers-mathematical-foundations)
   - [Domain 1: Kinematics & Mechanics](#domain-1-kinematics--mechanics)
   - [Domain 2: Geometric Optics](#domain-2-geometric-optics)
   - [Domain 3: DC Linear Circuits (Modified Nodal Analysis)](#domain-3-dc-linear-circuits-modified-nodal-analysis)
6. [Perception, Vision & Document Intelligence Deep Dive](#6-perception-vision--document-intelligence-deep-dive)
   - [Multimodal VLM Classifier (Google Gemini)](#multimodal-vlm-classifier-google-gemini)
   - [Deterministic Classical Computer Vision Candidate Extractors](#deterministic-classical-computer-vision-candidate-extractors)
   - [Multilingual OCR Router (RapidOCR & EasyOCR Bangla)](#multilingual-ocr-router-rapidocr--easyocr-bangla)
   - [SAM 2 (Segment Anything 2) Mask Provider](#sam-2-segment-anything-2-mask-provider)
   - [Spatial-Semantic Grounding & Parameter Association](#spatial-semantic-grounding--parameter-association)
7. [Frontend Architecture & User Experience](#7-frontend-architecture--user-experience)
   - [Sub-Pixel 2-Layer Stage Alignment & CoordinateMapper](#sub-pixel-2-layer-stage-alignment--coordinatemapper)
   - [Common Interactive Runtime vs Legacy Studio](#common-interactive-runtime-vs-legacy-studio)
   - [Bidirectional Interactivity (Direct Drag Handles & Sliders)](#bidirectional-interactivity-direct-drag-handles--sliders)
   - [Telemetry Inspector & Grounded Bilingual AI Tutor](#telemetry-inspector--grounded-bilingual-ai-tutor)
8. [Comprehensive Testing, Invariants & Verification Matrix](#8-comprehensive-testing-invariants--verification-matrix)
9. [The Next Frontier: PR-07 Roadmap](#9-the-next-frontier-pr-07-roadmap)

---

## 1. Project Inception, Motivation & Vision

### 1.1 The Core Problem in STEM Education
Physics education in secondary and higher secondary schools across the developing and developed world relies overwhelmingly on printed textbooks. In countries like Bangladesh, where millions of students study under the **National Curriculum and Textbook Board (NCTB)** syllabus, textbook diagrams serve as the primary visual foundation for learning classical mechanics, geometric optics, and electric circuits.

However, static 2D printed diagrams have severe intrinsic limitations:
- **No Temporal Dynamics**: A diagram of a pendulum with an arrow showing motion cannot convey time periods, velocity profiles, damping, or kinetic-potential energy exchange.
- **No Counterfactual Exploration**: Students cannot ask: *"What if the lens had a shorter focal length?"*, *"What if the incident angle exceeded the critical angle?"*, or *"What happens if this resistor burns out?"*
- **Disconnection from Abstract Physics**: When students use external simulation software (like PhET or Algodoo), they are confronted with a blank, artificial vector stage that looks completely different from the diagram in their textbook exam questions.

### 1.2 The Research Paradigm
AugmentedPhysics is built upon the paradigm proposed by:
> **"Augmented Physics: Creating Interactive and Embedded Physics Simulations from Static Textbook Diagrams"**  
> *ACM UIST '24 — Gunturu et al.*

The core vision is: **Never discard the textbook illustration.** Instead, keep the authentic printed diagram as the base layer, and overlay an interactive, mathematically rigorous, sub-pixel-registered physics simulation directly onto it. The printed lines, labels, and figures come alive as interactive physical entities.

### 1.3 Book-Agnostic Design Guarantee
While NCTB secondary physics textbooks (Bangla and English versions) serve as the primary benchmark dataset, the entire platform—its schemas, coordinate transformers, computer vision algorithms, and solvers—is strictly **book-agnostic**. The platform can ingest textbook pages from Cambridge IGCSE, NCERT India, OpenStax, or Halliday & Resnick without rewriting physics engines.

---

## 2. The Core Philosophy: The Zero-Fabrication Invariant

### 2.1 The Fatal Flaw of Naive AI Systems: "Simulation Fabrication"
Prior to PR-01, early prototypes of AI-enhanced textbooks suffered from a critical flaw: **parameter and simulation fabrication**.
When given an ambiguous or incomplete diagram:
- If a diagram of an inclined ramp omitted the mass of the rolling cylinder, the code silently injected `mass = 1.0 kg` and `gravity = 9.81 m/s²`.
- If an optics diagram did not label the focal length, the system silently guessed `f = 20 cm`.
- If an uploaded file was named `lens.png`, heuristic string classifiers routed it to the optics engine without inspecting the image pixels.
- In the worst case, uploading a photograph of a cat or a landscape photo would cause the system to default to a swinging pendulum because the server insisted on running *something*.

### 2.2 Why Fabrication is Academically Destructive
In an educational tool, silent guessing is unacceptable. If a student uploads a textbook problem asking *"Find the unknown resistance $R$,"* and the software silently fills in $R = 10\,\Omega$ and runs a simulation, the student is misled into believing the textbook stated $10\,\Omega$. It destroys trust and undermines scientific pedagogy.

### 2.3 The Non-Negotiable Gate Zero Invariant
In AugmentedPhysics v2, the following rules are structurally enforced in code:
1. **Zero Parameter Guessing**: Missing physical values (mass, resistance, voltage, focal length) remain `null` or ungrounded. They are NEVER populated with arbitrary numbers.
2. **Zero Coordinate Fabrication**: Computer vision models cannot guess positions. If a pivot or lens cannot be detected with verified confidence, coordinates remain `null`.
3. **The Status Contract**:
   - `status == "ready"` **strictly requires** a non-null, fully verified `scene`.
   - `status != "ready"` (`needs_review`, `unsupported`, `unresolved`) **strictly requires** `scene: null`.
4. **Honest Review over Fake Physics**: If a diagram has missing evidence, the system halts at Gate Zero, displays diagnostic badges detailing what is missing, and opens a review drawer for user input.

---

## 3. Chronological Milestone Journey (PR-01 through PR-06)

### PR-01: Strict Audit, Invariant Formalization & De-Fabrication
- **Context & Motivation**: The repository contained legacy shortcuts where heuristic classifiers checked file names and fallback logic generated synthetic scenes from empty evidence.
- **What Was Done**:
  - Audited the entire backend (`apps/api/main.py`) and eliminated all filename-based physics routing.
  - Implemented `make_analysis_response(...)`, structurally enforcing the status-scene contract.
  - Introduced the parameter provenance contract: every physical value must declare its provenance (`observed`, `derived`, `assumed`, `default`, `student`).
  - Added negative-path tests verifying that non-physics images or missing parameters never yield executable physics scenes.
- **Key Files**: [`apps/api/main.py`](file:///d:/AugmentedPhysics/apps/api/main.py), [`shared/schemas/`](file:///d:/AugmentedPhysics/shared/schemas/).

### PR-02: Canonical PhysicsScene Schema v1.0 & PhysicsRuntime
- **Context & Motivation**: Frontend simulations relied on ad-hoc, disparate JSON structures between mechanics, optics, and circuits. Solvers were tightly coupled to specific DOM elements.
- **What Was Done**:
  - Created the canonical `PhysicsScene` schema (v1.0 / v2.1) defining domain, subtype, elements, coordinate frames, parameters, and render bounds.
  - Built `PhysicsRuntime.js` as an engine-agnostic lifecycle coordinator managing start, pause, reset, step, and parameter update loops.
  - Built `SolverRegistry.js` allowing domain engines to register independently.
  - Established the multi-coordinate system standard (`source_px`, `view_px`, `world_m`).
- **Key Files**: [`engine/core/PhysicsRuntime.js`](file:///d:/AugmentedPhysics/engine/core/PhysicsRuntime.js), [`shared/schemas/physics_scene.schema.json`](file:///d:/AugmentedPhysics/shared/schemas/physics_scene.schema.json).

### PR-03: Source-Aligned Rendering & Bidirectional Manipulation
- **Context & Motivation**: Students needed to interact with textbook diagrams directly on the canvas, not merely adjust sliders in a sidebar.
- **What Was Done**:
  - Implemented `RendererRegistry.js` and `SimulationCapabilityRegistry.js`.
  - Built direct-manipulation drag handles on top of canvas elements (optical object arrows, pendulum bobs, circuit switches).
  - Established bidirectional synchronization: dragging a handle on the canvas updates the physics solver and HUD readouts; modifying a slider in the HUD immediately repositions the canvas drag handle and updates the simulation overlay.
  - Solved sub-pixel alignment across varied screen resolutions using `CoordinateMapper.js`.
- **Key Files**: [`apps/web/src/features/simulations/core/RendererRegistry.js`](file:///d:/AugmentedPhysics/apps/web/src/features/simulations/core/RendererRegistry.js), [`apps/web/src/features/simulations/core/SimulationCapabilityRegistry.js`](file:///d:/AugmentedPhysics/apps/web/src/features/simulations/core/SimulationCapabilityRegistry.js).

### PR-04: Real-File Ingestion, Cryptographic Identity & Gate Zero
- **Context & Motivation**: The application needed to transition from loading pre-authored JSON test fixtures to accepting arbitrary user-uploaded scans and photos.
- **What Was Done**:
  - Engineered `UploadService.py` with streaming chunked reads (supporting files up to 50 MB) and cryptographic raw-byte SHA-256 fingerprinting. Filenames are treated strictly as metadata.
  - Established canonical Intermediate Representations: `SourceAsset` $\to$ `PageIR` $\to$ `BookIR`.
  - Built the **Gate Zero UI** (`UploadModal.js` and `IRDebugPanel.js`): when an uploaded image is processed, if evidence is missing, the UI gracefully renders a diagnostic drawer detailing ungrounded entities and missing parameters without crashing or faking physics.
- **Key Files**: [`ai/ingestion/SourceAsset.py`](file:///d:/AugmentedPhysics/ai/ingestion/SourceAsset.py), [`ai/ingestion/PageIRBuilder.py`](file:///d:/AugmentedPhysics/ai/ingestion/PageIRBuilder.py), [`ai/ingestion/UploadService.py`](file:///d:/AugmentedPhysics/ai/ingestion/UploadService.py).

### PR-05: Multimodal VLM Semantic Understanding (Gemini)
- **Context & Motivation**: Rule-based computer vision alone struggled to identify whether a complex diagram was an optical bench, an electrical schematic, or a kinematics problem. Foundation Vision-Language Models (VLMs) were needed for semantic categorization.
- **What Was Done**:
  - Integrated Google Gemini via the official `google-genai` SDK (`GeminiVisionProvider`).
  - **Strict Semantic Boundary**: The VLM is strictly confined to semantic classification:
    - Allowed: Categorizing `isPhysics` (boolean), `domain`, `subtype`, and rough entity taxonomy (`pivot`, `bob`, `cord`, `lens`, `resistor`).
    - Prohibited: The VLM is strictly forbidden from generating numbers (mass, voltage, focal length) or authoritative coordinates.
  - **Conservative Confidence Policy**: Reserved $1.0$ confidence exclusively for verified ground truth. VLM confidence is capped below $1.0$, and overall confidence is computed as:
    $$\text{confidence}_{\text{overall}} = \min(\text{isPhysics}, \text{domain}, \text{subtype})$$
  - **Async Event Loop Offloading**: Heavy synchronous network calls offloaded via `await asyncio.to_thread(...)` to ensure FastAPI's event loop never freezes.
  - Created `MockVisionProvider` with canned responses for offline, deterministic CI/CD testing with zero network overhead.
- **Key Files**: [`ai/ingestion/vision/gemini_provider.py`](file:///d:/AugmentedPhysics/ai/ingestion/vision/gemini_provider.py), [`ai/ingestion/vision/analyzer.py`](file:///d:/AugmentedPhysics/ai/ingestion/vision/analyzer.py), [`shared/schemas/semantic.py`](file:///d:/AugmentedPhysics/shared/schemas/semantic.py).

### PR-06: Classical CV + Multilingual OCR Parameter Grounding (Current State)
- **Context & Motivation**: While PR-05 recognized *what* the diagram was semantically, it left physical parameters empty (`{}`) and coordinates ungrounded (`null`). PR-06 was engineered to read printed text (in English, Bangla, and Greek symbols) and locate exact geometry via deterministic CV and SAM 2.
- **What Was Done**:
  - Built 7 domain-specific **Classical CV Extractors** (Pendulum, Projectile, Thin Lens, Spherical Mirror, Interface Refraction, Triangular Prism, Circuits).
  - Built the **Multilingual OCR Router** (`MultiOCRRouter`): combines RapidOCR (ONNX Runtime) for English numbers and units, and EasyOCR for Bengali script (`১০ ওহম`, `২০ সে.মি.`).
  - Integrated **Greek Physics Symbol Detection**: resolves symbols easily confused by standard OCR ($\theta, \lambda, \Omega, \mu, \Sigma$).
  - Built **SAM 2 Provider** (`SAM2SegmentationProvider`) for sub-pixel boundary mask extraction.
  - Built **GrounderRegistry**: spatial-semantic fusion matching OCR text tokens to geometric candidates without coordinate guessing.
  - Created typed evidence contracts in [`shared/schemas/evidence.py`](file:///d:/AugmentedPhysics/shared/schemas/evidence.py).
- **Key Files**: [`ai/evidence/`](file:///d:/AugmentedPhysics/ai/evidence/), [`shared/schemas/evidence.py`](file:///d:/AugmentedPhysics/shared/schemas/evidence.py), [`tests/unit/test_pr06_*.py`](file:///d:/AugmentedPhysics/tests/unit/).

---

## 4. End-to-End Architectural Pipeline & Intermediate Representations

### 4.1 The Five Canonical Data Representations

```
Raw Image Bytes (Disk)
       │
       ▼
1. SourceAsset ─────────► Immutable container: SHA-256 hash, MIME, dimensions
       │
       ▼
2. PageIR ──────────────► Normalized source_px viewport, figure bounding boxes
       │
       ▼
3. Semantic BookIR ─────► PR-05 VLM output: domain, subtype, rough roles (no numbers)
       │
       ▼
4. Grounded BookIR ─────► PR-06 CV+OCR output: verified geometries & parsed values
       │
       ▼
5. PhysicsScene ────────► Executable simulation JSON consumed by browser engines
```

1. **`SourceAsset`** ([`shared/schemas/ingestion.py`](file:///d:/AugmentedPhysics/shared/schemas/ingestion.py)):
   - Encapsulates the immutable uploaded diagram.
   - Holds SHA-256 cryptographic digest, MIME type, file size, and native dimensions $(W_{\text{src}}, H_{\text{src}})$.
2. **`PageIR`** ([`shared/schemas/ingestion.py`](file:///d:/AugmentedPhysics/shared/schemas/ingestion.py)):
   - Represents the page layout and identified figure regions in native `source_px`.
   - Isolates the diagram crop so surrounding textbook paragraphs do not distort coordinates.
3. **`BookIR` (Semantic)** ([`shared/schemas/ingestion.py`](file:///d:/AugmentedPhysics/shared/schemas/ingestion.py)):
   - Represents the high-level semantic physics model.
   - In PR-05, entities hold coarse bounding boxes (`vlmApproxBBox`), but numerical parameters are strictly empty (`{}`) and coordinates are ungrounded (`position_source_px = None`).
4. **`Grounded BookIR`** ([`shared/schemas/evidence.py`](file:///d:/AugmentedPhysics/shared/schemas/evidence.py)):
   - Enriched by PR-06 evidence extraction. Contains geometric candidates (lines, circles, vertices), verified OCR tokens, and spatial-semantic parameter bindings.
5. **`PhysicsScene`** ([`shared/schemas/physics_scene.schema.json`](file:///d:/AugmentedPhysics/shared/schemas/physics_scene.schema.json)):
   - The canonical simulation contract consumed by frontend renderers.
   - Contains elements, parameters, coordinate transformation metadata, and rendering instructions.

### 4.2 Coordinate Spaces: source_px, view_px, and world_m

A major source of bugs in graphics and simulation systems is coordinate confusion. AugmentedPhysics explicitly separates three coordinate frames:

| Space | Unit | Purpose | Transformation |
| :--- | :--- | :--- | :--- |
| **`source_px`** | Pixels | Native image resolution (e.g., $1024 \times 768$). All CV, OCR, and authoring coordinates are stored here. | Ground truth frame. |
| **`view_px`** | Pixels | CSS layout coordinates in the browser viewport. Varies based on user window size. | $\text{view\_px} = s \cdot \text{source\_px} + \text{offset}$ (via `CoordinateMapper`) |
| **`world_m`** | Meters | Real-world SI units used by mathematical differential equation solvers. | $\text{world\_m} = \text{source\_px} \times \text{pixel\_scale}$ |

### 4.3 The Non-Negotiable Status Invariant Hierarchy

The system defines four mutually exclusive compilation statuses:
- **`READY`**: All required parameters and geometry have been verified. Returns a non-null `PhysicsScene`. The browser immediately boots the interactive simulation.
- **`NEEDS_REVIEW`**: The diagram was recognized as a supported physics domain, but one or more parameters or geometries are ungrounded. Returns `scene: null`. The browser opens the Gate Zero review drawer.
- **`UNSUPPORTED`**: The diagram is genuine physics, but the specific subtype (e.g., thermodynamics, wave interference) is not yet implemented in solvers. Returns `scene: null`.
- **`UNRESOLVED`**: The uploaded image is not a physics diagram, is corrupted, or has unresolvable ambiguities. Returns `scene: null`.

---

## 5. The Multi-Domain Physics Solvers (Mathematical Foundations)

### Domain 1: Kinematics & Mechanics

#### 1. High-Precision Runge-Kutta 4 (RK4) Nonlinear Pendulum Solver
In physics textbooks, pendulums are often depicted swinging at large initial angles ($\theta_0 = 30^\circ - 60^\circ$). Standard simulation engines make the small-angle approximation $\sin\theta \approx \theta$, which introduces noticeable frequency errors. AugmentedPhysics integrates the exact nonlinear ordinary differential equation:
$$\frac{d^2\theta}{dt^2} + \frac{b}{m}\frac{d\theta}{dt} + \frac{g}{L}\sin(\theta) = 0$$

Let $\omega = \frac{d\theta}{dt}$. The system is converted into two coupled first-order ODEs:
$$\begin{cases}
\frac{d\theta}{dt} = \omega \\
\frac{d\omega}{dt} = -\frac{g}{L}\sin(\theta) - \frac{b}{m}\omega
\end{cases}$$

The state vector $\mathbf{y} = [\theta, \omega]^T$ is updated using 4th-order Runge-Kutta:
$$\mathbf{y}_{n+1} = \mathbf{y}_n + \frac{\Delta t}{6} \left(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4\right)$$
where:
$$\begin{aligned}
\mathbf{k}_1 &= f(t_n, \mathbf{y}_n) \\
\mathbf{k}_2 &= f\left(t_n + \frac{\Delta t}{2}, \mathbf{y}_n + \frac{\Delta t}{2}\mathbf{k}_1\right) \\
\mathbf{k}_3 &= f\left(t_n + \frac{\Delta t}{2}, \mathbf{y}_n + \frac{\Delta t}{2}\mathbf{k}_2\right) \\
\mathbf{k}_4 &= f(t_n + \Delta t, \mathbf{y}_n + \Delta t\mathbf{k}_3)
\end{aligned}$$
Executed at 240 Hz sub-stepping, this maintains an energy conservation drift of $< 0.05\%$ over 10 minutes of simulation.

#### 2. Matter.js 2D Rigid Body Dynamics & Concave Polygon Decomposition
For projectile trajectories, inclined planes, and curved ramps:
- Uses `poly-decomp` to decompose non-convex textbook terrain into convex hulls.
- Solves centroid-shift alignment: when Matter.js creates a body from vertices via `Bodies.fromVertices`, it shifts the origin to the center of mass. Our engine calculates the exact offset vector and realigns the body with sub-pixel precision ($< 10^{-14}$ error), ensuring rolling balls do not sink into or hover over the printed ramp.
- Invisible Colliders: Static background scenery is rendered with `render.visible = false` so that the original printed diagram remains pristine while providing physical collision boundaries.

---

### Domain 2: Geometric Optics

#### 1. Gaussian Thin Lens Analytical Ray Tracer
For biconvex and biconcave lenses, principal rays are computed analytically using the Gaussian lens equation:
$$\frac{1}{f} = \frac{1}{u} + \frac{1}{v}, \quad m = -\frac{v}{u}$$
where:
- $u$: Object distance from optical center (by Cartesian convention, $u < 0$ for real objects to the left).
- $v$: Image distance ($v > 0$ for real inverted images to the right; $v < 0$ for virtual erect images to the left).
- $f$: Focal length ($f > 0$ for converging convex lenses; $f < 0$ for diverging concave lenses).
- $m$: Linear magnification ($m = h_i / h_o$).

The engine traces three canonical principal rays:
1. **Parallel Ray**: Emanates from the object tip parallel to the optical axis, refracts through the focal point $F_2$.
2. **Central Ray**: Passes directly through the optical center $(x_0, y_0)$ without angular deviation.
3. **Focal Ray**: Passes through the front focal point $F_1$, emerging parallel to the optical axis.

#### 2. Vector Snell's Law & Total Internal Reflection (TIR)
At planar dielectric interfaces (e.g., air-water or air-glass), incident rays are refracted using the vector formulation of Snell's Law:
$$\vec{r} = \frac{n_1}{n_2} \vec{d} + \left( \frac{n_1}{n_2} \cos\theta_1 - \sqrt{1 - \left(\frac{n_1}{n_2}\right)^2 (1 - \cos^2\theta_1)} \right) \vec{n}$$
where $\vec{d}$ is the incident unit vector and $\vec{n}$ is the interface surface normal.

The critical angle $\theta_c$ is calculated:
$$\theta_c = \arcsin\left(\frac{n_2}{n_1}\right) \quad (\text{for } n_1 > n_2)$$
If the angle of incidence $\theta_1 \ge \theta_c$, the term inside the square root becomes negative, signaling Total Internal Reflection. The engine seamlessly branches to the reflection law:
$$\vec{r}_{\text{refl}} = \vec{d} - 2(\vec{d} \cdot \vec{n})\vec{n}$$

#### 3. Triangular Prism Ray Deviation
For triangular prisms with apex angle $A$ and refractive index $n$:
$$\delta = (i_1 - r_1) + (i_2 - r_2) = i_1 + i_2 - A$$
At the minimum deviation condition ($\delta = \delta_m$), symmetry dictates $i_1 = i_2$ and $r_1 = r_2 = A/2$, yielding:
$$n = \frac{\sin\left(\frac{A + \delta_m}{2}\right)}{\sin\left(\frac{A}{2}\right)}$$

---

### Domain 3: DC Linear Circuits (Modified Nodal Analysis)

#### 1. Browser-Native Modified Nodal Analysis (MNA)
Unlike mechanics engines that simulate collisions, electrical circuits operate on topological conservation laws. AugmentedPhysics solves circuits using Modified Nodal Analysis formulated as:
$$\begin{bmatrix}
\mathbf{G} & \mathbf{B} \\
\mathbf{C} & \mathbf{D}
\end{bmatrix}
\begin{bmatrix}
\mathbf{v} \\
\mathbf{j}
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{i} \\
\mathbf{e}
\end{bmatrix}$$
where:
- $\mathbf{G}$: Conductance matrix ($N \times N$) derived from resistor branch conductances ($g_k = 1/R_k$).
- $\mathbf{B}$: Incidence matrix coupling independent voltage sources to nodes.
- $\mathbf{C}$: Transpose of $\mathbf{B}$ for independent sources.
- $\mathbf{D}$: Zero matrix for ideal independent voltage sources.
- $\mathbf{v}$: Vector of unknown node voltages with respect to reference ground ($V_0 = 0\,\text{V}$).
- $\mathbf{j}$: Vector of unknown currents flowing through voltage sources.
- $\mathbf{i}$: Vector of injected currents from current sources.
- $\mathbf{e}$: Vector of independent voltage source values.

The system performs **LU Decomposition with partial pivoting** directly on JavaScript typed `Float64Array` buffers in the browser, achieving sub-millisecond execution times at 60 FPS.

#### 2. Union-Find Electrical Node Clustering
Hand-drawn or scanned textbook circuits have disjoint wire lines that visually meet at junctions. The engine implements a Disjoint-Set Union (Union-Find) algorithm with adaptive geometric snapping ($r_{\text{snap}} = \max(3 \cdot \text{stroke}, 0.005 \cdot \text{diagonal})$). All touching wire endpoints and component terminals are clustered into discrete electrical nodes, deterministically establishing the circuit graph topology.

#### 3. Animated Electron Flow
Wires are compiled into cumulative arc-length polylines. Animated charge carrier particles travel along the wires with velocities strictly proportional to the solved branch current:
$$v_{\text{particle}} = \alpha \cdot |I_{\text{branch}}|$$
The direction of particle drift dynamically reverses if the user toggles a voltage source or changes resistor values.

---

## 6. Perception, Vision & Document Intelligence Deep Dive

### 6.1 Multimodal VLM Classifier (Google Gemini)
- **Model Architecture**: Uses Google Gemini (`gemini-2.5-flash` / `gemini-3.1-flash-lite`) via `google-genai`.
- **Structured JSON Schema**: Prompts are constrained by strict JSON schema contracts (`shared/schemas/semantic.py`), requiring the model to emit typed categorizations.
- **Quarantined Roles**: Bounding boxes emitted by the VLM are tagged as `vlmApproxBBox` and used strictly as search regions for downstream classical CV. They are never treated as authoritative pixel coordinates.

### 6.2 Deterministic Classical Computer Vision Candidate Extractors
Located in [`ai/evidence/cv/`](file:///d:/AugmentedPhysics/ai/evidence/cv/):

1. **`PendulumCVCandidateExtractor`**:
   - Applies Otsu thresholding and morphological opening to isolate dark structural elements.
   - Detects circular bobs using Hough Circle Transform ($R \in [10, 80]$ px).
   - Traces the suspension cord using skeletonization (`skimage.morphology.skeletonize`) and Hough Line Transforms.
   - Computes the pivot point as the intersection of the cord line with the upper support boundary.
2. **`ThinLensCVCandidateExtractor`**:
   - Detects the long horizontal optical axis using directional morphological kernels.
   - Locates the vertical lens aperture line and calculates the optical center $(x_0, y_0)$ using sub-pixel column intensity profiles.
   - Scans along the optical axis for tick marks and focal markers ($F_1, F_2, 2F$).
3. **`InterfaceRefractionCVCandidateExtractor`**:
   - Identifies the horizontal medium interface boundary line.
   - Identifies the vertical normal line at the point of incidence.
   - Traces incident and refracted ray segments to calculate angles $\theta_1$ and $\theta_2$ relative to the normal.
4. **`SphericalMirrorCVCandidateExtractor`**:
   - Extracts vertical curved contours.
   - Fits a circle via algebraic least-squares to extract the center of curvature $(C_x, C_y)$, radius $R$, and pole $P$.
5. **`PrismCVCandidateExtractor`**:
   - Uses Douglas-Peucker polygon approximation on closed contours to extract the three vertices of triangular prisms.
6. **`CircuitCVCandidateExtractor`**:
   - Extracts rectangular schematic loops, orthogonal wire corners, and terminal solder pads.

### 6.3 Multilingual OCR Router (RapidOCR & EasyOCR Bangla)
Textbooks contain diverse typography:
- **`RapidOCRProvider`**: Runs ONNX Runtime locally on CPU. Rapidly extracts English numbers, decimals, and Latin letters (`12 V`, `20 cm`, `5 kg`).
- **`BanglaOCRProvider`**: Powered by EasyOCR. Accurately decodes Bengali script and numerals (`১০ ওহম`, `১৫ সেমি`, `৪৫°`).
- **`GreekSymbolDetector`**: Specialized rule-based resolver for confusable physics symbols ($\Omega$ confused with `O`, $\theta$ confused with `0`, $\mu$ confused with `u`).

### 6.4 SAM 2 (Segment Anything 2) Mask Provider
- Powered by Meta's SAM 2 Hiera Tiny checkpoint (`sam2.1_hiera_tiny.pt`).
- Accepts candidate point prompts or bounding box priors generated by classical CV to extract exact alpha-transparent foreground masks.
- Enables the extraction of dynamic sprites (e.g., an authentic textbook candle, pendulum bob, or rolling ball) that move across the canvas.

### 6.5 Spatial-Semantic Grounding & Parameter Association
- **`PhysicalValueParser`**: Converts unstructured OCR strings into standardized SI floats:
  - `"20 cm"` $\to$ `0.20 m`
  - `"10 kohm"` $\to$ `10,000 Ω`
  - `"45 deg"` $\to$ `45.0°`
- **`GrounderRegistry`**: Uses spatial Euclidean proximity and directional ray casting to link a parsed value (`10 Ω`) to the nearest physical component candidate (a resistor symbol), creating a verified parameter binding with full provenance.

---

## 7. Frontend Architecture & User Experience

```
┌────────────────────────────────────────────────────────────────────────┐
│                        apps/web/index.html                             │
├───────────────────────────────────┬────────────────────────────────────┤
│ Domain Switcher                   │ Gate Zero Upload Trigger           │
│ (Kinematics / Optics / Circuits)  │ (Drag-and-Drop Diagram Modal)      │
├───────────────────────────────────┴────────────────────────────────────┤
│ Platform Mode Bar:                                                     │
│ [⚡ Common Interactive Runtime <InteractiveFigure>] [🛠 Legacy Studio]  │
├────────────────────────────────────────────────────────────────────────┤
│ <InteractiveFigure> Container:                                         │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ 2-Layer Composite Stage                                      │     │
│   │   Layer 1 (Base):  <img id="diagram-image"> (Authentic Scan) │     │
│   │   Layer 2 (Top):   <canvas> (60 FPS P5 / Matter.js Overlay)  │     │
│   └──────────────────────────────────────────────────────────────┘     │
├───────────────────────────────────┬────────────────────────────────────┤
│ Live Telemetry Inspector Table    │ Dynamic Parameter HUD Cards        │
│ (Energy, Angles, Voltages)        │ (Bidirectional Sliders & Toggles)  │
├───────────────────────────────────┴────────────────────────────────────┤
│ Grounded Bilingual AI Tutor Drawer (Bangla/English Socratic Guidance)  │
└────────────────────────────────────────────────────────────────────────┘
```

### 7.1 Sub-Pixel 2-Layer Stage Alignment & CoordinateMapper
- To ensure responsive scaling without visual misalignment, `CoordinateMapper.js` calculates CSS `object-fit: contain` geometry:
  $$s = \min\left(\frac{W_{\text{viewport}}}{W_{\text{source}}}, \frac{H_{\text{viewport}}}{H_{\text{source}}}\right)$$
  $$\text{offset}_x = \frac{W_{\text{viewport}} - s \cdot W_{\text{source}}}{2}, \quad \text{offset}_y = \frac{H_{\text{viewport}} - s \cdot H_{\text{source}}}{2}$$
- Converts bidirectional mouse events:
  $$\begin{aligned}
  x_{\text{source}} &= \frac{x_{\text{mouse}} - \text{offset}_x}{s} \\
  y_{\text{source}} &= \frac{y_{\text{mouse}} - \text{offset}_y}{s}
  \end{aligned}$$
- Guarantees that interactive handles remain locked directly on top of printed diagram lines on mobile, tablet, and 4K displays.

### 7.2 Common Interactive Runtime vs Legacy Studio
- **Common Runtime (`<InteractiveFigure>`)**: Modern, unified presentation component for canonical verification figures (Pendulum, Convex Lens, DC Loop, Projectile).
- **Legacy Studio**: Comprehensive multi-domain laboratory with manual scenario selectors, canvas inspectors, and direct component editors.

### 7.3 Bidirectional Interactivity
- Moving an optical candle on the canvas immediately updates the focal calculation in the HUD.
- Typing `30 cm` into the HUD slider immediately moves the candle on the canvas.
- Clicking a circuit switch flips the boolean state, recalculates the MNA matrix, and redirects electron particle flow.

### 7.4 Telemetry Inspector & Grounded Bilingual AI Tutor
- Real-time telemetry inspector displays live quantities (kinetic energy, angular momentum, loop currents, magnification).
- The AI Tutor drawer provides curriculum-grounded Socratic explanations in both English and Bangla without hallucinating nonexistent textbook facts.

---

## 8. Comprehensive Testing, Invariants & Verification Matrix

The repository enforces strict test automation across both Python backend services and JavaScript frontend modules:

| Test Suite | Location | Test Count | Pass Rate | What It Verifies |
| :--- | :--- | :--- | :--- | :--- |
| **Python Unit Tests** | `tests/unit/` | **116** | **100%** | Schema invariants, MNA matrix math, CV candidate extractors, OCR parsing, coordinate transforms, and negative grounding rejection. |
| **Python Integration**| `tests/integration/` | **3** | **100%** | End-to-end file upload API, VLM mock pipelines, and evidence extraction workflows. |
| **Acceptance Tests** | `tests/acceptance/` | **3** | **100%** | Unseen textbook scan benchmarks (pendulum, circuit, optics) and adversarial non-physics inputs. |
| **Frontend Unit Tests**| `apps/web/` (`npm test`) | **241** | **100%** | CoordinateMapper letterboxing, optics ray-tracer, pendulum RK4 dynamics, MNA circuit solver, and UI handlers. |
| **Total Automated Tests**| Repository-wide | **363** | **100%** | Zero failing tests across the entire codebase. |

---

## 9. The Next Frontier: PR-07 Roadmap

With PR-01 through PR-06 successfully merged into `main`, all foundational components (solvers, schemas, VLM semantics, classical CV, multilingual OCR, and spatial grounding) are operational.

### The PR-07 Objective: End-to-End Simulation Bootstrapping
PR-07 will fuse PR-05 semantic roles with PR-06 perceptual evidence to achieve fully automated, zero-touch simulation bootstrapping:
1. **Automated Pipeline Binding**: Direct routing from `/api/ingest` through `EvidenceExtractionPipeline` to produce `BookIR(RESOLVED)`.
2. **PhysicsScene Synthesis**: Automatic instantiation of canonical `PhysicsScene` objects from grounded entities.
3. **Classroom Benchmark Validation**: Comprehensive evaluation across 50+ real NCTB textbook scans spanning Class 9-10 and Class 11-12 physics curricula.

---

*Report authored for AugmentedPhysics v2. Validated against repository commit `849cc1b`.*
