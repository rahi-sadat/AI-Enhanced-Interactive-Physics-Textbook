/**
 * apps/web/src/features/simulations/optics/OpticsRenderer.js
 * 
 * Generic, source-aligned optics simulation renderer.
 * Consumes solved RuntimeOutput geometry for thin lenses, spherical mirrors,
 * interface refraction, and prisms.
 * Provides direct bidirectional manipulation on top of the original textbook diagram.
 * RENDERER NEVER SOLVES PHYSICS EQUATIONS.
 */

import { SimulationRenderer } from '../core/SimulationRenderer.js';

export class OpticsRenderer extends SimulationRenderer {
  constructor() {
    super();
    this.svg = null;
    this.layers = {
      axis: null,
      landmarks: null,
      shapes: null,
      rays: null,
      image: null,
      object: null,
      handles: null,
    };

    this._dragState = null; // { type: 'object_pos' | 'object_tip' | 'source_pos', startX, startY }
    this._boundOnPointerDown = this._handlePointerDown.bind(this);
    this._boundOnPointerMove = this._handlePointerMove.bind(this);
    this._boundOnPointerUp = this._handlePointerUp.bind(this);
  }

  mount({ container, sourceImage = null, scene, coordinateMapper, onInteract = () => {} }) {
    super.mount({ container, sourceImage, scene, coordinateMapper, onInteract });

    // 1. Build authoritative SVG canvas matching source image coordinates
    container.innerHTML = '';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'optics-overlay-svg');
    svg.style.position = 'absolute';
    svg.style.overflow = 'visible';
    svg.style.pointerEvents = 'none';
    svg.style.userSelect = 'none';

    // Layer groups for precise z-stacking
    const gAxis = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gAxis.setAttribute('class', 'layer-axis');
    const gLandmarks = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gLandmarks.setAttribute('class', 'layer-landmarks');
    const gShapes = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gShapes.setAttribute('class', 'layer-shapes');
    const gRays = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gRays.setAttribute('class', 'layer-rays');
    const gImage = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gImage.setAttribute('class', 'layer-image');
    const gObject = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gObject.setAttribute('class', 'layer-object');
    const gHandles = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gHandles.setAttribute('class', 'layer-handles');
    gHandles.style.pointerEvents = 'auto';

    svg.appendChild(gAxis);
    svg.appendChild(gLandmarks);
    svg.appendChild(gShapes);
    svg.appendChild(gRays);
    svg.appendChild(gImage);
    svg.appendChild(gObject);
    svg.appendChild(gHandles);

    container.appendChild(svg);
    this.svg = svg;
    this.layers = {
      axis: gAxis,
      landmarks: gLandmarks,
      shapes: gShapes,
      rays: gRays,
      image: gImage,
      object: gObject,
      handles: gHandles,
    };

    this.resize(coordinateMapper);

    // Bind pointer events on container
    container.addEventListener('pointerdown', this._boundOnPointerDown);
    window.addEventListener('pointermove', this._boundOnPointerMove);
    window.addEventListener('pointerup', this._boundOnPointerUp);
    window.addEventListener('pointercancel', this._boundOnPointerUp);
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

    this._clearLayers();

    const subtype = runtimeOutput.subtype;
    if (!subtype) {
      // Missing subtype: explicit failure / render nothing, never silently fall back
      return;
    }

    const geom = runtimeOutput.geometry || {};

    if (subtype === 'thin_lens') {
      this._renderThinLens(geom, runtimeOutput);
    } else if (subtype === 'spherical_mirror' || subtype === 'mirror') {
      this._renderMirror(geom, runtimeOutput);
    } else if (subtype === 'interface_refraction') {
      this._renderInterfaceRefraction(geom, runtimeOutput);
    } else if (subtype === 'prism') {
      this._renderPrism(geom, runtimeOutput);
    }
  }

  _clearLayers() {
    for (const group of Object.values(this.layers)) {
      if (group) group.innerHTML = '';
    }
  }

  // ---------------------------------------------------------------------------
  // Subtype Renderers (Pure Visual Projection of Solved Geometry)
  // ---------------------------------------------------------------------------

  _renderThinLens(geom, output) {
    const { opticalAxis, landmarks, lens, object, image, rays } = geom;

    // 1. Principal Optical Axis
    if (opticalAxis) {
      const line = this._createLine(opticalAxis.minX, opticalAxis.y, opticalAxis.maxX, opticalAxis.y, {
        stroke: 'rgba(148, 163, 184, 0.45)',
        strokeWidth: 1.5,
        strokeDasharray: '6 4'
      });
      this.layers.axis.appendChild(line);
    }

    // 2. Optical Center & Focal Markers
    if (landmarks) {
      if (landmarks.lensCenter) {
        const { x, y } = landmarks.lensCenter;
        this.layers.landmarks.appendChild(this._createCircle(x, y, 3.5, { fill: '#38bdf8' }));
        this.layers.landmarks.appendChild(this._createText(x, y + 16, 'O', { fill: '#38bdf8', fontSize: 12, textAnchor: 'middle' }));
      }
      if (Array.isArray(landmarks.focalPoints)) {
        for (const fp of landmarks.focalPoints) {
          this.layers.landmarks.appendChild(this._createCircle(fp.x, fp.y, 3, { fill: '#34d399' }));
          this.layers.landmarks.appendChild(this._createText(fp.x, fp.y + 15, fp.label, { fill: '#34d399', fontSize: 11, textAnchor: 'middle' }));
        }
      }
    }

    // 3. Lens Geometric Stems & Arrows (Convex / Concave)
    // Only rendered when explicit aperture height geometry is supplied by the scene.
    // In source_px augmentation mode, if static lens shape geometry is absent,
    // we leave the original textbook object visible rather than drawing a guessed replacement.
    if (lens && lens.apertureHeight != null) {
      const lx = lens.x;
      const ay = lens.axisY;
      const apH = lens.apertureHeight / 2;
      const isConcave = lens.lensType === 'concave';

      // Vertical aperture centerline
      const stem = this._createLine(lx, ay - apH, lx, ay + apH, {
        stroke: 'rgba(56, 189, 248, 0.7)',
        strokeWidth: 2.5
      });
      this.layers.shapes.appendChild(stem);

      // Top & Bottom Chevron caps
      const capD = isConcave ? 8 : -8;
      const topCap = this._createPolyline([
        [lx - 8, ay - apH - capD],
        [lx, ay - apH],
        [lx + 8, ay - apH - capD]
      ], { stroke: 'rgba(56, 189, 248, 0.9)', strokeWidth: 2, fill: 'none' });

      const botCap = this._createPolyline([
        [lx - 8, ay + apH + capD],
        [lx, ay + apH],
        [lx + 8, ay + apH + capD]
      ], { stroke: 'rgba(56, 189, 248, 0.9)', strokeWidth: 2, fill: 'none' });

      this.layers.shapes.appendChild(topCap);
      this.layers.shapes.appendChild(botCap);
    }

    // 4. Principal Rays
    if (Array.isArray(rays)) {
      const rayColors = ['#f59e0b', '#38bdf8', '#a855f7', '#ec4899'];
      rays.forEach((ray, idx) => {
        const col = rayColors[idx % rayColors.length];
        const pts = ray.points || [];
        for (let i = 0; i < pts.length - 1; i++) {
          const p1 = pts[i];
          const p2 = pts[i + 1];
          const rLine = this._createLine(p1.x, p1.y, p2.x, p2.y, {
            stroke: col,
            strokeWidth: 2,
            strokeDasharray: ray.dashed ? '5 4' : null,
            opacity: ray.dashed ? 0.7 : 0.95
          });
          this.layers.rays.appendChild(rLine);
        }
      });
    }

    // 5. Formed Image Arrow
    if (image && Number.isFinite(image.x) && Number.isFinite(image.height)) {
      const col = image.isReal ? '#34d399' : '#f87171';
      this._renderArrow(this.layers.image, image.base.x, image.base.y, image.tip.x, image.tip.y, {
        color: col,
        dashed: !image.isReal,
        label: image.isReal ? 'Real Image' : 'Virtual Image'
      });
    }

    // 6. Object Arrow & Direct Manipulation Handles
    if (object) {
      this._renderArrow(this.layers.object, object.base.x, object.base.y, object.tip.x, object.tip.y, {
        color: '#38bdf8',
        dashed: false,
        label: 'Object'
      });

      const arrowHandle = geom.handles?.objectArrow;
      const targetId = arrowHandle?.targetId;

      // Draggable Object Handle (Position / Distance) - only if explicitly editable, with targetId and parameter address
      const xParamAddress = arrowHandle?.axes?.x?.parameter;
      if (targetId && xParamAddress && arrowHandle?.axes?.x?.editable !== false) {
        const handlePos = this._createCircle(object.base.x, object.base.y + object.height / 2, 9, {
          fill: 'rgba(56, 189, 248, 0.25)',
          stroke: '#38bdf8',
          strokeWidth: 2,
          cursor: 'ew-resize',
          class: 'if-handle if-handle-object-pos'
        });
        handlePos.setAttribute('data-handle', 'object_pos');
        handlePos.setAttribute('data-target-id', targetId);
        handlePos.setAttribute('data-param-address', xParamAddress);
        this.layers.handles.appendChild(handlePos);
      }

      // Draggable Arrow Tip Handle (Height) - only if explicitly editable, with targetId and parameter address
      const yParamAddress = arrowHandle?.axes?.y?.parameter;
      if (targetId && yParamAddress && arrowHandle?.axes?.y?.editable !== false) {
        const handleTip = this._createCircle(object.tip.x, object.tip.y, 7, {
          fill: '#38bdf8',
          stroke: '#ffffff',
          strokeWidth: 2,
          cursor: 'ns-resize',
          class: 'if-handle if-handle-object-tip'
        });
        handleTip.setAttribute('data-handle', 'object_tip');
        handleTip.setAttribute('data-target-id', targetId);
        handleTip.setAttribute('data-param-address', yParamAddress);
        this.layers.handles.appendChild(handleTip);
      }
    }
  }

  _renderMirror(geom, output) {
    const { opticalAxis, landmarks, mirror, object, image, rays } = geom;

    // Optical Axis
    if (opticalAxis) {
      this.layers.axis.appendChild(this._createLine(opticalAxis.minX, opticalAxis.y, opticalAxis.maxX, opticalAxis.y, {
        stroke: 'rgba(148, 163, 184, 0.45)',
        strokeWidth: 1.5,
        strokeDasharray: '6 4'
      }));
    }

    // Landmarks (P, F, C)
    if (landmarks) {
      if (landmarks.pole) {
        this.layers.landmarks.appendChild(this._createCircle(landmarks.pole.x, landmarks.pole.y, 3.5, { fill: '#38bdf8' }));
        this.layers.landmarks.appendChild(this._createText(landmarks.pole.x, landmarks.pole.y + 16, 'P', { fill: '#38bdf8', fontSize: 12, textAnchor: 'middle' }));
      }
      if (Array.isArray(landmarks.focalPoints)) {
        for (const fp of landmarks.focalPoints) {
          this.layers.landmarks.appendChild(this._createCircle(fp.x, fp.y, 3, { fill: '#34d399' }));
          this.layers.landmarks.appendChild(this._createText(fp.x, fp.y + 15, fp.label, { fill: '#34d399', fontSize: 11, textAnchor: 'middle' }));
        }
      }
    }

    // Mirror Arc Curve (only when explicit aperture height geometry is supplied)
    if (mirror && mirror.apertureHeight != null) {
      const mx = mirror.x;
      const ay = mirror.axisY;
      const apH = mirror.apertureHeight / 2;
      const isConvex = mirror.model === 'convex';
      const sagitta = isConvex ? 14 : -14;

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${mx + sagitta} ${ay - apH} Q ${mx} ${ay} ${mx + sagitta} ${ay + apH}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', '#38bdf8');
      path.setAttribute('stroke-width', '3');
      this.layers.shapes.appendChild(path);
    }

    // Rays
    if (Array.isArray(rays)) {
      const rayColors = ['#f59e0b', '#38bdf8', '#a855f7'];
      rays.forEach((ray, idx) => {
        const col = rayColors[idx % rayColors.length];
        const pts = ray.points || [];
        for (let i = 0; i < pts.length - 1; i++) {
          this.layers.rays.appendChild(this._createLine(pts[i].x, pts[i].y, pts[i + 1].x, pts[i + 1].y, {
            stroke: col,
            strokeWidth: 2,
            strokeDasharray: ray.dashed ? '5 4' : null,
            opacity: ray.dashed ? 0.7 : 0.95
          }));
        }
      });
    }

    // Image Arrow
    if (image && Number.isFinite(image.x) && Number.isFinite(image.height)) {
      const col = image.isReal ? '#34d399' : '#f87171';
      this._renderArrow(this.layers.image, image.base.x, image.base.y, image.tip.x, image.tip.y, {
        color: col,
        dashed: !image.isReal,
        label: image.isReal ? 'Real Image' : 'Virtual Image'
      });
    }

    // Object Arrow & Handles
    if (object) {
      this._renderArrow(this.layers.object, object.base.x, object.base.y, object.tip.x, object.tip.y, {
        color: '#38bdf8',
        dashed: false,
        label: 'Object'
      });

      const arrowHandle = geom.handles?.objectArrow;
      const targetId = arrowHandle?.targetId;

      const xParamAddress = arrowHandle?.axes?.x?.parameter;
      if (targetId && xParamAddress && arrowHandle?.axes?.x?.editable !== false) {
        const handlePos = this._createCircle(object.base.x, object.base.y + object.height / 2, 9, {
          fill: 'rgba(56, 189, 248, 0.25)',
          stroke: '#38bdf8',
          strokeWidth: 2,
          cursor: 'ew-resize',
          class: 'if-handle if-handle-object-pos'
        });
        handlePos.setAttribute('data-handle', 'object_pos');
        handlePos.setAttribute('data-target-id', targetId);
        handlePos.setAttribute('data-param-address', xParamAddress);
        this.layers.handles.appendChild(handlePos);
      }

      const yParamAddress = arrowHandle?.axes?.y?.parameter;
      if (targetId && yParamAddress && arrowHandle?.axes?.y?.editable !== false) {
        const handleTip = this._createCircle(object.tip.x, object.tip.y, 7, {
          fill: '#38bdf8',
          stroke: '#ffffff',
          strokeWidth: 2,
          cursor: 'ns-resize',
          class: 'if-handle if-handle-object-tip'
        });
        handleTip.setAttribute('data-handle', 'object_tip');
        handleTip.setAttribute('data-target-id', targetId);
        handleTip.setAttribute('data-param-address', yParamAddress);
        this.layers.handles.appendChild(handleTip);
      }
    }
  }

  _renderInterfaceRefraction(geom, output) {
    const { boundary, normal, rays, n1, n2, isTIR } = geom;
    const srcW = this.coordinateMapper?.sourceW;
    const srcH = this.coordinateMapper?.sourceH;

    const bY = boundary?.y;
    const nX = normal?.x;

    // 1. Boundary line between media (only if boundary geometry supplied by scene)
    if (bY != null && srcW != null) {
      this.layers.shapes.appendChild(this._createLine(0, bY, srcW, bY, {
        stroke: 'rgba(56, 189, 248, 0.8)',
        strokeWidth: 2.5
      }));

      // Medium labels (only if n1 or n2 explicitly supplied)
      if (n1 != null) {
        this.layers.landmarks.appendChild(this._createText(20, bY - 10, `Medium 1 (n₁ = ${n1})`, { fill: '#94a3b8', fontSize: 12 }));
      }
      if (n2 != null) {
        this.layers.landmarks.appendChild(this._createText(20, bY + 20, `Medium 2 (n₂ = ${n2})`, { fill: '#94a3b8', fontSize: 12 }));
      }
    }

    // 2. Normal line (only if normal geometry supplied by scene)
    if (nX != null && srcH != null) {
      this.layers.shapes.appendChild(this._createLine(nX, 0, nX, srcH, {
        stroke: 'rgba(148, 163, 184, 0.5)',
        strokeWidth: 1.5,
        strokeDasharray: '5 5'
      }));
    }

    // 3. Rays
    if (Array.isArray(rays)) {
      rays.forEach((ray, idx) => {
        const pts = ray.points || [];
        const col = isTIR && idx > 0 ? '#ef4444' : (idx === 0 ? '#f59e0b' : '#34d399');
        for (let i = 0; i < pts.length - 1; i++) {
          this.layers.rays.appendChild(this._createLine(pts[i].x, pts[i].y, pts[i + 1].x, pts[i + 1].y, {
            stroke: col,
            strokeWidth: 2.5
          }));
        }
      });
    }

    // 4. Interactive Light Source Emitter Handle (only when declared editable, with targetId and parameter address)
    const lsHandle = geom.handles?.lightSource;
    const srcPt = rays?.[0]?.points?.[0];
    const lsTargetId = lsHandle?.targetId;
    const lsParamAddress = lsHandle?.parameter;
    if (lsHandle && lsHandle.editable !== false && srcPt && lsTargetId && lsParamAddress) {
      const srcHandle = this._createCircle(srcPt.x, srcPt.y, 8, {
        fill: '#facc15',
        stroke: '#eab308',
        strokeWidth: 2,
        cursor: 'move',
        class: 'if-handle if-handle-light-source'
      });
      srcHandle.setAttribute('data-handle', 'light_source');
      srcHandle.setAttribute('data-target-id', lsTargetId);
      srcHandle.setAttribute('data-param-key', lsHandle.key || 'theta1');
      srcHandle.setAttribute('data-param-address', lsParamAddress);
      this.layers.handles.appendChild(srcHandle);
      this.layers.landmarks.appendChild(this._createText(srcPt.x, srcPt.y - 12, 'Beam Source', { fill: '#facc15', fontSize: 11, textAnchor: 'middle' }));
    }
  }

  _renderPrism(geom, output) {
    const { prismVertices, rays, normals } = geom;

    // 1. Prism Glass Polygon
    if (Array.isArray(prismVertices) && prismVertices.length >= 3) {
      const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      const ptsStr = prismVertices.map(v => `${v.x},${v.y}`).join(' ');
      poly.setAttribute('points', ptsStr);
      poly.setAttribute('fill', 'rgba(56, 189, 248, 0.12)');
      poly.setAttribute('stroke', 'rgba(56, 189, 248, 0.85)');
      poly.setAttribute('stroke-width', '2.5');
      this.layers.shapes.appendChild(poly);
    }

    // 2. Normals
    if (Array.isArray(normals)) {
      for (const n of normals) {
        if (n.p1 && n.p2) {
          this.layers.shapes.appendChild(this._createLine(n.p1.x, n.p1.y, n.p2.x, n.p2.y, {
            stroke: 'rgba(148, 163, 184, 0.45)',
            strokeWidth: 1.5,
            strokeDasharray: '4 4'
          }));
        }
      }
    }

    // 3. Rays (Incident, Internal, Emergent)
    if (Array.isArray(rays)) {
      rays.forEach((seg) => {
        let col = '#f59e0b';
        if (seg.type === 'internal') col = '#38bdf8';
        if (seg.type === 'emergent') col = '#34d399';
        if (seg.type === 'tir_reflected') col = '#ef4444';

        const p1 = seg.start || seg.points?.[0];
        const p2 = seg.end || seg.points?.[1];
        if (p1 && p2) {
          this.layers.rays.appendChild(this._createLine(p1.x, p1.y, p2.x, p2.y, {
            stroke: col,
            strokeWidth: 2.5
          }));
        }
      });
    }

    // 4. Interactive Beam Emitter Handle
    // Disabled until point/vector parameter contract is fully established. No non-functional visible handle.
  }

  // ---------------------------------------------------------------------------
  // Direct Pointer Manipulation -> Canonical Parameter Update Bridge
  // ---------------------------------------------------------------------------

  _getPointerSourcePoint(e) {
    const rect = this.container.getBoundingClientRect();
    const cssX = e.clientX - rect.left;
    const cssY = e.clientY - rect.top;
    const isContained = Boolean(this.container?.classList?.contains?.('figure-viewport-overlay'));
    if (isContained && typeof this.coordinateMapper.overlayToSource === 'function') {
      return this.coordinateMapper.overlayToSource(cssX, cssY);
    }
    return this.coordinateMapper.viewToSource(cssX, cssY);
  }

  _handlePointerDown(e) {
    const handleEl = e.target.closest?.('.if-handle');
    if (!handleEl || !this.coordinateMapper) return;

    e.preventDefault();
    e.stopPropagation();

    const handleType = handleEl.getAttribute('data-handle');
    const srcPt = this._getPointerSourcePoint(e);

    this._dragState = {
      type: handleType,
      startX: srcPt.x,
      startY: srcPt.y,
    };

    handleEl.setPointerCapture?.(e.pointerId);
  }

  _handlePointerMove(e) {
    if (!this._dragState || !this.coordinateMapper || !this.runtimeOutput) return;

    e.preventDefault();
    const srcPt = this._getPointerSourcePoint(e);
    const geom = this.runtimeOutput?.geometry || {};
    const handle = geom.handles?.objectArrow;
    const lx = handle?.lensX ?? geom.lens?.x ?? geom.mirror?.x;
    const ay = handle?.axisY ?? geom.opticalAxis?.y ?? geom.lens?.axisY ?? geom.mirror?.axisY;
    if (lx == null || ay == null) return;

    if (this._dragState.type === 'object_pos') {
      // Horizontal object drag: converts source px displacement to physical unit via calibration
      const axisX = handle?.axes?.x;
      const ppu = axisX?.pixelsPerUnit || 1.0;
      const uPx = lx - srcPt.x;
      const uCandidate = uPx / ppu;

      // Interaction limits derived from canonical parameter control.min/max and scene geometry
      const minU = axisX?.min != null ? Number(axisX.min) : 0.1;
      const maxU = axisX?.max != null ? Number(axisX.max) : Number((lx / ppu).toFixed(2));

      const constrainedU = Math.min(maxU, Math.max(minU, uCandidate));
      const uVal = Number(constrainedU.toFixed(2));

      const targetId = handle?.targetId;
      const key = axisX?.parameterKey;
      const address = axisX?.parameter;
      if (!targetId || !key || !address) return;

      this.onInteract?.({
        targetId,
        key,
        address,
        value: uVal,
        unit: axisX?.unit || 'px'
      });
    } else if (this._dragState.type === 'object_tip') {
      // Vertical tip drag: converts vertical displacement to physical unit via calibration
      const axisY = handle?.axes?.y;
      const ppu = axisY?.pixelsPerUnit || 1.0;
      const rawHPx = srcPt.y - ay;
      // Object height: negative in SVG screen coordinates represents upward arrow
      const hCandidate = rawHPx / ppu;

      let minH = axisY?.min != null ? -Math.abs(axisY.min) : -Number(((ay * 0.9) / ppu).toFixed(2));
      let maxH = axisY?.max != null ? -Math.abs(axisY.max) : -Number((1.0 / ppu).toFixed(2));
      if (minH > maxH) {
        const tmp = minH; minH = maxH; maxH = tmp;
      }

      const constrainedH = Math.min(maxH, Math.max(minH, hCandidate));
      const hVal = Number(constrainedH.toFixed(2));

      const targetId = handle?.targetId;
      const key = axisY?.parameterKey;
      const address = axisY?.parameter;
      if (!targetId || !key || !address) return;

      this.onInteract?.({
        targetId,
        key,
        address,
        value: hVal,
        unit: axisY?.unit || 'px'
      });
    } else if (this._dragState.type === 'light_source') {
      // Interface refraction beam source angular drag
      const bY = geom.boundaryY ?? geom.boundary?.y;
      const nX = geom.normalX ?? geom.normal?.x;
      if (bY != null && nX != null) {
        const dx = nX - srcPt.x;
        const dy = bY - srcPt.y;
        if (dy > 2) {
          const rad = Math.atan2(Math.abs(dx), dy);
          const deg = Number(((rad * 180) / Math.PI).toFixed(1));
          const lsHandle = geom.handles?.lightSource;
          const targetId = lsHandle?.targetId;
          const key = lsHandle?.key;
          const address = lsHandle?.parameter;
          if (!targetId || !key || !address) return;

          this.onInteract?.({
            targetId,
            key,
            address,
            value: deg,
            unit: 'deg'
          });
        }
      }
    }
  }

  _handlePointerUp(e) {
    if (this._dragState) {
      this._dragState = null;
    }
  }

  // ---------------------------------------------------------------------------
  // SVG Graphic Primitives Helpers
  // ---------------------------------------------------------------------------

  _createLine(x1, y1, x2, y2, attrs = {}) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    el.setAttribute('x1', String(x1));
    el.setAttribute('y1', String(y1));
    el.setAttribute('x2', String(x2));
    el.setAttribute('y2', String(y2));
    for (const [k, v] of Object.entries(attrs)) {
      if (v != null) el.setAttribute(k.replace(/[A-Z]/g, m => `-${m.toLowerCase()}`), String(v));
    }
    return el;
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

  _createPolyline(points, attrs = {}) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    el.setAttribute('points', points.map(p => `${p[0]},${p[1]}`).join(' '));
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

  _renderArrow(parent, x1, y1, x2, y2, { color = '#38bdf8', dashed = false, label = '' } = {}) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'optics-arrow');

    // Shaft
    const shaft = this._createLine(x1, y1, x2, y2, {
      stroke: color,
      strokeWidth: 3,
      strokeDasharray: dashed ? '5 4' : null,
      opacity: 0.95
    });
    g.appendChild(shaft);

    // Arrowhead
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const headLen = 12;
    const pLeft = [x2 - headLen * Math.cos(angle - Math.PI / 6), y2 - headLen * Math.sin(angle - Math.PI / 6)];
    const pRight = [x2 - headLen * Math.cos(angle + Math.PI / 6), y2 - headLen * Math.sin(angle + Math.PI / 6)];

    const head = this._createPolyline([pLeft, [x2, y2], pRight], {
      stroke: color,
      strokeWidth: 3,
      fill: 'none'
    });
    g.appendChild(head);

    if (label) {
      const lbl = this._createText(x2, y2 + (y2 < y1 ? -10 : 18), label, {
        fill: color,
        fontSize: 11,
        fontWeight: 'bold',
        textAnchor: 'middle'
      });
      g.appendChild(lbl);
    }

    parent.appendChild(g);
  }

  dispose() {
    if (this.container) {
      this.container.removeEventListener('pointerdown', this._boundOnPointerDown);
    }
    window.removeEventListener('pointermove', this._boundOnPointerMove);
    window.removeEventListener('pointerup', this._boundOnPointerUp);
    window.removeEventListener('pointercancel', this._boundOnPointerUp);

    if (this.svg) {
      this.svg.remove();
      this.svg = null;
    }
    super.dispose();
  }
}
