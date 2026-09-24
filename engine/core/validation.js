/**
 * engine/core/validation.js
 * 
 * Strict pre-execution validation layer for canonical PhysicsScene v1.
 * Enforces schema integrity, coordinate space declarations, domain boundaries,
 * and parameter validity before any numerical solver is invoked.
 */

import {
  PhysicsSceneValidationError,
  MissingRequiredParameterError,
  DomainObjectMismatchError
} from './errors.js';

const VALID_DOMAINS = new Set(['mechanics', 'optics', 'circuits']);
const VALID_COORDINATE_TYPES = new Set(['source_px', 'world', 'local']);

const MECHANICS_FORBIDDEN_OBJECT_TYPES = new Set([
  'thin_lens',
  'convex_lens',
  'concave_lens',
  'mirror',
  'spherical_mirror',
  'prism',
  'interface_boundary',
  'resistor',
  'capacitor',
  'inductor',
  'voltage_source',
  'battery'
]);

const OPTICS_FORBIDDEN_OBJECT_TYPES = new Set([
  'pendulum',
  'projectile',
  'block',
  'inclined_plane',
  'spring',
  'resistor',
  'voltage_source',
  'battery'
]);

const CIRCUITS_FORBIDDEN_OBJECT_TYPES = new Set([
  'pendulum',
  'projectile',
  'thin_lens',
  'mirror',
  'prism'
]);

/**
 * Normalizes legacy scene aliases into single canonical fields.
 * Downstream runtime and solvers only ever read `scene.subtype` and `scene.coordinateSpace`.
 * @param {object} rawScene
 * @returns {object} Canonical PhysicsScene
 */
export function normalizeLegacyScene(rawScene) {
  if (!rawScene || typeof rawScene !== 'object') {
    return rawScene;
  }

  const scene = JSON.parse(JSON.stringify(rawScene));

  // 1. Canonical domain
  if (!scene.domain) {
    if (scene.simulation?.domain) {
      scene.domain = scene.simulation.domain;
    } else if (scene.simulation_type === 'kinematics') {
      scene.domain = 'mechanics';
    } else if (scene.simulation_type === 'optics') {
      scene.domain = 'optics';
    } else if (scene.simulation_type === 'circuits') {
      scene.domain = 'circuits';
    }
  }

  // 2. Canonical subtype (eliminate type alias downstream)
  if (!scene.subtype) {
    if (scene.type) {
      scene.subtype = scene.type;
    } else if (scene.simulation?.subtype) {
      scene.subtype = scene.simulation.subtype;
    }
  }
  delete scene.type;

  // Circuit subtype normalization: analysis type "dc"
  if (scene.domain === 'circuits') {
    if (scene.subtype === 'series_parallel' || scene.subtype === 'circuit' || !scene.subtype) {
      scene.subtype = 'dc';
    }
  }

  // 3. Canonical coordinateSpace (eliminate coordinateSystem alias downstream)
  if (!scene.coordinateSpace && scene.coordinateSystem) {
    const cs = scene.coordinateSystem;
    const unit = cs.unit || 'px';

    if (unit === 'm' || unit === 'meters' || unit === 'world') {
      scene.coordinateSpace = {
        type: 'world',
        unit: 'm'
      };
    } else if (unit === 'local') {
      scene.coordinateSpace = {
        type: 'local',
        width: cs.width || 800,
        height: cs.height || 600,
        unit: 'px'
      };
    } else {
      // Default legacy assumption for diagram overlays: source_px
      scene.coordinateSpace = {
        type: 'source_px',
        width: cs.width || scene.source?.width || 800,
        height: cs.height || scene.source?.height || 600,
        unit: 'px'
      };
    }
  }
  delete scene.coordinateSystem;

  // 4. Canonical parameters structure
  if (!scene.parameters) {
    scene.parameters = {};
  }

  return scene;
}

/**
 * Validates a normalized PhysicsScene against structural and domain consistency rules.
 * @param {object} scene - Normalized PhysicsScene
 * @returns {{valid: boolean, issues: Array<{code: string, path: string, message: string}>}}
 */
export function validatePhysicsScene(scene) {
  const issues = [];

  if (!scene || typeof scene !== 'object') {
    return {
      valid: false,
      issues: [{
        code: 'SCENE_NULL_OR_INVALID',
        path: '',
        message: 'Scene must be a non-null object.'
      }]
    };
  }

  // 1. Schema Version
  if (scene.schemaVersion !== '1.0') {
    issues.push({
      code: 'INVALID_SCHEMA_VERSION',
      path: 'schemaVersion',
      message: `Expected schemaVersion "1.0", received "${scene.schemaVersion}".`
    });
  }

  // 2. ID
  if (!scene.id || typeof scene.id !== 'string') {
    issues.push({
      code: 'MISSING_SCENE_ID',
      path: 'id',
      message: 'Scene must possess a non-empty string identifier (id).'
    });
  }

  // 3. Domain
  if (!scene.domain || !VALID_DOMAINS.has(scene.domain)) {
    issues.push({
      code: 'UNSUPPORTED_DOMAIN',
      path: 'domain',
      message: `Domain must be one of: ${[...VALID_DOMAINS].join(', ')}. Got: "${scene.domain}".`
    });
  }

  // 4. Subtype
  if (!scene.subtype || typeof scene.subtype !== 'string' || !scene.subtype.trim()) {
    issues.push({
      code: 'MISSING_SUBTYPE',
      path: 'subtype',
      message: 'Scene must explicitly declare a non-empty subtype string.'
    });
  }

  // 5. Coordinate Space (discriminated union)
  if (!scene.coordinateSpace || typeof scene.coordinateSpace !== 'object') {
    issues.push({
      code: 'MISSING_COORDINATE_SPACE',
      path: 'coordinateSpace',
      message: 'Scene must declare an explicit coordinateSpace object.'
    });
  } else {
    const cs = scene.coordinateSpace;
    if (!cs.type || !VALID_COORDINATE_TYPES.has(cs.type)) {
      issues.push({
        code: 'INVALID_COORDINATE_SPACE_TYPE',
        path: 'coordinateSpace.type',
        message: `Coordinate space type must be one of: ${[...VALID_COORDINATE_TYPES].join(', ')}. Got: "${cs.type}".`
      });
    } else if (cs.type === 'source_px' || cs.type === 'local') {
      if (!Number.isFinite(cs.width) || cs.width <= 0) {
        issues.push({
          code: 'INVALID_COORDINATE_DIMENSIONS',
          path: 'coordinateSpace.width',
          message: `Coordinate space "${cs.type}" requires a positive finite width. Got: ${cs.width}.`
        });
      }
      if (!Number.isFinite(cs.height) || cs.height <= 0) {
        issues.push({
          code: 'INVALID_COORDINATE_DIMENSIONS',
          path: 'coordinateSpace.height',
          message: `Coordinate space "${cs.type}" requires a positive finite height. Got: ${cs.height}.`
        });
      }
    } else if (cs.type === 'world') {
      if (!cs.unit || typeof cs.unit !== 'string') {
        issues.push({
          code: 'MISSING_WORLD_UNIT',
          path: 'coordinateSpace.unit',
          message: 'World coordinate space must specify a physical unit (e.g. "m").'
        });
      }
    }
  }

  // 6. Parameters Validation
  if (!scene.parameters || typeof scene.parameters !== 'object') {
    issues.push({
      code: 'MISSING_PARAMETERS_DICTIONARY',
      path: 'parameters',
      message: 'Scene must possess a parameters dictionary.'
    });
  } else {
    for (const [key, param] of Object.entries(scene.parameters)) {
      if (!param || typeof param !== 'object') {
        issues.push({
          code: 'INVALID_PARAMETER_SPEC',
          path: `parameters.${key}`,
          message: `Parameter "${key}" must be an object specification.`
        });
        continue;
      }

      const status = param.status || 'known';
      if (status === 'known') {
        if (param.value !== undefined && param.value !== null) {
          if (typeof param.value === 'number' && !Number.isFinite(param.value)) {
            issues.push({
              code: 'NON_FINITE_PARAMETER_VALUE',
              path: `parameters.${key}.value`,
              message: `Known parameter "${key}" contains non-finite value: ${param.value}.`
            });
          }
        }
      }
    }
  }

  // 7. Domain Object Integrity Checks
  const objects = scene.objects || [];
  const objectIds = new Set();

  for (let i = 0; i < objects.length; i++) {
    const obj = objects[i];
    if (!obj || typeof obj !== 'object') continue;

    const objId = obj.id || `obj_${i}`;
    if (objectIds.has(objId)) {
      issues.push({
        code: 'DUPLICATE_OBJECT_ID',
        path: `objects[${i}].id`,
        message: `Duplicate object identifier "${objId}".`
      });
    }
    objectIds.add(objId);

    const objType = obj.type || obj.optics?.model || '';

    if (scene.domain === 'mechanics' && MECHANICS_FORBIDDEN_OBJECT_TYPES.has(objType)) {
      issues.push({
        code: 'DOMAIN_OBJECT_MISMATCH',
        path: `objects[${i}]`,
        message: `Optical/electrical object "${objId}" of type "${objType}" cannot exist in mechanics domain.`
      });
    }

    if (scene.domain === 'optics' && OPTICS_FORBIDDEN_OBJECT_TYPES.has(objType)) {
      issues.push({
        code: 'DOMAIN_OBJECT_MISMATCH',
        path: `objects[${i}]`,
        message: `Mechanics/electrical object "${objId}" of type "${objType}" cannot exist in optics domain.`
      });
    }

    if (scene.domain === 'circuits' && CIRCUITS_FORBIDDEN_OBJECT_TYPES.has(objType)) {
      issues.push({
        code: 'DOMAIN_OBJECT_MISMATCH',
        path: `objects[${i}]`,
        message: `Physical/optical object "${objId}" of type "${objType}" cannot exist in circuits domain.`
      });
    }
  }

  // 8. Circuit Graph Validation (when domain === 'circuits')
  if (scene.domain === 'circuits') {
    if (!scene.circuit || typeof scene.circuit !== 'object') {
      issues.push({
        code: 'MISSING_CIRCUIT_GRAPH',
        path: 'circuit',
        message: 'Circuits domain scene must declare an explicit circuit graph.'
      });
    } else {
      const nodes = scene.circuit.nodes || [];
      const components = scene.circuit.components || [];

      if (!Array.isArray(nodes) || nodes.length === 0) {
        issues.push({
          code: 'EMPTY_CIRCUIT_NODES',
          path: 'circuit.nodes',
          message: 'Circuit graph must contain at least one node.'
        });
      }

      if (!Array.isArray(components) || components.length === 0) {
        issues.push({
          code: 'EMPTY_CIRCUIT_COMPONENTS',
          path: 'circuit.components',
          message: 'Circuit graph must contain at least one component.'
        });
      }

      // Check unique node IDs
      const nodeIds = new Set();
      for (let i = 0; i < nodes.length; i++) {
        const nid = typeof nodes[i] === 'string' ? nodes[i] : nodes[i]?.id;
        if (!nid) {
          issues.push({
            code: 'MALFORMED_NODE_ID',
            path: `circuit.nodes[${i}]`,
            message: 'Circuit node must possess a valid identifier.'
          });
        } else if (nodeIds.has(nid)) {
          issues.push({
            code: 'DUPLICATE_NODE_ID',
            path: `circuit.nodes[${i}]`,
            message: `Duplicate circuit node identifier "${nid}".`
          });
        }
        if (nid) nodeIds.add(nid);
      }

      // Check components
      const componentIds = new Set();
      for (let i = 0; i < components.length; i++) {
        const comp = components[i];
        if (!comp || !comp.id) {
          issues.push({
            code: 'MALFORMED_COMPONENT_ID',
            path: `circuit.components[${i}]`,
            message: 'Circuit component must possess a valid identifier (id).'
          });
          continue;
        }

        if (componentIds.has(comp.id)) {
          issues.push({
            code: 'DUPLICATE_COMPONENT_ID',
            path: `circuit.components[${i}].id`,
            message: `Duplicate circuit component identifier "${comp.id}".`
          });
        }
        componentIds.add(comp.id);

        // Verify connected terminals reference existing nodes
        const termNodes = comp.nodes || (Array.isArray(comp.terminals) ? comp.terminals.map(t => t.node).filter(Boolean) : []);
        for (const tNode of termNodes) {
          if (!nodeIds.has(tNode)) {
            issues.push({
              code: 'UNKNOWN_COMPONENT_NODE_REFERENCE',
              path: `circuit.components[${i}]`,
              message: `Component "${comp.id}" references undeclared node "${tNode}".`
            });
          }
        }
      }
    }
  }

  return {
    valid: issues.length === 0,
    issues
  };
}

/**
 * Asserts scene matches expected domain.
 * @param {object} scene
 * @param {string} domain
 */
export function assertDomain(scene, domain) {
  if (scene.domain !== domain) {
    throw new PhysicsSceneValidationError([{
      code: 'UNEXPECTED_DOMAIN',
      path: 'domain',
      message: `Expected domain "${domain}", got "${scene.domain}".`
    }]);
  }
}

/**
 * Asserts scene matches expected subtype.
 * @param {object} scene
 * @param {string} subtype
 */
export function assertSubtype(scene, subtype) {
  if (scene.subtype !== subtype) {
    throw new PhysicsSceneValidationError([{
      code: 'UNEXPECTED_SUBTYPE',
      path: 'subtype',
      message: `Expected subtype "${subtype}", got "${scene.subtype}".`
    }]);
  }
}
