# Automation audit: findings and repair plan

**Date:** 2026-10-11 (Asia/Dhaka)  
**Repository:** `D:\AugmentedPhysics`  
**Status:** Findings reflect the current, uncommitted working tree. Several edits predated this audit; see `git status` and `git diff` before changing or committing anything.

## Executive finding

The platform has a real ingestion, evidence, review, compilation, and simulation path, but it is **not fully automatic for every diagram in its existing domains**. A diagram can omit physical quantities, contain ambiguous connections, or represent a model outside the seven implemented subtypes. In those cases the correct behavior is `NEEDS_REVIEW` with no runnable scene. Calling such cases automatically simulated would require inventing physics.

The audit also found cases where the implementation crossed that boundary. A real Bengali circuit image was initially marked ready despite lacking a voltage source. An OCR `g` symbol could become a numerical gravity value without a measured number. Automatic resolution could imply user acceptance of assumptions. Those paths have been corrected in the current working tree and regression tested. This is a safety improvement, not proof of universal diagram support.

## Intended product contract and present scope

The project aims to turn textbook figures from any supported book into source-aligned, interactive physics simulations. The intended path is:

`upload → SourceAsset → PageIR → semantic BookIR → OCR/CV grounded evidence → readiness/review → PhysicsScene → explicit simulation start`

The VLM classifies meaning; classical OCR/CV and reviewed evidence provide physical values and geometry. Provenance must survive compilation. Student exploration changes the live scene, not the textbook evidence. The NCTB Bangla book is demonstration content, not a restriction on the platform.

The current implementation recognizes these **model subtypes**, rather than every possible diagram in their broad domains:

| Domain | Implemented subtype | What must be established before a faithful simulation |
| --- | --- | --- |
| Mechanics | `pendulum` | Geometry, physical length or scale, and applicable physical parameters or disclosed assumptions |
| Mechanics | `projectile` | Launch geometry and scale, numeric parameters or reviewed assumptions |
| Optics | `thin_lens` | Lens geometry, object/ray geometry, focal evidence and units |
| Optics | `spherical_mirror` | Mirror geometry, object/ray geometry, curvature/focal evidence and units |
| Optics | `interface_refraction` | Interface/ray geometry and refractive-index evidence |
| Optics | `prism` | Prism/ray geometry and refractive-index evidence |
| Circuits | `dc_linear` | Components, numerical ratings, source, and verified electrical connectivity |

An unlabeled image generally cannot determine an absolute length, voltage, resistance, focal length, or refractive index. Automation should therefore mean **automatic when evidence is sufficient; guided review when it is not; no fabricated scene**.

## What was exercised

The backend was run under WSL Python 3.12.3 with an isolated environment at `/home/torikul/augmentedphysics-audit-venv` and `USE_MOCK_VISION=1`. The health endpoint returned HTTP 200. The server was stopped after testing. Windows `python` was not on `PATH` in this environment; WSL worked. The mock vision provider is deterministic and classifies the live upload as a pendulum, so these runs do not measure real VLM classification accuracy.

| Check | Observed result | Interpretation |
| --- | --- | --- |
| Real pendulum sketch uploaded through backend | Mechanics/pendulum classification; CV supplied source-pixel geometry; result `NEEDS_REVIEW`, `scene: null` because physical length/scale was absent | Correct abstention on missing evidence |
| Same pendulum, reviewed through resolution API | User supplied length `0.8 m` and explicitly accepted earth-gravity, standard-mass, and zero-damping policies; compile returned `READY` with length `0.8 m` | Assisted end-to-end simulation works for this example |
| Real Bengali circuit fixture before correction | Only a `10 Ω` resistor was grounded, no source, yet readiness and compilation returned ready | Confirmed unsafe false-ready defect |
| Same circuit after correction | `NEEDS_REVIEW`, no scene | Missing source now blocks compilation |
| Synthetic two-component circuit | OCR originally consumed nearby resistor text and left source value missing; after quantity-aware association, source receives `12 V` and authentic end-to-end case passes | Specific OCR association defect fixed |
| Frontend tests | `npm.cmd test` passed | Existing JS test suite passed; this is not a visual browser acceptance test |
| Real-image PR-06 acceptance and safety regressions | 8 passed, 11 warnings | Includes six real-image fixtures; no live VLM |
| Multi-domain grounding and all-domain prepared-BookIR checks | 14 passed in one focused run | Exercises prepared inputs and grounding; not arbitrary uploads |
| PR-07 evaluator, policies, negative grounding, multi-domain grounding | 37 passed | Readiness and policy behavior passed focused checks |
| Safety regressions, all-domain acceptance, evaluator | 20 passed | Includes corrected projectile requirement behavior |
| Real pendulum end-to-end acceptance plus then-current safety regressions | 3 passed | Proves a reviewed path, not zero-review automation |

The suites above overlap; their counts must not be added into a unique total. A third safety regression was added after the initial 8-test run and was included in the later 20-test run. The tests use offline mocks as required by `AGENTS.md`; no Gemini key or live Gemini acceptance run was used.

## Findings register

### F1 — The universal automation claim exceeds the model and evidence boundary (critical, open)

The system supports seven named physical models, while a broad domain can contain many other diagrams. Even a matching subtype may omit values needed for an absolute simulation. The product should expose the distinction between automatically compiled, awaiting evidence/review, and unsupported. Do not convert uncertainty into hidden defaults.

### F2 — Missing circuit source could produce a runnable scene (critical, corrected locally)

The real Bengali fixture initially produced a resistor-only BookIR marked `READY_TO_COMPILE`; the compiler also returned `READY`. Circuit grounding and compiler gates now require a source, physical values, and valid referenced connectivity; shorted sources are rejected. This prevents the demonstrated false-ready case. Circuit topology verification still needs a broader audit: wire presence and two inferred nodes do not alone prove every junction, crossing, or closed path is electrically correct.

### F3 — OCR association could assign a component the wrong value (high, corrected locally)

The circuit grounder matched nearby OCR text without adequately separating voltage and resistance quantities. A resistor label could be consumed before the voltage source was assigned its value. Matching now respects physical quantity and does not consume another component's designator. More multi-component, multilingual, rotated, and crowded layouts are needed before claiming robust association.

### F4 — Resolution could misrepresent evidence or consent (high, corrected locally)

The prior automatic candidate path expected snake_case fields while serialized evidence used camelCase, so it was ineffective. More seriously, automatic policy application could set `user_accepted=True` even though the current policies require user opt-in. Automatic resolution now leaves raw OCR candidates for grounder verification/review and skips opt-in policies. Explicit user acceptance remains the route for missing physical parameters. Provenance must continue to distinguish OCR, diagram measurements, user corrections, and policy assumptions.

### F5 — Projectile readiness and compilation had an inconsistent contract (high, corrected locally)

The OCR symbol `g` could yield numerical `9.80665 m/s²` with OCR provenance despite no numeric OCR measurement. The grounder now promotes only a numeric OCR value. Projectile `pixels_per_meter` and `radius` are now required by readiness, matching compiler needs. Implicit numerical scale/radius fallbacks and confidence-derived scale were removed. This closes identified paths to a fabricated runnable projectile scene.

### F6 — Real upload evaluation is narrow (high, open)

The live upload check used one pendulum with mock semantic classification. Prepared-BookIR acceptance tests are useful for contracts but bypass real classification, page parsing, and some image ambiguity. There is no measured end-to-end success, abstention, numerical error, or pixel registration rate across unseen examples for all seven subtypes. Live Gemini acceptance is intentionally separate from offline CI and has not been established here.

### F7 — Full pages and multiple figures need an explicit product boundary (medium, open)

`PageIRBuilder` currently treats the uploaded image as one figure. A full textbook page with multiple diagrams or surrounding prose may therefore be mis-segmented. Either scope uploads to one cropped figure in the UI and documentation or implement page layout detection, figure selection, and per-figure provenance.

### F8 — Runtime and presentation need integrated verification (medium, open)

Successful Python compilation does not establish that every resulting scene simulates numerically correctly in the JS engine or overlays its source image accurately. The circuit MNA solver, other domain adapters, `CoordinateMapper`, explicit Start Simulation flow, reset, and evidence/exploration separation need browser-level checks using representative real fixtures.

### F9 — Setup and documentation lag the implementation (medium, open)

Windows Python was unavailable on `PATH`, while WSL setup required Python packaging dependencies and sizable CPU/model installations. Reproducible local setup and bounded model startup behavior need documentation. `PROJECT_CONTEXT.md` and `docs/ARCHITECTURE.md` contain PR status or endpoint descriptions that do not fully match the newer PR-06 through PR-08 state in `AGENTS.md`; reconcile them after implementation is verified.

## Changes already made in the working tree

These are uncommitted local changes made during the preceding audit and repair work, layered on a working tree that already had unrelated edits:

| File | Audit change |
| --- | --- |
| `ai/evidence/grounding/circuits.py` | Quantity-safe OCR matching; circuit readiness requires source, values, and verified connectivity |
| `ai/evidence/grounding/projectile.py` | A symbolic `g` does not become a numeric OCR value |
| `ai/ingestion/PhysicsCompiler.py` | Circuit source/value/connectivity gates; removed implicit projectile scale/radius fallbacks |
| `ai/resolution/engine.py` | Removed unsafe automatic candidate confirmation and automatic acceptance of opt-in policies |
| `ai/resolution/requirements.py` | Projectile readiness requires scale and radius |
| `tests/acceptance/test_pr06_real_unseen_acceptance.py` | Corrected circuit topology assertion to inspect geometry |
| `tests/unit/test_automatic_readiness_safety.py` | Added three targeted safety regressions |

The changes should be reviewed against the existing diff before any commit. No physics integrator or solver algorithm was intentionally rewritten.

## Repair plan

### Phase 1 — Establish an honest, enforceable readiness contract

1. Define a public capability matrix for the seven subtypes: required image evidence, allowed reviewed inputs, and explicit reasons for `NEEDS_REVIEW` or unsupported classification.
2. Make backend readiness and compiler requirements identical for every subtype. Add a contract test that feeds missing, ambiguous, and contradictory evidence to both and asserts no scene is produced.
3. Preserve `inferred`, `default`, `author_override`, and `diagram_measurement` provenance through BookIR, review responses, PhysicsScene, and runtime initialization. Keep opt-in policy acceptance explicit. Treat an assumption-based preview as exploration, clearly identified to the student.
4. Keep unknown or out-of-model diagrams at `scene: null`; surface useful review/unsupported reasons rather than a generic failure.

**Exit criterion:** Every invalid or underdetermined fixture abstains; every compiled scene has evidence or explicit reviewed assumption for each required physical value, with valid units and provenance.

### Phase 2 — Build a representative unseen-diagram corpus and measurement harness

1. Collect legally usable, book-neutral fixtures for each subtype: printed and hand-drawn, Bangla and English labels, high and low resolution, rotated/crowded layouts, missing values, contradictory text, and unsupported lookalikes. Keep fixture sources and expected facts documented.
2. Test the whole path from uploaded image through classification, grounding, review/readiness, compilation, JS simulation, and source-aligned rendering. Keep fast CI deterministic with `MockVisionProvider`; run gated live VLM acceptance separately when a key is configured.
3. Measure subtype classification, false-ready rate, correct abstention, OCR quantity/value accuracy, component/wire topology, parameter error with units, scene validity, simulation numerical error, overlay pixel error, and latency. Report per subtype and by fixture class, with denominators.
4. Add positive, negative, and ambiguity fixtures whenever a defect is found. Use separate integration tests for the full backend and browser rather than treating prepared-BookIR tests as image-to-simulation proof.

**Exit criterion:** A published benchmark report names the corpus, per-subtype pass rates, error tolerances, and known failure classes. False-ready cases are treated as release blockers.

### Phase 3 — Repair perception and topology where measurements fail

1. Strengthen OCR-to-entity association with units, quantity type, label identity, spatial relations, and conflict detection. Reject ambiguous assignments for review.
2. For circuits, validate actual graph continuity, source terminals, junction-versus-crossing decisions, parallel/series structure, and multi-component loops. Compare canonical compilation with the existing topology validator; preserve the working MNA algorithm.
3. Audit every subtype's geometry calibration, coordinate preservation, numerical units, and readiness/compiler agreement. Improve the responsible grounder or builder rather than patching generated output.
4. Decide whether full-page uploads are in scope. If yes, add figure segmentation/selection in PageIR and test multi-figure pages. If no, require a cropped single figure in the upload flow.

**Exit criterion:** The corpus failures are fixed or explicitly classified as review/unsupported, without adding hidden physical constants.

### Phase 4 — Verify the student experience and operate it reproducibly

1. Run browser end-to-end checks for each subtype: upload, review, compile, explicit start, parameter exploration, reset, and visual alignment on the source image.
2. Check runtime outputs against analytical or trusted reference cases at multiple parameter values. Confirm simulation changes do not mutate BookIR evidence.
3. Document WSL/Windows setup, pinned or bounded dependencies, offline test commands, model download/cache behavior, backend health semantics, and expected CPU latency. Keep live provider tests in `tests/acceptance/` behind `GEMINI_API_KEY`.
4. Reconcile architecture and project-context documentation with the verified implementation, then review the final diff with code owners for shared files before committing bounded changes.

**Exit criterion:** A new developer can reproduce backend and frontend acceptance checks; real fixture flows work in the browser; documentation states supported cases and measured limits.

**Progress (2026-10-11):** The real pendulum upload/review/compile/start/explore/reset/reopen flow now passes an asserting headless Chrome check. The compiled scene starts playback after loading; source image and overlay rectangles matched at the tested viewport. See `docs/reports/PHASE4_PROGRESS.md` for commands, environment, latency, and remaining six subtype/browser-alignment checks. Phase 4 remains open.

**Further progress (2026-10-11):** After explicit user authorization, a live Gemini plus browser test verified the open-switch circuit abstains and the valid parallel circuit compiles, starts, responds numerically to a resistance edit, preserves BookIR, and resets. The alignment inspector no longer displays hardcoded reticles. The five remaining model-family browser lifecycles and source-feature comparisons keep Phase 4 open; current details are in `PHASE4_PROGRESS.md`.

### Phase 5 — Qualify the bounded release claim

Phase 5 can collect release evidence while Phase 4 is in progress, but its exit gate cannot pass until Phase 4's seven-model browser and operational checks are complete. It is a release decision for the explicitly supported models, not a promise that every diagram in physics can be simulated.

1. Run an explicitly authorized live-classifier acceptance set, report per-subtype classification and failure cases, and keep credentials and raw provider data out of reports. A configured key alone does not authorize transfer of user images to a third-party service.
2. Expand the independent image corpus with switch gaps, wire crossings, crowded labels, rotated and low-resolution scans, contradictory values, missing calibration, and unsupported lookalikes. Any false-ready scene blocks release.
3. Freeze a reproducible environment and rerun backend, browser, numerical, provenance, and visual-landmark gates. Record the model versions, corpus identifiers, tolerances, denominators, and measured latency.
4. Publish a narrow capability statement naming the seven models, one-cropped-figure input, required review cases, and unsupported cases. Obtain code-owner review for shared-file changes before bounded commits.

**Exit criterion:** The seven real-fixture browser flows and numerical/landmark checks pass; the independent and authorized live sets have measured, acceptable classification accuracy with zero false-ready releases; a new developer can reproduce the results; the public claim matches those measurements. The [Phase 5 readiness audit](PHASE5_RELEASE_READINESS.md) currently records a **no-go** decision and open gates.

## Recommended immediate next work

Start with Phase 1's cross-subtype readiness/compiler parity test and Phase 2's fixture inventory. Those expose unsafe false-ready paths before broadening automatic behavior. Circuit graph validation and the seven browser flows should follow from the measured failures. Do not claim “all diagrams” until the supported model boundary and benchmark evidence support a narrower, testable claim.

## Phase 1 progress — 2026-10-11

Compilation now re-evaluates current BookIR readiness after checking the stored `READY_TO_COMPILE` status. A newly added regression removes the provenance of an otherwise usable pendulum length after the status was set to ready; compilation now returns `NEEDS_REVIEW` with no scene. The focused safety and seven-subtype acceptance run passed (14 tests).

The broader offline Python run produced **205 passed, 1 skipped, 2 failed**. One failure is the old PR-04 aggregate ingestion test: it constructs ready fixtures without the entities and provenance required by the newer PR-07 contract, so 23 of its embedded checks now disagree with the stricter gate. Those fixtures need migration to grounded/reviewed BookIR rather than weakening the gate. The other failure is an OCR benchmark whose token accuracy was exactly `0.40`, while its assertion requires greater than `0.40`; this is separate from the compiler change. Phase 1 remains in progress until the legacy fixture migration and cross-subtype negative contract matrix are complete.

**Next Phase 1 increment:** The PR-04 ready fixtures now include explicit synthetic review provenance and authoritative entity positions. Compiler validation still returns its specific missing-value, unit, and grounding errors before the final readiness recheck. In the seven-subtype acceptance suite, each valid scene is followed by missing required evidence and an ambiguous required visual entity; re-evaluation and compilation reject both despite the stored ready status. The affected suites passed (15 tests). The wider offline run before adding the missing-evidence assertions, deselecting only the independent OCR accuracy benchmark, passed: **207 passed, 1 skipped, 1 deselected**. The affected suites still passed after the new assertions. The OCR benchmark remains unresolved. Contradictory-evidence handling and comprehensive units/provenance parity are still needed to finish Phase 1.

**Contradiction and consent increment:** Readiness now rejects a parameter whose current value conflicts with its recorded resolution. It also rejects a policy resolution when its policy is unknown or a required opt-in acceptance is absent. Because compilation re-evaluates readiness, both cases return `NEEDS_REVIEW` with no scene even if BookIR retained a ready status. New safety regressions cover both cases. Focused readiness and seven-subtype suites: **31 passed**. Wider offline Python suite, deselecting only the previously failing OCR accuracy benchmark: **209 passed, 1 skipped, 1 deselected**. Remaining Phase 1 work includes unit normalization consistency, provenance checks beyond the tested resolved parameters, and the independent OCR benchmark investigation.

### Phase 1 completion check — 2026-10-11

The current named-model safety gate is complete for this phase. The compiler rechecks current readiness after its detailed grounding and parameter validation; seven-subtype prepared-BookIR acceptance cases now reject missing required evidence and ambiguous required entities. Readiness rejects stale resolution conflicts, non-finite or dimensionally invalid required values, and unaccepted opt-in policies. Compilation preserves known parameter provenance in emitted scene parameters instead of relabeling user-supplied and policy values as observed or assumed. Lens compilation no longer derives an object height or distance from aperture or focal length when object evidence is incomplete. Refraction converts a supplied radian incident angle to degrees; circuit source and resistance units are validated and normalized in a scene copy, leaving BookIR evidence unchanged.

The OCR benchmark failure was due to tiny fallback text rendering under WSL when Windows font paths were unavailable. The test now finds full-size Latin and Bengali fonts on either Windows or WSL and skips if those fonts are unavailable. With the available WSL-mounted fonts, the real local OCR benchmark passed. Final verification: **216 passed, 1 skipped** in the complete offline Python unit and acceptance suite; `apps/web` `npm.cmd test` passed. The one skipped test was not needed for the current gate. The real pendulum acceptance test also passed after the evaluator was taught to read typed `PhysicalValue` objects.

This Phase 1 result establishes the tested safety contract for the implemented models. It does not establish image-to-simulation accuracy for arbitrary diagrams, full circuit graph correctness, multi-figure page handling, or browser visual registration. Those remain Phase 2 through Phase 4 work.

### Phase 2 baseline — 2026-10-11

The offline benchmark now follows the API order from image bytes through grounding, `auto_resolve`, readiness, and compilation. It covers 11 repository images: nine across the seven named models, one non-physics image, and one unsupported wave diagram. Expected semantic labels are injected through `MockVisionProvider`; live classification remains unmeasured. After correcting the refraction grounder and incident-angle alias, one refraction image compiled automatically without a user value. Eight other supported images abstained, as did both negatives. Two explicitly reviewed images (pendulum and projectile) compiled and ran in the headless JS runtime. The final measurement found **0 false-ready, 0 false abstentions, 10/12 numerical value checks, 6/6 source-pixel point checks, and 3/3 JSON scenes loaded in JS**. The two misses were a mirror focal marker and a Bengali circuit source voltage. Review analysis now blocks a resistor-only circuit, matching the compiler's safety gate.

That initial 11-image result is superseded by the 21-image run in [PHASE2_BASELINE.md](PHASE2_BASELINE.md). Phase 2's offline measurement/reporting exit criterion is complete: 0 false-ready scenes under supplied semantic labels, 2 automatic scenes, 2/2 reviewed scenes, 21/25 value checks, and 11/12 source-pixel landmarks. The user-provided open-switch circuit initially compiled incorrectly; preserving its semantic switch and blocking ungrounded switch topology fixed that case in the benchmark. The full offline Python unit/acceptance suite passed 219 tests, 1 skipped; backend integration passed 24; frontend tests passed. Live classifier accuracy, broader independent coverage, and browser registration remain release evidence gaps and are not represented as passing results. Phase 3 should repair the measured lens, mirror, pendulum-angle, circuit OCR, and topology limitations without changing working solvers.

### Phase 3 measured-corpus repair — 2026-10-11

The [Phase 3 verification report](PHASE3_REPAIR_VERIFICATION.md) records the repairs and review decisions. The lens's printed focal length, Bengali pendulum angle, and both annotated mirror poles now pass. The legacy Bengali circuit's low-confidence voltage text cannot prove a source symbol and remains in review; the open-switch diagram remains in review; the valid parallel network passes graph and electrical validator checks. The upload UI now asks for one cropped diagram because full-page figure selection is not implemented. The final 21-image rerun has 0 false-ready scenes, 23/25 value checks, 12/12 landmarks, 6/6 targeted circuit graph checks, and 4/4 emitted scenes loaded in headless runtime. Python unit, acceptance, and integration tests: 245 passed, 1 skipped; frontend tests passed. Phase 3's corpus-failure exit criterion is met, with general topology, live classification, and browser overlay still outside the verified release claim.
