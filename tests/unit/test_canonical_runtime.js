/**
 * tests/unit/test_canonical_runtime.js
 * 
 * Exhaustive PR-02 Canonical Physics Runtime Test Suite:
 * 1. Operational unit conversions, scaling, and incompatible dimension rejection.
 * 2. Discriminated CoordinateSpace union (source_px, world, local) for book-agnostic / text-to-simulation pathways.
 * 3. Mechanics routing, pure headless RK4 / kinematics execution, and separation of validation vs unsupported errors.
 * 4. Zero-fabrication optics routing matrix (thin_lens, spherical_mirror, snell, prism) & missing parameter rejection.
 * 5. Circuits DC / MNA analysis routing with generic SI output (zero hardcoded fixture assumptions).
 * 6. Atomic parameter addressing, provenance tagging ('student'), and live unit conversion.
 * 7. Unified runtime lifecycle (start, pause, step, reset, dispose) and deterministic SolverRegistry.
 * 8. Strict validation failures, non-fabrication guarantees, and domain object integrity.
 */

import { PhysicsRuntime } from '../../engine/core/PhysicsRuntime.js';
import { SolverRegistry, defaultRegistry } from '../../engine/core/SolverRegistry.js';
import { MechanicsAdapter } from '../../engine/mechanics/MechanicsAdapter.js';
import { OpticsAdapter } from '../../engine/optics/OpticsAdapter.js';
import { CircuitAdapter } from '../../engine/circuits/CircuitAdapter.js';
import {
  PhysicsSceneValidationError,
  UnsupportedPhysicsDomainError,
  UnsupportedPhysicsSubtypeError,
  MissingRequiredParameterError,
  DomainObjectMismatchError
} from '../../engine/core/errors.js';
import { convertUnit, getParameterInUnit } from '../../engine/core/units.js';

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
  assert(diff <= tol, `${message} (expected ~${expected}, got ${actual})`);
}

function assertThrows(fn, ExpectedErrorType, message) {
  try {
    fn();
    failed++;
    console.error(`  ✗ FAIL (Expected error was not thrown): ${message}`);
  } catch (err) {
    if (ExpectedErrorType && !(err instanceof ExpectedErrorType)) {
      failed++;
      console.error(`  ✗ FAIL (Wrong error type): ${message}. Expected ${ExpectedErrorType.name}, got ${err.constructor.name}: ${err.message}`);
    } else {
      passed++;
      console.log(`  ✓ PASS: ${message} (threw ${err.constructor.name})`);
    }
  }
}

async function assertThrowsAsync(asyncFn, ExpectedErrorType, message) {
  try {
    await asyncFn();
    failed++;
    console.error(`  ✗ FAIL (Expected async error was not thrown): ${message}`);
  } catch (err) {
    if (ExpectedErrorType && !(err instanceof ExpectedErrorType)) {
      failed++;
      console.error(`  ✗ FAIL (Wrong async error type): ${message}. Expected ${ExpectedErrorType.name}, got ${err.constructor.name}: ${err.message}`);
    } else {
      passed++;
      console.log(`  ✓ PASS: ${message} (threw ${err.constructor.name})`);
    }
  }
}

async function runTests() {
  console.log('====================================================');
  console.log('  TESTING PR-02 CANONICAL PHYSICS RUNTIME MATRIX');
  console.log('====================================================\n');

  // ---------------------------------------------------------------
  // 1. OPERATIONAL PHYSICAL UNITS
  // ---------------------------------------------------------------
  console.log('[1/8] Testing operational physical unit conversions & validation:');
  {
    assertClose(convertUnit(80, 'cm', 'm'), 0.8, 1e-6, '80 cm converts to 0.8 m');
    assertClose(convertUnit(1.5, 'm', 'cm'), 150, 1e-6, '1.5 m converts to 150 cm');
    assertClose(convertUnit(500, 'mm', 'm'), 0.5, 1e-6, '500 mm converts to 0.5 m');
    assertClose(convertUnit(180, 'deg', 'rad'), Math.PI, 1e-6, '180 deg converts to π rad');
    assertClose(convertUnit(Math.PI / 2, 'rad', 'deg'), 90, 1e-6, 'π/2 rad converts to 90 deg');
    assertClose(convertUnit(10, 'kΩ', 'Ω'), 10000, 1e-6, '10 kΩ converts to 10,000 Ω');
    assertClose(convertUnit(500, 'mA', 'A'), 0.5, 1e-6, '500 mA converts to 0.5 A');
    assertClose(convertUnit(5, 'kV', 'V'), 5000, 1e-6, '5 kV converts to 5000 V');

    assertThrows(
      () => convertUnit(10, 'kg', 'm'),
      Error,
      'Rejects incompatible unit conversion (kg to m)'
    );

    const testScene = {
      parameters: {
        length: { value: 80, unit: 'cm', status: 'known' },
        mass: { value: 2.5, unit: 'kg', status: 'known' },
        unknownVal: { value: 10, unit: 'm', status: 'unknown' }
      }
    };

    const resolvedMeters = getParameterInUnit(testScene, 'length', 'm');
    assertClose(resolvedMeters, 0.8, 1e-6, 'getParameterInUnit resolves 80 cm as 0.8 m');

    assertThrows(
      () => getParameterInUnit(testScene, 'mass', 'm'),
      PhysicsSceneValidationError,
      'getParameterInUnit throws PhysicsSceneValidationError for incompatible target unit'
    );

    assertThrows(
      () => getParameterInUnit(testScene, 'unknownVal', 'm'),
      PhysicsSceneValidationError,
      'getParameterInUnit throws PhysicsSceneValidationError for status unknown'
    );
  }

  // ---------------------------------------------------------------
  // 2. COORDINATE SPACE DISCRIMINATED UNION
  // ---------------------------------------------------------------
  console.log('\n[2/8] Testing CoordinateSpace discriminated union (source_px, world, local):');
  {
    const runtime = new PhysicsRuntime();

    // 1. source_px
    const sourcePxScene = {
      schemaVersion: '1.0',
      id: 'COORD-SRC-01',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 797, height: 652 },
      parameters: {
        focalLength: { value: 100, unit: 'px', status: 'known' },
        objectDistance: { value: 200, unit: 'px', status: 'known' },
        objectHeight: { value: -50, unit: 'px', status: 'known' }
      },
      geometry: { axisY: 326, lensX: 398 }
    };
    const out1 = await runtime.load(sourcePxScene);
    assert(out1.domain === 'optics', 'source_px coordinateSpace loads successfully');
    assert(runtime.scene.coordinateSpace.type === 'source_px', 'coordinateSpace.type preserved as source_px');
    assert(runtime.scene.coordinateSpace.width === 797, 'source_px width is 797');

    // 2. world
    const worldScene = {
      schemaVersion: '1.0',
      id: 'COORD-WORLD-01',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'world', unit: 'm', bounds: { maxX: 10, maxY: 10 } },
      parameters: {
        length: { value: 1.5, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 0.2, unit: 'rad', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed', source: 'ideal_pendulum_model' }
      },
      objects: [{
        id: 'pendulum_world',
        type: 'pendulum',
        geometry: { pivot: { x: 0, y: 5 }, string_length_px: 150, bob_radius_px: 15 }
      }]
    };
    const out2 = await runtime.load(worldScene);
    assert(out2.domain === 'mechanics', 'world coordinateSpace loads successfully');
    assert(runtime.scene.coordinateSpace.type === 'world', 'coordinateSpace.type preserved as world');
    assert(runtime.scene.coordinateSpace.unit === 'm', 'world coordinateSpace unit is m');

    // 3. local
    const localScene = {
      schemaVersion: '1.0',
      id: 'COORD-LOCAL-01',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'local', width: 1000, height: 700 },
      parameters: {
        focalLength: { value: 100, unit: 'px', status: 'known' },
        objectDistance: { value: 200, unit: 'px', status: 'known' },
        objectHeight: { value: -50, unit: 'px', status: 'known' }
      },
      geometry: { axisY: 350, lensX: 500 }
    };
    const out3 = await runtime.load(localScene);
    assert(out3.domain === 'optics', 'local coordinateSpace loads successfully');
    assert(runtime.scene.coordinateSpace.type === 'local', 'coordinateSpace.type preserved as local');
  }

  // ---------------------------------------------------------------
  // 3. MECHANICS ROUTING, PURE HEADLESS RK4 & ZERO FABRICATION
  // ---------------------------------------------------------------
  console.log('\n[3/8] Testing Mechanics routing & real headless physics execution:');
  {
    const runtime = new PhysicsRuntime();

    // 1. Pendulum routes to pendulum solver and actually evolves theta/omega via RK4
    const pendulumScene = {
      schemaVersion: '1.0',
      id: 'MECH-PEND-01',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 797, height: 652 },
      parameters: {
        length: { value: 1.2, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 20, unit: 'deg', status: 'known' },
        mass: { value: 1.5, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed', source: 'ideal_pendulum_model' }
      },
      objects: [{
        id: 'pendulum_sys',
        type: 'pendulum',
        geometry: { pivot: { x: 400, y: 100 }, string_length_px: 250, bob_radius_px: 20 }
      }]
    };
    const pendOut = await runtime.load(pendulumScene);
    assert(pendOut.subtype === 'pendulum', 'Pendulum scene routes to pendulum solver');
    const initialTheta = pendOut.state.thetaRad;
    const initialOmega = pendOut.state.omega;

    // Run 30 steps of real numerical physics (headless)
    for (let i = 0; i < 30; i++) {
      runtime.step(1 / 60);
    }
    const evolvedState = runtime.getState();
    assert(evolvedState.time > 0.4, 'Simulation time advanced');
    assert(evolvedState.thetaRad !== initialTheta, 'Pendulum angle theta evolved via RK4 integration');
    assert(Math.abs(evolvedState.omega) > 0.01, 'Pendulum angular velocity omega evolved via RK4 integration');

    // 2. Projectile routes to projectile solver and actually calculates x(t), y(t), vx, vy
    const projScene = {
      schemaVersion: '1.0',
      id: 'MECH-PROJ-01',
      domain: 'mechanics',
      subtype: 'projectile',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      calibration: { pixels_per_meter: 50.0 },
      parameters: {
        speed: { value: 20, unit: 'm/s', status: 'known' },
        angle: { value: 45, unit: 'deg', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' }
      },
      objects: [{
        id: 'cannonball',
        type: 'projectile',
        geometry: { launch_source_px: { x: 100, y: 500 }, radius_source_px: 18.0 }
      }]
    };
    const projOut = await runtime.load(projScene);
    assert(projOut.subtype === 'projectile', 'Projectile scene routes to projectile solver');

    // Step projectile 30 times (0.5 sec)
    for (let i = 0; i < 30; i++) {
      runtime.step(1 / 60);
    }
    const projEvolved = runtime.getState();
    assertClose(projEvolved.time, 0.5, 0.05, 'Projectile time is 0.5s');
    // x = 20 * cos(45) * 0.5 = 14.14 * 0.5 = ~7.07 m
    assertClose(projEvolved.xM, 7.07, 0.2, 'Projectile x position evolved analytically');
    // y = 20 * sin(45) * 0.5 - 0.5 * 9.81 * 0.25 = 7.07 - 1.226 = ~5.84 m
    assertClose(projEvolved.yM, 5.84, 0.2, 'Projectile y position evolved analytically');
    // vy = 20 * sin(45) - 9.81 * 0.5 = 14.14 - 4.9 = ~9.24 m/s
    assertClose(projEvolved.vy, 9.24, 0.2, 'Projectile vertical velocity vy evolved analytically');

    // 3. Missing physical parameters strictly throws (Zero fabrication)
    const missingLengthScene = {
      schemaVersion: '1.0',
      id: 'MECH-FAIL-01',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 20, unit: 'deg', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed' }
      },
      objects: [{ id: 'p', type: 'pendulum', geometry: { pivot: { x: 100, y: 100 }, string_length_px: 200, bob_radius_px: 20 } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(missingLengthScene),
      MissingRequiredParameterError,
      'Pendulum missing length throws MissingRequiredParameterError (no fallback to 1.0m)'
    );

    const missingDampingScene = {
      schemaVersion: '1.0',
      id: 'MECH-FAIL-DAMPING',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        length: { value: 1.0, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 20, unit: 'deg', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' }
      },
      objects: [{ id: 'p', type: 'pendulum', geometry: { pivot: { x: 100, y: 100 }, string_length_px: 200, bob_radius_px: 20 } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(missingDampingScene),
      MissingRequiredParameterError,
      'Pendulum missing damping throws MissingRequiredParameterError (no silent zero damping)'
    );

    const missingBobRadiusScene = {
      schemaVersion: '1.0',
      id: 'MECH-FAIL-RADIUS',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        length: { value: 1.0, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 20, unit: 'deg', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed' }
      },
      objects: [{ id: 'p', type: 'pendulum', geometry: { pivot: { x: 100, y: 100 }, string_length_px: 200 } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(missingBobRadiusScene),
      MissingRequiredParameterError,
      'Pendulum missing bob_radius_px throws MissingRequiredParameterError (no fallback to 24px)'
    );

    const missingGravityScene = {
      schemaVersion: '1.0',
      id: 'MECH-FAIL-02',
      domain: 'mechanics',
      subtype: 'projectile',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      calibration: { pixels_per_meter: 50.0 },
      parameters: {
        speed: { value: 10, unit: 'm/s', status: 'known' },
        angle: { value: 30, unit: 'deg', status: 'known' }
      },
      objects: [{ id: 'b', type: 'projectile', geometry: { launch_source_px: { x: 50, y: 50 }, radius_source_px: 18.0 } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(missingGravityScene),
      MissingRequiredParameterError,
      'Projectile missing gravity throws MissingRequiredParameterError (no fallback to 9.81)'
    );

    const missingPpmScene = {
      schemaVersion: '1.0',
      id: 'MECH-FAIL-PPM',
      domain: 'mechanics',
      subtype: 'projectile',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        speed: { value: 10, unit: 'm/s', status: 'known' },
        angle: { value: 30, unit: 'deg', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' }
      },
      objects: [{ id: 'b', type: 'projectile', geometry: { launch_source_px: { x: 50, y: 50 }, radius_source_px: 18.0 } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(missingPpmScene),
      MissingRequiredParameterError,
      'Projectile missing pixels_per_meter in source_px throws MissingRequiredParameterError (no fallback to 50)'
    );

    // 4. Well-formed inclined plane throws UnsupportedPhysicsSubtypeError
    const inclineScene = {
      schemaVersion: '1.0',
      id: 'MECH-INC-01',
      domain: 'mechanics',
      subtype: 'inclined_plane',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: { inclineAngle: { value: 30, unit: 'deg', status: 'known' } }
    };
    await assertThrowsAsync(
      async () => runtime.load(inclineScene),
      UnsupportedPhysicsSubtypeError,
      'Well-formed inclined_plane throws UnsupportedPhysicsSubtypeError on execution'
    );
  }

  // ---------------------------------------------------------------
  // 4. OPTICS ROUTING MATRIX & ZERO FABRICATION
  // ---------------------------------------------------------------
  console.log('\n[4/8] Testing Optics routing matrix & zero fabrication:');
  {
    const runtime = new PhysicsRuntime();

    // 1. Thin lens
    const lensScene = {
      schemaVersion: '1.0',
      id: 'OPT-LENS-01',
      domain: 'optics',
      subtype: 'thin_lens',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        focalLength: { value: 130, unit: 'px', status: 'known' },
        objectDistance: { value: 260, unit: 'px', status: 'known' },
        objectHeight: { value: -80, unit: 'px', status: 'known' }
      },
      geometry: { axisY: 300, lensX: 400 }
    };
    const lensOut = await runtime.load(lensScene);
    assert(lensOut.subtype === 'thin_lens', 'Thin lens routes to thin lens solver');
    assert(lensOut.state.v === 260, 'Thin lens solves v = 260 at u = 2f');

    // 2. Spherical Mirror
    const mirrorScene = {
      schemaVersion: '1.0',
      id: 'OPT-MIRR-01',
      domain: 'optics',
      subtype: 'spherical_mirror',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        focalLength: { value: 100, unit: 'px', status: 'known' },
        objectDistance: { value: 200, unit: 'px', status: 'known' },
        objectHeight: { value: -60, unit: 'px', status: 'known' },
        mirrorType: { value: 'concave', status: 'known' }
      },
      geometry: { axisY: 300, mirrorX: 400 }
    };
    const mirrOut = await runtime.load(mirrorScene);
    assert(mirrOut.subtype === 'spherical_mirror', 'Spherical mirror routes to mirror solver');
    assert(mirrOut.state.v === 200, 'Concave mirror solves v = 200 at u = 2f');

    // 3. Interface Refraction (Snell's Law)
    const snellScene = {
      schemaVersion: '1.0',
      id: 'OPT-SNELL-01',
      domain: 'optics',
      subtype: 'interface_refraction',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { boundaryY: 300, normalX: 400, sourcePosition: { x: 220, y: 120 } },
      parameters: {
        n1: { value: 1.0, status: 'known' },
        n2: { value: 1.5, status: 'known' }
      }
    };
    const snellOut = await runtime.load(snellScene);
    assert(snellOut.subtype === 'interface_refraction', 'Interface refraction routes to snell solver');
    assert(snellOut.state.solution.theta2Deg !== undefined, 'Calculates refracted angle theta2');

    // 4. Missing n1/n2 throws MissingRequiredParameterError (No fallback 1.0 or 1.52)
    const snellMissingNScene = {
      schemaVersion: '1.0',
      id: 'OPT-SNELL-FAIL',
      domain: 'optics',
      subtype: 'interface_refraction',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: { boundaryY: 300, normalX: 400, sourcePosition: { x: 200, y: 100 } },
      parameters: {}
    };
    await assertThrowsAsync(
      async () => runtime.load(snellMissingNScene),
      MissingRequiredParameterError,
      'Snell interface missing n1/n2 throws MissingRequiredParameterError (no fallback)'
    );

    // 5. Prism with explicit geometry
    const prismScene = {
      schemaVersion: '1.0',
      id: 'OPT-PRISM-01',
      domain: 'optics',
      subtype: 'prism',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      geometry: {
        prismVertices: [
          { x: 400, y: 180 },
          { x: 510, y: 380 },
          { x: 290, y: 380 }
        ],
        rayOrigin: { x: 240, y: 220 },
        rayDirection: { x: 1.0, y: 0.15 }
      },
      parameters: {
        refractiveIndex: { value: 1.52, status: 'known' }
      }
    };
    const prismOut = await runtime.load(prismScene);
    assert(prismOut.subtype === 'prism', 'Prism routes to prism solver');
    assert(prismOut.state.solution.rays !== undefined, 'Prism traces internal refraction rays');

    // 6. Missing prism vertices throws MissingRequiredParameterError (NO synthetic equilateral prism!)
    const prismMissingVerts = {
      schemaVersion: '1.0',
      id: 'OPT-PRISM-FAIL',
      domain: 'optics',
      subtype: 'prism',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: { refractiveIndex: { value: 1.52, status: 'known' } }
    };
    await assertThrowsAsync(
      async () => runtime.load(prismMissingVerts),
      MissingRequiredParameterError,
      'Prism missing vertices throws MissingRequiredParameterError (no synthetic prism)'
    );
  }

  // ---------------------------------------------------------------
  // 5. CIRCUITS ROUTING & GENERIC SI OUTPUT
  // ---------------------------------------------------------------
  console.log('\n[5/8] Testing Circuits routing (dc / MNA) & generic SI output:');
  {
    const runtime = new PhysicsRuntime();

    const circuitScene = {
      schemaVersion: '1.0',
      id: 'CIRC-DC-01',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 500 },
      parameters: {
        V1: { value: 12, unit: 'V', status: 'known' },
        R1: { value: 6, unit: 'Ω', status: 'known' }
      },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N1' }, { id: 'N0' }],
        components: [
          { id: 'V1', type: 'voltage_source', voltage: 12, nodes: ['N1', 'N0'] },
          { id: 'R1', type: 'resistor', resistance: 6, nodes: ['N1', 'N0'] }
        ]
      }
    };
    const circOut = await runtime.load(circuitScene);
    assert(circOut.subtype === 'dc', 'Circuit routes to dc/MNA solver');
    assert(circOut.state.nodeVoltages['N1'] === 12, 'Node N1 voltage is 12 V');
    assert(Math.abs(circOut.state.branchCurrents['R1'] - 2.0) < 1e-4, 'Current through R1 is 2.0 A');

    // Verify Generic Output has NO hardcoded fixture assumptions
    assert(circOut.state.nodeV1 === undefined, 'State does NOT contain fixture-specific nodeV1');
    assert(circOut.state.currentR1_mA === undefined, 'State does NOT contain fixture-specific currentR1_mA');
    assert(circOut.state.type === undefined, 'State does NOT contain hardcoded type "series_parallel"');
  }

  // ---------------------------------------------------------------
  // 6. ATOMIC PARAMETER UPDATES, UNITS & STUDENT PROVENANCE
  // ---------------------------------------------------------------
  console.log('\n[6/8] Testing atomic parameter updates, units & student provenance:');
  {
    const runtime = new PhysicsRuntime();

    const circuitScene = {
      schemaVersion: '1.0',
      id: 'CIRC-ATOMIC-01',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 500 },
      parameters: {
        V1: { value: 12, unit: 'V', status: 'known' },
        R1: { value: 10, unit: 'Ω', status: 'known' },
        R2: { value: 20, unit: 'Ω', status: 'known' }
      },
      circuit: {
        reference_node: 'N0',
        nodes: [{ id: 'N1' }, { id: 'N2' }, { id: 'N0' }],
        components: [
          { id: 'V1', type: 'voltage_source', voltage: 12, nodes: ['N1', 'N0'] },
          { id: 'R1', type: 'resistor', resistance: 10, nodes: ['N1', 'N2'] },
          { id: 'R2', type: 'resistor', resistance: 20, nodes: ['N2', 'N0'] }
        ]
      }
    };
    await runtime.load(circuitScene);
    assertClose(runtime.getState().nodeVoltages['N2'], 8.0, 0.1, 'Initial N2 voltage is 8.0 V');

    // 1. ATOMIC FAILURE: Invalid string value throws error AND leaves scene completely unchanged!
    assertThrows(
      () => runtime.updateParameter('R2', 'hello_corrupted_value'),
      PhysicsSceneValidationError,
      'Invalid non-numeric parameter throws PhysicsSceneValidationError'
    );
    assert(runtime.scene.parameters.R2.value === 20, 'Scene parameter was NOT mutated on validation failure');
    assertClose(runtime.getState().nodeVoltages['N2'], 8.0, 0.1, 'Solver state was NOT mutated on validation failure');

    // 2. ATOMIC FAILURE: Non-positive resistance throws error AND leaves scene unchanged
    assertThrows(
      () => runtime.updateParameter('R2', -5),
      PhysicsSceneValidationError,
      'Negative resistance throws PhysicsSceneValidationError'
    );
    assert(runtime.scene.parameters.R2.value === 20, 'Scene parameter was NOT mutated on negative resistance');

    // 3. OPERATIONAL UNIT CONVERSION: update with kΩ converts to Ω
    runtime.updateParameter({ targetId: 'R2', key: 'resistance', value: 0.02, unit: 'kΩ' }); // 0.02 kΩ = 20 Ω -> let's make it 0.01 kΩ = 10 Ω
    runtime.updateParameter({ targetId: 'R2', key: 'resistance', value: 0.01, unit: 'kΩ' }); // 10 Ω
    assert(runtime.scene.parameters.R2.value === 10, '0.01 kΩ converted to 10 Ω');
    assertClose(runtime.getState().nodeVoltages['N2'], 6.0, 0.1, 'Recalculates N2 to 6.0 V (10Ω / 10Ω divider)');
    assert(runtime.scene.parameters.R2.provenance === 'student', 'R2 provenance updated to "student"');

    // 4. PENDULUM OPERATIONAL UNITS: cm to m
    const pendulumScene = {
      schemaVersion: '1.0',
      id: 'MECH-UNIT-01',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        length: { value: 1.0, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 0.1, unit: 'rad', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed', source: 'ideal_pendulum_model' }
      },
      objects: [{ id: 'p', type: 'pendulum', geometry: { pivot: { x: 400, y: 100 }, string_length_px: 200, bob_radius_px: 20 } }]
    };
    await runtime.load(pendulumScene);
    assertClose(runtime.getState().length, 1.0, 0.01, 'Initial length is 1.0 m');

    runtime.updateParameter({ key: 'length', value: 80, unit: 'cm' });
    assertClose(runtime.getState().length, 0.8, 0.01, '80 cm live update converted to 0.8 m in solver');
    assert(runtime.scene.parameters.length.value === 0.8, 'Scene parameter stored as 0.8 m');

    // Angle update in rad: 0.5 rad stays 0.5 rad, not 0.5 deg!
    runtime.updateParameter({ key: 'initialAngle', value: 0.5, unit: 'rad' });
    assertClose(runtime.getState().thetaRad, 0.5, 0.01, '0.5 rad live update maintained as 0.5 rad (not 0.5 deg)');

    // 5. PROJECTILE LIVE PARAMETER UPDATE
    const projScene = {
      schemaVersion: '1.0',
      id: 'MECH-PROJ-UPDATE',
      domain: 'mechanics',
      subtype: 'projectile',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      calibration: { pixels_per_meter: 50.0 },
      parameters: {
        speed: { value: 10, unit: 'm/s', status: 'known' },
        angle: { value: 45, unit: 'deg', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' }
      },
      objects: [{ id: 'b', type: 'projectile', geometry: { launch_source_px: { x: 100, y: 500 }, radius_source_px: 18.0 } }]
    };
    await runtime.load(projScene);
    assertClose(runtime.getState().speed, 10, 0.1, 'Initial projectile speed is 10 m/s');

    runtime.updateParameter('speed', 30);
    assertClose(runtime.getState().speed, 30, 0.1, 'Projectile solver updated speed to 30 m/s');
    runtime.step(0.5);
    // x = 30 * cos(45) * 0.5 = 21.21 * 0.5 = ~10.6 m
    assertClose(runtime.getState().xM, 10.6, 0.3, 'Step reflects updated speed (x ~ 10.6 m)');
  }

  // ---------------------------------------------------------------
  // 7. LIFECYCLE & RESET SEMANTICS
  // ---------------------------------------------------------------
  console.log('\n[7/8] Testing unified runtime lifecycle and clean reset:');
  {
    const runtime = new PhysicsRuntime();

    const pendulumScene = {
      schemaVersion: '1.0',
      id: 'MECH-LIFECYCLE',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {
        length: { value: 1.0, unit: 'm', status: 'known' },
        gravity: { value: 9.81, unit: 'm/s²', status: 'known' },
        initialAngle: { value: 0.3, unit: 'rad', status: 'known' },
        mass: { value: 1.0, unit: 'kg', status: 'known' },
        damping: { value: 0.0, unit: '1/s', status: 'assumed', source: 'ideal_pendulum_model' }
      },
      objects: [{ id: 'p', type: 'pendulum', geometry: { pivot: { x: 400, y: 100 }, string_length_px: 200, bob_radius_px: 20 } }]
    };
    await runtime.load(pendulumScene);
    assert(runtime.running === false, 'Initially paused');

    runtime.start();
    assert(runtime.running === true, 'start() sets running true');

    runtime.step(0.2);
    assert(runtime.getState().time > 0.1, 'Simulation time stepped');
    assert(runtime.getState().thetaRad !== 0.3, 'Angle moved during step');

    runtime.reset();
    assert(runtime.running === false, 'reset() pauses simulation');
    assertClose(runtime.getState().time, 0.0, 0.001, 'reset() returns time to 0.0');
    assertClose(runtime.getState().thetaRad, 0.3, 0.001, 'reset() returns theta to initialAngle (0.3 rad)');
    assertClose(runtime.getState().omega, 0.0, 0.001, 'reset() returns angular velocity to 0.0');

    // 8. Deterministic SolverRegistry verification
    const registry = new SolverRegistry();
    class UnannotatedSolver {}
    assertThrows(
      () => registry.register(UnannotatedSolver),
      Error,
      'SolverRegistry rejects registration of class without domain'
    );
    registry.register('mechanics', UnannotatedSolver);
    assert(registry.get('mechanics') === UnannotatedSolver, 'SolverRegistry registers with explicit domain string');

    // 9. Single Authoritative Physics Kernel shared between Adapter and Simulation
    const mockContainer = {
      clientWidth: 800,
      clientHeight: 600,
      appendChild: () => {},
      removeChild: () => {},
      addEventListener: () => {},
      removeEventListener: () => {}
    };
    if (typeof document === 'undefined') {
      globalThis.document = {
        createElement: () => ({
          style: {},
          getContext: () => new Proxy({}, { get: () => () => {} }),
          addEventListener: () => {},
          removeEventListener: () => {},
          remove: () => {}
        })
      };
      globalThis.ResizeObserver = class {
        observe() {}
        unobserve() {}
        disconnect() {}
      };
      globalThis.requestAnimationFrame = (cb) => setTimeout(cb, 16);
      globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
    }

    const browserRuntime = new PhysicsRuntime();
    await browserRuntime.load(pendulumScene, mockContainer);
    assert(browserRuntime.adapter.sim !== null, 'Browser PendulumSimulation instantiated');
    assert(browserRuntime.adapter.physicsKernel === browserRuntime.adapter.sim.kernel, 'Simulation and Adapter share the EXACT same physics kernel authority');

    // Stepping simulation advances both visible renderer state and canonical telemetry identically
    browserRuntime.adapter.sim.kernel.step(0.1);
    const kernelTheta = browserRuntime.adapter.physicsKernel.theta;
    const simTheta = browserRuntime.adapter.sim.theta;
    const telemetryTheta = browserRuntime.getState().thetaRad;
    assert(simTheta === kernelTheta, 'Renderer theta matches physics kernel exactly');
    assert(telemetryTheta === Number(kernelTheta.toFixed(4)), 'Runtime telemetry reflects active physics kernel with zero drift');
  }

  // ---------------------------------------------------------------
  // 8. STRICT VALIDATION FAILURES & NON-FABRICATION
  // ---------------------------------------------------------------
  console.log('\n[8/8] Testing strict validation failures & non-fabrication:');
  {
    const runtime = new PhysicsRuntime();

    // 1. Missing schemaVersion
    const badScene1 = { id: 'TEST-01', domain: 'mechanics', subtype: 'pendulum', parameters: {} };
    await assertThrowsAsync(
      async () => runtime.load(badScene1),
      PhysicsSceneValidationError,
      'Rejects missing schemaVersion'
    );

    // 2. Unsupported domain
    const badScene2 = { schemaVersion: '1.0', id: 'TEST-02', domain: 'quantum_chromodynamics', subtype: 'gluon', parameters: {} };
    await assertThrowsAsync(
      async () => runtime.load(badScene2),
      PhysicsSceneValidationError,
      'Rejects unsupported domain'
    );

    // 3. Domain Object Mismatch (thin lens object in mechanics domain)
    const badScene3 = {
      schemaVersion: '1.0',
      id: 'TEST-03',
      domain: 'mechanics',
      subtype: 'pendulum',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: { length: { value: 1.0, status: 'known' } },
      objects: [{ id: 'lens_1', type: 'thin_lens', optics: { model: 'thin_lens' } }]
    };
    await assertThrowsAsync(
      async () => runtime.load(badScene3),
      PhysicsSceneValidationError,
      'Rejects domain object mismatch (optical lens in mechanics domain)'
    );

    // 4. Circuit with missing/empty nodes
    const badCirc1 = {
      schemaVersion: '1.0',
      id: 'CIRC-FAIL-01',
      domain: 'circuits',
      subtype: 'dc',
      coordinateSpace: { type: 'source_px', width: 800, height: 600 },
      parameters: {},
      circuit: { nodes: [], components: [] }
    };
    await assertThrowsAsync(
      async () => runtime.load(badCirc1),
      PhysicsSceneValidationError,
      'Rejects circuit with empty nodes'
    );
  }

  console.log('\n====================================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('====================================================\n');

  if (failed > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

runTests();
