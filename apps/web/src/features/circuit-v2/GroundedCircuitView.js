import { FigureViewport } from '../../components/FigureViewport.js';
import { CircuitRenderer } from '../simulations/circuits/CircuitRenderer.js';
import { analysisOutput } from './analysisOutput.js';

// Reuse the source registration and conductor animation implementations. Keep
// printed symbols/labels visible; this lab supplies authoritative backend flow.
class GroundedRenderer extends CircuitRenderer {
  _renderWires(geometry) {
    for (const wire of geometry.wires) {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.dataset.wireId = wire.id;
      path.dataset.currentA = wire.current_A ?? '';
      path.dataset.direction = wire.direction;
      path.dataset.fault = String(wire.fault);
      path.setAttribute('d', wire.points.map((p,i) => `${i ? 'L' : 'M'} ${p[0]} ${p[1]}`).join(' '));
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', wire.fault ? '#f59e0b' : wire.shortRoute ? '#f97316' : '#0891b2');
      path.setAttribute('stroke-width', String((wire.uncertainty_px || 1) * (wire.fault ? 2 : 1)));
      path.setAttribute('stroke-opacity', wire.fault ? '.8' : '.4');
      this.layers.wires.append(path);
    }
  }
  _renderComponents(geometry) {
    for (const c of geometry.components) {
      const box = c.geometry?.bbox_source_px;
      if (box) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.dataset.componentId = c.id;
        rect.dataset.orientation = c.geometry.orientation;
        for (const [key,value] of Object.entries({x:box[0],y:box[1],width:box[2]-box[0],height:box[3]-box[1],
          fill:'none',stroke:'#0d9488','stroke-width':1,'stroke-dasharray':'4 3'})) rect.setAttribute(key,String(value));
        this.layers.components.append(rect);
      }
      for (const t of c.terminals || []) {
        const dot = this._createCircle(...t.source_px, 1.5, {fill:'#0d9488'});
        dot.dataset.terminalId = t.id;
        this.layers.components.append(dot);
      }
    }
  }
  _renderSwitches() {} // Preserve the printed, measured switch arm.
  _renderNodeBadges() {} // Numerical values live in the adjacent telemetry table.
}

export class GroundedCircuitView {
  constructor(host, response) {
    const source = response.source_asset;
    this.viewport = new FigureViewport(host, {sourceWidth:source.width_px, sourceHeight:source.height_px,
      imageUrl:response.image_url});
    this.renderer = new GroundedRenderer();
    this.renderer.mount({container:this.viewport.getOverlayContainer(), coordinateMapper:this.viewport.mapper,
      scene:response.scene, sourceImage:response.image_url});
    this.unsubscribe = this.viewport.onLayoutChange(() => this.renderer.resize(this.viewport.mapper));
    this.playing = true;
  }
  show(analysis) { this.output = analysisOutput(analysis); this.render(); }
  render() {
    if (!this.output) return;
    const output = structuredClone(this.output);
    if (!this.playing) for (const w of output.geometry.wires) w.direction = 'none';
    this.renderer.render(output);
    this.renderer.layers.flow.replaceChildren();
  }
  toggle() { this.playing = !this.playing; this.render(); return this.playing; }
  destroy() { this.unsubscribe(); this.renderer.dispose(); this.viewport.destroy(); }
}
