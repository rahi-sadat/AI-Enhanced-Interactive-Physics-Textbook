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
- [ ] Preserved all existing comments, docstrings, and parameter provenance.
