/**
 * core/matterUnitAdapter.js
 * 
 * Bridges SI physical units (m/s², m/s, meters, kg) with Matter.js internal conventions.
 * Matter.js default gravity.scale is 0.001 and normalizes velocities relative to a 60 Hz step.
 */

export class MatterUnitAdapter {
  /**
   * @param {number} [pixelsPerMeter=100] - Visual calibration scale
   */
  constructor(pixelsPerMeter = 100) {
    this.ppm = Math.max(1e-3, Number(pixelsPerMeter) || 100);
  }

  /**
   * Updates pixels per meter calibration.
   * @param {number} ppm
   */
  setPixelsPerMeter(ppm) {
    if (ppm && ppm > 0) {
      this.ppm = ppm;
    }
  }

  /**
   * Configures Matter.js engine gravity to match true SI acceleration g (m/s²).
   * @param {import('matter-js').Engine} engine
   * @param {number} gMS2 - Gravitational acceleration in m/s² (e.g. 9.81)
   */
  setGravity(engine, gMS2) {
    if (!engine) return;
    engine.gravity.x = 0;
    engine.gravity.y = 1;
    // Matter integrates using millisecond timestep: dt = 16.67ms
    // gravity force applied per ms²: scale = (g * ppm) / 1,000,000
    engine.gravity.scale = (Number(gMS2) * this.ppm) / 1_000_000;
  }

  /**
   * Converts physical velocity in m/s to Matter.js internal velocity units.
   * @param {number} vMS - Velocity in m/s
   * @returns {number}
   */
  velocityMpsToMatter(vMS) {
    // Matter velocity represents pixels per 60Hz frame
    return (Number(vMS) * this.ppm) / 60.0;
  }

  /**
   * Converts Matter.js internal velocity to physical m/s.
   * @param {number} matterV
   * @returns {number}
   */
  velocityMatterToMps(matterV) {
    return (Number(matterV) * 60.0) / this.ppm;
  }
}
