# Layout-Invariant Figure Alignment Specification & Architecture

## Executive Summary

This document establishes the permanent architectural contract for **Augmented Physics Figure Alignment**. In an AI-enhanced interactive textbook, simulation objects (pendulums, light rays, lenses, circuit nodes, particles) must remain locked with sub-pixel precision to the original textbook diagram pixels, regardless of viewport size, sidebar drawer state, control panel dimensions, or responsive breakpoints.

---

## 1. Root Cause Analysis: The Coordinate Mixing Bug

### 1.1 The Legacy Pipeline (Flawed)

```text
CURRENT PIPELINE (BEFORE FIX)

Source textbook image (e.g., circuit2.png: 878 × 593 px)
    ↓ (Hardcoded / cropped scene dimensions: 784 × 462 px)
Scene JSON Coordinates
    ↓ (Renderers inspected container.clientWidth or window.innerWidth)
Display / Canvas Geometry (createCanvas(w, h))
    ↓ (Independent aspect ratio or unpadded canvas scaling)
Renderer Drawing (P5 / Canvas2D / Matter.js)
    ↓
Broken Alignment (Simulation drifted or squashed onto blank whitespace)
```

### 1.2 Identified Root Causes

1. **Unshared Display Rectangles**:
   Previously, the background image was sized via CSS rules (`max-width: 100%`, `object-fit: contain`) while the simulation canvas queried `container.clientWidth` or `window.innerWidth`. When letterboxing or pillarboxing occurred, the image centered itself with CSS padding, but the canvas covered the entire container, causing simulation anchors to drift by tens or hundreds of pixels away from diagram features.

2. **Hardcoded / Downscaled Scene Metadata**:
   In several scenes (`circuit2_scene.json`, `circuit3_scene.json`, `circuit4_scene.json`), coordinates were measured against cropped or thumbnail resolutions (e.g., $784 \times 462$ instead of $878 \times 593$), producing a permanent mismatch between the scene coordinate space and the raster image's native resolution.

3. **Window Resize vs. Local Container Resizing**:
   Components listened to `window.addEventListener('resize')`. When the AI sidebar opened, the book column narrowed by $320\text{ px}$, but the browser window width remained unchanged. Consequently, no resize event fired, leaving the simulation stretched at stale dimensions.

4. **Simulation State Coupled to Render Geometry**:
   Physics solvers or renderers reset physical variables (e.g., resetting pendulum angle $\theta$ or re-initializing Matter.js bodies) upon layout shifts instead of maintaining pure physical state in source space.

---

## 2. The Authoritative Architecture

### 2.1 The Invariant Pipeline (After Fix)

```text
AUTHORITATIVE PIPELINE (AFTER FIX)

                      Textbook Source Diagram
                                 │
                   Native Pixel Space (Authoritative)
                   e.g., sourceWidth = 878, sourceHeight = 593
                                 │
                                 ▼
                           PhysicsScene
                    (Coordinates stored in source_px)
                                 │
                                 ▼
                          PhysicsRuntime
              (State: θ, v, voltages, ray geometries)
              [NEVER depends on CSS / display dimensions]
                                 │
                                 ▼
                     FigureViewport / Host
                                 │
             ┌───────────────────┴───────────────────┐
             │                                       │
     ResizeObserver                     Uniform Contain Mapper
  (Watches local container)             (scale = min(W/Sw, H/Sh))
             │                                       │
             └───────────────────┬───────────────────┘
                                 │
                                 ▼
                         CoordinateMapper
             (renderedImageRect: left, top, width, height)
                                 │
             ┌───────────────────┴───────────────────┐
             ▼                                       ▼
    Textbook Image <img>                   Simulation Overlay <div>
  [Shared left/top/w/h]                  [Shared left/top/w/h]
             │                                       │
             └───────────────────┬───────────────────┘
                                 │
                                 ▼
                           RenderContext
                 { toScreen, toSource, toOverlay, scale }
                                 │
                                 ▼
                          Domain Renderers
                    (Mechanics, Optics, Circuits)
               [All draw using unified RenderContext]
```

---

## 3. Permanent Architectural Rules

### Rule 1: Source Image Native Coordinates Are Authoritative
Native image dimensions (`image.naturalWidth`, `image.naturalHeight` or explicit scene metadata) are the permanent ground truth. Coordinates stored in scene files must be in native source pixels. Never store CSS pixels, browser percentages, or viewport-derived coordinates in persistent scene definitions.

### Rule 2: Physics State Never Depends on CSS Size
The simulation state ($\theta$, $\omega$, charges, node voltages, ray intersections) lives purely in source/physical units. Changing CSS width, collapsing a sidebar, or rotating a tablet alters only the display projection matrix, never the physical state.

### Rule 3: Only the Mapping/Render Layer Converts Coordinates
Solvers compute exclusively in source space. The `CoordinateMapper` (via `FigureViewport`) provides the one authoritative projection:
$$\text{scale} = \min\left(\frac{\text{viewportWidth}}{\text{sourceWidth}}, \frac{\text{viewportHeight}}{\text{sourceHeight}}\right)$$
$$\text{offsetX} = \frac{\text{viewportWidth} - (\text{sourceWidth} \times \text{scale})}{2}$$
$$\text{offsetY} = \frac{\text{viewportHeight} - (\text{sourceHeight} \times \text{scale})}{2}$$

Forward transform:
$$\text{displayX} = \text{offsetX} + (\text{sourceX} \times \text{scale})$$
$$\text{displayY} = \text{offsetY} + (\text{sourceY} \times \text{scale})$$

Inverse transform:
$$\text{sourceX} = \frac{\text{displayX} - \text{offsetX}}{\text{scale}}$$
$$\text{sourceY} = \frac{\text{displayY} - \text{offsetY}}{\text{scale}}$$

### Rule 4: Pointer Input Must Convert Back to Source Coordinates
Any drag, click, or touch event on an overlay element must be transformed through `mapper.domEventToSource(event)` before modifying physics parameters.

### Rule 5: Image and Overlay Share Exactly One Rectangle
The diagram `<img>` and simulation overlay container must share the identical bounding box (`renderedImageRect`). Symmetrical letterbox/pillarbox padding must apply to both elements identically.

### Rule 6: Container Resize Is Observed Directly
Every interactive figure must use a `ResizeObserver` attached to its viewport container element. Window resize listeners alone are prohibited because UI container transitions (drawer open/close, split-screen) occur without window resizing.

### Rule 7: Frontend Redesigns Must Not Change Simulation Geometry
If the surrounding page is redesigned (e.g., migrating from sidebar to bottom controls or mobile drawer), mounting `FigureViewport` into the new DOM container will automatically preserve 100% pixel-accurate diagram registration without editing a single line of physics code.

### Rule 8: Domain Renderers Do Not Independently Invent Scaling
All domain adapters (`MechanicsAdapter`, `OpticsAdapter`, `CircuitAdapter`) receive the unified `RenderContext` and must use its transform rather than calculating ad-hoc scale factors.

---

## 4. Verification & Precision Benchmark

The system has been verified using deterministic fixture tests (`tests/unit/test_figure_viewport_fixtures.js`) simulating realistic responsive viewport scenarios:

| Scenario / Breakpoint | Viewport Dimensions | Native Source Dimensions | Contain Scale | Max Registration Error | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Large Desktop (Sidebar Closed)** | $1440 \times 900\text{ px}$ | $800 \times 600\text{ px}$ | $1.5000\times$ | **$0.0000\text{ px}$** | **PASS** |
| **2. Large Desktop (Sidebar Open)** | $650 \times 900\text{ px}$ | $800 \times 600\text{ px}$ | $0.8125\times$ | **$0.0000\text{ px}$** | **PASS** |
| **3. Standard Laptop Screen** | $1024 \times 768\text{ px}$ | $800 \times 600\text{ px}$ | $1.2800\times$ | **$0.0000\text{ px}$** | **PASS** |
| **4. Tablet Portrait Layout** | $768 \times 1024\text{ px}$ | $800 \times 600\text{ px}$ | $0.9600\times$ | **$0.0000\text{ px}$** | **PASS** |
| **5. Compact Mobile Breakpoint** | $390 \times 844\text{ px}$ | $800 \times 600\text{ px}$ | $0.4875\times$ | **$0.0000\text{ px}$** | **PASS** |
| **Dynamic Sidebar Transition** | $1440 \to 650 \to 1440\text{ px}$ | $800 \times 600\text{ px}$ | Dynamic | **$0.0000\text{ px}$** drift | **PASS** |

Total Assertions: **375 passed, 0 failed**.

---

## 5. Domain Anchors Calibration Reference

To inspect sub-pixel alignment at runtime, enable developer anchors via the UI button (`🎯 Anchors (0px)`) or `viewport.setInspectAnchors(true)`.

### 5.1 Mechanics (Pendulum)
* **Pivot**: Stored at $(x=468.0, y=99.7)$ on `test1.jpg`.
* **Bob Center**: Stored at $(x=246.6, y=527.6)$.
* **Invariant**: Bob moves along circular arc of constant source length $L = 478.4\text{ px}$ regardless of viewport scaling.

### 5.2 Optics (Thin Lens / Mirror)
* **Optical Center ($O$)**: Stored at $(x=400.0, y=300.0)$ on canonical lens.
* **Focal Points ($F_1, F_2$)**: Stored symmetrically at $O \pm f$.
* **Invariant**: Light rays pass through optical center and focal points without angular distortion.

### 5.3 Circuits (NCTB Schematics)
* **Circuit 1**: $484 \times 399\text{ px}$
* **Circuit 2**: $878 \times 593\text{ px}$ (Rails at $y=99, 502$; branches at $x=138, 436, 734$)
* **Circuit 3**: $529 \times 273\text{ px}$ (7-resistor mesh with 6 voltage probes)
* **Circuit 4**: $1272 \times 581\text{ px}$ (Ladder network with rails at $y=133, 478$; columns at $x=281, 800, 910$)
* **Invariant**: Wire paths and current particles track exactly along the black schematic lines of the textbook illustration.
