# Circuit V2 repair baseline

Inspection completed before implementation on `main`, commit
`20f29e067021af90ad9c94c8f6fd2b3edf130337`.

The user's staged experiment/provenance changes, staged verified evaluator and
untracked 99-image report are preserved. No staging or commits are authorized.
Original status and both diffs are saved in the ignored directory
`outputs/circuit_v2_repair_20261106/` alongside test logs, XML and fresh baseline
results. Existing diagnostic directories are read-only inputs.

## Environment and models

- System Python 3.12.10; repository venv Python 3.12.11; Node 26.4.0.
- Venv torch 2.14.0+cpu, torchvision 0.29.0+cpu; CUDA unavailable.
- Installed dependencies captured in `dependencies.txt`.
- Circuit V2 checkpoint `runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt`
  SHA256 `95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46`.
  Real load and inference succeed. Classes: 0 resistor, 1 voltage_source,
  2 capacitor, 3 switch. Existing confidence threshold remains 0.25.
- SAM2 source `D:/AugmentedPhysics/sam2/sam2/__init__.py`; clean external
  checkout `2b90b9f5ceec907a1c18123530e92e794ad901a4`.
- Checkpoint `checkpoints/sam2.1_hiera_tiny.pt` exists (156008466 bytes).
  YAML `sam2/sam2/configs/sam2.1/sam2.1_hiera_t.yaml` targets
  `sam2.modeling.backbones.hieradet.Hiera`. Its direct import fails because
  `iopath` is missing. SAM2's own setup requires `iopath>=0.1.10`.
  Baseline `available()` incorrectly returns true without building the model.

## Source evidence and reference

Both requested DOCX reports were located and their full text/tables read.
Original rasters were visually inspected, along with their masks, graph and OCR
records. Neither case is reconstructed from a description.

| Case | Original image | Dimensions | SHA256 |
|---|---|---|---|
| C3 | `outputs/c3_pipeline_20261106/00_original.png` | 1536 × 1024 | `c76d6e931a337cb7786764dc1452ab2ca9f1a326908224282f8ecacc0a512346` |
| Series-parallel | `outputs/series_parallel_pipeline_20261106/00_original.png` | 403 × 178 | `30a0e9f48da206782234147846dbbbe4fd6c9f45b49b0c7145b57b8b4996b200` |

The complete series-parallel reference is available: R1=5 Ω, R2=3 Ω,
R3=6 Ω, R4=1 Ω, V1=12 V; R1 and R4 in series with R2||R3.
Independent reference: Req=8 Ω, source=1.5 A, R2=1 A, R3=0.5 A.

C3 has five resistors (4,6,4,8,12 Ω) and a 12 V source. The far-right
`cv_wire_51` shorts the rails. Ideal rejection is correct and must remain.
The five Ω-glyph CV candidates fail terminal attachment and are not components.

Fresh execution of the existing service factory and `run_experiment` with real
V2, local OCR/CV and attempted real SAM2 reproduced both reports: C3 retains six
components and `SHORTED_CIRCUIT_SOURCE`; series-parallel retains only three
unvalued resistors. SAM2 repeatedly fails during Hiera loading. Both return
`NEEDS_REVIEW`, scene=null. Existing previews invent different circuits.

## Baseline tests

Command (from repository root, venv Python):

```powershell
.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_circuit_grounding_repair.py tests/unit/test_circuit_v2_experiment.py tests/unit/test_circuit_generalization.py tests/unit/test_circuit_crossing_cv.py tests/unit/test_circuit_capacitor_pipeline.py tests/unit/test_circuit_asset_handoff.py tests/unit/test_circuit_dataset_generator.py tests/integration/test_circuit_v2_upload.py tests/integration/test_circuit_images.py tests/unit/test_pr06_segmentation.py -q --basetemp outputs/circuit_v2_repair_20261106/baseline_tmp --tb=short --junitxml outputs/circuit_v2_repair_20261106/baseline.xml
```

Result: **98 passed, 12 failed, 0 skipped**. All 12 failures are in
`test_circuit_generalization.py`: three supplied drawings, selected-component
resolution, four rotated/scaled variants, value tampering setup and three
observed-OCR cases. Names and failures are preserved in the log/XML. The upload
integration passes using real V2 plus canned OCR; this is not full real-provider
acceptance. The old image integration silently continues if images are absent;
its passing result alone is not evidence that all four images ran.

The initial run without `--basetemp` had 76 passed, 12 failed and 19 temp-fixture
errors due to Windows denying access to the default pytest temp directory.
Using a fresh workspace directory removes those errors without changing tests.

`npm.cmd test` ran all configured frontend suites; individual summaries report
zero assertion failures. PowerShell reported exit 1 while redirecting native
stderr, so the final run must capture the underlying process return code directly.

## Implementation stages

1. SAM2 readiness, dependency repair and real mask verification.
2. Measured component boundaries/plate geometry, OCR parsing/association and
   source-aligned graph evidence. Test before proceeding.
3. Separate validated non-ideal MNA route, explicit assumptions and qualitative
   fallback. Preserve canonical ideal rejection. Test before proceeding.
4. Laboratory mode controls and source-aligned backend telemetry/animation;
   real-image acceptance, frontend build and browser verification.

No stage is complete until its verification has run. Remaining baseline defects
must be explicitly distinguished from any introduced regressions.
