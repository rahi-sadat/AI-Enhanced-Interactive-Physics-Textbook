# AugmentedPhysics Unified Engine — Comprehensive Project Context & Architecture Document

---

## 1. Executive Summary & Project Mission

**AugmentedPhysics v2** is an AI-enhanced, layout-invariant, interactive physics textbook simulator designed to transform static diagrams (from NCTB and standard national physics curricula) into interactive, mathematically rigorous, animated simulations directly inside a web browser.

The platform targets three primary physical domains across high school and undergraduate curricula:
1. **Kinematics & Dynamics (Mechanics)**: Simple pendulums, 5-bob Newton's cradles, ballistic projectiles with aerodynamic drag, inclined planes, and mass-spring oscillators.
2. **Geometric Optics**: Thin convex and concave lenses, spherical mirrors (concave/convex), triangular dispersing prisms, and planar dielectric refraction interfaces governed by Snell's Law.
3. **Electric Circuits**: Direct current (DC) loops, series-parallel resistor networks, ammeter/voltmeter probes, and Wheatstone bridge null-deflection balance networks solved via Modified Nodal Analysis (MNA).

### Core Problem Solved
Historically, the project suffered from fractured domain solvers (Matter.js + an ad-hoc RK4 integrator for mechanics, separate hand-rolled ray tracers for optics, and a rudimentary linear solver for circuits). Each solver had unique coordinate assumptions, hardcoded pixel dimensions (e.g. assuming $800 \times 600$ viewports), severe geometric drift (>150 px error on pendulums), reversed ray-tracing paths on concave mirrors, classifier hallucinations that assigned projectile diagrams to Wheatstone bridge circuits, and character encoding corruptions (mojibake).

This project undertook an end-to-end architectural overhaul:
- Built a **Unified Physics Simulation Engine Core** based on generalized state vectors, a multidimensional Newton-Raphson algebraic solver, a symplectic semi-implicit Euler dynamic integrator, and a continuous event/collision redirection engine.
- Implemented a **Strict Sub-Pixel Coordinate System Contract** (`source_px`) ensuring layout-invariant rendering with zero drift across responsive device viewports.
- Developed an **Automated Diagram Classifier and Calibration Pipeline** capable of analyzing user-uploaded textbook images, classifying domain concepts without hallucinations, and auto-calibrating physical geometries.
- Fixed all regressions, encoding bugs, and domain-specific edge cases, achieving 100% test pass rates across all test suites.

---

## 2. Root Cause Analysis & Problem Breakdown

Prior to this architectural unification, the project exhibited critical failures across multiple layers:

### A. Fragmented Solvers & Architectural Discontinuity
- **Mechanics**: Matter.js rigid-body dynamics was paired with an independent 240 Hz Runge-Kutta 4 (RK4) integrator for pendulums. Neither communicated with a common state vector, causing desynchronization between colliders, visual sprites, and telemetry cards.
- **Optics**: Standalone modules (`thinLensEngine.js`, `mirrorEngine.js`, `prismEngine.js`, `snellInterfaceEngine.js`) re-implemented ray-intersection math from scratch with inconsistent normal-vector conventions.
- **Circuits**: A standalone DC solver with fragile nodal parsing failed on multi-branch bridge configurations or when ammeter branches introduced zero-impedance paths.

### B. Geometry & Pivot Misalignment (Pendulum / Newton's Cradle)
- In diagrams such as `test1.jpg` ($797 \times 652\text{ px}$ scan) and `pendulum.png` (5-bob Newton's cradle), the simulation rendered the pivot and bobs with a **$>158\text{ px}$ offset** from the underlying textbook diagram lines.
- In the 5-pendulum system, momentum was not conserved across elastic impacts: striking Bob 1 caused bobs to overlap or freeze rather than propagating momentum cleanly to Bob 5.

### C. Concave Mirror Vector Reversal Bug
- For right-facing concave mirrors with an object located in front of the reflective surface ($x_{\text{obj}} > x_{\text{mirror}}$), the ray-reflection logic flipped the sign of the horizontal normal improperly. Rays passed behind the mirror towards $x = 0$ instead of focusing at the real image plane in the front reflective half-space ($x \ge x_{\text{mirror}}$).

### D. Hardcoded Viewports & Viewport Leakage
- `diagramAnalyzer.js` and early scene builders assumed a fixed canvas size of $800 \times 600\text{ px}$ and hardcoded key elements to $(400, 300)\text{ px}$. When users uploaded high-resolution diagrams (e.g., $1920 \times 878\text{ px}$ or $1485 \times 885\text{ px}$), the simulation overlay shrunk to an isolated corner or drifted completely off-screen.

### E. Classifier Hallucinations & Domain Misassignments
- The OpenCV classification pipeline in `apps/api/main.py` relied on naive Hough Line transforms. Because projectile trajectory diagrams feature diagonal tangent vectors and Wheatstone bridges feature diamond diagonals, the classifier frequently categorized 2D projectile diagrams as Wheatstone bridges.
- Similarly, optical thin lens diagrams (such as Figure 2.14 showing biconvex lens image formation at $2F$) were misclassified as 2D projectile motion because the curved lens contours triggered the parabolic arc detector.

### F. Projectile Kinematics Mismatch
- When projectile motion loaded, default launch angles ($51^\circ$ instead of $45^\circ$) and uncalibrated pixels-per-meter ratios led to an Apex of $19.13\text{ m}$ instead of the textbook diagram's theoretical $15.93\text{ m}$ ($v_0 = 25\text{ m/s}, \theta = 45^\circ, g = 9.81\text{ m/s}^2$), causing visible discordance between the drawn curve and the animated sprite.

### G. UI Desynchronization & Mojibake Font Corruptions
- When uploading or switching scenarios in Circuits mode, the diagram rendered a Wheatstone bridge while the scenario selector dropdown remained stuck on "Series Circuit: 12V, 10Ω, 20Ω".
- Multi-byte UTF-8 emoji and Bengali script characters in `index.html` were saved or transformed with mismatched encodings, producing garbled mojibake text (e.g. `ÐŸ'£ MECHANICS CONTROLS`, `âš-ï¸ `, `nâ‚ `) and triggering Vite build parse warnings (`control-character-in-input-stream`).

---

## 3. High-Level System Architecture

The following diagram illustrates the complete, integrated architecture of AugmentedPhysics v2:

```mermaid
graph TB
    subgraph Client ["Client Browser (apps/web)"]
        UI["User Interface Layer<br/>(HTML5 / CSS3 / Vanilla JS)"]
        Nav["Domain Navigation Tabs<br/>[Kinematics | Optics | Circuits]"]
        UploadModal["Universal Diagram Upload Modal<br/>(Drag-and-Drop / File Picker)"]
        
        subgraph ViewportLayer ["Figure Viewport & Coordinate System"]
            CoordMap["Uniform Contain CoordinateMapper<br/>(Source px &harr; Viewport px)"]
            Layer1["Layer 1: Visual Background (&lt;img&gt; Source)"]
            Layer2["Layer 2: Transparent Physics Canvas Overlay"]
            Layer3["Layer 3: Interactive Sprites, Draggables & HUD"]
        end
        
        subgraph FrontendCV ["Browser-Side Diagram Analysis Fallback"]
            ClientAnalyzer["diagramAnalyzer.js<br/>(Geometric Feature & Color Segmentation)"]
        end

        subgraph CompatLayer ["Engine Compatibility Layer (compat/)"]
            AdapterRouter["EngineCompatibilityLayer.js<br/>(Drop-in Shim & Runtime Adapter)"]
        end
    end

    subgraph BackendAPI ["FastAPI Python Service (apps/api)"]
        FastAPI["FastAPI App (port 8000)"]
        Classifier["Hierarchical Diagram Classifier<br/>(classify_diagram_concept)"]
        CV_Optics["Optics Extractor<br/>(Optical Axis, Lens Contour, Focal Points)"]
        CV_Proj["Projectile Extractor<br/>(Parabolic Polyfit, Anisotropic PPM)"]
        CV_Bridge["Bridge Extractor<br/>(HoughCircles Galvo, Node Junctions)"]
    end

    subgraph UnifiedEngine ["Unified Physics Engine Core (src/core/)"]
        StateVec["Generalized State Vector [q, q_dot, &lambda;]"]
        NewtonRaphson["Newton-Raphson Nonlinear Solver<br/>(Finite-Difference Jacobian J, Damping)"]
        Integrator["Symplectic Semi-Implicit Euler Integrator<br/>(Volume-Preserving Dynamic Stepper)"]
        EventEngine["Event & Collision Engine<br/>(Snell Refraction, Law of Reflection, Impulse Restitution)"]
    end

    subgraph DomainAdapters ["Domain Adapters (src/adapters/)"]
        MechAdapter["MechanicsAdapter.js<br/>(Pendulum, Newton's Cradle, Projectile, Springs)"]
        OpticsAdapter["OpticsAdapter.js<br/>(Thin Lenses, Spherical Mirrors, Prisms, Snell Interfaces)"]
        CircuitAdapter["CircuitsAdapter.js<br/>(Modified Nodal Analysis, KCL/KVL, Wheatstone Bridge)"]
    end

    %% Wiring connections
    UploadModal -->|Multipart Image POST| FastAPI
    UploadModal -->|Local Fallback| ClientAnalyzer
    FastAPI --> Classifier
    Classifier --> CV_Optics
    Classifier --> CV_Proj
    Classifier --> CV_Bridge
    CV_Optics & CV_Proj & CV_Bridge -->|Calibrated Scene JSON| AdapterRouter
    ClientAnalyzer -->|Calibrated Scene JSON| AdapterRouter

    UI --> Nav
    Nav --> AdapterRouter
    AdapterRouter --> MechAdapter & OpticsAdapter & CircuitAdapter

    MechAdapter & OpticsAdapter & CircuitAdapter --> StateVec
    StateVec --> NewtonRaphson
    StateVec --> Integrator
    Integrator & NewtonRaphson --> EventEngine
    EventEngine --> StateVec

    StateVec -->|Sub-pixel Source Coordinates| CoordMap
    CoordMap --> Layer2
    CoordMap --> Layer3
```

---

## 4. Detailed Data Flow Pipeline

The end-to-end processing pipeline from diagram upload to live animation follows a deterministic, 6-stage lifecycle:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Web Frontend (apps/web)
    participant API as Python API (apps/api)
    participant Shim as Compatibility Layer
    participant Adapter as Domain Adapter
    participant Core as Unified Engine Core
    participant Canvas as Render Canvas

    User->>Web: Uploads Textbook Diagram (PNG/JPG)
    Web->>API: POST /api/analyze-diagram (Image + Filename)
    Note over API: Hierarchical Classifier: Lens -> Projectile -> Bridge -> Circuit
    API->>API: Sub-pixel Geometry Extraction & Calibration
    API-->>Web: Scene JSON (Source Coordinates, Anchor Points, PPM)
    Web->>Shim: PhysicsRuntime.load(scene, container)
    Shim->>Adapter: Instantiate Domain Adapter (Mechanics/Optics/Circuits)
    Adapter->>Core: Compile State Vector [q, q_dot, &lambda;] & Residual Funcs
    
    loop Simulation Loop (60 Hz / 240 Hz Sub-stepped)
        Core->>Core: Evaluate Residuals & Constraints (Newton-Raphson)
        Core->>Core: Dynamic State Integration (Symplectic Euler)
        Core->>Core: Continuous Collision & Event Check (EventEngine)
        Core-->>Adapter: Updated Physical State
        Adapter-->>Canvas: Project Coordinates via CoordinateMapper (source_px -> view_px)
        Canvas-->>User: Rendered Frame (Layered Sprites, Vectors, HUD Telemetry)
    end

    User->>Web: Interacts with Sliders / Drag Handles (e.g. angle &theta;, lens position)
    Web->>Adapter: setParameter(name, value)
    Adapter->>Core: Mutate State Vector / Re-solve Constraints
```

---

## 5. Unified Physics Engine Core Architecture

The Unified Physics Engine is implemented under `d:/Augmented physics unified engine/src/core/` and integrated into `D:/AugmentedPhysics/engine/unified/`. It replaces fragmented, domain-specific ad-hoc scripts with a unified mathematical formulation.

### A. Generalized State Vector Formulation
All physical systems are abstracted into a single continuous-discrete state vector:
$$\mathbf{X} = \begin{bmatrix} \mathbf{q} \\ \mathbf{\dot{q}} \\ \boldsymbol{\lambda} \end{bmatrix}$$
Where:
- $\mathbf{q} \in \mathbb{R}^n$: Generalized coordinates (e.g., pendulum angles $\theta_i$, projectile positions $[x, y]^T$, optical ray origins/directions $[x_r, y_r, \theta_r]^T$, capacitor voltages).
- $\mathbf{\dot{q}} \in \mathbb{R}^n$: Generalized velocities ($\dot{\theta}_i, v_x, v_y, \dot{V}_k$).
- $\boldsymbol{\lambda} \in \mathbb{R}^m$: Algebraic constraint variables (e.g., wire tensions, lens surface normals, node voltages in MNA circuits).

### B. Newton-Raphson Multidimensional Nonlinear Solver (`NewtonRaphson.js`)
For algebraic loops, optical path intersections, and MNA nodal balances:
$$\mathbf{F}(\mathbf{X}) = \mathbf{0}$$
The solver performs iterative updates:
$$\mathbf{X}^{(k+1)} = \mathbf{X}^{(k)} - \left[ \mathbf{J}(\mathbf{X}^{(k)}) \right]^{-1} \mathbf{F}(\mathbf{X}^{(k)})$$
- **Numerical Finite-Difference Jacobian**: Computed via forward/central differences $J_{ij} = \frac{\partial F_i}{\partial X_j} \approx \frac{F_i(\mathbf{X} + \epsilon \mathbf{e}_j) - F_i(\mathbf{X})}{\epsilon}$, eliminating the need for symbolic derivation.
- **Singularity Damping (Levenberg-Marquardt style)**: When matrix condition numbers spike (e.g., ill-conditioned circuit nodes or ray grazing incidence), damping is applied: $(\mathbf{J}^T \mathbf{J} + \mu \mathbf{I}) \Delta \mathbf{X} = -\mathbf{J}^T \mathbf{F}$.
- **Backtracking Armijo Line Search**: Ensures monotonic decrease in $\|\mathbf{F}\|_2$.

### C. Symplectic Semi-Implicit Euler Integrator (`Integrator.js`)
For dynamic systems (pendulums, Newton's cradle, projectiles with drag, springs):
$$\mathbf{v}_{t + \Delta t} = \mathbf{v}_t + \mathbf{M}^{-1} \mathbf{F}_{\text{total}}(\mathbf{q}_t, \mathbf{v}_t) \Delta t$$
$$\mathbf{q}_{t + \Delta t} = \mathbf{q}_t + \mathbf{v}_{t + \Delta t} \Delta t$$
- **Conservation of Phase-Space Volume**: Unlike standard explicit Euler (which gains artificial energy) or RK4 (which dampens or drifts over long times), the semi-implicit Euler scheme preserves the symplectic 2-form $\sum dq_i \wedge dp_i$, bounding energy drift to $< 0.7\%$ over thousands of oscillation cycles.

### D. Continuous Event & Collision Engine (`EventEngine.js`)
Handles discontinuous boundary crossings across all domains:
1. **Ray-Segment & Ray-Arc Intersections**: Exact quadratic and linear parametric roots for lens surfaces, mirror boundaries, and prism facets.
2. **Snell's Law Vector Refraction**:
   $$\mathbf{t} = \eta \mathbf{i} + \left( \eta \cos\theta_i - \sqrt{1 - \eta^2 (1 - \cos^2\theta_i)} \right) \mathbf{n}, \quad \eta = \frac{n_1}{n_2}$$
   Detects Total Internal Reflection (TIR) when $1 - \eta^2 (1 - \cos^2\theta_i) < 0$ and redirects rays into specular reflection.
3. **Law of Reflection**:
   $$\mathbf{r} = \mathbf{i} - 2(\mathbf{i} \cdot \mathbf{n})\mathbf{n}$$
4. **Impulse Restitution & Momentum Transfer**:
   $$J = -\frac{(1 + e) (\mathbf{v}_1 - \mathbf{v}_2) \cdot \mathbf{n}}{\frac{1}{m_1} + \frac{1}{m_2}}$$

---

## 6. Domain Adapters & Compatibility Architecture

```mermaid
classDiagram
    class UnifiedEngineCore {
        +stateVector: Float64Array
        +residuals: Function[]
        +constraints: Function[]
        +step(dt)
        +solveAlgebraic()
        +registerEvent(trigger, action)
    }

    class MechanicsAdapter {
        +bobs: PendulumBob[]
        +projectile: ProjectileBall
        +cradleBobs: Bob[]
        +buildResiduals()
        +stepDynamics(dt)
        +applyMomentumTransfer()
    }

    class OpticsAdapter {
        +opticalElements: Element[]
        +rays: OpticalRay[]
        +traceRays()
        +calculateGaussianImage()
        +evaluateSnellBoundary()
    }

    class CircuitsAdapter {
        +nodes: Node[]
        +components: Component[]
        +mnaMatrix: Matrix
        +solveMNA()
        +calculateEquivalentResistance()
        +getBranchCurrents()
    }

    class EngineCompatibilityLayer {
        +load(scene, container, options)
        +play()
        +pause()
        +reset()
        +setParameter(name, value)
        +getState()
    }

    UnifiedEngineCore <|-- MechanicsAdapter
    UnifiedEngineCore <|-- OpticsAdapter
    UnifiedEngineCore <|-- CircuitsAdapter
    EngineCompatibilityLayer --> MechanicsAdapter
    EngineCompatibilityLayer --> OpticsAdapter
    EngineCompatibilityLayer --> CircuitsAdapter
```

### 1. `MechanicsAdapter.js`
- Translates simple pendulums, 5-bob cradles, and projectiles into the state vector.
- Calculates analytical metrics (period $T_0 = 2\pi\sqrt{L/g}$, apex height $H = \frac{v_0^2 \sin^2\theta}{2g}$, range $R = \frac{v_0^2 \sin 2\theta}{g}$).
- Employs an exact closed-form trajectory solver alongside the symplectic integrator to allow instantaneous slider updates without visual stutter.

### 2. `OpticsAdapter.js`
- Translates optical benches, thin spherical lenses, concave/convex mirrors, and prisms.
- Employs Fermat's principle and Gaussian optics formulas ($\frac{1}{v} - \frac{1}{u} = \frac{1}{f}$, $m = \frac{v}{u}$) to compute canonical reference rays (parallel-through-focal, optical-center through-pass, focal-to-parallel) that project cleanly onto textbook diagrams.

### 3. `CircuitsAdapter.js`
- Formulates the standard Modified Nodal Analysis (MNA) block matrix:
  $$\begin{bmatrix} \mathbf{G} & \mathbf{B} \\ \mathbf{C} & \mathbf{D} \end{bmatrix} \begin{bmatrix} \mathbf{v} \\ \mathbf{j} \end{bmatrix} = \begin{bmatrix} \mathbf{i} \\ \mathbf{e} \end{bmatrix}$$
- Solves for all node potentials $\mathbf{v}$ and voltage source currents $\mathbf{j}$ via $LU$ decomposition with partial pivoting ($PA = LU$).
- Computes Wheatstone bridge null deflection ($I_G = 0\text{ A}$ when $P/Q = R/S$) and total equivalent network resistance $R_{\text{eq}}$.

### 4. `EngineCompatibilityLayer.js`
- Implements the `PhysicsRuntime` interface expected by `InteractiveFigure.js`:
  - `load(scene, container, options)`, `play()`, `pause()`, `reset()`, `setParameter(key, val)`, `getParameter(key)`, `getState()`, `destroy()`.
- Provides drop-in shims for legacy controllers in `main.js`, guaranteeing zero regressions across older pages and test suites.

---

## 7. The Coordinate System & Layout-Invariant Engine

A major accomplishment was eliminating layout drift across viewport resizing. 

### The Coordinate Contract
- **Authoritative Frame**: Native image pixel resolution (`source_px`). All physics positions, pivots, lens centers, and circuit junctions are defined solely in `source_px`.
- **Viewport Frame**: Screen pixel space (`view_px`).

### Uniform Contain Coordinate Mapper
The mapping is computed dynamically by `CoordinateMapper.js`:
$$s = \min\left( \frac{W_{\text{viewport}}}{W_{\text{source}}}, \frac{H_{\text{viewport}}}{H_{\text{source}}} \right)$$
$$x_0 = \frac{W_{\text{viewport}} - W_{\text{source}} \cdot s}{2}, \quad y_0 = \frac{H_{\text{viewport}} - H_{\text{source}} \cdot s}{2}$$

Transformations between frames:
$$x_{\text{view}} = x_0 + x_{\text{source}} \cdot s, \quad y_{\text{view}} = y_0 + y_{\text{source}} \cdot s$$
$$x_{\text{source}} = \frac{x_{\text{view}} - x_0}{s}, \quad y_{\text{source}} = \frac{y_{\text{view}} - y_0}{s}$$

### Multi-Breakpoint Validation
The automated test suite in `apps/web/tests/figure-system.test.js` exercises 5 distinct viewport configurations:
1. **Desktop 1080p** ($1920 \times 1080$)
2. **Laptop Standard** ($1440 \times 900$)
3. **Tablet Landscape** ($1024 \times 768$)
4. **Tablet Portrait** ($768 \times 1024$)
5. **Mobile Viewport** ($390 \times 844$)
6. **Dynamic Sidebar Transition** ($1440\text{ px} \to 650\text{ px} \to 1440\text{ px}$)

**Result**: Tested across all anchor points (pivots, resistors, switches, batteries, optical centers), the maximum detected drift is **$0.0000\text{ px}$** (tolerance: $0.001\text{ px}$).

---

## 8. Universal Diagram Scanner & Classifier Pipeline

The classifier pipeline lives in `apps/api/main.py` with an in-browser fallback in `apps/web/src/features/simulations/core/diagramAnalyzer.js`.

### The Hierarchical Classification Algorithm
To prevent the previous classifier hallucinations, recognition executes in a strict priority hierarchy:

```mermaid
flowchart TD
    Start["Input Image (w &times; h)"] --> Step1["Step 1: Check Manual Domain Override"]
    Step1 -- "Domain Explicitly Set" --> ForceDomain["Enforce Domain (optics/circuits/mechanics)"]
    Step1 -- "Auto-Detect" --> Step2{"Step 2: Optical Feature Scan"}
    
    Step2 -- "Optical Axis + Central Lens Contour Detected" --> ClassOptics["Classify: Geometric Optics<br/>(thin_lens / mirror / prism)"]
    Step2 -- "No Strong Optical Axis" --> Step3{"Step 3: Parabolic Arc Detection"}
    
    Step3 -- "Blue Channel CC Polyfit R&sup2; > 0.92" --> ClassProj["Classify: Kinematics<br/>(projectile motion)"]
    Step3 -- "No Strong Parabola" --> Step4{"Step 4: Galvanometer & Diamond Scan"}
    
    Step4 -- "Central Galvo Circle + 4 Nodes" --> ClassBridge["Classify: Circuits<br/>(wheatstone_bridge)"]
    Step4 -- "No Galvo Circle" --> Step5{"Step 5: Circuit Line Loops"}
    
    Step5 -- "Rectangular Loop + Component Symbols" --> ClassLoop["Classify: Circuits<br/>(dc_loop / ladder)"]
    Step5 -- "No Circuit Loops" --> ClassMechFallback["Fallback: Mechanics<br/>(pendulum / incline)"]
```

### Key Technical Innovations
1. **Optical Priority**: Inspecting central vertical axes and focal point labels ($F_1, F_2$) *before* arc fitting completely stopped thin lens diagrams from being classified as projectile parabolas.
2. **Galvanometer Circle Gate**: Requiring a central circle (via HoughCircles at $38\%\text{--}62\% x, 28\%\text{--}72\% y$) before classifying a diamond shape as a Wheatstone bridge stopped projectile diagrams with diagonal tangent vectors from triggering false bridge matches.
3. **Dynamic Scaling Proportions**: Scene builders now scale geometries relative to actual image dimensions ($w \times h$) rather than hardcoding $(400, 300)$.
4. **Filename Semantic Forwarding**: Frontend upload handler forwards the original file name (`uploadedFile.name`), allowing semantic tokens (`bridge`, `lens`, `prism`, `projectile`, `circuit`) to provide immediate high-confidence priors.

---

## 9. Comprehensive Bug Fixes & Diagnostics Log

| Diagnostic Issue | Root Cause | Technical Resolution Applied | Verification Artifact / Status |
| :--- | :--- | :--- | :--- |
| **5-Pendulum Newton's Cradle Failure** | Hardcoded bob centers and missing momentum propagation step | Calibrated 5 bobs to source diagram ($0.246\text{ px}$ error vs target); added elastic collision impulse handler in `MechanicsAdapter` | `newtons_cradle_scene.json`<br/>**PASS** (Bob 5 swings to $25.80^\circ$) |
| **Concave Mirror Ray Reversal** | Horizontal normal vector sign flipped incorrectly for right-facing mirrors | Enforced reflection strictly in reflective half-space ($x \ge x_{\text{mirror}}$); bounded rays to viewport | `test_optics_adapter.js`<br/>**PASS** ($x_{\text{end}} = 733\text{ px}$) |
| **Projectile Simulation Drift & Telemetry Mismatch** | Default angle set to $51^\circ$ instead of $45^\circ$, causing $H=19.13\text{ m}$ vs target $15.93\text{ m}$ | Calibrated analytical solver to $v_0 = 25\text{ m/s}, \theta = 45^\circ, g = 9.81\text{ m/s}^2$; added live sliders for angle and speed | `fix_check2_projectile.png`<br/>**PASS** ($H = 15.93\text{ m}, R = 63.71\text{ m}$) |
| **Circuit Dropdown Desync (Wheatstone Bridge)** | Scenario selector did not update when bridge diagram was uploaded | Wired `CircuitController.js` and `diagramAnalyzer.js` to automatically select and sync Wheatstone Bridge MNA state | `nctb_series_circuit_check4.png`<br/>**PASS** ($V_C = V_D = 5\text{V}, I_G = 0\text{A}$) |
| **Lens Diagram Auto-Detect Failure (Screenshot 4)** | Lens contours triggered parabolic polynomial fit, classifying lens as projectile | Implemented hierarchical classifier prioritizing optical axes and lens markers before projectile arc fitting | `optics_autodetect_check3.png`<br/>**PASS** (Classifies as `thin_lens`) |
| **Mojibake & UTF-8 Encoding Corruptions** | Multi-byte UTF-8 emojis and Bengali text improperly decoded in HTML & scripts | Sanitized all corrupted bytes in `index.html` and controllers; converted to standard HTML entities and clean Unicode | `fix_check1_mechanics.png`<br/>**PASS** (Clean fonts, 0 build warnings) |

---

## 10. Verification & Test Metrics Summary

### 1. Multi-Domain Diagram Verification Suite (`tests/test_all_domains_diagrams.js`)
- **Optics Domain**: 7 / 7 passed (Snell's law error $1.11 \times 10^{-15}$, thin lens Gaussian error $0.0094\text{ px}$, mirror reflection ray count = 2).
- **Kinematics Domain**: 4 / 4 passed (Pendulum period error $< 10^{-5}\text{ s}$, symplectic energy drift $0.6754\% < 1.0\%$, Newton's cradle 5-bob momentum transfer verified).
- **Projectile Domain**: 3 / 3 passed (Time to apex error $5.05 \times 10^{-6}\text{ s}$, apex height error $0.884\text{ px} < 0.1\%$, ground restitution bounce verified).
- **Circuits Domain**: 7 / 7 passed (4 MNA unknowns, reference node $0.0000\text{ V}$, bridge balance potential difference $8.88 \times 10^{-16}\text{ V}$, galvanometer current $1.78 \times 10^{-17}\text{ A}$, equivalent resistance $100.0000\,\Omega$).
- **Total**: **21 / 21 passed (100.0%)**.

### 2. Frontend Layout & Regression Suite (`apps/web/tests/figure-system.test.js`)
- **Total Test Cases**: **375 / 375 passed (100.0%)**.
- **Layout Invariance**: $0.0000\text{ px}$ drift across all breakpoints.

### 3. Production Build Validation (`npm run build`)
- **Vite v8.3.0 Client Build**: **Success (408 modules transformed, 0 errors, 0 parse warnings)**.

---

## 11. Project Directory Structure & Key File Map

```
AugmentedPhysics Unified Project/
│
├── d:/Augmented physics unified engine/     [Engine Workspace]
│   ├── BUILD_LOG.md                         # Detailed incremental development log
│   ├── context.md                           # This comprehensive master architecture document
│   ├── package.json                         # Unified engine test dependencies
│   ├── src/
│   │   ├── core/
│   │   │   ├── UnifiedEngineCore.js         # Core state vector, stepper, constraint registry
│   │   │   ├── NewtonRaphson.js             # Multidimensional nonlinear algebraic solver
│   │   │   ├── Integrator.js                # Symplectic semi-implicit Euler dynamic integrator
│   │   │   └── EventEngine.js               # Ray-boundary intersections, Snell & reflection redirects
│   │   ├── adapters/
│   │   │   ├── MechanicsAdapter.js          # Pendulums, Newton's cradle, projectiles with drag
│   │   │   ├── OpticsAdapter.js             # Thin lenses, mirrors, prisms, planar interfaces
│   │   │   └── CircuitsAdapter.js           # MNA solver, KCL/KVL, Wheatstone bridge
│   │   └── compat/
│   │       └── EngineCompatibilityLayer.js  # Zero-breakage shim for PhysicsRuntime interface
│   └── tests/
│       ├── test_all_domains_diagrams.js     # Master 21-point multi-domain verification test
│       ├── test_engine_core.js              # Unit tests for Newton-Raphson & Integrator
│       ├── test_mechanics_adapter.js        # Regression tests for pendulums and projectiles
│       ├── test_optics_adapter.js           # Regression tests for mirrors and lenses
│       └── test_circuits_adapter.js         # Linear system and Wheatstone bridge tests
│
└── D:/AugmentedPhysics/                     [Full Application Repository]
    ├── apps/
    │   ├── api/
    │   │   └── main.py                      # FastAPI backend with OpenCV hierarchical classifier
    │   └── web/
    │       ├── index.html                   # Sanitized HTML with entity icons and clean typography
    │       ├── package.json                 # Web dependencies (Vite, P5, Canvas utilities)
    │       ├── src/
    │       │   ├── main.js                  # App bootstrap, upload modal wiring, domain router
    │       │   ├── components/
    │       │   │   ├── InteractiveFigure.js # Platform runtime container
    │       │   │   └── FigureViewport.js    # Canvas mount and coordinate mapper interface
    │       │   └── features/simulations/
    │       │       ├── core/
    │       │       │   ├── coordinateMapper.js # Uniform Contain coordinate transform math
    │       │       │   ├── diagramAnalyzer.js  # In-browser CV fallback & scene builder
    │       │       │   └── overlayStage.js     # Multi-layer canvas management
    │       │       ├── mechanics/
    │       │       │   └── mechanicsController.js # Projectile & pendulum UI controllers
    │       │       ├── optics/
    │       │       │   └── opticsController.js    # Lens, mirror, prism controllers
    │       │       └── circuits/
    │       │           └── CircuitController.js   # MNA circuit controller & meter probes
    └── engine/                              # Production symlink / mirror of unified engine modules
```

---

## 12. How to Run, Test, and Verify

### Running the Web Application
```bash
cd "D:/AugmentedPhysics/apps/web"
npm run dev
# Vite will launch on http://127.0.0.1:5173/
```

### Running the Python Computer Vision API (Optional for Backend CV)
```bash
cd "D:/AugmentedPhysics/apps/api"
uvicorn main:app --reload --port 8000
# Runs FastAPI on http://127.0.0.1:8000/
```

### Running Frontend Tests & Production Build
```bash
cd "D:/AugmentedPhysics/apps/web"
npm test          # Runs 375-point layout invariance test suite
npm run build     # Compiles production distribution bundle
```

### Running the Master Multi-Domain Verification Suite
```bash
node "d:/Augmented physics unified engine/tests/test_all_domains_diagrams.js"
# Validates all 4 physical domains (21 / 21 PASS)
```

---
*Document Version: 2.0.0 — Author: Antigravity AI Engineering Team — Date: 2026-09-21*
