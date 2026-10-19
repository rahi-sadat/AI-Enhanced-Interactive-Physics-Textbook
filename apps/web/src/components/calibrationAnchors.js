/** Build inspection reticles only from compiled source-pixel coordinates. */
export function calibrationAnchorsFromScene(scene) {
  const geometry = scene?.geometry || {};
  const anchors = [];
  const add = (id, label, point, color = '#38bdf8') => {
    let x;
    let y;
    if (Array.isArray(point)) [x, y] = point;
    else if (point && typeof point === 'object') ({ x, y } = point);
    if (typeof x !== 'number' || typeof y !== 'number' ||
        !Number.isFinite(x) || !Number.isFinite(y)) return;
    anchors.push({ id, label, x, y, color });
  };

  switch (scene?.subtype || scene?.type) {
    case 'pendulum':
      add('pivot', 'Pivot', geometry.pivot);
      add('bob', 'Bob Initial', geometry.bob_center, '#f59e0b');
      break;
    case 'projectile':
      add('launch', 'Launch point', geometry.launch_position || geometry.launch_origin);
      break;
    case 'thin_lens':
      add('lens_center', 'Optical center', geometry.lens_center ||
        (Number.isFinite(geometry.lensX) && Number.isFinite(geometry.axisY)
          ? { x: geometry.lensX, y: geometry.axisY } : null));
      break;
    case 'spherical_mirror':
      add('pole', 'Mirror pole', geometry.pole);
      break;
    case 'interface_refraction':
      add('incidence', 'Incidence point', geometry.incidence_point ||
        (Number.isFinite(geometry.normalX) && Number.isFinite(geometry.boundaryY)
          ? { x: geometry.normalX, y: geometry.boundaryY } : null));
      break;
    case 'prism':
      if (Array.isArray(geometry.vertices)) {
        geometry.vertices.forEach((vertex, index) => add(`vertex_${index}`, `Prism vertex ${index + 1}`, vertex));
      }
      break;
    case 'dc_linear':
      for (const component of scene?.circuit?.components || []) {
        for (const terminal of component.terminals || []) {
          add(terminal.id, `${component.id} terminal`, terminal.source_px);
        }
      }
      break;
  }
  return anchors;
}
