# Migration Path Map (OLD PATH -> NEW PATH)

This document tracks all relocations executed during the repository architecture migration (`refactor/repository-architecture-v2`).

---

## 1. Web Applications & Legacy

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `simulation_frontend/augmented_physics_v2/` | `apps/web/` | Canonical active frontend |
| `simulation_frontend/physics simulation/` | `legacy/frontend-v1/` | Historical prototype v1 preserved |

## 2. Backend & Services

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `backend/server.py` | `apps/api/main.py` | FastAPI application bootstrap |

## 3. Physics Engines (`engine/`)

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `simulation_frontend/augmented_physics_v2/src/optics/engines/thinLensEngine.js` | `engine/optics/thinLensEngine.js` | Thin lens formula |
| `simulation_frontend/augmented_physics_v2/src/optics/engines/mirrorEngine.js` | `engine/optics/mirrorEngine.js` | Spherical & plane mirror |
| `simulation_frontend/augmented_physics_v2/src/optics/engines/prismEngine.js` | `engine/optics/prismEngine.js` | Prism refraction & deviation |
| `simulation_frontend/augmented_physics_v2/src/optics/engines/snellInterfaceEngine.js` | `engine/optics/snellInterfaceEngine.js` | Interface refraction & TIR |
| `simulation_frontend/augmented_physics_v2/src/optics/engines/rayGeometry.js` | `engine/optics/rayGeometry.js` | Ray vector math |
| `backend/optics/optics_registry.py` | `engine/optics/optics_registry.py` | Optics presets |
| `simulation_frontend/augmented_physics_v2/src/circuits/CircuitSolver.js` | `engine/circuits/CircuitSolver.js` | Browser MNA matrix solver |
| `simulation_frontend/augmented_physics_v2/src/circuits/CircuitCompiler.js` | `engine/circuits/CircuitCompiler.js` | Circuit compiler & indexer |
| `simulation_frontend/augmented_physics_v2/src/circuits/LinearSystem.js` | `engine/circuits/LinearSystem.js` | Gaussian / LU matrix solver |
| `simulation_frontend/augmented_physics_v2/src/circuits/EquationGenerator.js` | `engine/circuits/EquationGenerator.js` | Circuit step derivation |
| `backend/circuits/solver/mna_solver.py` | `engine/circuits/mna_solver.py` | Python MNA solver |
| `backend/circuits/solver/transient_solver.py` | `engine/circuits/transient_solver.py` | Python RC transient solver |
| `backend/circuits/solver/equation_generator.py` | `engine/circuits/equation_generator.py` | Python equation generator |
| `backend/circuits/solver/spice_adapter.py` | `engine/circuits/spice_adapter.py` | SPICE netlist adapter |
| `backend/circuits/circuit_registry.py` | `engine/circuits/circuit_registry.py` | Circuit component registry |
| `backend/circuits/topology/` | `engine/circuits/topology/` | Union-find & topology builder |
| `simulation_frontend/augmented_physics_v2/src/mechanics/pendulumSimulation.js` | `engine/mechanics/pendulumSimulation.js` | 240Hz nonlinear RK4 pendulum |
| `simulation_frontend/augmented_physics_v2/src/mechanics/projectileSimulation.js` | `engine/mechanics/projectileSimulation.js` | Closed-form kinematics |
| `simulation_frontend/augmented_physics_v2/src/mechanics/physicsBodyFactory.js` | `engine/mechanics/physicsBodyFactory.js` | Matter.js factory & springs |
| `simulation_frontend/augmented_physics_v2/src/mechanics/simulation.js` | `engine/mechanics/simulation.js` | Mechanics runner |
| `simulation_frontend/augmented_physics_v2/src/core/coordinateMapper.js` | `engine/core/coordinateMapper.js` | Contain coordinate mapper |
| `simulation_frontend/augmented_physics_v2/src/core/matterUnitAdapter.js` | `engine/core/matterUnitAdapter.js` | SI to Matter.js units |
| `simulation_frontend/augmented_physics_v2/src/core/sceneLoader.js` | `engine/core/sceneLoader.js` | Scene JSON loader |
| `simulation_frontend/augmented_physics_v2/src/core/sceneRouter.js` | `engine/core/sceneRouter.js` | Domain scene router |
| `backend/core/coordinate_space.py` | `engine/core/coordinate_space.py` | Coordinate space definitions |
| `backend/core/parameter_resolver.py` | `engine/core/parameter_resolver.py` | SI parameter engine |
| `backend/core/provenance.py` | `engine/core/provenance.py` | Provenance engine |

## 4. AI & Perception (`ai/`)

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `backend/circuits/perception/` | `ai/perception/circuits/` | Circuit CV detectors |
| `backend/circuits/circuit_analyzer.py` | `ai/perception/circuits/circuit_analyzer.py` | End-to-end circuit analyzer |
| `backend/optics/optics_geometry.py` | `ai/perception/optics/optics_geometry.py` | Optics geometry extraction |
| `backend/kinematics/pendulum_geometry.py` | `ai/perception/kinematics/pendulum_geometry.py` | Pendulum geometry extraction |
| `backend/core/geometry_utils.py` | `ai/perception/core/geometry_utils.py` | Contour & polygon utilities |
| `backend/core/mask_quality.py` | `ai/perception/core/mask_quality.py` | SAM 2 mask scoring |
| `backend/core/sprite_utils.py` | `ai/perception/core/sprite_utils.py` | Transparent sprite generator |
| `backend/circuits/parameters/circuit_ocr.py` | `ai/document_intelligence/ocr/circuit_ocr.py` | Circuit text OCR |
| `backend/circuits/parameters/value_parser.py` | `ai/document_intelligence/parsing/value_parser.py` | Circuit value parser |
| `backend/circuits/parameters/parameter_binder.py` | `ai/document_intelligence/parsing/parameter_binder.py` | Parameter binder |
| `backend/optics/optics_text.py` | `ai/document_intelligence/parsing/optics_text.py` | Focal length & axis inference |
| `backend/optics/optics_semantics.py` | `ai/document_intelligence/parsing/optics_semantics.py` | Semantic binding & prompts |
| `backend/circuits/scene/circuit_scene_builder.py` | `ai/scene_compiler/circuit_scene_builder.py` | Circuit scene compiler |
| `backend/optics/optics_scene_builder.py` | `ai/scene_compiler/optics_scene_builder.py` | Optics scene compiler |
| `backend/core/scene_builder.py` | `ai/scene_compiler/scene_builder.py` | Canonical scene compiler |

## 5. Shared Contracts (`shared/`)

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `physics_scene.json` (root) | `shared/schemas/physics_scene.json` | Simulator compatibility schema |
| `physics_scene_full.json` (root) | `shared/schemas/physics_scene_full.json` | Visual perception contract |
| `backend/circuits/models.py` | `shared/schemas/circuit_models.py` | Dataclass circuit models |

## 6. Tests (`tests/`)

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `simulation_frontend/augmented_physics_v2/test/test_optics_engines.js` | `tests/unit/test_optics_engines.js` | Optics unit test |
| `simulation_frontend/augmented_physics_v2/test/test_circuit_solver.js` | `tests/unit/test_circuit_solver.js` | Circuit solver unit test |
| `simulation_frontend/augmented_physics_v2/test/test_coordinate_mapper.js` | `tests/unit/test_coordinate_mapper.js` | CoordinateMapper unit test |
| `simulation_frontend/augmented_physics_v2/test/test_coordinateMapper.js` | `tests/unit/test_coordinateMapper_legacy.js` | Legacy mapper test |
| `simulation_frontend/augmented_physics_v2/test/test_pendulum_physics.js` | `tests/unit/test_pendulum_physics.js` | Pendulum unit test |
| `backend/circuits/tests/test_mna.py` | `tests/unit/test_mna.py` | Python MNA unit test |
| `backend/circuits/tests/test_topology.py` | `tests/unit/test_topology.py` | Python topology unit test |
| `backend/circuits/tests/test_value_parser.py` | `tests/unit/test_value_parser.py` | Python value parser test |
| `backend/tests/test_pendulum_geometry.py` | `tests/unit/test_pendulum_geometry.py` | Python pendulum geometry |
| `backend/circuits/tests/test_circuit_images.py` | `tests/integration/test_circuit_images.py` | Circuit image perception |
| `backend/test_optics_precision.py` | `tests/integration/test_optics_precision.py` | Optics precision test |
| `backend/kinematics/verify_multiple_objects.py` | `tests/integration/verify_multiple_objects.py` | Multi-object verification |
| `simulation_frontend/augmented_physics_v2/test/test_browser_automation.js` | `tests/simulations/test_browser_automation.js` | Browser automation |
| `simulation_frontend/augmented_physics_v2/test/verify_mechanics_scenes.js` | `tests/simulations/verify_mechanics_scenes.js` | Headless mechanics test |
| `simulation_frontend/augmented_physics_v2/test/fast_verify_all.js` | `tests/simulations/fast_verify_all.js` | All-domains fast verify |
| `images/` | `tests/fixtures/images/` | Benchmark test diagrams |

## 7. Developer Scripts (`scripts/`)

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `backend/optics/optics_authoring.py` | `scripts/optics_authoring.py` | Optics GUI authoring tool |
| `backend/optics/build_optics_scene.py` | `scripts/build_optics_scene.py` | Optics scene generator GUI |
| `backend/optics/run_optics_pipeline.py` | `scripts/run_optics_pipeline.py` | Pipeline CLI runner |
| `backend/kinematics/build_kinematics_scene.py` | `scripts/build_kinematics_scene.py` | Kinematics authoring GUI |

## 8. Research & Storage

| Old Path | New Path | Status / Notes |
| :--- | :--- | :--- |
| `experiments/` | `research/experiments/` | Exploratory prototypes |
| `backend/kinematics/test_sam.py` | `research/experiments/test_sam.py` | SAM single-object experiment |
| `uploads/` | `storage/uploads/` | User runtime uploads |
