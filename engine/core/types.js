/**
 * engine/core/types.js
 * 
 * JSDoc type contracts reflecting shared/schemas/physicsScene.schema.json.
 * Serves as documentation and IDE type hints; schema.json remains the source of truth.
 */

/**
 * @typedef {Object} SourcePixelCoordinateSpace
 * @property {"source_px"} type
 * @property {number} width - Native diagram width in pixels
 * @property {number} height - Native diagram height in pixels
 * @property {"px"} [unit="px"]
 */

/**
 * @typedef {Object} WorldCoordinateSpace
 * @property {"world"} type
 * @property {"m"|"cm"|"km"} unit - Real-world physical unit
 * @property {number} [originX=0]
 * @property {number} [originY=0]
 */

/**
 * @typedef {Object} LocalCoordinateSpace
 * @property {"local"} type
 * @property {number} width - Standard viewport width
 * @property {number} height - Standard viewport height
 * @property {"px"} [unit="px"]
 */

/**
 * Authoritative coordinate space definition (discriminated union).
 * @typedef {SourcePixelCoordinateSpace | WorldCoordinateSpace | LocalCoordinateSpace} CoordinateSpace
 */

/**
 * @typedef {"known" | "symbolic" | "unknown"} ParameterStatus
 */

/**
 * @typedef {"detected" | "derived" | "assumption" | "student" | "teacher" | "system" | "observed" | "author_override" | "default" | "user"} ParameterSource
 */

/**
 * @typedef {Object} ParameterControl
 * @property {"slider" | "number" | "toggle" | "select"} type
 * @property {number} [min]
 * @property {number} [max]
 * @property {number} [step]
 * @property {Array<string|number>} [options]
 */

/**
 * @template [T=number]
 * @typedef {Object} ParameterSpec
 * @property {T} [value] - Current parameter value
 * @property {ParameterStatus} [status="known"] - Evidentiary status
 * @property {string} [unit] - Physical unit (e.g. "m", "kg", "V", "Ω")
 * @property {boolean} [editable=true] - Whether interactive controls can mutate this
 * @property {ParameterSource} [provenance="observed"] - Origin of this value
 * @property {string} [source] - Descriptive source string
 * @property {number} [confidence] - Confidence score (0.0 to 1.0)
 * @property {string} [label] - Human-readable parameter label
 * @property {ParameterControl} [control] - UI control specification
 * @property {string} [description] - Educational or contextual description
 */

/**
 * Canonical PhysicsScene Specification v1.
 * @typedef {Object} PhysicsSceneV1
 * @property {"1.0"} schemaVersion
 * @property {string} id - Unique identifier (e.g. PHY-MECH-001)
 * @property {"mechanics" | "optics" | "circuits"} domain
 * @property {string} subtype - Canonical subtype (e.g. pendulum, projectile, thin_lens, spherical_mirror, interface_refraction, prism, dc)
 * @property {CoordinateSpace} coordinateSpace
 * @property {Record<string, ParameterSpec>} parameters
 * @property {string} [title]
 * @property {string} [description]
 * @property {Array<object>} [objects]
 * @property {object} [environment]
 * @property {object} [circuit]
 * @property {object} [geometry]
 * @property {object} [visual]
 * @property {object} [metadata]
 */

/**
 * Normalized runtime output produced by any specialized domain solver.
 * @typedef {Object} RuntimeOutput
 * @property {"mechanics" | "optics" | "circuits"} domain
 * @property {string} subtype
 * @property {number} time - Simulation epoch time in seconds
 * @property {object} state - Solved numerical states (e.g. angles, voltages, ray counts)
 * @property {object} geometry - Renderable landmarks and vectors
 * @property {Record<string, unknown>} telemetry - Physical calculations for HUD overlays
 * @property {Array<object>} events - Discrete events occurring during step
 * @property {Record<string, ParameterSpec>} editableParameters - Live parameter specs with provenance
 */

export {};
