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

  _renderWires(geom) {
    const wires = geom.wires || [];
    for (const w of wires) {
      const pts = w.points || [];
      if (pts.length < 2) continue;

      const pathStr = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`).join(' ');

      // Base conductor wire path
      const wirePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      wirePath.setAttribute('d', pathStr);
      wirePath.setAttribute('fill', 'none');
      wirePath.setAttribute('stroke', 'rgba(148, 163, 184, 0.5)');
      wirePath.setAttribute('stroke-width', '3');
      wirePath.setAttribute('stroke-linecap', 'round');
      wirePath.setAttribute('stroke-linejoin', 'round');
      this.layers.wires.appendChild(wirePath);
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
      const cA = this._createCircle(tA[0], tA[1], 4, { fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 1.5 });
      const cB = this._createCircle(tB[0], tB[1], 4, { fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 1.5 });
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
    const components = geom.components || [];

    // Find physical coordinates for each node from terminal coordinates
    const nodeCoords = new Map();
    for (const c of components) {
      if (Array.isArray(c.terminals)) {
        for (const t of c.terminals) {
          if (t.node && t.source_px) {
            if (!nodeCoords.has(t.node)) {
              nodeCoords.set(t.node, t.source_px);
            }
          }
        }
      }
    }

    for (const [nodeId, voltage] of Object.entries(nodeVoltages)) {
      const coord = nodeCoords.get(nodeId);
      if (!coord) continue;

      const [x, y] = coord;
      const vText = `${nodeId}: ${Number(voltage.toFixed(2))}V`;

      // Badge group
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      const width = 64;
      const height = 18;
      rect.setAttribute('x', String(x - width / 2));
      rect.setAttribute('y', String(y - height / 2 - 16));
      rect.setAttribute('width', String(width));
      rect.setAttribute('height', String(height));
      rect.setAttribute('rx', '4');
      rect.setAttribute('fill', 'rgba(15, 23, 42, 0.85)');
      rect.setAttribute('stroke', '#38bdf8');
      rect.setAttribute('stroke-width', '1');

      const text = this._createText(x, y - 16 + 4, vText, {
        fill: '#38bdf8',
        fontSize: 10,
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

      const center = c.center_source_px;
      if (!center) continue;

      const [cx, cy] = center;
      const cur = c.current_A != null ? Math.abs(c.current_A) : null;
      let curText = '';
      if (cur != null && cur > 0) {
        curText = cur >= 1.0 ? `${cur.toFixed(2)}A` : `${(cur * 1000).toFixed(0)}mA`;
      }

      if (curText) {
        const text = this._createText(cx, cy + 24, `${c.label || c.id} • ${curText}`, {
          fill: '#f59e0b',
          fontSize: 10.5,
          fontWeight: 'bold',
          textAnchor: 'middle'
        });
        this.layers.components.appendChild(text);
      }
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

  _updateParticleFlow(dt) {
    if (!this.layers.flow || !this.runtimeOutput) return;

    this.layers.flow.innerHTML = '';
    const geom = this.runtimeOutput.geometry || {};
    const wires = geom.wires || [];

    // Advance particle phase
    this._particleOffset += dt * 45; // base speed

    for (const w of wires) {
      const pts = w.points || [];
      if (pts.length < 2) continue;

      const current = w.current_A || 0;
      if (Math.abs(current) < 1e-5 || w.direction === 'none') {
        // No current flow on this branch (e.g. open circuit or unmapped branch)
        continue;
      }

      const pathStr = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`).join(' ');
      const flowPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      flowPath.setAttribute('d', pathStr);
      flowPath.setAttribute('fill', 'none');
      flowPath.setAttribute('stroke', '#38bdf8');
      flowPath.setAttribute('stroke-width', '2.5');
      flowPath.setAttribute('stroke-dasharray', '8 16');

      // Dash offset direction depends on wire direction and signed current
      const sign = (w.direction === 'backward' || current < 0) ? 1 : -1;
      const speedMultiplier = Math.min(3, Math.max(0.4, Math.abs(current) * 2));
      const offset = (sign * this._particleOffset * speedMultiplier) % 24;
      flowPath.setAttribute('stroke-dashoffset', String(offset));
      flowPath.setAttribute('opacity', '0.85');

      this.layers.flow.appendChild(flowPath);
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
