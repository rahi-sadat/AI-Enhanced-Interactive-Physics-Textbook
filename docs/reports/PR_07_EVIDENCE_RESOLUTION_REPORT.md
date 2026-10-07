# AugmentedPhysics v2 — Research & Engineering Progress Report
## Milestone PR-07: Evidence Resolution, User Review, Explicit Defaults & Compilation Readiness

**Project:** AugmentedPhysics v2 (AI-Enhanced Interactive Physics Textbook Platform)  
**Author:** Research & Engineering Team  
**Date:** October 2026  
**Target Audience:** Academic Supervisor & Project Stakeholders  
**Repository Branch:** `main`  
**Milestone:** PR-07 (Evidence Resolution, User Review, Explicit Defaults & Compilation Readiness)  

---

## Executive Summary

PR-01 through PR-06 established the ingestion, semantic understanding, multimodal evidence extraction, authoritative visual grounding (`source_px`), parameter provenance, and compiler-gating architecture. Following PR-06, textbook diagrams are grounded with honest pixel coordinates and OCR text candidates, leaving incomplete physics specifications in `BookIR(status: NEEDS_REVIEW)`.

**PR-07 delivers the missing architectural layer between grounded perception and simulation compilation:**
How to safely transform an incomplete, grounded `BookIR` into a fully resolved `BookIR` that is legitimately allowed to transition to `READY_TO_COMPILE` without violating the **Zero Parameter Fabrication** invariant.

### Key Pillars of PR-07:

1. **Evidence vs. Resolution Separation**:
   - PR-06 evidence (`observed_visual`, `observed_ocr`, bounding boxes, OCR candidates) is strictly immutable.
   - User inputs, candidate confirmations, corrections, and policy defaults form a declarative resolution decision layer on top of evidence, never destroying original observations.

2. **Zero Parameter Fabrication**:
   - `PhysicsCompiler` strictly forbids fallback constants (`or 9.81`, `or 0.0`, `or 200.0`, `n_air = 1.0`).
   - Every physical parameter required for simulation must have verified provenance (`observed_ocr`, `user_supplied`, `user_confirmed`, `user_corrected`, `policy_default`, or `derived_calibration`).

3. **Machine-Readable Requirement Specifications**:
   - Reusable `ModelRequirementSpec` catalog defining parameter requirements, expected physical dimensions, allowed units, and valid default policies for all 7 supported subtypes (`mechanics/pendulum`, `mechanics/projectile`, `optics/thin_lens`, `optics/spherical_mirror`, `optics/interface_refraction`, `optics/prism`, `circuits/dc_linear`).

4. **Auditable Explicit Policy Registry**:
   - 8 named, documented default policies (`policy_earth_gravity`, `policy_zero_damping`, `policy_standard_mass`, etc.). Every policy application records explicit provenance (`policy_id`, `policy_version`, `user_accepted`).

5. **Type-Safe Unit Normalization & Non-Invasive Spatial Calibration**:
   - SI unit parser validating dimensions, preventing string arithmetic, and normalizing values to SI standard units.
   - Evidence-based spatial scale derivation (`pixels_per_meter`) without ever touching native `source_px` coordinates.

6. **Deterministic Readiness Evaluation & Reversibility**:
   - `ReadinessEvaluator` deterministically checks the `READY_TO_COMPILE` invariant.
   - Reversibility: Deleting or modifying a resolution immediately invalidates readiness, reverting status to `NEEDS_REVIEW` and causing `PhysicsCompiler` to refuse compilation (`scene: null`).

---

## 1. Architecture Flow

```
SourceAsset (Bytes, Hash)
       │
       ▼
PageIR (Layout, OCR Candidates)
       │
       ▼
BookIR Semantic Analysis (Gemini VLM / MockVisionProvider)
       │
       ▼
PR-06 Perception & Visual Grounding (SAM 2, OpenCV, Multi-OCR)
       │
       ▼
BookIR [status: NEEDS_REVIEW] (Unresolved physical requirements, immutable evidence)
       │
       ▼
┌────────────────────────────────────────────────────────┐
│               PR-07 RESOLUTION LAYER                   │
│                                                        │
│  1. ResolutionAnalyzer (pure, non-mutating)            │
│     ├── Evaluates against ModelRequirementSpec         │
│     └── Identifies ReviewIssues & Candidates           │
│                                                        │
│  2. User Review / Explicit Policies                    │
│     ├── User input (validated & unit-normalized)       │
│     ├── Candidate confirmation/correction              │
│     └── Named policy application (PolicyRegistry)      │
│                                                        │
│  3. CalibrationEngine                                  │
│     └── Derives pixels_per_meter (preserves source_px) │
│                                                        │
│  4. ReadinessEvaluator (strict invariant)              │
│     └── BookIR transitions to READY_TO_COMPILE         │
└────────────────────────────────────────────────────────┘
       │
       ▼
PhysicsCompiler (compiles ONLY when status == READY_TO_COMPILE)
       │
       ▼
Canonical PR-02 PhysicsScene (status: READY, schemaVersion: "1.0")
```

---

## 2. Compiler Requirement Specifications

Machine-readable requirement contracts are defined in [requirements.py](file:///d:/AugmentedPhysics/ai/resolution/requirements.py) matching the canonical `PhysicsCompiler`:

| Domain | Subtype | Mandatory Simulation Parameters | Allowed Policies | Geometry Requirements |
| :--- | :--- | :--- | :--- | :--- |
| `mechanics` | `pendulum` | `pivot`, `bob_position`, `string_length_px`, `bob_radius_px`, `gravity`, `mass`, `damping`, `length` (or `pixels_per_meter`) | `policy_earth_gravity`, `policy_zero_damping`, `policy_standard_mass` | Point: `pivot`, Point: `bob_center`, `string_length_px`, `bob_radius_px` |
| `mechanics` | `projectile` | `launch_position`, `launch_speed`, `launch_angle_deg`, `gravity`, `pixels_per_meter`, `ball_radius_px` | `policy_earth_gravity` | Point: `launch_position`, `ball_radius_px` |
| `optics` | `thin_lens` | `lens_center`, `focal_length_px`, `aperture_height_px` (optional: `lens_type`) | `policy_standard_lens_aperture` | Point: `lens_center` |
| `optics` | `spherical_mirror` | `pole`, `focal_length_px`, `concavity`, `aperture_height_px` | `policy_standard_mirror_aperture` | Point: `pole` |
| `optics` | `interface_refraction` | `boundary_y`, `normal_x`, `n1`, `n2`, and one-of (`theta1`, `source_position`) | `policy_air_refractive_index`, `policy_water_refractive_index`, `policy_crown_glass_refractive_index` | Boundary line: `boundary_y`, Normal line: `normal_x` |
| `optics` | `prism` | `vertices`, `n`, `apex_angle_deg`, `ray_origin`, `ray_direction` | `policy_crown_glass_refractive_index` | Contour: `vertices`, Ray: `ray_origin`, `ray_direction` |
| `circuits` | `dc_linear` | `nodes`, `components` (valid circuit topology) | (None: no default resistances or voltages) | Component bounding boxes, wire paths |

---

## 3. Explicit Default Policy Registry

All policies are registered in [policies.py](file:///d:/AugmentedPhysics/ai/resolution/policies.py) with domain and subtype scoping to eliminate silent fabrication:

| Policy ID | Domain | Target Subtype | Target Parameter | Default Value | Physical Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `policy_earth_gravity` | `mechanics` | `None` (all mechanics) | `gravity` | $9.80665\,\text{m/s}^2$ | Standard terrestrial gravitational acceleration. |
| `policy_zero_damping` | `mechanics` | `pendulum` | `damping` | $0.0\,\text{s}^{-1}$ | Ideal undamped conservative motion assumption. |
| `policy_standard_mass` | `mechanics` | `pendulum` | `mass` | $1.0\,\text{kg}$ | Unit inertial test mass for kinematic models. |
| `policy_air_refractive_index` | `optics` | `None` (optics) | `n1` / `n` | $1.0003$ | Standard refractive index of air at STP. |
| `policy_water_refractive_index` | `optics` | `None` (optics) | `n2` / `n` | $1.333$ | Refractive index of pure water at $20^\circ\text{C}$. |
| `policy_crown_glass_refractive_index` | `optics` | `None` (optics) | `n` / `n2` | $1.52$ | Standard optical crown glass refractive index. |
| `policy_standard_lens_aperture` | `optics` | `thin_lens` | `aperture_height_px` | $200.0\,\text{px}$ | Standard visual lens aperture height. |
| `policy_standard_mirror_aperture` | `optics` | `spherical_mirror` | `aperture_height_px` | $200.0\,\text{px}$ | Standard visual spherical mirror aperture height. |

---

## 4. API Endpoints

The FastAPI backend (`apps/api/main.py`) exposes a coherent REST API for review, resolution, evaluation, and compilation:

- `POST /api/resolution/review`: Deterministically analyzes a grounded `BookIR`, returning all `ReviewIssue`s, candidates, and policies without mutating state.
- `POST /api/resolution/resolve`: Applies one or more `ResolutionDecision`s (user values, candidate confirmations, corrections, or policies) to `BookIR` and updates provenance.
- `POST /api/resolution/evaluate`: Evaluates compilation readiness, returning a structured `ReadinessReport` and setting `BookIR.status` to `READY_TO_COMPILE` if all invariants hold.
- `POST /api/resolution/compile`: Gated compile endpoint. Compiles `BookIR` into a canonical `PhysicsScene` only when `status == "READY_TO_COMPILE"`. Returns HTTP 400 with a detailed blocker report when compilation readiness is not met.
- `GET /api/ingest/health`: Reports pipeline version `PR-07` and lists active engines, policies, and supported grounder subtypes.

---

## 5. Verification & Test Suite Summary

- **Backend Pytest Suite:** All test suites passing (100% pass rate, 0 failed).
- **PR-07 Dedicated Tests:** Includes extensive unit, integration, and acceptance suites:
  - Unit tests: unit normalization, policy registry & domain scoping, resolution engine validation & rejection of unknown/out-of-range parameters, and readiness evaluation.
  - Integration tests: `/api/resolution/review`, `/api/resolution/resolve`, `/api/resolution/evaluate`, `/api/resolution/compile`.
  - Acceptance tests across all 7 domains: `test_pr07_all_domains.py` validates grounded BookIR resolution, policy application, calibration, readiness evaluation, and compiler execution for pendulum, projectile, thin lens, spherical mirror, interface refraction, prism, and DC linear circuit.
  - **Real Textbook Diagram E2E Acceptance:** `test_pr07_real_pendulum_e2e.py` runs full end-to-end perception from real textbook sketch (`pendulum_sketch_raw.png`), visual grounding (OpenCV/SAM 2), OCR candidate extraction, PR-07 review analysis, candidate confirmation, policy application, calibration derivation (`pixels_per_meter`), readiness evaluation, and compilation into a runnable canonical PhysicsScene.
- **Negative & Security Invariant Tests:**
  - Rejection of wrong-domain policies (optics policies rejected on pendulum, mechanics policies rejected on optics).
  - Filtering of unassigned subtype policies by domain (pendulum reviews never advertise air/water/glass optics policies).
  - Rejection of undeclared/unknown parameters (`UNKNOWN_PARAMETER_FOR_SUBTYPE`).
  - Strict enforcement of parameter ranges: projectile angle ($180^\circ$ rejected), prism apex angle ($250^\circ$ rejected).
  - Strict enforcement of categorical parameter domains: spherical mirror concavity (`banana` rejected).
  - Strict parameter-specific provenance: unrelated entity evidence references strictly forbidden from satisfying provenance for physical parameters (`gravity`, `mass`, etc.).
