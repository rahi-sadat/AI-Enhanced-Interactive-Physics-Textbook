/**
 * circuits/CircuitHitTest.js
 * Authoritative geometric hit testing performed strictly in source_px coordinates.
 * Converts viewport CSS pointer coordinates via CoordinateMapper before testing
 * against component bounding boxes, terminals, switches, and wire polylines.
 */

export class CircuitHitTest {
  /**
   * Perform hit test at a given CSS point (relative to the container).
   * @param {number} cssX
   * @param {number} cssY
   * @param {object} mapper - CoordinateMapper instance
   * @param {object} model - Compiled CircuitModel
   * @returns {object|null} Hit result
   */
  static hitTest(cssX, cssY, mapper, model) {
    if (!mapper || !model) return null;

    // Convert CSS coordinates to authoritative source_px
    const srcPt = mapper.viewToSource(cssX, cssY);
    const { x, y } = srcPt;

    // 1. Check Switches FIRST (highest priority interactive control)
    for (const sw of model.switches) {
      const swBbox = sw.geometry?.bbox_source_px || [190, 100, 270, 140];
      // Include terminal contacts and clickable badge rendered below lever
      const extendedBbox = [swBbox[0] - 12, swBbox[1] - 12, swBbox[2] + 12, swBbox[3] + 32];
      if (this._isInsideBBox(x, y, extendedBbox, 6)) {
        return {
          type: 'switch',
          id: sw.id,
          component: sw,
          sourcePoint: srcPt
        };
      }
    }

    // 2. Check Terminals (highest precision probe target)
    const snapRadius = 14.0; // in source_px
    for (const [tId, term] of model.terminalById.entries()) {
      const [tx, ty] = term.source_px || [0, 0];
      const dist = Math.hypot(x - tx, y - ty);
      if (dist <= snapRadius) {
        // If this terminal belongs to a switch, treat click as switch toggle
        if (model.switches.some(s => s.id === term.componentId)) {
          return {
            type: 'switch',
            id: term.componentId,
            sourcePoint: { x: tx, y: ty },
            distance: dist
          };
        }
        return {
          type: 'terminal',
          id: tId,
          terminal: term,
          componentId: term.componentId,
          nodeId: term.node,
          sourcePoint: { x: tx, y: ty },
          distance: dist
        };
      }
    }

    // 3. Check Components (resistors, batteries, etc.)
    for (const [cId, comp] of model.componentById.entries()) {
      if (comp.geometry?.bbox_source_px) {
        if (this._isInsideBBox(x, y, comp.geometry.bbox_source_px, 12)) {
          return {
            type: 'component',
            id: cId,
            component: comp,
            sourcePoint: srcPt
          };
        }
      }
    }

    // 4. Check Wire Polylines
    const wireSnapTol = 10.0; // in source_px
    for (const wire of model.wires) {
      const pts = wire.points || [];
      for (let i = 0; i < pts.length - 1; i++) {
        const dist = this._pointToSegmentDist(x, y, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]);
        if (dist <= wireSnapTol) {
          return {
            type: 'wire',
            id: wire.id,
            nodeId: wire.node,
            wire,
            sourcePoint: srcPt,
            distance: dist
          };
        }
      }
    }

    return null;
  }

  static _isInsideBBox(x, y, bbox, padding = 8) {
    const [minX, minY, maxX, maxY] = bbox;
    return (
      x >= minX - padding &&
      x <= maxX + padding &&
      y >= minY - padding &&
      y <= maxY + padding
    );
  }

  static _pointToSegmentDist(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const lenSq = dx * dx + dy * dy;
    if (lenSq === 0) return Math.hypot(px - x1, py - y1);

    // Project point onto segment
    let t = ((px - x1) * dx + (py - y1) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));
    const projX = x1 + t * dx;
    const projY = y1 + t * dy;
    return Math.hypot(px - projX, py - projY);
  }
}
