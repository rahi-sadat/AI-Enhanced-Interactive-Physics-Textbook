/**
 * tests/unit/test_interactive_rendering.js
 * 
 * PR-03 Milestone Acceptance Test Suite:
 * Source-Aligned Interactive Rendering & Bidirectional Manipulation.
 * 
 * Verifies that for any supported optics or DC circuit diagram:
 * 1. Scene recognition & automatic renderer resolution (RendererRegistry)
 * 2. Source-aligned simulation overlay without synthetic replacement canvas
 * 3. Principal-ray tracing for thin lens and spherical mirror
 * 4. Direct manipulation: object horizontal drag -> objectDistance -> MNA/lens solve -> rays/image
 * 5. Direct manipulation: vertical tip drag -> objectHeight -> proportional image resize
 * 6. 1:1 bidirectional lockstep between pointer manipulation, parameters, and telemetry
 * 7. DC circuit switch toggle -> MNA re-solve -> current halts/resumes
 * 8. DC circuit component parameter change -> MNA re-solve -> currents/voltages update
 * 9. Genericity proof: multiple distinct diagrams of same subtype work with 0 code changes
 * 10. Responsive layout invariance & sub-pixel coordinate mapping
 * 11. Zero diagram-specific coordinate constants in renderers
 * 12. Strict architectural boundary: renderers never solve physics; engine never imports apps/
 */

import { PhysicsRuntime } from '../../engine/core/PhysicsRuntime.js';
import { CoordinateMapper } from '../../engine/core/coordinateMapper.js';
import { defaultRendererRegistry } from '../../apps/web/src/features/simulations/core/RendererRegistry.js';
import { OpticsRenderer } from '../../apps/web/src/features/simulations/optics/OpticsRenderer.js';
import { CircuitRenderer } from '../../apps/web/src/features/simulations/circuits/CircuitRenderer.js';
import { CircuitCompiler } from '../../engine/circuits/CircuitCompiler.js';
import { MissingCalibrationError } from '../../engine/core/errors.js';
import { defaultCapabilityRegistry } from '../../engine/core/capabilities.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '../../');

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ PASS: ${message}`);
  } else {
    failed++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

function assertClose(actual, expected, tol = 0.05, message = '') {
  const diff = Math.abs(actual - expected);
  assert(diff <= tol, `${message} (diff: ${diff.toFixed(4)}, tol: ${tol}, actual: ${actual.toFixed(2)}, expected: ${expected.toFixed(2)})`);
}

// Minimal DOM mock for Node.js test environment
class MockElement {
  constructor(tagName = 'div', namespace = null) {
    this.tagName = tagName;
    this.namespace = namespace;
    this.attributes = {};
    this.style = {};
    this.children = [];
    this.listeners = {};
    this._innerHTML = '';
  }

  setAttribute(k, v) {
    this.attributes[k] = String(v);
  }

  getAttribute(k) {
    return this.attributes[k] || null;
  }

  appendChild(child) {
    child.parent = this;
    this.children.push(child);
    return child;
  }

  removeChild(child) {
    const idx = this.children.indexOf(child);
    if (idx !== -1) this.children.splice(idx, 1);
    child.parent = null;
    return child;
  }

  remove() {
    if (this.parent) {
      this.parent.removeChild(this);
    }
  }

  addEventListener(event, fn) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(fn);
  }

  removeEventListener(event, fn) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== fn);
  }

  dispatchEvent(event) {
    const cbs = this.listeners[event.type] || [];
    for (const cb of cbs) cb(event);
  }

  getBoundingClientRect() {
    return { left: 0, top: 0, width: 800, height: 600 };
  }

  getContext() {
    return new Proxy({}, { get: () => () => {} });
  }

  set innerHTML(html) {
    this._innerHTML = html;
    this.children = [];
  }

  get innerHTML() {
    return this._innerHTML;
  }
}

if (typeof globalThis.document === 'undefined') {
  globalThis.document = {
    createElement(tag) { return new MockElement(tag); },
    createElementNS(ns, tag) { return new MockElement(tag, ns); }
  };
}

if (typeof globalThis.window === 'undefined') {
  globalThis.window = {
    addEventListener(event, fn) {},
    removeEventListener(event, fn) {}
  };
}

if (typeof globalThis.requestAnimationFrame === 'undefined') {
  globalThis.requestAnimationFrame = (cb) => setTimeout(cb, 16);
  globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
}

if (typeof globalThis.ResizeObserver === 'undefined') {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

console.log('===================================================================');
console.log('  RUNNING PR-03 SOURCE-ALIGNED INTERACTIVE RENDERING TEST SUITE');
console.log('===================================================================\n');

async function runTests() {
  // -----------------------------------------------------------------
  // 1. RENDERER REGISTRY & AUTOMATIC RESOLUTION
  // -----------------------------------------------------------------
  console.log('[1/10] Verifying RendererRegistry automatic subtype & domain resolution:');
  {
    assert(defaultRendererRegistry.has('optics', 'thin_lens'), 'RendererRegistry has optics/thin_lens');
    assert(defaultRendererRegistry.has('optics', 'spherical_mirror'), 'RendererRegistry has optics/spherical_mirror');
    assert(defaultRendererRegistry.has('optics', 'interface_refraction'), 'RendererRegistry has optics/interface_refraction');
    assert(defaultRendererRegistry.has('optics', 'prism'), 'RendererRegistry has optics/prism');
    assert(defaultRendererRegistry.has('circuits', 'dc'), 'RendererRegistry has circuits/dc');
    assert(defaultRendererRegistry.has('circuits', 'series_parallel'), 'RendererRegistry handles legacy subtype series_parallel');

    const lensRenderer = defaultRendererRegistry.resolve({ domain: 'optics', subtype: 'thin_lens' });
    assert(lensRenderer instanceof OpticsRenderer, 'Resolved optics renderer is instance of OpticsRenderer');

    const circRenderer = defaultRendererRegistry.resolve({ domain: 'circuits', subtype: 'dc' });
    assert(circRenderer instanceof CircuitRenderer, 'Resolved circuit renderer is instance of CircuitRenderer');

    let unsupportedRejected = false;
    try {
      defaultRendererRegistry.resolve({ domain: 'acoustics', subtype: 'sonar' });
    } catch (e) {
      unsupportedRejected = true;
    }
    assert(unsupportedRejected, 'Unsupported domain cleanly rejected by RendererRegistry');
  }

  // -----------------------------------------------------------------
  // 2. OPTICS: THIN LENS BIDIRECTIONAL DIRECT MANIPULATION
  // -----------------------------------------------------------------
  console.log('\n[2/10] Verifying Thin Lens principal rays, direct dragging, and bidirectional lockstep:');
  {
    const sceneLensA = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-001',
      domain: 'optics',
      subtype: 'thin_lens',
      title: 'Thin Convex Lens Ray Tracing',
      coordinateSpace: {
        type: 'source_px',
        width: 800,
        height: 600,
        bounds: { xMin: 0, xMax: 800, yMin: 0, yMax: 600 }
      },
      geometry: {
        lensX: 400,
        axisY: 300,
        sourceWidth: 800,
        sourceHeight: 600
      },
      parameters: {
        focalLength: {
          value: 130.0,
          unit: 'px',
          editable: true,
          provenance: 'observed',
          source: 'textbook_exercise'
        },
        objectDistance: {
          value: 260.0,
          unit: 'px',
          editable: true,
          provenance: 'observed',
          source: 'diagram_measurement'
        },
        objectHeight: {
          value: -80.0,
          unit: 'px',
          editable: true,
          provenance: 'observed',
          source: 'diagram_measurement'
        }
      },
      visual: {
        background_url: '/scenes/optics/nctb_lens_diagram.png'
      }
    };

    const runtime = new PhysicsRuntime();
    const mockContainer = new MockElement('div');
    await runtime.load(sceneLensA, mockContainer);

    let output = runtime.getOutput();
    assert(output !== null, 'Runtime successfully loaded thin lens scene and produced output');
    assert(output.geometry !== undefined, 'Runtime output includes solved geometry');

    // 2a. Verify solved geometry landmarks & 3 principal rays
    const geom = output.geometry;
    assert(geom.opticalAxis.y === 300, 'Optical axis y-position is 300 source px');
    assert(geom.landmarks.lensCenter.x === 400 && geom.landmarks.lensCenter.y === 300, 'Optical center O is at (400, 300)');
    assertClose(geom.landmarks.focalPoints[0].x, 270, 0.01, 'Front focus F1 is at x=270 (400 - 130)');
    assertClose(geom.landmarks.focalPoints[1].x, 530, 0.01, 'Back focus F2 is at x=530 (400 + 130)');
    assert(geom.rays.length === 3, 'Output includes all 3 principal rays');
    assert(geom.image !== null, 'Output includes resultant image arrow');
    assertClose(geom.image.base.x, 660, 0.01, 'Initial real image formed at x=660 (400 + 260)');
    assertClose(geom.image.tip.y, 380, 0.01, 'Initial image is inverted with height +80');
    assertClose(output.telemetry.magnification, -1.0, 0.01, 'Initial magnification is -1.0');

    // 2b. Simulate Horizontal Object Drag: pointer x moves from 140 to 220
    // Relative distance to lens changes from 260 to 180 (closer to focal point)
    console.log('  -> Simulating horizontal pointer drag: objectDistance 260px -> 180px');
    runtime.updateParameter({
      targetId: 'object_main',
      key: 'objectDistance',
      value: 180.0,
      unit: 'px'
    });

    output = runtime.getOutput();
    // Theoretical 1/v = 1/f - 1/u = 1/130 - 1/180 = (180 - 130)/(130 * 180) = 50 / 23400 => v = 468.0px
    const expectedV = (180 * 130) / (180 - 130); // 468.0
    const expectedMagnification = -expectedV / 180.0; // -2.6
    assertClose(output.telemetry.imageDistance, expectedV, 0.1, `Image distance recalculated to ${expectedV.toFixed(1)}px`);
    assertClose(output.telemetry.magnification, expectedMagnification, 0.05, `Magnification updated to ${expectedMagnification.toFixed(2)}`);
    assertClose(output.geometry.image.base.x, 400 + expectedV, 0.1, 'Image arrow base moved to new position');
    const hasRays = output.geometry.rays.length > 0 && (output.geometry.rays[0].points || output.geometry.rays[0].segments);
    assert(Boolean(hasRays), 'Principal ray 1 re-traced through focus');

    // Verify provenance transitioned to 'student'
    assert(output.editableParameters.objectDistance.provenance === 'student', 'Modified parameter provenance is "student"');

    // 2c. Simulate Vertical Tip Drag: objectHeight -80px -> -40px
    console.log('  -> Simulating vertical arrow-tip drag: objectHeight -80px -> -40px');
    runtime.updateParameter({
      targetId: 'object_main',
      key: 'objectHeight',
      value: -40.0,
      unit: 'px'
    });

    output = runtime.getOutput();
    const expectedImageHeight = -40.0 * expectedMagnification; // +104.0
    assertClose(output.geometry.image.tip.y - output.geometry.image.base.y, expectedImageHeight, 0.1, 'Image height resized in proportion to tip drag');

    // 2d. Simulate Parameter Slider Update: focalLength 130px -> 100px
    console.log('  -> Simulating sidebar slider update: focalLength 130px -> 100px');
    runtime.updateParameter({
      targetId: 'focalLength',
      key: 'focalLength',
      value: 100.0,
      unit: 'px'
    });

    output = runtime.getOutput();
    assertClose(output.geometry.landmarks.focalPoints[0].x, 300, 0.01, 'Front focal point updated to x=300 (400 - 100)');
    assertClose(output.geometry.landmarks.focalPoints[1].x, 500, 0.01, 'Back focal point updated to x=500 (400 + 100)');

    // 2e. Verify Reset Restores Complete Initial State
    console.log('  -> Verifying Reset restores original parameters and geometry');
    runtime.reset();
    output = runtime.getOutput();
    assertClose(output.geometry.landmarks.focalPoints[0].x, 270, 0.01, 'Focal point restored to x=270');
    assertClose(output.geometry.image.base.x, 660, 0.01, 'Image position restored to x=660');
    assertClose(output.telemetry.magnification, -1.0, 0.01, 'Magnification restored to -1.0');
    assert(output.editableParameters.objectDistance.value === 260.0, 'Object distance restored to 260px');
  }

  // -----------------------------------------------------------------
  // 3. OPTICS GENERICITY: DIFFERENT LENS DIAGRAM (ZERO CODE CHANGES)
  // -----------------------------------------------------------------
  console.log('\n[3/10] Verifying Optics Genericity: completely different lens diagram works with 0 code changes:');
  {
    const sceneLensB = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-002-DIFFERENT',
      domain: 'optics',
      subtype: 'thin_lens',
      title: 'Different Textbook Lens Diagram',
      coordinateSpace: {
        type: 'source_px',
        width: 1200,
        height: 900,
        bounds: { xMin: 0, xMax: 1200, yMin: 0, yMax: 900 }
      },
      geometry: {
        lensX: 650,
        axisY: 450,
        sourceWidth: 1200,
        sourceHeight: 900
      },
      parameters: {
        focalLength: { value: 200.0, unit: 'px' },
        objectDistance: { value: 400.0, unit: 'px' },
        objectHeight: { value: -120.0, unit: 'px' }
      },
      visual: {
        background_url: '/scenes/optics/lens_alt.png'
      }
    };

    const runtimeB = new PhysicsRuntime();
    await runtimeB.load(sceneLensB, new MockElement('div'));
    const outputB = runtimeB.getOutput();

    // 1/v = 1/200 - 1/400 = 1/400 => v = 400px. Image base = 650 + 400 = 1050
    assert(outputB !== null, 'Different lens diagram loaded without errors');
    assertClose(outputB.geometry.landmarks.lensCenter.x, 650, 0.01, 'Lens center correctly extracted as 650');
    assertClose(outputB.geometry.opticalAxis.y, 450, 0.01, 'Optical axis y correctly extracted as 450');
    assertClose(outputB.geometry.image.base.x, 1050, 0.1, 'Real image base formed at x=1050 (650 + 400)');
    assertClose(outputB.telemetry.magnification, -1.0, 0.01, 'Magnification is -1.0 for symmetric 2f object distance');
  }

  // -----------------------------------------------------------------
  // 4. OPTICS: SPHERICAL MIRROR SIMULATION
  // -----------------------------------------------------------------
  console.log('\n[4/10] Verifying Spherical Mirror simulation:');
  {
    const mirrorScene = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-MIRROR',
      domain: 'optics',
      subtype: 'spherical_mirror',
      title: 'Concave Spherical Mirror',
      coordinateSpace: {
        type: 'source_px',
        width: 800,
        height: 600
      },
      geometry: {
        poleX: 600,
        axisY: 300,
        curvatureRadius: 300,
        isConcave: true
      },
      parameters: {
        focalLength: { value: 150.0, unit: 'px' },
        objectDistance: { value: 300.0, unit: 'px' },
        objectHeight: { value: -60.0, unit: 'px' }
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(mirrorScene, new MockElement('div'));
    const output = runtime.getOutput();

    assert(output !== null, 'Mirror scene loaded successfully');
    assert(output.geometry.mirror !== undefined, 'Mirror geometry exposed');
    assertClose(output.geometry.landmarks.pole.x, 600, 0.01, 'Pole P is at x=600');
    assertClose(output.geometry.landmarks.focus.x, 450, 0.01, 'Focus F is at x=450 (600 - 150)');
    assertClose(output.geometry.landmarks.center.x, 300, 0.01, 'Center of curvature C is at x=300 (600 - 300)');
    assert(output.geometry.rays.length >= 2, 'Principal incident and reflected rays generated');
    assertClose(output.telemetry.imageDistance, 300, 0.1, 'Real image forms at center of curvature (300px)');
  }

  // -----------------------------------------------------------------
  // 5. OPTICS: INTERFACE REFRACTION & PRISM
  // -----------------------------------------------------------------
  console.log('\n[5/10] Verifying Interface Refraction & Prism simulation:');
  {
    const refractionScene = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-REFRACT',
      domain: 'optics',
      subtype: 'interface_refraction',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        n1: { value: 1.0 },
        n2: { value: 1.5 },
        theta1: { value: 30.0, unit: 'deg' }
      },
      geometry: {
        interfaceY: 300,
        normalX: 400
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(refractionScene, new MockElement('div'));
    let out = runtime.getOutput();

    // theta2 = arcsin(1.0 * sin(30) / 1.5) = arcsin(0.5 / 1.5) = 19.47 deg
    assert(out !== null, 'Refraction scene loaded');
    assertClose(out.telemetry.refractedAngle_deg, 19.47, 0.05, 'Refracted angle matches Snell\'s Law (19.47 deg)');
    assert(out.geometry.rays.some(r => r.id === 'refracted_ray'), 'Geometry contains refracted ray');

    // Total Internal Reflection (TIR) scenario: n1 = 1.5, n2 = 1.0, theta1 = 50 deg > theta_c (41.81 deg)
    runtime.updateParameter({ targetId: 'n1', key: 'n1', value: 1.5 });
    runtime.updateParameter({ targetId: 'n2', key: 'n2', value: 1.0 });
    runtime.updateParameter({ targetId: 'theta1', key: 'theta1', value: 50.0 });
    out = runtime.getOutput();
    assert(out.telemetry.tir === true, 'Total internal reflection flagged correctly');
    assert(out.geometry.rays.some(r => r.id === 'reflected_ray'), 'Reflected ray emitted during TIR');

    // Prism scene
    const prismScene = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-PRISM',
      domain: 'optics',
      subtype: 'prism',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        refractiveIndex: { value: 1.52 },
        apexAngle: { value: 60.0 },
        incidentAngle: { value: 45.0 }
      },
      geometry: {
        vertices: [
          { x: 250, y: 450 },
          { x: 400, y: 150 },
          { x: 550, y: 450 }
        ],
        rayOrigin: { x: 100, y: 350 },
        rayDirection: { x: 1, y: 0 }
      }
    };

    const prismRuntime = new PhysicsRuntime();
    await prismRuntime.load(prismScene, new MockElement('div'));
    const prismOut = prismRuntime.getOutput();
    assert(prismOut.geometry.prismPolygon !== undefined, 'Prism polygon geometry preserved');
    assert(prismOut.geometry.rays.length >= 3, 'Incident, internal, and emergent rays traced through prism');
  }

  // -----------------------------------------------------------------
  // 6. CIRCUITS: GRAPH-DRIVEN DC MNA SIMULATION & SWITCH INTERACTION
  // -----------------------------------------------------------------
  console.log('\n[6/10] Verifying Circuit graph-driven MNA solve, switch toggle, and parameter edits:');
  {
    const circuitScene = {
      schemaVersion: '1.0',
      id: 'PHY-CIRC-001',
      domain: 'circuits',
      subtype: 'dc',
      title: 'DC Series Circuit',
      coordinateSpace: { type: 'source_px', width: 800, height: 500 },
      parameters: {
        V1: { value: 12.0, unit: 'V' },
        R1: { value: 10.0, unit: 'Ω' },
        R2: { value: 20.0, unit: 'Ω' }
      },
      visual: {
        background_url: '/scenes/circuits/textbook_circuit_diagram.svg'
      },
      circuit: {
        reference_node: 'N0',
        nodes: [
          { id: 'N0', reference: true, label: 'GND' },
          { id: 'N1', reference: false, label: 'N1' },
          { id: 'N1b', reference: false, label: 'N1b' },
          { id: 'N2', reference: false, label: 'N2' }
        ],
        components: [
          {
            id: 'V1',
            type: 'voltage_source',
            value: 12.0,
            unit: 'V',
            nodes: ['N1', 'N0'],
            terminals: [{ id: 'V1.p', node: 'N1', source_px: [140, 230] }, { id: 'V1.n', node: 'N0', source_px: [140, 270] }],
            geometry: { center_source_px: [140, 250] }
          },
          {
            id: 'S1',
            type: 'switch',
            state: 'closed',
            nodes: ['N1', 'N1b'],
            terminals: [{ id: 'S1.a', node: 'N1', source_px: [200, 120] }, { id: 'S1.b', node: 'N1b', source_px: [260, 120] }],
            geometry: { center_source_px: [230, 120], bbox_source_px: [195, 100, 265, 140] }
          },
          {
            id: 'R1',
            type: 'resistor',
            value: 10.0,
            unit: 'Ω',
            nodes: ['N1b', 'N2'],
            terminals: [{ id: 'R1.1', node: 'N1b', source_px: [340, 120] }, { id: 'R1.2', node: 'N2', source_px: [460, 120] }],
            geometry: { center_source_px: [400, 120] }
          },
          {
            id: 'R2',
            type: 'resistor',
            value: 20.0,
            unit: 'Ω',
            nodes: ['N2', 'N0'],
            terminals: [{ id: 'R2.1', node: 'N2', source_px: [660, 200] }, { id: 'R2.2', node: 'N0', source_px: [660, 300] }],
            geometry: { center_source_px: [660, 250] }
          }
        ],
        wires: [
          { id: 'w1', from: 'V1.p', to: 'S1.a', path_source_px: [[140, 230], [140, 120], [200, 120]] },
          { id: 'w2', from: 'S1.b', to: 'R1.1', path_source_px: [[260, 120], [340, 120]] },
          { id: 'w3', from: 'R1.2', to: 'R2.1', path_source_px: [[460, 120], [660, 120], [660, 200]] },
          { id: 'w4', from: 'R2.2', to: 'V1.n', path_source_px: [[660, 300], [660, 380], [140, 380], [140, 270]] }
        ]
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(circuitScene, new MockElement('div'));

    // 6a. Initial MNA Solve: R_total = 10 + 20 = 30 ohm => I = 12 / 30 = 0.4 A
    let output = runtime.getOutput();
    assert(output !== null, 'Circuit loaded and solved by MNA');
    assertClose(output.telemetry.totalCurrent_A, 0.4, 0.001, 'Initial total loop current is 0.400 A (12V / 30Ω)');
    assertClose(output.telemetry.nodeVoltages.N1, 12.0, 0.001, 'Node N1 voltage is 12.0 V');
    assertClose(output.telemetry.nodeVoltages.N2, 8.0, 0.001, 'Node N2 voltage is 8.0 V (across R2=20Ω)');

    // Verify wire geometry carries current for animation
    const wireGeom = output.geometry.wires;
    assert(wireGeom.length === 4, 'Geometry contains 4 wire paths');
    assertClose(wireGeom[0].current_A, 0.4, 0.001, 'Wire w1 current is 0.4 A');

    // 6b. Direct Manipulation: Click Switch S1 to OPEN (closed: false)
    console.log('  -> Simulating switch S1 click to OPEN: closed=false');
    runtime.updateParameter({
      targetId: 'S1',
      key: 'closed',
      value: false
    });

    output = runtime.getOutput();
    assertClose(output.telemetry.totalCurrent_A, 0.0, 0.0001, 'Current immediately halts to 0.0 A when switch opens');
    assert(output.geometry.switches[0].state === 'open', 'Switch visual geometry state is "open"');
    assertClose(output.geometry.wires[0].current_A, 0.0, 0.0001, 'Wire current is 0.0 A (current animation halts)');

    // 6c. Click Switch S1 to CLOSE (closed: true)
    console.log('  -> Simulating switch S1 click to CLOSE: closed=true');
    runtime.updateParameter({
      targetId: 'S1',
      key: 'closed',
      value: true
    });

    output = runtime.getOutput();
    assertClose(output.telemetry.totalCurrent_A, 0.4, 0.001, 'Current resumes to 0.4 A when switch is closed');
    assert(output.geometry.switches[0].state === 'closed', 'Switch visual geometry state is "closed"');

    // 6d. Parameter Edit: Change R1 from 10 ohm to 20 ohm
    // New R_total = 20 + 20 = 40 ohm => I = 12 / 40 = 0.3 A
    console.log('  -> Simulating sidebar edit: R1 resistance 10Ω -> 20Ω');
    runtime.updateParameter({
      targetId: 'R1',
      key: 'resistance',
      value: 20.0,
      unit: 'ohm'
    });

    output = runtime.getOutput();
    assertClose(output.telemetry.totalCurrent_A, 0.3, 0.001, 'Loop current recalculated to 0.300 A (12V / 40Ω)');
    assertClose(output.telemetry.nodeVoltages.N2, 6.0, 0.001, 'Node N2 voltage recalculated to 6.0 V');
    assertClose(output.geometry.wires[0].current_A, 0.3, 0.001, 'Wire w1 current updated to 0.3 A');

    // 6e. Reset restores initial circuit values
    runtime.reset();
    output = runtime.getOutput();
    assertClose(output.telemetry.totalCurrent_A, 0.4, 0.001, 'Reset restores loop current to 0.400 A');
    assert(output.geometry.switches[0].state === 'closed', 'Reset restores switch to closed state');
  }

  // -----------------------------------------------------------------
  // 7. CIRCUIT GENERICITY: DIFFERENT TOPOLOGY (3 RESISTORS PARALLEL)
  // -----------------------------------------------------------------
  console.log('\n[7/10] Verifying Circuit Genericity: arbitrary topology (series-parallel 3 resistors):');
  {
    const parallelScene = {
      schemaVersion: '1.0',
      id: 'PHY-CIRC-002-PARALLEL',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [
          { id: 'N0', reference: true },
          { id: 'N1', reference: false },
          { id: 'N2', reference: false }
        ],
        components: [
          { id: 'V1', type: 'voltage_source', value: 10.0, nodes: ['N1', 'N0'], terminals: [{ id: 'V1.p', node: 'N1', source_px: [100, 200] }, { id: 'V1.n', node: 'N0', source_px: [100, 400] }] },
          { id: 'R1', type: 'resistor', value: 5.0, nodes: ['N1', 'N2'], terminals: [{ id: 'R1.1', node: 'N1', source_px: [200, 150] }, { id: 'R1.2', node: 'N2', source_px: [300, 150] }] },
          { id: 'R2', type: 'resistor', value: 10.0, nodes: ['N2', 'N0'], terminals: [{ id: 'R2.1', node: 'N2', source_px: [400, 150] }, { id: 'R2.2', node: 'N0', source_px: [400, 350] }] },
          { id: 'R3', type: 'resistor', value: 10.0, nodes: ['N2', 'N0'], terminals: [{ id: 'R3.1', node: 'N2', source_px: [550, 150] }, { id: 'R3.2', node: 'N0', source_px: [550, 350] }] }
        ],
        wires: [
          { id: 'w1', from: 'V1.p', to: 'R1.1', path_source_px: [[100, 200], [100, 150], [200, 150]] }
        ]
      }
    };

    // Parallel R2 || R3 = (10 * 10) / (10 + 10) = 5 ohm
    // Total R = R1 + 5 = 5 + 5 = 10 ohm
    // Total I = 10V / 10 ohm = 1.0 A
    // Node N2 = 5.0 V
    const runtime = new PhysicsRuntime();
    await runtime.load(parallelScene, new MockElement('div'));
    const output = runtime.getOutput();

    assert(output !== null, 'Parallel topology loaded and solved with zero solver/renderer code changes');
    assertClose(output.telemetry.totalCurrent_A, 1.0, 0.001, 'Total current is 1.000 A');
    assertClose(output.telemetry.nodeVoltages.N2, 5.0, 0.001, 'Junction node N2 voltage is 5.0 V');
  }

  // -----------------------------------------------------------------
  // 8. RENDERER DOM/SVG MOUNTING & RUNTIMEOUTPUT CONSUMPTION
  // -----------------------------------------------------------------
  console.log('\n[8/10] Verifying OpticsRenderer and CircuitRenderer DOM/SVG mounting & rendering:');
  {
    const mapper = new CoordinateMapper(800, 600, 800, 600);
    const container = new MockElement('div');

    const opticsRenderer = new OpticsRenderer();
    let interactCaptured = null;
    opticsRenderer.mount({
      container,
      scene: { subtype: 'thin_lens' },
      coordinateMapper: mapper,
      onInteract: (action) => { interactCaptured = action; }
    });

    opticsRenderer.render({
      subtype: 'thin_lens',
      geometry: {
        lens: { x: 400, axisY: 300 },
        handles: {
          objectArrow: {
            targetId: 'object_main',
            axes: {
              x: {
                parameter: 'objectDistance',
                parameterKey: 'objectDistance',
                editable: true,
                unit: 'px'
              }
            }
          }
        }
      }
    });

    assert(opticsRenderer.svg !== null, 'OpticsRenderer mounted SVG overlay');
    assert(opticsRenderer.layers.rays !== null, 'OpticsRenderer created layer-rays group');
    assert(opticsRenderer.layers.handles !== null, 'OpticsRenderer created layer-handles group');

    // Simulate pointerdown on horizontal drag handle
    const handleEl = new MockElement('rect');
    handleEl.setAttribute('data-handle', 'object_pos');
    opticsRenderer._dragState = {
      type: 'object_pos',
      startX: 140,
      startY: 300,
      initialU: 260,
      initialH: -80,
      lensX: 400,
      axisY: 300,
      isConcave: false,
      hasX: true,
      hasY: false
    };

    // Simulate pointermove to x=220
    const mockPointerMove = { clientX: 220, clientY: 300, preventDefault: () => {} };
    opticsRenderer._handlePointerMove(mockPointerMove);
    assert(interactCaptured !== null, 'Pointer drag triggered onInteract callback');
    assert(interactCaptured.key === 'objectDistance', 'Interaction mapped to "objectDistance"');
    assertClose(interactCaptured.value, 180, 0.1, 'Calculated distance relative to lens is 180 source px');

    opticsRenderer.dispose();
    assert(opticsRenderer.svg === null, 'OpticsRenderer properly disposed');

    // CircuitRenderer mount & render
    const circuitContainer = new MockElement('div');
    const circuitRenderer = new CircuitRenderer();
    let switchInteract = null;
    circuitRenderer.mount({
      container: circuitContainer,
      scene: { subtype: 'dc' },
      coordinateMapper: mapper,
      onInteract: (action) => { switchInteract = action; }
    });

    assert(circuitRenderer.svg !== null, 'CircuitRenderer mounted SVG overlay');
    assert(circuitRenderer.layers.switches !== null, 'CircuitRenderer created layer-switches group');
    assert(circuitRenderer.layers.wires !== null, 'CircuitRenderer created layer-wires group');

    circuitRenderer.dispose();
    assert(circuitRenderer.svg === null, 'CircuitRenderer properly disposed');
  }

  // -----------------------------------------------------------------
  // 9. RESPONSIVE ALIGNMENT & SUB-PIXEL INVARIANCE
  // -----------------------------------------------------------------
  console.log('\n[9/10] Verifying responsive layout invariance across responsive viewports:');
  {
    const viewports = [
      { name: 'Desktop 1440x900', w: 1440, h: 900 },
      { name: 'Tablet 768x1024',  w: 768,  h: 1024 },
      { name: 'Mobile 390x844',   w: 390,  h: 844 }
    ];

    const sourceAnchor = { x: 362.0, y: 240.0 };

    for (const vp of viewports) {
      const mapper = new CoordinateMapper(800, 600, vp.w, vp.h);
      const viewPt = mapper.sourceToView(sourceAnchor.x, sourceAnchor.y);
      const roundTrip = mapper.viewToSource(viewPt.x, viewPt.y);

      assertClose(roundTrip.x, sourceAnchor.x, 0.0001, `[${vp.name}] Round-trip X exact`);
      assertClose(roundTrip.y, sourceAnchor.y, 0.0001, `[${vp.name}] Round-trip Y exact`);
    }
  }

  // -----------------------------------------------------------------
  // 10. NO DIAGRAM-SPECIFIC CONSTANTS IN RENDERERS
  // -----------------------------------------------------------------
  console.log('\n[10/10] Verifying zero diagram-specific positioning constants in renderers:');
  {
    const rendererPaths = [
      'apps/web/src/features/simulations/optics/OpticsRenderer.js',
      'apps/web/src/features/simulations/circuits/CircuitRenderer.js'
    ];

    const forbiddenPatterns = [
      /\b400\b/g, // Specific lens center in NCTB diagram
      /\b260\b/g, // Specific object distance in NCTB diagram
      /\b130\b/g  // Specific focal length in NCTB diagram
    ];

    for (const rel of rendererPaths) {
      const fullPath = path.resolve(rootDir, rel);
      if (!fs.existsSync(fullPath)) continue;
      const content = fs.readFileSync(fullPath, 'utf-8');

      // Check for hardcoded source physics coordinates (excluding SVG styling or default radii like 4, 12, etc.)
      const lines = content.split('\n');
      let hardcodedPhysicsCount = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Skip comment lines
        if (line.trim().startsWith('//') || line.trim().startsWith('*')) continue;

        // Check if line assigns hardcoded source coordinate
        if (/lensX\s*=\s*(400|260|130)/.test(line) || /objectDistance\s*=\s*(400|260|130)/.test(line)) {
          hardcodedPhysicsCount++;
        }
      }

      assert(hardcodedPhysicsCount === 0, `${rel} has 0 hardcoded physics coordinates (reads from runtimeOutput only)`);
    }
  }

  // -----------------------------------------------------------------
  // 11. PHYSICAL UNIT CALIBRATION & HIGH-RES DIAGRAM DRAG (px <-> cm)
  // -----------------------------------------------------------------
  console.log('\n[11/17] Verifying high-res (1600x1200) diagram with physical cm calibration drags correctly:');
  {
    const calibratedScene = {
      schemaVersion: '1.0',
      id: 'PHY-OPT-CALIB-001',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: {
        type: 'source_px',
        width: 1600,
        height: 1200
      },
      calibration: {
        pixels_per_cm: 20.0
      },
      geometry: {
        lensX: 900,
        axisY: 600,
        sourceWidth: 1600,
        sourceHeight: 1200
      },
      parameters: {
        focalLength: {
          value: 15.0,
          unit: 'cm',
          provenance: 'observed'
        },
        objectDistance: {
          value: 30.0,
          unit: 'cm',
          editable: true,
          targetId: 'object_main',
          provenance: 'observed',
          control: { min: 10.0, max: 40.0, step: 0.5 }
        },
        objectHeight: {
          value: -5.0,
          unit: 'cm',
          editable: true,
          targetId: 'object_main',
          provenance: 'observed',
          control: { min: -15.0, max: -1.0, step: 0.5 }
        }
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(calibratedScene, new MockElement('div'));
    let out = runtime.getOutput();

    assert(out !== null, 'Calibrated scene loaded successfully');
    // f = 15 cm * 20 px/cm = 300 px
    // u = 30 cm * 20 px/cm = 600 px -> objectX = 900 - 600 = 300 px
    // 1/v = 1/300 - 1/600 = 1/600 => v = 600 px = 30.0 cm -> imageX = 900 + 600 = 1500 px
    assertClose(out.geometry.landmarks.focalPoints[0].x, 600, 0.01, 'Front focus is at x=600 (900 - 300px)');
    assertClose(out.geometry.landmarks.focalPoints[1].x, 1200, 0.01, 'Back focus is at x=1200 (900 + 300px)');
    assertClose(out.geometry.object.base.x, 300, 0.01, 'Object base is at x=300 (900 - 600px)');
    assertClose(out.geometry.image.base.x, 1500, 0.01, 'Image base is at x=1500 (900 + 600px)');
    assertClose(out.telemetry.objectDistance, 30.0, 0.01, 'Telemetry reports objectDistance in cm (30.0 cm)');
    assertClose(out.telemetry.imageDistance, 30.0, 0.01, 'Telemetry reports imageDistance in cm (30.0 cm)');
    assertClose(out.telemetry.focalLength, 15.0, 0.01, 'Telemetry reports focalLength in cm (15.0 cm)');

    // Verify handle contract declares cm unit and calibration
    const handle = out.geometry.handles?.objectArrow;
    assert(handle !== undefined, 'Handle objectArrow created');
    assert(handle.axes.x.unit === 'cm', 'Handle x-axis declares "cm" unit contract');
    assertClose(handle.axes.x.pixelsPerUnit, 20.0, 0.01, 'Handle x-axis declares pixelsPerUnit = 20.0');
    assert(handle.axes.x.min === 10.0 && handle.axes.x.max === 40.0, 'Handle carries canonical control min/max');

    // Mount OpticsRenderer on 1600x1200 coordinate mapper
    const mapper = new CoordinateMapper(1600, 1200, 800, 600);
    const renderer = new OpticsRenderer();
    let draggedAction = null;
    renderer.mount({
      container: new MockElement('div'),
      scene: calibratedScene,
      coordinateMapper: mapper,
      onInteract: (action) => { draggedAction = action; }
    });
    renderer.render(out);

    // Simulate dragging handle: pointer moves to viewport coordinate corresponding to source_px x = 400
    // Viewport cssX for source x=400 with 1600->800 scaling is cssX = 200
    // uSourcePx = 900 - 400 = 500 px. In cm: 500 / 20 = 25.0 cm.
    renderer._dragState = { type: 'object_pos' };
    renderer._handlePointerMove({ clientX: 200, clientY: 300, preventDefault: () => {} });

    assert(draggedAction !== null, 'Renderer triggered onInteract on calibrated diagram');
    assert(draggedAction.key === 'objectDistance', 'Interaction targeted objectDistance');
    assert(draggedAction.unit === 'cm', 'Interaction sent CANONICAL "cm" unit, NOT pixels!');
    assertClose(draggedAction.value, 25.0, 0.05, 'Physical value correctly converted to 25.0 cm (500px / 20px/cm)');

    // Update runtime with this interaction
    runtime.updateParameter(draggedAction);
    out = runtime.getOutput();

    // 1/v = 1/15 - 1/25 = 2/75 => v = 37.5 cm = 750 px. Image base = 900 + 750 = 1650 px
    assertClose(out.telemetry.objectDistance, 25.0, 0.05, 'Runtime updated objectDistance to 25.0 cm');
    assertClose(out.telemetry.imageDistance, 37.5, 0.1, 'Image distance recalculated to 37.5 cm');
    assertClose(out.geometry.image.base.x, 1650, 0.1, 'Image base moved to 1650 px');

    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 12. ZERO HARDCODED SOURCE-COORDINATE FALLBACKS
  // -----------------------------------------------------------------
  console.log('\n[12/17] Verifying missing required scene geometry throws explicit errors (never defaults to 400, 300, etc.):');
  {
    // 12a. Missing lensX in thin_lens scene
    const missingLensX = {
      schemaVersion: '1.0',
      id: 'MISSING-LENS-X',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { axisY: 300 },
      parameters: { focalLength: { value: 100 }, objectDistance: { value: 200 }, objectHeight: { value: -50 } }
    };
    let threwLensX = false;
    try {
      const rt = new PhysicsRuntime();
      await rt.load(missingLensX, new MockElement('div'));
    } catch (e) {
      threwLensX = e.code === 'MISSING_REQUIRED_PARAMETER' || e.message?.includes('lensX');
    }
    assert(threwLensX, 'Missing lensX throws explicit MissingRequiredParameterError (no synthetic 400)');

    // 12b. Missing axisY in thin_lens scene
    const missingAxisY = {
      schemaVersion: '1.0',
      id: 'MISSING-AXIS-Y',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400 },
      parameters: { focalLength: { value: 100 }, objectDistance: { value: 200 }, objectHeight: { value: -50 } }
    };
    let threwAxisY = false;
    try {
      const rt = new PhysicsRuntime();
      await rt.load(missingAxisY, new MockElement('div'));
    } catch (e) {
      threwAxisY = e.code === 'MISSING_REQUIRED_PARAMETER' || e.message?.includes('axisY');
    }
    assert(threwAxisY, 'Missing axisY throws explicit MissingRequiredParameterError (no synthetic 300)');

    // 12c. Missing mirrorType in spherical_mirror scene
    const missingMirrorType = {
      schemaVersion: '1.0',
      id: 'MISSING-MIRROR-TYPE',
      domain: 'optics',
      subtype: 'spherical_mirror',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { mirrorX: 500, axisY: 300 },
      parameters: { focalLength: { value: 150 }, objectDistance: { value: 300 }, objectHeight: { value: -50 } }
    };
    let threwMirrorType = false;
    try {
      const rt = new PhysicsRuntime();
      await rt.load(missingMirrorType, new MockElement('div'));
    } catch (e) {
      threwMirrorType = e.code === 'MISSING_REQUIRED_PARAMETER' || e.message?.includes('mirrorType');
    }
    assert(threwMirrorType, 'Missing mirrorType throws explicit error (no silent "concave" default)');
  }

  // -----------------------------------------------------------------
  // 13. CANONICAL CONTROL METADATA (min/max/step) CONTROLS DRAG & UI
  // -----------------------------------------------------------------
  console.log('\n[13/17] Verifying canonical param.control.min/max/step strictly governs drag limits:');
  {
    const controlScene = {
      schemaVersion: '1.0',
      id: 'CONTROL-SCENE-001',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 1000, height: 800 },
      geometry: { lensX: 600, axisY: 400, sourceWidth: 1000, sourceHeight: 800 },
      parameters: {
        focalLength: { value: 120.0, unit: 'px' },
        objectDistance: {
          value: 240.0,
          unit: 'px',
          editable: true,
          targetId: 'object_main',
          control: { type: 'slider', min: 50.0, max: 350.0, step: 2.0 }
        },
        objectHeight: {
          value: -80.0,
          unit: 'px',
          editable: true,
          targetId: 'object_main',
          control: { type: 'slider', min: -180.0, max: -20.0, step: 1.0 }
        }
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(controlScene, new MockElement('div'));
    const out = runtime.getOutput();

    const mapper = new CoordinateMapper(1000, 800, 1000, 800);
    const renderer = new OpticsRenderer();
    let lastAction = null;
    renderer.mount({
      container: new MockElement('div'),
      scene: controlScene,
      coordinateMapper: mapper,
      onInteract: (a) => { lastAction = a; }
    });
    renderer.render(out);

    // Drag past max (pointer at x=100 -> uCandidate = 600 - 100 = 500px, but max is 350px)
    renderer._dragState = { type: 'object_pos' };
    renderer._handlePointerMove({ clientX: 100, clientY: 400, preventDefault: () => {} });
    assert(lastAction !== null && lastAction.value === 350.0, `Drag clamped to canonical control.max (350.0), got ${lastAction?.value}`);

    // Drag past min (pointer at x=580 -> uCandidate = 600 - 580 = 20px, but min is 50px)
    renderer._handlePointerMove({ clientX: 580, clientY: 400, preventDefault: () => {} });
    assert(lastAction !== null && lastAction.value === 50.0, `Drag clamped to canonical control.min (50.0), got ${lastAction?.value}`);

    // Tip drag past max (pointer at y=390 -> rawH = -10, but max upward height is -20)
    renderer._dragState = { type: 'object_tip' };
    renderer._handlePointerMove({ clientX: 360, clientY: 395, preventDefault: () => {} });
    assert(lastAction !== null && lastAction.value === -20.0, `Tip drag clamped to control.max (-20.0), got ${lastAction?.value}`);

    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 14. BRANCHED CIRCUIT WIRE CURRENTS ARE TOPOLOGY-CORRECT & DIRECTIONAL
  // -----------------------------------------------------------------
  console.log('\n[14/17] Verifying branched circuit wire currents preserve signed value and branch-specific magnitude:');
  {
    const branchScene = {
      schemaVersion: '1.0',
      id: 'BRANCH-SCENE-001',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [
          { id: 'N0', reference: true },
          { id: 'N1', reference: false }
        ],
        components: [
          {
            id: 'V1',
            type: 'voltage_source',
            value: 12.0,
            nodes: ['N1', 'N0'],
            terminals: [{ id: 'V1.p', node: 'N1', source_px: [100, 200] }, { id: 'V1.n', node: 'N0', source_px: [100, 400] }]
          },
          {
            id: 'R1',
            type: 'resistor',
            value: 10.0,
            nodes: ['N1', 'N0'],
            terminals: [{ id: 'R1.1', node: 'N1', source_px: [300, 200] }, { id: 'R1.2', node: 'N0', source_px: [300, 400] }]
          },
          {
            id: 'R2',
            type: 'resistor',
            value: 20.0,
            nodes: ['N1', 'N0'],
            terminals: [{ id: 'R2.1', node: 'N1', source_px: [500, 200] }, { id: 'R2.2', node: 'N0', source_px: [500, 400] }]
          }
        ],
        wires: [
          { id: 'w_main', from: 'V1.p', to: 'N1', path_source_px: [[100, 200], [100, 100], [200, 100]] },
          { id: 'w_branch1', from: 'N1', to: 'R1.1', path_source_px: [[200, 100], [300, 100], [300, 200]] },
          { id: 'w_branch2', from: 'N1', to: 'R2.1', path_source_px: [[300, 100], [500, 100], [500, 200]] },
          { id: 'w_ret1', from: 'R1.2', to: 'N0', path_source_px: [[300, 400], [300, 500], [200, 500]] },
          { id: 'w_ret2', from: 'R2.2', to: 'N0', path_source_px: [[500, 400], [500, 500], [300, 500]] }
        ]
      }
    };

    // I_R1 = 12 / 10 = 1.20 A
    // I_R2 = 12 / 20 = 0.60 A
    // I_total = 1.80 A
    const runtime = new PhysicsRuntime();
    await runtime.load(branchScene, new MockElement('div'));
    const out = runtime.getOutput();

    const wBranch1 = out.geometry.wires.find(w => w.id === 'w_branch1');
    const wBranch2 = out.geometry.wires.find(w => w.id === 'w_branch2');
    const wMain = out.geometry.wires.find(w => w.id === 'w_main');
    const wRet1 = out.geometry.wires.find(w => w.id === 'w_ret1');
    const wRet2 = out.geometry.wires.find(w => w.id === 'w_ret2');

    assertClose(wBranch1.current_A, 1.20, 0.01, 'Branch 1 wire carries R1 current: 1.20 A');
    assert(wBranch1.direction === 'forward', 'Branch 1 wire flows forward into R1');

    assertClose(wBranch2.current_A, 0.60, 0.01, 'Branch 2 wire carries R2 current: 0.60 A (NOT 1.2A or 1.8A)');
    assert(wBranch2.direction === 'forward', 'Branch 2 wire flows forward into R2');

    assertClose(wMain.current_A, 1.80, 0.01, 'Main feeder wire carries total current: 1.80 A');
    assert(wMain.direction === 'forward', 'Main feeder wire flows forward from V1.p');

    assertClose(wRet1.current_A, 1.20, 0.01, 'Return wire 1 carries R1 return current: 1.20 A');
    assertClose(wRet2.current_A, 0.60, 0.01, 'Return wire 2 carries R2 return current: 0.60 A');
  }

  // -----------------------------------------------------------------
  // 15. MISSING SWITCH GEOMETRY DOES NOT FABRICATE HIT TARGET
  // -----------------------------------------------------------------
  console.log('\n[15/17] Verifying missing switch geometry produces hitTarget: null (no fabricated coordinates):');
  {
    const missingSwitchGeomScene = {
      schemaVersion: '1.0',
      id: 'MISSING-SW-GEOM',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }, { id: 'N2', reference: false }],
        components: [
          { id: 'V1', type: 'voltage_source', value: 5.0, nodes: ['N1', 'N0'], terminals: [{ id: 'V1.p', node: 'N1', source_px: [100, 200] }, { id: 'V1.n', node: 'N0', source_px: [100, 300] }] },
          { id: 'R1', type: 'resistor', value: 50.0, nodes: ['N2', 'N0'] },
          { id: 'S_valid', type: 'switch', state: 'closed', nodes: ['N1', 'N2'], terminals: [{ id: 'S_valid.a', node: 'N1', source_px: [200, 150] }, { id: 'S_valid.b', node: 'N2', source_px: [260, 150] }] },
          { id: 'S_nogeom', type: 'switch', state: 'open', nodes: ['N1', 'N2'] } // Zero terminals, zero center_source_px
        ],
        wires: []
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(missingSwitchGeomScene, new MockElement('div'));
    const out = runtime.getOutput();

    const swValid = out.geometry.switches.find(s => s.id === 'S_valid');
    const swNoGeom = out.geometry.switches.find(s => s.id === 'S_nogeom');

    assert(swValid.hitTarget !== null, 'Valid switch has hitTarget');
    assertClose(swValid.hitTarget.x, 230, 0.01, 'Valid switch hitTarget midpoint x=230');
    assert(swNoGeom.hitTarget === null, 'Switch without geometry evidence has hitTarget === null (ZERO fabrication)');

    // Mount CircuitRenderer and verify NO handle element is created for S_nogeom
    const container = new MockElement('div');
    const renderer = new CircuitRenderer();
    renderer.mount({
      container,
      scene: missingSwitchGeomScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600)
    });
    renderer.render(out);

    const handleElements = renderer.layers.handles.children;
    const nogeomHandle = handleElements.find(el => el.getAttribute('data-target-id') === 'S_nogeom');
    assert(nogeomHandle === undefined, 'Renderer did NOT create any DOM handle for switch lacking geometry evidence');
    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 16. NON-EDITABLE COMPONENTS DO NOT GET CONTROLS
  // -----------------------------------------------------------------
  console.log('\n[16/17] Verifying non-editable components are NOT exposed as editable parameters:');
  {
    const selectiveEditScene = {
      schemaVersion: '1.0',
      id: 'SELECTIVE-EDIT-SCENE',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }, { id: 'N2', reference: false }],
        components: [
          { id: 'V1', type: 'voltage_source', value: 12.0, nodes: ['N1', 'N0'], editable: false }, // Explicitly false
          { id: 'R_locked', type: 'resistor', value: 50.0, nodes: ['N1', 'N2'], editable: false }, // Explicitly false
          { id: 'R_editable', type: 'resistor', value: 100.0, nodes: ['N2', 'N0'], editable: true } // Explicitly true
        ],
        wires: []
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(selectiveEditScene, new MockElement('div'));
    const out = runtime.getOutput();
    const editParams = out.editableParameters || {};

    assert(editParams['R_editable.resistance'] !== undefined, 'R_editable.resistance is exposed in editableParameters');
    assert(editParams['R_locked.resistance'] === undefined, 'R_locked.resistance is NOT exposed');
    assert(editParams['V1.voltage'] === undefined, 'V1.voltage is NOT exposed');
  }

  // -----------------------------------------------------------------
  // 17. REJECTED PARAMETER CHANGES DO NOT DESYNCHRONIZE UI AND RUNTIME
  // -----------------------------------------------------------------
  console.log('\n[17/17] Verifying rejected parameter updates throw, roll back, and preserve runtime authority:');
  {
    const circuitScene = {
      schemaVersion: '1.0',
      id: 'CIRCUIT-REJECT-SCENE',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        R1: { value: 25.0, unit: 'Ω', editable: true }
      },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }],
        components: [
          { id: 'V1', type: 'voltage_source', value: 10.0, nodes: ['N1', 'N0'] },
          { id: 'R1', type: 'resistor', value: 25.0, unit: 'Ω', nodes: ['N1', 'N0'], editable: true }
        ],
        wires: []
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(circuitScene, new MockElement('div'));

    const initialR = runtime.getParameter('R1')?.value;
    assertClose(initialR, 25.0, 0.01, 'Initial R1 is 25.0 Ω');

    // Attempt invalid negative resistance update (-100 Ω)
    let rejected = false;
    let rejectedErrorCode = null;
    try {
      runtime.updateParameter('R1', -100.0);
    } catch (err) {
      rejected = true;
      rejectedErrorCode = err.issues?.[0]?.code || err.code;
    }

    assert(rejected, 'Runtime rejected negative resistance (-100 Ω)');
    assert(rejectedErrorCode === 'NON_POSITIVE_VALUE', `Error code is NON_POSITIVE_VALUE (got ${rejectedErrorCode})`);

    // Verify runtime retained authoritative 25.0 Ω value (NO desynchronization)
    const afterR = runtime.getParameter('R1')?.value;
    assertClose(afterR, 25.0, 0.01, 'Runtime parameter remains exactly 25.0 Ω after rejected update');
    assertClose(runtime.getOutput().telemetry.totalCurrent_A, 0.40, 0.01, 'Solved current remains valid (10V / 25Ω = 0.4A)');
  }

  // -----------------------------------------------------------------
  // 18. PHYSICAL UNITS WITHOUT CALIBRATION MUST FAIL
  // -----------------------------------------------------------------
  console.log('\n[18/23] Verifying physical units without calibration fail explicitly:');
  {
    const uncalibratedScene = {
      schemaVersion: '1.0',
      id: 'UNCALIBRATED-OPTICS',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400, axisY: 300 },
      parameters: {
        focalLength: { value: 15.0, unit: 'cm' }, // Physical unit 'cm' without any calibration!
        objectDistance: { value: 30.0, unit: 'cm' },
        objectHeight: { value: -5.0, unit: 'cm' }
      }
    };

    const runtime = new PhysicsRuntime();
    let threwCalibrationError = false;
    let errorName = '';
    try {
      await runtime.load(uncalibratedScene, new MockElement('div'));
    } catch (err) {
      threwCalibrationError = true;
      errorName = err.name;
    }

    assert(threwCalibrationError, 'Physical unit parameter without calibration threw error');
    assert(errorName === 'MissingCalibrationError', `Error is MissingCalibrationError (got "${errorName}")`);
  }

  // -----------------------------------------------------------------
  // 19. NON-EDITABLE OPTICS PARAMETERS PRODUCE NO HANDLES/CONTROLS
  // -----------------------------------------------------------------
  console.log('\n[19/23] Verifying non-editable optics parameters produce no handles or controls:');
  {
    const nonEditableScene = {
      schemaVersion: '1.0',
      id: 'NON-EDITABLE-OPTICS',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400, axisY: 300, sourceWidth: 800, sourceHeight: 600 },
      parameters: {
        focalLength: { value: 100.0, unit: 'px', editable: false },
        objectDistance: { value: 200.0, unit: 'px', editable: false }, // explicitly false
        objectHeight: { value: -60.0, unit: 'px', editable: false } // explicitly false
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(nonEditableScene, new MockElement('div'));
    const out = runtime.getOutput();

    assert(Object.keys(out.editableParameters || {}).length === 0, 'editableParameters is empty for non-editable scene');
    assert(out.geometry.handles?.objectArrow === undefined, 'No objectArrow handle in geometry for non-editable parameters');

    const container = new MockElement('div');
    const renderer = new OpticsRenderer();
    renderer.mount({
      container,
      scene: nonEditableScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600)
    });
    renderer.render(out);

    assert(renderer.layers.handles.children.length === 0, 'OpticsRenderer rendered ZERO handles for non-editable scene');
    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 20. ARBITRARY OBJECT IDS SURVIVE DRAG BINDING
  // -----------------------------------------------------------------
  console.log('\n[20/23] Verifying arbitrary object IDs survive drag binding:');
  {
    const arbitraryIdScene = {
      schemaVersion: '1.0',
      id: 'ARBITRARY-ID-SCENE',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400, axisY: 300, sourceWidth: 800, sourceHeight: 600 },
      objects: [
        {
          id: 'probe_candle_99',
          type: 'optical_object',
          editable: true,
          optics: { model: 'optical_object', height_px: -70 }
        }
      ],
      parameters: {
        focalLength: { value: 120.0, unit: 'px' },
        'probe_candle_99.objectDistance': { value: 240.0, unit: 'px', editable: true, control: { min: 60, max: 360 } }
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(arbitraryIdScene, new MockElement('div'));
    const out = runtime.getOutput();

    const handle = out.geometry.handles?.objectArrow;
    assert(handle !== undefined, 'Handle objectArrow created for arbitrary object');
    assert(handle.targetId === 'probe_candle_99', `Handle targetId carries actual scene object ID (got "${handle.targetId}")`);
    assert(handle.axes.x.parameter === 'probe_candle_99.objectDistance', `Handle parameter address is "probe_candle_99.objectDistance"`);

    let interactionReceived = null;
    const renderer = new OpticsRenderer();
    renderer.mount({
      container: new MockElement('div'),
      scene: arbitraryIdScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600),
      onInteract: (a) => { interactionReceived = a; }
    });
    renderer.render(out);

    // Simulate drag: pointer at x=200 -> u = 400 - 200 = 200px
    renderer._dragState = { type: 'object_pos' };
    renderer._handlePointerMove({ clientX: 200, clientY: 300, preventDefault: () => {} });

    assert(interactionReceived !== null, 'Interaction triggered by drag');
    assert(interactionReceived.targetId === 'probe_candle_99', `Interaction dispatched targetId "probe_candle_99" (got "${interactionReceived.targetId}")`);
    assert(interactionReceived.address === 'probe_candle_99.objectDistance', 'Interaction dispatched full parameter address');

    // Runtime update using this action must succeed without errors
    runtime.updateParameter(interactionReceived);
    const updatedOut = runtime.getOutput();
    assertClose(updatedOut.telemetry.objectDistance, 200.0, 0.1, 'Runtime parameter updated to 200.0px via arbitrary object ID');
    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 21. REFRACTION WITH MISSING GEOMETRY PRODUCES NO SYNTHETIC OVERLAY
  // -----------------------------------------------------------------
  console.log('\n[21/23] Verifying refraction with missing geometry produces no synthetic overlay:');
  {
    const missingGeomRefractScene = {
      schemaVersion: '1.0',
      id: 'MISSING-GEOM-REFRACT',
      domain: 'optics',
      subtype: 'interface_refraction',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        n1: { value: 1.0 },
        n2: { value: 1.5 },
        theta1: { value: 45.0, unit: 'deg' }
      }
      // Missing geometry.interfaceY/boundary and missing normalX/normal
    };

    let runtimeThrew = false;
    try {
      const runtime = new PhysicsRuntime();
      await runtime.load(missingGeomRefractScene, new MockElement('div'));
    } catch (e) {
      runtimeThrew = true;
    }
    assert(runtimeThrew, 'Missing boundary geometry in interface refraction threw explicit error');

    // If solved headlessly with empty boundary, renderer must produce ZERO synthetic lines
    const mockOutput = {
      domain: 'optics',
      subtype: 'interface_refraction',
      geometry: { rays: [] },
      telemetry: {}
    };
    const renderer = new OpticsRenderer();
    renderer.mount({
      container: new MockElement('div'),
      scene: missingGeomRefractScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600)
    });
    renderer.render(mockOutput);

    assert(renderer.layers.shapes.children.length === 0, 'No synthetic boundary or normal line drawn when geometry is missing');
    assert(renderer.layers.landmarks.children.length === 0, 'No synthetic medium text labels drawn when geometry is missing');
    assert(renderer.layers.handles.children.length === 0, 'No synthetic beam source handle drawn when geometry is missing');
    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 22. PRISM DRAG EITHER WORKS END-TO-END OR HAS NO HANDLE
  // -----------------------------------------------------------------
  console.log('\n[22/23] Verifying prism drag has zero non-functional handles:');
  {
    const prismScene = {
      schemaVersion: '1.0',
      id: 'PRISM-NO-HANDLE',
      domain: 'optics',
      subtype: 'prism',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: {
        vertices: [{ x: 250, y: 450 }, { x: 400, y: 150 }, { x: 550, y: 450 }],
        rayOrigin: { x: 100, y: 350 },
        rayDirection: { x: 1, y: -0.2 }
      },
      parameters: {
        refractiveIndex: { value: 1.52 }
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(prismScene, new MockElement('div'));
    const out = runtime.getOutput();

    const renderer = new OpticsRenderer();
    renderer.mount({
      container: new MockElement('div'),
      scene: prismScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600)
    });
    renderer.render(out);

    // Verify zero non-functional handles on prism overlay
    assert(renderer.layers.handles.children.length === 0, 'Prism has ZERO non-functional visible handles');
    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 23. CURRENT DIRECTION DOES NOT DEPEND ON TERMINAL ID NAMING
  // -----------------------------------------------------------------
  console.log('\n[23/23] Verifying current direction does not depend on terminal ID naming:');
  {
    const arbitraryTerminalsScene = {
      schemaVersion: '1.0',
      id: 'ARBITRARY-TERMINALS-CIRCUIT',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }],
        components: [
          {
            id: 'V1',
            type: 'voltage_source',
            value: 12.0,
            nodes: ['N1', 'N0'],
            terminals: [
              { id: 'V1.custom_anode_out', node: 'N1', source_px: [100, 200] },
              { id: 'V1.custom_cathode_in', node: 'N0', source_px: [100, 400] }
            ]
          },
          {
            id: 'R1',
            type: 'resistor',
            value: 10.0,
            nodes: ['N1', 'N0'],
            terminals: [
              { id: 'R1.port_foo', node: 'N1', source_px: [400, 200] },
              { id: 'R1.port_bar', node: 'N0', source_px: [400, 400] }
            ]
          }
        ],
        wires: [
          { id: 'w_feed', from: 'V1.custom_anode_out', to: 'R1.port_foo', path_source_px: [[100, 200], [400, 200]] },
          { id: 'w_ret', from: 'R1.port_bar', to: 'V1.custom_cathode_in', path_source_px: [[400, 400], [100, 400]] }
        ]
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(arbitraryTerminalsScene, new MockElement('div'));
    const out = runtime.getOutput();

    const wFeed = out.geometry.wires.find(w => w.id === 'w_feed');
    const wRet = out.geometry.wires.find(w => w.id === 'w_ret');

    assertClose(wFeed.current_A, 1.20, 0.01, 'Feed wire carries correct current 1.20 A without standard terminal names');
    assert(wFeed.direction === 'forward', `Feed wire flows forward (got "${wFeed.direction}") based on structural nodes`);

    assertClose(wRet.current_A, 1.20, 0.01, 'Return wire carries correct current 1.20 A without standard terminal names');
    assert(wRet.direction === 'forward', `Return wire flows forward (got "${wRet.direction}") based on structural nodes`);
  }

  // -----------------------------------------------------------------
  // 24. UNIT-AWARE OPTICAL CALIBRATION & INDIVIDUAL PARAMETER UNITS
  // -----------------------------------------------------------------
  console.log('\n[24/27] Verifying unit-aware optical calibration (6.5 px/cm + 0.20 m -> 130 px):');
  {
    const unitAwareScene = {
      schemaVersion: '1.0',
      id: 'UNIT-AWARE-LENS-REGRESSION',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: {
        type: 'source_px',
        width: 800,
        height: 600,
        calibration: {
          pixels_per_cm: 6.5
        }
      },
      geometry: {
        lensX: 400,
        axisY: 300,
        sourceWidth: 800,
        sourceHeight: 600
      },
      parameters: {
        focalLength: {
          value: 0.20,
          unit: 'm',
          editable: true,
          targetId: 'lens_1'
        },
        objectDistance: {
          value: 40.0,
          unit: 'cm',
          editable: true,
          targetId: 'object_main'
        },
        objectHeight: {
          value: -10.0,
          unit: 'cm',
          editable: true,
          targetId: 'object_main'
        }
      },
      objects: [
        { id: 'lens_1', optics: { model: 'thin_lens' } },
        { id: 'object_main', optics: { model: 'optical_object' } }
      ]
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(unitAwareScene, new MockElement('div'));
    const out = runtime.getOutput();

    // 0.20 m = 20 cm. 20 cm * 6.5 px/cm = 130 px.
    assertClose(out.geometry.landmarks.focalPoints[0].x, 270, 0.01, 'Front focus is 270 px (400 - 130 px)');
    assertClose(out.geometry.landmarks.focalPoints[1].x, 530, 0.01, 'Back focus is 530 px (400 + 130 px)');

    // 40 cm * 6.5 px/cm = 260 px. objectX = 400 - 260 = 140 px.
    assertClose(out.geometry.object.base.x, 140, 0.01, 'Object is at 140 px (400 - 260 px)');

    // Telemetry must convert each quantity using its OWN parameter unit
    assertClose(out.telemetry.focalLength, 0.20, 0.001, 'Telemetry focalLength reports in its own declared unit: 0.20 m');
    assertClose(out.telemetry.objectDistance, 40.0, 0.01, 'Telemetry objectDistance reports in its own declared unit: 40.0 cm');
  }

  // -----------------------------------------------------------------
  // 25. CIRCUIT COMPILER: TERMINAL WITHOUT source_px COMPILES TO null
  // -----------------------------------------------------------------
  console.log('\n[25/27] Verifying CircuitCompiler terminal missing source_px compiles to null (no [0,0] fabrication):');
  {
    const circuitWithUnlocatedTerminals = {
      reference_node: 'N0',
      nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }],
      components: [
        {
          id: 'R1',
          type: 'resistor',
          value: 100,
          nodes: ['N1', 'N0'],
          terminals: [
            { id: 'R1.1', node: 'N1' },
            { id: 'R1.2', node: 'N0' }
          ]
        },
        {
          id: 'SW1',
          type: 'switch',
          closed: true,
          nodes: ['N1', 'N0'],
          terminals: [
            { id: 'SW1.1', node: 'N1' },
            { id: 'SW1.2', node: 'N0' }
          ]
        }
      ],
      wires: []
    };

    const compiled = CircuitCompiler.compile({ circuit: circuitWithUnlocatedTerminals });
    const r1 = compiled.componentById.get('R1');
    assert(r1.terminals[0].source_px === null, 'Resistor terminal 1 source_px is null, not [0, 0]');
    assert(r1.terminals[1].source_px === null, 'Resistor terminal 2 source_px is null, not [0, 0]');

    const sw1 = compiled.componentById.get('SW1');
    assert(sw1.terminals[0].source_px === null, 'Switch terminal 1 source_px is null, not [0, 0]');
    assert(sw1.terminals[1].source_px === null, 'Switch terminal 2 source_px is null, not [0, 0]');
    const runtime = new PhysicsRuntime();
    await runtime.load({
      schemaVersion: '1.0',
      id: 'UNLOCATED-CIRCUIT-SCENE',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: circuitWithUnlocatedTerminals
    }, new MockElement('div'));
    const out = runtime.getOutput();
    const swOut = out.geometry.switches.find(s => s.id === 'SW1');
    assert(swOut.hitTarget === null, 'Switch with unlocated terminals has hitTarget === null (no hit target at [0,0])');
  }

  // -----------------------------------------------------------------
  // 26. MULTI-SOURCE CIRCUITS DO NOT EXPOSE AMBIGUOUS totalCurrent_A
  // -----------------------------------------------------------------
  console.log('\n[26/27] Verifying multi-source circuit telemetry correctness (no ambiguous totalCurrent_A):');
  {
    const multiSourceScene = {
      schemaVersion: '1.0',
      id: 'MULTI-SOURCE-CIRCUIT-001',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [
          { id: 'N0', reference: true },
          { id: 'N1', reference: false },
          { id: 'N2', reference: false }
        ],
        components: [
          {
            id: 'V1',
            type: 'voltage_source',
            value: 12.0,
            nodes: ['N1', 'N0'],
            terminals: [{ id: 'V1.p', node: 'N1', source_px: [100, 100] }, { id: 'V1.n', node: 'N0', source_px: [100, 300] }]
          },
          {
            id: 'V2',
            type: 'voltage_source',
            value: 6.0,
            nodes: ['N2', 'N0'],
            terminals: [{ id: 'V2.p', node: 'N2', source_px: [500, 100] }, { id: 'V2.n', node: 'N0', source_px: [500, 300] }]
          },
          {
            id: 'R1',
            type: 'resistor',
            value: 10.0,
            nodes: ['N1', 'N2'],
            terminals: [{ id: 'R1.1', node: 'N1', source_px: [200, 100] }, { id: 'R1.2', node: 'N2', source_px: [400, 100] }]
          }
        ],
        wires: []
      }
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(multiSourceScene, new MockElement('div'));
    const out = runtime.getOutput();

    assert(out.telemetry.totalCurrent_A === undefined, 'Multi-source circuit omits ambiguous totalCurrent_A');
    assert(out.telemetry.loopCurrent_A === undefined, 'Multi-source circuit omits ambiguous loopCurrent_A');
    assert(out.telemetry.sourceCurrents && typeof out.telemetry.sourceCurrents === 'object', 'Multi-source circuit exposes per-source currents');
    assert(typeof out.telemetry.totalDeliveredSourceCurrent_A === 'number', 'Multi-source circuit exposes totalDeliveredSourceCurrent_A');
    assert(typeof out.telemetry.branchCurrents === 'object', 'Multi-source circuit exposes branchCurrents');
  }

  // -----------------------------------------------------------------
  // 27. OPTICS SEMANTIC INTEGRITY: ZERO FALLBACK IDENTITIES
  // -----------------------------------------------------------------
  console.log('\n[27/27] Verifying OpticsRenderer zero semantic identity fallbacks:');
  {
    const renderer = new OpticsRenderer();
    renderer.mount({
      container: new MockElement('div'),
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600)
    });

    // 27a. Missing subtype -> renders nothing
    renderer.render({
      domain: 'optics',
      geometry: { opticalAxis: { minX: 0, maxX: 800, y: 300 } }
    });
    assert(renderer.layers.axis.children.length === 0, 'Missing subtype renders nothing (axis layer empty)');
    assert(renderer.layers.shapes.children.length === 0, 'Missing subtype renders nothing (shapes layer empty)');

    // 27b. Missing targetId on handle -> renders NO handle
    renderer.render({
      domain: 'optics',
      subtype: 'thin_lens',
      geometry: {
        object: { base: { x: 100, y: 300 }, tip: { x: 100, y: 200 }, height: -100 },
        handles: {
          objectArrow: {
            axes: {
              x: { parameter: 'someParam', editable: true },
              y: { parameter: 'someParam2', editable: true }
            }
          }
        }
      }
    });
    assert(renderer.layers.handles.children.length === 0, 'Missing handle targetId produces ZERO interaction handles');

    // 27c. Missing parameter address on handle -> renders NO handle
    renderer.render({
      domain: 'optics',
      subtype: 'thin_lens',
      geometry: {
        object: { base: { x: 100, y: 300 }, tip: { x: 100, y: 200 }, height: -100 },
        handles: {
          objectArrow: {
            targetId: 'custom_obj_1',
            axes: {
              x: { editable: true },
              y: { editable: true }
            }
          }
        }
      }
    });
    assert(renderer.layers.handles.children.length === 0, 'Missing parameter address produces ZERO interaction handles');

    renderer.dispose();
  }

  // -----------------------------------------------------------------
  // 28. SIMULATION CAPABILITY REGISTRY & BIDIRECTIONAL DIRECT MANIPULATION
  // -----------------------------------------------------------------
  console.log('\n[28/28] Verifying SimulationCapabilityRegistry & bidirectional direct manipulation:');
  {
    // 28a. A thin-lens scene without explicit editable flags receives supported capabilities
    // and exposes its valid existing parameters
    const legacyLensScene = {
      schemaVersion: '1.0',
      id: 'LEGACY-LENS-NO-EDIT-FLAGS',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400, axisY: 300, sourceWidth: 800, sourceHeight: 600 },
      parameters: {
        focalLength: { value: 130.0, unit: 'px', provenance: 'observed' },
        objectDistance: { value: 260.0, unit: 'px', provenance: 'observed' },
        objectHeight: { value: -80.0, unit: 'px', provenance: 'observed' }
      },
      objects: [
        { id: 'green_arrow_7', role: 'object', type: 'optical_object' },
        { id: 'lens_main', role: 'lens', type: 'thin_lens' }
      ]
    };

    const runtime = new PhysicsRuntime();
    await runtime.load(legacyLensScene, new MockElement('div'));
    const out = runtime.getOutput();
    const editParams = out.editableParameters || {};

    assert(editParams.objectDistance !== undefined, 'objectDistance receives editable capability');
    assert(editParams.objectDistance.editable === true, 'objectDistance has editable === true');
    assert(editParams.objectDistance.control?.type === 'slider', 'objectDistance has slider control');

    assert(editParams.objectHeight !== undefined, 'objectHeight receives editable capability');
    assert(editParams.objectHeight.editable === true, 'objectHeight has editable === true');

    assert(editParams.focalLength !== undefined, 'focalLength receives editable capability');
    assert(editParams.focalLength.editable === true, 'focalLength has editable === true');

    // 28b. A detected object with arbitrary ID such as green_arrow_7 is the drag target
    assert(out.geometry.handles?.objectArrow !== undefined, 'Handles created for object');
    assert(out.geometry.handles.objectArrow.targetId === 'green_arrow_7', 'Actual arbitrary ID green_arrow_7 is the drag target');
    assert(out.geometry.handles.objectArrow.axes.x.editable === true, 'X-axis drag is enabled');
    assert(out.geometry.handles.objectArrow.axes.y.editable === true, 'Y-axis drag is enabled');

    // Mount OpticsRenderer and verify DOM handle attributes
    const container = new MockElement('div');
    const renderer = new OpticsRenderer();
    let interceptedInteraction = null;
    renderer.mount({
      container,
      scene: legacyLensScene,
      coordinateMapper: new CoordinateMapper(800, 600, 800, 600),
      onInteract: (action) => {
        interceptedInteraction = action;
        runtime.updateParameter(action);
      }
    });
    renderer.render(out);

    const handlePos = renderer.layers.handles.children.find(el => el.getAttribute('data-handle') === 'object_pos');
    assert(handlePos !== undefined, 'Renderer created object_pos DOM handle');
    assert(handlePos.getAttribute('data-target-id') === 'green_arrow_7', 'DOM handle carries data-target-id="green_arrow_7"');

    // 28c. Dragging updates the corresponding slider / parameter
    renderer._dragState = { type: 'object_pos', targetId: 'green_arrow_7' };
    renderer._handlePointerMove({
      preventDefault: () => {},
      clientX: 200, // In view coordinates (400 - 200 = 200px distance)
      clientY: 300
    });
    renderer._dragState = null;

    assert(interceptedInteraction !== null, 'Dragging triggered onInteract');
    assert(interceptedInteraction.targetId === 'green_arrow_7', 'Dispatched targetId is green_arrow_7');
    assert(interceptedInteraction.key === 'objectDistance', 'Dispatched key is objectDistance');
    assertClose(interceptedInteraction.value, 200.0, 0.1, 'Dispatched value is 200.0 px');

    // Verify runtime updated
    const afterDragOut = runtime.getOutput();
    assertClose(afterDragOut.editableParameters.objectDistance.value, 200.0, 0.1, 'editableParameters reflects dragged value 200.0');
    assertClose(afterDragOut.geometry.object.base.x, 200.0, 0.1, 'Rendered object base moved to x=200 px');

    // 28d. Slider update moves the rendered object (bidirectional sync)
    runtime.updateParameter('objectDistance', 320.0);
    const afterSliderOut = runtime.getOutput();
    assertClose(afterSliderOut.editableParameters.objectDistance.value, 320.0, 0.1, 'Slider update changed parameter to 320.0');
    assertClose(afterSliderOut.geometry.object.base.x, 80.0, 0.1, 'Rendered object base moved to 80 px (400 - 320)');
    renderer.dispose();

    // 28e. Pendulum and projectile also receive appropriate capabilities
    const legacyPendulumScene = {
      schemaVersion: '1.0',
      id: 'LEGACY-PENDULUM-NO-FLAGS',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        length: { value: 1.5, unit: 'm', provenance: 'observed' },
        initialAngle: { value: -25.0, unit: '°', provenance: 'observed' },
        gravity: { value: 9.81, unit: 'm/s²', provenance: 'assumed' },
        mass: { value: 1.0, unit: 'kg', provenance: 'assumed' }
      },
      objects: [{
        id: 'bob_alpha_9',
        type: 'pendulum',
        role: 'dynamic',
        geometry: { pivot: { x: 400, y: 100 }, string_length_px: 300, bob_radius_px: 25 },
        physics: { length_m: 1.5, mass_kg: 1.0, damping_s_inv: 0.0, theta0_rad: -0.436 }
      }]
    };

    const pRuntime = new PhysicsRuntime();
    await pRuntime.load(legacyPendulumScene, new MockElement('div'));
    const pOut = pRuntime.getOutput();

    assert(pOut.editableParameters.length !== undefined, 'Pendulum length receives editable capability');
    assert(pOut.editableParameters.length.editable === true, 'Pendulum length has editable === true');
    assert(pOut.editableParameters.initialAngle !== undefined, 'Pendulum initialAngle receives editable capability');
    assert(pOut.editableParameters.initialAngle.editable === true, 'Pendulum initialAngle has editable === true');

    // 28f. Evidence-only / unsupported parameters remain non-editable
    assert(pOut.editableParameters.gravity === undefined, 'Evidence-only gravity is NOT exposed in editableParameters');
    assert(pOut.editableParameters.mass === undefined, 'Mass is NOT exposed as student editable');

    // Projectile capabilities
    const legacyProjScene = {
      schemaVersion: '1.0',
      id: 'LEGACY-PROJ-NO-FLAGS',
      domain: 'mechanics',
      subtype: 'projectile',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      calibration: { pixels_per_meter: 50.0 },
      parameters: {
        speed: { value: 20.0, unit: 'm/s', provenance: 'observed' },
        angle: { value: 45.0, unit: '°', provenance: 'observed' },
        gravity: { value: 9.81, unit: 'm/s²', provenance: 'assumed' }
      },
      objects: [{
        id: 'cannonball_x',
        type: 'projectile',
        role: 'projectile',
        geometry: { launch_source_px: { x: 100, y: 500 }, radius_source_px: 16.0 },
        physics: { speed_m_s: 20.0, launch_angle_deg: 45.0 }
      }]
    };

    const projRuntime = new PhysicsRuntime();
    await projRuntime.load(legacyProjScene, new MockElement('div'));
    const projOut = projRuntime.getOutput();

    assert(projOut.editableParameters.speed !== undefined, 'Projectile speed receives editable capability');
    assert(projOut.editableParameters.speed.editable === true, 'Projectile speed is editable === true');
    assert(projOut.editableParameters.angle !== undefined, 'Projectile angle receives editable capability');
    assert(projOut.editableParameters.angle.editable === true, 'Projectile angle is editable === true');
    assert(projOut.editableParameters.gravity === undefined, 'Projectile gravity remains non-editable');

    // 28g. Circuit component controls are generated by component type, not fixed IDs
    const arbitraryCircuitScene = {
      schemaVersion: '1.0',
      id: 'ARBITRARY-CIRCUIT-COMPONENTS',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N0', reference: true }, { id: 'N1', reference: false }, { id: 'N2', reference: false }],
        components: [
          { id: 'custom_bat_1', type: 'battery', value: 9.0, unit: 'V', nodes: ['N1', 'N0'] },
          { id: 'custom_res_99', type: 'resistor', value: 75.0, unit: 'Ω', nodes: ['N1', 'N2'] },
          { id: 'custom_sw_2', type: 'switch', state: 'closed', nodes: ['N2', 'N0'] }
        ],
        wires: []
      }
    };

    const circRuntime = new PhysicsRuntime();
    await circRuntime.load(arbitraryCircuitScene, new MockElement('div'));
    const circOut = circRuntime.getOutput();

    assert(circOut.editableParameters['custom_bat_1.voltage'] !== undefined, 'custom_bat_1 gets voltage slider by component type');
    assert(circOut.editableParameters['custom_res_99.resistance'] !== undefined, 'custom_res_99 gets resistance slider by component type');
    assert(circOut.editableParameters['custom_sw_2.closed'] !== undefined, 'custom_sw_2 gets toggle control by component type');

    // 28h. A parameter absent from the scene is never fabricated merely because the registry supports it
    const partialLensScene = {
      schemaVersion: '1.0',
      id: 'PARTIAL-LENS-NO-HEIGHT',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { lensX: 400, axisY: 300 },
      parameters: {
        focalLength: { value: 120.0, unit: 'px' },
        objectDistance: { value: 240.0, unit: 'px' }
        // objectHeight is ABSENT
      },
      objects: [{ id: 'obj_1', role: 'object', type: 'optical_object', optics: { model: 'optical_object', height_px: 80 } }]
    };

    const partialRuntime = new PhysicsRuntime();
    await partialRuntime.load(partialLensScene, new MockElement('div'));
    const partialOut = partialRuntime.getOutput();

    assert(partialOut.editableParameters.objectDistance !== undefined, 'objectDistance is present and editable');
    assert(partialOut.editableParameters.objectHeight === undefined, 'ABSENT objectHeight is NEVER fabricated');
    assert(partialOut.geometry.handles?.objectArrow?.axes?.y?.editable !== true, 'No height drag handle when objectHeight is absent');

    // 28i. Missing geometry keeps parameter control available via slider but disables drag handles
    const noGeomLensScene = {
      schemaVersion: '1.0',
      id: 'NO-GEOM-LENS',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        focalLength: { value: 100.0, unit: 'px' },
        objectDistance: { value: 200.0, unit: 'px' }
      }
      // geometry is completely ABSENT
    };

    const resolvedNoGeom = defaultCapabilityRegistry.resolve(noGeomLensScene);
    assert(resolvedNoGeom.parameters.objectDistance.editable === true, 'Parameter remains editable in resolved scene');
    assert(resolvedNoGeom.parameters.objectDistance.control?.type === 'slider', 'Slider control remains configured');
    assert(Object.keys(resolvedNoGeom.interactions || {}).length === 0, 'No interaction handles bound when geometry is absent (zero fabrication)');
  }

  console.log('\n===================================================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('===================================================================');

  if (failed > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

runTests().catch(err => {
  console.error('Fatal test error:', err);
  process.exit(1);
});
