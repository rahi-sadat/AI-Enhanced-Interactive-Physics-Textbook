/**
 * circuits/CircuitTutorBridge.js
 * Bridges solver facts with the AI Tutor.
 * Constructs grounded bilingual (Bangla + English) explanations using
 * exact before/after solver diffs whenever a parameter or switch changes.
 */

export class CircuitTutorBridge {
  /**
   * @param {HTMLElement} hostContainer
   * @param {object} store - CircuitStore instance
   */
  constructor(hostContainer, store) {
    this.host = hostContainer;
    this.store = store;
    this.drawerElement = null;
    this._createDOM();
  }

  _createDOM() {
    this.drawerElement = document.createElement('div');
    this.drawerElement.className = 'circuit-tutor-drawer';
    this.drawerElement.style.display = 'none';
    this.drawerElement.addEventListener('pointerdown', (e) => e.stopPropagation());
    this.drawerElement.addEventListener('click', (e) => e.stopPropagation());
    this.host.appendChild(this.drawerElement);
  }

  /**
   * Explain why values changed for a given component.
   * @param {string} componentId
   * @param {object} [diffPayload]
   */
  explainChange(componentId, diffPayload = null) {
    const model = this.store.model;
    const state = this.store.electricalState;
    const comp = model.componentById.get(componentId);
    if (!comp || !state) return;

    const vs = model.voltageSources?.[0];
    const sourceV = vs ? Number(vs.value ?? 12.0) : 12.0;
    const current = state.primaryCurrent || 0.0;
    const req = state.equivalentResistance || 0.0;
    const vDrop = state.componentVoltages?.[comp.id] ?? 0.0;

    let banglaExp = '';
    let englishExp = '';

    if (comp.type === 'switch') {
      if (comp.state === 'open') {
        banglaExp = `চাবি ${comp.label || comp.id} খুলে দেওয়ায় (Open) বর্তনীটি বিচ্ছিন্ন হয়ে গেছে। ফলে ওহমের সূত্রানুসারে বর্তনী দিয়ে কোনো তড়িৎ প্রবাহিত হতে পারছে না (I = 0 A)।`;
        englishExp = `Opening the switch ${comp.id} breaks the closed electrical loop, dropping total current to 0 A.`;
      } else {
        banglaExp = `চাবি ${comp.label || comp.id} বন্ধ করায় (Closed) বর্তনীটি পুনরায় সম্পূর্ণ হয়েছে। ${sourceV} V ব্যাটারি থেকে এখন মোট ${current.toFixed(3)} A কারেন্ট প্রবাহিত হচ্ছে।`;
        englishExp = `Closing the switch completes the circuit, allowing ${current.toFixed(3)} A to flow from the ${sourceV} V battery.`;
      }
    } else if (comp.type === 'resistor') {
      const prevVal = diffPayload?.previous ?? comp.provenance?.value ?? 10.0;
      const curVal = Number(comp.value);
      const increased = curVal > prevVal;

      banglaExp = `
        ${comp.label || comp.id}-এর রোধ <strong>${prevVal.toFixed(1)} Ω</strong> থেকে ${increased ? 'বৃদ্ধি করে' : 'কমিয়ে'} 
        <strong>${curVal.toFixed(1)} Ω</strong> করা হয়েছে। 
        <br><br>
        এর ফলে বর্তনীর মোট সমতুল্য রোধ পরিবর্তিত হয়ে <strong>${req.toFixed(1)} Ω</strong> হয়েছে। 
        ওহমের সূত্র <em>(I = V / R_{eq})</em> অনুযায়ী ব্যাটারির অপরিবর্তিত ${sourceV} V বিভবের কারণে মোট তড়িৎ প্রবাহ 
        <strong>${increased ? 'হ্রাস পেয়ে' : 'বৃদ্ধি পেয়ে'} ${(current * 1000).toFixed(1)} mA</strong> হয়েছে। 
        <br><br>
        ডায়াগ্রামে কারেন্ট কণাগুলোর চলাচলের গতিও এই প্রবাহের পরিবর্তনের সাথে তাৎক্ষণিকভাবে পরিবর্তিত হয়েছে।
      `;

      englishExp = `
        Changing ${comp.id} from ${prevVal} Ω to ${curVal} Ω modified the total equivalent resistance to ${req.toFixed(1)} Ω.
        By Ohm's Law (I = V / R_eq), the battery current adjusted to ${(current * 1000).toFixed(1)} mA.
      `;
    }

    this.drawerElement.innerHTML = `
      <div class="tutor-drawer-content">
        <div class="tutor-drawer-header">
          <div class="tutor-avatar">🤖</div>
          <div>
            <div class="tutor-title">Augmented Physics AI Tutor</div>
            <div class="tutor-sub">বিজ্ঞানসম্মত নির্ভুল বিশ্লেষণ (Grounded Circuit Derivation)</div>
          </div>
          <button class="tutor-close-btn" id="tutor-close-btn">&times;</button>
        </div>

        <div class="tutor-drawer-body">
          <div class="tutor-message bangla-text">
            ${banglaExp}
          </div>

          <div class="tutor-message-en">
            <span class="en-label">English Summary:</span> ${englishExp}
          </div>

          <div class="tutor-facts-box">
            <div class="fact-row"><span>Target Element:</span> <strong>${comp.label || comp.id} (${comp.value} ${comp.unit || 'Ω'})</strong></div>
            <div class="fact-row"><span>Voltage Drop:</span> <strong>${vDrop.toFixed(2)} V</strong></div>
            <div class="fact-row"><span>Branch Current:</span> <strong>${(Math.abs(state.componentCurrents?.[comp.id] ?? 0) * 1000).toFixed(1)} mA</strong></div>
            <div class="fact-row"><span>Power Dissipation:</span> <strong>${(state.componentPower?.[comp.id] ?? 0).toFixed(2)} W</strong></div>
          </div>
        </div>
      </div>
    `;

    this.drawerElement.style.display = 'block';

    const btnClose = this.drawerElement.querySelector('#tutor-close-btn');
    if (btnClose) {
      btnClose.addEventListener('click', () => {
        this.drawerElement.style.display = 'none';
      });
    }
  }

  destroy() {
    if (this.drawerElement && this.drawerElement.parentNode) {
      this.drawerElement.parentNode.removeChild(this.drawerElement);
    }
    this.drawerElement = null;
  }
}
