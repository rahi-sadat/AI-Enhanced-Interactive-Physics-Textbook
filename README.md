# AI-Enhanced Interactive NCTB Physics Textbook (AugmentedPhysics)

Transform static NCTB physics textbook diagrams into embedded, interactive 2D simulations using Meta SAM 2, automated geometry extraction, and Matter.js.

Based on the research paradigm:  
> *"Augmented Physics: Creating Interactive and Embedded Physics Simulations from Static Textbook Diagrams"* (UIST '24) — Gunturu et al.

---

## 🏗 System Architecture

```
[NCTB Textbook Page / Diagram]
             │
             ▼
[Multimodal Perception: SAM 2 + Geometry Extraction]
 (Interactive point prompting, candidate mask re-ranking, RGBA sprite cutouts)
             │
             ▼
[Canonical PhysicsScene v2 (JSON)]
 (Domain-neutral, preserves uncertainty, separates perception from physics)
             │
             ▼
[Scene Compiler & Adapters]
 (Matter.js 2D Rigid-body / Spring Constraints / Concave Poly-Decomposition)
             │
             ▼
[Embedded Simulation Stage (HTML/CSS Canvas)]
 (Layer 1: Original Diagram  |  Layer 2: Transparent Matter.js Canvas)
```

---

## 📁 Repository Structure

```
AugmentedPhysics/
├── .gitignore                   # Ignore .venv, checkpoints, node_modules, zip archives
├── README.md                    # Project overview and setup instructions
├── PROJECT_CONTEXT.md           # Deep architectural knowledge base & roadmap
├── requirements.txt             # Python backend dependencies
│
├── backend/                     # Python Backend & CV Perception Engines
│   ├── core/                    # Shared CV & Scene utilities
│   │   ├── geometry_utils.py    # Polygon hull, OBB, circles, center of mass
│   │   ├── mask_quality.py      # Multi-candidate SAM 2 mask re-ranking logic
│   │   ├── scene_builder.py     # Viewport coordinate mapper & JSON schema builder
│   │   └── sprite_utils.py      # Transparent RGBA sprite cutout generation
│   │
│   ├── kinematics/              # Rigid-body mechanics pipeline
│   │   ├── build_kinematics_scene.py  # Interactive GUI authoring for Matter.js scenes
│   │   ├── test_sam.py          # Single-object segmentation test
│   │   └── verify_multiple_objects.py # Multi-object verification script
│   │
│   └── optics/                  # Domain-specific optics pipeline
│       ├── build_optics_scene.py      # Interactive GUI authoring for Optics2D scenes
│       ├── optics_authoring.py  # Optics GUI session with F/2F annotation mode
│       ├── optics_geometry.py   # Lens center, aperture, arrow tip/base, prism, axis
│       ├── optics_registry.py   # Semantic presets (lens, object, prism, mirror)
│       ├── optics_scene_builder.py    # Canonical PhysicsScene v2.1 builder
│       ├── optics_semantics.py  # Rule-based semantic binding & VLM prompt generation
│       └── optics_text.py       # F/2F classification & pixel-to-cm calibration
│
├── images/                      # Benchmark textbook diagrams & test images
│   ├── curved_ramp_spring.png   # Curved ramp with spring reference
│   ├── multi_balls_test.jpg     # Multi-ball segmentation test
│   └── test.jpg                 # Single-object benchmark
│
├── physics_scene_full.json      # Canonical v2 schema (visual perception contract)
├── physics_scene.json           # Simulator compatibility schema
│
└── simulation_frontend/         # Interactive Matter.js & Optics Web Simulation
    └── physics simulation/
        ├── index.html           # 2-Layer embedded textbook stage
        ├── package.json
        ├── public/              # Sprites, scene spec & background
        └── src/
            ├── main.js          # App lifecycle & dynamic object selector
            ├── physicsBodyFactory.js  # Matter.js body creation & spring dynamics
            ├── sceneLoader.js   # JSON scene loader
            ├── simulation.js    # Simulation runner & transparent canvas loop
            └── style.css        # Embedded stage styling
```

---

## 🚀 Quick Start & Installation

### 1. Backend & Perception Pipeline Setup

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

# Install Meta SAM 2
pip install -e git+https://github.com/facebookresearch/segment-anything-2.git
```

### 2. Download SAM 2 Model Checkpoint

The pre-trained weights (`sam2.1_hiera_tiny.pt`) should be placed in `checkpoints/`:

```bash
mkdir checkpoints
# Download sam2.1_hiera_tiny.pt (approx. 156 MB)
curl -L -o checkpoints/sam2.1_hiera_tiny.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt
```

### 3. Run the Interactive Authoring GUIs

**For Mechanics / Kinematics (Matter.js):**
```bash
python backend/kinematics/build_kinematics_scene.py images/with_spring.png
```

**For Optics (Thin Lens / Prism / Mirror):**
```bash
python backend/optics/build_optics_scene.py --image images/with_spring.png --subtype thin_lens
```

- **Left-Click**: Add positive prompt point (object).
- **Right-Click**: Add negative prompt point (background).
- **Press D / S**: Mark selected entity as **Dynamic** or **Static**.
- **Press F (in Optics)**: Toggle F / 2F annotation mode to place focal markers on the axis.
- **Press Enter**: Accept candidate mask & extract geometry + RGBA sprite.
- **Click '▶ SIMULATE'**: Automatically syncs assets to the frontend and launches the simulation.

### 4. Frontend Simulation Setup

```bash
cd "simulation_frontend/physics simulation"
npm install
npm run dev
```

Open the local server URL (e.g., `http://localhost:5173`) in your browser to interact with the simulation.

---

## 📜 Canonical Visual Schema

Perception and physics are strictly separated:
- `physics_scene_full.json` strictly preserves what is visually perceived or confirmed by the author (geometry, contours, bounds, centroids, author roles). It does **not** invent physical constants (e.g. mass, friction, gravity remain `null` until confirmed by text/OCR).
- `physics_scene.json` is generated for simulator engines (Matter.js), with sensible fallbacks and explicit provenance flags.

---

## 👥 Contributors & Milestones
- **Backend & CV Pipeline**: SAM 2 segmentation, candidate mask re-ranking, geometry extraction, transparent sprite generation, canonical schema exporter.
- **Simulation Frontend**: Matter.js embedded transparent canvas, concave polygon decomposition (`poly-decomp`), spring dynamics, and controls.