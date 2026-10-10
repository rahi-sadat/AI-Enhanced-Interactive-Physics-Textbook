/**
 * apps/web/src/features/simulations/circuits/CircuitRenderer.js
 * 
 * Generic, graph-driven circuit simulation renderer.
 * Consumes solved RuntimeOutput geometry (wires, components, switches, node voltages, branch currents).
 * Visualizes conventional current particle flow and interactive switch states on top of
 * the original textbook diagram without re-solving MNA physics.
 */

import { SimulationRenderer } from '../core/SimulationRenderer.js';

export class CircuitRenderer extends SimulationRenderer {
  constructor() {
    super();
    this.svg = null;
    this.layers = {
      wires: null,
      flow: null,
      nodes: null,
      switches: null,
      components: null,
      handles: null,
    };

    this._animFrameId = null;
    this._particleOffset = 0.0;
    this._lastFrameTime = performance.now();
    this._boundOnPointerDown = this._handlePointerDown.bind(this);
  }

  mount({ container, sourceImage = null, scene, coordinateMapper, onInteract = () => {} }) {
    super.mount({ container, sourceImage, scene, coordinateMapper, onInteract });

    container.innerHTML = '';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'circuit-overlay-svg');
    svg.style.position = 'absolute';
    svg.style.overflow = 'visible';
    svg.style.pointerEvents = 'none';
    svg.style.userSelect = 'none';

    // Layer groups
    const gWires = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gWires.setAttribute('class', 'circuit-layer-wires');
    const gFlow = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gFlow.setAttribute('class', 'circuit-layer-flow');
    const gNodes = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gNodes.setAttribute('class', 'circuit-layer-nodes');
    const gSwitches = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gSwitches.setAttribute('class', 'circuit-layer-switches');
    const gComponents = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gComponents.setAttribute('class', 'circuit-layer-components');
    const gHandles = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gHandles.setAttribute('class', 'circuit-layer-handles');
    gHandles.style.pointerEvents = 'auto';

    svg.appendChild(gWires);
    svg.appendChild(gFlow);
    svg.appendChild(gNodes);
    svg.appendChild(gSwitches);
    svg.appendChild(gComponents);
    svg.appendChild(gHandles);

    container.appendChild(svg);
    this.svg = svg;
    this.layers = {
      wires: gWires,
      flow: gFlow,
      nodes: gNodes,
      switches: gSwitches,
      components: gComponents,
      handles: gHandles,
    };

    this.resize(coordinateMapper);

    container.addEventListener('pointerdown', this._boundOnPointerDown);

    // Start 60 FPS current flow particle loop
    this._startAnimationLoop();
  }

  resize(coordinateMapper) {
    super.resize(coordinateMapper);
    if (!this.svg || !this.coordinateMapper) return;

    const m = this.coordinateMapper;
    const isContained = Boolean(this.container?.classList?.contains?.('figure-viewport-overlay'));
    if (isContained) {
      this.svg.style.left = '0px';
      this.svg.style.top = '0px';
      this.svg.style.width = '100%';
      this.svg.style.height = '100%';
    } else {
      this.svg.style.left = `${m.offsetX}px`;
      this.svg.style.top = `${m.offsetY}px`;
      this.svg.style.width = `${m.renderedW}px`;
      this.svg.style.height = `${m.renderedH}px`;
    }
    this.svg.setAttribute('viewBox', `0 0 ${m.sourceW} ${m.sourceH}`);
    this.svg.setAttribute('width', String(m.renderedW));
    this.svg.setAttribute('height', String(m.renderedH));
  }

  render(runtimeOutput) {
    super.render(runtimeOutput);
    if (!this.svg || !runtimeOutput) return;

    const geom = runtimeOutput.geometry || {};
    this._clearStaticLayers();

    this._renderWires(geom);
    this._renderSwitches(geom);
    this._renderNodeBadges(geom);
    this._renderComponents(geom);
  }

  _clearStaticLayers() {
    this.layers.wires.innerHTML = '';
    this.layers.nodes.innerHTML = '';
    this.layers.switches.innerHTML = '';
    this.layers.components.innerHTML = '';
    this.layers.handles.innerHTML = '';
  }

  // ---------------------------------------------------------------------------
  // Graph-Driven Visual Elements
  // ---------------------------------------------------------------------------

  _getNodeStyle(nodeId, nodeVoltages) {
    const v = nodeVoltages?.[nodeId] ?? 0.0;
    const allV = Object.values(nodeVoltages || {});
    const maxV = allV.length > 0 ? Math.max(...allV, 1.0) : 1.0;

    if (Math.abs(v) < 1e-4) {
      // Ground / 0V Reference: Cyan/Blue
      return {
        color: '#38bdf8',
        glow: 'rgba(56, 189, 248, 0.35)',
        border: '#0284c7',
        bg: 'rgba(15, 23, 42, 0.92)',
        voltage: v
      };
    }
    if (v >= maxV * 0.70) {
      // High Potential / Supply: Red / Coral / Rose
      return {
        color: '#f87171',
        glow: 'rgba(239, 68, 68, 0.35)',
        border: '#dc2626',
        bg: 'rgba(15, 23, 42, 0.92)',
        voltage: v
      };
    }
    // Intermediate Potential: Emerald / Green
    return {
      color: '#34d399',
      glow: 'rgba(52, 211, 153, 0.35)',
      border: '#059669',
      bg: 'rgba(15, 23, 42, 0.92)',
      voltage: v
    };
  }

  _formatCurrent(a) {
    if (a === undefined || a === null || isNaN(a)) return '0 A';
    const abs = Math.abs(a);
    if (abs >= 1.0) return `${abs.toFixed(2)} A`;
    if (abs >= 0.001) return `${(abs * 1000).toFixed(0)} mA`;
    if (abs >= 1e-6) return `${(abs * 1e6).toFixed(0)} µA`;
    return '0 A';
  }

  _renderWires(geom) {
    const wires = geom.wires || [];
    const nodeVoltages = geom.nodeVoltages || {};

    for (const w of wires) {
      const pts = w.points || [];
      if (pts.length < 2) continue;

      const pathStr = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`).join(' ');
      const style = this._getNodeStyle(w.node, nodeVoltages);

      // 1. Outer Translucent Glow Halo (Node Potential Color)
      const haloPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      haloPath.setAttribute('d', pathStr);
      haloPath.setAttribute('fill', 'none');
      haloPath.setAttribute('stroke', style.glow);
      haloPath.setAttribute('stroke-width', '14');
      haloPath.setAttribute('stroke-linecap', 'round');
      haloPath.setAttribute('stroke-linejoin', 'round');
      this.layers.wires.appendChild(haloPath);

      // 2. Conductor Glow Border
      const borderPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      borderPath.setAttribute('d', pathStr);
      borderPath.setAttribute('fill', 'none');
      borderPath.setAttribute('stroke', style.color);
      borderPath.setAttribute('stroke-width', '5');
      borderPath.setAttribute('stroke-opacity', '0.7');
      borderPath.setAttribute('stroke-linecap', 'round');
      borderPath.setAttribute('stroke-linejoin', 'round');
      this.layers.wires.appendChild(borderPath);

      // 3. Dark Conductor Core
      const corePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      corePath.setAttribute('d', pathStr);
      corePath.setAttribute('fill', 'none');
      corePath.setAttribute('stroke', '#0f172a');
      corePath.setAttribute('stroke-width', '2.5');
      corePath.setAttribute('stroke-linecap', 'round');
      corePath.setAttribute('stroke-linejoin', 'round');
      this.layers.wires.appendChild(corePath);
    }
  }

  _renderSwitches(geom) {
    const switches = geom.switches || [];
    for (const s of switches) {
      const isClosed = s.closed;
      const tA = s.terminals?.[0]?.source_px;
      const tB = s.terminals?.[1]?.source_px;

      // If terminal coordinates are missing: DO NOT FABRICATE coordinates.
      // Cleanly skip rendering switch lever and terminals.
      if (!tA || !tB || !Array.isArray(tA) || !Array.isArray(tB)) {
        continue;
      }

      // Switch terminals
      const cA = this._createCircle(tA[0], tA[1], 4.5, { fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 1.5 });
      const cB = this._createCircle(tB[0], tB[1], 4.5, { fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 1.5 });
      this.layers.switches.appendChild(cA);
      this.layers.switches.appendChild(cB);

      // Switch lever (closed = bridge; open = angled lever)
      const lever = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      lever.setAttribute('x1', String(tA[0]));
      lever.setAttribute('y1', String(tA[1]));

      if (isClosed) {
        lever.setAttribute('x2', String(tB[0]));
        lever.setAttribute('y2', String(tB[1]));
        lever.setAttribute('stroke', '#10b981');
        lever.setAttribute('stroke-width', '4');
      } else {
        // Lever open at ~35 degree angle
        const dx = tB[0] - tA[0];
        const dy = tB[1] - tA[1];
        const len = Math.hypot(dx, dy) * 0.95;
        const angle = Math.atan2(dy, dx) - Math.PI / 5;
        const lx2 = tA[0] + len * Math.cos(angle);
        const ly2 = tA[1] + len * Math.sin(angle);
        lever.setAttribute('x2', String(lx2));
        lever.setAttribute('y2', String(ly2));
        lever.setAttribute('stroke', '#ef4444');
        lever.setAttribute('stroke-width', '3.5');
      }
      this.layers.switches.appendChild(lever);

      // Switch status badge
      const midX = (tA[0] + tB[0]) / 2;
      const midY = (tA[1] + tB[1]) / 2;
      const statusText = isClosed ? 'CLOSED' : 'OPEN';
      const statusColor = isClosed ? '#10b981' : '#ef4444';
      const badge = this._createText(midX, midY - 14, `${s.id} (${statusText})`, {
        fill: statusColor,
        fontSize: 11,
        fontWeight: 'bold',
        textAnchor: 'middle'
      });
      this.layers.switches.appendChild(badge);

      // Interactive hit target circle: ONLY rendered when hitTarget exists from geometric evidence
      if (s.hitTarget && Number.isFinite(s.hitTarget.x) && Number.isFinite(s.hitTarget.y)) {
        const hitArea = this._createCircle(s.hitTarget.x, s.hitTarget.y, s.hitTarget.radius || 35, {
          fill: 'rgba(245, 158, 11, 0.08)',
          stroke: 'rgba(245, 158, 11, 0.4)',
          strokeWidth: 1.5,
          strokeDasharray: '4 3',
          cursor: 'pointer',
          class: 'if-handle if-handle-switch'
        });
        hitArea.setAttribute('data-target-id', s.id);
        hitArea.setAttribute('data-action', 'toggle_switch');
        this.layers.handles.appendChild(hitArea);
      }
    }
  }

  _renderNodeBadges(geom) {
    const nodeVoltages = geom.nodeVoltages || {};
    const wires = geom.wires || [];
    const components = geom.components || [];

    // Collect all source points corresponding to each node (from wires and terminals)
    const nodePoints = new Map();
    for (const w of wires) {
      if (!w.node) continue;
      if (!nodePoints.has(w.node)) nodePoints.set(w.node, []);
      for (const p of (w.points || [])) {
        nodePoints.get(w.node).push(p);
      }
    }

    for (const c of components) {
      for (const t of (c.terminals || [])) {
        if (t.node && t.source_px) {
          if (!nodePoints.has(t.node)) nodePoints.set(t.node, []);
          nodePoints.get(t.node).push(t.source_px);
        }
      }
    }

    const allV = Object.values(nodeVoltages).map(Number);
    const maxV = allV.length > 0 ? Math.max(...allV, 1.0) : 1.0;

    let badgeIdx = 0;
    for (const [nodeId, voltage] of Object.entries(nodeVoltages)) {
      const pts = nodePoints.get(nodeId);
      if (!pts || pts.length === 0) continue;

      const vNum = Number(voltage);
      const isSupply = (vNum >= maxV * 0.75 && maxV > 0);
      const isGround = (Math.abs(vNum) < 1e-4);
      const style = this._getNodeStyle(nodeId, nodeVoltages);
      const vText = `${nodeId}: ${vNum >= 0 ? '+' : ''}${vNum.toFixed(1)}V`;

      const xs = pts.map(p => p[0]);
      const ys = pts.map(p => p[1]);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);

      const width = 76;
      const height = 20;

      // Find horizontal rail wires for this node to place badges cleanly along rails
      const nodeWires = wires.filter(w => w.node === nodeId && (w.points || []).length >= 2);
      const hWires = nodeWires.filter(w => Math.abs(w.points[0][1] - w.points[1][1]) < 8);

      let bx, by;
      if (hWires.length > 0) {
        const hxMin = Math.min(...hWires.flatMap(w => [w.points[0][0], w.points[1][0]]));
        const hxMax = Math.max(...hWires.flatMap(w => [w.points[0][0], w.points[1][0]]));
        const railY = hWires[0].points[0][1];
        bx = (hxMin + hxMax) / 2 - width / 2;

        if (isSupply || railY <= minY + 25) {
          by = railY - height - 12;
        } else if (isGround || railY >= maxY - 25) {
          by = railY + 14;
        } else {
          by = railY - height / 2;
        }
      } else {
        bx = (minX + maxX) / 2 - width / 2;
        by = (minY + maxY) / 2 - height / 2;
        if (isSupply) {
          by = minY - height - 12;
        } else if (isGround) {
          by = maxY + 14;
        } else {
          by += (badgeIdx % 2 === 0 ? -24 : 24);
        }
      }

      // Component Collision Avoidance: never allow a node badge to render on top of a resistor or component
      for (const c of components) {
        const cCenter = c.center_source_px || (c.bbox_source_px ? [(c.bbox_source_px[0] + c.bbox_source_px[2]) / 2, (c.bbox_source_px[1] + c.bbox_source_px[3]) / 2] : null);
        if (!cCenter) continue;
        const [cx, cy] = cCenter;
        const overlapsX = Math.abs((bx + width / 2) - cx) < 65;
        const overlapsY = Math.abs((by + height / 2) - cy) < 45;
        if (overlapsX && overlapsY) {
          if (by + height / 2 < cy) {
            by = cy - 45 - height;
          } else {
            by = cy + 45;
          }
        }
      }

      badgeIdx++;

      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'circuit-node-badge');

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', String(bx));
      rect.setAttribute('y', String(by));
      rect.setAttribute('width', String(width));
      rect.setAttribute('height', String(height));
      rect.setAttribute('rx', '5');
      rect.setAttribute('fill', style.bg);
      rect.setAttribute('stroke', style.color);
      rect.setAttribute('stroke-width', '1.5');
      rect.setAttribute('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))');

      const text = this._createText(bx + width / 2, by + height / 2 + 4, vText, {
        fill: style.color,
        fontSize: 10.5,
        fontWeight: 'bold',
        textAnchor: 'middle'
      });

      g.appendChild(rect);
      g.appendChild(text);
      this.layers.nodes.appendChild(g);
    }
  }

  _renderComponents(geom) {
    const components = geom.components || [];
    for (const c of components) {
      if (c.type === 'switch') continue;

      const center = c.center_source_px || (c.bbox_source_px ? [(c.bbox_source_px[0] + c.bbox_source_px[2]) / 2, (c.bbox_source_px[1] + c.bbox_source_px[3]) / 2] : null);
      const lblBox = c.label_bbox_source_px || (c.geometry?.label_bbox_source_px);

      if (!center && !lblBox) continue;

      const [cx, cy] = center || [0, 0];
      const cur = c.current_A != null ? Math.abs(c.current_A) : null;
      const curText = this._formatCurrent(cur);

      let valNumStr = '';
      let unitStr = '';
      if (c.value != null) {
        if (c.type === 'voltage_source' || c.type === 'battery' || c.type === 'dc_source') {
          valNumStr = `${Number(c.value.toFixed(1))}`;
          unitStr = 'V';
        } else {
          if (c.value >= 1000) {
            valNumStr = `${(c.value / 1000).toFixed(1)}`;
            unitStr = 'kΩ';
          } else {
            valNumStr = `${Number(c.value.toFixed(1))}`;
            unitStr = 'Ω';
          }
        }
      }

      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'circuit-component-ar');

      if (Array.isArray(lblBox) && lblBox.length >= 4) {
        const [lx, ly, lw, lh] = lblBox;

        // 1. In-diagram seamless whiteout patch covering static textbook text
        const patch = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        patch.setAttribute('x', String(lx - 3));
        patch.setAttribute('y', String(ly - 2));
        patch.setAttribute('width', String(lw + 6));
        patch.setAttribute('height', String(lh + 4));
        patch.setAttribute('rx', '3');
        patch.setAttribute('fill', '#ffffff');
        patch.setAttribute('fill-opacity', '0.98');
        patch.setAttribute('stroke', 'none');
        g.appendChild(patch);

        // 2. Textbook style math typography matching textbook print
        const fontSize = Math.max(16, Math.min(32, lh * 0.72));
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', String(lx + lw / 2));
        text.setAttribute('y', String(ly + lh * 0.68));
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#0f172a');
        text.setAttribute('font-family', 'Cambria, "Times New Roman", STIXGeneral, serif');
        text.setAttribute('font-size', String(fontSize));
        text.setAttribute('font-weight', '600');

        const isVolt = (c.type === 'voltage_source' || c.type === 'battery' || c.type === 'dc_source');
        const desigLetter = isVolt ? 'V' : 'R';
        const subIndex = c.id.replace(/^[a-zA-Z]+/, '');

        const tspanVar = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
        tspanVar.setAttribute('font-style', 'italic');
        tspanVar.textContent = desigLetter;
        text.appendChild(tspanVar);

        if (subIndex) {
          const tspanSub = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          tspanSub.setAttribute('dy', String(fontSize * 0.22));
          tspanSub.setAttribute('font-size', '0.75em');
          tspanSub.textContent = subIndex;
          text.appendChild(tspanSub);

          const tspanReset = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          tspanReset.setAttribute('dy', String(-fontSize * 0.22));
          tspanReset.textContent = ` = ${valNumStr} ${unitStr}`;
          text.appendChild(tspanReset);
        } else {
          const tspanVal = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          tspanVal.textContent = ` = ${valNumStr} ${unitStr}`;
          text.appendChild(tspanVal);
        }
        g.appendChild(text);

        // 3. Compact branch current indicator below textbook label
        if (cur != null) {
          const pillW = 78;
          const pillH = 18;
          const pillX = lx + lw / 2 - pillW / 2;
          const pillY = ly + lh + 5;

          const pillBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          pillBg.setAttribute('x', String(pillX));
          pillBg.setAttribute('y', String(pillY));
          pillBg.setAttribute('width', String(pillW));
          pillBg.setAttribute('height', String(pillH));
          pillBg.setAttribute('rx', '4');
          pillBg.setAttribute('fill', 'rgba(15, 23, 42, 0.90)');
          pillBg.setAttribute('stroke', '#38bdf8');
          pillBg.setAttribute('stroke-width', '1');
          pillBg.setAttribute('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))');
          g.appendChild(pillBg);

          const pillText = this._createText(pillX + pillW / 2, pillY + 12.5, `I = ${curText}`, {
            fill: '#38bdf8',
            fontSize: 10,
            fontWeight: 'bold',
            textAnchor: 'middle'
          });
          g.appendChild(pillText);
        }
      } else {
        // Fallback when no OCR label box exists: render adjacent to component center
        const width = 88;
        const height = 28;
        const bx = cx + 20;
        const by = cy - height / 2;

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', String(bx));
        rect.setAttribute('y', String(by));
        rect.setAttribute('width', String(width));
        rect.setAttribute('height', String(height));
        rect.setAttribute('rx', '6');
        rect.setAttribute('fill', 'rgba(15, 23, 42, 0.92)');
        rect.setAttribute('stroke', '#f59e0b');
        rect.setAttribute('stroke-width', '1.5');
        rect.setAttribute('filter', 'drop-shadow(0 2px 6px rgba(0,0,0,0.5))');
        g.appendChild(rect);

        const textVal = this._createText(bx + width / 2, by + 11.5, `${c.id} = ${valNumStr} ${unitStr}`, {
          fill: '#f8fafc',
          fontSize: 10,
          fontWeight: 'bold',
          textAnchor: 'middle'
        });
        g.appendChild(textVal);

        const textCur = this._createText(bx + width / 2, by + 22, `I = ${curText}`, {
          fill: '#38bdf8',
          fontSize: 9,
          fontWeight: '600',
          textAnchor: 'middle'
        });
        g.appendChild(textCur);
      }

      this.layers.components.appendChild(g);
    }
  }

  // ---------------------------------------------------------------------------
  // 60 FPS Particle Flow Animation Loop
  // ---------------------------------------------------------------------------

  _startAnimationLoop() {
    const loop = () => {
      const now = performance.now();
      const dt = Math.min((now - this._lastFrameTime) / 1000, 0.1);
      this._lastFrameTime = now;

      this._updateParticleFlow(dt);
      this._animFrameId = requestAnimationFrame(loop);
    };
    this._animFrameId = requestAnimationFrame(loop);
  }

  _getPointOnPolyline(pts, dist) {
    if (!pts || pts.length < 2) return null;
    let totalLen = 0;
    const segLens = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const len = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
      segLens.push(len);
      totalLen += len;
    }
    if (totalLen <= 0) return { x: pts[0][0], y: pts[0][1], angle: 0, totalLen: 0 };
    const d = ((dist % totalLen) + totalLen) % totalLen;
    let acc = 0;
    for (let i = 0; i < segLens.length; i++) {
      if (acc + segLens[i] >= d || i === segLens.length - 1) {
        const remain = d - acc;
        const t = segLens[i] > 0 ? remain / segLens[i] : 0;
        const x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t;
        const y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t;
        const angle = Math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]);
        return { x, y, angle, totalLen };
      }
      acc += segLens[i];
    }
    return { x: pts[0][0], y: pts[0][1], angle: 0, totalLen };
  }

  _updateParticleFlow(dt) {
    if (!this.layers.flow || !this.runtimeOutput) return;

    this.layers.flow.innerHTML = '';
    const geom = this.runtimeOutput.geometry || {};
    const wires = geom.wires || [];

    // Advance particle offset
    this._particleOffset += dt * 40;

    for (const w of wires) {
      const pts = w.points || [];
      if (pts.length < 2) continue;

      const current = w.current_A || 0;
      if (Math.abs(current) < 1e-5 || w.direction === 'none') {
        continue;
      }

      // Compute polyline metrics
      const pInit = this._getPointOnPolyline(pts, 0);
      const totalLen = pInit?.totalLen || 0;
      if (totalLen < 15) continue;

      const sign = (w.direction === 'backward' || current < 0) ? -1 : 1;
      const speedMultiplier = Math.min(3.5, Math.max(0.6, Math.abs(current) * 1.8));
      const spacing = 28; // spacing between particles
      const offset = (sign * this._particleOffset * speedMultiplier) % spacing;

      // 1. Spaced glowing particle dots along the polyline
      const numParticles = Math.floor(totalLen / spacing);
      for (let i = 0; i <= numParticles; i++) {
        const d = i * spacing + offset;
        const pt = this._getPointOnPolyline(pts, d);
        if (pt) {
          const dot = this._createCircle(pt.x, pt.y, 3.2, {
            fill: '#e0f2fe',
            stroke: '#0284c7',
            strokeWidth: 1.2,
            filter: 'drop-shadow(0 0 2px #38bdf8)'
          });
          this.layers.flow.appendChild(dot);
        }
      }

      // 2. Directional arrow at the midpoint
      const midPt = this._getPointOnPolyline(pts, totalLen / 2);
      if (midPt) {
        const arrowAngle = sign > 0 ? midPt.angle : midPt.angle + Math.PI;
        const arrowLen = 8;
        const arrowWidth = 5;

        const xTip = midPt.x + arrowLen * Math.cos(arrowAngle);
        const yTip = midPt.y + arrowLen * Math.sin(arrowAngle);
        const xBack1 = midPt.x - arrowLen * 0.5 * Math.cos(arrowAngle) + arrowWidth * Math.sin(arrowAngle);
        const yBack1 = midPt.y - arrowLen * 0.5 * Math.sin(arrowAngle) - arrowWidth * Math.cos(arrowAngle);
        const xBack2 = midPt.x - arrowLen * 0.5 * Math.cos(arrowAngle) - arrowWidth * Math.sin(arrowAngle);
        const yBack2 = midPt.y - arrowLen * 0.5 * Math.sin(arrowAngle) + arrowWidth * Math.cos(arrowAngle);

        const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        arrow.setAttribute('points', `${xTip},${yTip} ${xBack1},${yBack1} ${xBack2},${yBack2}`);
        arrow.setAttribute('fill', '#0284c7');
        arrow.setAttribute('stroke', '#ffffff');
        arrow.setAttribute('stroke-width', '0.8');
        this.layers.flow.appendChild(arrow);
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Switch Interaction Handler
  // ---------------------------------------------------------------------------

  _handlePointerDown(e) {
    const hitEl = e.target.closest?.('.if-handle-switch');
    if (!hitEl || !this.runtimeOutput) return;

    e.preventDefault();
    e.stopPropagation();

    const switchId = hitEl.getAttribute('data-target-id');
    const geom = this.runtimeOutput.geometry || {};
    const sw = geom.switches?.find(s => s.id === switchId);
    if (!sw) return;

    const nextClosed = !sw.closed;

    this.onInteract?.({
      targetId: switchId,
      key: 'closed',
      value: nextClosed
    });
  }

  _createCircle(cx, cy, r, attrs = {}) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    el.setAttribute('cx', String(cx));
    el.setAttribute('cy', String(cy));
    el.setAttribute('r', String(r));
    for (const [k, v] of Object.entries(attrs)) {
      if (v != null) el.setAttribute(k.replace(/[A-Z]/g, m => `-${m.toLowerCase()}`), String(v));
    }
    return el;
  }

  _createText(x, y, text, attrs = {}) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    el.setAttribute('x', String(x));
    el.setAttribute('y', String(y));
    el.textContent = text;
    for (const [k, v] of Object.entries(attrs)) {
      if (v != null) el.setAttribute(k.replace(/[A-Z]/g, m => `-${m.toLowerCase()}`), String(v));
    }
    return el;
  }

  dispose() {
    if (this._animFrameId) {
      cancelAnimationFrame(this._animFrameId);
      this._animFrameId = null;
    }
    if (this.container) {
      this.container.removeEventListener('pointerdown', this._boundOnPointerDown);
    }
    if (this.svg) {
      this.svg.remove();
      this.svg = null;
    }
    super.dispose();
  }
}
