/** optics/view/p5OpticsView.js
 * Unified p5.js instance-mode transparent canvas renderer.
 * Delegates visual primitives to OpticsRenderer and handles interactive 2D dragging.
 */
import p5 from 'p5';
import { THEME } from './opticsTheme.js';
import { OpticsRenderer } from './opticsRenderer.js';
import { opticsSprites } from './opticsSprites.js';

const CW = 800, CH = 600, DRAG_R = 25;

export class P5OpticsView {
  constructor(container, callbacks = {}) {
    this.onDragLens = callbacks.onDragLens || (() => {});
    this.onDragPrism = callbacks.onDragPrism || (() => {});
    this.onDragMirror = callbacks.onDragMirror || (() => {});
    this.onDragInterface = callbacks.onDragInterface || (() => {});

    this._state = null;
    this._model = null;
    this._dragTarget = null; // 'object_pos' | 'object_tip' | 'light_source'
    this._showDebug = false;

    this._p5 = new p5(p => {
      this.renderer = new OpticsRenderer(p);

      p.setup = () => {
        const cv = p.createCanvas(CW, CH);
        cv.parent(container);
        cv.style('background', 'transparent');
        p.noLoop();
        p.clear();
      };

      p.draw = () => {
        p.clear();
        if (!this._state || !this._model) return;
        this._renderCurrentScene(p);
      };

      p.mousePressed = () => {
        if (!this._model) return;
        const sub = this._model.subtype || 'thin_lens';

        if (sub === 'prism') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
            this._dragTarget = 'light_source';
            p.cursor('grabbing');
          }
          return;
        }

        if (sub === 'interface_refraction') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
            this._dragTarget = 'interface_source';
            p.cursor('grabbing');
          }
          return;
        }

        // For thin_lens or mirror: object arrow interaction
        const obj = this._model.object;
        if (!obj) return;
        const tipY = this._model.axisY + obj.height;
        const minY = Math.min(this._model.axisY, tipY);
        const maxY = Math.max(this._model.axisY, tipY);

        const nearTip = Math.hypot(p.mouseX - obj.x, p.mouseY - tipY) < DRAG_R;
        const nearShaft = Math.abs(p.mouseX - obj.x) < 22 && p.mouseY >= minY - 10 && p.mouseY <= maxY + 10;

        if (nearTip) {
          this._dragTarget = 'object_tip';
          p.cursor('grabbing');
        } else if (nearShaft) {
          this._dragTarget = 'object_pos';
          p.cursor('grabbing');
        }
      };

      p.mouseMoved = () => {
        if (!this._model || this._dragTarget) return;
        const sub = this._model.subtype || 'thin_lens';

        if (sub === 'prism') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
            p.cursor('grab');
          } else {
            p.cursor('default');
          }
          return;
        }

        if (sub === 'interface_refraction') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
            p.cursor('grab');
          } else {
            p.cursor('default');
          }
          return;
        }

        const obj = this._model.object;
        if (!obj) return;
        const tipY = this._model.axisY + obj.height;
        const minY = Math.min(this._model.axisY, tipY);
        const maxY = Math.max(this._model.axisY, tipY);
        const nearTip = Math.hypot(p.mouseX - obj.x, p.mouseY - tipY) < DRAG_R;
        const nearShaft = Math.abs(p.mouseX - obj.x) < 22 && p.mouseY >= minY - 10 && p.mouseY <= maxY + 10;

        if (nearTip) {
          p.cursor('ns-resize');
        } else if (nearShaft) {
          p.cursor('grab');
        } else {
          p.cursor('default');
        }
      };

      p.mouseDragged = () => {
        if (!this._dragTarget || !this._model) return;
        const sub = this._model.subtype || 'thin_lens';

        if (sub === 'prism') {
          if (this._dragTarget === 'light_source') {
            const newX = p.constrain(p.mouseX, 20, 240);
            const newY = p.constrain(p.mouseY, 150, 480);
            this.onDragPrism(newX, newY);
          }
          return;
        }

        if (sub === 'interface_refraction') {
          if (this._dragTarget === 'interface_source') {
            const boundY = this._model.boundary?.y ?? 300;
            const newX = p.constrain(p.mouseX, 20, CW - 20);
            const newY = p.constrain(p.mouseY, 20, boundY - 10);
            this.onDragInterface(newX, newY);
          }
          return;
        }

        const obj = this._model.object;
        if (!obj) return;
        const maxX = (sub === 'mirror' ? this._model.mirror.x : this._model.lens.x) - 10;

        if (this._dragTarget === 'object_tip') {
          // Adjust height vertically and position horizontally
          const newX = p.constrain(p.mouseX, 20, maxX);
          const rawHeight = p.mouseY - this._model.axisY;
          // Constrain height between -160 (tall upright) and -30 (short)
          const newH = p.constrain(rawHeight, -160, -30);
          if (sub === 'mirror') this.onDragMirror(newX, newH);
          else this.onDragLens(newX, newH);
        } else if (this._dragTarget === 'object_pos') {
          // Adjust position horizontally
          const newX = p.constrain(p.mouseX, 20, maxX);
          if (sub === 'mirror') this.onDragMirror(newX, obj.height);
          else this.onDragLens(newX, obj.height);
        }
      };

      p.mouseReleased = () => {
        this._dragTarget = null;
        p.cursor('default');
      };
    });
  }

  render(model, result) {
    this._model = model;
    this._state = result;
    this._p5.redraw();
  }

  setDebug(enable) {
    this._showDebug = enable;
    this._p5.redraw();
  }

  destroy() {
    this._p5.remove();
  }

  _renderCurrentScene(p) {
    const sub = this._model.subtype || 'thin_lens';
    if (sub === 'prism') {
      this._drawPrismScene(p);
    } else if (sub === 'mirror') {
      this._drawMirrorScene(p);
    } else if (sub === 'interface_refraction') {
      this._drawInterfaceRefractionScene(p);
    } else {
      this._drawThinLensScene(p);
    }
  }

  _drawThinLensScene(p) {
    const { _state: r, _model: m } = this;
    const ren = this.renderer;

    ren.drawOpticalAxis(m.axisY, CW);

    (m.focalPoints || []).forEach(fp => {
      ren.drawFocalPoint(fp.x, m.axisY, fp.label);
    });

    const isConcave = m.lens.focalLength < 0 || m.lens.model === 'concave';
    if (isConcave) {
      ren.drawConcaveLens(m.lens.x, m.axisY, m.lens.apertureHeight || THEME.lens.apertureH);
    } else {
      ren.drawConvexLens(m.lens.x, m.axisY, m.lens.apertureHeight || THEME.lens.apertureH);
    }

    // Draw principal rays
    (r.rays || []).forEach((ray, i) => {
      const col = THEME.rays[Math.min(i, THEME.rays.length - 1)];
      for (let j = 0; j < ray.points.length - 1; j++) {
        const pt1 = ray.points[j];
        const pt2 = ray.points[j + 1];
        if (ray.dashed) ren.drawDashedRay(pt1, pt2, col);
        else ren.drawRay(pt1, pt2, col);
      }
    });

    const spriteImg = m.object.spriteUrl ? opticsSprites.get(p, m.object.spriteUrl) : null;

    // Draw formed image (sprite or neon arrow)
    if (isFinite(r.imageX) && isFinite(r.imageHeight)) {
      let drew = false;
      if (spriteImg) {
        drew = opticsSprites.drawImage(p, spriteImg, r.imageX, m.axisY, m.object.height, r.magnification, r.isReal);
      }
      if (!drew) {
        ren.drawArrow(r.imageX, m.axisY, r.imageHeight, r.isReal ? THEME.imageReal : THEME.imageVirtual, r.isReal);
      }
    }

    // Draw original object (sprite or neon arrow)
    let drewObj = false;
    if (spriteImg) {
      drewObj = opticsSprites.drawObject(p, spriteImg, m.object.x, m.axisY, m.object.height);
    }
    if (!drewObj) {
      ren.drawArrow(m.object.x, m.axisY, m.object.height, THEME.object, true);
    }

    const tipY = m.axisY + m.object.height;
    if (!this._dragTarget && Math.abs(p.mouseX - m.object.x) < 25) {
      ren.drawDragHint(m.object.x, tipY, 20, 'drag');
    }

    if (this._showDebug) {
      ren.drawDebugTag(m.object.x, tipY - 8, `Obj (${Math.round(m.object.x)}, ${Math.round(tipY)})`);
      ren.drawDebugTag(m.lens.x, m.axisY + 22, `O (${Math.round(m.lens.x)}, ${Math.round(m.axisY)})`);
      if (isFinite(r.imageX) && isFinite(r.imageHeight)) {
        ren.drawDebugTag(r.imageX, m.axisY + r.imageHeight - 8, `Img (${Math.round(r.imageX)}, ${Math.round(m.axisY + r.imageHeight)})`);
      }
      (m.focalPoints || []).forEach(fp => {
        ren.drawDebugTag(fp.x, m.axisY + 22, `${fp.label} (${Math.round(fp.x)})`);
      });
    }
  }

  _drawPrismScene(p) {
    const { _state: r, _model: m } = this;
    const ren = this.renderer;

    // Draw prism glass polygon
    ren.drawPrism(m.prism.vertices);

    // Draw surface normals
    (r.normals || []).forEach(norm => {
      ren.drawNormal(norm.p1, norm.p2);
    });

    // Draw educational angle arcs at face 1 (i1 and r1)
    if (r.hit1 && r.N1 && r.I0) {
      const vSource = { x: -r.I0.x, y: -r.I0.y };
      const lblI1 = r.angles?.i1Deg != null ? `i₁ ${Math.round(r.angles.i1Deg)}°` : 'i₁';
      ren.drawAngleBetweenVectors(r.hit1, vSource, r.N1, 30, lblI1);

      if (r.I_internal) {
        const vNormIn = { x: -r.N1.x, y: -r.N1.y };
        const lblR1 = r.angles?.r1Deg != null ? `r₁ ${Math.round(r.angles.r1Deg)}°` : 'r₁';
        ren.drawAngleBetweenVectors(r.hit1, r.I_internal, vNormIn, 22, lblR1);
      }
    }

    // Draw refracted/emergent light rays
    (r.segments || []).forEach((seg, i) => {
      let col = THEME.rays[0];
      if (seg.type === 'internal') col = THEME.rays[1];
      if (seg.type === 'emergent') col = THEME.rays[2];
      if (seg.type === 'tir_reflected') col = '#f87171'; // Warning red for TIR
      ren.drawRay(seg.start, seg.end, col, 2.2);
    });

    // Draw interactive light source beam emitter
    const ls = m.lightSource;
    if (ls) {
      p.push();
      p.fill('#facc15');
      p.stroke('#eab308');
      p.strokeWeight(2);
      p.circle(ls.x, ls.y, 14);
      p.fill('#ffffff');
      p.noStroke();
      p.textSize(11);
      p.textAlign(p.CENTER, p.BOTTOM);
      p.text('Beam Source', ls.x, ls.y - 12);
      p.pop();

      if (!this._dragTarget && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
        ren.drawDragHint(ls.x, ls.y, 18, 'drag');
      }
    }

    if (this._showDebug) {
      m.prism.vertices.forEach((v, idx) => {
        ren.drawDebugTag(v.x, v.y - 6, `V${idx + 1} (${Math.round(v.x)}, ${Math.round(v.y)})`);
      });
      if (r.hit1) ren.drawDebugTag(r.hit1.x, r.hit1.y + 16, `Hit1 (${Math.round(r.hit1.x)}, ${Math.round(r.hit1.y)})`);
      if (r.hit2) ren.drawDebugTag(r.hit2.x, r.hit2.y + 16, `Hit2 (${Math.round(r.hit2.x)}, ${Math.round(r.hit2.y)})`);
      if (ls) ren.drawDebugTag(ls.x, ls.y + 16, `Src (${Math.round(ls.x)}, ${Math.round(ls.y)})`);
    }
  }

  _drawMirrorScene(p) {
    const { _state: r, _model: m } = this;
    const ren = this.renderer;

    ren.drawOpticalAxis(m.axisY, CW);

    (m.focalPoints || []).forEach(fp => {
      ren.drawFocalPoint(fp.x, m.axisY, fp.label);
    });

    ren.drawMirror(m.mirror.x, m.axisY, 280, 240, m.mirror.model);

    // Draw mirror principal rays
    (r.rays || []).forEach((ray, i) => {
      const col = THEME.rays[Math.min(i, THEME.rays.length - 1)];
      for (let j = 0; j < ray.points.length - 1; j++) {
        const pt1 = ray.points[j];
        const pt2 = ray.points[j + 1];
        if (ray.dashed) ren.drawDashedRay(pt1, pt2, col);
        else ren.drawRay(pt1, pt2, col);
      }
    });

    const spriteImg = m.object.spriteUrl ? opticsSprites.get(p, m.object.spriteUrl) : null;

    // Draw formed image
    if (isFinite(r.imageX) && isFinite(r.imageHeight)) {
      let drew = false;
      if (spriteImg) {
        drew = opticsSprites.drawImage(p, spriteImg, r.imageX, m.axisY, m.object.height, r.magnification, r.isReal);
      }
      if (!drew) {
        ren.drawArrow(r.imageX, m.axisY, r.imageHeight, r.isReal ? THEME.imageReal : THEME.imageVirtual, r.isReal);
      }
    }

    // Draw original object
    let drewObj = false;
    if (spriteImg) {
      drewObj = opticsSprites.drawObject(p, spriteImg, m.object.x, m.axisY, m.object.height);
    }
    if (!drewObj) {
      ren.drawArrow(m.object.x, m.axisY, m.object.height, THEME.object, true);
    }

    const tipY = m.axisY + m.object.height;
    if (!this._dragTarget && Math.abs(p.mouseX - m.object.x) < 25) {
      ren.drawDragHint(m.object.x, tipY, 20, 'drag');
    }

    if (this._showDebug) {
      ren.drawDebugTag(m.object.x, tipY - 8, `Obj (${Math.round(m.object.x)}, ${Math.round(tipY)})`);
      ren.drawDebugTag(m.mirror.x, m.axisY + 22, `P (${Math.round(m.mirror.x)}, ${Math.round(m.axisY)})`);
      if (isFinite(r.imageX) && isFinite(r.imageHeight)) {
        ren.drawDebugTag(r.imageX, m.axisY + r.imageHeight - 8, `Img (${Math.round(r.imageX)}, ${Math.round(m.axisY + r.imageHeight)})`);
      }
      (m.focalPoints || []).forEach(fp => {
        ren.drawDebugTag(fp.x, m.axisY + 22, `${fp.label} (${Math.round(fp.x)})`);
      });
    }
  }

  _drawInterfaceRefractionScene(p) {
    const { _state: r, _model: m } = this;
    const ren = this.renderer;

    const bY = m.boundary?.y ?? 300;
    const nX = m.normal?.x ?? 400;

    // 1. Subtle medium background fills / tints (upper rarer, lower denser)
    p.push();
    p.noStroke();
    // Medium 1 (top)
    p.fill(30, 41, 59, 120); // subtle slate
    p.rect(0, 0, CW, bY);
    // Medium 2 (bottom)
    p.fill(14, 116, 144, 90); // subtle cyan/water tint
    p.rect(0, bY, CW, CH - bY);

    // Medium labels
    p.fill('#94a3b8');
    p.textSize(13);
    p.textAlign(p.LEFT, p.TOP);
    const m1Name = m.medium1?.name || 'Medium 1';
    const m1N = m.medium1?.n != null ? Number(m.medium1.n).toFixed(2) : '1.00';
    p.text(`${m1Name} (n₁ = ${m1N})`, 25, 20);

    p.fill('#67e8f9');
    p.textAlign(p.LEFT, p.BOTTOM);
    const m2Name = m.medium2?.name || 'Medium 2';
    const m2N = m.medium2?.n != null ? Number(m.medium2.n).toFixed(2) : '1.50';
    p.text(`${m2Name} (n₂ = ${m2N})`, 25, CH - 20);
    p.pop();

    // 2. Boundary interface line
    p.push();
    p.stroke('#38bdf8');
    p.strokeWeight(2.5);
    p.line(0, bY, CW, bY);
    p.pop();

    // 3. Normal line (vertical dashed line across boundary)
    if (r.normalLine) {
      ren.drawNormal(r.normalLine.top, r.normalLine.bottom);
      p.push();
      p.fill('rgba(255,255,255,0.7)');
      p.noStroke();
      p.textSize(11);
      p.textAlign(p.CENTER, p.BOTTOM);
      p.text("Normal N-N'", nX, r.normalLine.top.y - 4);
      p.pop();
    }

    // 4. Draw Angle arcs at point of incidence
    const poi = { x: nX, y: bY };
    if (r.incidentRay) {
      const vInc = { x: r.incidentRay.start.x - poi.x, y: r.incidentRay.start.y - poi.y };
      const vNormTop = { x: 0, y: -1 };
      const lbl1 = r.angles?.theta1Deg != null ? `θ₁ ${Math.round(r.angles.theta1Deg)}°` : 'θ₁';
      ren.drawAngleBetweenVectors(poi, vInc, vNormTop, 36, lbl1);
    }

    if (r.refractedRay) {
      const vRefr = { x: r.refractedRay.end.x - poi.x, y: r.refractedRay.end.y - poi.y };
      const vNormBot = { x: 0, y: 1 };
      const lbl2 = r.angles?.theta2Deg != null ? `θ₂ ${Math.round(r.angles.theta2Deg)}°` : 'θ₂';
      ren.drawAngleBetweenVectors(poi, vRefr, vNormBot, 36, lbl2);
    }

    // 5. Draw Light Rays with glowing neon colors
    // Incident Ray (Bright Yellow / Amber)
    if (r.incidentRay) {
      ren.drawRay(r.incidentRay.start, r.incidentRay.end, '#facc15', 2.8);
    }

    // Refracted Ray (Cyan)
    if (r.refractedRay) {
      ren.drawRay(r.refractedRay.start, r.refractedRay.end, '#38bdf8', 2.8);
    }

    // Reflected Ray (Pink / Red)
    if (r.reflectedRay) {
      const col = r.isTIR ? '#f87171' : 'rgba(244, 114, 182, 0.6)';
      const weight = r.isTIR ? 2.8 : 1.5;
      ren.drawRay(r.reflectedRay.start, r.reflectedRay.end, col, weight);
    }

    // 6. Interactive Light Source emitter
    const ls = m.lightSource;
    if (ls) {
      p.push();
      p.fill('#facc15');
      p.stroke('#eab308');
      p.strokeWeight(2);
      p.circle(ls.x, ls.y, 16);
      p.fill('#ffffff');
      p.noStroke();
      p.textSize(11);
      p.textAlign(p.CENTER, p.BOTTOM);
      p.text('Ray Source (Drag)', ls.x, ls.y - 12);
      p.pop();

      if (!this._dragTarget && Math.hypot(p.mouseX - ls.x, p.mouseY - ls.y) < DRAG_R * 1.5) {
        ren.drawDragHint(ls.x, ls.y, 20, 'drag');
      }
    }

    // 7. Debug tags
    if (this._showDebug) {
      ren.drawDebugTag(nX, bY, `POI (${Math.round(nX)}, ${Math.round(bY)})`);
      if (ls) ren.drawDebugTag(ls.x, ls.y + 16, `Source (${Math.round(ls.x)}, ${Math.round(ls.y)})`);
    }
  }
}

