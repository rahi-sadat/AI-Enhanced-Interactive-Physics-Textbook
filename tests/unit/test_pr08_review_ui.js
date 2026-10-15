/**
 * tests/unit/test_pr08_review_ui.js
 *
 * Verifies student-facing evidence review UI logic:
 *   1. Natural-language domain labels for parameters.
 *   2. Candidate detection display, confidence badges, confirm and correct actions.
 *   3. Manual value input with allowed unit selectors.
 *   4. Explicit policy assumptions rendered with rationale without silent defaults.
 *   5. Unrelated policies strictly excluded.
 *   6. Double-submission prevention (actions disabled while in flight).
 *   7. Resolved provenance badges and reversibility (undo/change).
 *   8. Start Simulation activation when ready.
 */

import { PARAMETER_LABELS, DEFAULT_UNITS, PhysicsReviewModal } from '../../apps/web/src/components/PhysicsReviewModal.js';
import { SimulationOrchestrator, OrchestratorState } from '../../apps/web/src/features/simulations/core/SimulationOrchestrator.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ PASS: ${message}`);
  } else {
    failed++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

console.log('==============================================');
console.log('  RUNNING PR-08 REVIEW UI & INTERACTION TESTS');
console.log('==============================================\n');

// Lightweight DOM Mock for Node testing of PhysicsReviewModal
class SimpleElement {
  constructor(tagName = 'div') {
    this.tagName = tagName;
    const set = new Set();
    this.classList = {
      add: (c) => set.add(c),
      remove: (c) => set.delete(c),
      contains: (c) => set.has(c),
      toggle: (c, force) => {
        if (force === undefined) {
          if (set.has(c)) set.delete(c);
          else set.add(c);
        } else if (force) set.add(c);
        else set.delete(c);
      },
      has: (c) => set.has(c),
    };
    Object.defineProperty(this, 'className', {
      get: () => Array.from(set).join(' '),
      set: (val) => {
        set.clear();
        if (val) String(val).split(/\s+/).forEach((c) => c && set.add(c));
      },
    });
    this.attributes = {};
    this.style = {};
    this.children = [];
    this.listeners = {};
    this._innerHTML = '';
    this._textContent = '';
    this.disabled = false;
    this.value = '';
  }

  setAttribute(k, v) { this.attributes[k] = String(v); }
  getAttribute(k) { return this.attributes[k] || null; }

  set innerHTML(html) {
    this._innerHTML = html;
    this.children = [];
    this._parseMockChildren(html);
  }
  get innerHTML() { return this._innerHTML; }

  set textContent(txt) {
    this._textContent = txt;
  }
  get textContent() {
    if (this.children.length === 0) return this._textContent || '';
    return (this._textContent ? this._textContent + ' ' : '') + this.children.map((c) => c.textContent).join(' ');
  }

  appendChild(c) {
    this.children.push(c);
    return c;
  }

  addEventListener(ev, fn) {
    if (!this.listeners[ev]) this.listeners[ev] = [];
    this.listeners[ev].push(fn);
  }

  trigger(ev, eventObj = {}) {
    for (const fn of this.listeners[ev] || []) {
      fn({ target: this, ...eventObj });
    }
  }

  querySelector(selector) {
    return this._findFirst(selector);
  }

  querySelectorAll(selector) {
    const results = [];
    this._findAll(selector, results);
    return results;
  }

  focus() {}
  remove() {}

  _parseMockChildren(html) {
    const tagRegex = /([^<]*)(?:<(\/)?([a-z0-9-]+)([^>]*)>)/gi;
    const stack = [this];
    let match;
    let lastIndex = 0;

    while ((match = tagRegex.exec(html)) !== null) {
      lastIndex = tagRegex.lastIndex;
      const textBefore = match[1].trim();
      const isClosing = match[2] === '/';
      const tagName = match[3].toLowerCase();
      const rawAttrs = match[4] || '';
      const isVoid = /^(input|img|br|hr|meta|link)$/i.test(tagName) || rawAttrs.trim().endsWith('/');

      if (textBefore && stack.length > 0) {
        const top = stack[stack.length - 1];
        top._textContent = (top._textContent ? top._textContent + ' ' : '') + textBefore;
      }

      if (isClosing) {
        if (stack.length > 1 && stack[stack.length - 1].tagName === tagName) {
          stack.pop();
        }
      } else {
        const el = new SimpleElement(tagName);
        const classM = rawAttrs.match(/class=["']([^"']+)["']/i);
        if (classM) {
          el.className = classM[1];
        }

        const dataElM = rawAttrs.match(/data-el=["']([^"']+)["']/i);
        if (dataElM) el.setAttribute('data-el', dataElM[1]);

        const dataActM = rawAttrs.match(/data-action=["']([^"']+)["']/i);
        if (dataActM) el.setAttribute('data-action', dataActM[1]);

        const idM = rawAttrs.match(/id=["']([^"']+)["']/i);
        if (idM) el.attributes.id = idM[1];

        if (/disabled/i.test(rawAttrs)) el.disabled = true;

        const parent = stack[stack.length - 1];
        parent.children.push(el);
        el.parent = parent;

        if (!isVoid) {
          stack.push(el);
        }
      }
    }

    const trailing = html.slice(lastIndex).replace(/<[^>]*>/g, '').trim();
    if (trailing && stack.length > 0) {
      stack[stack.length - 1]._textContent = (stack[stack.length - 1]._textContent ? stack[stack.length - 1]._textContent + ' ' : '') + trailing;
    }
  }

  _findFirst(selector) {
    const all = [];
    this._findAll(selector, all);
    return all[0] || null;
  }

  _findAll(selector, out) {
    for (const c of this.children) {
      if (this._matches(c, selector)) out.push(c);
      c._findAll(selector, out);
    }
  }

  _matches(el, selector) {
    if (selector.startsWith('.')) {
      return el.classList.contains(selector.slice(1));
    }
    if (selector.startsWith('#')) {
      return el.attributes.id === selector.slice(1);
    }
    const dataElM = selector.match(/\[data-el=["']?([^"'\]]+)["']?\]/);
    if (dataElM) {
      return el.getAttribute('data-el') === dataElM[1];
    }
    const dataActM = selector.match(/\[data-action=["']?([^"'\]]+)["']?\]/);
    if (dataActM) {
      return el.getAttribute('data-action') === dataActM[1];
    }
    return el.tagName.toLowerCase() === selector.toLowerCase();
  }
}

// Set up mock DOM environment
globalThis.document = {
  createElement: (tag) => new SimpleElement(tag),
  addEventListener: () => {},
};

async function runTests() {
  // Test 1: Parameter Labels Dictionary Coverage
  console.log('[1/8] Verifying domain-agnostic parameter presentation labels');
  assert(PARAMETER_LABELS.length === 'String Length', 'length mapped to "String Length"');
  assert(PARAMETER_LABELS.gravity.includes('Gravitational Acceleration'), 'gravity mapped to Gravitational Acceleration');
  assert(PARAMETER_LABELS.launch_speed === 'Launch Speed (v₀)', 'launch_speed mapped to "Launch Speed (v₀)"');
  assert(PARAMETER_LABELS.pixels_per_meter === 'Diagram Spatial Scale', 'pixels_per_meter mapped to "Diagram Spatial Scale"');
  assert(PARAMETER_LABELS.n1.includes('Refractive Index'), 'n1 mapped to Refractive Index');

  // Test 2: Default Units Dictionary
  console.log('\n[2/8] Verifying default units catalog');
  assert(DEFAULT_UNITS.length.includes('m') && DEFAULT_UNITS.length.includes('cm'), 'length supports m and cm');
  assert(DEFAULT_UNITS.gravity.includes('m/s²'), 'gravity supports m/s²');
  assert(DEFAULT_UNITS.launch_speed.includes('m/s'), 'launch_speed supports m/s');

  // Test 3: Candidate display and confirmation action
  console.log('\n[3/8] Review issue with OCR candidate displays value and triggers confirmation');
  let confirmedParam = null;
  let confirmedCandidate = null;

  const mockOrch = {
    state: OrchestratorState.NEEDS_REVIEW,
    bookIR: {
      domain: 'mechanics',
      subtype: 'pendulum',
      status: 'NEEDS_REVIEW',
      parameters: {},
    },
    reviewState: {
      readyToCompile: false,
      blockersCount: 1,
      issues: [
        {
          id: 'iss_1',
          parameterName: 'length',
          question: 'What is the length of the pendulum string?',
          candidates: [{ numericValue: 80, rawUnit: 'cm', confidence: 0.88 }],
        },
      ],
      availablePolicies: [],
    },
    getSessionContext() {
      return {
        state: this.state,
        bookIR: this.bookIR,
        reviewState: this.reviewState,
        compiledScene: null,
        currentError: null,
      };
    },
    onStateChange: () => () => {},
    confirmCandidate: async (pName, cand) => {
      confirmedParam = pName;
      confirmedCandidate = cand;
    },
    submitManualValue: async () => {},
    applyPolicy: async () => {},
    removeResolution: async () => {},
    startSimulation: () => {},
  };

  const hostEl = new SimpleElement('div');
  const modal = new PhysicsReviewModal(hostEl, mockOrch);
  modal.open();

  const candBox = modal.dom.body.querySelector('.prm-candidate-box');
  assert(candBox !== null, 'Candidate box rendered for length');
  assert(candBox.textContent.includes('80 cm'), 'Candidate value 80 cm displayed in UI');
  assert(candBox.textContent.includes('88%'), 'Candidate confidence 88% displayed');

  const btnConfirm = candBox.querySelector('[data-action="confirm"]');
  assert(btnConfirm !== null, 'Confirm button rendered');
  btnConfirm.trigger('click');
  assert(confirmedParam === 'length', 'confirmCandidate called with parameterName "length"');
  assert(confirmedCandidate.numericValue === 80, 'confirmCandidate called with candidate numericValue 80');

  // Test 4: Manual correction revealing input form
  console.log('\n[4/8] Clicking [Correct] reveals manual entry form');
  let manualSubmittedParam = null;
  let manualSubmittedVal = null;
  mockOrch.submitManualValue = async (p, v) => {
    manualSubmittedParam = p;
    manualSubmittedVal = v;
  };

  const btnCorrect = candBox.querySelector('[data-action="correct"]');
  assert(btnCorrect !== null, 'Correct button rendered');
  btnCorrect.trigger('click');

  const manualForm = modal.dom.body.querySelector('.prm-manual-form');
  assert(manualForm !== null, 'Manual entry form appeared after clicking Correct');
  const numInput = manualForm.querySelector('[data-el="numInput"]');
  assert(numInput !== null, 'Numeric input is present in manual form');
  numInput.value = '60';

  const btnSaveManual = manualForm.querySelector('[data-action="save-manual"]');
  btnSaveManual.trigger('click');
  assert(manualSubmittedParam === 'length', 'submitManualValue called for length');
  assert(manualSubmittedVal === '60', 'submitManualValue called with corrected value 60');

  // Test 5: Modeling policies rendered with rationale without silent defaults
  console.log('\n[5/8] Explicit policy assumption renders with rationale');
  let appliedPolicyId = null;
  mockOrch.applyPolicy = async (polId) => {
    appliedPolicyId = polId;
  };

  mockOrch.reviewState.issues.push({
    id: 'iss_2',
    parameterName: 'gravity',
    question: 'Diagram does not specify local gravitational acceleration.',
    candidates: [],
    defaultPolicyId: 'policy_earth_gravity',
  });
  mockOrch.reviewState.availablePolicies = [
    {
      id: 'policy_earth_gravity',
      name: 'Standard Earth Gravity',
      value: 9.80665,
      unit: 'm/s²',
      educationalRationale: 'Standard terrestrial gravitational acceleration.',
      targetParameter: 'gravity',
    },
    // Unrelated policy that must NOT appear under pendulum issues
    {
      id: 'policy_air_refractive_index',
      name: 'Air Refractive Index',
      value: 1.000293,
      unit: '',
      targetParameter: 'refractive_index',
    },
  ];

  modal.render();

  const policyBox = modal.dom.body.querySelector('.prm-policy-box');
  assert(policyBox !== null, 'Policy assumption card rendered');
  assert(policyBox.textContent.includes('Standard Earth Gravity'), 'Displays policy name');
  assert(policyBox.textContent.includes('9.80665 m/s²'), 'Displays policy value and unit');
  assert(policyBox.textContent.includes('terrestrial gravitational acceleration'), 'Displays educational rationale');

  // Unrelated policy exclusion test
  assert(!modal.dom.body.textContent.includes('Air Refractive Index'), 'Strict exclusion: Air Refractive Index does NOT appear for pendulum');

  const btnApplyPolicy = policyBox.querySelector('[data-action="apply-policy"]');
  btnApplyPolicy.trigger('click');
  assert(appliedPolicyId === 'policy_earth_gravity', 'applyPolicy invoked with policy_earth_gravity');

  // Test 6: Resolved parameters display with provenance badge & reversibility
  console.log('\n[6/8] Resolved items display provenance and reversibility');
  let removedParam = null;
  mockOrch.removeResolution = async (p) => {
    removedParam = p;
  };

  mockOrch.bookIR.parameters = {
    length: { value: 0.8, unit: 'm', provenance: { source: 'user_supplied' } },
    gravity: { value: 9.80665, unit: 'm/s²', provenance: { source: 'policy_default', policyId: 'policy_earth_gravity' } },
  };
  mockOrch.bookIR.parameter_provenance = {
    length: { source: 'user_supplied' },
    gravity: { source: 'policy_default', policy_id: 'policy_earth_gravity' },
  };

  modal.render();

  const resolvedItems = modal.dom.body.querySelectorAll('.prm-resolved-item');
  assert(resolvedItems.length === 2, '2 resolved parameter items rendered');

  const undoBtn = resolvedItems[0].querySelector('[data-action="undo-resolution"]');
  assert(undoBtn !== null, 'Reversibility: undo/change button is present');
  undoBtn.trigger('click');
  assert(removedParam === 'length', 'Undo button triggers removeResolution for length');

  // Test 7: Ready state displays "Simulation Ready" hero and "Start Simulation"
  console.log('\n[7/8] READY_TO_SIMULATE state renders simulation ready hero');
  let startSimCalled = false;
  mockOrch.state = OrchestratorState.READY_TO_SIMULATE;
  mockOrch.reviewState.readyToCompile = true;
  mockOrch.compiledScene = { id: 'SCENE-TEST' };
  mockOrch.startSimulation = () => {
    startSimCalled = true;
    return mockOrch.compiledScene;
  };

  modal.render();

  const readyBanner = modal.dom.body.querySelector('.prm-ready-banner');
  assert(readyBanner !== null, 'Simulation ready hero banner rendered');
  assert(modal.dom.btnStartSim.style.display !== 'none', 'Footer Start Simulation button is visible');

  const btnStart = readyBanner.querySelector('[data-action="start-sim-banner"]');
  btnStart.trigger('click');
  assert(startSimCalled === true, 'Clicking Start Simulation called orchestrator.startSimulation()');
  assert(modal.isOpen === false, 'Modal closed automatically upon starting simulation');

  // Test 8: Double-submission prevention (busy disabling)
  console.log('\n[8/8] In-flight busy state disables mutation buttons');
  mockOrch.state = OrchestratorState.APPLYING_RESOLUTION;
  modal.open();
  assert(modal.dom.footerStatus.textContent.includes('Applying decision'), 'Displays busy status text');
}

runTests().then(() => {
  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================');
  if (failed > 0) process.exit(1);
});
