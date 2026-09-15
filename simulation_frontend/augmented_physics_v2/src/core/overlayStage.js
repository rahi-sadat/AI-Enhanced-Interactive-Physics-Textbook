/**
 * core/overlayStage.js
 * 
 * Manages the 2-layer embedded diagram stage:
 * Layer 1: Background textbook diagram (or clean inpainted static background)
 * Layer 2: Interactive physics/optics simulation canvas overlay
 */

export class OverlayStage {
  constructor(o = {}) {
    this.image = document.getElementById(o.imageId || 'diagram-image');
    this.container = document.getElementById(o.containerId || 'simulation-container');

    if (this.image) {
      this.image.style.objectFit = 'contain';
      this.image.style.objectPosition = '50% 50%';
    }
  }

  /**
   * Sets background diagram image with cache-busting timestamp.
   * @param {string|null} url
   */
  setBackground(url) {
    if (!this.image) return;
    if (!url) {
      this.image.src = '';
      this.image.removeAttribute('src');
      this.image.style.display = 'none';
      return;
    }
    this.image.style.objectFit = 'contain';
    this.image.style.objectPosition = '50% 50%';
    this.image.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
    this.image.style.display = 'block';
  }

  /**
   * Clears any active canvas elements inside simulation container.
   */
  clearOverlay() {
    while (this.container && this.container.firstChild) {
      this.container.removeChild(this.container.firstChild);
    }
  }

  getContainer() {
    return this.container;
  }

  /**
   * Gets current CSS client dimensions of container.
   * @returns {{width: number, height: number}}
   */
  getViewportSize() {
    return {
      width: this.container?.clientWidth || 800,
      height: this.container?.clientHeight || 600,
    };
  }
}
