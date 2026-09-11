/** optics/opticsController.js — Central coordinator for the optics domain.
 * Connects adapters -> engines (ThinLens, Prism, Mirror) -> p5View -> HUD.
 */
import { adaptOpticsScene } from './opticsSceneAdapter.js';
import { solveThinLens } from './engines/thinLensEngine.js';
import { solvePrismRefraction } from './engines/prismEngine.js';
import { solveMirror } from './engines/mirrorEngine.js';
import { traceInterfaceRefraction } from './engines/snellInterfaceEngine.js';
import { P5OpticsView } from './view/p5OpticsView.js';
import { OpticsHUD } from './view/opticsHUD.js';

export class OpticsController {
  constructor(scene, overlayStage) {
    this.overlayStage = overlayStage;
    this.scene = scene;
    this._useCandleSprite = false;
    this.currentConcept = 'thin_lens';

    this.model = adaptOpticsScene(scene);
    this._applyBackground();

    this.overlayStage.clearOverlay();

    this.view = new P5OpticsView(overlayStage.getContainer(), {
      onDragLens: (x, h) => this.moveObject(x, h),
      onDragMirror: (x, h) => this.moveObject(x, h),
      onDragPrism: (x, y) => this.movePrismSource(x, y),
      onDragInterface: (x, y) => this.moveInterfaceSource(x, y),
    });

    this.hud = new OpticsHUD('optics-hud');

    this._bindControls();
    this._showPanel();
    this._update();
  }

  moveObject(newX, newHeight = null) {
    if (!this.model.object) return;
    this.model.object.x = newX;
    if (newHeight != null) this.model.object.height = newHeight;
    this._update();
  }

  movePrismSource(newX, newY) {
    if (!this.model.lightSource) return;
    this.model.lightSource.x = newX;
    this.model.lightSource.y = newY;
    this._update();
  }

  moveInterfaceSource(newX, newY) {
    if (!this.model.lightSource) return;
    this.model.lightSource.x = newX;
    this.model.lightSource.y = newY;
    this._update();
  }

  setFocalLength(f) {
    if (this.model.subtype === 'mirror') {
      this.model.mirror.focalLength = f;
    } else if (this.model.lens) {
      this.model.lens.focalLength = f;
    }
    this._update();
  }

  setPrismRefractiveIndex(n) {
    if (this.model.prism) {
      this.model.prism.refractiveIndex = n;
      this._update();
    }
  }

  setMirrorType(type) {
    if (this.model.mirror) {
      this.model.mirror.model = type;
      const f = Math.abs(this.model.mirror.focalLength || 130);
      const mx = this.model.mirror.x;
      if (type === 'convex') {
        this.model.focalPoints = [
          { label: 'P', x: mx },
          { label: 'F', x: mx + f },
          { label: 'C', x: mx + 2 * f }
        ];
      } else if (type === 'concave') {
        this.model.focalPoints = [
          { label: 'C', x: mx - 2 * f },
          { label: 'F', x: mx - f },
          { label: 'P', x: mx }
        ];
      } else { // plane
        this.model.focalPoints = [
          { label: 'P', x: mx }
        ];
      }
      this._syncControlsUI();
      this._update();
    }
  }

  setDebug(enable) {
    this.view?.setDebug(enable);
  }

  toggleSprite(enable) {
    this._useCandleSprite = enable;
    if (this.model.object) {
      this.model.object.spriteUrl = enable ? '/scenes/optics/sprites/candle.png' : null;
      this._update();
    }
  }

  async loadConcept(concept) {
    this.currentConcept = concept;
    const conceptUrls = {
      thin_lens: '/scenes/optics/thin_lens_scene.json',
      concave_lens: '/scenes/optics/concave_lens_scene.json',
      prism: '/scenes/optics/prism_scene.json',
      glass_slab: '/scenes/optics/glass_slab_scene.json',
      tir_prism: '/scenes/optics/tir_prism_scene.json',
      interface_refraction: '/scenes/optics/interface_refraction_scene.json',
      mirror: '/scenes/optics/mirror_scene.json',
    };

    const url = conceptUrls[concept] || conceptUrls.thin_lens;
    try {
      const res = await fetch(url + '?t=' + Date.now());
      const sceneData = await res.json();
      this.scene = sceneData;
      this.model = adaptOpticsScene(sceneData);
      if (this._useCandleSprite && this.model.object) {
        this.model.object.spriteUrl = '/scenes/optics/sprites/candle.png';
      }
      this._applyBackground();
      this._syncControlsUI();
      this._update();
    } catch (err) {
      console.error('[OpticsController] Failed to load concept:', concept, err);
    }
  }

  destroy() {
    this.view?.destroy();
  }

  _applyBackground() {
    const bgUrl = this.scene?.visual?.background_url ?? this.scene?.source?.image ?? null;
    this.overlayStage.setBackground(bgUrl);
  }

  _update() {
    const sub = this.model.subtype || 'thin_lens';

    if (sub === 'prism') {
      const { prism, lightSource } = this.model;
      const rayDir = {
        x: lightSource.targetX - lightSource.x,
        y: lightSource.targetY - lightSource.y,
      };
      const result = solvePrismRefraction({
        prismVertices: prism.vertices,
        refractiveIndex: prism.refractiveIndex,
        rayOrigin: { x: lightSource.x, y: lightSource.y },
        rayDirection: rayDir,
      });
      this.view.render(this.model, result);
      this.hud.update('prism', result, prism.refractiveIndex);
      return;
    }

    if (sub === 'mirror') {
      const { mirror, object, axisY } = this.model;
      const result = solveMirror({
        mirrorType: mirror.model,
        mirrorX: mirror.x,
        axisY,
        objectX: object.x,
        objectHeight: object.height,
        focalLength: mirror.focalLength,
      });
      this.view.render(this.model, result);
      this.hud.update('mirror', result, mirror.focalLength, this.model.pixelPerCm);
      return;
    }

    if (sub === 'interface_refraction') {
      const { boundary, normal, medium1, medium2, lightSource, pointOfIncidence } = this.model;
      const result = traceInterfaceRefraction({
        boundaryY: boundary?.y ?? 300,
        normalX: normal?.x ?? 400,
        n1: medium1?.n ?? 1.0,
        n2: medium2?.n ?? 1.5,
        source: { x: lightSource.x, y: lightSource.y },
        targetPoint: pointOfIncidence ? { x: pointOfIncidence.x, y: pointOfIncidence.y } : { x: normal?.x ?? 400, y: boundary?.y ?? 300 }
      });
      this.view.render(this.model, result);
      this.hud.update('interface_refraction', result);
      return;
    }

    // Default: Thin Lens
    const { lens, object, axisY } = this.model;
    const result = solveThinLens({
      lensX: lens.x,
      axisY,
      objectX: object.x,
      objectHeight: object.height,
      focalLength: lens.focalLength,
    });
    this.view.render(this.model, result);
    this.hud.update('thin_lens', result, lens.focalLength, this.model.pixelPerCm);
  }

  _bindControls() {
    // Focal length slider
    const sl = document.getElementById('focal-length-slider');
    const lb = document.getElementById('focal-length-value');
    if (sl) {
      sl.addEventListener('input', () => {
        const val = Number(sl.value);
        if (lb) lb.textContent = Math.round(val) + ' px';
        this.setFocalLength(val);
      });
    }

    // Prism refractive index slider
    const nSlider = document.getElementById('prism-n-slider');
    const nVal = document.getElementById('prism-n-value');
    if (nSlider) {
      nSlider.addEventListener('input', () => {
        const val = parseFloat(nSlider.value);
        if (nVal) nVal.textContent = val.toFixed(2);
        this.setPrismRefractiveIndex(val);
      });
    }

    // Mirror type dropdown
    const mirrorSel = document.getElementById('mirror-type-select');
    if (mirrorSel) {
      mirrorSel.addEventListener('change', (e) => {
        this.setMirrorType(e.target.value);
      });
    }

    // Optics debug toggle
    const debugToggle = document.getElementById('toggle-optics-debug');
    if (debugToggle) {
      debugToggle.addEventListener('change', (e) => {
        this.setDebug(e.target.checked);
      });
    }

    // Concept switcher tabs
    ['optics-tab-lens', 'optics-tab-prism', 'optics-tab-mirror'].forEach(tabId => {
      const tab = document.getElementById(tabId);
      if (tab) {
        tab.addEventListener('click', () => {
          const concept = tab.getAttribute('data-concept');
          this.loadConcept(concept);
        });
      }
    });

    // Diagram scenario dropdown
    const sceneSelect = document.getElementById('optics-scene-select');
    if (sceneSelect) {
      sceneSelect.addEventListener('change', e => {
        this.loadConcept(e.target.value);
      });
    }

    // Sprite toggle
    const spriteToggle = document.getElementById('toggle-candle-sprite');
    if (spriteToggle) {
      spriteToggle.addEventListener('change', e => {
        this.toggleSprite(e.target.checked);
      });
    }

    this._syncControlsUI();
  }

  _syncControlsUI() {
    const sub = this.model.subtype || 'thin_lens';
    const focalGroup = document.getElementById('focal-slider-group');
    const prismNGroup = document.getElementById('prism-n-slider-group');
    const mirrorGroup = document.getElementById('mirror-type-group');
    const prismHint = document.getElementById('prism-hint');
    const lensHint = document.getElementById('lens-hint');
    const mirrorHint = document.getElementById('mirror-hint');
    const spriteGroup = document.getElementById('sprite-toggle-group');

    const isPlaneMirror = sub === 'mirror' && this.model.mirror?.model === 'plane';
    if (focalGroup) focalGroup.style.display = (sub === 'thin_lens' || (sub === 'mirror' && !isPlaneMirror)) ? 'flex' : 'none';
    if (prismNGroup) prismNGroup.style.display = sub === 'prism' ? 'flex' : 'none';
    if (mirrorGroup) mirrorGroup.style.display = sub === 'mirror' ? 'flex' : 'none';
    if (prismHint) prismHint.style.display = sub === 'prism' ? 'block' : 'none';
    if (lensHint) lensHint.style.display = sub === 'thin_lens' ? 'block' : 'none';
    if (mirrorHint) mirrorHint.style.display = sub === 'mirror' ? 'block' : 'none';
    if (spriteGroup) spriteGroup.style.display = (sub === 'prism' || sub === 'interface_refraction') ? 'none' : 'flex';
    const sceneSelect = document.getElementById('optics-scene-select');
    if (sceneSelect && this.currentConcept) {
      sceneSelect.value = this.currentConcept;
    }

    document.querySelectorAll('.optics-subtab').forEach(tab => {
      const concept = tab.getAttribute('data-concept');
      const isLens = concept === 'thin_lens' && (this.currentConcept === 'thin_lens' || this.currentConcept === 'concave_lens');
      const isPrism = concept === 'prism' && (this.currentConcept === 'prism' || this.currentConcept === 'glass_slab' || this.currentConcept === 'tir_prism');
      const isMirror = concept === 'mirror' && this.currentConcept === 'mirror';
      tab.classList.toggle('active', isLens || isPrism || isMirror);
    });

    if (sub === 'thin_lens' && this.model.lens) {
      const sl = document.getElementById('focal-length-slider');
      const lb = document.getElementById('focal-length-value');
      if (sl) sl.value = this.model.lens.focalLength;
      if (lb) lb.textContent = Math.round(this.model.lens.focalLength) + ' px';
    } else if (sub === 'prism' && this.model.prism) {
      const nSl = document.getElementById('prism-n-slider');
      const nLb = document.getElementById('prism-n-value');
      if (nSl) nSl.value = this.model.prism.refractiveIndex;
      if (nLb) nLb.textContent = Number(this.model.prism.refractiveIndex).toFixed(2);
    } else if (sub === 'mirror' && this.model.mirror) {
      const sl = document.getElementById('focal-length-slider');
      const lb = document.getElementById('focal-length-value');
      if (sl) sl.value = Math.abs(this.model.mirror.focalLength);
      if (lb) lb.textContent = Math.round(Math.abs(this.model.mirror.focalLength)) + ' px';

      const mirrorSel = document.getElementById('mirror-type-select');
      if (mirrorSel) mirrorSel.value = this.model.mirror.model || 'concave';
    }
  }

  _showPanel() {
    const mc = document.getElementById('mechanics-controls');
    const oc = document.getElementById('optics-controls');
    if (mc) mc.style.display = 'none';
    if (oc) oc.style.display = 'flex';
  }
}
