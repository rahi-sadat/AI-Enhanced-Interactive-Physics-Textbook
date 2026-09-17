# Team Git Workflow & Collision Prevention Guide

This document defines the mandatory collaboration protocol for all developers working on `AI-Enhanced-Interactive-Physics-Textbook`.

---

## 1. The Team Collision Problem & How We Solve It

### The Problem
Previously, two developers could concurrently modify the same file from different bases. When pushing, one developer's legitimate work could be overwritten, dropped, or corrupted by improper conflict resolution.

### The Solution: 5 Golden Rules
1. **Never develop directly on `main`**. `main` is the shared, stable source of truth.
2. **One branch = one bounded task**. Branches are short-lived (hours or days, never weeks).
3. **Always sync before starting work**.
4. **Always rebase on latest `origin/main` before opening or merging a PR**.
5. **Enforce single-writer policy on high-collision files**.

---

## 2. Daily Developer Workflow

### Step 1: Starting a New Task
Always branch from the latest updated `main`:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feat/<area>-<short-description>
```

Branch naming conventions:
- `feat/mechanics-pendulum-damping`
- `feat/optics-chromatic-dispersion`
- `feat/circuits-ac-sinusoidal`
- `feat/book-chapter-navigator`
- `feat/exam-quiz-timer`
- `fix/coordinate-mapping-aspect`

Avoid ambiguous branch names like `rahi-work`, `new-changes`, `final-test`.

### Step 2: Working on Your Branch
- Keep commits small, atomic, and well-described.
- Only edit files in your assigned domain.
- Do NOT reformat unrelated files or touch files outside your scope.
- Periodically check `git status` and `git diff`.

### Step 3: Preparing Your Pull Request
Before opening a PR or pushing your final commits:

```bash
# 1. Fetch latest changes from origin
git fetch origin

# 2. Rebase your feature branch on origin/main
git rebase origin/main

# 3. Inspect your full diff against main
git diff origin/main...HEAD

# 4. Run automated tests to verify zero regression
npm test          # In apps/web
python -m unittest # In repository root

# 5. Push your feature branch
git push -u origin feat/<area>-<short-description>
```

If you previously pushed your branch and need to update after rebasing:
```bash
git push --force-with-lease
```
**NEVER** use `git push --force` or force-push to `main`.

---

## 3. High-Collision / Shared File Policy

The following files are identified as high-collision areas because multiple features interact with them:

| High-Collision File | Purpose | Rule |
| :--- | :--- | :--- |
| `apps/web/src/main.js` | Web application bootstrap & scene switching | Single-writer per task. Coordinate before structural changes. |
| `apps/web/index.html` | Stage layout, sidebar containers | Use independent feature sub-containers. |
| `apps/web/src/style.css` | Global styles & layout variables | Do not override global element tags; use scoped feature classes. |
| `engine/core/sceneRouter.js` | Physics domain dispatcher | Additive registrations only. Do not rewrite domain resolution. |
| `engine/core/coordinateMapper.js` | Shared coordinate transform | Requires explicit review from both code owners. |
| `apps/api/main.py` | FastAPI application bootstrap | Use `apps/api/modules/` routers rather than appending to `main.py`. |
| `shared/schemas/` | Canonical JSON schemas & models | Schema additions must be backwards-compatible. |

### Single-Writer Rule:
Only **one** open PR should modify the structure of a high-collision file at a time. If Developer A is modifying `sceneRouter.js`, Developer B waits for Developer A's PR to merge before rebasing and registering their solver.

---

## 4. Recommended GitHub Main-Branch Protection Settings

Repository administrators should configure the following rules for the `main` branch under **Repository Settings -> Branches -> Branch protection rules**:

- [x] **Require a pull request before merging**
  - Require approvals: `1`
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners (`.github/CODEOWNERS`)
- [x] **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Pass CI test suite (Frontend build, JS unit tests, Python unit tests)
- [x] **Require conversation resolution before merging**
- [x] **Do not allow bypassing the above settings**
- [x] **Block force pushes** (applies to everyone, including administrators)
- [x] **Block branch deletions**
- [x] **Merge method**: Prefer *Squash and merge* for small feature PRs to keep `main` history linear and clean.
- [x] **Automatically delete head branches**: Enable auto-deletion of merged feature branches.
