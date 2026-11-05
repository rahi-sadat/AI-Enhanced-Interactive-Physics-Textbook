from pathlib import Path

import cv2
import pytest

from ai.evidence.cv.spherical_mirror_cv import SphericalMirrorCVCandidateExtractor


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/unseen/optics/concave_mirror_diagram.png"


@pytest.mark.parametrize("scale", [1.0, 0.75])
def test_mirror_pole_and_focus_follow_source_resize(scale):
    image = cv2.imread(str(FIXTURE))
    assert image is not None
    if scale != 1.0:
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    height, width = image.shape[:2]
    result = SphericalMirrorCVCandidateExtractor().extract(
        image, source_width=width, source_height=height,
    )
    pole = result["pole"]
    focus = result["focus_point"]
    assert pole is not None
    assert focus is not None
    assert abs(pole.x - 657 * scale) <= 20 * scale
    assert abs(pole.y - 308 * scale) <= 12 * scale
    assert abs(abs(pole.x - focus.x) - 132 * scale) <= 20 * scale
