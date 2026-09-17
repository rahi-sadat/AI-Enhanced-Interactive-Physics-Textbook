/** optics/view/p5OpticsView.js
 * Unified p5.js instance-mode transparent canvas renderer.
 * Operates authoritatively in native source-image coordinates via CoordinateMapper
 * and provides responsive scaling, dragging, and precision debug overlays.
 */
import p5 from 'p5';
import { THEME } from './opticsTheme.js';
import { OpticsRenderer } from './opticsRenderer.js';
import { CoordinateMapper } from '@engine/core/coordinateMapper.js';

const DRAG_R = 25;

export class P5OpticsView {
  constructor(container, callbacks = {}) {
    this.container = container;
    this.onDragLens = callbacks.onDragLens || (() => {});
    this.onDragPrism = callbacks.onDragPrism || (() => {});
    this.onDragMirror = callbacks.onDragMirror || (() => {});
    this.onDragInterface = callbacks.onDragInterface || (() => {});

    this._state = null;
    this._model = null;
    this._dragTarget = null; // 'object_pos' | 'object_tip' | 'light_source' | 'interface_source'
    this._showDebug = false;

    const initialW = container?.clientWidth || 800;
    const initialH = container?.clientHeight || 600;
    this.mapper = new CoordinateMapper(800, 600, initialW, initialH);

    this._p5 = new p5(p => {
      this.renderer = new OpticsRenderer(p);

      p.setup = () => {
        const w = this.container?.clientWidth || 800;
        const h = this.container?.clientHeight || 600;
        const cv = p.createCanvas(w, h);
        cv.parent(container);
        cv.style('background', 'transparent');
        this._recomputeMapper(w, h);
        p.noLoop();
        p.clear();
      };

      p.draw = () => {
        p.clear();
        if (!this._state || !this._model) return;

        // Render everything in pure source coordinates inside aspect-preserving transform stack
        p.push();
        p.translate(this.mapper.offsetX, this.mapper.offsetY);
        p.scale(this.mapper.scale);

        this._renderCurrentScene(p);

        if (this._showDebug) {
          this._drawPrecisionDebug(p);
        }

        p.pop();
      };

      p.mousePressed = () => {
        if (!this._model) return;
        const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
        const sub = this._model.subtype || 'thin_lens';
        const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);

        if (sub === 'prism') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
            this._dragTarget = 'light_source';
            p.cursor('grabbing');
          }
          return;
        }

        if (sub === 'interface_refraction') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
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

        const nearTip = Math.hypot(srcM.x - obj.x, srcM.y - tipY) < hitR;
        const shaftTol = 22 / Math.max(0.001, this.mapper.scale);
        const nearShaft = Math.abs(srcM.x - obj.x) < shaftTol && srcM.y >= minY - 10 && srcM.y <= maxY + 10;

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
        const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
        const sub = this._model.subtype || 'thin_lens';
        const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);

        if (sub === 'prism') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
            p.cursor('grab');
          } else {
            p.cursor('default');
          }
          return;
        }

        if (sub === 'interface_refraction') {
          const ls = this._model.lightSource;
          if (ls && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
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
        const nearTip = Math.hypot(srcM.x - obj.x, srcM.y - tipY) < hitR;
        const shaftTol = 22 / Math.max(0.001, this.mapper.scale);
        const nearShaft = Math.abs(srcM.x - obj.x) < shaftTol && srcM.y >= minY - 10 && srcM.y <= maxY + 10;

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
        const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
        const sub = this._model.subtype || 'thin_lens';
        const srcW = this._model.sourceWidth || 800;
        const srcH = this._model.sourceHeight || 600;

        if (sub === 'prism') {
          if (this._dragTarget === 'light_source') {
            const newX = p.constrain(srcM.x, 20, srcW - 20);
            const newY = p.constrain(srcM.y, 20, srcH - 20);
            this.onDragPrism(newX, newY);
          }
          return;
        }

        if (sub === 'interface_refraction') {
          if (this._dragTarget === 'interface_source') {
            const boundY = this._model.boundary?.y ?? 300;
            const newX = p.constrain(srcM.x, 20, srcW - 20);
            const newY = p.constrain(srcM.y, 20, boundY - 10);
            this.onDragInterface(newX, newY);
          }
          return;
        }

        const obj = this._model.object;
        if (!obj) return;
        const maxX = (sub === 'mirror' ? this._model.mirror.x : this._model.lens.x) - 10;

        if (this._dragTarget === 'object_tip') {
          const newX = p.constrain(srcM.x, 20, maxX);
          const rawHeight = srcM.y - this._model.axisY;
          const minH = -(srcH * 0.45);
          const newH = p.constrain(rawHeight, minH, -20);
          if (sub === 'mirror') this.onDragMirror(newX, newH);
          else this.onDragLens(newX, newH);
        } else if (this._dragTarget === 'object_pos') {
          const newX = p.constrain(srcM.x, 20, maxX);
          if (sub === 'mirror') this.onDragMirror(newX, obj.height);
          else this.onDragLens(newX, obj.height);
        }
      };

      p.mouseReleased = () => {
        this._dragTarget = null;
        p.cursor('default');
      };
    });

    // Resize observer to track container dimensions responsively
    if (typeof ResizeObserver !== 'undefined' && container) {
      this._resizeObserver = new ResizeObserver(entries => {
        for (const entry of entries) {
          const cr = entry.contentRect;
          const w = Math.round(cr.width);
          const h = Math.round(cr.height);
          if (w > 0 && h > 0 && this._p5) {
            this._p5.resizeCanvas(w, h);
            this._recomputeMapper(w, h);
            this._p5.redraw();
          }
        }
      });
      this._resizeObserver.observe(container);
    }
  }

  _recomputeMapper(w, h) {
    const srcW = this._model?.sourceWidth || 800;
    const srcH = this._model?.sourceHeight || 600;
    const viewW = w || this.container?.clientWidth || (this._p5 ? this._p5.width : 800);
    const viewH = h || this.container?.clientHeight || (this._p5 ? this._p5.height : 600);
    this.mapper.update(srcW, srcH, viewW, viewH);
  }

  render(model, result) {
    this._model = model;
    this._state = result;
    this._recomputeMapper();
    this._p5?.redraw();
  }

  setDebug(enable) {
    this._showDebug = enable;
    this._p5?.redraw();
  }

  destroy() {
    if (this._resizeObserver) {
      this._resizeObserver.disconnect();
      this._resizeObserver = null;
    }
    this._p5?.remove();
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
    const srcW = m.sourceWidth || 800;

    ren.drawOpticalAxis(m.axisY, srcW);

    (m.focalPoints || []).forEach(fp => {
      ren.drawFocalPoint(fp.x, m.axisY, fp.label);
    });

    const isConcave = m.lens.focalLength < 0 || m.lens.model === 'concave';
    const apH = m.lens.apertureHeight || THEME.lens.apertureH;
    if (isConcave) {
      ren.drawConcaveLens(m.lens.x, m.axisY, apH);
    } else {
      ren.drawConvexLens(m.lens.x, m.axisY, apH);
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

    const spriteImg = m.object?.spriteUrl ? opticsSprites.get(p, m.object.spriteUrl) : null;

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
    if (m.object) {
      let drewObj = false;
      if (spriteImg) {
        drewObj = opticsSprites.drawObject(p, spriteImg, m.object.x, m.axisY, m.object.height);
      }
      if (!drewObj) {
        ren.drawArrow(m.object.x, m.axisY, m.object.height, THEME.object, true);
      }

      const tipY = m.axisY + m.object.height;
      const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
      const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);
      if (!this._dragTarget && Math.abs(srcM.x - m.object.x) < hitR) {
        ren.drawDragHint(m.object.x, tipY, 20 / Math.max(0.001, this.mapper.scale), 'drag');
      }
    }

    if (this._showDebug) {
      if (m.object) {
        const tipY = m.axisY + m.object.height;
        ren.drawDebugTag(m.object.x, tipY - 8, `Obj (${Math.round(m.object.x)}, ${Math.round(tipY)})`);
      }
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
    (r.segments || []).forEach(seg => {
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

      const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
      const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);
      if (!this._dragTarget && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
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
    const srcW = m.sourceWidth || 800;

    ren.drawOpticalAxis(m.axisY, srcW);

    (m.focalPoints || []).forEach(fp => {
      ren.drawFocalPoint(fp.x, m.axisY, fp.label);
    });

    // Curvature radius & aperture height from detected geometry, without magic constants
    const R = m.mirror.curvatureRadius ?? (2 * Math.abs(m.mirror.focalLength || 100));
    const apH = m.mirror.apertureHeight ?? 220;
    ren.drawMirror(m.mirror.x, m.axisY, R, apH, m.mirror.model);

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

    const spriteImg = m.object?.spriteUrl ? opticsSprites.get(p, m.object.spriteUrl) : null;

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
    if (m.object) {
      let drewObj = false;
      if (spriteImg) {
        drewObj = opticsSprites.drawObject(p, spriteImg, m.object.x, m.axisY, m.object.height);
      }
      if (!drewObj) {
        ren.drawArrow(m.object.x, m.axisY, m.object.height, THEME.object, true);
      }

      const tipY = m.axisY + m.object.height;
      const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
      const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);
      if (!this._dragTarget && Math.abs(srcM.x - m.object.x) < hitR) {
        ren.drawDragHint(m.object.x, tipY, 20 / Math.max(0.001, this.mapper.scale), 'drag');
      }
    }

    if (this._showDebug) {
      if (m.object) {
        const tipY = m.axisY + m.object.height;
        ren.drawDebugTag(m.object.x, tipY - 8, `Obj (${Math.round(m.object.x)}, ${Math.round(tipY)})`);
      }
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
    const srcW = m.sourceWidth || 800;
    const srcH = m.sourceHeight || 600;

    const bY = m.boundary?.y ?? (srcH * 0.5);
    const nX = m.normal?.x ?? (srcW * 0.5);

    // 1. Medium background fills / tints (only draw when there is no textbook background image)
    if (!m.backgroundUrl) {
      p.push();
      p.noStroke();
      // Medium 1 (top)
      p.fill(30, 41, 59, 120); // subtle slate
      p.rect(0, 0, srcW, bY);
      // Medium 2 (bottom)
      p.fill(14, 116, 144, 90); // subtle cyan/water tint
      p.rect(0, bY, srcW, srcH - bY);

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
      p.text(`${m2Name} (n₂ = ${m2N})`, 25, srcH - 20);
      p.pop();
    }

    // 2. Boundary interface line
    p.push();
    p.stroke('#38bdf8');
    p.strokeWeight(2.5);
    p.line(0, bY, srcW, bY);
    p.pop();

    // 3. Normal line (vertical dashed line across boundary)
    const nTop = r.normalLine?.top || r.normalLine?.p1 || r.normalLine?.[0] || { x: nX, y: Math.max(20, bY - 220) };
    const nBot = r.normalLine?.bottom || r.normalLine?.p2 || r.normalLine?.[1] || { x: nX, y: Math.min(srcH - 20, bY + 220) };
    ren.drawNormal(nTop, nBot);
    p.push();
    p.fill('rgba(255,255,255,0.85)');
    p.noStroke();
    p.textSize(12);
    p.textAlign(p.CENTER, p.BOTTOM);
    p.text("Normal N-N'", nX, nTop.y - 6);
    p.pop();

    // 4. Resolve ray points safely
    const poi = { x: nX, y: bY };
    const incStart = r.incidentRay?.start || r.incidentRay?.[0] || (m.lightSource ? { x: m.lightSource.x, y: m.lightSource.y } : null);
    const incEnd   = r.incidentRay?.end   || r.incidentRay?.[1] || poi;

    const refrStart = r.refractedRay?.start || r.refractedRay?.[0] || poi;
    const refrEnd   = r.refractedRay?.end   || r.refractedRay?.[1];

    const reflStart = r.reflectedRay?.start || r.reflectedRay?.[0] || poi;
    const reflEnd   = r.reflectedRay?.end   || r.reflectedRay?.[1];

    // 5. Draw Angle arcs at point of incidence
    if (incStart) {
      const vInc = { x: incStart.x - poi.x, y: incStart.y - poi.y };
      const vNormTop = { x: 0, y: -1 };
      const lbl1 = r.angles?.theta1Deg != null ? `θ₁ = ${Math.round(r.angles.theta1Deg)}°` : 'θ₁';
      ren.drawAngleBetweenVectors(poi, vInc, vNormTop, 36, lbl1);
    }

    if (refrEnd && !r.isTIR) {
      const vRefr = { x: refrEnd.x - poi.x, y: refrEnd.y - poi.y };
      const vNormBot = { x: 0, y: 1 };
      const lbl2 = r.angles?.theta2Deg != null ? `θ₂ = ${Math.round(r.angles.theta2Deg)}°` : 'θ₂';
      ren.drawAngleBetweenVectors(poi, vRefr, vNormBot, 36, lbl2);
    }

    // 6. Draw Light Rays
    if (incStart && incEnd) {
      ren.drawRayWithArrow(incStart, incEnd, '#facc15', 3.0);
    }
    if (refrStart && refrEnd && !r.isTIR) {
      ren.drawRayWithArrow(refrStart, refrEnd, '#38bdf8', 3.0);
    }
    if (reflStart && reflEnd && r.isTIR) {
      ren.drawRayWithArrow(reflStart, reflEnd, '#f87171', 3.0);
    }

    // 7. Interactive Light Source emitter
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

      const srcM = this.mapper.viewToSource(p.mouseX, p.mouseY);
      const hitR = DRAG_R / Math.max(0.001, this.mapper.scale);
      if (!this._dragTarget && Math.hypot(srcM.x - ls.x, srcM.y - ls.y) < hitR * 1.5) {
        ren.drawDragHint(ls.x, ls.y, 20 / Math.max(0.001, this.mapper.scale), 'drag');
      }
    }

    // 8. Debug tags
    if (this._showDebug) {
      ren.drawDebugTag(nX, bY, `POI (${Math.round(nX)}, ${Math.round(bY)})`);
      if (ls) ren.drawDebugTag(ls.x, ls.y + 16, `Source (${Math.round(ls.x)}, ${Math.round(ls.y)})`);
    }
  }

  _drawPrecisionDebug(p) {
    const { _model: m } = this;
    const srcW = m.sourceWidth || 800;
    const srcH = m.sourceHeight || 600;

    p.push();
    // 1. Source bounds dashed frame
    p.noFill();
    p.stroke('rgba(56, 189, 248, 0.45)');
    p.strokeWeight(1.5 / Math.max(0.001, this.mapper.scale));
    p.drawingContext.setLineDash([8, 6]);
    p.rect(0, 0, srcW, srcH);
    p.drawingContext.setLineDash([]);

    // 2. Precision & Provenance Info Box (top-left)
    const pad = 12;
    p.fill('rgba(15, 23, 42, 0.85)');
    p.stroke('rgba(56, 189, 248, 0.7)');
    p.strokeWeight(1 / Math.max(0.001, this.mapper.scale));
    p.rect(pad, pad, 360, 72, 6);

    p.noStroke();
    p.fill('#38bdf8');
    p.textSize(12);
    p.textAlign(p.LEFT, p.TOP);
    p.text(`PRECISION OVERLAY [${m.isPrecision ? 'PRECISION MODE' : 'EXPLORE MODE'}]`, pad + 10, pad + 8);

    p.fill('#e2e8f0');
    p.textSize(10.5);
    const conf = m.confidence != null ? `${(m.confidence * 100).toFixed(0)}%` : 'N/A';
    p.text(`Source Res: ${srcW} × ${srcH} px | Scale: ${this.mapper.scale.toFixed(3)} | Confidence: ${conf}`, pad + 10, pad + 28);

    // Provenance details
    let provSummary = '';
    if (m.lens?.provenance?.focalLength) {
      const pl = m.lens.provenance.focalLength;
      provSummary = `Focal length: ${Math.round(m.lens.focalLength)} px (${pl.status}, conf: ${Math.round((pl.confidence || 0) * 100)}%)`;
    } else if (m.mirror?.provenance?.focalLength) {
      const pm = m.mirror.provenance.focalLength;
      provSummary = `Focal length: ${Math.round(m.mirror.focalLength)} px (${pm.status}, conf: ${Math.round((pm.confidence || 0) * 100)}%)`;
    } else if (m.prism?.provenance?.refractiveIndex) {
      const pp = m.prism.provenance.refractiveIndex;
      provSummary = `Index n: ${m.prism.refractiveIndex.toFixed(2)} (${pp.status})`;
    } else {
      provSummary = `Registration: 1:1 aspect-preserved contain transform`;
    }
    p.fill('#94a3b8');
    p.text(provSummary, pad + 10, pad + 48);

    p.pop();
  }
}
