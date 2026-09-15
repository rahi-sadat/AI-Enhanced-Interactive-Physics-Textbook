/**
 * circuits/CircuitController.js
 * Master lifecycle coordinator for Domain 3 (Circuits).
 * Integrates:
 * - Scene loading & background registration on OverlayStage
 * - CircuitCompiler (topology & polyline precomputation)
 * - CircuitSolver (browser MNA on Float64Array)
 * - CircuitStore (multi-layer state manager)
 * - P5CircuitView (60 FPS transparent particle & halo overlay)
 * - ComponentEditor (anchored HTML parameter popover)
 * - ProbeManager (virtual instruments)
 * - CircuitTelemetry (bidirectional table & derivations)
 * - CircuitTutorBridge (grounded bilingual AI explanation drawer)
 */

import { CircuitCompiler } from './CircuitCompiler.js';
import { CircuitSolver } from './CircuitSolver.js';
import { CircuitStore } from './CircuitStore.js';
import { CircuitHitTest } from './CircuitHitTest.js';
import { P5CircuitView } from './view/P5CircuitView.js';
import { ComponentEditor } from './ComponentEditor.js';
import { ProbeManager } from './ProbeManager.js';
import { CircuitTelemetry } from './CircuitTelemetry.js';
import { CircuitTutorBridge } from './CircuitTutorBridge.js';

export class CircuitController {
  /**
   * @param {object} scene - Canonical CircuitScene v3 JSON
   * @param {object} overlayStage - OverlayStage instance
   */
  constructor(scene, overlayStage) {
    this.scene = scene;
    this.overlayStage = overlayStage;

    // 1. Compile topology and initial solve
    this.model = CircuitCompiler.compile(this.scene);
    this.solver = new CircuitSolver(this.model);
    this.electricalState = this.solver.solveDC();

    // 2. Initialize multi-layer store
    this.store = new CircuitStore(this.scene, this.model, this.electricalState);

    // 3. Register background diagram on stage
    this._applyBackground();

    // 4. Set up CoordinateMapper binding
    this.mapper = this.overlayStage.getMapper();
    this.container = this.overlayStage.getContainer();

    this.overlayStage.onMapperChanged((mapper) => {
      this.mapper = mapper;
      this.view?.resize();
      this.editor?.position(this.store.model.componentById.get(this.store.uiState.selectedComponentId));
    });

    this.overlayStage.clearOverlay();

    // 5. Initialize P5 Transparent View
    this.view = new P5CircuitView(this.container, this.store, this.mapper);

    // 6. Initialize Anchored HTML Component Editor
    this.editor = new ComponentEditor(this.container, this.store, this.mapper, {
      onParameterChange: (id, key, val) => this.setParameter(id, key, val),
      onRestore: (id) => this.restoreParameter(id),
      onToggleSwitch: (id) => this.toggleSwitch(id),
      onWhy: (id) => this.explainChange(id)
    });

    // 7. Initialize Probe Manager
    this.probeManager = new ProbeManager(this.store);

    // 8. Initialize AI Tutor Bridge
    this.tutor = new CircuitTutorBridge(this.container, this.store);

    // 9. Initialize Side Panel Telemetry & Controls
    this._bindDOMControls();
    this._showPanel();

    // 10. Bind Pointer Events on Container
    this._bindPointerEvents();

    console.log('[CircuitController] Augmented Circuit Laboratory initialized.');
  }

  _applyBackground() {
    const bgUrl = this.scene.visual?.background_url ||
                  this.scene.source?.image ||
                  '/scenes/circuits/textbook_circuit_diagram.svg';
    const sw = this.scene.source?.image_width_px || 800;
    const sh = this.scene.source?.image_height_px || 500;
    this.overlayStage.setBackground(bgUrl, sw, sh);
  }

  solve() {
    this.electricalState = this.solver.solveDC();
    this.store.electricalState = this.electricalState;
    this.store.notify('SOLVE_COMPLETED', { state: this.electricalState });
    this.editor?.render();
  }

  setParameter(componentId, paramKey, value) {
    this.store.setParameter(componentId, paramKey, value);
    this.solve();
  }

  restoreParameter(componentId) {
    this.store.restoreTextbookValue(componentId);
    this.solve();
  }

  toggleSwitch(switchId) {
    this.store.model.toggleSwitch(switchId);
    // Recompile topology because switch state altered the matrix structure
    this.store.model = CircuitCompiler.compile(this.store.scene);
    this.solver.load(this.store.model);
    this.solve();
    this.store.notify('SWITCH_TOGGLED', { switchId });
  }

  explainChange(componentId) {
    this.tutor.explainChange(componentId);
  }

  // ---------------------------------------------------------------------------
  // Pointer Events & Hit Detection
  // ---------------------------------------------------------------------------

  _bindPointerEvents() {
    this._onPointerDown = (e) => {
      // Ignore clicks originating from inside HTML popovers or tutor drawer
      if (e.target?.closest?.('.circuit-component-popover') || e.target?.closest?.('.circuit-tutor-drawer')) {
        return;
      }

      const rect = this.container.getBoundingClientRect();
      const cssX = e.clientX - rect.left;
      const cssY = e.clientY - rect.top;

      const hit = CircuitHitTest.hitTest(cssX, cssY, this.mapper, this.store.model);
      const mode = this.store.uiState.mode;

      if (!hit) {
        if (mode === 'inspect' || mode === 'edit') {
          this.store.setSelectedComponent(null);
          this.editor.close();
        }
        return;
      }

      // Handle Switch Toggle on direct click
      if (hit.type === 'switch') {
        this.toggleSwitch(hit.id);
        return;
      }

      // Handle Virtual Instruments
      if (mode === 'voltage-probe') {
        this.probeManager.handleVoltageProbeClick(hit);
        return;
      } else if (mode === 'current-probe') {
        this.probeManager.handleCurrentProbeClick(hit);
        return;
      } else if (mode === 'kcl') {
        this.probeManager.handleKCLClick(hit);
        return;
      }

      // Inspect / Edit Mode
      if (hit.type === 'component') {
        this.store.setSelectedComponent(hit.id);
        this.editor.open(hit.id);
      }
    };

    this._onPointerMove = (e) => {
      const rect = this.container.getBoundingClientRect();
      const cssX = e.clientX - rect.left;
      const cssY = e.clientY - rect.top;

      const hit = CircuitHitTest.hitTest(cssX, cssY, this.mapper, this.store.model);

      if (hit?.type === 'component') {
        this.store.setHoveredComponent(hit.id);
        this.container.style.cursor = 'pointer';
      } else if (hit?.type === 'switch') {
        this.store.setHoveredComponent(hit.id);
        this.container.style.cursor = 'pointer';
      } else {
        this.store.setHoveredComponent(null);
        this.container.style.cursor = 'default';
      }
    };

    this.container.addEventListener('pointerdown', this._onPointerDown);
    this.container.addEventListener('pointermove', this._onPointerMove);
  }

  // ---------------------------------------------------------------------------
  // DOM Controls & Side Panel
  // ---------------------------------------------------------------------------

  _showPanel() {
    ['mechanics-controls', 'optics-controls'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });

    const circuitSection = document.getElementById('circuit-controls');
    if (circuitSection) {
      circuitSection.style.display = 'block';
    }
  }

  _bindDOMControls() {
    const circuitSection = document.getElementById('circuit-controls');
    if (!circuitSection) return;

    // Populate Side Panel HTML
    circuitSection.innerHTML = `
      <h2 class="section-title">⚡ Circuit Controls</h2>

      <!-- Scenario Selector -->
      <div class="control" style="margin-bottom: 8px;">
        <label for="circuit-scene-select">NCTB Diagram Scenario</label>
        <select id="circuit-scene-select" class="select" style="font-weight: 600; padding: 7px 10px; background: rgba(14,165,233,0.15); border-color: rgba(56,189,248,0.4); color: #38bdf8;">
          <option value="series_parallel">⚡ অনুক্রমিক বর্তনী (Series Circuit: 12V, 10Ω, 20Ω)</option>
          <option value="bridge">⚖️ হুইটস্টোন ব্রিজ (Wheatstone Bridge Network)</option>
        </select>
      </div>

      <!-- Mode Toolbar -->
      <div class="circuit-toolbar" role="toolbar" aria-label="Circuit tools">
        <button class="circuit-tool-btn active" data-mode="inspect" title="Inspect elements">↖ Inspect</button>
        <button class="circuit-tool-btn" data-mode="voltage-probe" title="Voltage probe (click 2 nodes)">⚡ V-Probe</button>
        <button class="circuit-tool-btn" data-mode="current-probe" title="Current probe (click branch)">🔌 I-Probe</button>
        <button class="circuit-tool-btn" data-mode="kcl" title="Kirchhoff's Current Law (click any node)">Σ KCL</button>
        <button class="circuit-tool-btn" data-mode="kvl" title="Kirchhoff's Voltage Law (trace loop)">⟳ KVL</button>
        <button class="circuit-tool-btn" id="btn-circuit-reset" title="Restore original textbook values">⟲ Restore</button>
      </div>

      <!-- Display Toggles -->
      <div class="circuit-toggles">
        <label class="toggle-label">
          <input type="checkbox" id="toggle-circuit-anim" checked /> Live Current Particles
        </label>
        <label class="toggle-label">
          <input type="checkbox" id="toggle-circuit-debug" /> Sub-Pixel Debug Overlay
        </label>
      </div>

      <!-- Telemetry Panel Container -->
      <div id="circuit-telemetry-container"></div>
    `;

    // Instantiate Telemetry Component inside container
    const telemetryContainer = document.getElementById('circuit-telemetry-container');
    this.telemetry = new CircuitTelemetry(telemetryContainer, this.store, {
      onSelectComponent: (cId) => {
        this.store.setSelectedComponent(cId);
        this.editor.open(cId);
      }
    });

    // Tool buttons
    const toolBtns = circuitSection.querySelectorAll('.circuit-tool-btn[data-mode]');
    toolBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        toolBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.getAttribute('data-mode');
        this.store.setMode(mode);
        if (mode === 'inspect') {
          this.probeManager.clearProbes();
        } else if (mode === 'kvl') {
          this.probeManager.handleKVLTrace();
        }
      });
    });

    // Scenario switch
    const sceneSelect = document.getElementById('circuit-scene-select');
    sceneSelect?.addEventListener('change', async (e) => {
      const scenario = e.target.value;
      const path = scenario === 'bridge'
        ? '/scenes/circuits/bridge_scene.json'
        : '/scenes/circuits/series_parallel_scene.json';

      const res = await fetch(path);
      const newScene = await res.json();
      this.loadNewScene(newScene);
    });

    // Reset button
    const btnReset = document.getElementById('btn-circuit-reset');
    btnReset?.addEventListener('click', () => {
      this.store.resetToTextbook();
      this.solve();
    });

    // Toggle animation
    const toggleAnim = document.getElementById('toggle-circuit-anim');
    toggleAnim?.addEventListener('change', (e) => {
      this.store.uiState.animationEnabled = e.target.checked;
    });

    // Toggle debug
    const toggleDebug = document.getElementById('toggle-circuit-debug');
    toggleDebug?.addEventListener('change', (e) => {
      this.store.uiState.debugOverlay = e.target.checked;
    });
  }

  loadNewScene(newScene) {
    this.scene = newScene;
    this.model = CircuitCompiler.compile(this.scene);
    this.solver = new CircuitSolver(this.model);
    this.electricalState = this.solver.solveDC();

    this.store.scene = this.scene;
    this.store.model = this.model;
    this.store.electricalState = this.electricalState;
    this.store.overrides.clear();

    this._applyBackground();
    this.editor.close();
    this.probeManager.clearProbes();
    this.store.notify('RESET_ALL', {});
  }

  destroy() {
    this.container.removeEventListener('pointerdown', this._onPointerDown);
    this.container.removeEventListener('pointermove', this._onPointerMove);
    this.view?.destroy();
    this.editor?.destroy();
    this.tutor?.destroy();
    this.overlayStage.clearOverlay();
  }
}
