/**
 * engine/core/units.js
 * 
 * Operational physical units conversion and validation.
 * Ensures parameters are verified and converted to canonical solver units
 * rather than blindly relying on anonymous numeric values.
 */

import { MissingRequiredParameterError, PhysicsSceneValidationError } from './errors.js';

// Unit conversion factors to canonical SI base units
const LENGTH_FACTORS = {
  m: 1.0,
  meter: 1.0,
  meters: 1.0,
  cm: 0.01,
  centimeter: 0.01,
  centimeters: 0.01,
  mm: 0.001,
  millimeter: 0.001,
  km: 1000.0,
};

const ANGLE_FACTORS_TO_RAD = {
  rad: 1.0,
  radian: 1.0,
  radians: 1.0,
  deg: Math.PI / 180.0,
  degree: Math.PI / 180.0,
  degrees: Math.PI / 180.0,
  '°': Math.PI / 180.0,
};

const RESISTANCE_FACTORS = {
  'Ω': 1.0,
  'ohm': 1.0,
  'ohms': 1.0,
  'kΩ': 1000.0,
  'kohm': 1000.0,
  'kohms': 1000.0,
  'MΩ': 1e6,
  'mohm': 1e6,
  'Mohm': 1e6,
};

const VOLTAGE_FACTORS = {
  V: 1.0,
  v: 1.0,
  volt: 1.0,
  volts: 1.0,
  mV: 0.001,
  mv: 0.001,
  millivolt: 0.001,
  kV: 1000.0,
  kv: 1000.0,
  kilovolt: 1000.0,
};

const CURRENT_FACTORS = {
  A: 1.0,
  a: 1.0,
  amp: 1.0,
  amps: 1.0,
  ampere: 1.0,
  mA: 0.001,
  ma: 0.001,
  milliamp: 0.001,
  uA: 1e-6,
  ua: 1e-6,
  'µA': 1e-6,
  'µa': 1e-6,
};

const MASS_FACTORS = {
  kg: 1.0,
  kilogram: 1.0,
  g: 0.001,
  gram: 0.001,
};

const TIME_FACTORS = {
  s: 1.0,
  sec: 1.0,
  second: 1.0,
  seconds: 1.0,
  ms: 0.001,
  millisecond: 0.001,
  min: 60.0,
  minute: 60.0,
};

const ACCEL_FACTORS = {
  'm/s²': 1.0,
  'm/s^2': 1.0,
  'm/s2': 1.0,
};

const VELOCITY_FACTORS = {
  'm/s': 1.0,
  'km/h': 1.0 / 3.6,
  'cm/s': 0.01,
};

/**
 * Normalizes a unit string for lookup.
 * @param {string} unit
 * @returns {string}
 */
export function normalizeUnitString(unit) {
  if (!unit) return '';
  const trimmed = String(unit).trim();
  // Standardize micro symbol
  if (trimmed === 'µA' || trimmed === 'μA') return 'uA';
  // Common Greek and symbol matches
  if (['Ω', 'kΩ', 'MΩ', '°', 'm/s²', 'm/s^2', 'm/s2', 'uA', 'mA', 'mV', 'kV', 'V', 'A', 'm/s', 'km/h', 'cm/s'].includes(trimmed)) {
    return trimmed;
  }
  return trimmed.toLowerCase();
}

/**
 * Converts a numerical value from one unit to another.
 * @param {number} value
 * @param {string} fromUnit
 * @param {string} toUnit
 * @returns {number}
 */
export function convertUnit(value, fromUnit, toUnit) {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    throw new TypeError(`Cannot convert non-finite value: ${value}`);
  }

  const uFrom = normalizeUnitString(fromUnit);
  const uTo = normalizeUnitString(toUnit);

  if (uFrom === uTo || !fromUnit || !toUnit) {
    return value;
  }

  // Length
  if (uFrom in LENGTH_FACTORS && uTo in LENGTH_FACTORS) {
    return (value * LENGTH_FACTORS[uFrom]) / LENGTH_FACTORS[uTo];
  }

  // Angle
  if (uFrom in ANGLE_FACTORS_TO_RAD && uTo in ANGLE_FACTORS_TO_RAD) {
    const rad = value * ANGLE_FACTORS_TO_RAD[uFrom];
    return rad / ANGLE_FACTORS_TO_RAD[uTo];
  }

  // Resistance
  if (uFrom in RESISTANCE_FACTORS && uTo in RESISTANCE_FACTORS) {
    return (value * RESISTANCE_FACTORS[uFrom]) / RESISTANCE_FACTORS[uTo];
  }

  // Voltage
  if (uFrom in VOLTAGE_FACTORS && uTo in VOLTAGE_FACTORS) {
    return (value * VOLTAGE_FACTORS[uFrom]) / VOLTAGE_FACTORS[uTo];
  }

  // Current
  if (uFrom in CURRENT_FACTORS && uTo in CURRENT_FACTORS) {
    return (value * CURRENT_FACTORS[uFrom]) / CURRENT_FACTORS[uTo];
  }

  // Mass
  if (uFrom in MASS_FACTORS && uTo in MASS_FACTORS) {
    return (value * MASS_FACTORS[uFrom]) / MASS_FACTORS[uTo];
  }

  // Time
  if (uFrom in TIME_FACTORS && uTo in TIME_FACTORS) {
    return (value * TIME_FACTORS[uFrom]) / TIME_FACTORS[uTo];
  }

  // Acceleration
  if (uFrom in ACCEL_FACTORS && uTo in ACCEL_FACTORS) {
    return value;
  }

  // Velocity
  if (uFrom in VELOCITY_FACTORS && uTo in VELOCITY_FACTORS) {
    return (value * VELOCITY_FACTORS[uFrom]) / VELOCITY_FACTORS[uTo];
  }

  throw new Error(`Incompatible units for conversion: cannot convert "${fromUnit}" to "${toUnit}".`);
}

/**
 * Resolves a parameter specification from a scene by key or targeted path.
 * Supports:
 *   - "length"
 *   - "R2.resistance"
 *   - "components.R2.resistance"
 * @param {object} scene
 * @param {string} address
 * @returns {object|null}
 */
export function resolveParameterSpec(scene, address) {
  if (!scene) return null;

  // 1. Direct top-level parameters lookup
  if (scene.parameters && scene.parameters[address]) {
    return scene.parameters[address];
  }

  // 2. Environment lookup
  if (scene.environment && scene.environment[address] !== undefined) {
    const val = scene.environment[address];
    if (typeof val === 'object' && val !== null && 'value' in val) {
      return val;
    }
    return { value: val, status: 'known', source: 'environment' };
  }

  // 3. Dot-notated addressing (e.g. R2.resistance or components.R2.resistance)
  const parts = address.split('.');
  if (parts.length >= 2) {
    const componentId = parts[parts.length - 2];
    const paramKey = parts[parts.length - 1];

    // Check circuit components
    if (scene.circuit?.components) {
      const comp = scene.circuit.components.find(c => c.id === componentId);
      if (comp) {
        if (comp.parameters?.[paramKey]) return comp.parameters[paramKey];
        if (comp[paramKey] !== undefined) {
          const v = comp[paramKey];
          return typeof v === 'object' && v !== null && 'value' in v ? v : { value: v, status: 'known' };
        }
      }
    }

    // Check scene objects
    if (scene.objects) {
      const obj = scene.objects.find(o => o.id === componentId);
      if (obj) {
        if (obj.physics?.[paramKey] !== undefined) {
          const v = obj.physics[paramKey];
          return typeof v === 'object' && v !== null && 'value' in v ? v : { value: v, status: 'known' };
        }
        if (obj.parameters?.[paramKey]) return obj.parameters[paramKey];
      }
    }
  }

  // 4. Fallback search by object/component id in circuit components or objects
  if (scene.circuit?.components) {
    const comp = scene.circuit.components.find(c => c.id === address);
    if (comp) {
      // Find main parameter (e.g. resistance or voltage)
      if (comp.parameters?.resistance) return comp.parameters.resistance;
      if (comp.parameters?.voltage) return comp.parameters.voltage;
      if (comp.resistance !== undefined) return { value: comp.resistance, status: 'known', unit: 'Ω' };
      if (comp.voltage !== undefined) return { value: comp.voltage, status: 'known', unit: 'V' };
    }
  }

  return null;
}

/**
 * Extracts a required known parameter and converts it to the requested canonical unit.
 * Throws PhysicsSceneValidationError if missing, unknown, or unit is incompatible.
 * @param {object} scene - Canonical PhysicsScene
 * @param {string} address - Parameter key or address (e.g. "length" or "R2.resistance")
 * @param {string} [targetUnit] - Canonical solver unit (e.g. "m", "rad", "Ω")
 * @param {object} [options={}] - Optional settings (e.g. defaultUnit)
 * @returns {number}
 */
export function getParameterInUnit(scene, address, targetUnit = null, options = {}) {
  const spec = resolveParameterSpec(scene, address);

  if (!spec) {
    throw new PhysicsSceneValidationError([{
      code: 'MISSING_REQUIRED_PARAMETER',
      path: `parameters.${address}`,
      message: `Required parameter "${address}" is missing from scene.`
    }]);
  }

  if (spec.status === 'unknown') {
    throw new PhysicsSceneValidationError([{
      code: 'PARAMETER_VALUE_UNKNOWN',
      path: `parameters.${address}`,
      message: `Required parameter "${address}" status is marked as unknown.`
    }]);
  }

  const rawValue = spec.value;
  if (rawValue === null || rawValue === undefined || !Number.isFinite(Number(rawValue))) {
    throw new PhysicsSceneValidationError([{
      code: 'INVALID_PARAMETER_VALUE',
      path: `parameters.${address}.value`,
      message: `Parameter "${address}" value is not a valid finite number: ${rawValue}`
    }]);
  }

  const numVal = Number(rawValue);
  const paramUnit = spec.unit || options.defaultUnit || null;

  if (!targetUnit) {
    return numVal;
  }

  if (!paramUnit) {
    // If scene did not specify unit, assume targetUnit if allowed by options, else warn/use directly
    return numVal;
  }

  try {
    return convertUnit(numVal, paramUnit, targetUnit);
  } catch (err) {
    throw new PhysicsSceneValidationError([{
      code: 'INCOMPATIBLE_UNIT',
      path: `parameters.${address}.unit`,
      message: `Parameter "${address}" unit "${paramUnit}" cannot be converted to required solver unit "${targetUnit}": ${err.message}`
    }]);
  }
}

/**
 * Validates an incoming parameter update and converts it to the canonical target unit.
 * Throws PhysicsSceneValidationError if value is non-finite, unit is incompatible, or target is unknown.
 * @param {object} scene
 * @param {string} address
 * @param {*} rawValue
 * @param {string|null} incomingUnit
 * @param {string|null} canonicalUnit
 * @returns {number} Converted numerical value in canonicalUnit
 */
export function validateAndConvertParameterUpdate(scene, address, rawValue, incomingUnit = null, canonicalUnit = null) {
  if (rawValue === null || rawValue === undefined || !Number.isFinite(Number(rawValue))) {
    throw new PhysicsSceneValidationError([{
      code: 'INVALID_PARAMETER_VALUE',
      path: address,
      message: `Parameter "${address}" value must be a valid finite number: got ${rawValue}`
    }]);
  }

  const numVal = Number(rawValue);
  const targetSpec = resolveParameterSpec(scene, address);
  const effectiveTargetUnit = canonicalUnit || targetSpec?.unit || null;
  const effectiveIncomingUnit = incomingUnit || targetSpec?.unit || null;

  if (effectiveTargetUnit && effectiveIncomingUnit && effectiveTargetUnit !== effectiveIncomingUnit) {
    try {
      return convertUnit(numVal, effectiveIncomingUnit, effectiveTargetUnit);
    } catch (err) {
      throw new PhysicsSceneValidationError([{
        code: 'INCOMPATIBLE_UNIT',
        path: address,
        message: `Cannot update "${address}" with unit "${effectiveIncomingUnit}": incompatible with target unit "${effectiveTargetUnit}".`
      }]);
    }
  }

  return numVal;
}
