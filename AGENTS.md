# Agent Operational Guidelines & Repository Rules

This document establishes mandatory rules for AI coding assistants (including Antigravity, Claude Code, GitHub Copilot, Codex, and others) working in the `AI-Enhanced-Interactive-Physics-Textbook` repository.

---

## 1. Core Principles

1. **Read Context First**: Always read `PROJECT_CONTEXT.md` and `docs/ARCHITECTURE.md` before making architectural or cross-module changes.
2. **Book-Agnostic Platform**: The system is designed as a book-agnostic AI-enhanced physics textbook and learning platform. Never hardcode our demonstration book (NCTB Bangla Physics) as the sole supported book. Generic solvers must remain book-neutral.
3. **Preserve Physics Algorithms**: Do NOT rewrite working physics algorithms, numerical integrators, or simulation logic during feature development, UI changes, or refactoring. Existing working physics must remain working.
4. **No Silent Overwrites**: Never resolve merge conflicts or discrepancies by blindly copying an entire file or discarding teammate changes. Inspect Git history with `git log` and `git blame` first.
5. **Inspect Diff Before & After**: Run `git status` and `git diff` before and after every modification to verify that only intended files and lines were touched.
6. **Feature Isolation & Bounded Scope**: Work only within the domain of the assigned task (e.g., modifying `apps/web/src/features/` should not touch `engine/optics/` unless explicitly required).
7. **Small, Atomic Commits**: Keep commits small, well-described, and bounded to one task. Avoid cross-domain megapacks.
8. **Shared Engine Review Required**: Changes to `engine/core/`, `shared/schemas/`, or `apps/api/main.py` require explicit justification and coordination with code owners.
9. **Never Commit Runtime Data**: Never commit runtime user uploads (`storage/uploads/*`), generated temporary files (`storage/generated/*`), or cache. Check `.gitignore`.
10. **Preserve Parameter Provenance**: Never strip provenance metadata (`inferred`, `default`, `author_override`, `diagram_measurement`). Physical values must retain their evidentiary source.
11. **Edit Source, Not Generated Artifacts**: If a file is generated from a script, template, or perception pipeline, modify the generator rather than patching the output artifact directly.
12. **Stable Domain Boundaries**: New physics domains (e.g., waves, thermodynamics, electromagnetism) must integrate through independent modules under `engine/<domain>/` and register with `engine/core/sceneRouter.js` rather than modifying existing solvers.
13. **High-Collision File Coordination**: High-collision files (`apps/web/src/main.js`, `apps/web/index.html`, `apps/web/src/style.css`, `engine/core/sceneRouter.js`, `apps/api/main.py`) follow a single-writer policy. Inspect recent Git history before modifying them.
14. **Multimodal VLM Boundaries & Zero Parameter Fabrication**: VLMs (such as Google Gemini) are purely semantic classifiers. They categorize `classification`, `isPhysics`, `domain`, `subtype`, and rough entity taxonomy with coarse bounding boxes isolated in `attributes["vlmApproxBBox"]`. VLMs must **never** fabricate numerical physics parameters (mass, resistance, voltage, focal length, refractive index) or authoritative visual coordinates (`position_source_px = None`, `geometry = None`). Downstream compilers must return `NEEDS_REVIEW` with `scene: null` until verified classical CV/OCR grounding (PR-06+) is active.
15. **Strict Schema Invariants & Subtype Purity**: Subtypes must strictly correspond to physical models (`pendulum`, `projectile`, `thin_lens`, `spherical_mirror`, `interface_refraction`, `prism`, `dc_linear`). Non-physics or unsupported status flags belong in `classification` and must force `domain = null` and `subtype = null`. `isPhysics` must be a native JSON boolean (or `null`). Confidence scores must be finite numbers in $[0.0, 1.0]$, defaulting conservatively to `0.0`. Entity IDs in relationships must resolve to valid declared entities.
16. **Offline Test Isolation & Mock Providers**: Automated CI/CD, unit tests, and regression tests MUST use `MockVisionProvider` with deterministic canned responses and zero external network/API calls. Live VLM tests (e.g. `GeminiVisionProvider`) must be placed in `tests/acceptance/`, gated by `GEMINI_API_KEY` presence and isolated from fast test suites. Never log API credentials. Support multi-model fallback (`gemini-3.1-flash-lite`, `gemini-3-flash-preview`) to handle Google GenAI rate limits.
17. **Async Event Loop Offloading for Blocking I/O**: Heavy synchronous operations (such as external VLM HTTP requests, OpenCV/scikit-image perception, or MNA matrix inversions) invoked from within FastAPI async route handlers must be offloaded using `await asyncio.to_thread(...)` to ensure the server's async event loop remains unblocked and responsive.

---

## 2. Directory Navigation Quick Reference

| To modify... | Look in... |
| :--- | :--- |
| Active web frontend, UI layouts, controls | `apps/web/src/` |
| Web feature modules (book, tutor, exams) | `apps/web/src/features/` |
| Backend API endpoints & server bootstrap | `apps/api/` |
| Mechanics / Kinematics physics solvers | `engine/mechanics/` |
| Optics ray tracing & optical formulas | `engine/optics/` |
| Circuit MNA matrix & topology solvers | `engine/circuits/` |
| Common physics runtime & coordinates | `engine/core/` |
| Diagram CV, segmentation, SAM 2 | `ai/perception/` |
| OCR, text detection, parameter binding | `ai/document_intelligence/` |
| Real-file ingestion, SourceAsset, PageIR, VLM providers | `ai/ingestion/` |
| Canonical PhysicsCompiler (BookIR -> PhysicsScene) | `ai/scene_compiler/physics_compiler.py` |
| Canonical scene builders & adapters | `ai/scene_compiler/` |
| Shared schemas, models, contracts | `shared/schemas/` |
| Demo textbook assets & curriculum | `content/demo-books/` |
| Research experiments & paper evaluation | `research/` |
| Automated unit & integration tests | `tests/` |

---

## 3. Git Collaboration Checklist for Agents

Before completing any task or proposing changes:
- [ ] Checked `git status` to ensure no stray or generated files are staged.
- [ ] Verified that existing tests pass (`apps/web` tests, Python unit tests).
- [ ] Confirmed zero unexpected logic changes in working physics.
- [ ] Confirmed zero parameter fabrication (VLM never populates physical constants or coordinates).
- [ ] Verified strict schema invariants and subtype purity (domain-subtype pairing, finite confidence).
- [ ] Ensured unit tests run with offline mocks (`MockVisionProvider`) and no external network calls.
- [ ] Preserved all existing comments, docstrings, and parameter provenance.
- [ ] Confirmed VLM confidence values are never 1.0 (cap: isPhysics ≤ 0.99, domain ≤ 0.98, subtype ≤ 0.96, overall ≤ 0.98).

---

## 4. Completed PR Milestones (Current Architecture State)

| PR | Status | Summary |
| :--- | :--- | :--- |
| PR-01 | ✅ | Strict audit and anti-fabrication invariants. No auto-path may generate runnable physics from missing evidence. |
| PR-02 | ✅ | Canonical PhysicsScene schema v1.0, PhysicsRuntime, SolverRegistry, multi-domain validation. |
| PR-03 | ✅ | Source-aligned rendering, RendererRegistry, SimulationCapabilityRegistry, bidirectional manipulation. |
| PR-04 | ✅ | Real upload ingestion: `SourceAsset → PageIR → BookIR`. Gate Zero anti-fabrication UI. 36 tests. |
| PR-05 | ✅ | Multimodal VLM semantic understanding (Gemini). Calibrated confidence, enriched roles, debug metadata, asserted acceptance test. |
| PR-06 | 🔄 | Classical CV + OCR parameter grounding. SAM 2 geometry, Tesseract OCR, spatial-semantic parameter binding. |
| PR-07 | 🔄 | End-to-end simulation bootstrapping: PR-05 + PR-06 → `BookIR(RESOLVED)` → runnable PhysicsScene. |

### PR-05 Active Boundary (CRITICAL — Do Not Cross Until PR-06)

```
VLM Output Boundary                CV/OCR Grounding Boundary (PR-06+)
-----------------------            -----------------------------------
classification       ✅            position_source_px          ❌ (null)
isPhysics            ✅            geometry                     ❌ (null)
domain               ✅            parameters (numeric)         ❌ (empty {})
subtype              ✅
confidence (0–0.99)  ✅
entities (coarse)    ✅ → quarantined in vlmApproxBBox only
visibleLabels        ✅ → verified=False only (unverified evidence)
```

- `BookIR.status` **must** remain `UNRESOLVED` at end of PR-05 pipeline.
- `PhysicsCompiler` **must** return `status="NEEDS_REVIEW"` with `scene=null`.
- Any agent that sets `BookIR.status = RESOLVED` or populates `position_source_px` from VLM output is violating the PR-05 boundary.
