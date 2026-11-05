/**
 * core/coordinateMapper.js
 * Authoritative, bidirectional coordinate transform between native source image pixels
 * and viewport/canvas pixels, preserving aspect ratio and letterboxing.
 */
export class CoordinateMapper {
  constructor(sourceW = 800, sourceH = 600, viewW = 800, viewH = 600, dpr = (typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1)) {
    this.update(sourceW, sourceH, viewW, viewH, dpr);
  }

  update(sourceW, sourceH, viewW = 800, viewH = 600, dpr = (typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1)) {
    this.sourceW = Math.max(1, Number(sourceW) || 800);
    this.sourceH = Math.max(1, Number(sourceH) || 600);
    this.viewW = Math.max(1, Number(viewW) || 800);
    this.viewH = Math.max(1, Number(viewH) || 600);
    this.dpr = Math.max(1, Number(dpr) || 1);

    this.scale = Math.min(this.viewW / this.sourceW, this.viewH / this.sourceH);
    this.renderedW = this.sourceW * this.scale;
    this.renderedH = this.sourceH * this.scale;

    this.offsetX = (this.viewW - this.renderedW) / 2.0;
    this.offsetY = (this.viewH - this.renderedH) / 2.0;
  }

  sourceToView(x, y) {
    let px = x;
    let py = y;
    if (typeof x === 'object' && x !== null) {
      px = x.x ?? x.left ?? x[0];
      py = x.y ?? x.top ?? x[1];
    }
    return {
      x: Number(px) * this.scale + this.offsetX,
      y: Number(py) * this.scale + this.offsetY,
    };
  }

  viewToSource(x, y) {
    let px = x;
    let py = y;
    if (typeof x === 'object' && x !== null) {
      px = x.x ?? x.left ?? x[0];
      py = x.y ?? x.top ?? x[1];
    }
    return {
      x: (Number(px) - this.offsetX) / this.scale,
      y: (Number(py) - this.offsetY) / this.scale,
    };
  }

  sourceLengthToView(len) {
    return Number(len) * this.scale;
  }

  viewLengthToSource(len) {
    return Number(len) / this.scale;
  }

  sourceVerticesToView(vertices = []) {
    return vertices.map(v => this.sourceToView(v.x ?? v[0], v.y ?? v[1]));
  }

  viewVerticesToSource(vertices = []) {
    return vertices.map(v => this.viewToSource(v.x ?? v[0], v.y ?? v[1]));
  }

  sourceBoxToView(box = {}) {
    const x = box.x ?? box.left ?? 0;
    const y = box.y ?? box.top ?? 0;
    const w = box.w ?? box.width ?? 0;
    const h = box.h ?? box.height ?? 0;
    const p = this.sourceToView(x, y);
    return {
      x: p.x,
      y: p.y,
      width: this.sourceLengthToView(w),
      height: this.sourceLengthToView(h),
    };
  }

  viewBoxToSource(box = {}) {
    const x = box.x ?? box.left ?? 0;
    const y = box.y ?? box.top ?? 0;
    const w = box.w ?? box.width ?? 0;
    const h = box.h ?? box.height ?? 0;
    const p = this.viewToSource(x, y);
    return {
      x: p.x,
      y: p.y,
      width: this.viewLengthToSource(w),
      height: this.viewLengthToSource(h),
    };
  }

  domEventToView(event, containerElement) {
    const rect = containerElement?.getBoundingClientRect ? containerElement.getBoundingClientRect() : { left: 0, top: 0, width: this.viewW, height: this.viewH };
    const clientX = event.clientX ?? (event.touches?.[0]?.clientX ?? 0);
    const clientY = event.clientY ?? (event.touches?.[0]?.clientY ?? 0);

    const cssScaleX = rect.width > 0 ? this.viewW / rect.width : 1;
    const cssScaleY = rect.height > 0 ? this.viewH / rect.height : 1;

    return {
      x: (clientX - rect.left) * cssScaleX,
      y: (clientY - rect.top) * cssScaleY,
    };
  }

  domEventToSource(event, containerElement) {
    const viewPt = this.domEventToView(event, containerElement);
    return this.viewToSource(viewPt.x, viewPt.y);
  }

  get renderedImageRect() {
    return {
      left: this.offsetX,
      top: this.offsetY,
      width: this.renderedW,
      height: this.renderedH,
    };
  }

  sourceToOverlay(x, y) {
    let px = x;
    let py = y;
    if (typeof x === 'object' && x !== null) {
      px = x.x ?? x.left ?? x[0];
      py = x.y ?? x.top ?? x[1];
    }
    return {
      x: Number(px) * this.scale,
      y: Number(py) * this.scale,
    };
  }

  overlayToSource(x, y) {
    let px = x;
    let py = y;
    if (typeof x === 'object' && x !== null) {
      px = x.x ?? x.left ?? x[0];
      py = x.y ?? x.top ?? x[1];
    }
    return {
      x: Number(px) / this.scale,
      y: Number(py) / this.scale,
    };
  }

  getRenderContext() {
    return {
      sourceWidth: this.sourceW,
      sourceHeight: this.sourceH,
      displayWidth: this.renderedW,
      displayHeight: this.renderedH,
      viewportWidth: this.viewW,
      viewportHeight: this.viewH,
      scale: this.scale,
      offsetX: this.offsetX,
      offsetY: this.offsetY,
      dpr: this.dpr,
      renderedImageRect: this.renderedImageRect,
      toScreen: (x, y) => this.sourceToView(x, y),
      toSource: (x, y) => this.viewToSource(x, y),
      toOverlay: (x, y) => this.sourceToOverlay(x, y),
      toSourceFromOverlay: (x, y) => this.overlayToSource(x, y),
    };
  }

  static computeRenderedImageRect(sourceW, sourceH, viewW, viewH) {
    const sw = Math.max(1, Number(sourceW) || 800);
    const sh = Math.max(1, Number(sourceH) || 600);
    const vw = Math.max(1, Number(viewW) || 800);
    const vh = Math.max(1, Number(viewH) || 600);
    const scale = Math.min(vw / sw, vh / sh);
    const renderedW = sw * scale;
    const renderedH = sh * scale;
    const offsetX = (vw - renderedW) / 2.0;
    const offsetY = (vh - renderedH) / 2.0;
    return {
      scale,
      renderedW,
      renderedH,
      offsetX,
      offsetY,
      left: offsetX,
      top: offsetY,
      width: renderedW,
      height: renderedH,
    };
  }

  metadata() {
    return {
      source_width_px: this.sourceW,
      source_height_px: this.sourceH,
      view_width_px: this.viewW,
      view_height_px: this.viewH,
      uniform_scale: this.scale,
      offset_x_px: this.offsetX,
      offset_y_px: this.offsetY,
      dpr: this.dpr,
      aspect_ratio: this.sourceW / this.sourceH,
    };
  }
}

export function getCanvasSize(scene) {
  const r = scene?.coordinate_system?.render ?? scene?.render ?? {};
  return { width: r.canvas_width_px ?? 800, height: r.canvas_height_px ?? 600 };
}

