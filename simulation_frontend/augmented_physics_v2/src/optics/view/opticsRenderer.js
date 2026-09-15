/** optics/view/opticsRenderer.js
 * Shared scientific rendering primitives for p5.js canvas.
 * Used across Thin Lens, Prism, and Mirror views.
 */
import { THEME } from './opticsTheme.js';

export class OpticsRenderer {
  constructor(p) {
    this.p = p;
  }

  /**
   * Draws an optical ray with neon glow and directional arrowhead.
   */
  drawRay(start, end, color = THEME.rays[0], weight = 1.8) {
    const p = this.p;
    const ctx = p.drawingContext;
    p.push();
    ctx.setLineDash([]);
    ctx.shadowBlur = 8;
    ctx.shadowColor = color;
    p.stroke(color);
    p.strokeWeight(weight);
    p.line(start.x, start.y, end.x, end.y);
    ctx.shadowBlur = 0;
    p.pop();
  }

  /**
   * Draws an optical ray with a directional arrowhead at the midpoint.
   */
  drawRayWithArrow(start, end, color = THEME.rays[0], weight = 2.2) {
    this.drawRay(start, end, color, weight);
    const p = this.p;
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    const angle = Math.atan2(end.y - start.y, end.x - start.x);
    p.push();
    p.translate(midX, midY);
    p.rotate(angle);
    p.fill(color);
    p.noStroke();
    p.triangle(7, 0, -7, -5, -7, 5);
    p.pop();
  }

  /**
   * Draws a dashed virtual ray extension without glow.
   */
  drawDashedRay(start, end, color = THEME.rays[0], dash = [8, 5]) {
    const p = this.p;
    const ctx = p.drawingContext;
    p.push();
    ctx.setLineDash(dash);
    p.stroke(this._colAlpha(color, THEME.virtual.alpha));
    p.strokeWeight(1.2);
    ctx.shadowBlur = 0;
    p.line(start.x, start.y, end.x, end.y);
    ctx.setLineDash([]);
    p.pop();
  }

  /**
   * Draws an arrow (solid or dashed) along the vertical direction.
   */
  drawArrow(x, ay, h, theme = THEME.object, solid = true) {
    const p = this.p;
    const tipY = ay + h;
    const ctx = p.drawingContext;
    p.push();
    if (solid) {
      ctx.setLineDash([]);
      ctx.shadowBlur = theme.glowBlur || 8;
      ctx.shadowColor = theme.glow || theme.stroke;
    } else {
      ctx.setLineDash(theme.dash || THEME.virtual.dash);
      ctx.shadowBlur = 0;
    }
    p.stroke(theme.stroke);
    p.strokeWeight(theme.weight || 2);
    p.line(x, ay, x, tipY);

    const dir = h < 0 ? -1 : 1;
    p.fill(theme.fill || theme.stroke);
    p.noStroke();
    p.triangle(x, tipY, x - 6, tipY + dir * 12, x + 6, tipY + dir * 12);
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;
    p.pop();
  }

  /**
   * Draws the horizontal optical axis across canvas.
   */
  drawOpticalAxis(y, width = 800) {
    const p = this.p;
    const ctx = p.drawingContext;
    ctx.setLineDash(THEME.axis.dash);
    p.push();
    p.stroke(THEME.axis.stroke);
    p.strokeWeight(THEME.axis.weight);
    p.line(0, y, width, y);
    p.pop();
    ctx.setLineDash([]);
  }

  /**
   * Draws a labeled focal or geometric point (e.g. F, 2F, C, P).
   */
  drawFocalPoint(x, y, label) {
    const p = this.p;
    p.push();
    p.fill(THEME.focal.fill);
    p.noStroke();
    p.circle(x, y, THEME.focal.radius * 2);
    p.fill(THEME.focalLabel.fill);
    p.textSize(THEME.focalLabel.size);
    p.textAlign(p.CENTER, p.BOTTOM);
    p.text(label, x, y - 8);
    p.pop();
  }

  /**
   * Draws a dashed surface normal at an optical boundary.
   */
  drawNormal(p1, p2) {
    const p = this.p;
    const ctx = p.drawingContext;
    ctx.setLineDash(THEME.normal.dash);
    p.push();
    p.stroke(THEME.normal.stroke);
    p.strokeWeight(THEME.normal.weight);
    p.line(p1.x, p1.y, p2.x, p2.y);
    p.pop();
    ctx.setLineDash([]);
  }

  /**
   * Draws an educational angle arc with label (e.g. i1, r1, delta).
   */
  drawAngleArc(center, radius, startAngle, endAngle, label = '') {
    const p = this.p;
    p.push();
    p.noFill();
    p.stroke(THEME.angleArc.stroke);
    p.strokeWeight(THEME.angleArc.weight);
    p.arc(center.x, center.y, radius * 2, radius * 2, startAngle, endAngle);

    if (label) {
      const midAngle = (startAngle + endAngle) / 2;
      const dist = radius + 20;
      const lx = center.x + Math.cos(midAngle) * dist;
      const ly = center.y + Math.sin(midAngle) * dist;
      p.push();
      p.textSize(12);
      p.textAlign(p.CENTER, p.CENTER);
      const tw = p.textWidth(label) + 12;
      const th = 18;
      // High-contrast badge so angle labels are always crystal clear and never obscured by rays
      p.fill('rgba(15, 23, 42, 0.90)');
      p.stroke('rgba(251, 191, 36, 0.7)');
      p.strokeWeight(1);
      p.rect(lx - tw / 2, ly - th / 2, tw, th, 4);
      p.noStroke();
      p.fill('#fbbf24');
      p.text(label, lx, ly);
      p.pop();
    }
    p.pop();
  }

  /**
   * Draws an angle arc between two 2D unit vectors v1 and v2 radiating from center.
   */
  drawAngleBetweenVectors(center, v1, v2, radius = 28, label = '') {
    const a1 = Math.atan2(v1.y, v1.x);
    const a2 = Math.atan2(v2.y, v2.x);
    let diff = a2 - a1;
    while (diff <= -Math.PI) diff += 2 * Math.PI;
    while (diff > Math.PI) diff -= 2 * Math.PI;

    let start = a1;
    let end = a1 + diff;
    if (diff < 0) {
      start = a1 + diff;
      end = a1;
    }
    this.drawAngleArc(center, radius, start, end, label);
  }

  /**
   * Draws a small debug coordinate / label tag.
   */
  drawDebugTag(x, y, text) {
    const p = this.p;
    p.push();
    p.textSize(10);
    const tw = p.textWidth(text);
    p.fill('rgba(15, 23, 42, 0.85)');
    p.stroke('rgba(96, 165, 250, 0.4)');
    p.strokeWeight(1);
    p.rect(x - tw / 2 - 4, y - 16, tw + 8, 14, 3);
    p.fill('#93c5fd');
    p.noStroke();
    p.textAlign(p.CENTER, p.CENTER);
    p.text(text, x, y - 9);
    p.pop();
  }

  /**
   * Draws a thin convex lens symbol.
   */
  drawConvexLens(x, ay, h = 220) {
    const p = this.p;
    const half = h / 2, ah = 10;
    const ctx = p.drawingContext;
    ctx.shadowBlur = 14;
    ctx.shadowColor = THEME.lens.glow;
    p.push();
    p.stroke(THEME.lens.stroke);
    p.strokeWeight(THEME.lens.weight);
    p.noFill();
    p.line(x, ay - half, x, ay + half);
    // Double arrow heads representing converging lens
    p.line(x, ay - half, x - ah, ay - half + ah);
    p.line(x, ay - half, x + ah, ay - half + ah);
    p.line(x, ay + half, x - ah, ay + half - ah);
    p.line(x, ay + half, x + ah, ay + half - ah);
    p.pop();
    ctx.shadowBlur = 0;
  }

  /**
   * Draws a thin concave (diverging) lens symbol with inward-pointing arrowheads.
   */
  drawConcaveLens(x, ay, h = 220) {
    const p = this.p;
    const half = h / 2, ah = 10;
    const ctx = p.drawingContext;
    ctx.shadowBlur = 14;
    ctx.shadowColor = THEME.lens.glow;
    p.push();
    p.stroke(THEME.lens.stroke);
    p.strokeWeight(THEME.lens.weight);
    p.noFill();
    p.line(x, ay - half, x, ay + half);
    // Inward pointing arrow heads representing diverging lens
    p.line(x, ay - half, x - ah, ay - half - ah);
    p.line(x, ay - half, x + ah, ay - half - ah);
    p.line(x, ay + half, x - ah, ay + half + ah);
    p.line(x, ay + half, x + ah, ay + half + ah);
    p.pop();
    ctx.shadowBlur = 0;
  }

  /**
   * Draws a spherical or plane mirror.
   */
  drawMirror(mx, ay, radius = 280, height = 240, type = 'concave') {
    const p = this.p;
    const ctx = p.drawingContext;
    p.push();
    ctx.shadowBlur = 12;
    ctx.shadowColor = THEME.mirror.glow;
    p.stroke(THEME.mirror.stroke);
    p.strokeWeight(THEME.mirror.weight);
    p.noFill();

    const isConcave = type === 'concave';

    if (type === 'plane') {
      p.line(mx, ay - height / 2, mx, ay + height / 2);
      // Back-silvering hatching marks
      p.stroke('rgba(255,255,255,0.3)');
      p.strokeWeight(1);
      const step = 14;
      for (let y = ay - height / 2; y <= ay + height / 2; y += step) {
        p.line(mx, y, mx + 8, y - 6);
      }
    } else {
      // Curved arc for concave or convex
      const safeRadius = Math.max(height / 2 + 1, Number(radius) || 280);
      const angleSpan = Math.asin(Math.min(0.99, (height / 2) / safeRadius));
      const cx = isConcave ? mx - safeRadius : mx + safeRadius;
      const start = isConcave ? -angleSpan : Math.PI - angleSpan;
      const end = isConcave ? angleSpan : Math.PI + angleSpan;
      p.arc(cx, ay, safeRadius * 2, safeRadius * 2, start, end);

      // Back-silvering hatching marks on mirror rear
      p.stroke('rgba(255,255,255,0.25)');
      p.strokeWeight(1);
      const numHatches = 12;
      for (let i = 0; i <= numHatches; i++) {
        const a = start + (end - start) * (i / numHatches);
        const px = cx + safeRadius * Math.cos(a);
        const py = ay + safeRadius * Math.sin(a);
        const hLen = 8;
        const hDir = isConcave ? 1 : -1;
        p.line(px, py, px + hDir * hLen * Math.cos(a + 0.4), py + hDir * hLen * Math.sin(a + 0.4));
      }
    }

    ctx.shadowBlur = 0;
    p.pop();
  }

  /**
   * Draws a polygonal prism with glass tint and subtle boundary glow.
   */
  drawPrism(vertices) {
    const p = this.p;
    const ctx = p.drawingContext;
    p.push();
    ctx.shadowBlur = 10;
    ctx.shadowColor = THEME.prism.glow;
    p.stroke(THEME.prism.stroke);
    p.strokeWeight(THEME.prism.weight);
    p.fill(THEME.prism.fill);

    p.beginShape();
    vertices.forEach(v => p.vertex(v.x, v.y));
    p.endShape(p.CLOSE);

    ctx.shadowBlur = 0;
    p.pop();
  }

  /**
   * Draws an interactive circular drag hint.
   */
  drawDragHint(x, y, radius = 25, label = 'drag') {
    const p = this.p;
    p.push();
    p.noFill();
    p.stroke('rgba(255,255,255,0.4)');
    p.strokeWeight(1);
    p.circle(x, y, radius * 2);
    p.fill('rgba(255,255,255,0.8)');
    p.noStroke();
    p.textAlign(p.CENTER, p.CENTER);
    p.textSize(11);
    p.text(label, x, y - radius - 8);
    p.pop();
  }

  _colAlpha(hex, a) {
    const p = this.p;
    return p.color(
      parseInt(hex.slice(1, 3), 16),
      parseInt(hex.slice(3, 5), 16),
      parseInt(hex.slice(5, 7), 16),
      Math.round(a * 255)
    );
  }
}
