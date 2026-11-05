# Phase 5 release-readiness audit

**Date:** 2026-10-11  
**Decision:** **NO-GO for a claim of fully automated simulation of all diagrams in the named domains.** This is a completed assessment of the available evidence, not completion of the Phase 5 release gate.

Phase 5 is defined in `AUTOMATION_FINDINGS_AND_REPAIR_PLAN.md` as qualification of a bounded, book-agnostic release claim after Phase 4. The system supports seven physical models in code; model support is not evidence that every photographed diagram of that model can be understood or safely simulated.

| Gate | Evidence now | Decision |
| --- | --- | --- |
| Offline image safety | 21-image mock-semantic corpus: 0 false-ready, 2 automatic scenes, 2 reviewed scenes; 23/25 annotated values, 12/12 landmarks, 6/6 targeted circuit graph checks. | Passed for this corpus only. |
| Browser student lifecycle | A real pendulum fixture passed reviewed upload through reset. A live user parallel circuit passed automatic readiness, explicit start, resistance exploration, Ohm-law current checks, BookIR immutability, and reset; the live open-switch upload remained in review. | Five subtype flows remain. |
| Browser runtime and registration | Four compiled real-image scenes started at two viewport sizes; 8/8 image/overlay rectangle checks passed. Evidenced inspection anchors are now used instead of hardcoded points. | Printed feature-to-overlay error remains unmeasured. |
| Independent numerical verification | Headless runtime checked pendulum energy, projectile trajectory, and Snell angle on emitted scenes; existing frontend solver suites pass. | Multiple browser parameter values and the remaining model families need independent cases. |
| Live semantic classifier | Initial automatic approval review rejected image transfer. The user then explicitly authorized sending the seven images to Gemini. The opt-in live audit ran: **7/7 correct domain/subtype pairs**, with the switch role identified in the open-switch image. Local grounding/compilation of those live semantic results produced **0 false-ready and 0 false-abstain cases**; the open switch remained review-gated and the valid parallel network compiled. | Passed on these seven supplied images; independent and stress-case accuracy remains unmeasured. |
| Circuit topology robustness | The user parallel network passed targeted graph checks. The user open-switch image remains review-gated when the semantic classifier identifies the switch. | Independent switch-gap and junction/crossing evidence is still missing. |
| Reproducible operation | Backend and production browser preview ran locally, with setup commands and observed CPU timing in `PHASE4_PROGRESS.md`. Python requirements are partly ranged rather than frozen. | Clean-environment reproducibility and dependency lock still need validation. |

## Why the decision is no-go

The release claim the user wants is that diagrams within the supported domains can be automatically converted to accurate simulations. The measured offline corpus has only two automatically ready scenes out of nineteen supported images. Most other cases correctly require evidence review. The new seven-image live semantic sample is encouraging but too small to establish broad accuracy; a missed switch on another image could still create a physically wrong graph. Feature-level overlay accuracy for all seven models has not been established. Claiming full automation now would exceed the evidence.

## Required work before changing the decision

1. Complete Phase 4's six remaining real-image browser lifecycles and feature-landmark comparisons; repair any failures while keeping ungrounded cases in review.
2. Expand the authorized live semantic sample beyond seven images, especially circuit switch gaps, wire crossings, low-resolution labels, and unsupported lookalikes. The opt-in `tests/acceptance/test_phase5_live_semantics.py` script has run on the seven user images with no key or raw provider output in the report. New external images need their own use and third-party-processing rights.
3. Add independent circuit switch, crossing, and graph cases plus broader rotated/crowded/low-resolution and unsupported images; require zero false-ready scenes on the release set.
4. Verify independent physics outputs at multiple values and record clean-environment install/model-cache steps and observed CPU latency.
5. Have code owners review the accumulated edits in high-collision and shared files before splitting work into bounded commits.

The seven user images were sent to Gemini only after explicit user authorization. No deployment, publication, or commit was performed as part of this audit.
