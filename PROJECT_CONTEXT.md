# AI-Enhanced Interactive NCTB Physics Textbook: Complete Project Knowledge Base & Context

> **Project Name**: AugmentedPhysics  
> **Target**: Multimodal NCTB Physics Diagram Understanding, Physics Simulation, and Bangla Intelligent Tutoring  
> **Reference Paper**: *"Augmented Physics: Creating Interactive and Embedded Physics Simulations from Static Textbook Diagrams"* (UIST '24) — Gunturu et al.  
> **Environment**: Windows 11, Python 3.13.5, RTX 3050 Laptop GPU (6 GB VRAM), CUDA 13.0, PyTorch 2.14+, Meta SAM 2 (SAM 2.1 Hiera Tiny).

---

## 1. High-Level Vision & Purpose

This project transforms static physics textbook pages (specifically NCTB Bangladesh curriculum) into an interactive, grounded learning experience:

```
[NCTB Textbook Page / Diagram]
             │
             ▼
[Multimodal Perception: SAM 2 + OCR/VLM]
 (Isolates visual objects & extracts geometry + RGBA sprites)
             │
             ▼
[Canonical PhysicsScene v2 (JSON)]
 (Domain-neutral, preserves uncertainty, no guessed physics)
             │
             ▼
[Scene Compiler & Domain Adapters]
 (Matter.js 2D Rigid-body / Optics / Circuits / GSAP Animation)
             │
             ▼
[Embedded Simulation Stage (Layered HTML/CSS)]
 (Layer 1: Textbook Diagram | Layer 2: Transparent Matter.js Canvas)
             │
             ▼
[Bangla Intelligent Pedagogical Tutor]
 (Grounded in textbook text, diagram geometry, and live simulation state)
```

---

## 2. Core Concepts in Plain Language

| Concept | Plain-Language Explanation | Role in AugmentedPhysics |
| :--- | :--- | :--- |
| **Model Architecture** | The blueprint or neural network design (e.g. SAM 2 Hiera architecture). Like an empty brain design before studying. | Defines how the image encoder, prompt encoder, and mask decoder communicate. |
| **Checkpoint (`.pt`)** | The saved numerical weights resulting from training on millions of images. The "learned experience/brain". | `sam2.1_hiera_tiny.pt` provides the pre-trained weights so SAM 2 knows what object boundaries look like. |
| **PyTorch & CUDA** | PyTorch is the mathematical engine running the neural net; CUDA connects PyTorch directly to NVIDIA GPU hardware cores. | Enables fast, real-time matrix operations on the local RTX 3050 (6 GB) instead of running slow on CPU. |
| **Segmentation Mask** | A binary/per-pixel map ($H \times W$) where $1 = \text{object}$, $0 = \text{background}$. | Isolates the exact pixels of the ball, block, slope, or ground from the textbook background. |
| **Prompt (Points / Boxes)** | Visual cues provided to SAM: positive point (label=1, "include this") or negative point (label=0, "exclude this"). | Allows human or AI to point at a diagram element to extract it without manual lassoing. |
| **Segmentation vs Tracking** | Segmentation isolates an object in a **single static image**. Tracking follows the same object across **multiple video frames**. | Current work is **image segmentation**. Video tracking is for dynamic live-camera/animation later. |
| **Multi-Mask Output** | When a prompt is ambiguous, SAM produces 3 candidate masks with confidence scores. | We re-rank these using stability, prompt consistency, and connectedness to select the true whole object. |
| **Physics Body (Polygon / Circle)** | The invisible mathematical representation ($x, y$ vertices or radius) that calculates collisions, gravity, and velocities. | In real life, physics is invisible. Matter.js calculates momentum and contact along these shapes. |
| **Sprite (Visual Cutout)** | The transparent RGBA image crop extracted from the original diagram using the SAM mask. | Textured onto moving Matter.js bodies so the real textbook object moves and rolls naturally. |
| **Embedded Canvas** | A transparent Matter.js canvas positioned directly over the textbook image. | Allows the simulation to happen directly "inside" the textbook page instead of on a detached gray canvas. |
| **PhysicsScene JSON** | Structured representation storing geometry, author roles, and physics parameters. | The contract separating computer vision from physics simulation engines. |

---

## 3. Milestone Progress to Date

### ✅ Milestone 1: Local SAM 2 Setup & First Single-Object Segmentation
- **Environment Established**: Resolved Windows multi-Python conflict (Python 2.7 -> Python 3.13.5). Created isolated virtual environment `.venv`.
- **GPU Acceleration**: Verified RTX 3050 (6 GB VRAM) with CUDA runtime through PyTorch (`torch.cuda.is_available() == True`).
- **SAM 2 Installed**: Cloned Meta `sam2`, downloaded `sam2.1_hiera_tiny.pt`, resolved Hydra configuration path (`configs/sam2.1/sam2.1_hiera_t.yaml`).
- **Pipeline Execution**: Encoded test image with SAM 2 image predictor, fed a single positive point prompt, generated candidate masks, selected top mask, and visualized overlay.

### ✅ Milestone 2: Multi-Object Segmentation & Candidate Mask Re-ranking
- Tested on multiple objects (e.g., three separate balls in one image).
- **Key Discovery**: The candidate mask with the highest raw SAM predicted-IoU score is often an internal sub-part rather than the whole object. Motivated multi-signal re-ranking (prompt consistency, contour stability, connectedness, overlap penalty).

### ✅ Milestone 3: Robust Interactive Scene Authoring Pipeline
- Built modular CV pipeline under `backend/`:
  - `backend/core/`: Shared CV utilities (`geometry_utils.py`, `mask_quality.py`, `scene_builder.py`, `sprite_utils.py`).
  - `backend/kinematics/`: Mechanics authoring GUI (`build_kinematics_scene.py`) exporting Matter.js scenes.
  - `backend/optics/`: Optics authoring GUI (`build_optics_scene.py`) supporting thin lenses, prisms, and mirrors for Optics2D.


### ✅ Milestone 4: Embedded Diagram Simulation, Sprites & Complex Kinematics
- **Transparent RGBA Sprite Extraction**: Implemented `sprite_utils.py`. Dynamic objects are automatically cut out from the source diagram as transparent PNGs (`/sprites/element_001.png`).
- **Embedded Composite Stage**:
  - 2-layer stage:
    - Layer 1: `<img id="diagram-image">` (original textbook diagram).
    - Layer 2: Transparent Matter.js canvas overlaid with 1:1 pixel coordinate alignment.
- **Invisible Static Collider Architecture**:
  - For static scenery (curved ramps, ground, walls), the textbook illustration is visible underneath. Matter.js sets `render.visible = false` on static colliders so no synthetic shapes obscure the diagram.
- **Concave Polygon Decomposition & Sub-Pixel Alignment**:
  - Integrated `poly-decomp` and `Common.setDecomp(decomp)` in Matter.js.
  - Resolved Matter.js `Bodies.fromVertices` decomposed centroid shift: after decomposition, the composite body bounds are aligned to the exact input vertices with sub-pixel precision (`< 1e-14` error), ensuring balls roll exactly on the visible surface without sinking inside the ramp.
- **Dynamic Spring System**:
  - Built a 1D restoring spring constraint with movable plunger plate in `physicsBodyFactory.js` and `simulation.js`, perfectly aligned with diagram coordinates (`y = 367.29 px`). When the ball rolls down the curve, it collides with the plunger, compresses the spring, and rebounds.

### ✅ Milestone 5: Domain Engine Splitting & Modern Architecture (`augmented_physics_v2`)
- **Authoritative Source-Pixel Coordinate System**:
  - Implemented `CoordinateMapper` (`src/core/coordinateMapper.js`) mapping native source diagram pixels directly to viewport CSS and physical device pixels via standard CSS `object-fit: contain` letterboxing with bidirectional inversion.
- **Dedicated Analytical RK4 Integrator for Simple Pendulums**:
  - Replaced imprecise spring/constraint approximations with `PendulumSimulation` (`src/mechanics/pendulumSimulation.js`), integrating full nonlinear equations $\ddot{\theta} + \frac{g}{L}\sin\theta + \beta\dot{\theta} = 0$ at 240 Hz with energy drift $< 0.05\%$.
- **Analytical Projectile Kinematics Engine**:
  - Built `ProjectileSimulation` (`src/mechanics/projectileSimulation.js`) with exact closed-form trajectories ($x(t)$, $y(t)$, apex, landing velocity) and interactive trace overlay.
- **Geometric Optics 2D Precision Ray Tracer**:
  - Built comprehensive ray optics suite (`src/optics/`):
    - Thin lens formula ($1/f = 1/u + 1/v$) with real/virtual image states and principal rays.
    - Spherical mirror solver (concave/convex, left/right bidirectional).
    - Snell's Law refractor with critical angle $\theta_c$ calculation and Total Internal Reflection (TIR).
    - Prisms & refractive polygon tracing with angle of deviation $\delta$ and dispersion.
- **Domain-Aware Diagram Routing**:
  - Updated `diagramAnalyzer.js` and `server.py` to prevent domain cross-talk: kinematics/Newton diagrams consistently route to mechanics solvers without defaulting to optics lenses.

---

## 4. Architecture & Pipeline Breakdown

```mermaid
flowchart TD
    A[Input Image / Diagram] --> B[SAM 2 Image Encoder]
    B --> C[Image Embeddings in VRAM]
    D[User / AI Prompt Points & Labels] --> E[SAM 2 Mask Decoder]
    C --> E
    E --> F[Candidate Masks + Raw Scores]
    F --> G[Mask Quality Evaluator mask_quality.py]
    G --> H[Human Confirmation / Refinement UI]
    H --> I[Accepted Mask]
    I --> J[Geometry Extractor geometry_utils.py]
    I --> K[Sprite Extractor sprite_utils.py]
    J --> L[Scene Builder scene_builder.py]
    K --> L
    L --> M[physics_scene_full.json Canonical v2]
    L --> N[physics_scene.json Multi-Domain Compat]
    N --> O[SceneRouter / DiagramAnalyzer]
    O -->|Mechanics: Rigid/Ramp/Spring| P1[Matter.js + SI Unit Adapter]
    O -->|Mechanics: Pendulum| P2[Analytical RK4 Solver 240Hz]
    O -->|Mechanics: Projectile| P3[Closed-Form Kinematics]
    O -->|Optics: Lens/Mirror/Prism| P4[Optics2D Ray Tracer]
    P1 & P2 & P3 & P4 --> Q[OverlayStage + CoordinateMapper]
    Q --> R[Layer 1: Diagram Image | Layer 2: Transparent Precision Canvas]
```

### Perception vs Physics Separation (Critical Rule)
The canonical `physics_scene_full.json` strictly records **what is visually perceived or confirmed by the author**:
- Geometry (centroids, vertices, radii, angles) in source pixels
- Masks and coordinates
- Author role (`dynamic`, `static`, `unknown`)
- Semantic labels and sprite dimensions

It **never** invents physical facts:
- `mass_kg`: `null` (unless explicitly provided by text/OCR)
- `initial_velocity`: `null`
- `friction`, `restitution`: `null`
- `gravity`: `null`

Defaults (like `mass_kg = 1.0` or `gravity = 9.81 m/s²`) are translated only at runtime via `MatterUnitAdapter`.

---

## 5. Frontend Architecture & Codebase Structure

```
simulation_frontend/augmented_physics_v2/
├── package.json               # vite, matter-js, p5, poly-decomp
├── index.html                 # Embedded stage + domain switcher + telemetry HUDs
├── public/
│   ├── scenes/
│   │   ├── kinematics/        # physics_scene.json, with_spring.png, sprites/
│   │   └── optics/            # thin_lens_scene.json, mirror_scene.json, prism_scene.json
│   └── physics_scene.json     # Root compatibility scene
├── src/
│   ├── main.js                # App entrypoint, scene loading, domain bootstrap
│   ├── core/
│   │   ├── coordinateMapper.js# Sub-pixel source-to-viewport coordinate mapping
│   │   ├── diagramAnalyzer.js # In-browser & FastAPI CV scene classification
│   │   ├── matterUnitAdapter.js# SI units (m/s², m/s, kg) to Matter.js scale translation
│   │   ├── overlayStage.js    # 2-layer stage management with transparent overlay
│   │   ├── sceneLoader.js     # JSON scene fetcher with cache-busting
│   │   └── sceneRouter.js     # Routes scenes to mechanics or optics controllers
│   ├── mechanics/
│   │   ├── mechanicsController.js # Engine lifecycle, UI bindings, AbortController
│   │   ├── physicsBodyFactory.js  # Matter.js bodies, polygon sub-pixel bounds alignment, springs
│   │   ├── pendulumSimulation.js  # High-order RK4 numerical integrator with energy conservation
│   │   ├── projectileSimulation.js# Closed-form kinematics with flight analytics
│   │   └── simulation.js          # Matter.js contact physics, runner & piston spring constraints
│   ├── optics/
│   │   ├── opticsController.js    # Optics UI bindings, preset loaders
│   │   ├── opticsSimulation.js    # P5.js ray tracing canvas renderer
│   │   ├── opticalBench.js        # Optical axis and bench state
│   │   ├── lensEquation.js        # Analytical Gaussian lens equations
│   │   ├── rayTracer.js           # Snell ray refraction & reflection engine
│   │   ├── elements/              # ThinLens, ThickLens, SphericalMirror, Prism, Slab
│   │   └── scenes/                # Optics preset configurations
│   └── style.css                  # Dark-mode glassmorphic interface styles
└── test/
    ├── test_coordinateMapper.js   # Letterbox & round-trip numerical tests
    ├── test_pendulum_physics.js   # Period verification & energy conservation tests
    ├── test_optics_engines.js     # 70 automated physics tests across lenses, mirrors & prisms
    └── test_browser_automation.js # Puppeteer end-to-end browser verification
```

---

## 6. Project Roadmap Ladder

```mermaid
graph LR
    P0[Phase 0: Env & SAM 2 Setup ✅] --> P1[Phase 1: Robust CV Scene Builder ✅]
    P1 --> P2[Phase 2: Verified Matter.js Integration ✅]
    P2 --> P3[Phase 3: Sprites & Embedded Diagram Stage ✅]
    P3 --> P4[Phase 4: Multi-Domain Precision Engines ✅]
    P4 --> P5[Phase 5: Automated Diagram Extraction & Inpainting ✅]
    P5 --> P6[Phase 6: NCTB Full Page & Bangla AI Tutor 🔄]
```

- **Phase 4 (Completed)**: Sub-pixel CoordinateMapper, analytical RK4 pendulum simulation, closed-form projectile solver, complete Optics2D ray tracer (lenses, spherical mirrors, prisms, TIR), and Matter.js concave polygon boundary alignment.
- **Phase 5 (Completed)**: Background inpainting for static diagrams, sub-pixel bob and string detection via PCA & TLS, and domain-aware diagram analyzer.
- **Phase 6 (Active Target - NCTB Full Page & Bangla Pedagogical Tutor)**:
  - Multimodal OCR/VLM pipeline (Gemini / GPT-4V) for automated diagram and problem prompt parameter extraction.
  - Multi-diagram full-page PDF layout parsing.
  - Intelligent pedagogical tutor speaking conversational Bengali grounded in live simulation state and textbook theory.
