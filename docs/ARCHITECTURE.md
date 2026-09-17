# System Architecture & Layer Boundaries

The **AugmentedPhysics** platform transforms static physics textbook pages into embedded, interactive, and grounded learning experiences.

The repository is organized into strict architectural layers to prevent code collisions, support independent development across multiple contributors, and allow product features to evolve without destabilizing the physics runtime.

---

## 1. High-Level Dependency Graph

```
                   ┌───────────────────────────────┐
                   │          apps/web             │
                   │ (UI, Features, Stage, Studio) │
                   └───────┬───────────────┬───────┘
                           │               │
                           ▼               │
                   ┌───────────────┐       │
                   │   apps/api    │       │
                   │ (FastAPI App) │       │
                   └───────┬───────┘       │
                           │               │
           ┌───────────────┴───────────────┼───────────────┐
           ▼                               ▼               ▼
┌─────────────────────┐         ┌─────────────────────┐   │
│       engine/       │         │         ai/         │   │
│ - core              │         │ - document_intel    │   │
│ - mechanics         │         │ - perception        │   │
│ - optics            │         │ - scene_compiler    │   │
│ - circuits          │         │ - tutor             │   │
└──────────┬──────────┘         └──────────┬──────────┘   │
           │                               │              │
           └───────────────┬───────────────┘              │
                           ▼                              │
                ┌─────────────────────┐                   │
                │       shared/       │◄──────────────────┘
                │ - schemas           │
                │ - constants         │
                │ - types             │
                └─────────────────────┘
```

### Dependency Rules:
1. **Unidirectional flow**: Applications (`apps/`) depend on `engine/`, `ai/`, and `shared/`.
2. **Engine independence**: `engine/` never imports from `apps/` or `ai/`. Solvers depend only on `shared/` contracts and standard math/physics libraries.
3. **Domain isolation**: `engine/mechanics/`, `engine/optics/`, and `engine/circuits/` are strictly independent from each other. They communicate with applications through `engine/core/`.
4. **No circular imports**: Modules within a layer must not circularly depend on each other.

---

## 2. Directory Responsibilities

### `apps/` — User-Facing Applications
Code in `apps/` bootstraps and runs applications that end users interact with.

- **`apps/web/`**: The canonical browser frontend (Vite + Vanilla JS). Contains:
  - `src/app/`: Application shell, routing, global providers, and layouts.
  - `src/features/`: Feature-driven product modules:
    - `simulations/`: Stage controller, diagram overlay, and HUDs for Mechanics, Optics, and Circuits.
    - `book/`: [Future] Interactive textbook reader, page navigator, and chapter viewer.
    - `tutor/`: [Future] AI Tutor chat interface and voice explanation panel.
    - `exams/`: [Future] Mock exam and formal assessment engine.
    - `quizzes/`: [Future] In-chapter quick checks.
    - `study-plan/`: [Future] Personalized revision schedules.
    - `progress/`: [Future] Learning mastery and analytics tracking.
    - `notes/`: [Future] Student notebook and diagram annotations.
    - `routine/`: [Future] Timetable and class routine planner.
    - `teacher/`: [Future] Teacher assignment and evaluation dashboard.
  - `src/shared/`: Shared UI widgets, badges, sliders, and utilities.
  - `public/`: Static diagram assets, sprites, and scenario JSONs.
- **`apps/api/`**: The canonical backend HTTP service (FastAPI + Uvicorn). Exposes `/api/health`, `/api/upload-diagram`, and `/api/analyze-diagram`.

### `engine/` — Physics Runtimes & Solvers
Contains the mathematical physics engines. Does not contain UI widgets, HTML, or API routes.

- **`engine/core/`**: Common runtime infrastructure:
  - `coordinateMapper.js`: Bidirectional `object-fit: contain` transform between native source diagram pixels and viewport CSS pixels.
  - `matterUnitAdapter.js`: Translates SI physical units (m, m/s, kg) to Matter.js simulation frames.
  - `parameter_resolver.py`: Case-sensitive SI engineering unit parser.
  - `provenance.py`: Parameter provenance tracker.
  - `sceneLoader.js`: Validated JSON scene loader.
  - `sceneRouter.js`: Routes a scene's domain to the correct physics controller.
- **`engine/mechanics/`**:
  - `pendulumSimulation.js`: High-precision 240 Hz nonlinear RK4 pendulum integrator.
  - `projectileSimulation.js`: Closed-form analytical projectile kinematics.
  - `physicsBodyFactory.js`: Matter.js rigid-body creation, concave polygon decomposition, and spring constraints.
  - `simulation.js`: Mechanics simulation runner.
- **`engine/optics/`**:
  - `thinLensEngine.js`: Thin lens formula ($1/f = 1/u + 1/v$) with real/virtual ray traces.
  - `mirrorEngine.js`: Spherical (concave/convex) and plane mirror solver.
  - `prismEngine.js`: Triangular prism and rectangular slab Snell refraction, deviation ($\delta$), and TIR.
  - `snellInterfaceEngine.js`: Snell's law interface refractor and critical angle ($\theta_c$) solver.
  - `rayGeometry.js`: 2D vector geometry, intersection, reflection, and refraction primitives.
- **`engine/circuits/`**:
  - `CircuitSolver.js`: Browser-side Modified Nodal Analysis (MNA) linear matrix solver.
  - `CircuitCompiler.js`: Circuit graph compiler, node indexer, and component binder.
  - `LinearSystem.js`: Gaussian elimination / LU matrix solver.
  - `EquationGenerator.js`: Step-by-step derivation generator.
  - `mna_solver.py`: Python authoritative MNA linear matrix solver.
  - `transient_solver.py`: Analytical RC transient charging/discharging solver.
  - `spice_adapter.py`: SPICE netlist export and sandbox validation.
  - `topology/`: Disjoint-set union (Union-Find) node clustering and wire graph connectivity.

### `ai/` — Artificial Intelligence & Perception
Contains multimodal perception, computer vision, document intelligence, and pedagogical reasoning.

- **`ai/perception/`**:
  - `circuits/`: Component, junction, terminal, wire, polarity, and region detectors.
  - `optics/`: Optical axis, lens, arrow, prism, and mirror geometry extractors.
  - `kinematics/`: Simple pendulum and multi-object ball geometry extractors.
  - `core/`: SAM 2 mask scoring, polygon approximation, and transparent RGBA sprite cutout generation.
- **`ai/document_intelligence/`**:
  - `ocr/`: Circuit text OCR.
  - `parsing/`: Case-sensitive value parsers, parameter binders, and focal length inference.
  - `[Future boundaries]`: Ingestion (PDF/image/DOCX), layout analysis, and caption association.
- **`ai/scene_compiler/`**:
  - Compiles perception and extracted parameters into canonical `PhysicsScene` JSON contracts.
- **`ai/tutor/`**:
  - Context grounding, curriculum alignment, and explanation synthesis.

### `shared/` — Canonical Schemas & Contracts
- **`shared/schemas/`**: Canonical schemas defining the boundary between perception and simulation:
  - `physics_scene.json`: Multi-domain simulator compatibility schema.
  - `physics_scene_full.json`: Canonical visual perception contract.
  - `circuit_models.py`: Strongly-typed dataclass schemas for electrical networks.

### `content/` — Educational Content
- **`content/demo-books/bangla-physics/`**: Controlled demonstration textbook materials (NCTB curriculum). Generic solvers must never assume this is the only book in existence.

### `storage/` — Runtime Storage
- `storage/uploads/`: User-uploaded diagram images (git-ignored, except reference fixtures).
- `storage/generated/`: Temporary simulation outputs and debug plots (git-ignored).
- `storage/cache/`: Model embeddings and runtime caches (git-ignored).

### `research/` — Research & Evaluation
- `research/experiments/`: Exploratory prototypes and early experimental scripts.
- `research/benchmarks/`: Benchmark evaluation scripts and datasets.

### `tests/` — Automated Testing
- `tests/unit/`: Fast, isolated mathematical and solver unit tests.
- `tests/integration/`: End-to-end perception and solver validation pipelines.
- `tests/simulations/`: Headless browser simulation runners.
- `tests/fixtures/`: Fixed test diagram images and golden benchmark files.

### `legacy/` — Preserved Historical Code
- `legacy/frontend-v1/`: Preserved initial prototype ("physics simulation") kept for historical reference without running as a competing active frontend.
