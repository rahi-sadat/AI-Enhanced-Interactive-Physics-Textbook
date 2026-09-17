# Contributing Guidelines

Thank you for contributing to the **AI-Enhanced-Interactive-Physics-Textbook** project!

---

## Code of Conduct & Contribution Standards

1. **Working Code First**: Never break existing simulations, solvers, or tests.
2. **Branching**: Always branch off `main` with a descriptive branch name (`feat/...` or `fix/...`). Never push directly to `main`.
3. **No Overwrites**: Do not resolve conflicts by overwriting teammate code. Consult `docs/TEAM_WORKFLOW.md`.
4. **Code Quality**:
   - Write self-documenting code with clear docstrings/comments.
   - Use meaningful variable names (e.g. `incidentRay`, `refractiveIndex`, not `r`, `n`).
   - Maintain physical parameter provenance when modifying diagram elements.
5. **Testing**:
   - Run existing unit tests before opening a pull request.
   - Add new tests in `tests/unit/` or `tests/integration/` when introducing new solver features.

---

## Local Development Setup

### Web Application (`apps/web`)
```bash
cd apps/web
npm install
npm run dev
```

### Python API & CV Pipeline (`apps/api`)
```bash
# In repository root
.venv\Scripts\activate
uvicorn apps.api.main:app --reload --port 8000
```
