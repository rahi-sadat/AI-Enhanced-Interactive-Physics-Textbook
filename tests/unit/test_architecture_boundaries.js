/**
 * tests/unit/test_architecture_boundaries.js
 * 
 * Strict architectural boundary and static verification test suite for PR-02:
 * 1. Engine / UI Boundary: Verifies 0 imports of `apps/` in `engine/` (except legacy `sceneRouter.js`).
 * 2. SceneRouter Isolation: Verifies canonical PhysicsRuntime and all adapters DO NOT import `sceneRouter.js`.
 * 3. Zero Fabrication / Fallback Patterns: Static scan checking that adapters do not use default fallback strings
 *    such as `?? 'pendulum'` or `|| 'thin_lens'`.
 * 4. Schema Source of Truth: Verifies `shared/schemas/physicsScene.schema.json` defines canonical fields:
 *    - `subtype`
 *    - `coordinateSpace` with discriminated union (`source_px`, `world`, `local`)
 *    - `student` in parameter provenance enum
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '../../');
const engineDir = path.resolve(rootDir, 'engine');

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

console.log('====================================================');
console.log('  TESTING PR-02 ARCHITECTURAL BOUNDARIES & INVARIANTS');
console.log('====================================================\n');

/**
 * Recursively find all JS files in a directory.
 */
function findJsFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const filePath = path.resolve(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      results = results.concat(findJsFiles(filePath));
    } else if (file.endsWith('.js')) {
      results.push(filePath);
    }
  }
  return results;
}

const engineFiles = findJsFiles(engineDir);

// -----------------------------------------------------------------
// 1. ENGINE / UI BOUNDARY VERIFICATION
// -----------------------------------------------------------------
console.log('[1/4] Verifying Engine/UI isolation (0 imports of apps/ in engine/):');
{
  const violations = [];
  for (const file of engineFiles) {
    const relPath = path.relative(rootDir, file).replace(/\\/g, '/');
    const content = fs.readFileSync(file, 'utf-8');
    // Match import ... from '...apps/...' or import('...apps/...')
    const regex = /(from\s+['"][^'"]*apps\/|import\s*\(\s*['"][^'"]*apps\/)/g;
    let match;
    while ((match = regex.exec(content)) !== null) {
      violations.push({ file: relPath, match: match[0] });
    }
  }

  assert(violations.length === 0, `Zero imports of apps/ across all engine files (found ${violations.length})`);
  if (violations.length > 0) {
    console.error('Violations detected:', violations);
  }

  // Verify required PR-03 files exist and renderers do NOT import or invoke numerical physics solvers directly
  const requiredPR03Files = [
    'apps/web/src/features/simulations/core/SimulationRenderer.js',
    'apps/web/src/features/simulations/core/RendererRegistry.js',
    'apps/web/src/features/simulations/optics/OpticsRenderer.js',
    'apps/web/src/features/simulations/circuits/CircuitRenderer.js',
    'apps/web/src/features/simulations/legacy/legacySceneRouter.js',
    'tests/unit/test_interactive_rendering.js'
  ];

  for (const rel of requiredPR03Files) {
    const fullPath = path.resolve(rootDir, rel);
    assert(fs.existsSync(fullPath), `Required PR-03 file must exist: ${rel}`);
  }

  const rendererFiles = [
    'apps/web/src/features/simulations/core/SimulationRenderer.js',
    'apps/web/src/features/simulations/core/RendererRegistry.js',
    'apps/web/src/features/simulations/optics/OpticsRenderer.js',
    'apps/web/src/features/simulations/circuits/CircuitRenderer.js',
  ];

  for (const rel of rendererFiles) {
    const fullPath = path.resolve(rootDir, rel);
    const content = fs.readFileSync(fullPath, 'utf-8');
    const importsSolvers = /(CircuitSolver|CircuitCompiler|thinLensEngine|mirrorEngine|snellInterfaceEngine|prismEngine)/i.test(content);
    assert(!importsSolvers, `${rel} does NOT import or call numerical solvers directly (renderer consumes RuntimeOutput only)`);
  }
}

// -----------------------------------------------------------------
// 2. SCENEROUTER ISOLATION
// -----------------------------------------------------------------
console.log('\n[2/4] Verifying sceneRouter isolation (PhysicsRuntime and adapters must NOT import sceneRouter):');
{
  const targetFiles = [
    'engine/core/PhysicsRuntime.js',
    'engine/core/SimulationAdapter.js',
    'engine/core/SolverRegistry.js',
    'engine/mechanics/MechanicsAdapter.js',
    'engine/optics/OpticsAdapter.js',
    'engine/circuits/CircuitAdapter.js'
  ];

  for (const rel of targetFiles) {
    const fullPath = path.resolve(rootDir, rel);
    const content = fs.readFileSync(fullPath, 'utf-8');
    const importsSceneRouter = /sceneRouter/i.test(content);
    assert(!importsSceneRouter, `${rel} does NOT import or reference sceneRouter`);
  }
}

// -----------------------------------------------------------------
// 3. ZERO FALLBACK CODE PATTERNS
// -----------------------------------------------------------------
console.log('\n[3/4] Verifying zero fallback / fabrication anti-patterns in adapters:');
{
  // 3a. MechanicsAdapter must not fallback to pendulum
  const mechPath = path.resolve(rootDir, 'engine/mechanics/MechanicsAdapter.js');
  const mechContent = fs.readFileSync(mechPath, 'utf-8');
  assert(!mechContent.includes("?? 'pendulum'") && !mechContent.includes('?? "pendulum"'), 'MechanicsAdapter has no ?? "pendulum" fallback');
  assert(!mechContent.includes("|| 'pendulum'") && !mechContent.includes('|| "pendulum"'), 'MechanicsAdapter has no || "pendulum" fallback');
  assert(!mechContent.includes("type === 'pendulum' || true"), 'MechanicsAdapter does not default all types to pendulum');

  // 3b. OpticsAdapter must not fallback to thin_lens
  const optPath = path.resolve(rootDir, 'engine/optics/OpticsAdapter.js');
  const optContent = fs.readFileSync(optPath, 'utf-8');
  assert(!optContent.includes("?? 'thin_lens'") && !optContent.includes('?? "thin_lens"'), 'OpticsAdapter has no ?? "thin_lens" fallback');
  assert(!optContent.includes("|| 'thin_lens'") && !optContent.includes('|| "thin_lens"'), 'OpticsAdapter has no || "thin_lens" fallback');

  // 3c. PhysicsRuntime must not fabricate synthetic scene or fallback dimensions
  const rtPath = path.resolve(rootDir, 'engine/core/PhysicsRuntime.js');
  const rtContent = fs.readFileSync(rtPath, 'utf-8');
  assert(!rtContent.includes('width: 800, height: 600'), 'PhysicsRuntime does not fabricate default 800x600 dimensions');
  assert(!rtContent.includes("domain: 'mechanics'"), 'PhysicsRuntime does not fabricate default mechanics domain');

  // 3d. Verify adapters have NO hidden geometric/physical defaults
  assert(!mechContent.includes('pivot || { x: 400, y: 150 }'), 'MechanicsAdapter has no synthetic pivot fallback');
  assert(!mechContent.includes('angleDeg = 45.0'), 'MechanicsAdapter has no default 45 deg projectile angle');
  assert(!mechContent.includes('let damping = 0.0;'), 'MechanicsAdapter has no silent damping fallback (0.0)');
  assert(!mechContent.includes('|| 24'), 'MechanicsAdapter has no fallback bob radius (24px)');
  assert(!mechContent.includes('|| 18.0'), 'MechanicsAdapter has no fallback projectile radius (18px)');
  assert(!mechContent.includes('|| 50.0'), 'MechanicsAdapter has no fallback ppm (50)');
  assert(!optContent.includes('let n = 1.52;'), 'OpticsAdapter has no fallback prism refractive index');
  assert(!optContent.includes('let n1 = 1.0;'), 'OpticsAdapter has no fallback Snell n1');
  assert(!optContent.includes('let n2 = 1.52;'), 'OpticsAdapter has no fallback Snell n2');
  assert(!optContent.includes('|| 10.0'), 'OpticsAdapter has no fallback world bounds (10.0)');

  const circPath = path.resolve(rootDir, 'engine/circuits/CircuitAdapter.js');
  const circContent = fs.readFileSync(circPath, 'utf-8');
  assert(!circContent.includes("scene.subtype || 'dc'"), 'CircuitAdapter requires explicit subtype (no fallback to "dc")');
  assert(!circContent.includes("nodeV1:"), 'CircuitAdapter has no hardcoded nodeV1 fixture state');
  assert(!circContent.includes("currentR1_mA:"), 'CircuitAdapter has no hardcoded currentR1_mA fixture state');
}

// -----------------------------------------------------------------
// 4. JSON SCHEMA SOURCE OF TRUTH VERIFICATION
// -----------------------------------------------------------------
console.log('\n[4/4] Verifying shared/schemas/physicsScene.schema.json as authoritative source of truth:');
{
  const schemaPath = path.resolve(rootDir, 'shared/schemas/physicsScene.schema.json');
  assert(fs.existsSync(schemaPath), 'Schema file exists');
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));

  // Schema explicitly requires subtype and coordinateSpace
  assert(schema.required?.includes('subtype'), 'Schema requires "subtype"');
  assert(schema.required?.includes('coordinateSpace'), 'Schema requires "coordinateSpace"');

  // Canonical subtype field exists
  assert(Boolean(schema.properties?.subtype), 'Schema defines canonical "subtype" property');

  // CoordinateSpace discriminated union exists
  const coordSpaceDef = schema.definitions?.coordinateSpace || schema.properties?.coordinateSpace;
  assert(Boolean(coordSpaceDef), 'Schema defines "coordinateSpace" property or definition');
  const oneOf = coordSpaceDef?.oneOf || schema.definitions?.coordinateSpace?.oneOf;
  assert(Array.isArray(oneOf) && oneOf.length >= 3, 'CoordinateSpace is a discriminated union with at least 3 variants (source_px, world, local)');

  // Provenance contains 'student'
  const paramProp = schema.properties?.parameters?.additionalProperties;
  const provenanceProp = paramProp?.properties?.provenance;
  const enumVals = provenanceProp?.enum || [];
  assert(enumVals.includes('student'), 'Parameter provenance enum includes "student"');
}

console.log('\n====================================================');
console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
