# Repository Map (1-Minute Developer Guide)

Quickly locate any subsystem, solver, or feature in the repository.

---

## Where do I find...

### 🌐 Frontend & User Interface
| Goal | Path |
| :--- | :--- |
| Main web app entrypoint | `apps/web/src/main.js` |
| Web page HTML stage shell | `apps/web/index.html` |
| Global styles, glassmorphic dark theme | `apps/web/src/style.css` |
| Simulation overlay stage & canvas | `apps/web/src/features/simulations/` |
| Mechanics controls & presets | `apps/web/src/features/simulations/mechanics/` |
| Optics controls, HUD, P5 view | `apps/web/src/features/simulations/optics/` |
| Circuit controls, telemetry table, P5 view | `apps/web/src/features/simulations/circuits/` |
| Future student features (book, tutor, exams) | `apps/web/src/features/<feature>/` |
| Web build configuration | `apps/web/vite.config.js` |

### ⚙️ Physics Solvers & Runtime
| Goal | Path |
| :--- | :--- |
| CoordinateMapper (contain transform) | `engine/core/coordinateMapper.js` |
| Scene loader & router | `engine/core/sceneLoader.js`, `engine/core/sceneRouter.js` |
| Unit adapter (SI to Matter.js) | `engine/core/matterUnitAdapter.js` |
| SI parameter engine (Python) | `engine/core/parameter_resolver.py` |
| Parameter provenance tracker | `engine/core/provenance.py` |
| Pendulum RK4 solver (240 Hz) | `engine/mechanics/pendulumSimulation.js` |
| Projectile kinematics equations | `engine/mechanics/projectileSimulation.js` |
| Matter.js bodies & spring dynamics | `engine/mechanics/physicsBodyFactory.js` |
| Thin lens formula solver ($1/f = 1/u + 1/v$) | `engine/optics/thinLensEngine.js` |
| Spherical & plane mirror solver | `engine/optics/mirrorEngine.js` |
| Prism refraction & deviation ($\delta$) | `engine/optics/prismEngine.js` |
| Snell interface refraction & TIR | `engine/optics/snellInterfaceEngine.js` |
| Ray vector geometry & intersections | `engine/optics/rayGeometry.js` |
| Browser MNA matrix solver | `engine/circuits/CircuitSolver.js` |
| Python MNA matrix solver | `engine/circuits/mna_solver.py` |
| Circuit graph compiler | `engine/circuits/CircuitCompiler.js` |
| Disjoint-set union-find & topology | `engine/circuits/topology/` |

### 🤖 AI, Perception & Document Intelligence
| Goal | Path |
| :--- | :--- |
| FastAPI diagram analysis endpoints | `apps/api/main.py` |
| Circuit CV component/wire detectors | `ai/perception/circuits/` |
| Optics geometry extraction (lens, prism, axis) | `ai/perception/optics/` |
| Kinematics geometry extraction | `ai/perception/kinematics/` |
| SAM 2 mask scoring & polygon utils | `ai/perception/core/` |
| Transparent RGBA sprite cutouts | `ai/perception/core/sprite_utils.py` |
| Circuit OCR & value parser | `ai/document_intelligence/` |
| Canonical scene JSON builders | `ai/scene_compiler/` |

### 📦 Schemas, Content & Storage
| Goal | Path |
| :--- | :--- |
| Canonical `physics_scene.json` schema | `shared/schemas/physics_scene.json` |
| Canonical `physics_scene_full.json` contract | `shared/schemas/physics_scene_full.json` |
| Circuit scene dataclass models | `shared/schemas/circuit_models.py` |
| Demonstration textbook assets | `content/demo-books/bangla-physics/` |
| Runtime uploads directory | `storage/uploads/` |

### 🧪 Tests & Tooling
| Goal | Path |
| :--- | :--- |
| Unit tests (Optics, Circuits, Kinematics) | `tests/unit/` |
| Integration tests (Circuit images, precision) | `tests/integration/` |
| Simulation tests & browser automation | `tests/simulations/` |
| Test images and reference fixtures | `tests/fixtures/` |
| Interactive GUI authoring tools | `scripts/` |
