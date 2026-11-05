"""Preserve real physics evidence when suppressing OCR readings of symbols."""
import pytest

from ai.evidence.pipeline import EvidenceExtractionPipeline


@pytest.mark.parametrize('text', ['mm', 'Mm', 'mW', 'MW', 'mV', 'MV', '10 mV', '5 Ω', 'R1'])
def test_units_values_and_designators_are_not_schematic_glyphs(text):
    assert not EvidenceExtractionPipeline._is_schematic_glyph_token(text)


@pytest.mark.parametrize('text', ['-WW', 'WWW', 'vvv', 'MM', '~WW~', '', '   '])
def test_repeated_symbol_strokes_are_suppressed(text):
    assert EvidenceExtractionPipeline._is_schematic_glyph_token(text)
