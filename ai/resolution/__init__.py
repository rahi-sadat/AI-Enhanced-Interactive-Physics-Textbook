"""PR-07 Resolution, Review, and Compilation Readiness Engine.

Architectural Layer:
  Evidence Grounded BookIR (PR-06)
      ↓
  Resolution Engine & Review Analyzer (PR-07)
      ↓
  Compilation Readiness Evaluator (PR-07)
      ↓
  READY_TO_COMPILE BookIR
      ↓
  PhysicsCompiler (PR-04/PR-02)
"""
from __future__ import annotations

from .requirements import (
    RequirementRegistry,
    ModelRequirementSpec,
)
from .policies import (
    ResolutionPolicy,
    PolicyRegistry,
)
from .units import (
    UnitEngine,
    ParsedQuantity,
    CANONICAL_UNITS,
)
from .calibration import (
    CalibrationEngine,
    CalibrationData,
)
from .analyzer import (
    ResolutionAnalyzer,
)
from .evaluator import (
    ReadinessEvaluator,
)
from .engine import (
    ResolutionEngine,
    ResolutionResult,
)

__all__ = [
    "RequirementRegistry",
    "ModelRequirementSpec",
    "ResolutionPolicy",
    "PolicyRegistry",
    "UnitEngine",
    "ParsedQuantity",
    "CANONICAL_UNITS",
    "CalibrationEngine",
    "CalibrationData",
    "ResolutionAnalyzer",
    "ReadinessEvaluator",
    "ResolutionEngine",
    "ResolutionResult",
]
