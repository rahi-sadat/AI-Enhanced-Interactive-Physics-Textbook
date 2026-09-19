/**
 * tests/unit/test_figure_viewport_fixtures.js
 * 
 * Architectural Milestone Verification: Layout-Invariant Augmented Figure System.
 * 
 * Verifies that regardless of UI layout changes (sidebar toggle, book width,
 * AI tutor drawer, tablet portrait, mobile width), the simulation overlay remains
 * anchored to the exact source pixels of textbook diagrams with error <= 1-2 CSS px.
 */

import { CoordinateMapper } from '../../engine/core/coordinateMapper.js';

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
  assert(diff <= tol, `${message} (diff: ${diff.toFixed(4)}px, tol: ${tol}px, actual: ${actual.toFixed(2)}, expected: ${expected.toFixed(2)})`);
}

console.log('===============================================================');
console.log('  LAYOUT-INVARIANT AUGMENTED FIGURE SYSTEM FIXTURE TESTS');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// The Three Authoritative Alignment Fixtures
// -----------------------------------------------------------------------------
const FIXTURES = [
  {
    domain: 'mechanics',
    name: 'Fixture 1: Nonlinear Pendulum (NCTB Class 9-10 Ch 4, test1.jpg)',
    sourceWidth: 797,
    sourceHeight: 652,
    anchors: [
      { id: 'pivot', label: 'Pivot Pin', x: 468.0, y: 99.7 },
      { id: 'bob_initial', label: 'Initial Bob Center', x: 246.58, y: 527.56 },
      { id: 'clamp_top', label: 'Support Clamp Top', x: 468.0, y: 30.0 },
    ],
  },
  {
    domain: 'optics',
    name: 'Fixture 2: Thin Convex Lens (NCTB Class 9-10 Ch 6, nctb_lens_diagram.png)',
    sourceWidth: 800,
    sourceHeight: 600,
    anchors: [
      { id: 'optical_center', label: 'Optical Center O', x: 400.0, y: 300.0 },
      { id: 'f1_focus', label: 'F1 Focal Point', x: 270.0, y: 300.0 }, // 400 - 130
      { id: 'f2_focus', label: 'F2 Focal Point', x: 530.0, y: 300.0 }, // 400 + 130
      { id: 'axis_left', label: 'Principal Axis Left', x: 0.0, y: 300.0 },
      { id: 'axis_right', label: 'Principal Axis Right', x: 800.0, y: 300.0 },
    ],
  },
  {
    domain: 'circuits',
    name: 'Fixture 3: DC Series Loop (NCTB Class 9-10 Ch 11, Fig 11.4)',
    sourceWidth: 800,
    sourceHeight: 500,
    anchors: [
      { id: 'battery_v1', label: 'Battery V1 Center', x: 140.0, y: 250.0 },
      { id: 'switch_s1', label: 'Switch S1 Center', x: 230.0, y: 120.0 },
      { id: 'resistor_r1', label: 'Resistor R1 Center', x: 400.0, y: 120.0 },
      { id: 'resistor_r2', label: 'Resistor R2 Center', x: 660.0, y: 250.0 },
      { id: 'junction_n1', label: 'Junction Node N1', x: 140.0, y: 120.0 },
    ],
  },
];

// -----------------------------------------------------------------------------
// The Five Tested Viewport Configurations (Sidebar toggles, breakpoints)
// -----------------------------------------------------------------------------
const VIEWPORTS = [
  { name: '1. Wide Desktop (Sidebar Closed)', width: 1440, height: 900 },
  { name: '2. Standard Book + Controls (Sidebar Open)', width: 850, height: 650 },
  { name: '3. Narrow Column / AI Tutor Drawer Open', width: 600, height: 600 },
  { name: '4. Tablet Portrait Layout', width: 768, height: 1024 },
  { name: '5. Compact Mobile Breakpoint', width: 390, height: 844 },
];

// -----------------------------------------------------------------------------
// Test 1: Layout Invariance & Anchor Sub-Pixel Registration across Viewports
// -----------------------------------------------------------------------------
FIXTURES.forEach((fixture) => {
  console.log(`\n--- Testing ${fixture.name} ---`);
  const { sourceWidth: sw, sourceHeight: sh, anchors } = fixture;

  VIEWPORTS.forEach((vp) => {
    const mapper = new CoordinateMapper(sw, sh, vp.width, vp.height);
    const rect = mapper.renderedImageRect;

    // Verify rendered image bounds are fully contained in viewport
    assert(
      rect.width <= vp.width + 0.001 && rect.height <= vp.height + 0.001,
      `[${vp.name}] Rendered dimensions (${rect.width.toFixed(1)}x${rect.height.toFixed(1)}) fit viewport (${vp.width}x${vp.height})`
    );

    // Verify letterboxing / pillarboxing symmetrical offsets
    assertClose(
      rect.left,
      (vp.width - rect.width) / 2,
      0.001,
      `[${vp.name}] Symmetrical X offset`
    );
    assertClose(
      rect.top,
      (vp.height - rect.height) / 2,
      0.001,
      `[${vp.name}] Symmetrical Y offset`
    );

    // Check each physical anchor point
    anchors.forEach((anchor) => {
      // 1. Where does the diagram pixel appear on screen?
      const diagramScreenX = rect.left + anchor.x * mapper.scale;
      const diagramScreenY = rect.top + anchor.y * mapper.scale;

      // 2. Where does the simulation overlay position this anchor?
      const overlayScreenPt = mapper.sourceToView(anchor.x, anchor.y);
      const localOverlayPt = mapper.sourceToOverlay(anchor.x, anchor.y);
      const reconstructedScreenX = rect.left + localOverlayPt.x;
      const reconstructedScreenY = rect.top + localOverlayPt.y;

      // Error metric: Euclidean distance between diagram pixel and simulation anchor
      const errViewport = Math.hypot(diagramScreenX - overlayScreenPt.x, diagramScreenY - overlayScreenPt.y);
      const errOverlay = Math.hypot(diagramScreenX - reconstructedScreenX, diagramScreenY - reconstructedScreenY);

      assert(
        errViewport <= 0.01 && errOverlay <= 0.01,
        `[${vp.name}] Anchor "${anchor.label}" error = ${errViewport.toFixed(4)}px (Target: <= 1.0px)`
      );

      // Bidirectional dragging inverse mapping: Screen -> Source
      const restoredSource = mapper.viewToSource(diagramScreenX, diagramScreenY);
      const restoredFromOverlay = mapper.overlayToSource(localOverlayPt.x, localOverlayPt.y);

      assertClose(
        restoredSource.x,
        anchor.x,
        0.001,
        `[${vp.name}] Inverse viewToSource X for "${anchor.id}"`
      );
      assertClose(
        restoredSource.y,
        anchor.y,
        0.001,
        `[${vp.name}] Inverse viewToSource Y for "${anchor.id}"`
      );
      assertClose(
        restoredFromOverlay.x,
        anchor.x,
        0.001,
        `[${vp.name}] Inverse overlayToSource X for "${anchor.id}"`
      );
      assertClose(
        restoredFromOverlay.y,
        anchor.y,
        0.001,
        `[${vp.name}] Inverse overlayToSource Y for "${anchor.id}"`
      );
    });
  });
});

// -----------------------------------------------------------------------------
// Test 2: Dynamic Transition / Sidebar Toggle Simulation
// -----------------------------------------------------------------------------
console.log('\n--- Testing Dynamic Sidebar Resize Transition (1440px -> 650px -> 1440px) ---');
const dynMapper = new CoordinateMapper(797, 652, 1440, 900);
const pivotSrc = { x: 468.0, y: 99.7 };

// Initial full desktop
const initialScreen = dynMapper.sourceToView(pivotSrc.x, pivotSrc.y);
console.log(`  Initial screen pivot at 1440x900: (${initialScreen.x.toFixed(2)}, ${initialScreen.y.toFixed(2)})`);

// User opens sidebar: width narrows from 1440 to 650
dynMapper.update(797, 652, 650, 650);
const narrowedScreen = dynMapper.sourceToView(pivotSrc.x, pivotSrc.y);
const narrowedRect = dynMapper.renderedImageRect;
const expectedNarrowX = narrowedRect.left + pivotSrc.x * dynMapper.scale;
const expectedNarrowY = narrowedRect.top + pivotSrc.y * dynMapper.scale;

assertClose(
  narrowedScreen.x,
  expectedNarrowX,
  0.001,
  'Pivot X aligns exactly with narrowed diagram image'
);
assertClose(
  narrowedScreen.y,
  expectedNarrowY,
  0.001,
  'Pivot Y aligns exactly with narrowed diagram image'
);
assert(
  Math.hypot(narrowedScreen.x - expectedNarrowX, narrowedScreen.y - expectedNarrowY) <= 0.01,
  'Pivot drift during sidebar open is 0.00px'
);

// User closes sidebar: width expands back to 1440
dynMapper.update(797, 652, 1440, 900);
const restoredScreen = dynMapper.sourceToView(pivotSrc.x, pivotSrc.y);
assertClose(
  restoredScreen.x,
  initialScreen.x,
  0.001,
  'Pivot X returns to initial position on sidebar close'
);
assertClose(
  restoredScreen.y,
  initialScreen.y,
  0.001,
  'Pivot Y returns to initial position on sidebar close'
);

// -----------------------------------------------------------------------------
// Summary
// -----------------------------------------------------------------------------
console.log('\n===============================================================');
console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
console.log('===============================================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('ALL LAYOUT-INVARIANT FIXTURE TESTS PASSED WITH 0px DRIFT!');
}
