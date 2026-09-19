/**
 * apps/web/src/components/FigureViewport.js
 * 
 * Layout-Invariant Augmented Figure Viewport.
 * Sole authority responsible for image + overlay registration,
 * container ResizeObserver, aspect-ratio preservation, and coordinate mapping.
 * 
 * Guarantee:
 * Regardless of sidebar open/close, book column width, responsive breakpoints,
 * or UI rearrangement, the simulation overlay remains attached to the exact
 * native pixels of the textbook diagram (anchor error ≤ 1–2 CSS px).
 */

import { CoordinateMapper } from '@engine/core/coordinateMapper.js';

export class FigureViewport {
  /**
   * @param {HTMLElement} hostElement - DOM element hosting the viewport
   * @param {object} [options={}]
   * @param {number} [options.sourceWidth=800]
   * @param {number} [options.sourceHeight=600]
   * @param {string} [options.imageUrl=null]
   * @param {Function} [options.onLayoutChange=null]
   */
  constructor(hostElement, options = {}) {
    if (!hostElement) {
      throw new Error('[FigureViewport] Host element is required.');
    }

    this.host = hostElement;
    this.sourceW = Math.max(1, Number(options.sourceWidth) || 800);
    this.sourceH = Math.max(1, Number(options.sourceHeight) || 600);
    this.imageUrl = options.imageUrl || null;

    this.mapper = new CoordinateMapper(this.sourceW, this.sourceH, 800, 600);
    this.listeners = new Set();
    if (typeof options.onLayoutChange === 'function') {
      this.listeners.add(options.onLayoutChange);
    }

    this.showInspectAnchors = false;
    this.calibrationAnchors = [];

    this._dom = {
      viewport: null,
      image: null,
      overlay: null,
      reticleLayer: null,
    };

    this._resizeObserver = null;
    this._renderScaffold();

    if (this.imageUrl) {
      this.setBackground(this.imageUrl, this.sourceW, this.sourceH);
    } else {
      this.recalculate();
    }
  }

  _renderScaffold() {
    this.host.innerHTML = '';

    const viewport = document.createElement('div');
    viewport.className = 'figure-viewport';
    viewport.style.position = 'relative';
    viewport.style.width = '100%';
    viewport.style.height = '100%';
    viewport.style.overflow = 'hidden';
    viewport.style.display = 'block';

    const img = document.createElement('img');
    img.className = 'figure-viewport-img';
    img.alt = 'Textbook diagram reference';
    img.style.position = 'absolute';
    img.style.display = 'none';
    img.style.userSelect = 'none';
    img.style.pointerEvents = 'none';
    img.style.zIndex = '1';

    const overlay = document.createElement('div');
    overlay.className = 'figure-viewport-overlay';
    overlay.style.position = 'absolute';
    overlay.style.zIndex = '2';
    overlay.style.touchAction = 'none';
    overlay.style.pointerEvents = 'auto';

    const reticleLayer = document.createElement('div');
    reticleLayer.className = 'figure-viewport-reticle-layer';
    reticleLayer.style.position = 'absolute';
    reticleLayer.style.inset = '0';
    reticleLayer.style.pointerEvents = 'none';
    reticleLayer.style.zIndex = '10';
    reticleLayer.style.display = 'none';

    viewport.appendChild(img);
    viewport.appendChild(overlay);
    viewport.appendChild(reticleLayer);
    this.host.appendChild(viewport);

    this._dom.viewport = viewport;
    this._dom.image = img;
    this._dom.overlay = overlay;
    this._dom.reticleLayer = reticleLayer;

    // Observe size changes of the viewport itself (not merely window resize)
    if (typeof ResizeObserver !== 'undefined') {
      this._resizeObserver = new ResizeObserver(() => {
        this.recalculate();
      });
      this._resizeObserver.observe(viewport);
    }
  }

  /**
   * Sets diagram background image and source dimensions.
   * @param {string} url
   * @param {number} [sourceW]
   * @param {number} [sourceH]
   */
  async setBackground(url, sourceW = null, sourceH = null) {
    if (sourceW && sourceW > 0) this.sourceW = Number(sourceW);
    if (sourceH && sourceH > 0) this.sourceH = Number(sourceH);

    const img = this._dom.image;
    if (!url) {
      this.imageUrl = null;
      img.src = '';
      img.style.display = 'none';
      this.recalculate();
      return;
    }

    this.imageUrl = url;
    img.src = url;
    img.style.display = 'block';

    await this._waitForImage(img);

    // If source dimensions were not explicitly passed, infer from natural image
    if ((!sourceW || !sourceH) && img.naturalWidth > 0 && img.naturalHeight > 0) {
      this.sourceW = img.naturalWidth;
      this.sourceH = img.naturalHeight;
    }

    this.recalculate();
  }

  async _waitForImage(img) {
    if (img.complete && img.naturalWidth > 0) return;

    if (typeof img.decode === 'function') {
      try {
        await img.decode();
        return;
      } catch (_) {
        // Fallback to load event if decode fails on certain SVGs
      }
    }

    await new Promise((resolve) => {
      const onDone = () => {
        img.removeEventListener('load', onDone);
        img.removeEventListener('error', onDone);
        resolve();
      };
      img.addEventListener('load', onDone, { once: true });
      img.addEventListener('error', onDone, { once: true });
    });
  }

  /**
   * Sets source dimensions without changing background URL.
   */
  setSourceDimensions(sourceW, sourceH) {
    if (sourceW > 0) this.sourceW = Number(sourceW);
    if (sourceH > 0) this.sourceH = Number(sourceH);
    this.recalculate();
  }

  /**
   * Authoritative recalculation of uniform aspect-ratio contain scaling
   * and symmetrical letterbox/pillarbox offsets.
   */
  recalculate() {
    const vp = this._dom.viewport;
    if (!vp) return this.getRenderContext();

    const viewW = vp.clientWidth || vp.getBoundingClientRect().width || 800;
    const viewH = vp.clientHeight || vp.getBoundingClientRect().height || 600;

    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
    this.mapper.update(this.sourceW, this.sourceH, viewW, viewH, dpr);

    const rect = this.mapper.renderedImageRect;

    // Both image and overlay consume the exact same rendered rectangle
    const img = this._dom.image;
    if (img) {
      img.style.left = `${rect.left}px`;
      img.style.top = `${rect.top}px`;
      img.style.width = `${rect.width}px`;
      img.style.height = `${rect.height}px`;
    }

    const overlay = this._dom.overlay;
    if (overlay) {
      overlay.style.left = `${rect.left}px`;
      overlay.style.top = `${rect.top}px`;
      overlay.style.width = `${rect.width}px`;
      overlay.style.height = `${rect.height}px`;
    }

    const context = this.getRenderContext();

    if (this.showInspectAnchors) {
      this._renderReticles(context);
    }

    // Notify listeners (renderers and adapters)
    for (const listener of this.listeners) {
      try {
        listener(context);
      } catch (err) {
        console.error('[FigureViewport] Error in layout listener:', err);
      }
    }

    return context;
  }

  /**
   * Returns current render context transform.
   */
  getRenderContext() {
    return this.mapper.getRenderContext();
  }

  /**
   * Returns the overlay DOM container element.
   * @returns {HTMLElement}
   */
  getOverlayContainer() {
    return this._dom.overlay;
  }

  /**
   * Returns the outer viewport element.
   * @returns {HTMLElement}
   */
  getViewportElement() {
    return this._dom.viewport;
  }

  /**
   * Subscribes to layout changes.
   * @param {Function} callback
   * @returns {Function} Unsubscribe function
   */
  onLayoutChange(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Configures known physical anchor points for precision calibration inspection.
   * @param {Array<{id: string, label: string, x: number, y: number, color?: string}>} anchors
   */
  setCalibrationAnchors(anchors = []) {
    this.calibrationAnchors = anchors;
    if (this.showInspectAnchors) {
      this._renderReticles(this.getRenderContext());
    }
  }

  /**
   * Toggles the alignment calibration inspection layer.
   * @param {boolean} enable
   */
  setInspectAnchors(enable) {
    this.showInspectAnchors = Boolean(enable);
    if (this._dom.reticleLayer) {
      this._dom.reticleLayer.style.display = this.showInspectAnchors ? 'block' : 'none';
    }
    if (this.showInspectAnchors) {
      this._renderReticles(this.getRenderContext());
    }
  }

  _renderReticles(context) {
    const layer = this._dom.reticleLayer;
    if (!layer) return;

    layer.innerHTML = '';
    if (!this.calibrationAnchors || this.calibrationAnchors.length === 0) return;

    for (const anchor of this.calibrationAnchors) {
      // Anchor screen position relative to viewport
      const screenPt = context.toScreen(anchor.x, anchor.y);
      const reticle = document.createElement('div');
      reticle.className = 'figure-alignment-reticle';
      reticle.style.position = 'absolute';
      reticle.style.left = `${screenPt.x}px`;
      reticle.style.top = `${screenPt.y}px`;
      reticle.style.transform = 'translate(-50%, -50%)';
      reticle.style.pointerEvents = 'none';

      const color = anchor.color || '#38bdf8';

      reticle.innerHTML = `
        <div style="position:relative; width:24px; height:24px; display:flex; align-items:center; justify-content:center;">
          <!-- Crosshairs -->
          <div style="position:absolute; width:24px; height:1px; background:${color}; box-shadow:0 0 4px ${color};"></div>
          <div style="position:absolute; width:1px; height:24px; background:${color}; box-shadow:0 0 4px ${color};"></div>
          <!-- Center ring -->
          <div style="width:10px; height:10px; border-radius:50%; border:1.5px solid ${color}; box-sizing:border-box;"></div>
          <!-- Label & Coordinates badge -->
          <div style="position:absolute; top:14px; left:14px; background:rgba(15,23,42,0.85); color:${color}; border:1px solid ${color}; padding:2px 6px; border-radius:4px; font-size:10px; font-family:monospace; white-space:nowrap;">
            ${anchor.label || anchor.id} (${Math.round(anchor.x)}, ${Math.round(anchor.y)})
          </div>
        </div>
      `;

      layer.appendChild(reticle);
    }
  }

  destroy() {
    if (this._resizeObserver) {
      this._resizeObserver.disconnect();
      this._resizeObserver = null;
    }
    this.listeners.clear();
    this.host.innerHTML = '';
  }
}
