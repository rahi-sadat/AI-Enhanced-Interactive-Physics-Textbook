/**
 * core/coordinateMapper.js
 * 
 * Single authoritative coordinate transformation service.
 * Translates between native source image pixels (geometry space)
 * and responsive CSS/Device pixels matching CSS:
 *   object-fit: contain;
 *   object-position: 50% 50%;
 */

export class CoordinateMapper {
  /**
   * @param {number} sourceWidth - Natural width of source diagram image in px
   * @param {number} sourceHeight - Natural height of source diagram image in px
   * @param {number} viewportWidth - CSS clientWidth of container
   * @param {number} viewportHeight - CSS clientHeight of container
   * @param {number} [dpr=1] - Window devicePixelRatio
   */
  constructor(sourceWidth, sourceHeight, viewportWidth = 800, viewportHeight = 600, dpr = 1) {
    this.sourceWidth = Math.max(1, Number(sourceWidth) || 800);
    this.sourceHeight = Math.max(1, Number(sourceHeight) || 600);
    this.dpr = Number(dpr) || 1;
    this.updateViewport(viewportWidth, viewportHeight, this.dpr);
  }

  /**
   * Updates viewport and recomputes exact contain letterboxing.
   * @param {number} viewportWidth 
   * @param {number} viewportHeight 
   * @param {number} [dpr=1]
   */
  updateViewport(viewportWidth, viewportHeight, dpr = this.dpr) {
    this.viewportWidth = Math.max(1, Number(viewportWidth) || 800);
    this.viewportHeight = Math.max(1, Number(viewportHeight) || 600);
    this.dpr = Number(dpr) || 1;

    // Uniform scale exactly matching CSS object-fit: contain
    this.scale = Math.min(
      this.viewportWidth / this.sourceWidth,
      this.viewportHeight / this.sourceHeight
    );

    this.renderedWidth = this.sourceWidth * this.scale;
    this.renderedHeight = this.sourceHeight * this.scale;

    // Symmetric letterbox offsets (object-position: 50% 50%)
    this.offsetX = (this.viewportWidth - this.renderedWidth) / 2.0;
    this.offsetY = (this.viewportHeight - this.renderedHeight) / 2.0;
  }

  /**
   * Converts a point from source image pixels to CSS viewport pixels.
   * @param {{x: number, y: number}} pt
   * @returns {{x: number, y: number}}
   */
  sourceToView(pt) {
    if (!pt) return { x: 0, y: 0 };
    return {
      x: pt.x * this.scale + this.offsetX,
      y: pt.y * this.scale + this.offsetY,
    };
  }

  /**
   * Converts a point from CSS viewport pixels back to source image pixels.
   * @param {{x: number, y: number}} pt
   * @returns {{x: number, y: number}}
   */
  viewToSource(pt) {
    if (!pt) return { x: 0, y: 0 };
    return {
      x: (pt.x - this.offsetX) / this.scale,
      y: (pt.y - this.offsetY) / this.scale,
    };
  }

  /**
   * Scales a scalar distance/length from source pixels to CSS viewport pixels.
   * @param {number} len
   * @returns {number}
   */
  sourceLengthToView(len) {
    return (Number(len) || 0) * this.scale;
  }

  /**
   * Scales a scalar distance/length from CSS viewport pixels to source pixels.
   * @param {number} len
   * @returns {number}
   */
  viewLengthToSource(len) {
    return (Number(len) || 0) / this.scale;
  }

  /**
   * Convenience alias: converts (x, y) from source to view space.
   * @param {number} x
   * @param {number} y
   * @returns {{x: number, y: number}}
   */
  point(x, y) {
    return this.sourceToView({ x, y });
  }

  /**
   * Convenience alias: converts scalar length from source to view space.
   * @param {number} val
   * @returns {number}
   */
  length(val) {
    return this.sourceLengthToView(val);
  }

  /**
   * Converts source pixels directly to device screen pixels (accounting for DPR).
   * @param {{x: number, y: number}} pt
   * @returns {{x: number, y: number}}
   */
  sourceToDevice(pt) {
    const v = this.sourceToView(pt);
    return {
      x: v.x * this.dpr,
      y: v.y * this.dpr,
    };
  }

  /**
   * Returns complete mapping metadata for diagnostics and serialization.
   */
  metadata() {
    return {
      source_width_px: this.sourceWidth,
      source_height_px: this.sourceHeight,
      viewport_width_px: this.viewportWidth,
      viewport_height_px: this.viewportHeight,
      scale: this.scale,
      offset_x_px: this.offsetX,
      offset_y_px: this.offsetY,
      rendered_width_px: this.renderedWidth,
      rendered_height_px: this.renderedHeight,
      dpr: this.dpr,
      fit: 'contain',
      position: 'center',
    };
  }
}
