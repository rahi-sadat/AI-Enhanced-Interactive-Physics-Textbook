/**
 * circuits/view/P5CircuitView.js
 * 60 FPS transparent p5.js instance overlay for the circuit domain.
 * Renders:
 * - Conventional current particle flow along precompiled wire polylines
 * - Flow direction chevrons scaled by current magnitude
 * - Equipotential conductor halos and node voltage badges
 * - Component selection/hover outlines
 * - Virtual voltmeter/ammeter test leads and digital readouts
 * - Sub-pixel debug inspection layer
 */

import p5 from 'p5';

export class P5CircuitView {
  /**
   * @param {HTMLElement} hostElement - Container DOM element
   * @param {object} store - CircuitStore instance
   * @param {object} mapper - CoordinateMapper instance
   * @param {object} callbacks - Pointer / interaction callbacks
   */
  constructor(hostElement, store, mapper, callbacks = {}) {
    this.host = hostElement;
    this.store = store;
    this.mapper = mapper;
    this.callbacks = callbacks;

    this.particleOffset = 0.0;
    this.lastFrameTime = performance.now();

    // Node equipotential color palette
    this.nodeColors = {
      'N1': 'rgba(239, 68, 68, 0.25)',   // Red / positive rail
      'N1b': 'rgba(249, 115, 22, 0.25)', // Orange / post-switch rail
      'N2': 'rgba(16, 185, 129, 0.25)',  // Emerald / midpoint rail
      'N0': 'rgba(59, 130, 246, 0.22)',  // Blue / ground rail
      'A': 'rgba(239, 68, 68, 0.25)',
      'B': 'rgba(59, 130, 246, 0.22)',
      'C': 'rgba(168, 85, 247, 0.25)',
      'D': 'rgba(234, 179, 8, 0.25)'
    };

    this._initP5();
  }

  _initP5() {
    const sketch = (p) => {
      this.p = p;

      p.setup = () => {
        const rect = this.host.getBoundingClientRect();
        const w = Math.round(rect.width || this.host.clientWidth || 800);
        const h = Math.round(rect.height || this.host.clientHeight || 500);
        const canvas = p.createCanvas(w, h);
        canvas.style('position', 'absolute');
        canvas.style('top', '0');
        canvas.style('left', '0');
        canvas.style('pointer-events', 'auto');
        if (this.mapper) {
          this.mapper.update(this.mapper.sourceW, this.mapper.sourceH, w, h);
        }
        p.clear();
        p.frameRate(60);
      };

      p.mouseClicked = () => {
        const model = this.store?.model;
        if (!model?.switches || !this.mapper) return;
        const ptSrc = this.mapper.viewToSource(p.mouseX, p.mouseY);
        for (const sw of model.switches) {
          const tA = sw.terminals?.[0]?.source_px || [200, 120];
          const tB = sw.terminals?.[1]?.source_px || [260, 120];
          const midX = (tA[0] + tB[0]) / 2;
          const midY = (tA[1] + tB[1]) / 2;
          if (Math.hypot(ptSrc.x - midX, ptSrc.y - midY) < 60) {
            this.store.toggleSwitch?.(sw.id);
            break;
          }
        }
      };

      p.draw = () => {
        p.clear();
        const now = performance.now();
        const dt = Math.min((now - this.lastFrameTime) / 1000.0, 0.1);
        this.lastFrameTime = now;

        const model = this.store.model;
        const state = this.store.electricalState;
        const ui = this.store.uiState;

        if (!model || !this.mapper) return;

        // Auto-sync canvas and mapper dimensions if container resized
        const currentW = Math.round(this.host.clientWidth || 0);
        const currentH = Math.round(this.host.clientHeight || 0);
        if (currentW > 0 && currentH > 0 && (p.width !== currentW || p.height !== currentH)) {
          p.resizeCanvas(currentW, currentH);
          this.mapper.update(this.mapper.sourceW, this.mapper.sourceH, currentW, currentH);
        }

        // 1. Equipotential Wire Halos
        if (ui.showEquipotential) {
          this._drawEquipotentialHalos(p, model);
        }

        // 2. Conventional Current Particles along Wires
        if (ui.animationEnabled && state && state.success && state.primaryCurrent > 1e-6) {
          this._updateAndDrawCurrentParticles(p, model, state, dt);
        }

        // 3. Directional Flow Arrows
        if (state && state.success && state.primaryCurrent > 1e-6) {
          this._drawCurrentArrows(p, model, state);
        }

        // 4. Node Voltage Badges
        if (ui.showNodeVoltages && state && state.nodeVoltages) {
          this._drawNodeVoltageBadges(p, model, state);
        }

        // 5. Component Highlights (Selection & Hover)
        this._drawComponentHighlights(p, model, ui);

        // 6. Interactive Switches (Animated Levers & State Badges)
        this._drawSwitches(p, model, ui);

        // 7. Virtual Probes & Leads
        this._drawProbeLeads(p, ui);

        // 7. KCL & KVL Overlays
        if (ui.kclResult) {
          this._drawKCLOverlay(p, model, ui.kclResult);
        }
        if (ui.kvlResult) {
          this._drawKVLOverlay(p, model, ui.kvlResult);
        }

        // 8. Debug Inspection Layer (?debugCircuit=1)
        if (ui.debugOverlay) {
          this._drawDebugOverlay(p, model);
        }
      };
    };

    this.p5Instance = new p5(sketch, this.host);
  }

  resize(width = null, height = null, renderContext = null) {
    if (!this.p || !this.host) return;
    const w = Math.round(width || this.host.clientWidth || 800);
    const h = Math.round(height || this.host.clientHeight || 500);
    if (w > 0 && h > 0) {
      this.p.resizeCanvas(w, h);
      if (this.mapper) {
        const sw = renderContext?.sourceWidth || this.mapper.sourceW || 800;
        const sh = renderContext?.sourceHeight || this.mapper.sourceH || 500;
        this.mapper.update(sw, sh, w, h);
      }
      this.p.redraw?.();
    }
  }


  destroy() {
    if (this.p5Instance) {
      this.p5Instance.remove();
      this.p5Instance = null;
    }
  }

  // ---------------------------------------------------------------------------
  // Layer Rendering Helpers
  // ---------------------------------------------------------------------------

  _drawEquipotentialHalos(p, model) {
    p.push();
    p.strokeWeight(12 * this.mapper.scale);
    p.strokeCap(p.ROUND);
    p.strokeJoin(p.ROUND);
    p.noFill();

    for (const wire of model.wires) {
      const color = this.nodeColors[wire.node] || 'rgba(148, 163, 184, 0.18)';
      p.stroke(color);
      p.beginShape();
      for (const pt of wire.points) {
        const v = this.mapper.sourceToView(pt[0], pt[1]);
        p.vertex(v.x, v.y);
      }
      p.endShape();
    }
    p.pop();
  }

  _updateAndDrawCurrentParticles(p, model, state, dt) {
    const current = state.primaryCurrent || 0.0;
    if (current < 1e-5) return; // No current flowing when circuit is open

    // Logarithmic speed scaling: visualSpeed = baseSpeed * log1p(|I| / I_ref)
    const baseSpeed = 90.0; // px/sec in source coordinates
    const speed = baseSpeed * Math.log1p(current / 0.1);

    this.particleOffset = (this.particleOffset + speed * dt) % 10000;

    p.push();
    p.noStroke();

    for (const wire of model.wires) {
      const totalLen = wire.totalLength;
      if (totalLen <= 0) continue;

      // Density: spacing between particles
      const particleSpacing = 42.0; // source_px
      const numParticles = Math.max(1, Math.floor(totalLen / particleSpacing));

      for (let i = 0; i < numParticles; i++) {
        const dist = (this.particleOffset + i * particleSpacing) % totalLen;
        const ptSrc = wire.getPointAtDistance(dist);
        const ptView = this.mapper.sourceToView(ptSrc.x, ptSrc.y);

        // Draw particle with subtle glow
        p.fill(56, 189, 248, 70); // Cyan outer glow
        p.circle(ptView.x, ptView.y, 10 * this.mapper.scale);

        p.fill(224, 242, 254, 250); // White-cyan core
        p.circle(ptView.x, ptView.y, 4.5 * this.mapper.scale);
      }
    }
    p.pop();
  }

  _drawCurrentArrows(p, model, state) {
    const current = state.primaryCurrent || 0.0;
    if (current < 1e-5) return; // No directional arrows when circuit is open

    p.push();
    p.fill(14, 165, 233);
    p.noStroke();

    for (const wire of model.wires) {
      const totalLen = wire.totalLength;
      if (totalLen < 30) continue;

      // Draw arrow at midpoint of the wire
      const midDist = totalLen * 0.5;
      const ptSrc = wire.getPointAtDistance(midDist);
      const v = this.mapper.sourceToView(ptSrc.x, ptSrc.y);

      p.push();
      p.translate(v.x, v.y);
      p.rotate(ptSrc.angle);

      const size = 5.0 * this.mapper.scale;
      p.beginShape();
      p.vertex(size * 1.5, 0);
      p.vertex(-size, -size * 0.8);
      p.vertex(-size * 0.4, 0);
      p.vertex(-size, size * 0.8);
      p.endShape(p.CLOSE);
      p.pop();
    }
    p.pop();
  }

  _drawNodeVoltageBadges(p, model, state) {
    p.push();
    p.textFont('Inter, sans-serif');
    p.textSize(10 * Math.max(0.8, this.mapper.scale));

    for (const [nodeId, voltage] of Object.entries(state.nodeVoltages)) {
      // Find a representative wire or terminal for this node
      const term = [...model.terminalById.values()].find(t => t.node === nodeId);
      const wire = model.wires.find(w => w.node === nodeId);
      let badgeSrcPt = null;

      if (term?.source_px) {
        badgeSrcPt = { x: term.source_px[0], y: term.source_px[1] };
      } else if (wire?.points?.[0]) {
        badgeSrcPt = { x: wire.points[0][0], y: wire.points[0][1] };
      }

      if (!badgeSrcPt) continue;

      const v = this.mapper.sourceToView(badgeSrcPt.x, badgeSrcPt.y);
      const label = `${nodeId}: ${voltage >= 0 ? '+' : ''}${voltage.toFixed(1)}V`;

      // Badge background
      p.stroke(30, 41, 59, 180);
      p.strokeWeight(1);
      p.fill(15, 23, 42, 220);
      const badgeW = p.textWidth(label) + 12;
      const badgeH = 18;
      p.rect(v.x - badgeW / 2, v.y - 24, badgeW, badgeH, 4);

      // Badge text
      p.noStroke();
      p.fill(241, 245, 249);
      p.textAlign(p.CENTER, p.CENTER);
      p.text(label, v.x, v.y - 15);
    }
    p.pop();
  }

  _drawComponentHighlights(p, model, ui) {
    p.push();
    p.noFill();
    p.strokeCap(p.ROUND);

    const drawHighlight = (comp, isSelected) => {
      if (!comp?.geometry?.bbox_source_px) return;
      const [x1, y1, x2, y2] = comp.geometry.bbox_source_px;
      const v1 = this.mapper.sourceToView(x1, y1);
      const v2 = this.mapper.sourceToView(x2, y2);
      const w = v2.x - v1.x;
      const h = v2.y - v1.y;

      if (isSelected) {
        p.stroke(2, 132, 199, 230); // Neon sky blue
        p.strokeWeight(2.5);
        p.rect(v1.x - 4, v1.y - 4, w + 8, h + 8, 6);
        // Corner brackets
        p.stroke(56, 189, 248, 255);
        p.strokeWeight(3.5);
        p.point(v1.x - 4, v1.y - 4);
        p.point(v2.x + 4, v2.y + 4);
      } else {
        // Hover
        p.stroke(14, 165, 233, 160);
        p.strokeWeight(1.8);
        p.rect(v1.x - 3, v1.y - 3, w + 6, h + 6, 5);
      }
    };

    if (ui.hoveredComponentId && ui.hoveredComponentId !== ui.selectedComponentId) {
      const comp = model.componentById.get(ui.hoveredComponentId);
      if (comp) drawHighlight(comp, false);
    }

    if (ui.selectedComponentId) {
      const comp = model.componentById.get(ui.selectedComponentId);
      if (comp) drawHighlight(comp, true);
    }

    p.pop();
  }

  _drawProbeLeads(p, ui) {
    if (!ui.voltageProbe.active) return;
    const { leadRed, leadBlack } = ui.voltageProbe;

    p.push();
    p.strokeWeight(2.5 * this.mapper.scale);
    p.noFill();

    // Red lead (+)
    if (leadRed) {
      const vRed = this.mapper.sourceToView(leadRed.x, leadRed.y);
      p.stroke(239, 68, 68);
      p.circle(vRed.x, vRed.y, 10);
      p.fill(239, 68, 68);
      p.circle(vRed.x, vRed.y, 4);
      p.noFill();
    }

    // Black lead (-)
    if (leadBlack) {
      const vBlack = this.mapper.sourceToView(leadBlack.x, leadBlack.y);
      p.stroke(15, 23, 42);
      p.circle(vBlack.x, vBlack.y, 10);
      p.fill(51, 65, 85);
      p.circle(vBlack.x, vBlack.y, 4);
      p.noFill();
    }

    p.pop();
  }

  _drawDebugOverlay(p, model) {
    p.push();
    p.textFont('monospace');
    p.textSize(9);

    // Draw Terminals
    for (const [tId, term] of model.terminalById.entries()) {
      const [tx, ty] = term.source_px || [0, 0];
      const v = this.mapper.sourceToView(tx, ty);

      p.stroke(244, 63, 94);
      p.strokeWeight(2);
      p.fill(255);
      p.circle(v.x, v.y, 8);

      p.noStroke();
      p.fill(244, 63, 94);
      p.textAlign(p.LEFT, p.BOTTOM);
      p.text(`${tId} [${tx.toFixed(0)},${ty.toFixed(0)}]`, v.x + 6, v.y - 4);
    }

    // Draw Component BBoxes
    for (const [cId, comp] of model.componentById.entries()) {
      if (comp.geometry?.bbox_source_px) {
        const [x1, y1, x2, y2] = comp.geometry.bbox_source_px;
        const v1 = this.mapper.sourceToView(x1, y1);
        const v2 = this.mapper.sourceToView(x2, y2);

        p.stroke(168, 85, 247, 180);
        p.strokeWeight(1);
        p.noFill();
        p.rect(v1.x, v1.y, v2.x - v1.x, v2.y - v1.y);

        p.noStroke();
        p.fill(168, 85, 247);
        p.text(cId, v1.x, v1.y - 3);
      }
    }

    p.pop();
  }

  _drawKCLOverlay(p, model, kcl) {
    p.push();
    // Find representative coordinates for the inspected node
    const term = [...model.terminalById.values()].find(t => t.node === kcl.nodeId);
    const wire = model.wires.find(w => w.node === kcl.nodeId);
    let srcPt = term?.source_px ? { x: term.source_px[0], y: term.source_px[1] } : null;
    if (!srcPt && wire?.points?.[0]) {
      srcPt = { x: wire.points[0][0], y: wire.points[0][1] };
    }
    if (!srcPt) { p.pop(); return; }

    const v = this.mapper.sourceToView(srcPt.x, srcPt.y);

    // Glowing pulsing junction ring
    const pulse = Math.sin(performance.now() / 200.0) * 4;
    p.stroke(16, 185, 129, 230); // Emerald green
    p.strokeWeight(3);
    p.noFill();
    p.circle(v.x, v.y, 24 + pulse);

    // KCL Badge
    const label = `ΣI = 0 ✓ (${(kcl.sumIn * 1000).toFixed(0)}mA in = ${(kcl.sumOut * 1000).toFixed(0)}mA out)`;
    p.textFont('Inter, sans-serif');
    p.textSize(11);
    const badgeW = p.textWidth(label) + 16;
    const badgeH = 22;

    p.fill(15, 23, 42, 230);
    p.stroke(16, 185, 129, 200);
    p.strokeWeight(1.5);
    p.rect(v.x - badgeW / 2, v.y - 45, badgeW, badgeH, 6);

    p.noStroke();
    p.fill(52, 211, 153);
    p.textAlign(p.CENTER, p.CENTER);
    p.text(label, v.x, v.y - 34);

    p.pop();
  }

  _drawKVLOverlay(p, model, kvl) {
    p.push();
    p.stroke(245, 158, 11, 220); // Amber loop glow
    p.strokeWeight(3.5 * this.mapper.scale);
    p.noFill();

    // Trace all wires in the loop
    for (const wire of model.wires) {
      p.beginShape();
      for (const pt of wire.points) {
        const v = this.mapper.sourceToView(pt[0], pt[1]);
        p.vertex(v.x, v.y);
      }
      p.endShape();
    }

    // Centered KVL Loop Badge
    const centerView = this.mapper.sourceToView(400, 250);
    const label = `ΣV = 0 ✓ (+${kvl.sourceV.toFixed(1)}V - ${kvl.elements.filter(e => e.sign === '-').map(e => e.voltage.toFixed(1) + 'V').join(' - ')} = 0V)`;
    p.textFont('Inter, sans-serif');
    p.textSize(11.5);
    p.textStyle(p.BOLD);
    const badgeW = p.textWidth(label) + 20;
    const badgeH = 26;

    p.fill(15, 23, 42, 240);
    p.stroke(245, 158, 11, 240);
    p.strokeWeight(1.8);
    p.rect(centerView.x - badgeW / 2, centerView.y - badgeH / 2, badgeW, badgeH, 6);

    p.noStroke();
    p.fill(251, 191, 36);
    p.textAlign(p.CENTER, p.CENTER);
    p.text(label, centerView.x, centerView.y);

    p.pop();
  }

  _drawSwitches(p, model, ui) {
    p.push();
    for (const sw of model.switches) {
      const tA = sw.terminals?.[0]?.source_px || [200, 120];
      const tB = sw.terminals?.[1]?.source_px || [260, 120];
      const vA = this.mapper.sourceToView(tA[0], tA[1]);
      const vB = this.mapper.sourceToView(tB[0], tB[1]);
      const isOpen = sw.state === 'open';
      const isHovered = ui.hoveredComponentId === sw.id;

      // Draw terminal contact dots
      p.stroke(15, 23, 42);
      p.strokeWeight(2.5 * this.mapper.scale);
      p.fill(248, 250, 252);
      p.circle(vA.x, vA.y, 9 * this.mapper.scale);
      p.circle(vB.x, vB.y, 9 * this.mapper.scale);

      // Draw switch lever
      if (isOpen) {
        // Lever tilted up at ~35 degrees with gap
        p.stroke(245, 158, 11); // Amber
        p.strokeWeight(3.8 * this.mapper.scale);
        const leverLen = Math.hypot(vB.x - vA.x, vB.y - vA.y) * 0.95;
        const baseAngle = Math.atan2(vB.y - vA.y, vB.x - vA.x);
        const angle = baseAngle - 0.58; // tilt up
        const xEnd = vA.x + Math.cos(angle) * leverLen;
        const yEnd = vA.y + Math.sin(angle) * leverLen;
        p.line(vA.x, vA.y, xEnd, yEnd);
        p.fill(245, 158, 11);
        p.circle(xEnd, yEnd, 7 * this.mapper.scale);
      } else {
        // Lever closed (conductive connection)
        p.stroke(2, 132, 199); // Sky blue
        p.strokeWeight(4.0 * this.mapper.scale);
        p.line(vA.x, vA.y, vB.x, vB.y);
      }

      // Live Clickable Badge below switch
      const midX = (vA.x + vB.x) / 2;
      const midY = (vA.y + vB.y) / 2 + 22 * this.mapper.scale;

      const badgeText = isOpen ? '🔴 [OPEN - Click to Close]' : '🟢 [CLOSED - Click to Open]';
      p.textFont('Inter, sans-serif');
      p.textSize(10.5 * Math.max(0.8, this.mapper.scale));
      p.textStyle(p.BOLD);
      const badgeW = p.textWidth(badgeText) + 16;
      const badgeH = 20;

      p.fill(15, 23, 42, 235);
      p.stroke(isOpen ? '#f59e0b' : '#10b981');
      p.strokeWeight(isHovered ? 2.5 : 1.2);
      p.rect(midX - badgeW / 2, midY - badgeH / 2, badgeW, badgeH, 4);

      p.noStroke();
      p.fill(isOpen ? '#fbbf24' : '#34d399');
      p.textAlign(p.CENTER, p.CENTER);
      p.text(badgeText, midX, midY);
    }
    p.pop();
  }
}
