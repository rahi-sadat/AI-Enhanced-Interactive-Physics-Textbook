/**
 * apps/web/src/components/InteractiveFigure.js
 * 
 * Reusable, book-agnostic interactive figure component.
 * Bridges any book page, exam question, AI tutor, or studio to the PhysicsRuntime.
 * Embeds transparent simulation overlays over textbook diagrams with sub-pixel alignment,
 * dynamic parameter sliders with evidentiary provenance badges, and live telemetry.
 */

import './interactiveFigure.css';
import { PhysicsRuntime } from '@engine/core/PhysicsRuntime.js';

export class InteractiveFigure {
  /**
   * @param {HTMLElement} hostElement - DOM element to mount the figure into
   * @param {object} [options={}]
   * @param {object|string} [options.scene] - Canonical PhysicsScene or URL
   * @param {Function} [options.onStateChange]
   * @param {Function} [options.onParameterChange]
   */
  constructor(hostElement, options = {}) {
    if (!hostElement) {
      throw new Error('[InteractiveFigure] Host DOM element is required.');
    }

    this.host = hostElement;
    this.options = options;
    this.runtime = new PhysicsRuntime();
    this.scene = null;
    this.currentDomain = 'mechanics';
    this.state = null;

    this.dom = {
      root: null,
      header: null,
      idChip: null,
      domainBadge: null,
      title: null,
      statusPill: null,
      stage: null,
      bgImage: null,
      overlay: null,
      sidebar: null,
      btnPlayPause: null,
      btnReset: null,
      paramsList: null,
      telemetryGrid: null,
      footer: null
    };

    this._resizeObserver = null;
    this._stateUnsub = null;
    this._sourceSize = { width: 800, height: 600 };

    this._renderScaffold();

    if (options.scene) {
      this.load(options.scene);
    }
  }

  _renderScaffold() {
    this.host.innerHTML = '';

    const root = document.createElement('div');
    root.className = 'interactive-figure-root';

    root.innerHTML = `
      <!-- Header -->
      <header class="if-header">
        <div class="if-header-left">
          <span class="if-id-chip" data-el="idChip">FIG-001</span>
          <span class="if-domain-badge mechanics" data-el="domainBadge">👣 Mechanics</span>
          <h3 class="if-title" data-el="title">Interactive Simulation</h3>
        </div>
        <div class="if-header-right">
          <span class="if-status-pill paused" data-el="statusPill">PAUSED</span>
        </div>
      </header>

      <!-- Body -->
      <div class="if-body">
        <!-- Stage Viewport -->
        <div class="if-stage-viewport" data-el="stage">
          <img class="if-background-img" data-el="bgImage" alt="Diagram reference" style="display:none;" />
          <div class="if-simulation-overlay" data-el="overlay"></div>
        </div>

        <!-- Sidebar -->
        <aside class="if-sidebar" data-el="sidebar">
          <!-- Controls -->
          <div class="if-control-bar">
            <button class="if-btn if-btn-primary" data-el="btnPlayPause">▶ Play</button>
            <button class="if-btn if-btn-secondary" data-el="btnReset">↺ Reset</button>
          </div>

          <!-- Dynamic Parameters with Provenance -->
          <div>
            <div class="if-section-title">Parameters &amp; Evidence</div>
            <div class="if-parameters-list" data-el="paramsList"></div>
          </div>

          <!-- Live Telemetry -->
          <div>
            <div class="if-section-title">Live Physics Telemetry</div>
            <div class="if-telemetry-panel">
              <div class="if-telemetry-grid" data-el="telemetryGrid">
                <div class="if-telemetry-metric">
                  <span class="if-metric-label">Status</span>
                  <span class="if-metric-value">Ready</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <!-- Footer -->
      <footer class="if-footer" data-el="footer">
        <span class="if-curriculum-tag" data-el="curriculumTag">Platform Content Spine v1</span>
        <span class="if-engine-tag" data-el="engineTag">Coordinate-Aligned Runtime</span>
      </footer>
    `;

    this.host.appendChild(root);
    this.dom.root = root;

    // Cache elements
    this.dom.idChip = root.querySelector('[data-el="idChip"]');
    this.dom.domainBadge = root.querySelector('[data-el="domainBadge"]');
    this.dom.title = root.querySelector('[data-el="title"]');
    this.dom.statusPill = root.querySelector('[data-el="statusPill"]');
    this.dom.stage = root.querySelector('[data-el="stage"]');
    this.dom.bgImage = root.querySelector('[data-el="bgImage"]');
    this.dom.overlay = root.querySelector('[data-el="overlay"]');
    this.dom.sidebar = root.querySelector('[data-el="sidebar"]');
    this.dom.btnPlayPause = root.querySelector('[data-el="btnPlayPause"]');
    this.dom.btnReset = root.querySelector('[data-el="btnReset"]');
    this.dom.paramsList = root.querySelector('[data-el="paramsList"]');
    this.dom.telemetryGrid = root.querySelector('[data-el="telemetryGrid"]');
    this.dom.curriculumTag = root.querySelector('[data-el="curriculumTag"]');
    this.dom.engineTag = root.querySelector('[data-el="engineTag"]');

    // Bind playback controls
    this.dom.btnPlayPause.addEventListener('click', () => {
      const isRunning = Boolean(this.state?.running);
      if (isRunning) {
        this.pause();
      } else {
        this.play();
      }
    });

    this.dom.btnReset.addEventListener('click', () => {
      this.reset();
    });

    // Handle responsive resizing
    this._resizeObserver = new ResizeObserver(() => {
      this._syncOverlayBox();
      this.runtime.resize(this.dom.overlay.clientWidth, this.dom.overlay.clientHeight);
    });
    this._resizeObserver.observe(this.dom.stage);
  }

  /**
   * Loads a simulation scene into this InteractiveFigure.
   * @param {object|string} sceneOrUrl - Scene JSON object or URL string
   */
  async load(sceneOrUrl) {
    let scene = sceneOrUrl;
    if (typeof sceneOrUrl === 'string') {
      const res = await fetch(sceneOrUrl);
      if (!res.ok) {
        throw new Error(`[InteractiveFigure] Failed to fetch scene from ${sceneOrUrl}`);
      }
      scene = await res.json();
    }

    this.scene = scene;
    const domain = scene.domain || scene.simulation?.domain || (scene.simulation_type === 'kinematics' ? 'mechanics' : scene.simulation_type || 'mechanics');
    this.currentDomain = domain;

    // 1. Update Header metadata
    this.dom.idChip.textContent = scene.id || 'FIG-001';
    this.dom.title.textContent = scene.title || `${domain.toUpperCase()} Figure`;

    this.dom.domainBadge.className = `if-domain-badge ${domain}`;
    if (domain === 'mechanics') {
      this.dom.domainBadge.innerHTML = '👣 Mechanics';
    } else if (domain === 'optics') {
      this.dom.domainBadge.innerHTML = '🔍 Optics';
    } else if (domain === 'circuits') {
      this.dom.domainBadge.innerHTML = '⚡ Circuits';
    }

    // 2. Set Background Image (if defined in scene source or visual)
    const bgUrl = scene.source?.image || scene.visual?.background_url;
    this._sourceSize = this._getSceneSourceSize(scene);
    if (bgUrl) {
      this.dom.bgImage.src = bgUrl;
      this.dom.bgImage.style.display = 'block';
      await this._waitForBackgroundImage();
    } else {
      this.dom.bgImage.style.display = 'none';
    }
    this._syncOverlayBox();

    // 3. Update Curriculum / Educational Footer
    if (scene.metadata?.chapter || scene.metadata?.topic) {
      this.dom.curriculumTag.textContent = `${scene.metadata.chapter || ''} • ${scene.metadata.topic || ''}`;
    } else {
      this.dom.curriculumTag.textContent = `Canonical Scene v1 (${domain})`;
    }

    // 4. Render Dynamic Parameters with Provenance Badges
    this._renderParameters(scene.parameters || {});

    // 5. Clear previous overlay and initialize PhysicsRuntime
    this.dom.overlay.innerHTML = '';
    await this.runtime.load(scene, this.dom.overlay);

    // 6. Subscribe to real-time telemetry updates
    this._stateUnsub?.();
    this._stateUnsub = this.runtime.onStateChange((state) => {
      this.state = state;
      this._updateTelemetry(state);
      this._updateStatusPill(state);
      this.options.onStateChange?.(state);
    });

    const initial = this.runtime.getState();
    this.state = initial;
    this._updateTelemetry(initial);
    this._updateStatusPill(initial);
  }

  _getSceneSourceSize(scene) {
    const source = scene.source || {};
    const coordinateSystem = scene.coordinateSystem || {};
    return {
      width: Number(coordinateSystem.width || source.width || source.image_width_px || scene.geometry?.source_width || 800),
      height: Number(coordinateSystem.height || source.height || source.image_height_px || scene.geometry?.source_height || 600)
    };
  }

  async _waitForBackgroundImage() {
    const img = this.dom.bgImage;
    if (!img || img.complete) return;

    if (typeof img.decode === 'function') {
      try {
        await img.decode();
        return;
      } catch (_) {
        // Fall through to load/error listeners; decode can reject for SVGs in some browsers.
      }
    }

    await new Promise((resolve) => {
      img.addEventListener('load', resolve, { once: true });
      img.addEventListener('error', resolve, { once: true });
    });
  }

  _syncOverlayBox() {
    const stage = this.dom.stage;
    const overlay = this.dom.overlay;
    if (!stage || !overlay) return;

    const stageW = stage.clientWidth || 0;
    const stageH = stage.clientHeight || 0;
    const hasBackground = this.dom.bgImage?.style.display !== 'none';
    const sourceW = this.dom.bgImage?.naturalWidth || this._sourceSize.width || 800;
    const sourceH = this.dom.bgImage?.naturalHeight || this._sourceSize.height || 600;

    if (!hasBackground || stageW <= 0 || stageH <= 0 || sourceW <= 0 || sourceH <= 0) {
      overlay.style.inset = '0';
      overlay.style.left = '';
      overlay.style.top = '';
      overlay.style.width = '100%';
      overlay.style.height = '100%';
      return;
    }

    const scale = Math.min(stageW / sourceW, stageH / sourceH);
    const renderedW = sourceW * scale;
    const renderedH = sourceH * scale;

    overlay.style.inset = 'auto';
    overlay.style.left = `${(stageW - renderedW) / 2}px`;
    overlay.style.top = `${(stageH - renderedH) / 2}px`;
    overlay.style.width = `${renderedW}px`;
    overlay.style.height = `${renderedH}px`;
  }

  _renderParameters(parameters) {
    this.dom.paramsList.innerHTML = '';

    const paramEntries = Object.entries(parameters);
    if (paramEntries.length === 0) {
      this.dom.paramsList.innerHTML = '<div style="font-size:0.8rem;color:#64748b;">No adjustable parameters.</div>';
      return;
    }

    for (const [key, param] of paramEntries) {
      const item = document.createElement('div');
      item.className = 'if-param-item';

      const labelText = param.label || key;
      const unitText = param.unit ? ` ${param.unit}` : '';
      const provenance = param.provenance || 'observed';
      const sourceDesc = param.source || 'textbook';
      const confPercent = param.confidence != null ? `${Math.round(param.confidence * 100)}%` : '100%';
      const minVal = param.min ?? 0;
      const maxVal = param.max ?? (Number(param.value) * 2 || 100);
      const stepVal = param.step ?? 1;

      item.innerHTML = `
        <div class="if-param-header">
          <span class="if-param-label">${labelText}</span>
          <span class="if-param-provenance ${provenance}" title="Evidence: ${provenance} • Source: ${sourceDesc} • Confidence: ${confPercent}">
            ${this._provenanceIcon(provenance)} ${provenance}
          </span>
        </div>
        <div class="if-param-controls">
          <input type="range" class="if-slider" 
                 min="${minVal}" max="${maxVal}" step="${stepVal}" value="${param.value}" />
          <input type="number" class="if-val-input" 
                 min="${minVal}" max="${maxVal}" step="${stepVal}" value="${param.value}" />
          <span class="if-unit-badge">${unitText}</span>
        </div>
      `;

      const slider = item.querySelector('.if-slider');
      const numInput = item.querySelector('.if-val-input');
      const provBadge = item.querySelector('.if-param-provenance');

      const onValChange = (newVal) => {
        const val = Number(newVal);
        slider.value = val;
        numInput.value = val;
        this.runtime.setParameter(key, val);

        // Update badge to 'student' modified state
        provBadge.className = 'if-param-provenance student';
        provBadge.innerHTML = '✏️ student';
        provBadge.title = `Evidence: student • Source: runtime_interaction • Confidence: 100%`;

        this.options.onParameterChange?.(key, val);
      };

      slider.addEventListener('input', (e) => onValChange(e.target.value));
      numInput.addEventListener('change', (e) => onValChange(e.target.value));

      this.dom.paramsList.appendChild(item);
    }
  }

  _provenanceIcon(prov) {
    switch (prov) {
      case 'observed': return '👁';
      case 'assumed': return '⚙';
      case 'inferred': return '🧠';
      case 'student': return '✏️';
      case 'author_override': return '📝';
      default: return '•';
    }
  }

  _updateStatusPill(state) {
    const isRunning = Boolean(state?.running);
    this.dom.statusPill.className = `if-status-pill ${isRunning ? 'running' : 'paused'}`;
    this.dom.statusPill.textContent = isRunning ? 'RUNNING' : 'PAUSED';

    this.dom.btnPlayPause.innerHTML = isRunning ? '⏸ Pause' : '▶ Play';
  }

  _updateTelemetry(state) {
    if (!state) return;

    this.dom.telemetryGrid.innerHTML = '';

    const addMetric = (label, val, highlight = false) => {
      const el = document.createElement('div');
      el.className = 'if-telemetry-metric';
      el.innerHTML = `
        <span class="if-metric-label">${label}</span>
        <span class="if-metric-value ${highlight ? 'highlight' : ''}">${val}</span>
      `;
      this.dom.telemetryGrid.appendChild(el);
    };

    if (state.domain === 'mechanics') {
      addMetric('Angle θ', `${state.thetaDeg ?? 0}°`, true);
      addMetric('Speed v', `${state.speed ?? 0} m/s`);
      addMetric('Length L', `${state.length ?? 1} m`);
      addMetric('Total Energy', `${state.totalEnergy ?? 0} J`);
    } else if (state.domain === 'optics') {
      addMetric('Object dist (u)', `${state.u ?? 0} px`);
      addMetric('Image dist (v)', `${state.v ?? 0} px`, true);
      addMetric('Focal length (f)', `${state.focalLength ?? 0} px`);
      addMetric('Magnification', `${state.magnification ?? 0}×`);
      addMetric('Image Type', state.imageType || 'real');
      addMetric('Real / Inverted', `${state.isReal ? 'Real' : 'Virtual'} • ${state.isInverted ? 'Inverted' : 'Upright'}`);
    } else if (state.domain === 'circuits') {
      addMetric('Total Power', `${state.totalPower ?? 0} W`, true);
      if (state.nodeVoltages) {
        for (const [node, v] of Object.entries(state.nodeVoltages)) {
          addMetric(`Voltage ${node}`, `${v} V`);
        }
      }
      if (state.branchCurrents) {
        for (const [branch, i] of Object.entries(state.branchCurrents)) {
          if (!branch.endsWith('.branch')) {
            addMetric(`Current ${branch}`, `${i} mA`);
          }
        }
      }
    } else {
      for (const [k, v] of Object.entries(state)) {
        if (typeof v === 'number' || typeof v === 'string') {
          addMetric(k, String(v));
        }
      }
    }
  }

  play() {
    this.runtime.play();
  }

  pause() {
    this.runtime.pause();
  }

  reset() {
    this.runtime.reset();
  }

  setParameter(name, value) {
    this.runtime.setParameter(name, value);
  }

  getState() {
    return this.runtime.getState();
  }

  destroy() {
    this._resizeObserver?.disconnect();
    this._stateUnsub?.();
    this.runtime.destroy();
    this.host.innerHTML = '';
  }
}

// Register as Web Component for direct declarative embedding:
// <interactive-figure src="/scenes/canonical/pendulum_figure.json"></interactive-figure>
if (typeof customElements !== 'undefined' && !customElements.get('interactive-figure')) {
  customElements.define('interactive-figure', class extends HTMLElement {
    async connectedCallback() {
      const src = this.getAttribute('src');
      this.figure = new InteractiveFigure(this);
      if (src) {
        await this.figure.load(src);
      }
    }

    disconnectedCallback() {
      this.figure?.destroy();
    }
  });
}
