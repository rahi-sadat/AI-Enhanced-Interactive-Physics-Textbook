/** optics/view/opticsHUD.js - Live educational HUD card (pure HTML). */
export class OpticsHUD {
  constructor(id) {
    this.el = document.getElementById(id || 'optics-hud');
  }

  update(subtype, result, param1, pixelPerCm = null) {
    if (!this.el) return;
    if (subtype === 'interface_refraction') {
      this._updateInterfaceRefraction(result);
    } else if (subtype === 'prism') {
      this._updatePrism(result, param1);
    } else if (subtype === 'mirror') {
      this._updateMirror(result, param1, pixelPerCm);
    } else {
      this._updateLens(result, param1, pixelPerCm);
    }
  }

  _updateInterfaceRefraction(result) {
    const h = result.hud || {};
    const tirBadge = h.isTIR
      ? `<div class="hud-state tir">⚡ TOTAL INTERNAL REFLECTION (&theta;₁ > &theta;c)</div>`
      : `<div class="hud-state real">${h.stateLabel}</div>`;

    this.el.innerHTML = `
      <div class="hud-title">${h.title || "Interface Refraction"}</div>
      <div class="hud-row"><span class="hud-label">Medium 1 (rarer) n₁</span><span class="hud-val">${h.n1}</span></div>
      <div class="hud-row"><span class="hud-label">Medium 2 (denser) n₂</span><span class="hud-val">${h.n2}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-row"><span class="hud-label">Angle of incidence &theta;₁</span><span class="hud-val">${h.theta1}</span></div>
      <div class="hud-row"><span class="hud-label">Angle of refraction &theta;₂</span><span class="hud-val">${h.theta2}</span></div>
      <div class="hud-row"><span class="hud-label">Critical angle &theta;c</span><span class="hud-val">${h.criticalAngle}</span></div>
      <div class="hud-divider"></div>
      ${tirBadge}
      <div class="hud-formula">Snell's Law: <strong>n₁ &middot; sin(&theta;₁) = n₂ &middot; sin(&theta;₂)</strong></div>
    `;
  }

  _updateLens(result, fPx, pixelPerCm) {
    const px = (valPx) => {
      if (!isFinite(valPx)) return '∞';
      const absPx = Math.abs(valPx);
      if (pixelPerCm && pixelPerCm > 0) {
        const cm = (absPx / pixelPerCm).toFixed(1);
        return `${cm} cm <span class="hud-unit-sub">(${absPx.toFixed(0)} px)</span>`;
      }
      return `${absPx.toFixed(0)} px`;
    };

    const mfm = (v) => isFinite(v) ? v.toFixed(2) : '∞';
    const sc  = result.isReal ? 'real' : (result.imageType === 'infinity' ? 'infinity' : 'virtual');
    const lbl = this._stateLabel(result);
    const chk = this._checkFormula(result.u, result.v, fPx, result.imageType);

    const title = (fPx < 0 || result.lensType === 'concave') ? 'Concave Lens (Diverging)' : 'Convex Lens (Converging)';
    this.el.innerHTML = `
      <div class="hud-title">${title} &mdash; 1/f = 1/u + 1/v</div>
      <div class="hud-row"><span class="hud-label">u (object dist.)</span><span class="hud-val">${px(result.u)}</span></div>
      <div class="hud-row"><span class="hud-label">v (image dist.)</span><span class="hud-val">${px(result.v)}</span></div>
      <div class="hud-row"><span class="hud-label">f (focal length)</span><span class="hud-val">${px(fPx)}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-row"><span class="hud-label">m (magnification)</span><span class="hud-val">${mfm(result.magnification)}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-state ${sc}">${lbl}</div>
      <div class="hud-formula">Formula 1/f = 1/u + 1/v: <strong>${chk}</strong></div>
    `;
  }

  _updatePrism(result, n) {
    const ang = result.angles || {};
    const i1 = ang.i1Deg != null ? ang.i1Deg.toFixed(1) + '°' : '—';
    const r1 = ang.r1Deg != null ? ang.r1Deg.toFixed(1) + '°' : '—';
    const dev = ang.deviationDeg != null ? ang.deviationDeg.toFixed(1) + '°' : 'N/A (TIR)';
    const crit = ang.criticalAngleDeg != null ? ang.criticalAngleDeg.toFixed(1) + '°' : '41.8°';

    let tirBadge;
    if (result.tir) {
      tirBadge = `<div class="hud-state tir">⚡ TOTAL INTERNAL REFLECTION (&theta;i > &theta;c)</div>`;
    } else if (ang.deviationDeg != null && Math.abs(ang.deviationDeg) < 0.5) {
      tirBadge = `<div class="hud-state real">✓ Parallel Emergent Beam &middot; &delta; = 0° (Lateral Shift)</div>`;
    } else {
      tirBadge = `<div class="hud-state real">Refracted Beam &middot; Emergent ray deviation &delta; = ${dev}</div>`;
    }

    this.el.innerHTML = `
      <div class="hud-title">Prism &mdash; Snell's Law n₁ sin i = n₂ sin r</div>
      <div class="hud-row"><span class="hud-label">Refractive index n</span><span class="hud-val">${n.toFixed(2)}</span></div>
      <div class="hud-row"><span class="hud-label">Incidence angle i₁</span><span class="hud-val">${i1}</span></div>
      <div class="hud-row"><span class="hud-label">Refraction angle r₁</span><span class="hud-val">${r1}</span></div>
      <div class="hud-row"><span class="hud-label">Critical angle &theta;c</span><span class="hud-val">${crit}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-row"><span class="hud-label">Angle of deviation &delta;</span><span class="hud-val">${dev}</span></div>
      <div class="hud-divider"></div>
      ${tirBadge}
    `;
  }

  _updateMirror(result, fPx, pixelPerCm) {
    const px = (valPx) => {
      if (!isFinite(valPx)) return '∞';
      const absPx = Math.abs(valPx);
      if (pixelPerCm && pixelPerCm > 0) {
        const cm = (absPx / pixelPerCm).toFixed(1);
        return `${cm} cm <span class="hud-unit-sub">(${absPx.toFixed(0)} px)</span>`;
      }
      return `${absPx.toFixed(0)} px`;
    };

    const mfm = (v) => isFinite(v) ? v.toFixed(2) : '∞';
    const sc  = result.isReal ? 'real' : (result.imageType === 'infinity' ? 'infinity' : 'virtual');
    const lbl = this._stateLabel(result);
    const chk = this._checkFormula(result.u, result.v, fPx, result.imageType);

    this.el.innerHTML = `
      <div class="hud-title">${result.mirrorType === 'convex' ? 'Convex' : 'Concave'} Mirror &mdash; 1/f = 1/u + 1/v</div>
      <div class="hud-row"><span class="hud-label">u (object dist.)</span><span class="hud-val">${px(result.u)}</span></div>
      <div class="hud-row"><span class="hud-label">v (image dist.)</span><span class="hud-val">${px(result.v)}</span></div>
      <div class="hud-row"><span class="hud-label">f (focal length)</span><span class="hud-val">${px(fPx)}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-row"><span class="hud-label">m (magnification)</span><span class="hud-val">${mfm(result.magnification)}</span></div>
      <div class="hud-divider"></div>
      <div class="hud-state ${sc}">${lbl}</div>
      <div class="hud-formula">Formula 1/f = 1/u + 1/v: <strong>${chk}</strong></div>
    `;
  }

  _stateLabel(r) {
    if (r.imageType === 'infinity') return '⚡ Object at F &mdash; Image at ∞';
    const real   = r.isReal     ? 'Real'     : 'Virtual';
    const orient = r.isInverted ? 'Inverted' : 'Upright';
    const sz     = !isFinite(r.magnification) ? 'Magnified'
                 : Math.abs(r.magnification) > 1.05 ? 'Magnified'
                 : Math.abs(r.magnification) < 0.95 ? 'Diminished' : 'Same size';
    return `${real} &middot; ${orient} &middot; ${sz}`;
  }

  _checkFormula(u, v, f, type) {
    if (type === 'infinity') return '✓ (1/u = 1/f, v → ∞)';
    if (!isFinite(v) || u === 0 || f === 0) return '?';
    const diff = Math.abs(1/f - (1/u + 1/v));
    return diff < 0.001 ? '✓ Verified' : `? (Δ=${diff.toFixed(4)})`;
  }
}


