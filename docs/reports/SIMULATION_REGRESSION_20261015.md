# Simulation regression investigation — 2026-10-15

Status: local retry/error/review-flow fixes implemented; fresh live uploads remain blocked by the external vision provider. No claim of complete end-to-end recovery.

## Checkout and reproduction

The user reported previously working diagrams failing around commit 108. On inspection, HEAD was `f59652f` (108 reachable commits), with no tracked modifications. Reflog showed reconstruction commit `56cc340` followed by a reset to `f59652f`. The earlier Phase 1–3 working changes were absent. This investigation did not reset Git or restore the broad reconstruction commit.

Two direct uploads of the supplied prism to the running `/api/ingest` returned `unresolved`, null domain/subtype, and `VisionProviderError`. The recorded cause was Gemini **503 UNAVAILABLE / high demand** across the configured fallback sequence. No physics scene was produced. This failure occurs before CV grounding/compilation, so it is not evidence of a solver regression. It also does not establish the cause of every failure on the reverted commit.

An automated Chrome upload of the supplied convex lens reproduced an ERROR with null classification after the local API restart. Its visible workflow kept the uploaded image selected and enabled retry. The captured failure is local ignored output at `storage/generated/last_upload_failure.png`.

## Bounded changes

- Fixed the ineffective retry loop in `GeminiVisionProvider`: transient 502/503/504/unavailable errors now receive the existing second attempt before model fallback. Quota/missing-model errors switch models immediately; authorization failures stop. Attempts remain bounded. No canned classification, filename routing, fixture geometry, or solver fallback was added.
- `SimulationOrchestrator` distinguishes provider/configuration failures from an unrecognized diagram and clears stale review/readiness state when starting another upload.
- The upload UI opens the existing review dialog for `NEEDS_REVIEW` instead of ending with a generic interpretation failure. Provider/network error text is scrolled into view, and the selected image remains available for retry.
- The opt-in browser test now waits for the new document's load event after reload; previously it could see the old ready window and then call `reset()` on an undefined orchestrator. It also records actual UI errors and a screenshot before a domain assertion hides the failure.

No physics algorithms, CV detector thresholds, shared schemas, or API endpoints were modified. Changes are uncommitted.

## Verification and limits

| Check | Result |
| --- | --- |
| Offline provider retry + PR-05 pipeline/analyzer tests | 20 passed; mocked SDK calls, network disabled |
| Orchestrator regression | 32 assertions passed |
| Frontend suite | All 17 scripts passed |
| Production build | Passed; existing large-bundle warning |
| Chrome runtime matrix using earlier real-image compiled scenes | 8 scenes, 32 viewport checks passed |
| Fresh live HTTP prism upload | Failed twice at semantic provider: 503 UNAVAILABLE |
| Fresh Chrome lens upload | ERROR at semantic provider; no scene |

The eight runtime scenes cover the supplied lens, mirror, prism, both pendulums, parallel circuit, plus projectile and refraction. They use saved outputs from earlier real-image compilation and the actual current runtime; they do not prove current upload classification, printed-feature registration, or arbitrary-image accuracy. The open-switch figure was already review-gated in that earlier baseline and is not included among these eight successes.

The manual computer-use connection could not attach: browser discovery returned no browser, and the Windows helper reported `native pipe is unavailable`. Browser verification therefore used the repository's existing Chrome regression harness, not manual clicks. A test-produced screenshot was inspected. Manual end-to-end acceptance remains outstanding.

The identified non-reloading local API process was restarted to load the fix. A subsequent process inspection showed a separately restarted `uvicorn ... --reload` process on port 8000; that process was left running.

Ignored local evidence: `regression_prism_20261015.json`, `regression_prism_retry_20261015.json`, `regression_all_figures_runtime_20261015.log`, `regression_live_browser_20261015.log`, `regression_frontend_20261015.log`, and `regression_build_20261015.log` under `storage/generated/`.

Do not mark live simulation recovery or Phase 3 complete until the provider succeeds and the actual upload → review if needed → start → parameter interaction → reset flows pass. Do not treat the historical reconstruction progress report as the state of this reset checkout.
