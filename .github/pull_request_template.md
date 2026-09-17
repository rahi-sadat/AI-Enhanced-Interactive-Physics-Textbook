## Pull Request Description

### Summary of Changes
<!-- Provide a clear, concise summary of what this PR introduces or fixes. -->

### Domain / Area Affected
- [ ] `apps/web` (Frontend application, features, UI)
- [ ] `apps/api` (Backend HTTP API)
- [ ] `engine/mechanics` (Mechanics simulation engine)
- [ ] `engine/optics` (Optics simulation engine)
- [ ] `engine/circuits` (Circuits simulation engine)
- [ ] `engine/core` (Shared simulation runtime infrastructure)
- [ ] `ai/perception` (Computer vision, SAM 2, geometry extraction)
- [ ] `ai/document_intelligence` (OCR, parameter parsing)
- [ ] `shared/schemas` (Canonical schemas & contracts)
- [ ] `content` (Textbook content & assets)
- [ ] `research` / `tests` / `docs`

---

## Pre-Merge Quality & Non-Collision Checklist

Please confirm all checks before requesting review:

- [ ] **Single Bounded Task**: This PR addresses one specific, bounded task only.
- [ ] **Synced with Main**: Rebased on latest `origin/main` (`git fetch origin && git rebase origin/main`).
- [ ] **Diff Reviewed**: Self-reviewed the full diff (`git diff origin/main...HEAD`) and verified no unintended changes.
- [ ] **No Overwriting Teammate Work**: Verified that no teammate changes were inadvertently dropped or reverted.
- [ ] **Zero Unintended Logic Changes**: Verified that working physics solvers, formulas, or constants were not modified.
- [ ] **Tests Pass Locally**:
  - [ ] Frontend & JS engine tests (`npm test` in `apps/web`)
  - [ ] Python unit & integration tests (`unittest discover`)
- [ ] **No Runtime Bloat**: Confirmed that temporary uploads, caches, models, or generated artifacts are NOT committed.
- [ ] **Shared Boundary Coordination**: Any modification to `engine/core/`, `shared/schemas/`, or `apps/api/main.py` was coordinated with the relevant code owner.
