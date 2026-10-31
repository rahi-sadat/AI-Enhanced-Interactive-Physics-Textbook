# Phase 2 corpus and benchmark report

**Date:** 2026-10-11  
**Status:** Phase 2 offline corpus and measurement exit criterion completed; live classification and browser registration remain unmeasured and are not release-approved.

**Post-repair update:** Phase 3 improved the same 21-image corpus to 23/25 values and 12/12 landmarks with zero false-ready scenes. See [Phase 3 repair verification](PHASE3_REPAIR_VERIFICATION.md). Figures below preserve the Phase 2 baseline for comparison.

## Final expanded-corpus result

The final run used **21 images**: 11 repository fixtures, three independently sourced public-domain diagrams, and seven user-provided challenge images. It passed the benchmark's readiness gate: **0 false-ready, 0 false-abstain, and 0 backend review/readiness disagreements** under `MockVisionProvider` expected semantic labels. There were **2 automatic scenes**, **2/2 attempted reviewed scenes**, **21/25 annotated numeric values** within tolerance, and **11/12 annotated source-pixel landmarks** within tolerance. All four emitted scenes loaded in headless `PhysicsRuntime`. The complete offline Python unit/acceptance suite passed **219 tests, 1 skipped**; the backend integration suite passed **24 tests**; `apps/web` `npm.cmd test` passed.

An added graph assertion on the user-provided parallel circuit passed **6/6** checks: the five component identities/types and the shared endpoint pair of R2/R3. This is a targeted topology check, not exhaustive junction/crossing validation.

| Model/class | Images | Automatic scenes | Value checks | Source-pixel points |
| --- | ---: | ---: | ---: | ---: |
| Pendulum | 5 | 0 | 2/3 | 6/6 |
| Projectile | 2 | 0 | 2/2 | 1/1 |
| Thin lens | 2 | 0 | 0/1 | 2/2 |
| Spherical mirror | 3 | 0 | 1/2 | 1/2 |
| Interface refraction | 1 | 1 | 4/4 | 1/1 |
| Prism | 2 | 0 | 3/3 | 0/0 |
| DC linear circuit | 4 | 1 | 9/10 | 0/0 |
| Non-physics / unsupported | 2 | 0 | 0/0 | 0/0 |
| **Total** | **21** | **2** | **21/25** | **11/12** |

This closes Phase 2's **measurement/reporting exit criterion**: corpus provenance, per-model denominators, tolerances, correct abstention, numerical runtime checks, known failure classes, and reproducible commands are recorded. It does not establish that arbitrary diagrams in a named domain will simulate. The sample is small and uneven, transformed/low-resolution/rotated/crowded cases are not systematic, and most supported diagrams still require review. Live classifier accuracy is unknown because no `GEMINI_API_KEY` is configured. Browser visual registration is a Phase 4 acceptance task. These are explicit release evidence gaps, not passing results. Phase 3 can now repair the measured grounding/topology failures against this benchmark.

## User-provided diagrams (2026-10-11)

Seven images supplied by the user were copied unchanged into `tests/fixtures/unseen/` and annotated in the manifest. They cover a convex lens, concave mirror, open-switch series circuit, prism, parallel resistor network, symbolic pendulum, and Bengali labeled pendulum. They are a useful challenge set, but their creation history is unknown, so independence from project development cannot be proven. The offline harness used expected semantic labels through `MockVisionProvider`; live VLM classification remains unmeasured.

| Image | Expected and observed result | Grounding result |
| --- | --- | --- |
| Convex lens | Needs review; no scene | Lens center within 2.3 px; printed 15 cm focal length was not promoted. |
| Concave mirror | Needs review; no scene | Printed 20 cm radius was promoted; pole missed by 167 px. |
| Series circuit with open switch | **Must not run; incorrectly compiled a scene** | 12 V, 10 ohm, 20 ohm read, but the emitted graph omitted the open switch and connected source plus resistors in a closed loop. This is a false-ready safety defect. |
| Prism | Needs review; no scene | 60 degree apex angle promoted; refractive index is not given. |
| Parallel resistor network | Ready; scene compiled | 12 V and all four resistor values promoted. Emitted graph had R1 and R4 in series with parallel R2/R3, matching the drawing. |
| Symbolic pendulum | Needs review; no scene | Pivot and bob within 19 and 4 px; physical length not stated. |
| Bengali pendulum | Needs review; no scene | 20 cm length and pivot/bob positions grounded; printed 30 degree initial angle was not promoted. |

Across these seven images, **11/13 annotated numeric values** and **5/6 source-pixel landmarks** passed the stated tolerances. One valid circuit auto-compiled; one open-switch circuit falsely auto-compiled; five correctly withheld a scene. Backend review analysis and readiness agreed in all seven cases. Both emitted circuit scenes loaded in headless `PhysicsRuntime`, but runtime loading does not validate diagram topology. The benchmark's first run exited nonzero for the open-switch false-ready result. Detailed ignored outputs are `storage/generated/phase2_user_circuits.json` and `storage/generated/phase2_user_noncircuits.json`.

The open-switch defect was repaired for images whose semantic classification identifies a switch. The circuit grounder now preserves that ungrounded semantic entity and readiness blocks compilation; a targeted rerun yielded **0 false-ready scenes** for the open-switch and parallel-network pair, while the valid parallel graph still compiled. A focused regression passed. This is a bounded guard: a live classifier that misses the switch can still allow the wrong topology, so independent switch detection and graph continuity remain release work. Lens focal-length OCR, mirror pole geometry, and Bengali initial-angle promotion are measured grounding repairs. Do not use these seven examples to claim general automatic coverage; no live classifier or browser overlay was measured.

## Independent corpus addition (2026-10-11)

Three diagrams created outside this project were added to the manifest and run through the same offline harness: a [pendulum](https://commons.wikimedia.org/wiki/File:Pendule_schematique.png), [projectile](https://commons.wikimedia.org/wiki/File:ProjectileMotion.jpg), and [concave mirror](https://commons.wikimedia.org/wiki/File:Concave_mirror.png). Their Commons description pages record public-domain author dedications. The fixture files are stored at their original resolution and the manifest records each source and license. These are independent of the repository's development fixtures, but cover only three of seven supported models and have no annotated numeric ground truth yet.

The targeted three-image run produced **0 automatic scenes, 0 false-ready scenes, and 0 readiness disagreements**. All three abstained as expected because the diagrams omit the physical values needed for an authoritative simulation. This is a safety result, not an automation success rate: `MockVisionProvider` still supplied their correct semantic labels. The Wikimedia download endpoint returned HTTP 429 when fetching a fourth diagram, so the corpus expansion stopped there rather than using an unverified source.

The isolated WSL test environment now has `iopath 0.1.10`. A targeted pendulum rerun with `PYTHONPATH=/mnt/d/AugmentedPhysics/sam2` no longer emitted the SAM2 model-loading failure, and its readiness result remained safe. This confirms that the missing dependency was repaired for that probe; segmentation mask quality and all-model SAM2 behavior remain unmeasured. `GEMINI_API_KEY` remains absent from the process environment, so live VLM classification is still untested.

## Corpus and method

The [manifest](../../tests/fixtures/unseen/phase2_manifest.json) identifies 11 repository images: nine examples spanning all seven implemented models, a landscape photo, and an unsupported wave diagram. The images include printed and hand-drawn examples and English and Bangla labels. Several were already used by acceptance tests, so this is **not an independent unseen holdout**. Four images can be generated by existing tests if absent. Origins and redistribution rights for legacy images have not been established. The set lacks systematic low-resolution, rotated, crowded, contradictory, and full-page examples.

The [Python harness](../../scripts/benchmark_phase2.py) reads local image bytes, creates `SourceAsset` and `PageIR`, injects expected semantic labels through `MockVisionProvider`, runs BookIR understanding, OCR/CV evidence extraction, the same `auto_resolve` step used by `/api/ingest`, backend readiness, and `PhysicsCompiler`. It records each image hash, status, blockers, grounded parameters, numerical and source-pixel errors, scene serialization, and CPU latency in ignored `storage/generated/phase2_benchmark.json`. A separate explicit-review path supplies approved parameters and policies for two incomplete images. The [JavaScript harness](../../scripts/benchmark_phase2_runtime.mjs) loads the actual emitted scenes into headless `PhysicsRuntime` and checks reference physics.

```bash
/home/torikul/augmentedphysics-audit-venv/bin/python scripts/benchmark_phase2.py
node scripts/benchmark_phase2_runtime.mjs
```

The Python command exits nonzero for a false-ready case, a false abstention against a positive expectation, a failed explicitly reviewed compilation, or a non-JSON scene. It records grounding accuracy misses in the JSON and report so one miss does not hide measurements from later cases. `--case ID` permits targeted reruns. No external VLM request is made by this offline benchmark.

## Results on the available images

| Expected class | Cases | Automatic ready | Assisted scene | Value checks | Source-pixel point checks |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pendulum | 2 | 0 | 1/1 reviewed | 1/1 | 2/2 |
| Projectile | 1 | 0 | 1/1 reviewed | 2/2 | 1/1 |
| Thin lens | 1 | 0 | none attempted | none annotated | 1/1 |
| Spherical mirror | 1 | 0 | none attempted | 0/1 | 1/1 |
| Interface refraction | 1 | 1 | no review needed | 4/4 | 1/1 |
| Prism | 1 | 0 | none attempted | 2/2 | none annotated |
| DC linear circuit | 2 | 0 | none attempted | 1/2 | none annotated |
| Non-physics / unsupported | 2 | 0 | not applicable | none annotated | none annotated |
| **Total** | **11** | **1** | **2/2 reviewed** | **10/12** | **6/6** |

The 10 cases expected to abstain produced no scene. The one expected automatic-ready refraction case compiled. There were **0 false-ready cases, 0 false abstentions, and 0 disagreements** between review analysis and backend readiness after the circuit readiness fix. The non-physics image retained `UNRESOLVED`; the wave diagram retained `UNSUPPORTED`. The values listed in the manifest include expected units, but this table measures numerical agreement after grounding; it is not a separate unit-label recognition score. Source-pixel points use the manifest's radial tolerances of 15–20 px, so 6/6 does not mean subpixel overlay registration.

### Measured grounding failures

- **Spherical mirror:** The diagram marks F about 132 px from the pole, but `focal_length_px` was not promoted. Pole location was within 20 px. Review is still required for focal length, concavity, and aperture.
- **Bengali circuit:** The diagram prints a 12 V source, but no `V1_voltage` was promoted and the grounded graph lacked a source. Its 10 Ω resistor value passed. The compiler and review analyzer now both block the incomplete circuit; the source symbol and connectivity remain an open perception/topology defect.
- **Prism and lens:** Their annotated index/apex or center checks passed, while required ray/vertex or focal/aperture facts remained unresolved. These cases abstained; the benchmark does not show that review can complete them.

### Compiled scene and runtime checks

All three emitted scenes were JSON serializable and loaded in headless JavaScript `PhysicsRuntime`:

| Image path | Review input | Runtime comparison |
| --- | --- | --- |
| Pendulum sketch | User supplied `0.8 m`; accepted gravity, mass, zero-damping policies | At 0.5 s, angle evolved; relative undamped energy drift `0.0000151` (limit `0.001`); reset restored time to zero. |
| Projectile scan | User supplied an exploratory scale of `100 px/m`; accepted Earth-gravity policy | At 0.5 s, position differed from the analytic trajectory by `0.000246 m` (axis limits `0.002 m`); reset restored time to zero. |
| Refraction scan | None; both indices, incident angle, and interface geometry grounded from the image | Refracted angle matched Snell's law within `0.01°`; measured difference `0°`. |

The projectile scale is a declared reviewer input, not evidence measured from its drawing. The optics solver is static, so time advancement is checked only for mechanics. These comparisons exercise three implemented models and do not prove numerical correctness for the remaining four or actual browser rendering.

## Environment and measurement limits

- The semantic classification and rough roles are supplied by `MockVisionProvider`. **Classification accuracy is unmeasured**, including the negative examples. `GEMINI_API_KEY` was absent, so gated live acceptance was not run.
- The initial baseline run did not execute SAM2 because `iopath` was absent. The isolated WSL environment now has `iopath 0.1.10`, and subsequent runs with the vendored SAM2 path did not emit that loading failure. Mask quality is still unmeasured.
- Fixture origins/rights and independence from development tests need verification. The 11-image corpus is too small and uneven for a generalization claim.
- Circuit graph correctness, browser Start Simulation and reset flows, source-overlay pixel error, multi-figure pages, and full end-to-end API behavior were not measured by this harness. Existing frontend unit tests cover runtime and coordinate contracts separately, but they do not substitute for these real-image checks.
- CPU image-processing times are single-run observations and include repeated OCR initialization; they are not throughput or service-latency estimates.

## Phase 2 exit decision and concrete remaining work

The original 11-image baseline below remains as historical evidence. The expanded 21-image result at the top is the current Phase 2 measurement decision. Phase 2's report exit criterion is met, while generalization, live classification, and browser alignment remain unverified. The current measured automatic-ready rate is **2/19 supported images**; **2/2 attempted assisted cases** reached a runtime. A claim that every diagram within a broad domain automatically simulates would be unsupported.

For release evidence, expand legally usable independent images across every model and negative class, with rotations, blur, crowded layouts, contradictory labels, and full pages. Run gated live semantic classification when a key is configured, quantify SAM2 masks, and collect browser overlay landmarks and API-to-runtime results. Keep grounding misses and any future false-ready result visible as Phase 3 repair findings.

## Verification

The final 11-case Python benchmark and three-scene JavaScript runtime check passed. The complete offline Python suite passed **218 tests, 1 skipped**; `apps/web` `npm.cmd test` passed. No solver or integrator was changed during this increment.
