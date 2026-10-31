# Phase 3 repair and verification

**Date:** 2026-10-11  
**Scope:** Repair measured Phase 2 grounding and topology defects without changing physics solvers.

## Changes and image evidence

| Finding | Repair or decision | Direct image check |
| --- | --- | --- |
| Convex lens `f = 15 cm` visible but missing | Thin-lens grounder now accepts the parser's explicit `focal_length` quantity as well as a generic length. The value retains OCR provenance and converts to metres. | User lens: `0.15 m` promoted; no false-ready scene. |
| Bengali pendulum `θ=30°` visible but missing | OCR router keeps a high-confidence explicit physics expression when an overlapping Bengali OCR reading has low confidence. Both readings remain available as alternatives. | User pendulum: `30°` promoted; no false-ready scene. |
| Mirror pole about 167 px from the marked point | Mirror CV distinguishes the principal axis from long reflected rays and searches for a supported near-vertical mirror stroke at the axis when the arc is split by crossings. | User mirror pole error 7.3 px; legacy mirror pole error 6.3 px. Both remain review-gated. |
| Bengali circuit `12 V` absent from graph | The OCR router retains a low-confidence `১২ V` candidate, but CV does not verify a source symbol and terminals. The analyzer correctly requires review. No voltage source is fabricated from text alone. | Legacy circuit remains `NEEDS_REVIEW`, scene null. |
| Open switch compiled as closed loop | The Phase 2 repair preserves semantic switch entities and blocks an ungrounded switch state. This remains dependent on semantic switch detection. | User open-switch image remains `NEEDS_REVIEW`, scene null. |
| Parallel resistor topology | Kept the working topology extraction and solvers. The emitted circuit has R1 and R4 in series with parallel R2/R3. | Six graph assertions pass; the existing electrical topology validator returns `valid=True`, `mode=precision`, no diagnostics. |

The existing topology validator checks electrical graph consistency. It cannot prove that a graph matches every symbol and crossing in the source image. The open-switch case demonstrated that limitation, so semantic or visual evidence must still gate topology before compilation. No MNA solver or integrator was changed.

## Upload scope

`PageIRBuilder` treats one uploaded image as one figure. Full textbook pages with multiple figures are outside the verified input contract. The upload dialog now asks for **one cropped diagram** and names the supported model families. Figure segmentation and automatic selection would be a separate feature with its own corpus and provenance tests.

## Remaining limits for release

- Live VLM classification is unmeasured without a configured key. A missed switch can still evade the semantic switch guard; independent visual switch and wire-gap detection is needed before claiming general circuit automation.
- The sample does not establish robust junction-versus-crossing handling, arbitrary series/parallel networks, or multi-component loops. Ambiguous or ungrounded cases must remain in review.
- The lens, mirror, and pendulum examples still lack other verified inputs or accepted policies needed for automatic scenes. Recovery of one printed value does not imply simulation readiness.
- Browser overlay registration and full student flows are Phase 4 acceptance work.

## Final verification and exit decision

The final 21-image benchmark passed its safety gate: **0 false-ready, 0 false-abstain, 0 readiness disagreements**, **2 automatic scenes**, and **2/2 reviewed scenes**. Annotated accuracy improved from Phase 2's **21/25 values and 11/12 landmarks** to **23/25 values and 12/12 landmarks**. The user lens focal length, Bengali pendulum angle, and both old and new mirror pole landmarks now pass. The parallel resistor case passes **6/6 graph assertions**. All four emitted scenes load in headless `PhysicsRuntime`; mechanics and refraction reference comparisons remain within their Phase 2 tolerances.

The two remaining numeric misses are the legacy mirror's focal marker distance and the legacy Bengali circuit's 12 V source. Neither produced a scene. The mirror still needs focal/aperture/concavity review, and the circuit still needs visual source and connectivity review. The open-switch diagram also remains review-gated. Thus every observed corpus failure is either repaired or explicitly classified as review, with no hidden physical constant inserted. **Phase 3's measured-corpus exit criterion is met.**

Complete offline Python unit, acceptance, and API integration suite: **245 passed, 1 skipped**. Frontend `npm.cmd test` passed. New deterministic OCR tests: **2 passed**. The backend was not deployed; generated benchmark JSON remains ignored runtime output.

The result does not prove general automation for arbitrary diagrams. Missing live classifier accuracy, independent switch/wire-gap detection, broader network topology coverage, full-page figure selection, and measured browser alignment remain release limitations. Phase 4 should verify the student flow and overlay against actual source images, while future corpus growth should test these unsupported or ambiguous classes explicitly.
