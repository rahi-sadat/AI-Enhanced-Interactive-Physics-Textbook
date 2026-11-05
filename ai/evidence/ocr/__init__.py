"""PR-06 OCR Providers Package."""
from .base import OCRProvider
from .rapidocr import RapidOCRProvider
from .bangla import EasyOCRBanglaProvider, is_bengali_text
from .greek_symbols import (
    GreekSymbolOCRProvider,
    PhysicsSymbolCandidateResolver,
    GreekConfusableResolver,
    generate_symbol_alternatives,
)
from .formula import (
    FormulaRecognitionProvider,
    MockFormulaRecognitionProvider,
    UnavailableFormulaRecognitionProvider,
)
from .router import MultiOCRRouter
from .mock import MockOCRProvider, UnavailableOCRProvider

__all__ = [
    "OCRProvider",
    "RapidOCRProvider",
    "EasyOCRBanglaProvider",
    "is_bengali_text",
    "GreekSymbolOCRProvider",
    "PhysicsSymbolCandidateResolver",
    "GreekConfusableResolver",
    "generate_symbol_alternatives",
    "FormulaRecognitionProvider",
    "MockFormulaRecognitionProvider",
    "UnavailableFormulaRecognitionProvider",
    "MultiOCRRouter",
    "MockOCRProvider",
    "UnavailableOCRProvider",
]
