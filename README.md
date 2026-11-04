# AI-Enhanced Interactive NCTB Physics Textbook (AugmentedPhysics)

Transform static NCTB physics textbook diagrams into embedded, interactive 2D simulations using Meta SAM 2, automated geometry extraction, Modified Nodal Analysis (MNA), and ray-tracing/rigid-body simulation engines.

Based on the research paradigm:  
> *"Augmented Physics: Creating Interactive and Embedded Physics Simulations from Static Textbook Diagrams"* (UIST '24) — Gunturu et al.

---

## 🏗 System Architecture

```
[NCTB Textbook Page / Diagram]
             │
             ▼
[ai/ Multimodal Perception: SAM 2 + CV Detectors + Document Intelligence]
 (Interactive point prompting, candidate mask re-ranking, OCR, parameter binding)
             │
             ▼
[shared/ Canonical Schemas (JSON)]
 (PhysicsScene v2.1 & Canonical CircuitScene v3: separates perception from simulation)
             │
             ▼
[engine/ Multi-Domain Physics Solvers]
 (MNA Electrical Solver / Optics Ray-Tracing / Mechanics Rigid-Body Dynamics)
             │
             ▼
[apps/web/ Interactive Simulation Platform]
 (Embedded stage, dynamic HUDs, real-time telemetry, Bangla AI tutor overlay)
```

---

## 📁 Repository Structure

```
AI-Enhanced-Interactive-Physics-Textbook/
├── .github/                     # CODEOWNERS and PR templates
├── apps/
│   ├── api/                     # FastAPI backend (POST /api/analyze-diagram, /api/upload-diagram)
│   └── web/                     # Modern Vite simulation frontend (multi-domain stages & telemetry)
├── engine/                      # Pure, framework-agnostic physics solvers
│   ├── circuits/                # Modified Nodal Analysis (MNA), SPICE adapter, equation generator
│   ├── core/                    # Coordinate spaces, parameter resolution, provenance tracking
│   ├── mechanics/               # Rigid-body, spring dynamics, and collision helpers
│   └── optics/                  # Optical ray-tracing, lenses, mirrors, and prisms
├── ai/                          # Perception and document understanding
│   ├── document_intelligence/   # OCR heuristics and physics value parser
│   ├── perception/              # CV detectors for circuits, optics, kinematics, and SAM 2
│   └── scene_compiler/          # Compiles perceived elements into canonical scene models
├── shared/                      # Canonical JSON schemas and shared dataclass models
│   └── schemas/                 # CircuitScene v3, PhysicsScene v2.1, and contracts
├── storage/                     # Diagram uploads, generated sprites, and cache (git-ignored)
│   └── uploads/                 # Canonical diagram upload directory
├── tests/                       # Automated multi-domain test suites
│   ├── fixtures/                # Benchmark diagrams, scenes, and test images
│   ├── integration/             # End-to-end perception and solver tests
│   └── unit/                    # Fast isolated mathematical and physical unit tests
├── scripts/                     # Standalone CLI tools & interactive authoring GUIs
├── docs/                        # Complete architectural and collaborative documentation
│   ├── ARCHITECTURE.md          # Architectural layers, contracts, and design principles
│   ├── REPO_MAP.md              # File-by-file inventory and location map
│   ├── MIGRATION_MAP.md         # Before-and-after path mapping
│   ├── TEAM_WORKFLOW.md         # Developer collaboration guidelines (@rahi-sadat & @THE-FOOL-T)
│   └── CONTRIBUTING.md          # PR standards, testing requirements, and ownership
└── legacy/                      # Archived early prototypes (frontend-v1)
```

---

## 🚀 Quick Start & Installation

For the matched Windows/Python environment and new circuit dataset/YOLO tools,
use [the reproducible setup guide](docs/WINDOWS_REPRODUCIBLE_SETUP.md).
[This Codex prompt](docs/CODEX_FRIEND_SETUP_PROMPT.md) performs the setup on a
collaborator's laptop. The [circuit model handoff](docs/TEAM_HANDOFF_20261031.md)
lists the detector checkpoints included in Git.

### 1. Backend & Perception Setup

```bash
# Clone the repository
git clone https://github.com/rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook.git
cd AI-Enhanced-Interactive-Physics-Textbook

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the API Server

```bash
uvicorn apps.api.main:app --reload --port 8000
```

Interactive API documentation will be available at: `http://localhost:8000/docs`.

### 3. Launch the Web Simulation Platform

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:5173` to explore interactive mechanics, circuits, and optics simulations.

### Upload a circuit image

Open the upload dialog, select a cropped circuit schematic, and click **Generate Interactive Simulation**.
The upload pipeline tries the local `circuit_v2` checkpoint (`weights/last.pt`) before
Gemini. It proposes resistor, voltage source, capacitor, and switch locations.
The existing CV and OCR stages verify geometry and recover values. A circuit
with a solvable graph starts automatically, using editable assumptions for
missing values. If playback cannot start, the upload dialog explains the issue
and lets the student retry.

When the local detector recognizes a circuit, the upload works without a Gemini
key. Images without a confident circuit detection use the existing semantic
classifier. Set `CIRCUIT_V2_ONLY=true` in the API's `.env` to keep all diagram
uploads on the local circuit path, including images the checkpoint cannot classify.

Open `/circuit-v2.html` on the web server for the **Circuit v2 experiment**.
It runs the real detector, OCR/CV grounding, resolution and compiler locally,
shows the checkpoint SHA-256 and per-stage failures, and downloads the full trace.
When compilation is blocked, the checked preview option plays an explicitly
experimental series circuit with guessed connections and editable assumed values.
Synthetic stand-ins are disclosed when no source or resistor is detected.
This preview is separate from the source evidence and never marks it verified.
`CIRCUIT_V2_CHECKPOINT` selects a different local checkpoint. The Vite API proxy
can target a separate running API via `API_PROXY_TARGET`.

---

## 🧪 Testing & Verification

### Automated Frontend Tests
```bash
cd apps/web
npm test
```
*Runs optics engine verification, coordinate mappers, pendulum physics, and circuit solvers (97+ tests).*

### Automated Python Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*Runs MNA matrix math, Union-Find circuit topology, SI prefix parsing, sub-pixel pendulum geometry, and full-pipeline diagram analysis.*

---

## 👥 Team & Ownership

This project is collaboratively developed with strict domain boundaries to prevent code collisions:
- **`@rahi-sadat`**: Backend CV perception, SAM 2 segmentation, canonical schemas, MNA electrical solver, and API integration.
- **`@THE-FOOL-T`**: Frontend simulation engines, interactive stages, telemetry overlays, UI components, and educational interactions.

For detailed branch policies, commit standards, and PR workflows, see [docs/TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
