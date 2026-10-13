import assert from 'node:assert/strict';
import { CoordinateMapper } from '../../engine/core/coordinateMapper.js';

const images = [[393, 328], [800, 600], [1024, 1024], [1536, 1024], [984, 1537]];
const viewports = [[390, 700], [900, 700], [1280, 900], [1600, 600]];
const dprs = [1, 1.25, 1.5, 2];
const sourceErrors = [];

for (const [width, height] of images) {
  const landmarks = [[0, 0], [width / 3, height / 5], [width / 2, height / 2], [width, height]];
  for (const [viewWidth, viewHeight] of viewports) {
    for (const dpr of dprs) {
      const mapper = new CoordinateMapper(width, height, viewWidth, viewHeight, dpr);
      const rect = mapper.renderedImageRect;
      for (const [x, y] of landmarks) {
        const imagePoint = mapper.sourceToView(x, y);
        const overlayPoint = mapper.sourceToOverlay(x, y);
        assert.ok(Math.abs(imagePoint.x - (rect.left + overlayPoint.x)) < 1e-9);
        assert.ok(Math.abs(imagePoint.y - (rect.top + overlayPoint.y)) < 1e-9);
        const recovered = mapper.viewToSource(imagePoint.x, imagePoint.y);
        sourceErrors.push(Math.hypot(recovered.x - x, recovered.y - y));
      }
    }
  }
}

const mean = sourceErrors.reduce((sum, error) => sum + error, 0) / sourceErrors.length;
const max = Math.max(...sourceErrors);
assert.ok(mean <= 1, `Mean registration error ${mean} source px`);
assert.ok(max <= 1, `Max registration error ${max} source px`);
console.log(`Registration matrix: ${sourceErrors.length} landmarks, mean ${mean.toExponential(2)} source px, max ${max.toExponential(2)} source px`);
