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
import { FigureViewport } from './FigureViewport.js';

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
    this.viewport = null;

    this.dom = {
      root: null,
      header: null,
      idChip: null,
      domainBadge: null,
      title: null,
      statusPill: null,
      body: null,
      viewportHost: null,
      sidebar: null,
      btnPlayPause: null,
      btnReset: null,
      btnToggleSidebar: null,
      btnToggleAnchors: null,
      paramsList: null,
      telemetryGrid: null,
      footer: null
    };

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
          <button class="if-btn if-btn-secondary" data-el="btnToggleAnchors" title="Toggle sub-pixel alignment reticles" style="padding:4px 10px; font-size:0.76rem;">
            🎯 Anchors (0px)
          </button>
          <button class="if-btn if-btn-secondary" data-el="btnToggleSidebar" title="Simulate drawer/sidebar width changes" style="padding:4px 10px; font-size:0.76rem;">
            ⇄ Sidebar
          </button>
          <span class="if-status-pill paused" data-el="statusPill">PAUSED</span>
        </div>
      </header>

      <!-- Body -->
      <div class="if-body" data-el="body">
        <!-- Layout-Invariant Figure Viewport Host -->
        <div class="if-viewport-host" data-el="viewportHost"></div>

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
        <span class="if-engine-tag" data-el="engineTag">Layout-Invariant FigureViewport</span>
      </footer>
    `;

    this.host.appendChild(root);
    this.dom.root = root;

    // Cache elements
    this.dom.idChip = root.querySelector('[data-el="idChip"]');
    this.dom.domainBadge = root.querySelector('[data-el="domainBadge"]');
    this.dom.title = root.querySelector('[data-el="title"]');
    this.dom.statusPill = root.querySelector('[data-el="statusPill"]');
    this.dom.body = root.querySelector('[data-el="body"]');
    this.dom.viewportHost = root.querySelector('[data-el="viewportHost"]');
    this.dom.sidebar = root.querySelector('[data-el="sidebar"]');
    this.dom.btnPlayPause = root.querySelector('[data-el="btnPlayPause"]');
    this.dom.btnReset = root.querySelector('[data-el="btnReset"]');
    this.dom.btnToggleSidebar = root.querySelector('[data-el="btnToggleSidebar"]');
    this.dom.btnToggleAnchors = root.querySelector('[data-el="btnToggleAnchors"]');
    this.dom.paramsList = root.querySelector('[data-el="paramsList"]');
    this.dom.telemetryGrid = root.querySelector('[data-el="telemetryGrid"]');
    this.dom.curriculumTag = root.querySelector('[data-el="curriculumTag"]');
    this.dom.engineTag = root.querySelector('[data-el="engineTag"]');

    // Instantiate authoritative FigureViewport
    this.viewport = new FigureViewport(this.dom.viewportHost, {
      onLayoutChange: (context) => {
        this.runtime.resize(context.displayWidth, context.displayHeight, context);
      }
    });

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

    // Bind sidebar collapse toggle for live responsiveness testing
    this.dom.btnToggleSidebar?.addEventListener('click', () => {
      this.toggleSidebar();
    });

    // Bind calibration anchor inspector
    this.dom.btnToggleAnchors?.addEventListener('click', () => {
      const active = !this.viewport.showInspectAnchors;
      this.viewport.setInspectAnchors(active);
      this.dom.btnToggleAnchors.classList.toggle('if-btn-primary', active);
      this.dom.btnToggleAnchors.classList.toggle('if-btn-secondary', !active);
    });
  }

  toggleSidebar() {
    this.dom.body.classList.toggle('sidebar-collapsed');
    // FigureViewport's ResizeObserver detects container width change instantly
  }

  /**
   * Loads a simulation scene into this InteractiveFigure.
   * @param {object|string} sceneOrUrl - Scene JSON object or URL string
   */
  async load(sceneOrUrl) {
    let scene = sceneOrUrl;
    if (typeof sceneOrUrl === 'string') {
      const cacheBustUrl = sceneOrUrl.includes('?') ? `${sceneOrUrl}&t=${Date.now()}` : `${sceneOrUrl}?t=${Date.now()}`;
      const res = await fetch(cacheBustUrl);
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

    // 2. Set Background Image and Dimensions via FigureViewport
    const bgUrl = scene.source?.image || scene.visual?.background_url;
    this._sourceSize = this._getSceneSourceSize(scene);
    await this.viewport.setBackground(bgUrl, this._sourceSize.width, this._sourceSize.height);

    // 3. Configure calibration alignment anchors for inspection
    this._setupSceneCalibrationAnchors(scene);

    // 4. Update Curriculum / Educational Footer
    if (scene.metadata?.chapter || scene.metadata?.topic) {
      this.dom.curriculumTag.textContent = `${scene.metadata.chapter || ''} • ${scene.metadata.topic || ''}`;
    } else {
      this.dom.curriculumTag.textContent = `Canonical Scene v1 (${domain})`;
    }

    // 5. Render Dynamic Parameters with Provenance Badges
    this._renderParameters(scene.parameters || {});

    // 6. Clear previous overlay canvas and mount into FigureViewport overlay container
    const overlayContainer = this.viewport.getOverlayContainer();
    overlayContainer.innerHTML = '';
    await this.runtime.load(scene, overlayContainer, {
      viewport: this.viewport,
      renderContext: this.viewport.getRenderContext()
    });

    // 7. Subscribe to real-time telemetry updates
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

  _setupSceneCalibrationAnchors(scene) {
    const domain = this.currentDomain;
    const anchors = [];

    if (domain === 'mechanics') {
      const pObj = scene.objects?.find(o => o.type === 'pendulum') || scene;
      const pivot = pObj.geometry?.pivot || scene.geometry?.pivot || { x: 468.0, y: 99.7 };
      const bob = scene.geometry?.bob_center || { x: 246.58, y: 527.56 };
      anchors.push({ id: 'pivot', label: 'Pivot', x: pivot.x, y: pivot.y, color: '#38bdf8' });
      anchors.push({ id: 'bob', label: 'Bob Initial', x: bob.x, y: bob.y, color: '#f59e0b' });
    } else if (domain === 'optics') {
      const lx = scene.geometry?.lensX || 400;
      const ay = scene.geometry?.axisY || 300;
      const f = Number(scene.parameters?.focalLength?.value ?? 130);
      anchors.push({ id: 'lens_center', label: 'Optical Center O', x: lx, y: ay, color: '#38bdf8' });
      anchors.push({ id: 'f1', label: 'F₁ Focus', x: lx - f, y: ay, color: '#34d399' });
      anchors.push({ id: 'f2', label: 'F₂ Focus', x: lx + f, y: ay, color: '#34d399' });
    } else if (domain === 'circuits') {
      anchors.push({ id: 'v1', label: 'Battery V₁', x: 140, y: 250, color: '#ef4444' });
      anchors.push({ id: 's1', label: 'Key S₁', x: 230, y: 120, color: '#f59e0b' });
      anchors.push({ id: 'r1', label: 'Resistor R₁', x: 400, y: 120, color: '#38bdf8' });
      anchors.push({ id: 'r2', label: 'Resistor R₂', x: 660, y: 250, color: '#38bdf8' });
    }

    this.viewport.setCalibrationAnchors(anchors);
  }

  _getSceneSourceSize(scene) {
    const source = scene.source || {};
    const coordinateSystem = scene.coordinateSystem || {};
    return {
      width: Number(coordinateSystem.width || source.width || source.image_width_px || scene.geometry?.source_width || 800),
      height: Number(coordinateSystem.height || source.height || source.image_height_px || scene.geometry?.source_height || 600)
    };
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
    this._stateUnsub?.();
    this.viewport?.destroy();
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
