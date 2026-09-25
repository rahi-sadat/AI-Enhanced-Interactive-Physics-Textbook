/**
 * engine/core/errors.js
 * 
 * Typed runtime error classes for canonical PhysicsScene validation and execution.
 */

/**
 * Thrown when a PhysicsScene violates structural or semantic schema requirements.
 */
export class PhysicsSceneValidationError extends Error {
  /**
   * @param {Array<{code: string, path: string, message: string}>} issues
   */
  constructor(issues = []) {
    const summary = issues.map(i => `[${i.code}] ${i.path}: ${i.message}`).join('; ');
    super(`PhysicsScene validation failed: ${summary || 'Unknown validation issue'}`);
    this.name = 'PhysicsSceneValidationError';
    this.issues = issues;
  }
}

/**
 * Thrown when an unregistered or unsupported physics domain is requested.
 */
export class UnsupportedPhysicsDomainError extends Error {
  /**
   * @param {string} domain
   */
  constructor(domain) {
    super(`Unsupported physics domain: "${domain}"`);
    this.name = 'UnsupportedPhysicsDomainError';
    this.domain = domain;
  }
}

/**
 * Thrown when a domain subtype is recognized or structurally valid, but has no verified solver.
 */
export class UnsupportedPhysicsSubtypeError extends Error {
  /**
   * @param {string} domain
   * @param {string} subtype
   */
  constructor(domain, subtype) {
    super(`Unsupported physics subtype "${subtype}" for domain "${domain}"`);
    this.name = 'UnsupportedPhysicsSubtypeError';
    this.domain = domain;
    this.subtype = subtype;
  }
}

/**
 * Thrown when a numerical solver requires an explicit parameter that is missing or unknown.
 */
export class MissingRequiredParameterError extends Error {
  /**
   * @param {string} paramName
   * @param {string} [path='']
   */
  constructor(paramName, path = '') {
    super(`Missing required parameter "${paramName}"${path ? ` at ${path}` : ''}`);
    this.name = 'MissingRequiredParameterError';
    this.paramName = paramName;
    this.path = path;
  }
}

/**
 * Thrown when an executable entity does not belong to the declared domain.
 */
export class DomainObjectMismatchError extends Error {
  /**
   * @param {string} domain
   * @param {string} objectType
   * @param {string} [objectId='']
   */
  constructor(domain, objectType, objectId = '') {
    super(`Object "${objectId || 'anonymous'}" of type "${objectType}" is invalid for domain "${domain}"`);
    this.name = 'DomainObjectMismatchError';
    this.domain = domain;
    this.objectType = objectType;
    this.objectId = objectId;
  }
}

/**
 * Thrown when physical-unit parameters (cm, m, etc.) lack explicit or derivable calibration.
 */
export class MissingCalibrationError extends Error {
  /**
   * @param {string} unit
   * @param {string} [paramName='']
   */
  constructor(unit, paramName = '') {
    super(`Missing required coordinate calibration (pixelsPerUnit) for physical-unit parameter "${paramName || 'parameter'}" with unit "${unit}". Physical units require explicit or derivable calibration in coordinateSpace or diagram metadata.`);
    this.name = 'MissingCalibrationError';
    this.unit = unit;
    this.paramName = paramName;
    this.code = 'MISSING_CALIBRATION';
  }
}
