/** core/coordinateMapper.js - Canvas coordinate helpers. */
export function getCanvasSize(scene) {
  const r = scene?.coordinate_system?.render ?? scene?.render ?? {};
  return { width: r.canvas_width_px ?? 800, height: r.canvas_height_px ?? 600 };
}
