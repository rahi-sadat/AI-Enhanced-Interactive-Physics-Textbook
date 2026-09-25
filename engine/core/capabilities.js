/**
 * engine/core/capabilities.js
 * 
 * Domain/subtype-level Simulation Capability Registry.
 * Decouples physical scene representation from interactive UI capabilities.
 * 
 * Core Invariants:
 * 1. Zero Fabrication: Never invents physical parameters or coordinates not already in scene.
 * 2. Role-Based Resolution: Binds interaction targets by semantic role and actual object ID
 *    (e.g. "green_arrow_7", "custom_res_99"), never hardcoded IDs like "object_main" or "R1".
 * 3. Author Overrides Respected: If a parameter or component declares editable === false,
 *    it remains strictly non-editable.
 * 4. Geometry-Conditional Interactions: If required source geometry or calibration is absent,
 *    keeps parameter controls (sliders) available where physically valid, while disabling
 *    only the direct drag handles without fabricating geometry.
 * 5. Evidence-Only Preservation: Physical constants (e.g. gravitational acceleration g) and
 *    citations/references remain non-editable unless explicitly authored as editable.
 */

export const CAPABILITY_DEFINITIONS = {
  optics: {
    thin_lens: {
      parameters: {
        objectDistance: {
          aliases: ['u', 'object_distance', 'u_px', 'u_cm'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        },
        objectHeight: {
          aliases: ['h', 'height', 'object_height', 'h_px', 'h_cm'],
          control: { type: 'slider', min: -200, max: 200, step: 1 }
        },
        focalLength: {
          aliases: ['f', 'focal_length', 'f_px', 'f_cm'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        }
      },
      roles: {
        object: {
          match: (o) => o.role === 'object' || o.type === 'optical_object' || o.type === 'object' || o.optics?.model === 'optical_object',
          handles: {
            translateX: { parameterKey: 'objectDistance' },
            resizeY: { parameterKey: 'objectHeight' }
          }
        }
      }
    },
    spherical_mirror: {
      parameters: {
        objectDistance: {
          aliases: ['u', 'object_distance'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        },
        objectHeight: {
          aliases: ['h', 'object_height'],
          control: { type: 'slider', min: -200, max: 200, step: 1 }
        },
        focalLength: {
          aliases: ['f', 'focal_length'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        }
      },
      roles: {
        object: {
          match: (o) => o.role === 'object' || o.type === 'optical_object' || o.type === 'object' || o.optics?.model === 'optical_object',
          handles: {
            translateX: { parameterKey: 'objectDistance' },
            resizeY: { parameterKey: 'objectHeight' }
          }
        }
      }
    },
    mirror: {
      parameters: {
        objectDistance: {
          aliases: ['u', 'object_distance'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        },
        objectHeight: {
          aliases: ['h', 'object_height'],
          control: { type: 'slider', min: -200, max: 200, step: 1 }
        },
        focalLength: {
          aliases: ['f', 'focal_length'],
          control: { type: 'slider', min: 10, max: 500, step: 1 }
        }
      },
      roles: {
        object: {
          match: (o) => o.role === 'object' || o.type === 'optical_object' || o.type === 'object' || o.optics?.model === 'optical_object',
          handles: {
            translateX: { parameterKey: 'objectDistance' },
            resizeY: { parameterKey: 'objectHeight' }
          }
        }
      }
    },
    interface_refraction: {
      parameters: {
        theta1: {
          aliases: ['incidentAngle', 'incident_angle_deg', 'theta1Deg'],
          control: { type: 'slider', min: 0, max: 89, step: 1 }
        },
        n1: {
          aliases: ['refractiveIndex1'],
          control: { type: 'slider', min: 1.0, max: 3.5, step: 0.01 }
        },
        n2: {
          aliases: ['refractiveIndex2'],
          control: { type: 'slider', min: 1.0, max: 3.5, step: 0.01 }
        }
      },
      roles: {
        interface: {
          match: (o) => o.type === 'interface' || o.type === 'boundary' || o.role === 'interface',
          handles: {
            dragAngle: { parameterKey: 'theta1' }
          }
        }
      }
    },
    prism: {
      parameters: {
        refractiveIndex: {
          aliases: ['n', 'refractive_index'],
          control: { type: 'slider', min: 1.0, max: 2.5, step: 0.01 }
        },
        theta1: {
          aliases: ['incidentAngle'],
          control: { type: 'slider', min: 0, max: 89, step: 1 }
        }
      },
      roles: {}
    }
  },
  mechanics: {
    pendulum: {
      parameters: {
        length: {
          aliases: ['length_m', 'string_length', 'L'],
          control: { type: 'slider', min: 0.2, max: 5.0, step: 0.05 }
        },
        initialAngle: {
          aliases: ['theta0', 'angle', 'theta0_rad', 'theta0_deg'],
          control: { type: 'slider', min: -80, max: 80, step: 1 }
        }
      },
      // Note: gravity and mass are evidence-only, NOT in parameters map
      roles: {
        bob: {
          match: (o) => o.type === 'pendulum' || o.role === 'bob' || o.role === 'dynamic',
          handles: {
            dragAngle: { parameterKey: 'initialAngle' }
          }
        }
      }
    },
    projectile: {
      parameters: {
        speed: {
          aliases: ['speed_m_s', 'v0', 'launch_speed'],
          control: { type: 'slider', min: 1, max: 100, step: 1 }
        },
        angle: {
          aliases: ['launch_angle_deg', 'angleDeg', 'theta'],
          control: { type: 'slider', min: 0, max: 90, step: 1 }
        }
      },
      // Note: gravity is evidence-only, NOT in parameters map
      roles: {
        projectile: {
          match: (o) => o.type === 'projectile' || o.type === 'circle' || o.role === 'projectile',
          handles: {
            dragVelocity: { parameterKeys: ['speed', 'angle'] }
          }
        }
      }
    }
  },
  circuits: {
    _componentTypes: {
      resistor: {
        parameterKey: 'resistance',
        control: { type: 'slider', min: 1, max: 1000, step: 1 }
      },
      voltage_source: {
        parameterKey: 'voltage',
        control: { type: 'slider', min: 0, max: 100, step: 1 }
      },
      battery: {
        parameterKey: 'voltage',
        control: { type: 'slider', min: 0, max: 100, step: 1 }
      },
      switch: {
        parameterKey: 'closed',
        control: { type: 'toggle' },
        click: 'closed'
      }
    }
  }
};

export class SimulationCapabilityRegistry {
  constructor() {
    this._definitions = new Map();
    this._registerDefaults();
  }

  _registerDefaults() {
    for (const [domain, subObj] of Object.entries(CAPABILITY_DEFINITIONS)) {
      if (domain === 'circuits') {
        this._definitions.set('circuits:*', subObj);
      } else {
        for (const [subtype, def] of Object.entries(subObj)) {
          this._definitions.set(`${domain}:${subtype}`, def);
        }
      }
    }
  }

  /**
   * Registers a capability definition for a specific domain and subtype.
   * @param {string} domain
   * @param {string} subtype
   * @param {object} definition
   */
  register(domain, subtype, definition) {
    this._definitions.set(`${domain}:${subtype}`, definition);
  }

  /**
   * Retrieves the capability definition for domain and subtype.
   * @param {string} domain
   * @param {string} subtype
   * @returns {object|null}
   */
  get(domain, subtype) {
    if (this._definitions.has(`${domain}:${subtype}`)) {
      return this._definitions.get(`${domain}:${subtype}`);
    }
    if (domain === 'circuits' && this._definitions.has('circuits:*')) {
      return this._definitions.get('circuits:*');
    }
    return null;
  }

  /**
   * Checks whether capability definition exists for domain and subtype.
   * @param {string} domain
   * @param {string} [subtype]
   * @returns {boolean}
   */
  has(domain, subtype = null) {
    return Boolean(this.get(domain, subtype));
  }

  /**
   * Resolves interactive capabilities for a canonical PhysicsScene.
   * Enriches ONLY existing valid parameters and components without fabricating values or geometry.
   * Respects explicit author overrides (editable === false).
   * 
   * @param {object} scene - Validated canonical PhysicsScene
   * @returns {object} Capability-enriched scene
   */
  resolve(scene) {
    if (!scene || typeof scene !== 'object') {
      return scene;
    }

    if (scene._capabilitiesResolved) {
      return scene;
    }

    const domain = scene.domain || scene.simulation?.domain;
    const subtype = scene.subtype || scene.type;
    const cap = this.get(domain, subtype);

    if (!cap && domain !== 'circuits') {
      return scene;
    }

    // Work on a deep clone to preserve caller's reference integrity
    const resolved = JSON.parse(JSON.stringify(scene));
    resolved._capabilitiesResolved = true;
    if (!resolved.parameters) {
      resolved.parameters = {};
    }

    // 1. Enrich existing scene parameters for optics and mechanics
    if (cap?.parameters) {
      for (const [capKey, capDef] of Object.entries(cap.parameters)) {
        const match = this._findExistingParameter(resolved.parameters, capKey, capDef.aliases);
        if (match) {
          const { key: actualKey, param } = match;
          // Zero fabrication: Only enrich if value is defined and finite/boolean
          if (param && (Number.isFinite(Number(param.value)) || typeof param.value === 'boolean')) {
            // Author override: If author explicitly set editable === false, NEVER override
            if (param.editable !== false) {
              param.editable = true;
              param.control = {
                type: param.control?.type || capDef.control?.type || 'slider',
                min: param.control?.min ?? param.min ?? capDef.control?.min ?? 0,
                max: param.control?.max ?? param.max ?? capDef.control?.max ?? 100,
                step: param.control?.step ?? param.step ?? capDef.control?.step ?? 1
              };
            }
          }
        }
      }
    }

    // 2. Enrich circuit components by component type
    if (domain === 'circuits' || resolved.circuit?.components) {
      const compTypes = cap?._componentTypes || CAPABILITY_DEFINITIONS.circuits._componentTypes;
      if (Array.isArray(resolved.circuit?.components)) {
        for (const comp of resolved.circuit.components) {
          const typeDef = compTypes[comp.type];
          if (!typeDef) continue;

          // If author explicitly declared editable === false, preserve it
          if (comp.editable === false || comp.parameter?.editable === false) {
            continue;
          }

          comp.editable = true;
          if (comp.type === 'switch') {
            comp.control = comp.control || { type: 'toggle' };
            const swParam = resolved.parameters[comp.id] || resolved.parameters[`${comp.id}.closed`];
            if (swParam && swParam.editable !== false) {
              swParam.editable = true;
              swParam.control = swParam.control || { type: 'toggle' };
            }
          } else {
            const pKey = typeDef.parameterKey; // 'resistance' or 'voltage'
            const defaultMin = typeDef.control.min;
            const defaultMax = comp.value ? Math.max(typeDef.control.max, comp.value * 2) : typeDef.control.max;
            const defaultStep = typeDef.control.step;

            comp.control = comp.control || {
              type: 'slider',
              min: comp.min ?? comp.parameter?.min ?? defaultMin,
              max: comp.max ?? comp.parameter?.max ?? defaultMax,
              step: comp.step ?? comp.parameter?.step ?? defaultStep
            };

            const cParam = resolved.parameters[comp.id] || resolved.parameters[`${comp.id}.${pKey}`];
            if (cParam && cParam.editable !== false) {
              cParam.editable = true;
              cParam.control = {
                type: cParam.control?.type || 'slider',
                min: cParam.control?.min ?? cParam.min ?? comp.control.min,
                max: cParam.control?.max ?? cParam.max ?? comp.control.max,
                step: cParam.control?.step ?? cParam.step ?? comp.control.step
              };
            }
          }
        }
      }
    }

    // 3. Resolve semantic object roles and bind interactions with actual object IDs
    if (cap?.roles && Array.isArray(resolved.objects)) {
      const interactions = resolved.interactions || {};

      for (const [roleName, roleDef] of Object.entries(cap.roles)) {
        const matchingObj = resolved.objects.find(o => roleDef.match(o));
        if (!matchingObj) continue;

        const targetId = matchingObj.id;
        if (!targetId) continue;

        // Verify required scene geometry / calibration for direct manipulation
        const geomSupported = this._isDirectManipulationSupported(resolved, domain, subtype, matchingObj);

        if (geomSupported) {
          matchingObj.editable = true;
          interactions[targetId] = {
            targetId,
            role: roleName,
            handles: {}
          };

          // Attach handles ONLY for parameters that ACTUALLY EXIST
          for (const [handleType, handleConfig] of Object.entries(roleDef.handles || {})) {
            if (handleConfig.parameterKey) {
              const pKey = handleConfig.parameterKey;
              const hasParam = this._findExistingParameter(resolved.parameters, pKey, cap.parameters?.[pKey]?.aliases);
              if (hasParam && hasParam.param?.editable !== false) {
                interactions[targetId].handles[handleType] = {
                  parameter: hasParam.key,
                  parameterKey: pKey
                };
                if (!hasParam.param.targetId) {
                  hasParam.param.targetId = targetId;
                }
              }
            } else if (Array.isArray(handleConfig.parameterKeys)) {
              const boundKeys = [];
              for (const pKey of handleConfig.parameterKeys) {
                const hasParam = this._findExistingParameter(resolved.parameters, pKey, cap.parameters?.[pKey]?.aliases);
                if (hasParam && hasParam.param?.editable !== false) {
                  boundKeys.push({ parameter: hasParam.key, parameterKey: pKey });
                  if (!hasParam.param.targetId) {
                    hasParam.param.targetId = targetId;
                  }
                }
              }
              if (boundKeys.length > 0) {
                interactions[targetId].handles[handleType] = {
                  parameters: boundKeys
                };
              }
            }
          }
        }
      }

      resolved.interactions = interactions;
    }

    return resolved;
  }

  /**
   * Finds an existing parameter by canonical key or its aliases.
   * Never fabricates if not found.
   * @private
   */
  _findExistingParameter(parameters, canonicalKey, aliases = []) {
    if (!parameters || typeof parameters !== 'object') return null;

    // 1. Direct match
    if (parameters[canonicalKey] !== undefined) {
      return { key: canonicalKey, param: parameters[canonicalKey] };
    }

    // 2. Alias match
    for (const alias of aliases) {
      if (parameters[alias] !== undefined) {
        return { key: alias, param: parameters[alias] };
      }
    }

    // 3. Scoped match (e.g. "obj_1.objectDistance")
    for (const [k, p] of Object.entries(parameters)) {
      if (k.endsWith(`.${canonicalKey}`)) {
        return { key: k, param: p };
      }
      for (const alias of aliases) {
        if (k.endsWith(`.${alias}`)) {
          return { key: k, param: p };
        }
      }
    }

    return null;
  }

  /**
   * Verifies if required scene geometry/calibration exists for direct manipulation.
   * Prevents fabricating coordinates.
   * @private
   */
  _isDirectManipulationSupported(scene, domain, subtype, object) {
    if (domain === 'optics') {
      const geom = scene.geometry || {};
      const hasLensX = geom.lensX != null || geom.lens_center != null || geom.mirrorX != null;
      const hasAxisY = geom.axisY != null || geom.optical_axis_y != null;
      if (subtype === 'thin_lens' || subtype === 'mirror' || subtype === 'spherical_mirror') {
        return Boolean(hasLensX && hasAxisY);
      }
      if (subtype === 'interface_refraction') {
        return Boolean(object.geometry?.boundary != null || geom.interface != null || geom.boundary != null);
      }
      return false;
    }

    if (domain === 'mechanics') {
      if (subtype === 'pendulum') {
        const pivot = object.geometry?.pivot || scene.geometry?.pivot || object.pivot;
        return Boolean(pivot && Number.isFinite(pivot.x) && Number.isFinite(pivot.y));
      }
      if (subtype === 'projectile') {
        const launch = object.geometry?.launch_source_px || scene.geometry?.launch_source || object.initial_position;
        return Boolean(launch && Number.isFinite(launch.x) && Number.isFinite(launch.y));
      }
      return false;
    }

    return true;
  }
}

export const defaultCapabilityRegistry = new SimulationCapabilityRegistry();
