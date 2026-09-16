# AugmentedPhysics v2 — Comprehensive Project Report & Architecture Documentation

**Repository:** [rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook](https://github.com/rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook)  
**Baseline Reference Commit:** [`5405882`](https://github.com/rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook/commit/5405882473a5156aba4f4dbeb827732bd0df8eae) *(Implemented optics scene authoring pipeline, geometry extraction, and v2.1 schema)*  
**Current Head Commit:** [`31f6d22`](https://github.com/rahi-sadat/AI-Enhanced-Interactive-Physics-Textbook/commit/31f6d22)  
**Date:** September 2026  
**Scope:** Progress report, directory architecture, key source implementations, and visual verification across **Mechanics**, **Geometric Optics**, and **Circuits**.

---

## 1. Executive Summary

AugmentedPhysics v2 transforms static National Curriculum and Textbook Board (NCTB) physics diagrams into interactive, visually grounded simulation laboratories. Rather than replacing textbook illustrations with abstract canvas drawings, the system preserves the authentic printed diagram as the base layer, superimposing a transparent 60 FPS interactive physics overlay directly over it with sub-pixel alignment.

Between commit `5405882` and current `HEAD`, the project underwent a major architectural expansion:
1. **Geometric Optics (Domain 2)**: Transitioned from static JSON authoring to a comprehensive real-time optics laboratory featuring analytical thin lenses (convex & concave), Snell's law interface refraction, critical angle/total internal reflection (TIR), triangular & right-angle prisms with angular deviation ($\delta$), spherical & plane mirrors, and an educational HUD.
2. **Mechanics & Kinematics (Domain 1)**: Integrated high-precision Runge-Kutta 4 (RK4) pendulum physics alongside Matter.js rigid-body dynamics, resolved sub-pixel ramp and spring contact geometries, and added Newton's Cradle (5-bob pendulum) restitution.
3. **Circuits Laboratory (Domain 3)**: Designed and implemented a browser-native Modified Nodal Analysis (MNA) solver on `Float64Array` (strictly avoiding Matter.js), canonical `CircuitScene v3` schema, 60 FPS conventional electron flow, anchored HTML parameter popovers, live Kirchhoff's Current Law ($\Sigma I = 0$) and Voltage Law ($\Sigma V = 0$) inspectors, an authentic diamond Wheatstone Bridge with balance detection, and a grounded bilingual AI tutor bridge.
4. **Core Infrastructure & Diagram Upload Studio**: Built the `CoordinateMapper` for uniform `contain` scaling and letterbox/pillarbox offset compensation, an AI Diagram Upload Studio with scenario presets, isolated multi-domain control panels, and removed proxy bottlenecks for static asset delivery.

---

## 2. System Architecture

The application is structured into a clean decoupled pipeline connecting backend computer vision perception to browser-native analytical solvers and transparent presentation overlays.

```mermaid
graph TD
    subgraph Perception_Pipeline [Backend Perception & Schema Ingestion]
        A["Textbook Diagram (PNG/SVG)"] --> B["FastAPI Server (/api/upload-diagram)"]
        B --> C["SAM 2 & OpenCV Segmentation"]
        B --> D["OCR Parameter Extraction"]
        C --> E["Topology & Coordinate Space Extractor"]
        D --> E
        E --> F["Canonical Scene JSON (v2.1 Optics / v3.0 Circuits)"]
    end

    subgraph Core_Engine [Frontend Core Infrastructure]
        F --> G["SceneRouter (core/sceneRouter.js)"]
        G --> H["OverlayStage (core/overlayStage.js)"]
        H --> I["CoordinateMapper (core/coordinateMapper.js)"]
        I -.->|"Source (px) <==> View (px)"| J["2-Layer Visual Viewport"]
        J --> K["Base Layer: <img id='diagram-image'>"]
        J --> L["Top Layer: <div id='simulation-container'>"]
    end

    subgraph Domain_Controllers [Domain Simulation Controllers]
        G -->|"domain: kinematics"| M["MechanicsController"]
        G -->|"domain: optics"| N["OpticsController"]
        G -->|"domain: circuits"| O["CircuitController"]
    end

    subgraph Physics_Solvers [Specialized Physics Engines]
        M --> M1["Matter.js Contact Engine + RK4 Pendulum"]
        N --> N1["Thin Lens Equation (1/f = 1/u + 1/v)"]
        N --> N2["Vector Snell's Law & TIR Engine"]
        N --> N3["Prism Ray Deviation Engine"]
        N --> N4["Spherical/Plane Mirror Engine"]
        O --> O1["LinearSystem (Float64 LU Decomposition)"]
        O --> O2["CircuitSolver (Browser MNA Matrix Solver)"]
        O --> O3["CircuitCompiler (Wire Polylines & Arc Lengths)"]
    end

    subgraph Presentation_Layer [Presentation & Interactive Instruments]
        N1 & N2 & N3 & N4 --> P["P5OpticsView (60 FPS Ray Renderer)"]
        P --> Q["OpticsHUD (Metrics, Angles, Real-Time Sliders)"]
        O1 & O2 & O3 --> R["P5CircuitView (Particles, Voltage Halos)"]
        R --> S["ComponentEditor (Anchored HTML Popovers)"]
        R --> T["ProbeManager (Voltmeter, Ammeter, KCL, KVL)"]
        R --> U["CircuitTelemetry (Bidirectional Sync Table)"]
        R --> V["CircuitTutorBridge (Grounded Bilingual AI Drawer)"]
    end
```

---

## 3. Directory Structure

Below is the repository directory tree highlighting newly developed modules, core engines, test suites, and documentation assets:

```text
AugmentedPhysics/
├── backend/                                   # Python FastAPI backend server & perception pipelines
│   ├── circuits/                              # Circuits domain computer vision & MNA modules
│   │   ├── perception/                        # Wire, terminal, junction, and component detectors
│   │   ├── topology/                          # Union-Find reduction, wire graph, and SPICE validator
│   │   ├── solver/                            # Python MNA matrix solver, equation generator
│   │   └── models.py                          # Canonical CircuitScene v3 Pydantic models
│   ├── core/                                  # Coordinate space, provenance, and parameter resolvers
│   ├── kinematics/                            # Kinematics CV and trajectory extractors
│   ├── optics/                                # Optics geometry extractors and scene builders
│   └── server.py                              # FastAPI endpoints (/api/upload-diagram, /api/analyze-diagram)
├── docs/                                      # Project documentation & visual assets
│   ├── images/                                # High-resolution verification screenshots
│   │   ├── wheatstone_bridge.png
│   │   ├── series_circuit_switch.png
│   │   ├── circuit_component_popover.png
│   │   ├── ai_tutor_drawer.png
│   │   ├── kvl_law_card.png
│   │   ├── thin_lens_simulation.png
│   │   ├── prism_simulation.png
│   │   ├── mirror_simulation.png
│   │   ├── interface_refraction.png
│   │   ├── kinematics_projectile.png
│   │   └── diagram_upload_studio.png
│   └── PROJECT_REPORT.md                      # This comprehensive report
├── simulation_frontend/
│   └── augmented_physics_v2/                  # Modern Vite/JavaScript interactive frontend
│       ├── public/                            # Static assets served at root
│       │   ├── scenes/
│       │   │   ├── circuits/                  # Authentic textbook SVGs & circuit scenario JSONs
│       │   │   │   ├── textbook_circuit_diagram.svg
│       │   │   │   ├── textbook_bridge_diagram.svg
│       │   │   │   ├── series_parallel_scene.json
│       │   │   │   ├── bridge_scene.json
│       │   │   │   └── circuit1_scene.json ... circuit4_scene.json
│       │   │   ├── kinematics/                # Kinematics scenario definitions
│       │   │   └── optics/                    # Optics scenario definitions & textbook diagrams
│       │   │       ├── nctb_lens_diagram.png
│       │   │       ├── nctb_refraction_diagram.png
│       │   │       ├── thin_lens_scene.json
│       │   │       ├── prism_scene.json
│       │   │       ├── mirror_scene.json
│       │   │       └── interface_refraction_scene.json
│       │   └── uploads/                       # Evaluation images (circuit1.png - circuit4.png)
│       ├── src/
│       │   ├── circuits/                      # Domain 3 (Circuits) Frontend Architecture
│       │   │   ├── view/
│       │   │   │   └── P5CircuitView.js       # 60 FPS transparent particle & halo renderer
│       │   │   ├── CircuitCompiler.js         # Polyline precomputation & distance interpolation
│       │   │   ├── CircuitController.js       # Master circuit lifecycle coordinator
│       │   │   ├── CircuitHitTest.js          # Authoritative geometric hit testing in source_px
│       │   │   ├── CircuitSolver.js           # Browser MNA DC operating point solver
│       │   │   ├── CircuitStore.js            # 4-layer state manager (Scene/Model/State/UI)
│       │   │   ├── CircuitTelemetry.js        # Bidirectional sync data table & equations
│       │   │   ├── CircuitTutorBridge.js      # Grounded bilingual AI tutor explanation drawer
│       │   │   ├── ComponentEditor.js         # Anchored HTML popover with log sliders
│       │   │   ├── EquationGenerator.js       # Step-by-step physical derivations
│       │   │   ├── KCLInspector.js            # Kirchhoff's Current Law node summations
│       │   │   ├── KVLInspector.js            # Kirchhoff's Voltage Law closed loop walks
│       │   │   ├── LinearSystem.js            # Float64Array LU decomposition with partial pivoting
│       │   │   └── ProbeManager.js            # Virtual Voltmeter & Ammeter instruments
│       │   ├── core/                          # Cross-domain core infrastructure
│       │   │   ├── coordinateMapper.js        # Aspect-ratio preserving CoordinateMapper
│       │   │   ├── diagramAnalyzer.js         # Client API client for diagram synthesis
│       │   │   ├── matterUnitAdapter.js       # SI to screen scaling adapter
│       │   │   ├── overlayStage.js            # 2-layer stage management
│       │   │   ├── sceneLoader.js             # Async scene loader
│       │   │   └── sceneRouter.js             # Factory routing to domain controllers
│       │   ├── mechanics/                     # Domain 1 (Mechanics/Kinematics)
│       │   │   ├── mechanicsController.js     # Mechanics lifecycle & UI bindings
│       │   │   ├── pendulumSimulation.js      # RK4 pendulum & phase portrait
│       │   │   ├── physicsBodyFactory.js      # Matter.js body creation & contact points
│       │   │   ├── projectileSimulation.js    # Analytical projectile flight
│       │   │   └── simulation.js              # Matter.js physics runner
│       │   ├── optics/                        # Domain 2 (Geometric Optics)
│       │   │   ├── engines/                   # Pure mathematical optics solvers
│       │   │   │   ├── mirrorEngine.js        # Spherical & plane mirror reflections
│       │   │   │   ├── prismEngine.js         # Triangular prism & glass slab ray tracing
│       │   │   │   ├── rayGeometry.js         # Vector math, line intersection, Snell solver
│       │   │   │   ├── snellInterfaceEngine.js# Interface refraction & TIR
│       │   │   │   └── thinLensEngine.js      # Thin lens conjugate equations & rays
│       │   │   ├── view/                      # Visual presentation & instruments
│       │   │   │   ├── opticsHUD.js           # Real-time metrics & angle badges
│       │   │   │   ├── opticsRenderer.js      # Ray drawing utilities
│       │   │   │   ├── opticsSprites.js       # Optical object sprites (candle flame)
│       │   │   │   ├── opticsTheme.js         # Curated HSL color palette
│       │   │   │   └── p5OpticsView.js        # p5 canvas overlay with draggable handles
│       │   │   ├── opticsController.js        # Master optics lifecycle coordinator
│       │   │   └── opticsSceneAdapter.js      # Schema v2.1 adapter
│       │   ├── main.js                        # App bootstrapping & domain tab switching
│       │   └── style.css                      # Modern dark theme, glassmorphism & responsive toolbars
│       ├── test/                              # Automated test suites
│       │   ├── test_circuit_solver.js         # 6 MNA solver precision tests (< 1e-12)
│       │   ├── test_coordinate_mapper.js      # 21 bidirectional coordinate mapping tests
│       │   └── test_optics_engines.js         # 65 optics analytical physics tests
│       ├── index.html                         # Responsive application layout
│       └── vite.config.js                     # Vite build & proxy configuration
├── PROJECT_CONTEXT.md                         # Authoritative roadmap & context specifications
└── README.md                                  # Repository overview
```

---

## 4. Key Milestones & Features Implemented (Since Commit `5405882`)

### 4.1 Domain 2: Geometric Optics Laboratory

Building on the initial geometry extraction in `5405882`, we implemented four dedicated mathematical solvers decoupled from canvas coordinates, executing in `source_px` and rendered via a 60 FPS transparent p5.js overlay:

1. **Analytical Thin Lens Formula**:
   - Implements Gaussian lens formula $\frac{1}{f} = \frac{1}{u} + \frac{1}{v}$ and lateral magnification $m = -\frac{v}{u}$.
   - Traces 3 principal rays: parallel ray passing through focal point $F_2$, central ray passing undeflected through optical center $O$, and focal ray through $F_1$ emerging parallel to principal axis.
   - For virtual images ($u < f$ or concave lenses), calculates dashed backward ray projections converging to virtual image coordinates.
2. **Snell's Law Interface Refraction & Total Internal Reflection (TIR)**:
   - Evaluates boundary conditions between media $n_1$ and $n_2$: $n_1 \sin\theta_1 = n_2 \sin\theta_2$.
   - Automatically detects critical angle $\theta_c = \arcsin(n_2 / n_1)$ when light travels from denser to rarer media.
   - Smoothly transitions from refracted ray to 100% Total Internal Reflection (TIR) when $\theta_1 > \theta_c$.
3. **Prism & Glass Slab Angular Deviation ($\delta$)**:
   - Traces ray entering first prism face, internal refraction, and second face emergence.
   - Dynamically calculates net deviation angle $\delta = (i_1 + i_2) - A$ and highlights normal lines at both boundaries.
4. **Spherical & Plane Mirrors**:
   - Models concave mirrors ($f > 0$, real and virtual inverted images), convex mirrors ($f < 0$, upright diminished virtual images), and plane mirrors ($v = -u, m = 1$).

```
                      Optics Verification Visuals
```
| Thin Lens Simulation | Triangular Prism Deviation |
| :---: | :---: |
| ![Thin Lens](./images/thin_lens_simulation.png) | ![Prism](./images/prism_simulation.png) |
| *Convex thin lens: principal rays, inverted real image, optical center, and focal points.* | *Ray entering triangular prism undergoing internal refraction with deviation angle.* |

| Spherical Convex Mirror | Snell's Law Interface Refraction |
| :---: | :---: |
| ![Convex Mirror](./images/mirror_simulation.png) | ![Interface Refraction](./images/interface_refraction.png) |
| *Convex mirror showing virtual upright diminished image behind the reflective surface.* | *Light ray crossing medium boundary with live incident and refracted angle arcs.* |

---

### 4.2 Domain 1: Mechanics & Kinematics Enhancements

1. **Analytical & Runge-Kutta 4 (RK4) Pendulum**:
   - Added pendulum physics with energy phase portrait, displaying potential energy $E_p = mgh$, kinetic energy $E_k = \frac{1}{2}mv^2$, and exact total energy conservation.
2. **Inclined Ramp & Sub-Pixel Spring Contact**:
   - Calibrated Matter.js collision polygons to match textbook ramp boundaries.
   - Resolved spring compression and launch physics obeying Hooke's Law ($F = -kx$) and elastic potential energy ($E_e = \frac{1}{2}kx^2$).
3. **Newton's Cradle Restitution**:
   - Implemented 5-bob momentum transfer with elastic collision restitution ($e \approx 1.0$).

![Kinematics Simulation](./images/kinematics_projectile.png)  
*Figure: Mechanics projectile in flight with live trajectory parabola, velocity vector, and collision detection.*

---

### 4.3 Domain 3: Circuits (Augmented Circuit Laboratory)

Circuits were designed following a strict architectural mandate: **Matter.js is prohibited for circuits**. Schematic wire length does not introduce electrical resistance. The domain operates purely via browser Modified Nodal Analysis:

1. **Mathematical MNA Engine (`LinearSystem.js` & `CircuitSolver.js`)**:
   - Solves the system of linear equations:
     $$\mathbf{A} \cdot \mathbf{x} = \mathbf{z} \quad \Longleftrightarrow \quad \begin{bmatrix} \mathbf{G} & \mathbf{B} \\ \mathbf{C} & \mathbf{D} \end{bmatrix} \begin{bmatrix} \mathbf{v} \\ \mathbf{j} \end{bmatrix} = \begin{bmatrix} \mathbf{i} \\ \mathbf{e} \end{bmatrix}$$
   - Uses `Float64Array` with dense LU decomposition and partial pivoting for maximum numerical stability.
   - Computes node voltages ($V_{\text{node}}$), component branch currents ($I_{\text{comp}}$), power dissipation ($P = V \cdot I$), and circuit equivalent resistance ($R_{\text{eq}}$).
2. **Parametric Polyline Particle Flow (`CircuitCompiler.js` & `P5CircuitView.js`)**:
   - Precomputes cumulative Euclidean segment lengths on schematic wires.
   - Implements `getPointAtDistance(d)` with tangent angle interpolation.
   - Conventional electron flow animates at 60 FPS with logarithmic speed scaling:
     $$\text{visualSpeed} = v_{\text{base}} \cdot \log\left(1 + \frac{|I|}{I_{\text{ref}}}\right)$$
   - Halos color-code wires by equipotential node voltages (red = high potential, blue = ground).
3. **Interactive Switch Key ($S_1$)**:
   - Dynamic switch rendering featuring an animated lever arm and interactive status badge (`🟢 [CLOSED - Click to Open]` / `🔴 [OPEN - Click to Close]`).
   - Clicking the switch toggles the physical circuit state, drops current to $0.0\text{ mA}$, sets $R_{\text{eq}} = \infty\text{ (Open)}$, and clears moving particles.
4. **Authentic Diamond Wheatstone Bridge (`textbook_bridge_diagram.svg`)**:
   - Features standard NCTB Class IX-X textbook styling with diamond vertices $A, B, C, D$, arms $P, Q, R, S$, central galvanometer $G$, key $K$, and battery $E$.
   - Accurately displays the balance condition ($\frac{P}{Q} = \frac{R}{S} \implies I_G = 0.0\text{ mA}$).
5. **Interactive Instruments & Grounded AI Tutor**:
   - **Virtual Probes**: Voltmeter ($V_{\text{red}} - V_{\text{black}}$) and Ammeter ($I_{\text{branch}}$).
   - **Kirchhoff's Current Law (KCL)**: Clicking any junction displays the green verification card ($\sum I_{\text{in}} = \sum I_{\text{out}}$).
   - **Kirchhoff's Voltage Law (KVL)**: Traces closed loops with an illuminated amber trail and step-by-step voltage summation ($\sum_{\text{loop}} V = 0$).
   - **Anchored Parameter Editor**: HTML popover floating beside clicked components with logarithmic sliders ($1\,\Omega \to 100\,\text{k}\Omega$) and live $V/I/P$ telemetry.
   - **Bilingual AI Tutor**: Contextual drawer explaining physical changes in English and Bengali.

```
                      Circuits Laboratory Visuals
```
| Diamond Wheatstone Bridge | Interactive Switch Toggled Open |
| :---: | :---: |
| ![Wheatstone Bridge](./images/wheatstone_bridge.png) | ![Switch Open](./images/series_circuit_switch.png) |
| *Authentic diamond Wheatstone bridge with arms P, Q, R, S ($100\,\Omega$), Galvanometer ($50\,\Omega, 0.0\text{ mA}$), and balance condition.* | *Key $S_1$ opened: lever lifted, particles halted, current $0.0\text{ mA}$, and $R_{\text{eq}} = \infty$.* |

| Anchored Parameter Popover | Live KVL Law Inspector |
| :---: | :---: |
| ![Popover](./images/circuit_component_popover.png) | ![KVL Card](./images/kvl_law_card.png) |
| *Anchored popover on Resistor $R_2$ with log resistance slider, live readouts, and [Why?] button.* | *Active KVL card with loop derivation $+12\text{V} - 4\text{V} - 8\text{V} = 0\text{V}$ and illuminated loop walk.* |

---

### 4.4 Core Infrastructure & AI Diagram Upload Studio

1. **Sub-Pixel Coordinate Registration (`CoordinateMapper.js`)**:
   - Authoritatively maps between original textbook image coordinates (`source_px`) and dynamic viewport pixels (`view_px`).
   - Computes uniform scale factor $s = \min(V_w / S_w, V_h / S_h)$ and letterbox/pillarbox offsets $(O_x, O_y)$.
   - Guarantees that interactive handles and physics overlays track textbook diagrams under any window resizing.
2. **Diagram Upload Studio (`upload_modal`)**:
   - Drag-and-drop modal allowing users to upload any textbook image.
   - Integrated with presets for quick testing and backend FastAPI computer vision synthesis.
3. **Bug Fixes & Hardening**:
   - Resolved Vite proxy collision by removing unnecessary `/uploads` proxy, ensuring static diagrams (`nctb_refraction_diagram.png`, `circuit1.png`–`circuit4.png`) load instantaneously with HTTP 200.
   - Isolated domain side panels so mechanics, optics, and circuits controls never overlap.

![Diagram Upload Studio](./images/diagram_upload_studio.png)  
*Figure: AI Diagram Upload Studio with drag-and-drop area, domain selector, and scenario presets.*

---

## 5. Important Source Code Implementations

### 5.1 Modified Nodal Analysis (MNA) Linear Solver
File: [`src/circuits/LinearSystem.js`](file:///d:/AugmentedPhysics/simulation_frontend/augmented_physics_v2/src/circuits/LinearSystem.js)

```javascript
export class LinearSystem {
  /**
   * Solve A * x = z using Gaussian elimination with partial pivoting and back-substitution.
   * @param {number} n - Matrix dimension
   * @param {Float64Array} A - Flat row-major matrix of size n*n
   * @param {Float64Array} z - Vector of size n
   * @returns {Float64Array} Solution vector x
   */
  static solve(n, A, z) {
    const M = new Float64Array(A);
    const b = new Float64Array(z);

    // Forward elimination with row pivoting
    for (let k = 0; k < n; k++) {
      let maxVal = Math.abs(M[k * n + k]);
      let pivotRow = k;
      for (let i = k + 1; i < n; i++) {
        const val = Math.abs(M[i * n + k]);
        if (val > maxVal) {
          maxVal = val;
          pivotRow = i;
        }
      }

      if (maxVal < 1e-12) {
        throw new Error(`[LinearSystem] Singular matrix: near-zero pivot at col ${k}`);
      }

      if (pivotRow !== k) {
        for (let j = k; j < n; j++) {
          const tmp = M[k * n + j];
          M[k * n + j] = M[pivotRow * n + j];
          M[pivotRow * n + j] = tmp;
        }
        const tmpB = b[k];
        b[k] = b[pivotRow];
        b[pivotRow] = tmpB;
      }

      const pivot = M[k * n + k];
      for (let i = k + 1; i < n; i++) {
        const factor = M[i * n + k] / pivot;
        M[i * n + k] = 0.0;
        for (let j = k + 1; j < n; j++) {
          M[i * n + j] -= factor * M[k * n + j];
        }
        b[i] -= factor * b[k];
      }
    }

    // Back-substitution
    const x = new Float64Array(n);
    for (let i = n - 1; i >= 0; i--) {
      let sum = b[i];
      for (let j = i + 1; j < n; j++) {
        sum -= M[i * n + j] * x[j];
      }
      x[i] = sum / M[i * n + i];
    }
    return x;
  }
}
```

---

### 5.2 Sub-Pixel Coordinate Mapper
File: [`src/core/coordinateMapper.js`](file:///d:/AugmentedPhysics/simulation_frontend/augmented_physics_v2/src/core/coordinateMapper.js)

```javascript
export class CoordinateMapper {
  constructor(sourceW = 800, sourceH = 600, viewW = 800, viewH = 600) {
    this.update(sourceW, sourceH, viewW, viewH);
  }

  update(sourceW, sourceH, viewW, viewH) {
    this.sourceW = sourceW > 0 ? sourceW : 800;
    this.sourceH = sourceH > 0 ? sourceH : 600;
    this.viewW = viewW > 0 ? viewW : 800;
    this.viewH = viewH > 0 ? viewH : 600;

    // Uniform aspect-ratio preserving scale (CSS object-fit: contain)
    this.scale = Math.min(this.viewW / this.sourceW, this.viewH / this.sourceH);
    this.renderW = this.sourceW * this.scale;
    this.renderH = this.sourceH * this.scale;

    // Centering offsets (letterbox / pillarbox)
    this.offsetX = (this.viewW - this.renderW) / 2;
    this.offsetY = (this.viewH - this.renderH) / 2;
  }

  sourceToView(srcX, srcY) {
    return {
      x: srcX * this.scale + this.offsetX,
      y: srcY * this.scale + this.offsetY
    };
  }

  viewToSource(viewX, viewY) {
    return {
      x: (viewX - this.offsetX) / this.scale,
      y: (viewY - this.offsetY) / this.scale
    };
  }
}
```

---

### 5.3 Analytical Thin Lens Solver & Virtual Ray Projections
File: [`src/optics/engines/thinLensEngine.js`](file:///d:/AugmentedPhysics/simulation_frontend/augmented_physics_v2/src/optics/engines/thinLensEngine.js)

```javascript
export function solveThinLens({ lensX, axisY, objectX, objectHeight, focalLength, bounds }) {
  const u = lensX - objectX; // Object distance (positive to the left)
  const f = focalLength;     // Positive for convex, negative for concave

  // Gaussian lens formula: 1/v - 1/u = 1/f  ==> 1/v = 1/f - 1/u (with sign convention u > 0)
  // 1/f = 1/u + 1/v ==> v = (f * u) / (u - f)
  const denom = u - f;
  const isInfinity = Math.abs(denom) < 1e-4;

  let v, m, imageX, imageHeight, isReal;
  if (isInfinity) {
    v = Infinity;
    m = Infinity;
    imageX = null;
    imageHeight = null;
    isReal = false;
  } else {
    v = (f * u) / denom;
    m = -v / u;
    imageX = lensX + v;
    imageHeight = objectHeight * m;
    isReal = (f > 0 && u > f);
  }

  // Generate principal rays: Parallel -> Focus, Central -> Undeflected, Focus -> Parallel
  const rays = generateThinLensRays({
    lensX, axisY, objectX, objectHeight, f, u, v, imageX, imageHeight, isReal, bounds
  });

  return { u, v, f, m, isReal, imageX, imageHeight, rays };
}
```

---

## 6. Testing & Quality Assurance Summary

The system is validated through comprehensive unit tests and end-to-end browser automation suites:

| Test Suite | Target Component | Coverage / Scenarios | Status |
| :--- | :--- | :--- | :--- |
| `test_circuit_solver.js` | `LinearSystem.js`, `CircuitSolver.js` | Series ($12\text{V}, 10\,\Omega, 20\,\Omega$), Open switch ($I = 0$), Parallel ($6\,\Omega \parallel 3\,\Omega$), Ideal Ammeter, Balanced Wheatstone Bridge ($I_G = 0$), Interactive Recalculation | **6 / 6 Passed** ($\Delta < 10^{-12}$) |
| `test_coordinate_mapper.js` | `CoordinateMapper.js` | Pillarbox mapping ($393 \times 328$), Letterbox mapping ($1536 \times 1024$), Bidirectional source/view inversion, Box scaling round-trip | **21 / 21 Passed** |
| `test_optics_engines.js` | `thinLensEngine`, `prismEngine`, `mirrorEngine`, `snellInterfaceEngine` | Real/inverted images ($u > 2f$, $u = 2f$, $f < u < 2f$), Virtual upright images ($u < f$, concave lenses), Vector Snell refraction, Triangular/right-angle prism TIR, Concave/convex/plane mirrors, Interface critical angle $\theta_c$ | **65 / 65 Passed** |
| **Total Automated Tests** | **Full Multi-Domain Suite** | **92 unit and integration tests** | **92 / 92 Passed (100%)** |

### Build Validation
- Production bundle compiled via Vite: `✓ 388 modules transformed`, built in 2.55s with 0 errors.

---

## 7. Conclusion & Next Steps

The AugmentedPhysics project has evolved from early optics segmentation into a complete, mathematically rigorous multi-domain textbook laboratory. With the successful delivery of Domain 3 (Circuits), high-precision optics ray tracing, and resilient coordinate mapping, students and educators can directly interact with printed textbook diagrams as live physics experiments.

**Planned Future Enhancements:**
- **Dynamic AC / RLC Circuits**: Transient analysis for inductors ($L$) and capacitors ($C$) using trapezoidal integration.
- **Wave Optics (Domain 2 Extension)**: Young's Double Slit interference patterns and diffraction gratings.
- **Mobile Touch Optimization**: Multi-touch pinch-to-zoom and mobile gesture navigation for classroom tablet deployments.
