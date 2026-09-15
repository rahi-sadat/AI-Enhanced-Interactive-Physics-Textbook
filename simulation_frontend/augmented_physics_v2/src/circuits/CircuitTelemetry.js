/**
 * circuits/CircuitTelemetry.js
 * Side panel telemetry view with bidirectional highlighting and equation derivations.
 * Synchronizes hover and selection seamlessly between the textbook diagram and the data table.
 */

import { EquationGenerator } from './EquationGenerator.js';

export class CircuitTelemetry {
  /**
   * @param {HTMLElement} containerElement
   * @param {object} store - CircuitStore instance
   * @param {object} callbacks - { onSelectComponent, onToggleSwitch }
   */
  constructor(containerElement, store, callbacks = {}) {
    this.container = containerElement;
    this.store = store;
    this.callbacks = callbacks;

    this.store.subscribe((type, payload) => {
      if (['PARAMETER_CHANGED', 'SELECTION_CHANGED', 'HOVER_CHANGED', 'RESET_ALL', 'PROBE_UPDATED'].includes(type)) {
        this.render();
      }
    });

    this.render();
  }

  render() {
    if (!this.container) return;
    const model = this.store.model;
    const state = this.store.electricalState;
    const ui = this.store.uiState;

    if (!model || !state) {
      this.container.innerHTML = '<div class="telemetry-empty">No active circuit loaded.</div>';
      return;
    }

    const current = state.primaryCurrent || 0.0;
    const req = state.equivalentResistance || 0.0;
    const pTot = state.totalPower || 0.0;
    const vs = model.voltageSources?.[0];
    const sourceV = vs ? Number(vs.value ?? 12.0) : 12.0;

    // Component rows
    let rowsHtml = '';
    for (const [cId, comp] of model.componentById.entries()) {
      const v = state.componentVoltages?.[cId] ?? 0.0;
      const i = state.componentCurrents?.[cId] ?? 0.0;
      const p = state.componentPower?.[cId] ?? 0.0;
      const isSelected = ui.selectedComponentId === cId;
      const isHovered = ui.hoveredComponentId === cId;

      const rowClass = `telemetry-row ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`;

      let valStr = '';
      if (comp.type === 'voltage_source' || comp.type === 'battery') valStr = `${comp.value} V`;
      else if (comp.type === 'resistor') valStr = `${comp.value} Ω`;
      else if (comp.type === 'switch') valStr = comp.state.toUpperCase();
      else valStr = `${comp.value ?? '-'}`;

      rowsHtml += `
        <tr class="${rowClass}" data-component-id="${cId}">
          <td class="td-name"><strong>${comp.label || cId}</strong></td>
          <td class="td-val">${valStr}</td>
          <td class="td-v">${Math.abs(v).toFixed(2)} V</td>
          <td class="td-i">${(Math.abs(i) * 1000).toFixed(1)} mA</td>
          <td class="td-p">${p.toFixed(2)} W</td>
        </tr>
      `;
    }

    // Step-by-step equations
    const derivations = EquationGenerator.generateDerivations(model, state);
    let equationsHtml = '';
    for (const step of derivations.steps) {
      equationsHtml += `
        <div class="derivation-step">
          <div class="step-title">${step.title}</div>
          <div class="step-formula">${step.formula}</div>
          <div class="step-subst">${step.substitution}</div>
          <div class="step-result"><strong>${step.result}</strong></div>
          <div class="step-exp">${step.explanation}</div>
        </div>
      `;
    }

    this.container.innerHTML = `
      <div class="circuit-telemetry-panel">
        <!-- Summary Cards -->
        <div class="telemetry-summary-cards">
          <div class="summary-card">
            <span class="card-label">মূল প্রবাহ (Total I)</span>
            <span class="card-val">${(current * 1000).toFixed(1)} mA</span>
            <span class="card-sub">${current.toFixed(3)} A</span>
          </div>
          <div class="summary-card">
            <span class="card-label">সমতুল্য রোধ (R_eq)</span>
            <span class="card-val">${isFinite(req) ? req.toFixed(1) + ' Ω' : '∞ (Open)'}</span>
            <span class="card-sub">${sourceV.toFixed(1)} V Source</span>
          </div>
          <div class="summary-card">
            <span class="card-label">মোট ক্ষমতা (Total P)</span>
            <span class="card-val">${pTot.toFixed(2)} W</span>
            <span class="card-sub">P = V × I</span>
          </div>
        </div>

        <!-- Telemetry Table -->
        <div class="telemetry-table-container">
          <table class="telemetry-table">
            <thead>
              <tr>
                <th>Element</th>
                <th>Value</th>
                <th>Drop (V)</th>
                <th>Current (I)</th>
                <th>Power (P)</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
        </div>

        <!-- Step-by-Step Physics Equations -->
        <div class="equations-container">
          <div class="equations-header">
            <span class="eq-icon">📐</span>
            <span class="eq-title">হিসাব ও বিশ্লেষণ (Step-by-Step Derivation)</span>
          </div>
          <div class="equations-body">
            ${equationsHtml}
          </div>
        </div>
      </div>
    `;

    // Bind row interaction for bidirectional highlighting
    const rows = this.container.querySelectorAll('.telemetry-row');
    rows.forEach(row => {
      const cId = row.getAttribute('data-component-id');
      row.addEventListener('mouseenter', () => {
        this.store.setHoveredComponent(cId);
      });
      row.addEventListener('mouseleave', () => {
        this.store.setHoveredComponent(null);
      });
      row.addEventListener('click', () => {
        this.callbacks.onSelectComponent?.(cId);
      });
    });
  }
}
