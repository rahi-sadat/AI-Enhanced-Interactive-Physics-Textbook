"""A wire crossing needs a visible dot before CV may call it a junction."""
import cv2
import numpy as np

from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor


def test_crossing_and_junction_dot_have_distinct_cv_evidence():
    extractor = CircuitCVCandidateExtractor()

    def inspect(with_dot):
        image = np.full((400, 400, 3), 255, dtype=np.uint8)
        cv2.line(image, (50, 200), (350, 200), (0, 0, 0), 2)
        cv2.line(image, (200, 50), (200, 350), (0, 0, 0), 2)
        if with_dot:
            cv2.circle(image, (200, 200), 7, (0, 0, 0), -1)
        return extractor.extract(image, source_width=400, source_height=400)

    crossing = inspect(False)
    junction = inspect(True)
    assert not any(point.distance_to(type(point)(200, 200)) < 15
                   for point in crossing["junctions"])
    assert any(point.distance_to(type(point)(200, 200)) < 15
               for point in junction["junctions"])
