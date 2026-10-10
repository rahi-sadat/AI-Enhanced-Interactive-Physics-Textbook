/**
 * apps/web/src/components/PhysicsReviewModal.js
 *
 * Student-Facing Interactive Review & Evidence Resolution Dialog.
 *
 * UX Principles:
 *   1. What did the system detect? (Candidates with confidence badges)
 *   2. What is uncertain or missing? (Blockers from PR-07 ReviewState)
 *   3. What can I confirm or correct? (Confirm, Correct, Manual Entry, Policy Assumptions)
 *   4. When can I start the simulation? (Clear "Start Simulation" when READY_TO_SIMULATE)
 *
 * Strictly adheres to backend authority:
 *   - Renders issues and policies declared by backend ReviewState.
 *   - Never fabricates defaults or bypasses ResolutionEngine.
 *   - Disables actions while mutations are in flight (double-submission prevention).
 */

import { OrchestratorState } from '../features/simulations/core/SimulationOrchestrator.js';

export const PARAMETER_LABELS = {
  length: 'String Length',
  gravity: 'Gravitational Acceleration (g)',
  mass: 'Bob Mass (m)',
  damping: 'Air Resistance / Damping (b)',
  initial_angle_deg: 'Initial Release Angle (θ₀)',
  launch_speed: 'Launch Speed (v₀)',
  launch_angle_deg: 'Launch Angle (θ₀)',
  pixels_per_meter: 'Diagram Spatial Scale',
  focal_length_px: 'Focal Length (f)',
  focal_length: 'Focal Length (f)',
  object_distance_px: 'Object Distance (u)',
  object_distance: 'Object Distance (u)',
  n1: 'Refractive Index — Medium 1 (n₁)',
  n2: 'Refractive Index — Medium 2 (n₂)',
  refractive_index: 'Refractive Index (n)',
  apex_angle_deg: 'Prism Apex Angle (A)',
  incident_angle_deg: 'Incident Angle (θ₁)',
  curvature_radius_px: 'Radius of Curvature (R)',
  source_voltage: 'Source Voltage (V)',
  resistance: 'Resistance (R)',
  source_current: 'Source Current (I)',
  current: 'Current (I)',
};

export const DEFAULT_UNITS = {
  length: ['m', 'cm', 'mm'],
  gravity: ['m/s²'],
  mass: ['kg', 'g'],
  damping: ['1/s'],
  initial_angle_deg: ['deg', 'rad'],
  launch_speed: ['m/s', 'km/h'],
  launch_angle_deg: ['deg'],
  pixels_per_meter: ['px/m', 'px/cm'],
  focal_length_px: ['px'],
  focal_length: ['cm', 'm', 'mm'],
  object_distance: ['cm', 'm', 'px'],
  source_voltage: ['V', 'mV'],
  voltage: ['V', 'mV'],
  resistance: ['Ω', 'kΩ', 'ohm'],
  current: ['A', 'mA'],
};

export function getParameterUnits(paramName) {
  if (DEFAULT_UNITS[paramName]) return DEFAULT_UNITS[paramName];
  const p = (paramName || '').toLowerCase();
  if (p.includes('resistance') || p.includes('resistor')) return ['Ω', 'kΩ', 'ohm'];
  if (p.includes('voltage') || p.includes('emf') || p.startsWith('v')) return ['V', 'mV'];
  if (p.includes('current')) return ['A', 'mA'];
  if (p.includes('capacitance')) return ['μF', 'nF', 'pF', 'F'];
  if (p.includes('angle')) return ['deg', 'rad'];
  if (p.includes('speed') || p.includes('velocity')) return ['m/s', 'km/h'];
  if (p.includes('mass')) return ['kg', 'g'];
  if (p.includes('length') || p.includes('distance') || p.includes('height')) return ['m', 'cm', 'mm'];
  return ['m'];
}

export class PhysicsReviewModal {
  /**
   * @param {HTMLElement} hostElement
   * @param {import('../features/simulations/core/SimulationOrchestrator.js').SimulationOrchestrator} orchestrator
   * @param {object} [options={}]
   * @param {function(): void} [options.onStartSimulation]
   * @param {function(): void} [options.onClose]
   */
  constructor(hostElement, orchestrator, options = {}) {
    if (!hostElement) {
      throw new Error('[PhysicsReviewModal] Host element is required.');
    }
    this.host = hostElement;
    this.orchestrator = orchestrator;
    this.options = options;

    this.isOpen = false;
    this._correctionModes = new Set(); // Parameter names where student chose [Correct]
    this._manualValues = new Map(); // Temporary inputs

    this.dom = {
      backdrop: null,
      dialog: null,
      title: null,
      subtypeChip: null,
      subtitle: null,
      btnClose: null,
      body: null,
      footerStatus: null,
      btnStartSim: null,
      btnCancel: null,
    };

    this._renderScaffold();
    this._bindEvents();

    this._unsub = this.orchestrator.onStateChange((state, ctx) => {
      this._handleOrchestratorChange(state, ctx);
    });
  }

  _renderScaffold() {
    const backdrop = document.createElement('div');
    backdrop.className = 'prm-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.setAttribute('aria-labelledby', 'prm-dialog-title');

    backdrop.innerHTML = `
      <div class="prm-dialog" tabindex="-1">
        <!-- Header -->
        <header class="prm-header">
          <div class="prm-header-info">
            <div class="prm-title-row">
              <h2 id="prm-dialog-title" class="prm-title">
                <span>🔬</span> Textbook Evidence Review
              </h2>
              <span class="prm-subtype-chip" data-el="subtypeChip">Physics Diagram</span>
            </div>
            <p class="prm-subtitle" data-el="subtitle">
              Verify diagram measurements and modeling assumptions before simulation.
            </p>
          </div>
          <button class="prm-close-btn" data-el="btnClose" aria-label="Close review dialog">&times;</button>
        </header>

        <!-- Body -->
        <div class="prm-body" data-el="body">
          <!-- Dynamic cards injected here -->
        </div>

        <!-- Footer -->
        <footer class="prm-footer">
          <div class="prm-footer-status" data-el="footerStatus">
            <span>Ready for review</span>
          </div>
          <div style="display:flex; align-items:center; gap:10px;">
            <button class="prm-btn prm-btn-secondary" data-el="btnCancel">Dismiss</button>
            <button class="prm-btn prm-btn-success" data-el="btnStartSim" style="display:none;">
              ▶ Start Simulation
            </button>
          </div>
        </footer>
      </div>
    `;

    this.host.appendChild(backdrop);

    this.dom.backdrop = backdrop;
    this.dom.dialog = backdrop.querySelector('.prm-dialog');
    this.dom.subtypeChip = backdrop.querySelector('[data-el="subtypeChip"]');
    this.dom.subtitle = backdrop.querySelector('[data-el="subtitle"]');
    this.dom.btnClose = backdrop.querySelector('[data-el="btnClose"]');
    this.dom.body = backdrop.querySelector('[data-el="body"]');
    this.dom.footerStatus = backdrop.querySelector('[data-el="footerStatus"]');
    this.dom.btnStartSim = backdrop.querySelector('[data-el="btnStartSim"]');
    this.dom.btnCancel = backdrop.querySelector('[data-el="btnCancel"]');
  }

  _bindEvents() {
    this.dom.btnClose.addEventListener('click', () => this.close());
    this.dom.btnCancel.addEventListener('click', () => this.close());

    this.dom.btnStartSim.addEventListener('click', () => {
      try {
        const scene = this.orchestrator.startSimulation();
        this.close();
        this.options.onStartSimulation?.(scene);
      } catch (err) {
        console.error('[PhysicsReviewModal] Failed to start simulation:', err);
        if (this.dom.footerStatus) {
          this.dom.footerStatus.innerHTML = `<span style="color:#ef4444;">⚠️ ${this._escape(err.message)}</span>`;
        }
      }
    });

    // Close on backdrop click (outside dialog)
    this.dom.backdrop.addEventListener('click', (e) => {
      if (e.target === this.dom.backdrop) {
        this.close();
      }
    });

    // Keyboard support: Escape closes dialog
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  open() {
    this.isOpen = true;
    this.dom.backdrop.classList.add('open');
    this.dom.dialog.focus();
    this.render();
  }

  close() {
    this.isOpen = false;
    this.dom.backdrop.classList.remove('open');
    this.options.onClose?.();
  }

  _handleOrchestratorChange(state, ctx) {
    // Automatically open modal when review is required
    if (state === OrchestratorState.NEEDS_REVIEW && !this.isOpen) {
      this.open();
    }
    if (this.isOpen) {
      this.render();
    }
  }

  /**
   * Main render method. Translates backend ReviewState into student-facing cards.
   */
  render() {
    const ctx = this.orchestrator.getSessionContext();
    const state = ctx.state;
    const bookIR = ctx.bookIR;
    const reviewState = ctx.reviewState;
    const isBusy =
      state === OrchestratorState.APPLYING_RESOLUTION ||
      state === OrchestratorState.EVALUATING ||
      state === OrchestratorState.COMPILING;

    // 1. Update Subtype chip
    const subtype = bookIR?.subtype || 'Diagram';
    const domain = bookIR?.domain || 'Physics';
    this.dom.subtypeChip.textContent = `${subtype} (${domain})`;

    // 2. Clear Body
    this.dom.body.innerHTML = '';

    // 3. Error Banner if present
    if (ctx.currentError) {
      const errDiv = document.createElement('div');
      errDiv.className = 'prm-error-notice';
      errDiv.innerHTML = `<span>⚠️</span> <span>${this._escape(ctx.currentError)}</span>`;
      this.dom.body.appendChild(errDiv);
    }

    // 4. Ready Hero Banner if ready to simulate
    const isReady =
      state === OrchestratorState.READY_TO_SIMULATE ||
      state === OrchestratorState.READY_TO_COMPILE ||
      (ctx.compiledScene !== null && reviewState?.readyToCompile);

    if (isReady) {
      const readyBanner = document.createElement('div');
      readyBanner.className = 'prm-ready-banner';
      readyBanner.innerHTML = `
        <div class="prm-ready-info">
          <div class="prm-ready-title">
            <span>✓</span> Simulation Ready
          </div>
          <p class="prm-ready-desc">
            All physical measurements and modeling assumptions are complete.
          </p>
        </div>
        <button class="prm-btn prm-btn-success" data-action="start-sim-banner" ${isBusy ? 'disabled' : ''}>
          ▶ Start Simulation
        </button>
      `;
      readyBanner.querySelector('[data-action="start-sim-banner"]').addEventListener('click', () => {
        try {
          const scene = this.orchestrator.startSimulation();
          this.close();
          this.options.onStartSimulation?.(scene);
        } catch (err) {
          console.error('[PhysicsReviewModal] Start sim error:', err);
          if (this.dom.footerStatus) {
            this.dom.footerStatus.innerHTML = `<span style="color:#ef4444;">⚠️ ${this._escape(err.message)}</span>`;
          }
        }
      });
      this.dom.body.appendChild(readyBanner);
      this.dom.btnStartSim.style.display = 'inline-flex';
      this.dom.btnStartSim.disabled = isBusy;
    } else {
      this.dom.btnStartSim.style.display = 'none';
    }

    // 5. Unresolved Issues Section
    const issues = reviewState?.issues || [];
    const unresolvedIssues = issues.filter((iss) => {
      // If already resolved in BookIR parameters, skip from unresolved list
      const pName = iss.parameterName || iss.parameter_name;
      if (!pName) return true;
      const isResolved = bookIR?.parameters && bookIR.parameters[pName] !== undefined;
      return !isResolved;
    });

    if (unresolvedIssues.length > 0) {
      const sectionTitle = document.createElement('div');
      sectionTitle.className = 'prm-section-title';
      sectionTitle.innerHTML = `
        <span>Requires Your Confirmation (${unresolvedIssues.length})</span>
        <span style="font-size:0.7rem; color:#64748b;">Zero silent defaults</span>
      `;
      this.dom.body.appendChild(sectionTitle);

      for (const issue of unresolvedIssues) {
        const card = this._renderIssueCard(issue, isBusy, reviewState?.availablePolicies || []);
        this.dom.body.appendChild(card);
      }
    }

    // 6. Resolved Parameters Section (Auditable Provenance & Reversibility)
    const resolvedParams = Object.entries(bookIR?.parameters || {});
    if (resolvedParams.length > 0) {
      const resolvedSection = document.createElement('div');
      resolvedSection.style.marginTop = '10px';

      const resolvedTitle = document.createElement('div');
      resolvedTitle.className = 'prm-section-title';
      resolvedTitle.innerHTML = `
        <span>Resolved Evidence &amp; Assumptions (${resolvedParams.length})</span>
      `;
      resolvedSection.appendChild(resolvedTitle);

      const list = document.createElement('div');
      list.className = 'prm-resolved-list';

      for (const [paramKey, pVal] of resolvedParams) {
        const item = this._renderResolvedItem(paramKey, pVal, bookIR, isBusy);
        list.appendChild(item);
      }

      resolvedSection.appendChild(list);
      this.dom.body.appendChild(resolvedSection);
    }

    // 7. Update Footer Status
    if (isBusy) {
      this.dom.footerStatus.innerHTML = `
        <span class="prm-spinner"></span>
        <span>${this._formatBusyText(state)}</span>
      `;
    } else if (isReady) {
      this.dom.footerStatus.innerHTML = `
        <span style="color:#34d399;">✓ Ready to simulate</span>
      `;
    } else {
      this.dom.footerStatus.innerHTML = `
        <span>${unresolvedIssues.length} item(s) pending confirmation</span>
      `;
    }
  }

  /**
   * Renders a single review issue card.
   * @private
   */
  _renderIssueCard(issue, isBusy, availablePolicies) {
    const card = document.createElement('div');
    card.className = 'prm-issue-card';

    const paramName = issue.parameterName || issue.parameter_name || 'parameter';
    const friendlyLabel = PARAMETER_LABELS[paramName] || issue.title || paramName;
    const isCorrecting = this._correctionModes.has(paramName);

    // Header
    const header = document.createElement('div');
    header.className = 'prm-issue-header';
    header.innerHTML = `
      <div class="prm-param-name">
        <span>📍</span>
        <span>${this._escape(friendlyLabel)}</span>
      </div>
      <span class="prm-prov-tag detected">Uncertain</span>
    `;
    card.appendChild(header);

    // Question / Description
    if (issue.question || issue.description) {
      const q = document.createElement('p');
      q.className = 'prm-issue-question';
      q.textContent = issue.question || issue.description;
      card.appendChild(q);
    }

    // A. Evidence Candidate (e.g. from OCR)
    const candidate = issue.candidates && issue.candidates.length > 0 ? issue.candidates[0] : null;

    if (candidate && !isCorrecting) {
      const candBox = document.createElement('div');
      candBox.className = 'prm-candidate-box';

      const valStr = `${candidate.numericValue} ${candidate.rawUnit || ''}`.trim();
      const confStr = candidate.confidence ? `${Math.round(candidate.confidence * 100)}%` : '';

      candBox.innerHTML = `
        <div class="prm-candidate-details">
          <span class="prm-candidate-label">Detected from diagram:</span>
          <span class="prm-candidate-val">${this._escape(valStr)}</span>
          ${confStr ? `<span style="font-size:0.72rem; color:#64748b;">Confidence: ${confStr}</span>` : ''}
        </div>
        <div class="prm-candidate-actions">
          <button class="prm-btn prm-btn-secondary" data-action="correct" ${isBusy ? 'disabled' : ''}>
            ✏️ Correct
          </button>
          <button class="prm-btn prm-btn-primary" data-action="confirm" ${isBusy ? 'disabled' : ''}>
            ✓ Confirm
          </button>
        </div>
      `;

      candBox.querySelector('[data-action="confirm"]').addEventListener('click', async () => {
        try {
          await this.orchestrator.confirmCandidate(paramName, candidate);
        } catch (err) {
          console.error('[PhysicsReviewModal] Confirm error:', err);
        }
      });

      candBox.querySelector('[data-action="correct"]').addEventListener('click', () => {
        this._correctionModes.add(paramName);
        this.render();
      });

      card.appendChild(candBox);
    }

    // B. Manual Entry Form (if applicable)
    const isStructural = issue.issueType === 'ungrounded_geometry' ||
                         issue.issueType === 'ambiguous_geometry' ||
                         paramName === 'nodes' ||
                         paramName === 'components' ||
                         !paramName;

    if (!isStructural && (!candidate || isCorrecting)) {
      const form = this._renderManualForm(issue, paramName, isBusy);
      card.appendChild(form);
    } else if (isStructural && (!candidate || isCorrecting)) {
      const infoBox = document.createElement('div');
      infoBox.className = 'prm-info-box';
      infoBox.style.cssText = 'padding: 8px 12px; font-size: 0.85rem; color: #94a3b8; background: rgba(255,255,255,0.03); border-radius: 6px; border: 1px dashed rgba(255,255,255,0.1); margin-top: 8px;';
      infoBox.innerHTML = `<span>Schematic geometry requires visual grounding from diagram lines and symbols.</span>`;
      card.appendChild(infoBox);
    }

    // C. Explicit Policy Options (Modeling Assumptions)
    const matchingPolicies = this._findMatchingPolicies(issue, paramName, availablePolicies);
    for (const policy of matchingPolicies) {
      const polBox = this._renderPolicyBox(policy, paramName, isBusy);
      card.appendChild(polBox);
    }

    return card;
  }

  /**
   * Renders the manual value input form for a parameter.
   * @private
   */
  _renderManualForm(issue, paramName, isBusy) {
    const form = document.createElement('div');
    form.className = 'prm-manual-form';

    const allowedUnits = issue.allowedUnits?.length ? issue.allowedUnits : getParameterUnits(paramName);
    const currentVal = this._manualValues.get(paramName) || '';

    let unitOptionsHtml = '';
    for (const u of allowedUnits) {
      unitOptionsHtml += `<option value="${this._escape(u)}">${this._escape(u)}</option>`;
    }

    form.innerHTML = `
      <input type="number" step="any" class="prm-input" placeholder="Enter value" value="${this._escape(currentVal)}" data-el="numInput" ${isBusy ? 'disabled' : ''} />
      ${allowedUnits.length > 0 ? `<select class="prm-select" data-el="unitSelect" ${isBusy ? 'disabled' : ''}>${unitOptionsHtml}</select>` : ''}
      <button class="prm-btn prm-btn-primary" data-action="save-manual" ${isBusy ? 'disabled' : ''}>
        Save Value
      </button>
      ${this._correctionModes.has(paramName) ? `<button class="prm-btn prm-btn-secondary" data-action="cancel-correct" ${isBusy ? 'disabled' : ''}>Cancel</button>` : ''}
    `;

    const numInput = form.querySelector('[data-el="numInput"]');
    const unitSelect = form.querySelector('[data-el="unitSelect"]');

    numInput.addEventListener('input', (e) => {
      this._manualValues.set(paramName, e.target.value);
    });

    form.querySelector('[data-action="save-manual"]').addEventListener('click', async () => {
      const val = numInput.value.trim();
      const unit = unitSelect ? unitSelect.value : null;
      if (!val) {
        numInput.focus();
        return;
      }
      try {
        await this.orchestrator.submitManualValue(paramName, val, unit);
        this._correctionModes.delete(paramName);
      } catch (err) {
        console.error('[PhysicsReviewModal] Save manual error:', err);
      }
    });

    const cancelBtn = form.querySelector('[data-action="cancel-correct"]');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        this._correctionModes.delete(paramName);
        this.render();
      });
    }

    return form;
  }

  /**
   * Renders an explicit policy assumption card.
   * @private
   */
  _renderPolicyBox(policy, paramName, isBusy) {
    const box = document.createElement('div');
    box.className = 'prm-policy-box';

    const valStr = `${policy.value} ${policy.unit || ''}`.trim();
    const rationale = policy.educationalRationale || policy.description || 'Standard modeling assumption.';

    box.innerHTML = `
      <div class="prm-policy-header">
        <div>
          <span style="font-size:0.7rem; color:#f59e0b; text-transform:uppercase; font-weight:700;">Modeling Assumption</span>
          <div class="prm-policy-title">${this._escape(policy.name || policy.id)}</div>
        </div>
        <span class="prm-policy-val">${this._escape(valStr)}</span>
      </div>
      <p class="prm-policy-desc">${this._escape(rationale)}</p>
      <div style="display:flex; justify-content:flex-end;">
        <button class="prm-btn prm-btn-warning" data-action="apply-policy" ${isBusy ? 'disabled' : ''}>
          Use This Assumption
        </button>
      </div>
    `;

    box.querySelector('[data-action="apply-policy"]').addEventListener('click', async () => {
      try {
        await this.orchestrator.applyPolicy(policy.id || policy.policyId, paramName);
      } catch (err) {
        console.error('[PhysicsReviewModal] Apply policy error:', err);
      }
    });

    return box;
  }

  /**
   * Renders an already resolved item with provenance badge and reversibility action.
   * @private
   */
  _renderResolvedItem(paramKey, pVal, bookIR, isBusy) {
    const item = document.createElement('div');
    item.className = 'prm-resolved-item';

    const friendlyLabel = PARAMETER_LABELS[paramKey] || paramKey;
    let valStr = '';
    let unitStr = '';

    if (typeof pVal === 'object' && pVal !== null) {
      valStr = String(pVal.value !== undefined ? pVal.value : '');
      unitStr = pVal.unit || '';
    } else {
      valStr = String(pVal);
    }

    // Provenance identification
    const provRecord = bookIR?.parameter_provenance?.[paramKey] || pVal?.provenance;
    let badgeClass = 'confirmed';
    let badgeText = 'Confirmed';

    if (provRecord) {
      const src = (provRecord.source || '').toLowerCase();
      if (src.includes('policy')) {
        badgeClass = 'assumption';
        badgeText = 'Assumption';
      } else if (src.includes('correct')) {
        badgeClass = 'corrected';
        badgeText = 'Corrected';
      } else if (src.includes('derived')) {
        badgeClass = 'detected';
        badgeText = 'Derived';
      } else if (src.includes('user')) {
        badgeClass = 'confirmed';
        badgeText = 'Student Value';
      }
    }

    item.innerHTML = `
      <div class="prm-resolved-left">
        <span class="prm-prov-tag ${badgeClass}">${badgeText}</span>
        <span class="prm-resolved-name">${this._escape(friendlyLabel)}</span>
        <span class="prm-resolved-val">${this._escape(valStr)} ${this._escape(unitStr)}</span>
      </div>
      <button class="prm-btn-link" data-action="undo-resolution" ${isBusy ? 'disabled' : ''} title="Revert to change this value">
        Change / Undo
      </button>
    `;

    item.querySelector('[data-action="undo-resolution"]').addEventListener('click', async () => {
      try {
        await this.orchestrator.removeResolution(paramKey);
      } catch (err) {
        console.error('[PhysicsReviewModal] Undo resolution error:', err);
      }
    });

    return item;
  }

  /**
   * Finds backend policies that match an issue or parameter name.
   * @private
   */
  _findMatchingPolicies(issue, paramName, availablePolicies) {
    const list = [];
    if (!availablePolicies) return list;

    for (const pol of availablePolicies) {
      const pParam = pol.targetParameter || pol.parameterName || pol.target_parameter;
      const polId = pol.id || pol.policyId;
      if (issue.defaultPolicyId && polId === issue.defaultPolicyId) {
        list.push(pol);
      } else if (pParam && pParam === paramName) {
        list.push(pol);
      }
    }
    return list;
  }

  _formatBusyText(state) {
    switch (state) {
      case OrchestratorState.APPLYING_RESOLUTION:
        return 'Applying decision...';
      case OrchestratorState.EVALUATING:
        return 'Verifying simulation readiness...';
      case OrchestratorState.COMPILING:
        return 'Compiling canonical physics scene...';
      default:
        return 'Processing...';
    }
  }

  _escape(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  destroy() {
    this._unsub?.();
    this.dom.backdrop?.remove();
  }
}
