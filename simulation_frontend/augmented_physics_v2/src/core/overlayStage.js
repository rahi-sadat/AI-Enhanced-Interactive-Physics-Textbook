/** core/overlayStage.js - 2-layer embedded diagram stage. */
export class OverlayStage {
  constructor(o = {}) {
    this.image     = document.getElementById(o.imageId     || 'diagram-image');
    this.container = document.getElementById(o.containerId || 'simulation-container');
  }
  setBackground(url) {
    if (!this.image) return;
    if (!url) {
      this.image.src = '';
      this.image.removeAttribute('src');
      this.image.style.display = 'none';
      return;
    }
    this.image.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
    this.image.style.display = 'block';
  }
  clearOverlay() {
    while (this.container && this.container.firstChild)
      this.container.removeChild(this.container.firstChild);
  }
  getContainer() { return this.container; }
}
