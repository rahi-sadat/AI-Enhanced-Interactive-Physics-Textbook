/** optics/view/opticsSprites.js
 * Sprite rendering and transformation for optics objects and their images.
 * Caches loaded p5.Image instances and applies optical transformations (scale, inversion, transparency).
 */

class SpriteManager {
  constructor() {
    this._cache = new Map();
    this._loading = new Set();
  }

  /**
   * Returns the loaded p5.Image if available, or initiates loading.
   */
  get(p, url) {
    if (!url) return null;
    if (this._cache.has(url)) return this._cache.get(url);

    if (!this._loading.has(url)) {
      this._loading.add(url);
      p.loadImage(
        url,
        img => {
          this._cache.set(url, img);
          this._loading.delete(url);
          p.redraw();
        },
        err => {
          console.warn('[OpticsSprites] Failed to load sprite:', url, err);
          this._loading.delete(url);
        }
      );
    }
    return null;
  }

  /**
   * Draws the object sprite at base (x, axisY) with specified height.
   */
  drawObject(p, img, x, axisY, height) {
    if (!img || img.width === 0) return false;
    const targetH = Math.abs(height);
    const aspect = img.width / img.height;
    const targetW = targetH * aspect;

    p.push();
    p.imageMode(p.CENTER);
    // Base is at axisY, tip is at axisY + height (height is negative for upright in screen coords)
    const centerY = axisY + height / 2;
    p.image(img, x, centerY, targetW, targetH);
    p.pop();
    return true;
  }

  /**
   * Draws the transformed image sprite at (x, axisY) based on magnification m and real/virtual nature.
   */
  drawImage(p, img, x, axisY, baseHeight, magnification, isReal) {
    if (!img || img.width === 0 || !isFinite(x) || !isFinite(magnification)) return false;

    const scale = Math.abs(magnification);
    const targetH = Math.abs(baseHeight) * scale;
    const aspect = img.width / img.height;
    const targetW = targetH * aspect;

    p.push();
    if (!isReal) {
      // Semi-transparent tint for virtual images
      p.tint(255, 175);
    }

    p.translate(x, axisY);
    // If magnification is negative (inverted image), flip Y axis
    if (magnification < 0) {
      p.scale(1, -1);
    }

    p.imageMode(p.CENTER);
    // Base is at 0 in translated space, height extends to -baseHeight/2 (upright relative to base)
    const localCenterY = -Math.abs(baseHeight) * scale / 2;
    p.image(img, 0, localCenterY, targetW, targetH);
    p.pop();
    return true;
  }
}

export const opticsSprites = new SpriteManager();
