/**
 * circuits/ComponentEditor.js
 * Anchored HTML parameter control popover positioned in view coordinates
 * directly beside the selected textbook component.
 * Features logarithmic resistance scaling, live V/I/P readouts, OCR provenance,
 * and the contextual [Why?] tutor explanation button.
 */

export class ComponentEditor {
  /**
   * @param {HTMLElement} hostContainer
   * @param {object} store - CircuitStore instance
   * @param {object} mapper - CoordinateMapper instance
   * @param {object} callbacks - { onParameterChange, onRestore, onWhy }
   */
  constructor(hostContainer, store, mapper, callbacks = {}) {
    this.host = hostContainer;
    this.store = store;
    this.mapper = mapper;
    this.callbacks = callbacks;

    this.element = null;
    this._createDOM();
  }

  _createDOM() {
    this.element = document.createElement('div');
    this.element.className = 'circuit-component-popover';
    this.element.style.display = 'none';
    this.element.addEventListener('pointerdown', (e) => e.stopPropagation());
    this.element.addEventListener('click', (e) => e.stopPropagation());
    this.host.appendChild(this.element);
  }

  /**
   * Show editor for a specific component.
   */
  open(componentId) {
    const comp = this.store.model.componentById.get(componentId);
    if (!comp) return;

    this.currentComponentId = componentId;
    this.render();
    this.position(comp);
    this.element.style.display = 'block';
  }

  close() {
    this.currentComponentId = null;
    if (this.element) {
      this.element.style.display = 'none';
    }
  }

  position(comp) {
    if (!comp || !this.element || !this.mapper) return;

    const centerSrc = comp.geometry?.center_source_px || [400, 250];
    const viewPt = this.mapper.sourceToView(centerSrc[0], centerSrc[1]);

    // Offset slightly so it floats cleanly beside the textbook drawing
    const left = Math.max(10, Math.min(viewPt.x + 25, this.host.clientWidth - 260));
    const top = Math.max(10, Math.min(viewPt.y - 60, this.host.clientHeight - 220));

    this.element.style.left = `${left}px`;
    this.element.style.top = `${top}px`;
  }

  render() {
    if (!this.currentComponentId || !this.element) return;
    const comp = this.store.model.componentById.get(this.currentComponentId);
    if (!comp) return;

    const state = this.store.electricalState;
    const vDrop = state?.componentVoltages?.[comp.id] ?? 0.0;
    const current = state?.componentCurrents?.[comp.id] ?? 0.0;
    const power = state?.componentPower?.[comp.id] ?? 0.0;

    const override = this.store.overrides.get(comp.id);
    const isModified = Boolean(override);
    const isResistor = comp.type === 'resistor' || comp.type === 'bulb';
    const isBattery = comp.type === 'voltage_source' || comp.type === 'battery';
    const isSwitch = comp.type === 'switch';

    const currentValue = Number(comp.value ?? (isBattery ? 12.0 : 10.0));

    let controlHtml = '';

    if (isResistor) {
      // Logarithmic slider: 10^0 (1Ω) to 10^5 (100kΩ)
      const logVal = Math.log10(Math.max(1, currentValue));
      controlHtml = `
        <div class="popover-slider-row">
          <label class="popover-label">Resistance: <strong>${currentValue.toFixed(1)} Ω</strong></label>
          <input type="range" class="popover-slider" id="popover-slider-r"
                 min="0" max="5" step="0.05" value="${logVal.toFixed(2)}" />
          <div class="slider-ticks">
            <span>1 Ω</span>
            <span>10 Ω</span>
            <span>100 Ω</span>
            <span>1 kΩ</span>
            <span>10 kΩ</span>
          </div>
        </div>
      `;
    } else if (isBattery) {
      // Linear slider: 0V to 24V
      controlHtml = `
        <div class="popover-slider-row">
          <label class="popover-label">Voltage: <strong>${currentValue.toFixed(1)} V</strong></label>
          <input type="range" class="popover-slider" id="popover-slider-v"
                 min="0" max="24" step="0.5" value="${currentValue}" />
          <div class="slider-ticks">
            <span>0 V</span>
            <span>6 V</span>
            <span>12 V</span>
            <span>18 V</span>
            <span>24 V</span>
          </div>
        </div>
      `;
    } else if (isSwitch) {
      controlHtml = `
        <div class="popover-switch-row">
          <span class="switch-status-label">State: <strong>${comp.state.toUpperCase()}</strong></span>
          <button id="popover-btn-toggle-switch" class="btn btn-primary btn-sm">
            ${comp.state === 'open' ? '🔌 Close Switch' : '⚡ Open Switch'}
          </button>
        </div>
      `;
    }

    this.element.innerHTML = `
      <div class="popover-header">
        <span class="popover-title">${comp.label || comp.id}</span>
        <button class="popover-close-btn" id="popover-close-btn">&times;</button>
      </div>

      <div class="popover-body">
        ${controlHtml}

        <div class="popover-readouts">
          <div class="readout-item">
            <span class="readout-label">Voltage Drop</span>
            <span class="readout-val">${vDrop.toFixed(2)} V</span>
          </div>
          <div class="readout-item">
            <span class="readout-label">Current</span>
            <span class="readout-val">${(Math.abs(current) * 1000).toFixed(1)} mA</span>
          </div>
          <div class="readout-item">
            <span class="readout-label">Power</span>
            <span class="readout-val">${power.toFixed(2)} W</span>
          </div>
        </div>

        <div class="popover-provenance">
          <span class="prov-icon">📖</span>
          <span class="prov-text">
            Textbook: ${override?.originalValue ?? comp.provenance?.value ?? currentValue} ${comp.unit || 'Ω'}
            ${isModified ? '<span class="prov-tag">(Student modified)</span>' : ''}
          </span>
        </div>

        <div class="popover-actions">
          ${isModified ? '<button id="popover-btn-restore" class="btn btn-secondary btn-xs">Restore Textbook</button>' : ''}
          <button id="popover-btn-why" class="btn btn-accent btn-xs">🤔 Why did values change?</button>
        </div>
      </div>
    `;

    // Bind slider events
    const sliderR = this.element.querySelector('#popover-slider-r');
    if (sliderR) {
      sliderR.addEventListener('input', (e) => {
        const val = Math.pow(10, parseFloat(e.target.value));
        const rounded = val < 10 ? Math.round(val * 10) / 10 : Math.round(val);
        this.callbacks.onParameterChange?.(comp.id, 'value', rounded);
      });
    }

    const sliderV = this.element.querySelector('#popover-slider-v');
    if (sliderV) {
      sliderV.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        this.callbacks.onParameterChange?.(comp.id, 'value', val);
      });
    }

    const btnToggle = this.element.querySelector('#popover-btn-toggle-switch');
    if (btnToggle) {
      btnToggle.addEventListener('click', () => {
        this.callbacks.onToggleSwitch?.(comp.id);
      });
    }

    const btnRestore = this.element.querySelector('#popover-btn-restore');
    if (btnRestore) {
      btnRestore.addEventListener('click', () => {
        this.callbacks.onRestore?.(comp.id);
      });
    }

    const btnWhy = this.element.querySelector('#popover-btn-why');
    if (btnWhy) {
      btnWhy.addEventListener('click', () => {
        this.callbacks.onWhy?.(comp.id);
      });
    }

    const btnClose = this.element.querySelector('#popover-close-btn');
    if (btnClose) {
      btnClose.addEventListener('click', () => this.close());
    }
  }

  destroy() {
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
    this.element = null;
  }
}
