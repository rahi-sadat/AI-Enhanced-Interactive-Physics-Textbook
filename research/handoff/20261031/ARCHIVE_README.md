# Historical research evidence

The archive preserves completed CV/OCR/physics debugging inputs, observations, arrays, browser screenshots and recorded outputs. Browser profiles, browser caches, credentials, virtual environments and installed packages are excluded.

Inspect the checked-in walkthrough reports without rerunning them. To restore the historical raw evidence to its original ignored paths, run:

```powershell
.\.venv\Scripts\python.exe scripts/verify_circuit_handoff.py --restore-research
```

The restorer checks the versioned archive hash, every entry hash, path boundaries and existing files before writing. Different local evidence is protected. Captured results are historical observations, not claims that the current checkout passes all old acceptance cases. See docs/TEAM_HANDOFF_20261031.md for current validation and model roles.
