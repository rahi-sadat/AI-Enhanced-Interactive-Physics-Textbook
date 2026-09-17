/** core/overlayStage.js - 2-layer embedded diagram stage with shared CoordinateMapper. */
import { CoordinateMapper } from './coordinateMapper.js';

export class OverlayStage {
  constructor(o = {}) {
    this.stage     = document.getElementById(o.stageId     || 'diagram-stage');
    this.image     = document.getElementById(o.imageId     || 'diagram-image');
    this.container = document.getElementById(o.containerId || 'simulation-container');
    this.currentSourceW = 800;
    this.currentSourceH = 600;

    const initialViewW = this.stage?.clientWidth || 800;
    const initialViewH = this.stage?.clientHeight || 600;
    this.mapper    = new CoordinateMapper(800, 600, initialViewW, initialViewH);
    this.listeners = [];

    if (this.image) {
      this.image.onload = () => {
        const nw = this.image.naturalWidth || 800;
        const nh = this.image.naturalHeight || 600;
        this.currentSourceW = nw;
        this.currentSourceH = nh;
        const vw = this.stage?.clientWidth || 800;
        const vh = this.stage?.clientHeight || 600;
        this.updateMapper(nw, nh, vw, vh);
      };
    }

    if (typeof ResizeObserver !== 'undefined' && this.stage) {
      this.resizeObserver = new ResizeObserver(() => {
        const vw = this.stage.clientWidth || 800;
        const vh = this.stage.clientHeight || 600;
        this.updateMapper(this.currentSourceW, this.currentSourceH, vw, vh);
      });
      this.resizeObserver.observe(this.stage);
    }
  }

  onMapperChanged(cb) {
    if (typeof cb === 'function') this.listeners.push(cb);
  }

  updateMapper(sourceW, sourceH, viewW = null, viewH = null) {
    this.currentSourceW = sourceW || this.currentSourceW || 800;
    this.currentSourceH = sourceH || this.currentSourceH || 600;
    const vw = viewW ?? (this.stage?.clientWidth || 800);
    const vh = viewH ?? (this.stage?.clientHeight || 600);
    this.mapper.update(this.currentSourceW, this.currentSourceH, vw, vh);
    this.listeners.forEach(cb => {
      try { cb(this.mapper); } catch (e) { console.error('[OverlayStage] listener error:', e); }
    });
  }

  getMapper() {
    return this.mapper;
  }

  setBackground(url, sourceW, sourceH) {
    if (!this.image) return;
    if (!url) {
      this.image.src = '';
      this.image.removeAttribute('src');
      this.image.style.display = 'none';
      const vw = this.stage?.clientWidth || 800;
      const vh = this.stage?.clientHeight || 600;
      this.updateMapper(800, 600, vw, vh);
      return;
    }
    if (sourceW && sourceH) {
      this.currentSourceW = sourceW;
      this.currentSourceH = sourceH;
      const vw = this.stage?.clientWidth || 800;
      const vh = this.stage?.clientHeight || 600;
      this.updateMapper(sourceW, sourceH, vw, vh);
    }
    const isBlobOrData = url.startsWith('blob:') || url.startsWith('data:');
    const finalUrl = isBlobOrData ? url : (url + (url.includes('?') ? '&' : '?') + 't=' + Date.now());
    this.image.src = finalUrl;
    this.image.style.display = 'block';
  }

  setImage(url, sourceW = null, sourceH = null) {
    this.setBackground(url, sourceW, sourceH);
  }

  clearOverlay() {
    while (this.container && this.container.firstChild)
      this.container.removeChild(this.container.firstChild);
  }

  getContainer() { return this.container; }

  destroy() {
    if (this.resizeObserver && this.stage) {
      this.resizeObserver.unobserve(this.stage);
      this.resizeObserver.disconnect();
    }
    this.listeners = [];
  }
}
