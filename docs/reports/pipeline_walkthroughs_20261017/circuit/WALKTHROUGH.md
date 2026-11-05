# Series DC circuit: complete component-by-component debugging walkthrough

Trace ID: `TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017`. These documents use the existing live native Windows request from 2026-10-17. No models, detectors or solvers were rerun while writing them. No production fixes were made.

Source reference: A 12 V battery with polarity marks, an OPEN switch S, R1=10 Ω on the top branch, R2=20 Ω on the right vertical branch, connecting wires and a current-direction annotation.

Known and unknown evidence: 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

Expected geometry for this diagram: Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

Expected initial simulation: Compilation should remain blocked while topology/switch state is ungrounded. A hypothetical corrected ideal open-switch model would have no conducting loop, but that is not a solver output from this trace. Do not present a closed-switch 0.4 A result as actual output.

Exact expected coordinates/masks are unavailable: EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS. Expected behavior below is a contract or a qualitative source comparison, never a hand-drawn expected result.

![Unchanged original diagram](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/00_source/original.png)

## How to read this document

Follow stages 01–34 in order. Every stage has actual input, expected input, actual output, expected output, verdict and downstream handoff. Summaries show selected recorded fields; the complete input/output bundle and original raw files remain linked. Empty/undefined returns are not automatically errors: in-place mutations and resulting state are shown separately.

The order is logical data flow. Parent call entry timestamps precede nested work; their outputs are explained only after that work. Repeated readiness/resolution calls remain distinct in stage bundles. Startup/demo frontend events before this request are excluded.

## Pipeline map

01 Browser selects the original diagram → 02 HTTP request reaches /api/ingest → 03 Upload persistence and dimension decoding → 04 PageIR / whole-figure coordinate frame → 05 Actual Gemini request and response → 06 Semantic validation, confidence caps and thresholds → 07 Initial semantic BookIR → 08 Evidence dispatch and source decode → 09 RapidOCR: first text/box observations → 10 EasyOCR: independent OCR candidates → 11 Symbol candidates, deduplication and final OCR → 12 Grayscale, blur and edge extraction → 13 OCR-region suppression before geometry detection → 14 Domain CV: raw candidates → selected geometry → 15 SAM2 segmentation prompted by CV → 16 Semantic-to-spatial grounding and parameter binding → 17 Grounded BookIR and OCR-enriched PageIR → 18 Enforce authoritative source dimensions → 19 Automatic resolution and explicit policy values → 20 Resolution decisions, units and calibration → 21 Requirement and ambiguity analysis → 22 Readiness decision → 23 PhysicsCompiler entry and gate → 24 Canonical scene construction and schema validation → 25 API response delivered to the browser → 26 Frontend receives result and selects next state → 27 Review / explicit compile request branch → 28 InteractiveFigure receives the compiled scene → 29 FigureViewport background and layout → 30 PhysicsRuntime normalization and adapter initialization → 31 Domain solver and actual initial state → 32 CoordinateMapper: source → overlay → browser → 33 Actual renderer at t=0 over the original → 34 Activation, motion and reset

## 01. Browser selects the original diagram

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** User original file → this component → HTTP request reaches /api/ingest.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "original_file": {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "source": "C:\\Users\\saher\\Downloads\\photo_2026-10-10_12-06-37 (2).jpg",
      "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
      "bytes": 38634
    },
    "metadata": {
      "file_format": "JPEG",
      "encoded_width": 1280,
      "encoded_height": 960,
      "EXIF_orientation": null,
      "orientation": "landscape",
      "decoded_width": 1280,
      "decoded_height": 960,
      "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
      "png_note": "Lossless serialization of OpenCV decoded original JPEG; no resize, crop, redrawing, or orientation edit. Byte-exact original.jpg retained.",
      "decoded_pixels_sha256": "3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7",
      "browser_images": [
        {
          "tag": "DIV",
          "id": "",
          "className": "if-viewport-host",
          "src": null,
          "viewBox": null,
          "rect": {
            "x": 34,
            "y": 227,
            "width": 1010,
            "height": 480,
            "top": 227,
            "right": 1044,
            "bottom": 707,
            "left": 34
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "DIV",
          "id": "",
          "className": "figure-viewport",
          "src": null,
          "viewBox": null,
          "rect": {
            "x": 34,
            "y": 227,
            "width": 1010,
            "height": 480,
            "top": 227,
            "right": 1044,
            "bottom": 707,
            "left": 34
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "",
          "className": "figure-viewport-img",
          "src": "http://127.0.0.1:5173/uploads/test1.jpg",
          "naturalWidth": 797,
          "naturalHeight": 652,
          "width": 587,
          "height": 480,
          "viewBox": null,
          "rect": {
            "x": 245.625,
            "y": 227,
            "width": 586.734375,
            "height": 480,
            "top": 227,
            "right": 832.359375,
            "bottom": 707,
            "left": 245.625
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "DIV",
          "id": "",
          "className": "figure-viewport-overlay",
          "src": null,
          "viewBox": null,
          "rect": {
            "x": 245.625,
            "y": 227,
            "width": 586.734375,
            "height": 480,
            "top": 227,
            "right": 832.359375,
            "bottom": 707,
            "left": 245.625
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "CANVAS",
          "id": "",
          "className": "pendulum-overlay-canvas",
          "src": null,
          "width": 587,
          "height": 480,
          "viewBox": null,
          "rect": {
            "x": 245.625,
            "y": 227,
            "width": 586.734375,
            "height": 480,
            "top": 227,
            "right": 832.359375,
            "bottom": 707,
            "left": 245.625
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "diagram-image",
          "className": "diagram-image",
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207669693",
          "naturalWidth": 855,
          "naturalHeight": 686,
          "width": 855,
          "height": 686,
          "viewBox": null,
          "rect": {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "CANVAS",
          "id": "",
          "className": null,
          "src": null,
          "width": 855,
          "height": 686,
          "viewBox": null,
          "rect": {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "preview-image",
          "className": null,
          "src": "blob:http://127.0.0.1:5173/6f086ac5-e45d-4540-a321-37641fe2c0f1",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 224,
          "height": 168,
          "viewBox": null,
          "rect": {
            "x": 599.3900146484375,
            "y": 277.04498291015625,
            "width": 219.219970703125,
            "height": 164.9000244140625,
            "top": 277.04498291015625,
            "right": 818.6099853515625,
            "bottom": 441.94500732421875,
            "left": 599.3900146484375
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        }
      ]
    }
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startWithFile",
    "phase": "input",
    "wallTime": 4060.0999999940395,
    "data": [
      {},
      null
    ]
  }
]
```

**What it should receive — expected input:** An unchanged image File selected by the user. Identity is the recorded filename, byte count and SHA-256.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startWithFile",
      "phase": "output",
      "wallTime": 37146.69999998808,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** One upload operation: first UPLOADING, then a response-governed final state. This outer async call spans the rest of the pipeline; it must not invent a scene locally.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** File → multipart request. The generic JS File snapshot is {}, so use multipart metadata and the byte-exact source, not {} as evidence of an empty file.

[Complete stage input/output bundle](stage_data/01_upload.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 02. HTTP request reaches /api/ingest

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Browser selects the original diagram → this component → Upload persistence and dimension decoding.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "trace_id": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "method": "POST",
    "path": "/api/ingest",
    "headers": {
      "count": 17,
      "first_8_records": [
        [
          "host",
          "127.0.0.1:8000"
        ],
        [
          "connection",
          "close"
        ],
        [
          "content-length",
          "38841"
        ],
        [
          "x-physics-trace-id",
          "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017"
        ],
        [
          "sec-ch-ua-platform",
          "\"Windows\""
        ],
        [
          "user-agent",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"
        ],
        [
          "sec-ch-ua",
          "\"Google Chrome\";v=\"155\", \"Chromium\";v=\"155\", \"Not(A:Brand\";v=\"24\""
        ],
        [
          "content-type",
          "multipart/form-data; boundary=----WebKitFormBoundarySuj5sVJDOtUxYumt"
        ]
      ],
      "complete_list": "See complete stage bundle / original artifact"
    }
  }
]
```

**What it should receive — expected input:** POST multipart/form-data with the same image bytes and X-Physics-Trace-ID.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "handler_input": {
        "file": {
          "type": "starlette.datastructures.UploadFile",
          "not_serialized": true
        }
      },
      "note": "UploadFile is opaque in profiler; source and multipart bytes provide exact contents."
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A parsed UploadFile passed to ingestion. Request transport must not resize or re-encode the source.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Browser transport → FastAPI handler. Handler parameter is opaque in the profiler; saved multipart bytes are the authoritative payload.

[Complete stage input/output bundle](stage_data/02_http_in.json)

- [Exact multipart body](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207672293216400_request_body.bin)

- [HTTP response 1792207672293216400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207672293216400_response_body.json)

- [HTTP response 1792207704511725600_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207704511725600_response_body.json)

- [HTTP response 1792207705365140500_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207705365140500_response_body.json)

## 03. Upload persistence and dimension decoding

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** HTTP request reaches /api/ingest → this component → PageIR / whole-figure coordinate frame.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00003_UploadService.ingest",
    "value": {
      "data": {
        "bytes": 38634,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63.bin"
      },
      "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
      "mime_type": "image/jpeg"
    }
  }
]
```

**What it should receive — expected input:** Original encoded JPEG bytes, filename and MIME type from the upload.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00003_UploadService.ingest",
      "return_value": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** SourceAsset with storage path/public URL, content hash, native decoded dimensions and original filename.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Encoded bytes are persisted; metadata and an asset ID are added. This is not object detection.

[Complete stage input/output bundle](stage_data/03_asset.json)

- [UploadService.ingest — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

- [Code: ai\ingestion\UploadService.py](contracts/ai/ingestion/UploadService.py)

## 04. PageIR / whole-figure coordinate frame

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Upload persistence and dimension decoding → this component → Actual Gemini request and response.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00006_PageIRBuilder.build",
    "value": {
      "asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      },
      "public_url": "/uploads/diagram_9b910bff.jpg"
    }
  }
]
```

**What it should receive — expected input:** The verified SourceAsset for this image.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00006_PageIRBuilder.build",
      "return_value": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [],
        "metadata": {
          "pipeline": "PR-04-standalone-upload",
          "note": "Single-diagram upload. figure_001 is the entire image. Text blocks populated downstream by PR-06 evidence pipeline."
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Full-image region/figure in source_px, width=1280, height=960, top-left origin. No invented crop or landmark coordinates.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** SourceAsset → PageIR. The whole image is user-supplied; confidence in that extent does not imply confidence in physics landmarks.

[Complete stage input/output bundle](stage_data/04_page.json)

- [PageIRBuilder.build — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- [Code: ai\ingestion\PageIRBuilder.py](contracts/ai/ingestion/PageIRBuilder.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/actual_overlay_on_source.png)

## 05. Actual Gemini request and response

**Execution:** EXECUTED. **Verdict:** PASS WITH LIMITS.

**Upstream → downstream:** PageIR / whole-figure coordinate frame → this component → Semantic validation, confidence caps and thresholds.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00010_GeminiVisionProvider.analyze_diagram",
    "value": {
      "image_bytes": {
        "bytes": 38634,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63.bin"
      },
      "mime_type": "image/jpeg",
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [],
        "metadata": {
          "pipeline": "PR-04-standalone-upload",
          "note": "Single-diagram upload. figure_001 is the entire image. Text blocks populated downstream by PR-06 evidence pipeline."
        }
      }
    }
  },
  {
    "call": "00012_Models.generate_content",
    "value": {
      "model": "gemini-3.1-flash-lite",
      "contents": [
        {
          "media_resolution": null,
          "code_execution_result": null,
          "executable_code": null,
          "file_data": null,
          "function_call": null,
          "function_response": null,
          "inline_data": {
            "data": {
              "bytes": 38634,
              "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
              "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63.bin"
            },
            "display_name": null,
            "mime_type": "image/jpeg"
          },
          "text": null,
          "thought": null,
          "thought_signature": null,
          "video_metadata": null,
          "tool_call": null,
          "_other_fields_in_complete_snapshot": [
            "tool_response",
            "part_metadata",
            "audio_transcription",
            "media_processing",
            "speech_metadata"
          ]
        },
        {
          "string_length": 3987,
          "complete_text": "See complete stage bundle / original artifact; not rewritten"
        }
      ],
      "config": {
        "http_options": null,
        "should_return_http_response": null,
        "system_instruction": null,
        "temperature": 0.1,
        "top_p": null,
        "top_k": null,
        "candidate_count": null,
        "max_output_tokens": null,
        "stop_sequences": null,
        "response_logprobs": null,
        "logprobs": null,
        "presence_penalty": null,
        "_other_fields_in_complete_snapshot": [
          "frequency_penalty",
          "seed",
          "response_mime_type",
          "response_schema",
          "response_json_schema",
          "routing_config",
          "model_selection_config",
          "safety_settings",
          "tools",
          "tool_config",
          "labels",
          "cached_content",
          "response_modalities",
          "media_resolution",
          "speech_config",
          "audio_timestamp",
          "automatic_function_calling",
          "thinking_config",
          "image_config",
          "enable_enhanced_civic_answers",
          "model_armor_config",
          "service_tier",
          "audio_transcription_config"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** The same encoded image, semantic prompt, configured model and response schema. Credentials are redacted.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00010_GeminiVisionProvider.analyze_diagram",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "gemini-3.1-flash-lite",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      }
    },
    {
      "call": "00012_Models.generate_content",
      "return_value": {
        "sdk_http_response": {
          "headers": {
            "x-gemini-service-tier": "standard",
            "content-type": "application/json; charset=UTF-8",
            "vary": "Origin, X-Origin, Referer",
            "content-encoding": "gzip",
            "date": "Sat, 17 Oct 2026 03:28:00 GMT",
            "server": "scaffolding on HTTPServer2",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "x-content-type-options": "nosniff",
            "server-timing": "gfet4t7; dur=7862",
            "alt-svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
            "transfer-encoding": "chunked"
          },
          "body": null
        },
        "candidates": [
          {
            "content": {
              "parts": [
                {
                  "media_resolution": null,
                  "code_execution_result": null,
                  "executable_code": null,
                  "file_data": null,
                  "function_call": null,
                  "function_response": null,
                  "inline_data": null,
                  "text": "{\n  \"classification\": \"supported\",\n  \"isPhysics\": true,\n  \"domain\": \"circuits\",\n  \"subtype\": \"dc_linear\",\n  \"confidence\": {\n    \"isPhysics\": 1.0,\n    \"domain\": 1.0,\n    \"subtype\": 1.0,\n    \"overall\": 1.0\n  },\n  \"entities\": [\n    {\n      \"temporaryId\": \"voltage_source_1\",\n      \"role\": \"voltage_source\",\n      \"label\": \"12 V\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"switch_1\",\n      \"role\": \"switch\",\n      \"label\": \"S\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"resistor_1\",\n      \"role\": \"resistor\",\n      \"label\": \"R1 = 10 Ω\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"resistor_2\",\n      \"role\": \"resistor\",\n      \"label\": \"R2 = 20 Ω\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"wire_1\",\n      \"role\": \"wire\",\n      \"label\": \"I\",\n      \"confidence\": 0.95\n    }\n  ],\n  \"relationships\": [\n    {\n      \"type\": \"connected_in_series\",\n      \"from\": \"voltage_source_1\",\n      \"to\": \"switch_1\",\n      \"confidence\": 1.0\n    },\n    {\n      \"type\": \"connected_in_series\",\n      \"from\": \"switch_1\",\n      \"to\": \"resistor_1\",\n      \"confidence\": 1.0\n    },\n    {\n      \"type\": \"connected_in_series\",\n      \"from\": \"resistor_1\",\n      \"to\": \"resistor_2\",\n      \"confidence\": 1.0\n    },\n    {\n      \"type\": \"connected_in_series\",\n      \"from\": \"resistor_2\",\n      \"to\": \"voltage_source_1\",\n      \"confidence\": 1.0\n    }\n  ],\n  \"visibleLabels\": [\n    {\n      \"text\": \"12 V\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"voltage_value\"\n    },\n    {\n      \"text\": \"S\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"switch_label\"\n    },\n    {\n      \"text\": \"R1 = 10 Ω\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"resistor_label\"\n    },\n    {\n      \"text\": \"R2 = 20 Ω\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"resistor_label\"\n    },\n    {\n      \"text\": \"I\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"current_label\"\n    },\n    {\n      \"text\": \"Fig. 9 Series DC Circuit\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"caption\"\n    }\n  ],\n  \"candidates\": [],\n  \"notes\": [\n    \"The diagram shows a simple series DC circuit with a voltage source, a switch, and two resistors.\"\n  ]\n}",
                  "thought": null,
                  "video_metadata": null,
                  "tool_call": null,
                  "tool_response": null,
                  "part_metadata": null,
                  "audio_transcription": null,
                  "media_processing": null,
                  "speech_metadata": null,
                  "_nested_fields_in_complete_snapshot": [
                    "thought_signature"
                  ]
                }
              ],
              "role": "model"
            },
            "citation_metadata": null,
            "finish_message": null,
            "token_count": null,
            "finish_reason": "STOP",
            "grounding_metadata": null,
            "avg_logprobs": null,
            "index": 0,
            "logprobs_result": null,
            "safety_ratings": null,
            "url_context_metadata": null
          }
        ],
        "create_time": null,
        "model_version": "gemini-3.1-flash-lite",
        "prompt_feedback": null,
        "response_id": "OevSatu6OdzFg8UP5ePU-As",
        "usage_metadata": {
          "cache_tokens_details": null,
          "cached_content_token_count": null,
          "candidates_token_count": 812,
          "candidates_tokens_details": null,
          "prompt_token_count": 2233,
          "prompt_tokens_details": [
            {
              "modality": "TEXT",
              "token_count": 1169
            },
            {
              "modality": "IMAGE",
              "token_count": 1064
            }
          ],
          "thoughts_token_count": null,
          "tool_use_prompt_token_count": null,
          "tool_use_prompt_tokens_details": null,
          "total_token_count": 3045,
          "traffic_type": null
        },
        "model_status": null,
        "automatic_function_calling_history": [],
        "parsed": {
          "classification": "supported",
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "confidence": {
            "isPhysics": 1.0,
            "domain": 1.0,
            "subtype": 1.0,
            "overall": 1.0
          },
          "entities": [
            {
              "temporaryId": "voltage_source_1",
              "role": "voltage_source",
              "label": "12 V",
              "confidence": 1.0
            },
            {
              "temporaryId": "switch_1",
              "role": "switch",
              "label": "S",
              "confidence": 1.0
            },
            {
              "temporaryId": "resistor_1",
              "role": "resistor",
              "label": "R1 = 10 Ω",
              "confidence": 1.0
            },
            {
              "temporaryId": "resistor_2",
              "role": "resistor",
              "label": "R2 = 20 Ω",
              "confidence": 1.0
            },
            {
              "temporaryId": "wire_1",
              "role": "wire",
              "label": "I",
              "confidence": 0.95
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 1.0
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 1.0
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 1.0
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 1.0
            }
          ],
          "visibleLabels": [
            {
              "text": "12 V",
              "confidence": 1.0,
              "semanticRole": "voltage_value"
            },
            {
              "text": "S",
              "confidence": 1.0,
              "semanticRole": "switch_label"
            },
            {
              "text": "R1 = 10 Ω",
              "confidence": 1.0,
              "semanticRole": "resistor_label"
            },
            {
              "text": "R2 = 20 Ω",
              "confidence": 1.0,
              "semanticRole": "resistor_label"
            },
            {
              "text": "I",
              "confidence": 1.0,
              "semanticRole": "current_label"
            },
            {
              "text": "Fig. 9 Series DC Circuit",
              "confidence": 1.0,
              "semanticRole": "caption"
            }
          ],
          "candidates": [],
          "notes": [
            "The diagram shows a simple series DC circuit with a voltage source, a switch, and two resistors."
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Semantic classification, domain/subtype, entity roles and relationships. Numerical physical parameters and authoritative geometry must not originate here.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=circuits / dc_linear. Expected semantic content: A 12 V battery with polarity marks, an OPEN switch S, R1=10 Ω on the top branch, R2=20 Ω on the right vertical branch, connecting wires and a current-direction annotation. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Image → model response. SDK/provider-internal preprocessing and private tensors were not exposed; no transform is invented for them.

[Complete stage input/output bundle](stage_data/05_vlm.json)

- [GeminiVisionProvider.analyze_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- [Models.generate_content — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

- [Code: ai\ingestion\vision\gemini_provider.py](contracts/ai/ingestion/vision/gemini_provider.py)

## 06. Semantic validation, confidence caps and thresholds

**Execution:** EXECUTED. **Verdict:** PASS WITH LIMITS.

**Upstream → downstream:** Actual Gemini request and response → this component → Initial semantic BookIR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00009_PhysicsVisionAnalyzer.analyze",
    "value": {
      "source_asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [],
        "metadata": {
          "pipeline": "PR-04-standalone-upload",
          "note": "Single-diagram upload. figure_001 is the entire image. Text blocks populated downstream by PR-06 evidence pipeline."
        }
      }
    }
  },
  {
    "call": "00015_validate_semantic_payload",
    "value": {
      "raw": {
        "classification": "supported",
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "confidence": {
          "isPhysics": 1.0,
          "domain": 1.0,
          "subtype": 1.0,
          "overall": 1.0
        },
        "entities": [
          {
            "temporaryId": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 1.0
          },
          {
            "temporaryId": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 1.0
          },
          {
            "temporaryId": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 1.0
          },
          {
            "temporaryId": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 1.0
          },
          {
            "temporaryId": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 1.0
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 1.0
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 1.0
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 1.0
          }
        ],
        "visibleLabels": [
          {
            "text": "12 V",
            "confidence": 1.0,
            "semanticRole": "voltage_value"
          },
          {
            "text": "S",
            "confidence": 1.0,
            "semanticRole": "switch_label"
          },
          {
            "text": "R1 = 10 Ω",
            "confidence": 1.0,
            "semanticRole": "resistor_label"
          },
          {
            "text": "R2 = 20 Ω",
            "confidence": 1.0,
            "semanticRole": "resistor_label"
          },
          {
            "text": "I",
            "confidence": 1.0,
            "semanticRole": "current_label"
          },
          {
            "text": "Fig. 9 Series DC Circuit",
            "confidence": 1.0,
            "semanticRole": "caption"
          }
        ],
        "candidates": [],
        "notes": [
          "The diagram shows a simple series DC circuit with a voltage source, a switch, and two resistors."
        ]
      }
    }
  },
  {
    "call": "00051_PhysicsVisionAnalyzer._apply_thresholds",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "gemini-3.1-flash-lite",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** The actual raw provider response, including its confidence values and declared entity IDs.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00009_PhysicsVisionAnalyzer.analyze",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "gemini-3.1-flash-lite",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      }
    },
    {
      "call": "00015_validate_semantic_payload",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      }
    },
    {
      "call": "00051_PhysicsVisionAnalyzer._apply_thresholds",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "gemini-3.1-flash-lite",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Supported domain/subtype pairing, native boolean isPhysics, bounded finite confidence and valid relationship references. Approximate VLM boxes remain non-authoritative.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=circuits / dc_linear. Expected semantic content: A 12 V battery with polarity marks, an OPEN switch S, R1=10 Ω on the top branch, R2=20 Ω on the right vertical branch, connecting wires and a current-direction annotation. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Raw semantic response → validated semantic representation. Compare raw_provider confidence with the capped accepted values.

[Complete stage input/output bundle](stage_data/06_semantic.json)

- [PhysicsVisionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- [validate_semantic_payload — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- [PhysicsVisionAnalyzer._apply_thresholds — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00051_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

- [Code: ai\ingestion\vision\analyzer.py](contracts/ai/ingestion/vision/analyzer.py)

- [Code: shared\schemas\semantic.py](contracts/shared/schemas/semantic.py)

## 07. Initial semantic BookIR

**Execution:** EXECUTED. **Verdict:** PASS WITH LIMITS.

**Upstream → downstream:** Semantic validation, confidence caps and thresholds → this component → Evidence dispatch and source decode.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00007_BookUnderstandingPipeline.analyze",
    "value": {
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [],
        "metadata": {
          "pipeline": "PR-04-standalone-upload",
          "note": "Single-diagram upload. figure_001 is the entire image. Text blocks populated downstream by PR-06 evidence pipeline."
        }
      },
      "asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      }
    }
  },
  {
    "call": "00052_BookUnderstandingPipeline._build_book_ir_from_result",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "entities": [
          {
            "temporary_id": "voltage_source_1",
            "role": "voltage_source",
            "label": "12 V",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "switch_1",
            "role": "switch",
            "label": "S",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_1",
            "role": "resistor",
            "label": "R1 = 10 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "resistor_2",
            "role": "resistor",
            "label": "R2 = 20 Ω",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "wire_1",
            "role": "wire",
            "label": "I",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "source_id": "voltage_source_1",
            "target_id": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "switch_1",
            "target_id": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_1",
            "target_id": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "source_id": "resistor_2",
            "target_id": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "model": "gemini-3.1-flash-lite",
        "_other_fields_in_complete_snapshot": [
          "confidence",
          "visible_labels",
          "candidates",
          "notes",
          "provider",
          "prompt_version",
          "timestamp",
          "latency_ms",
          "cache_hit",
          "fallback_used",
          "debug"
        ]
      },
      "asset_id": "9b910bff7ee74e90a1763e5358b474ff",
      "page_ir_version": "1.0",
      "figure_id": "figure_001"
    }
  }
]
```

**What it should receive — expected input:** Validated semantic result plus the SourceAsset/PageIR identity.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00007_BookUnderstandingPipeline.analyze",
      "return_value": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "voltage_source_1",
            "type": "voltage_source",
            "label": "12 V",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_1",
            "type": "resistor",
            "label": "R1 = 10 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_2",
            "type": "resistor",
            "label": "R2 = 20 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "wire_1",
            "type": "wire",
            "label": "I",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    },
    {
      "call": "00052_BookUnderstandingPipeline._build_book_ir_from_result",
      "return_value": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "voltage_source_1",
            "type": "voltage_source",
            "label": "12 V",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_1",
            "type": "resistor",
            "label": "R1 = 10 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_2",
            "type": "resistor",
            "label": "R2 = 20 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "wire_1",
            "type": "wire",
            "label": "I",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** BookIR with semantic entities and evidence references, but null authoritative positions/geometry until CV/OCR grounds them. Missing numbers remain missing.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=circuits / dc_linear. Expected semantic content: A 12 V battery with polarity marks, an OPEN switch S, R1=10 Ω on the top branch, R2=20 Ω on the right vertical branch, connecting wires and a current-direction annotation. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Semantic roles are assigned durable entity IDs. This BookIR is an intermediate hypothesis, not a runnable simulation.

[Complete stage input/output bundle](stage_data/07_book.json)

- [BookUnderstandingPipeline.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- [BookUnderstandingPipeline._build_book_ir_from_result — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00052_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- [Code: ai\ingestion\BookUnderstandingPipeline.py](contracts/ai/ingestion/BookUnderstandingPipeline.py)

## 08. Evidence dispatch and source decode

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Initial semantic BookIR → this component → RapidOCR: first text/box observations.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00055_GrounderRegistry.find_grounder",
    "value": {
      "domain": "circuits",
      "subtype": "dc_linear"
    }
  },
  {
    "call": "00063_load_and_validate_source_image",
    "value": {
      "asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      }
    }
  }
]
```

**What it should receive — expected input:** Supported domain/subtype, semantic BookIR, SourceAsset and PageIR.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00055_GrounderRegistry.find_grounder",
      "return_value": {
        "type": "ai.evidence.grounding.circuits.CircuitGrounder",
        "not_serialized": true
      }
    },
    {
      "call": "00063_load_and_validate_source_image",
      "return_value": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The matching subtype grounder and the unchanged native BGR image array; decoder dimensions must match the asset.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** The pipeline routes to the domain module. Other grounders may execute supports() checks; their ground() methods are not thereby executed.

[Complete stage input/output bundle](stage_data/08_route.json)

- [GrounderRegistry.find_grounder — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00055_GrounderRegistry.find_grounder/STAGE.html)

- [load_and_validate_source_image — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00063_load_and_validate_source_image/STAGE.html)

- [Code: ai\evidence\grounding\registry.py](contracts/ai/evidence/grounding/registry.py)

- [Code: ai\evidence\transforms.py](contracts/ai/evidence/transforms.py)

## 09. RapidOCR: first text/box observations

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** Evidence dispatch and source decode → this component → EasyOCR: independent OCR candidates.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00067_RapidOCRProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "region": null
    }
  }
]
```

**What it should receive — expected input:** Native image array and source dimensions, with any region transform explicit.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00067_RapidOCRProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_001",
            "raw_text": "S",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 378.0,
              "y": 159.0,
              "width": 47.0,
              "height": 53.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 378.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 212.0
                },
                {
                  "x": 378.0,
                  "y": 212.0
                }
              ]
            },
            "confidence": 0.99926,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "R1 = 10 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 636.0,
              "y": 148.0,
              "width": 242.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 636.0,
                  "y": 151.0
                },
                {
                  "x": 877.0,
                  "y": 148.0
                },
                {
                  "x": 878.0,
                  "y": 213.0
                },
                {
                  "x": 637.0,
                  "y": 216.0
                }
              ]
            },
            "confidence": 0.86803,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "十",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 175.0,
              "y": 362.0,
              "width": 40.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 175.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 402.0
                },
                {
                  "x": 175.0,
                  "y": 402.0
                }
              ]
            },
            "confidence": 0.72651,
            "script_candidate": "mixed",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "12 V",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 39.0,
              "y": 426.0,
              "width": 123.0,
              "height": 63.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 39.0,
                  "y": 428.0
                },
                {
                  "x": 161.0,
                  "y": 426.0
                },
                {
                  "x": 162.0,
                  "y": 487.0
                },
                {
                  "x": 40.0,
                  "y": 489.0
                }
              ]
            },
            "confidence": 0.98113,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "R2 = 20 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1029.0,
              "y": 421.0,
              "width": 241.0,
              "height": 71.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1029.0,
                  "y": 423.0
                },
                {
                  "x": 1270.0,
                  "y": 421.0
                },
                {
                  "x": 1270.0,
                  "y": 490.0
                },
                {
                  "x": 1029.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.90339,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "I",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 613.0,
              "y": 706.0,
              "width": 39.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 613.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 758.0
                },
                {
                  "x": 613.0,
                  "y": 758.0
                }
              ]
            },
            "confidence": 0.99429,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Fig. 9 Series DC Circuit",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 336.0,
              "y": 817.0,
              "width": 603.0,
              "height": 70.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 336.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 887.0
                },
                {
                  "x": 336.0,
                  "y": 887.0
                }
              ]
            },
            "confidence": 0.97378,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          }
        ],
        "provider": "rapidocr",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "recognizer_language": "latin_digits_ch",
        "latency_ms": 1656.969499978004,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Observed strings, confidence, source-space polygons/boxes and recognizer metadata. Text recognition alone does not locate the physical component represented by a label.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Changes, provenance and possible information loss:** Image → text candidates. Inspect exact source boxes; a correct string can still have a box overlapping diagram geometry.

[Complete stage input/output bundle](stage_data/09_rapid.json)

- [RapidOCRProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00067_RapidOCRProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\rapidocr.py](contracts/ai/evidence/ocr/rapidocr.py)

## 10. EasyOCR: independent OCR candidates

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** RapidOCR: first text/box observations → this component → Symbol candidates, deduplication and final OCR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00116_EasyOCRBanglaProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "region": null
    }
  }
]
```

**What it should receive — expected input:** The same source image and dimensional contract.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00116_EasyOCRBanglaProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "bn_tok_001",
            "raw_text": "R1 = 10 `2",
            "normalized_text": "R1 = 10 `2",
            "bbox_source_px": {
              "x": 642.0,
              "y": 151.0,
              "width": 233.0,
              "height": 66.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 642.0,
                  "y": 151.0
                },
                {
                  "x": 875.0,
                  "y": 151.0
                },
                {
                  "x": 875.0,
                  "y": 217.0
                },
                {
                  "x": 642.0,
                  "y": 217.0
                }
              ]
            },
            "confidence": 0.46127750970800835,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_001"
          },
          {
            "id": "bn_tok_002",
            "raw_text": "12 `",
            "normalized_text": "12 `",
            "bbox_source_px": {
              "x": 42.0,
              "y": 432.0,
              "width": 122.0,
              "height": 54.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 42.0,
                  "y": 432.0
                },
                {
                  "x": 164.0,
                  "y": 432.0
                },
                {
                  "x": 164.0,
                  "y": 486.0
                },
                {
                  "x": 42.0,
                  "y": 486.0
                }
              ]
            },
            "confidence": 0.3936148122970558,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_002"
          },
          {
            "id": "bn_tok_003",
            "raw_text": "R2 = 20 2",
            "normalized_text": "R2 = 20 2",
            "bbox_source_px": {
              "x": 1035.0,
              "y": 427.0,
              "width": 232.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1035.0,
                  "y": 427.0
                },
                {
                  "x": 1267.0,
                  "y": 427.0
                },
                {
                  "x": 1267.0,
                  "y": 495.0
                },
                {
                  "x": 1035.0,
                  "y": 495.0
                }
              ]
            },
            "confidence": 0.43002614643260995,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_003"
          },
          {
            "id": "bn_tok_004",
            "raw_text": "9",
            "normalized_text": "9",
            "bbox_source_px": {
              "x": 451.0,
              "y": 825.0,
              "width": 38.0,
              "height": 48.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 451.0,
                  "y": 825.0
                },
                {
                  "x": 489.0,
                  "y": 825.0
                },
                {
                  "x": 489.0,
                  "y": 873.0
                },
                {
                  "x": 451.0,
                  "y": 873.0
                }
              ]
            },
            "confidence": 0.9999800921477267,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_004"
          },
          {
            "id": "bn_tok_005",
            "raw_text": "Series DC Circuit",
            "normalized_text": "Series DC Circuit",
            "bbox_source_px": {
              "x": 515.0,
              "y": 821.0,
              "width": 424.0,
              "height": 60.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 515.0,
                  "y": 821.0
                },
                {
                  "x": 939.0,
                  "y": 821.0
                },
                {
                  "x": 939.0,
                  "y": 881.0
                },
                {
                  "x": 515.0,
                  "y": 881.0
                }
              ]
            },
            "confidence": 0.5601091971201398,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_005"
          },
          {
            "id": "bn_tok_006",
            "raw_text": "Fig",
            "normalized_text": "Fig",
            "bbox_source_px": {
              "x": 332.34095141343704,
              "y": 813.0766894303488,
              "width": 121.31809717312592,
              "height": 80.84662113930244
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 345.96667006423115,
                  "y": 813.0766894303488
                },
                {
                  "x": 453.65904858656296,
                  "y": 833.8419749950954
                },
                {
                  "x": 440.03332993576885,
                  "y": 893.9233105696512
                },
                {
                  "x": 332.34095141343704,
                  "y": 873.1580250049046
                }
              ]
            },
            "confidence": 0.9334288835525513,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_006"
          }
        ],
        "provider": "easyocr_bangla",
        "model": "bengali.pth",
        "package": "easyocr",
        "package_version": "1.7.2",
        "detector_model": "craft_mlt_25k.pth",
        "recognizer_model": "bengali.pth",
        "recognizer_language": "bn+en",
        "latency_ms": 12240.185100003146,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Independent text alternatives with confidence and source positions; uncertain alternatives should not silently overwrite stronger evidence.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Changes, provenance and possible information loss:** Alternative OCR supplies competing evidence. Its errors are distinct from whichever result the router actually selects.

[Complete stage input/output bundle](stage_data/10_easy.json)

- [EasyOCRBanglaProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00116_EasyOCRBanglaProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\bangla.py](contracts/ai/evidence/ocr/bangla.py)

## 11. Symbol candidates, deduplication and final OCR

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** EasyOCR: independent OCR candidates → this component → Grayscale, blur and edge extraction.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 10,
  "first_8_records": [
    {
      "call": "00066_MultiOCRRouter.extract",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
        },
        "source_width": 1280,
        "source_height": 960,
        "region": null
      }
    },
    {
      "call": "00167_deduplicate_spatial_tokens",
      "value": {
        "tokens": [
          {
            "id": "ocr_tok_001",
            "raw_text": "S",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 378.0,
              "y": 159.0,
              "width": 47.0,
              "height": 53.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 378.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 212.0
                },
                {
                  "x": 378.0,
                  "y": 212.0
                }
              ]
            },
            "confidence": 0.99926,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "R1 = 10 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 636.0,
              "y": 148.0,
              "width": 242.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 636.0,
                  "y": 151.0
                },
                {
                  "x": 877.0,
                  "y": 148.0
                },
                {
                  "x": 878.0,
                  "y": 213.0
                },
                {
                  "x": 637.0,
                  "y": 216.0
                }
              ]
            },
            "confidence": 0.86803,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R1 = 10 `2",
                "script": "latin",
                "confidence": 0.46127750970800835,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "十",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 175.0,
              "y": 362.0,
              "width": 40.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 175.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 402.0
                },
                {
                  "x": 175.0,
                  "y": 402.0
                }
              ]
            },
            "confidence": 0.72651,
            "script_candidate": "mixed",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "12 V",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 39.0,
              "y": 426.0,
              "width": 123.0,
              "height": 63.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 39.0,
                  "y": 428.0
                },
                {
                  "x": 161.0,
                  "y": 426.0
                },
                {
                  "x": 162.0,
                  "y": 487.0
                },
                {
                  "x": 40.0,
                  "y": 489.0
                }
              ]
            },
            "confidence": 0.98113,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "12 `",
                "script": "latin",
                "confidence": 0.3936148122970558,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "R2 = 20 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1029.0,
              "y": 421.0,
              "width": 241.0,
              "height": 71.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1029.0,
                  "y": 423.0
                },
                {
                  "x": 1270.0,
                  "y": 421.0
                },
                {
                  "x": 1270.0,
                  "y": 490.0
                },
                {
                  "x": 1029.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.90339,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R2 = 20 2",
                "script": "latin",
                "confidence": 0.43002614643260995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "I",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 613.0,
              "y": 706.0,
              "width": 39.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 613.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 758.0
                },
                {
                  "x": 613.0,
                  "y": 758.0
                }
              ]
            },
            "confidence": 0.99429,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Fig. 9 Series DC Circuit",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 336.0,
              "y": 817.0,
              "width": 603.0,
              "height": 70.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 336.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 887.0
                },
                {
                  "x": 336.0,
                  "y": 887.0
                }
              ]
            },
            "confidence": 0.97378,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9334288835525513,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          }
        ]
      }
    },
    {
      "call": "00175_GreekSymbolVisualOCR.extract_symbols",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
        },
        "existing_tokens": [
          {
            "id": "ocr_tok_007",
            "raw_text": "Fig. 9 Series DC Circuit",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 336.0,
              "y": 817.0,
              "width": 603.0,
              "height": 70.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 336.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 887.0
                },
                {
                  "x": 336.0,
                  "y": 887.0
                }
              ]
            },
            "confidence": 0.97378,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9334288835525513,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "R2 = 20 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1029.0,
              "y": 421.0,
              "width": 241.0,
              "height": 71.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1029.0,
                  "y": 423.0
                },
                {
                  "x": 1270.0,
                  "y": 421.0
                },
                {
                  "x": 1270.0,
                  "y": 490.0
                },
                {
                  "x": 1029.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.90339,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R2 = 20 2",
                "script": "latin",
                "confidence": 0.43002614643260995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "R1 = 10 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 636.0,
              "y": 148.0,
              "width": 242.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 636.0,
                  "y": 151.0
                },
                {
                  "x": 877.0,
                  "y": 148.0
                },
                {
                  "x": 878.0,
                  "y": 213.0
                },
                {
                  "x": 637.0,
                  "y": 216.0
                }
              ]
            },
            "confidence": 0.86803,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R1 = 10 `2",
                "script": "latin",
                "confidence": 0.46127750970800835,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "12 V",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 39.0,
              "y": 426.0,
              "width": 123.0,
              "height": 63.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 39.0,
                  "y": 428.0
                },
                {
                  "x": 161.0,
                  "y": 426.0
                },
                {
                  "x": 162.0,
                  "y": 487.0
                },
                {
                  "x": 40.0,
                  "y": 489.0
                }
              ]
            },
            "confidence": 0.98113,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "12 `",
                "script": "latin",
                "confidence": 0.3936148122970558,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "S",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 378.0,
              "y": 159.0,
              "width": 47.0,
              "height": 53.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 378.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 212.0
                },
                {
                  "x": 378.0,
                  "y": 212.0
                }
              ]
            },
            "confidence": 0.99926,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "I",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 613.0,
              "y": 706.0,
              "width": 39.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 613.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 758.0
                },
                {
                  "x": 613.0,
                  "y": 758.0
                }
              ]
            },
            "confidence": 0.99429,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "十",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 175.0,
              "y": 362.0,
              "width": 40.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 175.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 402.0
                },
                {
                  "x": 175.0,
                  "y": 402.0
                }
              ]
            },
            "confidence": 0.72651,
            "script_candidate": "mixed",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          }
        ],
        "source_width": 1280,
        "source_height": 960
      }
    },
    {
      "call": "00176_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_007",
          "raw_text": "Fig. 9 Series DC Circuit",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 336.0,
            "y": 817.0,
            "width": 603.0,
            "height": 70.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 336.0,
                "y": 817.0
              },
              {
                "x": 939.0,
                "y": 817.0
              },
              {
                "x": 939.0,
                "y": 887.0
              },
              {
                "x": 336.0,
                "y": 887.0
              }
            ]
          },
          "confidence": 0.97378,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9334288835525513,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_007"
        }
      }
    },
    {
      "call": "00178_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_005",
          "raw_text": "R2 = 20 Ω",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1029.0,
            "y": 421.0,
            "width": 241.0,
            "height": 71.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1029.0,
                "y": 423.0
              },
              {
                "x": 1270.0,
                "y": 421.0
              },
              {
                "x": 1270.0,
                "y": 490.0
              },
              {
                "x": 1029.0,
                "y": 492.0
              }
            ]
          },
          "confidence": 0.90339,
          "script_candidate": "greek",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "R2 = 20 2",
              "script": "latin",
              "confidence": 0.43002614643260995,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_005"
        }
      }
    },
    {
      "call": "00180_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_002",
          "raw_text": "R1 = 10 Ω",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 636.0,
            "y": 148.0,
            "width": 242.0,
            "height": 68.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 636.0,
                "y": 151.0
              },
              {
                "x": 877.0,
                "y": 148.0
              },
              {
                "x": 878.0,
                "y": 213.0
              },
              {
                "x": 637.0,
                "y": 216.0
              }
            ]
          },
          "confidence": 0.86803,
          "script_candidate": "greek",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "R1 = 10 `2",
              "script": "latin",
              "confidence": 0.46127750970800835,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      }
    },
    {
      "call": "00182_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_004",
          "raw_text": "12 V",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 39.0,
            "y": 426.0,
            "width": 123.0,
            "height": 63.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 39.0,
                "y": 428.0
              },
              {
                "x": 161.0,
                "y": 426.0
              },
              {
                "x": 162.0,
                "y": 487.0
              },
              {
                "x": 40.0,
                "y": 489.0
              }
            ]
          },
          "confidence": 0.98113,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "12 `",
              "script": "latin",
              "confidence": 0.3936148122970558,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_004"
        }
      }
    },
    {
      "call": "00184_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_001",
          "raw_text": "S",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 378.0,
            "y": 159.0,
            "width": 47.0,
            "height": 53.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 378.0,
                "y": 159.0
              },
              {
                "x": 425.0,
                "y": 159.0
              },
              {
                "x": 425.0,
                "y": 212.0
              },
              {
                "x": 378.0,
                "y": 212.0
              }
            ]
          },
          "confidence": 0.99926,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        }
      }
    }
  ],
  "complete_list": "See complete stage bundle / original artifact"
}
```

**What it should receive — expected input:** Provider token candidates, spatial overlap information and symbol alternatives.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": {
    "count": 10,
    "first_8_records": [
      {
        "call": "00066_MultiOCRRouter.extract",
        "return_value": {
          "status": "success",
          "tokens": [
            {
              "id": "ocr_tok_007",
              "raw_text": "Fig. 9 Series DC Circuit",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 336.0,
                "y": 817.0,
                "width": 603.0,
                "height": 70.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 336.0,
                    "y": 817.0
                  },
                  {
                    "x": 939.0,
                    "y": 817.0
                  },
                  {
                    "x": 939.0,
                    "y": 887.0
                  },
                  {
                    "x": 336.0,
                    "y": 887.0
                  }
                ]
              },
              "confidence": 0.97378,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Fig",
                  "script": "latin",
                  "confidence": 0.9334288835525513,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_007"
            },
            {
              "id": "ocr_tok_005",
              "raw_text": "R2 = 20 Ω",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1029.0,
                "y": 421.0,
                "width": 241.0,
                "height": 71.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1029.0,
                    "y": 423.0
                  },
                  {
                    "x": 1270.0,
                    "y": 421.0
                  },
                  {
                    "x": 1270.0,
                    "y": 490.0
                  },
                  {
                    "x": 1029.0,
                    "y": 492.0
                  }
                ]
              },
              "confidence": 0.90339,
              "script_candidate": "greek",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "R2 = 20 2",
                  "script": "latin",
                  "confidence": 0.43002614643260995,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_005"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "R1 = 10 Ω",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 636.0,
                "y": 148.0,
                "width": 242.0,
                "height": 68.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 636.0,
                    "y": 151.0
                  },
                  {
                    "x": 877.0,
                    "y": 148.0
                  },
                  {
                    "x": 878.0,
                    "y": 213.0
                  },
                  {
                    "x": 637.0,
                    "y": 216.0
                  }
                ]
              },
              "confidence": 0.86803,
              "script_candidate": "greek",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "R1 = 10 `2",
                  "script": "latin",
                  "confidence": 0.46127750970800835,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            },
            {
              "id": "ocr_tok_004",
              "raw_text": "12 V",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 39.0,
                "y": 426.0,
                "width": 123.0,
                "height": 63.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 39.0,
                    "y": 428.0
                  },
                  {
                    "x": 161.0,
                    "y": 426.0
                  },
                  {
                    "x": 162.0,
                    "y": 487.0
                  },
                  {
                    "x": 40.0,
                    "y": 489.0
                  }
                ]
              },
              "confidence": 0.98113,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "12 `",
                  "script": "latin",
                  "confidence": 0.3936148122970558,
                  "provider": "easyocr_bangla"
                },
                {
                  "text": "12 V",
                  "script": "mixed",
                  "name": "voltage_value",
                  "confidence": 0.95,
                  "provider": "physics_unit_confusable"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_004"
            },
            {
              "id": "ocr_tok_001",
              "raw_text": "S",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 378.0,
                "y": 159.0,
                "width": 47.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 378.0,
                    "y": 159.0
                  },
                  {
                    "x": 425.0,
                    "y": 159.0
                  },
                  {
                    "x": 425.0,
                    "y": 212.0
                  },
                  {
                    "x": 378.0,
                    "y": 212.0
                  }
                ]
              },
              "confidence": 0.99926,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "I",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 613.0,
                "y": 706.0,
                "width": 39.0,
                "height": 52.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 613.0,
                    "y": 706.0
                  },
                  {
                    "x": 652.0,
                    "y": 706.0
                  },
                  {
                    "x": 652.0,
                    "y": 758.0
                  },
                  {
                    "x": 613.0,
                    "y": 758.0
                  }
                ]
              },
              "confidence": 0.99429,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "1",
                  "script": "numeric",
                  "name": "one",
                  "confidence": 0.845,
                  "provider": "confusable_resolver"
                },
                {
                  "text": "l",
                  "script": "latin",
                  "name": "length_l",
                  "confidence": 0.795,
                  "provider": "confusable_resolver"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "十",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 175.0,
                "y": 362.0,
                "width": 40.0,
                "height": 40.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 175.0,
                    "y": 362.0
                  },
                  {
                    "x": 215.0,
                    "y": 362.0
                  },
                  {
                    "x": 215.0,
                    "y": 402.0
                  },
                  {
                    "x": 175.0,
                    "y": 402.0
                  }
                ]
              },
              "confidence": 0.72651,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            }
          ],
          "provider": "multi_ocr_router",
          "model": "PP-OCRv6-onnx",
          "package": "rapidocr+easyocr+greek_ocr",
          "package_version": "3.9.2",
          "detector_model": "PP-OCRv6_det_small.onnx",
          "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
          "recognizer_language": "en+bn+el",
          "latency_ms": 14451.245300006121,
          "error": null,
          "metadata": {
            "bangla_available": true,
            "greek_available": true,
            "formula_available": false,
            "regions_count": 7,
            "token_count": 7
          }
        }
      },
      {
        "call": "00167_deduplicate_spatial_tokens",
        "return_value": [
          {
            "id": "ocr_tok_007",
            "raw_text": "Fig. 9 Series DC Circuit",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 336.0,
              "y": 817.0,
              "width": 603.0,
              "height": 70.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 336.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 817.0
                },
                {
                  "x": 939.0,
                  "y": 887.0
                },
                {
                  "x": 336.0,
                  "y": 887.0
                }
              ]
            },
            "confidence": 0.97378,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9334288835525513,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "R2 = 20 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1029.0,
              "y": 421.0,
              "width": 241.0,
              "height": 71.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1029.0,
                  "y": 423.0
                },
                {
                  "x": 1270.0,
                  "y": 421.0
                },
                {
                  "x": 1270.0,
                  "y": 490.0
                },
                {
                  "x": 1029.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.90339,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R2 = 20 2",
                "script": "latin",
                "confidence": 0.43002614643260995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "R1 = 10 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 636.0,
              "y": 148.0,
              "width": 242.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 636.0,
                  "y": 151.0
                },
                {
                  "x": 877.0,
                  "y": 148.0
                },
                {
                  "x": 878.0,
                  "y": 213.0
                },
                {
                  "x": 637.0,
                  "y": 216.0
                }
              ]
            },
            "confidence": 0.86803,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R1 = 10 `2",
                "script": "latin",
                "confidence": 0.46127750970800835,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "12 V",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 39.0,
              "y": 426.0,
              "width": 123.0,
              "height": 63.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 39.0,
                  "y": 428.0
                },
                {
                  "x": 161.0,
                  "y": 426.0
                },
                {
                  "x": 162.0,
                  "y": 487.0
                },
                {
                  "x": 40.0,
                  "y": 489.0
                }
              ]
            },
            "confidence": 0.98113,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "12 `",
                "script": "latin",
                "confidence": 0.3936148122970558,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "S",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 378.0,
              "y": 159.0,
              "width": 47.0,
              "height": 53.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 378.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 159.0
                },
                {
                  "x": 425.0,
                  "y": 212.0
                },
                {
                  "x": 378.0,
                  "y": 212.0
                }
              ]
            },
            "confidence": 0.99926,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "I",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 613.0,
              "y": 706.0,
              "width": 39.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 613.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 706.0
                },
                {
                  "x": 652.0,
                  "y": 758.0
                },
                {
                  "x": 613.0,
                  "y": 758.0
                }
              ]
            },
            "confidence": 0.99429,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "十",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 175.0,
              "y": 362.0,
              "width": 40.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 175.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 362.0
                },
                {
                  "x": 215.0,
                  "y": 402.0
                },
                {
                  "x": 175.0,
                  "y": 402.0
                }
              ]
            },
            "confidence": 0.72651,
            "script_candidate": "mixed",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          }
        ]
      },
      {
        "call": "00175_GreekSymbolVisualOCR.extract_symbols",
        "return_value": []
      },
      {
        "call": "00176_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_007",
          "raw_text": "Fig. 9 Series DC Circuit",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 336.0,
            "y": 817.0,
            "width": 603.0,
            "height": 70.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 336.0,
                "y": 817.0
              },
              {
                "x": 939.0,
                "y": 817.0
              },
              {
                "x": 939.0,
                "y": 887.0
              },
              {
                "x": 336.0,
                "y": 887.0
              }
            ]
          },
          "confidence": 0.97378,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9334288835525513,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_007"
        }
      },
      {
        "call": "00178_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_005",
          "raw_text": "R2 = 20 Ω",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1029.0,
            "y": 421.0,
            "width": 241.0,
            "height": 71.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1029.0,
                "y": 423.0
              },
              {
                "x": 1270.0,
                "y": 421.0
              },
              {
                "x": 1270.0,
                "y": 490.0
              },
              {
                "x": 1029.0,
                "y": 492.0
              }
            ]
          },
          "confidence": 0.90339,
          "script_candidate": "greek",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "R2 = 20 2",
              "script": "latin",
              "confidence": 0.43002614643260995,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_005"
        }
      },
      {
        "call": "00180_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_002",
          "raw_text": "R1 = 10 Ω",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 636.0,
            "y": 148.0,
            "width": 242.0,
            "height": 68.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 636.0,
                "y": 151.0
              },
              {
                "x": 877.0,
                "y": 148.0
              },
              {
                "x": 878.0,
                "y": 213.0
              },
              {
                "x": 637.0,
                "y": 216.0
              }
            ]
          },
          "confidence": 0.86803,
          "script_candidate": "greek",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "R1 = 10 `2",
              "script": "latin",
              "confidence": 0.46127750970800835,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      },
      {
        "call": "00182_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_004",
          "raw_text": "12 V",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 39.0,
            "y": 426.0,
            "width": 123.0,
            "height": 63.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 39.0,
                "y": 428.0
              },
              {
                "x": 161.0,
                "y": 426.0
              },
              {
                "x": 162.0,
                "y": 487.0
              },
              {
                "x": 40.0,
                "y": 489.0
              }
            ]
          },
          "confidence": 0.98113,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "12 `",
              "script": "latin",
              "confidence": 0.3936148122970558,
              "provider": "easyocr_bangla"
            },
            {
              "text": "12 V",
              "script": "mixed",
              "name": "voltage_value",
              "confidence": 0.95,
              "provider": "physics_unit_confusable"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_004"
        }
      },
      {
        "call": "00184_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_001",
          "raw_text": "S",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 378.0,
            "y": 159.0,
            "width": 47.0,
            "height": 53.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 378.0,
                "y": 159.0
              },
              {
                "x": 425.0,
                "y": 159.0
              },
              {
                "x": 425.0,
                "y": 212.0
              },
              {
                "x": 378.0,
                "y": 212.0
              }
            ]
          },
          "confidence": 0.99926,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        }
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Merged tokens with retained provenance/alternatives. Preserve literal printed values and symbolic quantities. Do not turn L or m into a numerical length or mass.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Changes, provenance and possible information loss:** OCR alternatives → selected token set. PageIR text blocks are filled from these tokens inside the evidence pipeline.

[Complete stage input/output bundle](stage_data/11_ocr.json)

- [MultiOCRRouter.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00066_MultiOCRRouter.extract/STAGE.html)

- [deduplicate_spatial_tokens — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00167_deduplicate_spatial_tokens/STAGE.html)

- [GreekSymbolVisualOCR.extract_symbols — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00175_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00176_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00178_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00180_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00182_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00184_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00186_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00188_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [Code: ai\evidence\ocr\router.py](contracts/ai/evidence/ocr/router.py)

- [Code: ai\evidence\ocr\greek_symbols.py](contracts/ai/evidence/ocr/greek_symbols.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00066_MultiOCRRouter.extract/actual_overlay_on_source.png)

## 12. Grayscale, blur and edge extraction

**Execution:** EXECUTED. **Verdict:** FRAME PASS / LOSSY PROCESSING.

**Upstream → downstream:** Symbol candidates, deduplication and final OCR → this component → OCR-region suppression before geometry detection.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00197_preprocess_diagram",
    "value": {
      "img_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
      },
      "blur_ksize": [
        5,
        5
      ],
      "blur_sigma": 1.0,
      "canny_thresh1": 50.0,
      "canny_thresh2": 150.0
    }
  }
]
```

**What it should receive — expected input:** Native BGR array and actual Canny/blur settings.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00197_preprocess_diagram",
      "return_value": [
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\0ba8a7e5778191cf5390046b7b11e82d1f0afacfc94a2d90b4adca826f66d795.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\0ba8a7e5778191cf5390046b7b11e82d1f0afacfc94a2d90b4adca826f66d795.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\638c1df586d32feda06d9944317fc908dc89cb609c3d4234da3429f0591dfc3e.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\638c1df586d32feda06d9944317fc908dc89cb609c3d4234da3429f0591dfc3e.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png"
        }
      ]
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Grayscale/blur/edge arrays in the same 1280×960 source frame. Image processing may change intensities, but must not imply a spatial crop/scale that was not performed.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Arrays preserve the source frame. Blur and Canny change image information; no detector correctness is inferred from shape alone.

**Changes, provenance and possible information loss:** Color/intensity information becomes an edge representation. Exact arrays are retained. OpenCV internal per-operation frames were not separately profiled.

[Complete stage input/output bundle](stage_data/12_pre.json)

- [preprocess_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00197_preprocess_diagram/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png)

![0ba8a7e5778191cf5390046b7b11e82d1f0afacfc94a2d90b4adca826f66d795.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/0ba8a7e5778191cf5390046b7b11e82d1f0afacfc94a2d90b4adca826f66d795.png)

![638c1df586d32feda06d9944317fc908dc89cb609c3d4234da3429f0591dfc3e.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/638c1df586d32feda06d9944317fc908dc89cb609c3d4234da3429f0591dfc3e.png)

![c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png)

## 13. OCR-region suppression before geometry detection

**Execution:** EXECUTED. **Verdict:** NO EARLIER GEOMETRIC FAILURE DEMONSTRATED.

**Upstream → downstream:** Grayscale, blur and edge extraction → this component → Domain CV: raw candidates → selected geometry.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00198_mask_out_text_regions",
    "value": {
      "edge_map": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png"
      },
      "ocr_boxes": [
        {
          "x": 336.0,
          "y": 817.0,
          "width": 603.0,
          "height": 70.0
        },
        {
          "x": 1029.0,
          "y": 421.0,
          "width": 241.0,
          "height": 71.0
        },
        {
          "x": 636.0,
          "y": 148.0,
          "width": 242.0,
          "height": 68.0
        },
        {
          "x": 39.0,
          "y": 426.0,
          "width": 123.0,
          "height": 63.0
        },
        {
          "x": 378.0,
          "y": 159.0,
          "width": 47.0,
          "height": 53.0
        },
        {
          "x": 613.0,
          "y": 706.0,
          "width": 39.0,
          "height": 52.0
        },
        {
          "x": 175.0,
          "y": 362.0,
          "width": 40.0,
          "height": 40.0
        }
      ],
      "margin_px": 4
    }
  }
]
```

**What it should receive — expected input:** Actual edge map, selected OCR boxes and margin_px.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00198_mask_out_text_regions",
      "return_value": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** An edge map suppressing text while preserving relevant diagram boundaries/rays. This is the registration requirement; the implementation zeros the entire expanded rectangle without distinguishing text from geometry.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Removed-edge overlay was inspected. No earlier failure explaining the later rail/pivot error is established by this mask capture.

**Changes, provenance and possible information loss:** Every pixel removed by the actual mask is shown in red on the original. A valid OCR box does not guarantee safe geometry suppression.

[Complete stage input/output bundle](stage_data/13_mask.json)

- [mask_out_text_regions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00198_mask_out_text_regions/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![removed_edges_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00198_mask_out_text_regions/removed_edges_on_source.png)

![c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/c4e36da9d2001992b7a9a749be2d9134bd440ff858c17f6a70cac952eb884a27.png)

![e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/arrays/e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.png)

## 14. Domain CV: raw candidates → selected geometry

**Execution:** EXECUTED. **Verdict:** FAIL — PERCEPTION / SELECTION.

**Upstream → downstream:** OCR-region suppression before geometry detection → this component → SAM2 segmentation prompted by CV.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00195_CircuitCVCandidateExtractor.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.npy",
        "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\3d3e7d615137463287492abb8fbf1567d972805989fc625bf6bd0cec8af40ab7.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "ocr_boxes": [
        {
          "x": 336.0,
          "y": 817.0,
          "width": 603.0,
          "height": 70.0
        },
        {
          "x": 1029.0,
          "y": 421.0,
          "width": 241.0,
          "height": 71.0
        },
        {
          "x": 636.0,
          "y": 148.0,
          "width": 242.0,
          "height": 68.0
        },
        {
          "x": 39.0,
          "y": 426.0,
          "width": 123.0,
          "height": 63.0
        },
        {
          "x": 378.0,
          "y": 159.0,
          "width": 47.0,
          "height": 53.0
        },
        {
          "x": 613.0,
          "y": 706.0,
          "width": 39.0,
          "height": 52.0
        },
        {
          "x": 175.0,
          "y": 362.0,
          "width": 40.0,
          "height": 40.0
        }
      ]
    }
  }
]
```

**What it should receive — expected input:** Image/edge evidence and OCR boxes in source pixels, with no hand-authored landmarks.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00195_CircuitCVCandidateExtractor.extract",
      "return_value": {
        "components": [],
        "wires": {
          "count": 15,
          "first_8_records": [
            {
              "start": {
                "x": 230.0,
                "y": 253.0
              },
              "end": {
                "x": 345.0,
                "y": 253.0
              }
            },
            {
              "start": {
                "x": 230.0,
                "y": 672.0
              },
              "end": {
                "x": 993.0,
                "y": 672.0
              }
            },
            {
              "start": {
                "x": 228.0,
                "y": 669.0
              },
              "end": {
                "x": 228.0,
                "y": 508.0
              }
            },
            {
              "start": {
                "x": 473.0,
                "y": 666.0
              },
              "end": {
                "x": 591.0,
                "y": 666.0
              }
            },
            {
              "start": {
                "x": 234.0,
                "y": 421.0
              },
              "end": {
                "x": 234.0,
                "y": 259.0
              }
            },
            {
              "start": {
                "x": 989.0,
                "y": 386.0
              },
              "end": {
                "x": 989.0,
                "y": 253.0
              }
            },
            {
              "start": {
                "x": 547.0,
                "y": 697.0
              },
              "end": {
                "x": 713.0,
                "y": 697.0
              }
            },
            {
              "start": {
                "x": 995.0,
                "y": 669.0
              },
              "end": {
                "x": 995.0,
                "y": 543.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "junctions": [
          {
            "x": 230.0,
            "y": 253.0
          },
          {
            "x": 230.0,
            "y": 672.0
          },
          {
            "x": 993.0,
            "y": 672.0
          },
          {
            "x": 234.0,
            "y": 421.0
          }
        ],
        "rails_y": [
          255,
          416,
          668
        ],
        "branches_x": [
          231,
          992
        ],
        "edges": {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.png"
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Source-supported candidate lines/circles/polygons and selected geometry, with scores, rejection/selection diagnostics and unresolved ambiguity where evidence is insufficient.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** components=[]; branches_x=[231,992]; rails_y=[255,416,668]. Returned rails span x=231→992 at all three Y values. y=416 crosses empty circuit interior; y=255 bridges the open switch/components. The implementation accepts a span with more than ten edge pixels, without requiring continuous wire support.

**Changes, provenance and possible information loss:** Candidate generation and selection are distinct. Compare all_candidates_overlay with selected output; inspect locals for fitted lines, rejected candidates and thresholds.

[Complete stage input/output bundle](stage_data/14_cv.json)

- [CircuitCVCandidateExtractor.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00195_CircuitCVCandidateExtractor.extract/STAGE.html)

- [Code: ai\evidence\cv\circuits_cv.py](contracts/ai/evidence/cv/circuits_cv.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00195_CircuitCVCandidateExtractor.extract/actual_overlay_on_source.png)

![all_candidates_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00195_CircuitCVCandidateExtractor.extract/all_candidates_overlay.png)

## 15. SAM2 segmentation prompted by CV

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** Domain CV: raw candidates → selected geometry → this component → Semantic-to-spatial grounding and parameter binding.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Source image plus the actual CV-provided box/point prompts, with prompt provenance.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Segmentation mask, score, centroid, area and source bbox. Segmentation only supports the prompted object; it cannot certify unrelated geometry.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result. The active segmentation trigger requires a best_proposal.bob; this domain did not produce that trigger.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/15_sam.json)

## 16. Semantic-to-spatial grounding and parameter binding

**Execution:** EXECUTED. **Verdict:** FAIL / UPSTREAM DAMAGE PROPAGATES.

**Upstream → downstream:** SAM2 segmentation prompted by CV → this component → Grounded BookIR and OCR-enriched PageIR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01183_CircuitGrounder.ground",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "voltage_source_1",
            "type": "voltage_source",
            "label": "12 V",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_1",
            "type": "resistor",
            "label": "R1 = 10 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_2",
            "type": "resistor",
            "label": "R2 = 20 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "wire_1",
            "type": "wire",
            "label": "I",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "cv_candidates": {
        "components": [],
        "wires": {
          "count": 15,
          "first_8_records": [
            {
              "start": {
                "x": 230.0,
                "y": 253.0
              },
              "end": {
                "x": 345.0,
                "y": 253.0
              }
            },
            {
              "start": {
                "x": 230.0,
                "y": 672.0
              },
              "end": {
                "x": 993.0,
                "y": 672.0
              }
            },
            {
              "start": {
                "x": 228.0,
                "y": 669.0
              },
              "end": {
                "x": 228.0,
                "y": 508.0
              }
            },
            {
              "start": {
                "x": 473.0,
                "y": 666.0
              },
              "end": {
                "x": 591.0,
                "y": 666.0
              }
            },
            {
              "start": {
                "x": 234.0,
                "y": 421.0
              },
              "end": {
                "x": 234.0,
                "y": 259.0
              }
            },
            {
              "start": {
                "x": 989.0,
                "y": 386.0
              },
              "end": {
                "x": 989.0,
                "y": 253.0
              }
            },
            {
              "start": {
                "x": 547.0,
                "y": 697.0
              },
              "end": {
                "x": 713.0,
                "y": 697.0
              }
            },
            {
              "start": {
                "x": 995.0,
                "y": 669.0
              },
              "end": {
                "x": 995.0,
                "y": 543.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "junctions": [
          {
            "x": 230.0,
            "y": 253.0
          },
          {
            "x": 230.0,
            "y": 672.0
          },
          {
            "x": 993.0,
            "y": 672.0
          },
          {
            "x": 234.0,
            "y": 421.0
          }
        ],
        "rails_y": [
          255,
          416,
          668
        ],
        "branches_x": [
          231,
          992
        ],
        "edges": {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.npy",
          "image": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017\\arrays\\e43fd5c1f17898d796fc4383315ee7be81c112e7ccb418ec93c4483ed9cd79a2.png"
        }
      },
      "ocr_result": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_007",
            "raw_text": "Fig. 9 Series DC Circuit",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 336.0,
              "y": 817.0,
              "width": 603.0,
              "height": 70.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.97378,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9334288835525513,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "R2 = 20 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1029.0,
              "y": 421.0,
              "width": 241.0,
              "height": 71.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.90339,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R2 = 20 2",
                "script": "latin",
                "confidence": 0.43002614643260995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "R1 = 10 Ω",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 636.0,
              "y": 148.0,
              "width": 242.0,
              "height": 68.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.86803,
            "script_candidate": "greek",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "R1 = 10 `2",
                "script": "latin",
                "confidence": 0.46127750970800835,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "12 V",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 39.0,
              "y": 426.0,
              "width": 123.0,
              "height": 63.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.98113,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "12 `",
                "script": "latin",
                "confidence": 0.3936148122970558,
                "provider": "easyocr_bangla"
              },
              {
                "text": "12 V",
                "script": "mixed",
                "name": "voltage_value",
                "confidence": 0.95,
                "provider": "physics_unit_confusable"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "S",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 378.0,
              "y": 159.0,
              "width": 47.0,
              "height": 53.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99926,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "I",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 613.0,
              "y": 706.0,
              "width": 39.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99429,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "1",
                "script": "numeric",
                "name": "one",
                "confidence": 0.845,
                "provider": "confusable_resolver"
              },
              {
                "text": "l",
                "script": "latin",
                "name": "length_l",
                "confidence": 0.795,
                "provider": "confusable_resolver"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "十",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 175.0,
              "y": 362.0,
              "width": 40.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.72651,
            "script_candidate": "mixed",
            "language_candidate": "und",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          }
        ],
        "provider": "multi_ocr_router",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr+easyocr+greek_ocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
        "recognizer_language": "en+bn+el",
        "latency_ms": 14451.245300006121,
        "error": null,
        "metadata": {
          "bangla_available": true,
          "greek_available": true,
          "formula_available": false,
          "regions_count": 7,
          "token_count": 7
        }
      },
      "seg_result": null,
      "source_width": 1280,
      "source_height": 960
    }
  }
]
```

**What it should receive — expected input:** Semantic BookIR plus raw CV candidates, OCR result and optional segmentation result.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01183_CircuitGrounder.ground",
      "return_value": {
        "grounded_book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "diagnostics": [
          {
            "entity_id": "R2",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ],
            "checks": {
              "wire_connected": true
            },
            "conflicts": [],
            "notes": "Component grounded as R2 (resistor) with visual leads at (1149.0, 416.0)."
          },
          {
            "entity_id": "R1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ],
            "checks": {
              "wire_connected": true
            },
            "conflicts": [],
            "notes": "Component grounded as R1 (resistor) with visual leads at (757.0, 255.0)."
          },
          {
            "entity_id": "V1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ],
            "checks": {
              "wire_connected": true
            },
            "conflicts": [],
            "notes": "Component grounded as V1 (voltage_source) with visual leads at (231.0, 457.0)."
          }
        ],
        "new_evidence_records": {
          "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff": {
            "id": "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
            "method": "classical_cv",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": null,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "circuit_cv_extractor",
            "model": null,
            "version": null,
            "payload": {
              "component_count": 0,
              "wire_count": 15,
              "junction_count": 4
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_007": {
            "id": "ev_ocr_ocr_tok_007",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.97378,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Fig. 9 Series DC Circuit",
              "bbox": {
                "x": 336.0,
                "y": 817.0,
                "width": 603.0,
                "height": 70.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_005": {
            "id": "ev_ocr_ocr_tok_005",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.90339,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "R2 = 20 Ω",
              "bbox": {
                "x": 1029.0,
                "y": 421.0,
                "width": 241.0,
                "height": 71.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_002": {
            "id": "ev_ocr_ocr_tok_002",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.86803,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "R1 = 10 Ω",
              "bbox": {
                "x": 636.0,
                "y": 148.0,
                "width": 242.0,
                "height": 68.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_004": {
            "id": "ev_ocr_ocr_tok_004",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.98113,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "12 V",
              "bbox": {
                "x": 39.0,
                "y": 426.0,
                "width": 123.0,
                "height": 63.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_001": {
            "id": "ev_ocr_ocr_tok_001",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.99926,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "S",
              "bbox": {
                "x": 378.0,
                "y": 159.0,
                "width": 47.0,
                "height": 53.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_006": {
            "id": "ev_ocr_ocr_tok_006",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.99429,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "I",
              "bbox": {
                "x": 613.0,
                "y": 706.0,
                "width": 39.0,
                "height": 52.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_003": {
            "id": "ev_ocr_ocr_tok_003",
            "method": "ocr",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "figure_id": "figure_001",
            "confidence": 0.72651,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "十",
              "bbox": {
                "x": 175.0,
                "y": 362.0,
                "width": 40.0,
                "height": 40.0
              }
            },
            "metadata": {}
          }
        },
        "candidate_parameters": [
          {
            "raw_text": "R2 = 20 Ω",
            "numeric_value": 20.0,
            "raw_unit": "Ω",
            "canonical_unit": "ohm",
            "quantity_candidate": "resistance",
            "source_ocr_token_id": "ocr_tok_005",
            "confidence": 0.90339
          },
          {
            "raw_text": "R2 = 20 2",
            "numeric_value": 20.0,
            "raw_unit": "2",
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_005",
            "confidence": 0.813
          },
          {
            "raw_text": "R1 = 10 Ω",
            "numeric_value": 10.0,
            "raw_unit": "Ω",
            "canonical_unit": "ohm",
            "quantity_candidate": "resistance",
            "source_ocr_token_id": "ocr_tok_002",
            "confidence": 0.86803
          },
          {
            "raw_text": "R1 = 10 `2",
            "numeric_value": 10.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_002",
            "confidence": 0.781
          },
          {
            "raw_text": "R1 = 10 `2",
            "numeric_value": 2.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_002",
            "confidence": 0.781
          },
          {
            "raw_text": "12 V",
            "numeric_value": 12.0,
            "raw_unit": "V",
            "canonical_unit": "V",
            "quantity_candidate": "voltage",
            "source_ocr_token_id": "ocr_tok_004",
            "confidence": 0.98113
          },
          {
            "raw_text": "12 `",
            "numeric_value": 12.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_004",
            "confidence": 0.883
          },
          {
            "raw_text": "1",
            "numeric_value": 1.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_006",
            "confidence": 0.895
          }
        ],
        "parameter_associations": [
          {
            "candidate_id": "assoc_R2_resistance",
            "target_entity_id": "R2",
            "target_quantity": "resistance",
            "value": 20.0,
            "unit": "ohm",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_005",
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff"
            ],
            "association_checks": {},
            "confidence": 0.95,
            "diagnostics": {}
          },
          {
            "candidate_id": "assoc_R1_resistance",
            "target_entity_id": "R1",
            "target_quantity": "resistance",
            "value": 10.0,
            "unit": "ohm",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_002",
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff"
            ],
            "association_checks": {},
            "confidence": 0.95,
            "diagnostics": {}
          },
          {
            "candidate_id": "assoc_V1_voltage",
            "target_entity_id": "V1",
            "target_quantity": "voltage",
            "value": 12.0,
            "unit": "V",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_004",
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff"
            ],
            "association_checks": {},
            "confidence": 0.95,
            "diagnostics": {}
          },
          {
            "candidate_id": "assoc_ocr_tok_006",
            "target_entity_id": null,
            "target_quantity": "unknown",
            "value": 1.0,
            "unit": "",
            "state": "rejected",
            "supporting_evidence": [],
            "association_checks": {},
            "confidence": 0.895,
            "diagnostics": {}
          }
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Entities bound to supported source geometry; numeric OCR values attached to the correct entity with units/evidence; relationships still resolve after any entity changes. Unresolved evidence stays unresolved.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** CircuitGrounder creates R2 at (1149,416), with horizontal terminals (1115,416)/(1183,416), near the OCR label instead of the vertical resistor. It creates R1=(757,255), V1=(231,457), but nodes and component node lists are empty. Renaming semantic entity IDs to R1/R2/V1 leaves old relationship endpoints dangling. The switch is not grounded.

**Changes, provenance and possible information loss:** This is where semantic roles become authoritative source coordinates. Inspect grounded_book_ir, diagnostics, candidate_parameters and associations separately.

[Complete stage input/output bundle](stage_data/16_ground.json)

- [CircuitGrounder.ground — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01183_CircuitGrounder.ground/STAGE.html)

- [Code: ai\evidence\grounding\circuits.py](contracts/ai/evidence/grounding/circuits.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01183_CircuitGrounder.ground/actual_overlay_on_source.png)

## 17. Grounded BookIR and OCR-enriched PageIR

**Execution:** EXECUTED. **Verdict:** FAIL / UPSTREAM DAMAGE PROPAGATES.

**Upstream → downstream:** Semantic-to-spatial grounding and parameter binding → this component → Enforce authoritative source dimensions.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00054_EvidenceExtractionPipeline.extract_and_fuse",
    "value": {
      "asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [],
        "metadata": {
          "pipeline": "PR-04-standalone-upload",
          "note": "Single-diagram upload. figure_001 is the entire image. Text blocks populated downstream by PR-06 evidence pipeline."
        }
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "voltage_source_1",
            "type": "voltage_source",
            "label": "12 V",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_1",
            "type": "resistor",
            "label": "R1 = 10 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "resistor_2",
            "type": "resistor",
            "label": "R2 = 20 Ω",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          },
          {
            "id": "wire_1",
            "type": "wire",
            "label": "I",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** Original SourceAsset/PageIR and initial semantic BookIR at entry; child stages provide OCR, CV, SAM and grounder results.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00054_EvidenceExtractionPipeline.extract_and_fuse",
      "return_value": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_005"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_002"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_004"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029.0,
                421.0,
                241.0,
                71.0
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                636.0,
                148.0,
                242.0,
                68.0
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12.0,
              "unit": "V",
              "label_bbox_source_px": [
                39.0,
                426.0,
                123.0,
                63.0
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "length_px": 115.0
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "length_px": 763.0
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "points": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "length_px": 161.0
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "points": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "length_px": 118.0
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "points": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "length_px": 162.0
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "length_px": 133.0
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "points": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "length_px": 166.0
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "points": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "length_px": 126.0
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    }
  ],
  "in_place_outputs": [
    {
      "call": "00054_EvidenceExtractionPipeline.extract_and_fuse",
      "page_ir_after": {
        "version": "1.0",
        "source": {
          "assetId": "9b910bff7ee74e90a1763e5358b474ff",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_9b910bff.jpg",
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "coordinate_space": {
          "type": "source_px",
          "width": 1280,
          "height": 960,
          "origin": "top_left"
        },
        "regions": [
          {
            "id": "region_001",
            "label": "whole_image",
            "x": 0.0,
            "y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "confidence": 1.0,
            "detection_method": "user_supplied",
            "notes": "Whole image supplied directly by user; no sub-figure detection performed yet."
          }
        ],
        "figures": [
          {
            "id": "figure_001",
            "region_id": "region_001",
            "page_x": 0.0,
            "page_y": 0.0,
            "width": 1280.0,
            "height": 960.0,
            "detection_method": "user_supplied",
            "notes": "Figure spans the full uploaded image. Automatic figure detection not yet applied."
          }
        ],
        "text_blocks": [
          {
            "id": "ocr_tok_007",
            "text": "Fig. 9 Series DC Circuit",
            "x": 336.0,
            "y": 817.0,
            "width": 603.0,
            "height": 70.0,
            "confidence": 0.97378,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_005",
            "text": "R2 = 20 Ω",
            "x": 1029.0,
            "y": 421.0,
            "width": 241.0,
            "height": 71.0,
            "confidence": 0.90339,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_002",
            "text": "R1 = 10 Ω",
            "x": 636.0,
            "y": 148.0,
            "width": 242.0,
            "height": 68.0,
            "confidence": 0.86803,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_004",
            "text": "12 V",
            "x": 39.0,
            "y": 426.0,
            "width": 123.0,
            "height": 63.0,
            "confidence": 0.98113,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_001",
            "text": "S",
            "x": 378.0,
            "y": 159.0,
            "width": 47.0,
            "height": 53.0,
            "confidence": 0.99926,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_006",
            "text": "I",
            "x": 613.0,
            "y": 706.0,
            "width": 39.0,
            "height": 52.0,
            "confidence": 0.99429,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_003",
            "text": "十",
            "x": 175.0,
            "y": 362.0,
            "width": 40.0,
            "height": 40.0,
            "confidence": 0.72651,
            "extraction_method": "ocr"
          }
        ],
        "metadata": {
          "pipeline": "PR-06",
          "note": "Single-diagram upload. Text blocks populated via PR-06 OCR pipeline.",
          "ocr_provider": "multi_ocr_router"
        }
      }
    }
  ]
}
```

**What it should provide — implemented contract:** Grounded BookIR and PageIR text blocks with original source identity, native dimensions and evidence provenance intact.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** CircuitGrounder creates R2 at (1149,416), with horizontal terminals (1115,416)/(1183,416), near the OCR label instead of the vertical resistor. It creates R1=(757,255), V1=(231,457), but nodes and component node lists are empty. Renaming semantic entity IDs to R1/R2/V1 leaves old relationship endpoints dangling. The switch is not grounded.

**Changes, provenance and possible information loss:** The wrapper returns after stages 8–16. Its entry record comes earlier in the profiler, but its output belongs here in the data-flow story.

[Complete stage input/output bundle](stage_data/17_fused.json)

- [EvidenceExtractionPipeline.extract_and_fuse — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- [Code: ai\evidence\pipeline.py](contracts/ai/evidence/pipeline.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/actual_overlay_on_source.png)

## 18. Enforce authoritative source dimensions

**Execution:** EXECUTED. **Verdict:** FRAME PASS; GEOMETRY STILL WRONG.

**Upstream → downstream:** Grounded BookIR and OCR-enriched PageIR → this component → Automatic resolution and explicit policy values.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01234_enforce_source_dimensions",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12.0,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "asset": {
        "id": "9b910bff7ee74e90a1763e5358b474ff",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37 (2).jpg",
        "byte_size": 38634,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_9b910bff.jpg"
      }
    }
  }
]
```

**What it should receive — expected input:** Grounded BookIR and the actual source dimensions.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01234_enforce_source_dimensions",
      "return_value": null
    }
  ],
  "in_place_outputs": [
    {
      "call": "01234_enforce_source_dimensions",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "status_notes": "Circuit source, component values, or wire continuity require review.",
          "calibration": null,
          "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
          "isPhysics": true,
          "_nested_fields_in_complete_snapshot": [
            "entities",
            "relationships",
            "parameters",
            "geometry",
            "assumptions",
            "provenance",
            "evidence",
            "confidence",
            "resolutions",
            "review_issues",
            "parameter_provenance"
          ]
        }
      }
    }
  ]
}
```

**What it should provide — implemented contract:** Consistent source width/height/frame metadata. Existing landmark positions must not be rescaled to unrelated viewport dimensions.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Source extent is enforced without correcting the already incorrect landmark/topology evidence.

**Changes, provenance and possible information loss:** Metadata enforcement is not geometric validation. Mutation is recorded in locals_after when the function returns None.

[Complete stage input/output bundle](stage_data/18_dimensions.json)

- [enforce_source_dimensions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01234_enforce_source_dimensions/STAGE.html)

- [Code: ai\ingestion\source_dimensions.py](contracts/ai/ingestion/source_dimensions.py)

## 19. Automatic resolution and explicit policy values

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Enforce authoritative source dimensions → this component → Resolution decisions, units and calibration.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01235_AutoResolutionEngine.resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12.0,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** Grounded but possibly incomplete BookIR, including missing values and provenance.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01235_AutoResolutionEngine.resolve",
      "return_value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "assumptions": [],
        "failures": [
          {
            "code": "TOPOLOGY_INVALID",
            "message": "Circuit continuity is not grounded."
          }
        ],
        "readiness": {
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "ready": false,
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "book_ir_id",
            "resolved_requirements",
            "policy_assumptions",
            "unresolved_ambiguities",
            "calibration_status"
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Resolutions/assumptions/failures with honest evidentiary sources. For this debugging objective, an assumed exploration value must not be mistaken for a source observation or a successful registration.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit.

**Changes, provenance and possible information loss:** Inspect field_changes.json for every addition/replacement. Auto-policy execution in this checkout may satisfy requirements without a human decision; that is observed behavior, not approval supplied during tracing.

[Complete stage input/output bundle](stage_data/19_auto.json)

- [AutoResolutionEngine.resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01235_AutoResolutionEngine.resolve/STAGE.html)

- [Every changed field before/after](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01235_AutoResolutionEngine.resolve/field_changes.json)

- [Code: ai\resolution\auto.py](contracts/ai/resolution/auto.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01235_AutoResolutionEngine.resolve/actual_overlay_on_source.png)

## 20. Resolution decisions, units and calibration

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Automatic resolution and explicit policy values → this component → Requirement and ambiguity analysis.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 9,
  "first_8_records": [
    {
      "call": "01257_ResolutionEngine.auto_resolve",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01259_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "dc_linear",
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_005"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_002"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_004"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029.0,
                421.0,
                241.0,
                71.0
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                636.0,
                148.0,
                242.0,
                68.0
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12.0,
              "unit": "V",
              "label_bbox_source_px": [
                39.0,
                426.0,
                123.0,
                63.0
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "length_px": 115.0
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "length_px": 763.0
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "points": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "length_px": 161.0
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "points": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "length_px": 118.0
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "points": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "length_px": 162.0
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "length_px": 133.0
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "points": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "length_px": 166.0
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "points": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "length_px": 126.0
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        }
      }
    },
    {
      "call": "01260_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "dc_linear",
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_005"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_002"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_004"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029.0,
                421.0,
                241.0,
                71.0
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10.0,
              "unit": "ohm",
              "label_bbox_source_px": [
                636.0,
                148.0,
                242.0,
                68.0
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12.0,
              "unit": "V",
              "label_bbox_source_px": [
                39.0,
                426.0,
                123.0,
                63.0
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    253.0
                  ],
                  [
                    345.0,
                    253.0
                  ]
                ],
                "length_px": 115.0
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "points": [
                  [
                    230.0,
                    672.0
                  ],
                  [
                    993.0,
                    672.0
                  ]
                ],
                "length_px": 763.0
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "points": [
                  [
                    228.0,
                    669.0
                  ],
                  [
                    228.0,
                    508.0
                  ]
                ],
                "length_px": 161.0
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "points": [
                  [
                    473.0,
                    666.0
                  ],
                  [
                    591.0,
                    666.0
                  ]
                ],
                "length_px": 118.0
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "points": [
                  [
                    234.0,
                    421.0
                  ],
                  [
                    234.0,
                    259.0
                  ]
                ],
                "length_px": 162.0
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "points": [
                  [
                    989.0,
                    386.0
                  ],
                  [
                    989.0,
                    253.0
                  ]
                ],
                "length_px": 133.0
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "points": [
                  [
                    547.0,
                    697.0
                  ],
                  [
                    713.0,
                    697.0
                  ]
                ],
                "length_px": 166.0
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "points": [
                  [
                    995.0,
                    669.0
                  ],
                  [
                    995.0,
                    543.0
                  ]
                ],
                "length_px": 126.0
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        }
      }
    },
    {
      "call": "01287_ResolutionEngine.auto_resolve",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "R1_resistance": {
              "value": 10,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "V1_voltage": {
              "value": 12,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149,
                "y": 416,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119,
                  "y": 391,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 1115,
                  "y": 416
                },
                "terminal_2": {
                  "x": 1183,
                  "y": 416
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757,
                "y": 255,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727,
                  "y": 230,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 723,
                  "y": 255
                },
                "terminal_2": {
                  "x": 791,
                  "y": 255
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231,
                "y": 457,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206,
                  "y": 427,
                  "width": 50,
                  "height": 60
                },
                "terminal_1": {
                  "x": 231,
                  "y": 423
                },
                "terminal_2": {
                  "x": 231,
                  "y": 491
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01289_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "dc_linear",
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_005"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_002"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_004"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029,
                421,
                241,
                71
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10,
              "unit": "ohm",
              "label_bbox_source_px": [
                636,
                148,
                242,
                68
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12,
              "unit": "V",
              "label_bbox_source_px": [
                39,
                426,
                123,
                63
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "points": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "length_px": 115
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "points": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "length_px": 763
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "points": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "length_px": 161
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "points": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "length_px": 118
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "points": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "length_px": 162
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "points": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "length_px": 133
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "points": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "length_px": 166
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "points": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "length_px": 126
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        }
      }
    },
    {
      "call": "01290_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "dc_linear",
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_005"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_002"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_004"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029,
                421,
                241,
                71
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10,
              "unit": "ohm",
              "label_bbox_source_px": [
                636,
                148,
                242,
                68
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12,
              "unit": "V",
              "label_bbox_source_px": [
                39,
                426,
                123,
                63
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "points": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "length_px": 115
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "points": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "length_px": 763
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "points": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "length_px": 161
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "points": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "length_px": 118
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "points": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "length_px": 162
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "points": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "length_px": 133
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "points": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "length_px": 166
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "points": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "length_px": 126
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        }
      }
    },
    {
      "call": "01352_ResolutionEngine.auto_resolve",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "R1_resistance": {
              "value": 10,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "V1_voltage": {
              "value": 12,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149,
                "y": 416,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119,
                  "y": 391,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 1115,
                  "y": 416
                },
                "terminal_2": {
                  "x": 1183,
                  "y": 416
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757,
                "y": 255,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727,
                  "y": 230,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 723,
                  "y": 255
                },
                "terminal_2": {
                  "x": 791,
                  "y": 255
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231,
                "y": 457,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206,
                  "y": 427,
                  "width": 50,
                  "height": 60
                },
                "terminal_1": {
                  "x": 231,
                  "y": 423
                },
                "terminal_2": {
                  "x": 231,
                  "y": 491
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01354_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "dc_linear",
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_005"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_005"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_002"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_002"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_004"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_004"
              ],
              "confidence": 0.95,
              "notes": ""
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "nodes": [],
              "value": 20,
              "unit": "ohm",
              "label_bbox_source_px": [
                1029,
                421,
                241,
                71
              ],
              "terminals": [
                {
                  "id": "R2.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R2.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "R1",
              "type": "resistor",
              "nodes": [],
              "value": 10,
              "unit": "ohm",
              "label_bbox_source_px": [
                636,
                148,
                242,
                68
              ],
              "terminals": [
                {
                  "id": "R1.t1",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "R1.t2",
                  "node": null,
                  "polarity": null,
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "nodes": [],
              "value": 12,
              "unit": "V",
              "label_bbox_source_px": [
                39,
                426,
                123,
                63
              ],
              "terminals": [
                {
                  "id": "V1.t1",
                  "node": null,
                  "polarity": "+",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                },
                {
                  "id": "V1.t2",
                  "node": null,
                  "polarity": "-",
                  "_nested_fields_in_complete_snapshot": [
                    "source_px"
                  ]
                }
              ],
              "geometry": {
                "_nested_fields_in_complete_snapshot": [
                  "bbox_source_px",
                  "center_source_px",
                  "label_bbox_source_px"
                ]
              }
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "points": [
                  [
                    230,
                    253
                  ],
                  [
                    345,
                    253
                  ]
                ],
                "length_px": 115
              },
              {
                "id": "wire_2",
                "node": null,
                "polyline_source_px": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "points": [
                  [
                    230,
                    672
                  ],
                  [
                    993,
                    672
                  ]
                ],
                "length_px": 763
              },
              {
                "id": "wire_3",
                "node": null,
                "polyline_source_px": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "points": [
                  [
                    228,
                    669
                  ],
                  [
                    228,
                    508
                  ]
                ],
                "length_px": 161
              },
              {
                "id": "wire_4",
                "node": null,
                "polyline_source_px": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "points": [
                  [
                    473,
                    666
                  ],
                  [
                    591,
                    666
                  ]
                ],
                "length_px": 118
              },
              {
                "id": "wire_5",
                "node": null,
                "polyline_source_px": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "points": [
                  [
                    234,
                    421
                  ],
                  [
                    234,
                    259
                  ]
                ],
                "length_px": 162
              },
              {
                "id": "wire_6",
                "node": null,
                "polyline_source_px": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "points": [
                  [
                    989,
                    386
                  ],
                  [
                    989,
                    253
                  ]
                ],
                "length_px": 133
              },
              {
                "id": "wire_7",
                "node": null,
                "polyline_source_px": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "points": [
                  [
                    547,
                    697
                  ],
                  [
                    713,
                    697
                  ]
                ],
                "length_px": 166
              },
              {
                "id": "wire_8",
                "node": null,
                "polyline_source_px": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "points": [
                  [
                    995,
                    669
                  ],
                  [
                    995,
                    543
                  ]
                ],
                "length_px": 126
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        }
      }
    }
  ],
  "complete_list": "See complete stage bundle / original artifact"
}
```

**What it should receive — expected input:** Grounded values, policy resolutions, units and any supported pixel/physical-length pairs.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": {
    "count": 9,
    "first_8_records": [
      {
        "call": "01257_ResolutionEngine.auto_resolve",
        "return_value": {
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "ready": false,
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "book_ir_id",
            "resolved_requirements",
            "policy_assumptions",
            "unresolved_ambiguities",
            "calibration_status"
          ]
        }
      },
      {
        "call": "01259_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "01260_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "01287_ResolutionEngine.auto_resolve",
        "return_value": {
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "ready": false,
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "book_ir_id",
            "resolved_requirements",
            "policy_assumptions",
            "unresolved_ambiguities",
            "calibration_status"
          ]
        }
      },
      {
        "call": "01289_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "01290_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "01352_ResolutionEngine.auto_resolve",
        "return_value": {
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "ready": false,
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "book_ir_id",
            "resolved_requirements",
            "policy_assumptions",
            "unresolved_ambiguities",
            "calibration_status"
          ]
        }
      },
      {
        "call": "01354_CalibrationEngine.derive_for_subtype",
        "return_value": null
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Consistent resolved units and explicit calibration provenance. A scale derived using assumed physical length must remain assumption-derived; it is not measured ground truth.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit.

**Changes, provenance and possible information loss:** Several calls can occur inside auto-resolution. Exact invocation records are kept separately; null return can mean calibration was unavailable, not that a zero scale was measured.

[Complete stage input/output bundle](stage_data/20_calibration.json)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01257_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01259_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01260_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01287_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01289_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01290_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01352_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01354_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01355_CalibrationEngine.derive_for_subtype/STAGE.html)

- [Code: ai\resolution\engine.py](contracts/ai/resolution/engine.py)

- [Code: ai\resolution\calibration.py](contracts/ai/resolution/calibration.py)

## 21. Requirement and ambiguity analysis

**Execution:** EXECUTED. **Verdict:** BLOCKS CORRECTLY.

**Upstream → downstream:** Resolution decisions, units and calibration → this component → Readiness decision.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 28,
  "first_8_records": [
    {
      "call": "01239_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01241_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "spec": {
          "domain": "circuits",
          "subtype": "dc_linear",
          "required_entities": [
            "resistor"
          ],
          "required_geometry": [],
          "parameters": {
            "nodes": {
              "id": "req_circuits_nodes",
              "name": "nodes",
              "dimension": "topology_nodes",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "components": {
              "id": "req_circuits_components",
              "name": "components",
              "dimension": "topology_components",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            }
          },
          "mutually_exclusive_requirements": [],
          "one_of_requirements": [],
          "allowed_policies": [],
          "parameter_aliases": {},
          "notes": "Modified Nodal Analysis (MNA) matrix solver for DC resistor networks."
        },
        "issues": []
      }
    },
    {
      "call": "01242_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "spec": {
          "domain": "circuits",
          "subtype": "dc_linear",
          "required_entities": [
            "resistor"
          ],
          "required_geometry": [],
          "parameters": {
            "nodes": {
              "id": "req_circuits_nodes",
              "name": "nodes",
              "dimension": "topology_nodes",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "components": {
              "id": "req_circuits_components",
              "name": "components",
              "dimension": "topology_components",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            }
          },
          "mutually_exclusive_requirements": [],
          "one_of_requirements": [],
          "allowed_policies": [],
          "parameter_aliases": {},
          "notes": "Modified Nodal Analysis (MNA) matrix solver for DC resistor networks."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "01244_ResolutionAnalyzer._check_circuit_components",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "issues": []
      }
    },
    {
      "call": "01262_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01264_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "spec": {
          "domain": "circuits",
          "subtype": "dc_linear",
          "required_entities": [
            "resistor"
          ],
          "required_geometry": [],
          "parameters": {
            "nodes": {
              "id": "req_circuits_nodes",
              "name": "nodes",
              "dimension": "topology_nodes",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "components": {
              "id": "req_circuits_components",
              "name": "components",
              "dimension": "topology_components",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            }
          },
          "mutually_exclusive_requirements": [],
          "one_of_requirements": [],
          "allowed_policies": [],
          "parameter_aliases": {},
          "notes": "Modified Nodal Analysis (MNA) matrix solver for DC resistor networks."
        },
        "issues": []
      }
    },
    {
      "call": "01265_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "spec": {
          "domain": "circuits",
          "subtype": "dc_linear",
          "required_entities": [
            "resistor"
          ],
          "required_geometry": [],
          "parameters": {
            "nodes": {
              "id": "req_circuits_nodes",
              "name": "nodes",
              "dimension": "topology_nodes",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "components": {
              "id": "req_circuits_components",
              "name": "components",
              "dimension": "topology_components",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            }
          },
          "mutually_exclusive_requirements": [],
          "one_of_requirements": [],
          "allowed_policies": [],
          "parameter_aliases": {},
          "notes": "Modified Nodal Analysis (MNA) matrix solver for DC resistor networks."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "01267_ResolutionAnalyzer._check_circuit_components",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "position_source_px": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "position_source_px": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidence_refs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "position_source_px": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "page_ir_version",
            "figure_id",
            "provenance",
            "evidence",
            "confidence",
            "status_notes",
            "review_issues",
            "parameter_provenance",
            "id"
          ]
        },
        "issues": []
      }
    }
  ],
  "complete_list": "See complete stage bundle / original artifact"
}
```

**What it should receive — expected input:** Resolved BookIR and subtype-specific ModelRequirementSpec.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": {
    "count": 28,
    "first_8_records": [
      {
        "call": "01239_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "dc_linear",
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "ready_to_compile",
            "book_ir_id",
            "ambiguous_requirements",
            "blockers_count",
            "warnings_count",
            "issues",
            "available_policies",
            "diagnostics"
          ]
        }
      },
      {
        "call": "01241_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "01242_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "01244_ResolutionAnalyzer._check_circuit_components",
        "return_value": null
      },
      {
        "call": "01262_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "dc_linear",
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "missing_requirements": [],
          "satisfied_requirements": [
            "nodes",
            "components"
          ],
          "_other_fields_in_complete_snapshot": [
            "book_ir_status",
            "ready_to_compile",
            "book_ir_id",
            "ambiguous_requirements",
            "blockers_count",
            "warnings_count",
            "issues",
            "available_policies",
            "diagnostics"
          ]
        }
      },
      {
        "call": "01264_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "01265_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "01267_ResolutionAnalyzer._check_circuit_components",
        "return_value": null
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": {
    "count": 21,
    "first_8_records": [
      {
        "call": "01241_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01242_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01244_ResolutionAnalyzer._check_circuit_components",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01264_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01265_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01267_ResolutionAnalyzer._check_circuit_components",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01294_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      },
      {
        "call": "01295_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "circuits",
            "subtype": "dc_linear",
            "status": "NEEDS_REVIEW",
            "status_notes": "Circuit source, component values, or wire continuity require review.",
            "calibration": null,
            "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
            "isPhysics": true,
            "_nested_fields_in_complete_snapshot": [
              "entities",
              "relationships",
              "parameters",
              "geometry",
              "assumptions",
              "provenance",
              "evidence",
              "confidence",
              "resolutions",
              "review_issues",
              "parameter_provenance"
            ]
          }
        }
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  }
}
```

**What it should provide — implemented contract:** Satisfied/missing requirements, issues, blockers and warnings consistent with available evidence. Visual correctness and mere field presence must be evaluated separately.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** The current analyzer checks required entities/parameters and ambiguity. It does not compare every proposed line or point to image pixels.

[Complete stage input/output bundle](stage_data/21_requirements.json)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01239_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01241_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01242_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01244_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01262_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01264_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01265_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01267_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01292_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01294_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01295_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01297_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01310_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01312_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01313_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01315_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01334_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01336_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01337_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01339_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01357_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01359_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01360_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01362_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01376_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01378_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01379_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer._check_circuit_components — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01381_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- [Code: ai\resolution\analyzer.py](contracts/ai/resolution/analyzer.py)

## 22. Readiness decision

**Execution:** EXECUTED. **Verdict:** BLOCKS CORRECTLY.

**Upstream → downstream:** Requirement and ambiguity analysis → this component → PhysicsCompiler entry and gate.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01238_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12.0,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  },
  {
    "call": "01261_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12.0,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  },
  {
    "call": "01291_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  },
  {
    "call": "01333_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  },
  {
    "call": "01356_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  },
  {
    "call": "01375_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "R1_resistance": {
            "value": 10,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "V1_voltage": {
            "value": 12,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149,
              "y": 416,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119,
                "y": 391,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 1115,
                "y": 416
              },
              "terminal_2": {
                "x": 1183,
                "y": 416
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757,
              "y": 255,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727,
                "y": 230,
                "width": 60,
                "height": 50
              },
              "terminal_1": {
                "x": 723,
                "y": 255
              },
              "terminal_2": {
                "x": 791,
                "y": 255
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231,
              "y": 457,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206,
                "y": 427,
                "width": 50,
                "height": 60
              },
              "terminal_1": {
                "x": 231,
                "y": 423
              },
              "terminal_2": {
                "x": 231,
                "y": 491
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      },
      "mutate_status": true
    }
  }
]
```

**What it should receive — expected input:** BookIR, analyzer issues, parameter values, units/ranges and resolution provenance.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01238_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    },
    {
      "call": "01261_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    },
    {
      "call": "01291_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    },
    {
      "call": "01333_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    },
    {
      "call": "01356_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    },
    {
      "call": "01375_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Circuit component R2 has no valid two-node connection.",
          "Circuit component R1 has no valid two-node connection.",
          "Circuit component V1 has no valid two-node connection."
        ],
        "warnings": [
          "A switch is present and will be initialized in the interactive simulation."
        ],
        "missing_requirements": [],
        "satisfied_requirements": [
          "nodes",
          "components"
        ],
        "_other_fields_in_complete_snapshot": [
          "book_ir_status",
          "book_ir_id",
          "resolved_requirements",
          "policy_assumptions",
          "unresolved_ambiguities",
          "calibration_status"
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** READY_TO_COMPILE only when implemented invariants pass; missing/invalid topology should block. For faithful reconstruction, passing these invariants must not be interpreted as proof of source registration.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** All repeated evaluations are recorded. Use the final pre-compile decision as the gate, while retaining earlier decisions to see state changes.

[Complete stage input/output bundle](stage_data/22_readiness.json)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01238_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01261_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01291_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01333_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01356_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01375_ReadinessEvaluator.evaluate/STAGE.html)

- [Code: ai\resolution\evaluator.py](contracts/ai/resolution/evaluator.py)

## 23. PhysicsCompiler entry and gate

**Execution:** EXECUTED. **Verdict:** SAFE NULL SCENE.

**Upstream → downstream:** Readiness decision → this component → Canonical scene construction and schema validation.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01280_PhysicsCompiler.compile",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "circuits",
        "subtype": "dc_linear",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "circuit_topology": {
            "verified_connectivity": false,
            "node_count": 0
          }
        },
        "parameters": {
          "R2_resistance": {
            "value": 20.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "R1_resistance": {
            "value": 10.0,
            "unit": "ohm",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "V1_voltage": {
            "value": 12.0,
            "unit": "V",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.95,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "components": [
            {
              "id": "R2",
              "type": "resistor",
              "value": 20.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "value": 10.0,
              "unit": "ohm",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "value": 12.0,
              "unit": "V",
              "_nested_fields_in_complete_snapshot": [
                "nodes",
                "label_bbox_source_px",
                "terminals",
                "geometry"
              ]
            }
          ],
          "nodes": [],
          "wires": {
            "count": 15,
            "first_8_records": [
              {
                "id": "wire_1",
                "node": null,
                "length_px": 115.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_2",
                "node": null,
                "length_px": 763.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_3",
                "node": null,
                "length_px": 161.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_4",
                "node": null,
                "length_px": 118.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_5",
                "node": null,
                "length_px": 162.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_6",
                "node": null,
                "length_px": 133.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_7",
                "node": null,
                "length_px": 166.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              },
              {
                "id": "wire_8",
                "node": null,
                "length_px": 126.0,
                "_nested_fields_in_complete_snapshot": [
                  "polyline_source_px",
                  "points"
                ]
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "reference_node": "N0"
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "R2",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 1149.0,
              "y": 416.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 1119.0,
                "y": 391.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 1115.0,
                "y": 416.0
              },
              "terminal_2": {
                "x": 1183.0,
                "y": 416.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_005"
            ]
          },
          {
            "id": "R1",
            "type": "resistor",
            "label": null,
            "position_source_px": {
              "x": 757.0,
              "y": 255.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 727.0,
                "y": 230.0,
                "width": 60.0,
                "height": 50.0
              },
              "terminal_1": {
                "x": 723.0,
                "y": 255.0
              },
              "terminal_2": {
                "x": 791.0,
                "y": 255.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "V1",
            "type": "voltage_source",
            "label": null,
            "position_source_px": {
              "x": 231.0,
              "y": 457.0,
              "coordinate_space": "source_px",
              "method": "cv_circuit_component"
            },
            "geometry": {
              "bounds": {
                "x": 206.0,
                "y": 427.0,
                "width": 50.0,
                "height": 60.0
              },
              "terminal_1": {
                "x": 231.0,
                "y": 423.0
              },
              "terminal_2": {
                "x": 231.0,
                "y": 491.0
              },
              "wire_connected": true,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {},
            "evidence_refs": [
              "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
              "ev_ocr_ocr_tok_004"
            ]
          },
          {
            "id": "switch_1",
            "type": "switch",
            "label": "S",
            "position_source_px": null,
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "figure_001"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_in_series",
            "from": "voltage_source_1",
            "to": "switch_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "switch_1",
            "to": "resistor_1",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_1",
            "to": "resistor_2",
            "confidence": 0.95
          },
          {
            "type": "connected_in_series",
            "from": "resistor_2",
            "to": "voltage_source_1",
            "confidence": 0.95
          }
        ],
        "calibration": null,
        "_other_fields_in_complete_snapshot": [
          "version",
          "page_ir_version",
          "figure_id",
          "provenance",
          "evidence",
          "confidence",
          "status_notes",
          "review_issues",
          "parameter_provenance",
          "id"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** The actual resolved BookIR received by the compiler.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01280_PhysicsCompiler.compile",
      "return_value": {
        "status": "NEEDS_REVIEW",
        "scene": null,
        "issues": [
          {
            "code": "BOOK_IR_NOT_READY",
            "message": "BookIR status is 'NEEDS_REVIEW'; cannot compile without sufficient evidence. Notes: Circuit source, component values, or wire continuity require review."
          }
        ],
        "book_ir_status": "NEEDS_REVIEW"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A typed failure with scene=null when not ready, or a canonical PhysicsScene with source identity, units and provenance. Never manufacture an executable scene from a blocked case.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

**Changes, provenance and possible information loss:** The active compiler implementation is ai/ingestion/PhysicsCompiler.py. The scene_compiler module re-exports it.

[Complete stage input/output bundle](stage_data/23_gate.json)

- [PhysicsCompiler.compile — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01280_PhysicsCompiler.compile/STAGE.html)

- [Code: ai\ingestion\PhysicsCompiler.py](contracts/ai/ingestion/PhysicsCompiler.py)

## 24. Canonical scene construction and schema validation

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** PhysicsCompiler entry and gate → this component → API response delivered to the browser.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Validated BookIR and an initially empty canonical scene structure.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Domain scene objects, parameters and geometry that preserve evidence/provenance and source frame. If model geometry is reconstructed, distinguish it from observed geometry.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/24_compile.json)

## 25. API response delivered to the browser

**Execution:** EXECUTED. **Verdict:** SAFE NULL SCENE.

**Upstream → downstream:** Canonical scene construction and schema validation → this component → Frontend receives result and selects next state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00001_ingest_diagram",
    "value": {
      "file": {
        "type": "starlette.datastructures.UploadFile",
        "not_serialized": true
      }
    }
  }
]
```

**What it should receive — expected input:** Completed ingestion, evidence, resolution and compilation results.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00001_ingest_diagram",
      "return_value": {
        "domain": "circuits",
        "status": "needs-review",
        "scene": null,
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "R1_resistance": {
              "value": 10.0,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "V1_voltage": {
              "value": 12.0,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10.0,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12.0,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126.0,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 1149.0,
                "y": 416.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119.0,
                  "y": 391.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 1115.0,
                  "y": 416.0
                },
                "terminal_2": {
                  "x": 1183.0,
                  "y": 416.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 757.0,
                "y": 255.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727.0,
                  "y": 230.0,
                  "width": 60.0,
                  "height": 50.0
                },
                "terminal_1": {
                  "x": 723.0,
                  "y": 255.0
                },
                "terminal_2": {
                  "x": 791.0,
                  "y": 255.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "positionSourcePx": {
                "x": 231.0,
                "y": 457.0,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206.0,
                  "y": 427.0,
                  "width": 50.0,
                  "height": 60.0
                },
                "terminal_1": {
                  "x": 231.0,
                  "y": 423.0
                },
                "terminal_2": {
                  "x": 231.0,
                  "y": 491.0
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "positionSourcePx": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "sourceAssetId",
            "pageIRVersion",
            "figureId",
            "provenance",
            "evidence",
            "confidence",
            "statusNotes",
            "reviewIssues",
            "parameterProvenance",
            "id"
          ]
        },
        "source_asset": {
          "id": "9b910bff7ee74e90a1763e5358b474ff",
          "mimeType": "image/jpeg",
          "originalFilename": "photo_2026-10-10_12-06-37 (2).jpg",
          "byteSize": 38634,
          "width_px": 1280,
          "height_px": 960,
          "sha256": "e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63"
        },
        "assumptions": [],
        "_other_fields_in_complete_snapshot": [
          "success",
          "pipeline",
          "image_url",
          "debug_overlay_url",
          "page_ir",
          "compiler",
          "evidence",
          "grounding",
          "auto_failures",
          "failure_category",
          "debugId",
          "debugTrace",
          "scenario",
          "issues",
          "width",
          "height"
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A response whose status, scene, BookIR and readiness agree, correlated to this source and trace. HTTP 200 does not itself mean a simulation is ready.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

**Changes, provenance and possible information loss:** This is the handler return, after nested work. Exact HTTP status/body are retained separately from the Python object.

[Complete stage input/output bundle](stage_data/25_response.json)

- [ingest_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- [HTTP response 1792207672293216400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207672293216400_response_body.json)

- [HTTP response 1792207704511725600_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207704511725600_response_body.json)

- [HTTP response 1792207705365140500_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207705365140500_response_body.json)

- [Code: apps\api\main.py](contracts/apps/api/main.py)

## 26. Frontend receives result and selects next state

**Execution:** EXECUTED. **Verdict:** FRONTEND FLOW ISSUE.

**Upstream → downstream:** API response delivered to the browser → this component → Review / explicit compile request branch.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 4060.5,
    "data": [
      "UPLOADING"
    ]
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 36286.90000000596,
    "data": [
      "ANALYZING"
    ]
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 37146.5,
    "data": [
      "NEEDS_REVIEW"
    ]
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 37151.30000001192,
    "data": [
      "COMPILING"
    ]
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 38341.80000001192,
    "data": [
      "ERROR",
      "The simulation is not ready yet: BookIR is not ready to compile."
    ]
  }
]
```

**What it should receive — expected input:** The actual API response for this upload, not the startup demo scene.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 4060.800000011921,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 36287,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 37146.59999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 37151.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 38341.90000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "final_orchestrator_state": "ERROR",
      "currentError": "The simulation is not ready yet: BookIR is not ready to compile."
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Preserved source URL/frame and readiness-governed state. Needs-review cases should expose review issues without falsely activating an uploaded simulation.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

**Changes, provenance and possible information loss:** Only events after startWithFile for this trace are used here. Startup/demo events remain in the raw log but are excluded from this diagram’s runtime evidence.

[Complete stage input/output bundle](stage_data/26_orchestrator.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 27. Review / explicit compile request branch

**Execution:** EXECUTED. **Verdict:** FRONTEND FLOW ISSUE.

**Upstream → downstream:** Frontend receives result and selects next state → this component → InteractiveFigure receives the compiled scene.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "01281_review_book_ir",
    "value": {
      "req": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20,
              "unit": "ohm",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "R1_resistance": {
              "value": 10,
              "unit": "ohm",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "V1_voltage": {
              "value": 12,
              "unit": "V",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 1149,
                "y": 416,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 757,
                "y": 255,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "positionSourcePx": {
                "x": 231,
                "y": 457,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "positionSourcePx": null,
              "geometry": null,
              "_nested_fields_in_complete_snapshot": [
                "attributes",
                "evidenceRefs"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "sourceAssetId",
            "pageIRVersion",
            "figureId",
            "provenance",
            "evidence",
            "confidence",
            "statusNotes",
            "reviewIssues",
            "parameterProvenance",
            "id"
          ]
        }
      }
    }
  },
  {
    "call": "01326_compile_resolved",
    "value": {
      "req": {
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20,
              "unit": "ohm",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "R1_resistance": {
              "value": 10,
              "unit": "ohm",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "V1_voltage": {
              "value": 12,
              "unit": "V",
              "status": "observed",
              "_nested_fields_in_complete_snapshot": [
                "provenance"
              ]
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 1149,
                "y": 416,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 757,
                "y": 255,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "positionSourcePx": {
                "x": 231,
                "y": 457,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "_nested_fields_in_complete_snapshot": [
                "geometry",
                "attributes",
                "evidenceRefs"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "positionSourcePx": null,
              "geometry": null,
              "_nested_fields_in_complete_snapshot": [
                "attributes",
                "evidenceRefs"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "sourceAssetId",
            "pageIRVersion",
            "figureId",
            "provenance",
            "evidence",
            "confidence",
            "statusNotes",
            "reviewIssues",
            "parameterProvenance",
            "id"
          ]
        }
      }
    }
  },
  {
    "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.compile",
    "phase": "input",
    "wallTime": 37151.09999999404,
    "data": []
  }
]
```

**What it should receive — expected input:** A needs-review BookIR and subsequent actual browser review/compile requests, if any.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "01281_review_book_ir",
      "return_value": {
        "success": true,
        "review_state": {
          "subtype": "dc_linear",
          "blockers": [
            "Circuit component R2 has no valid two-node connection.",
            "Circuit component R1 has no valid two-node connection.",
            "Circuit component V1 has no valid two-node connection."
          ],
          "warnings": [
            "A switch is present and will be initialized in the interactive simulation."
          ],
          "_other_fields_in_complete_snapshot": [
            "bookIRStatus",
            "bookIrId",
            "readyToCompile",
            "satisfiedRequirements",
            "missingRequirements",
            "ambiguousRequirements",
            "blockersCount",
            "warningsCount",
            "issues",
            "availablePolicies",
            "diagnostics"
          ]
        },
        "ready_to_compile": false,
        "blockers_count": 3,
        "warnings_count": 1,
        "book_ir": {
          "isPhysics": true,
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "circuit_topology": {
              "verified_connectivity": false,
              "node_count": 0
            }
          },
          "parameters": {
            "R2_resistance": {
              "value": 20,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "R1_resistance": {
              "value": 10,
              "unit": "ohm",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "V1_voltage": {
              "value": 12,
              "unit": "V",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.95,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "components": [
              {
                "id": "R2",
                "type": "resistor",
                "value": 20,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "R1",
                "type": "resistor",
                "value": 10,
                "unit": "ohm",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              },
              {
                "id": "V1",
                "type": "voltage_source",
                "value": 12,
                "unit": "V",
                "_nested_fields_in_complete_snapshot": [
                  "nodes",
                  "label_bbox_source_px",
                  "terminals",
                  "geometry"
                ]
              }
            ],
            "nodes": [],
            "wires": {
              "count": 15,
              "first_8_records": [
                {
                  "id": "wire_1",
                  "node": null,
                  "length_px": 115,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_2",
                  "node": null,
                  "length_px": 763,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_3",
                  "node": null,
                  "length_px": 161,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_4",
                  "node": null,
                  "length_px": 118,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_5",
                  "node": null,
                  "length_px": 162,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_6",
                  "node": null,
                  "length_px": 133,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_7",
                  "node": null,
                  "length_px": 166,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                },
                {
                  "id": "wire_8",
                  "node": null,
                  "length_px": 126,
                  "_nested_fields_in_complete_snapshot": [
                    "polyline_source_px",
                    "points"
                  ]
                }
              ],
              "complete_list": "See complete stage bundle / original artifact"
            },
            "reference_node": "N0"
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "R2",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 1149,
                "y": 416,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 1119,
                  "y": 391,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 1115,
                  "y": 416
                },
                "terminal_2": {
                  "x": 1183,
                  "y": 416
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_005"
              ]
            },
            {
              "id": "R1",
              "type": "resistor",
              "label": null,
              "positionSourcePx": {
                "x": 757,
                "y": 255,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 727,
                  "y": 230,
                  "width": 60,
                  "height": 50
                },
                "terminal_1": {
                  "x": 723,
                  "y": 255
                },
                "terminal_2": {
                  "x": 791,
                  "y": 255
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "V1",
              "type": "voltage_source",
              "label": null,
              "positionSourcePx": {
                "x": 231,
                "y": 457,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component"
              },
              "geometry": {
                "bounds": {
                  "x": 206,
                  "y": 427,
                  "width": 50,
                  "height": 60
                },
                "terminal_1": {
                  "x": 231,
                  "y": 423
                },
                "terminal_2": {
                  "x": 231,
                  "y": 491
                },
                "wire_connected": true,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {},
              "evidenceRefs": [
                "ev_cv_circuits_9b910bff7ee74e90a1763e5358b474ff",
                "ev_ocr_ocr_tok_004"
              ]
            },
            {
              "id": "switch_1",
              "type": "switch",
              "label": "S",
              "positionSourcePx": null,
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "figure_001"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_in_series",
              "from": "voltage_source_1",
              "to": "switch_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "switch_1",
              "to": "resistor_1",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_1",
              "to": "resistor_2",
              "confidence": 0.95
            },
            {
              "type": "connected_in_series",
              "from": "resistor_2",
              "to": "voltage_source_1",
              "confidence": 0.95
            }
          ],
          "calibration": null,
          "_other_fields_in_complete_snapshot": [
            "version",
            "sourceAssetId",
            "pageIRVersion",
            "figureId",
            "provenance",
            "evidence",
            "confidence",
            "statusNotes",
            "reviewIssues",
            "parameterProvenance",
            "id"
          ]
        }
      }
    },
    {
      "call": "01326_compile_resolved",
      "return_value": null
    },
    {
      "traceId": "TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.compile",
      "phase": "output",
      "wallTime": 38341.90000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": [
    {
      "call": "01326_compile_resolved",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "9b910bff7ee74e90a1763e5358b474ff",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "circuits",
          "subtype": "dc_linear",
          "status": "NEEDS_REVIEW",
          "status_notes": "Circuit source, component values, or wire continuity require review.",
          "calibration": null,
          "id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
          "isPhysics": true,
          "_nested_fields_in_complete_snapshot": [
            "entities",
            "relationships",
            "parameters",
            "geometry",
            "assumptions",
            "provenance",
            "evidence",
            "confidence",
            "resolutions",
            "review_issues",
            "parameter_provenance"
          ]
        },
        "readiness": {
          "ready": false,
          "book_ir_status": "NEEDS_REVIEW",
          "status": "NEEDS_REVIEW",
          "book_ir_id": "9b910bff7ee74e90a1763e5358b474ff_figure_001",
          "subtype": "dc_linear",
          "calibration_status": null,
          "_nested_fields_in_complete_snapshot": [
            "blockers",
            "warnings",
            "satisfied_requirements",
            "resolved_requirements",
            "missing_requirements",
            "policy_assumptions",
            "unresolved_ambiguities"
          ]
        }
      }
    }
  ]
}
```

**What it should provide — implemented contract:** Review should list blockers; compile must reject unresolved evidence and keep scene=null. No synthetic user corrections are supplied in this trace.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

**Changes, provenance and possible information loss:** This branch executes for the circuit. Its rejection is an expected backend gate; the unnecessary frontend compile attempt is a separate issue.

[Complete stage input/output bundle](stage_data/27_review.json)

- [review_book_ir — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01281_review_book_ir/STAGE.html)

- [compile_resolved — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01326_compile_resolved/STAGE.html)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/15_browser/events.json)

- [HTTP response 1792207672293216400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207672293216400_response_body.json)

- [HTTP response 1792207704511725600_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207704511725600_response_body.json)

- [HTTP response 1792207705365140500_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/http/1792207705365140500_response_body.json)

- [Code: apps\api\main.py](contracts/apps/api/main.py)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 28. InteractiveFigure receives the compiled scene

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** Review / explicit compile request branch → this component → FigureViewport background and layout.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** The source-matched canonical scene approved by the backend.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A figure bound to the original image, with the correct domain runtime and an initial rendered output. No unrelated demo geometry.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/28_figure.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

## 29. FigureViewport background and layout

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** InteractiveFigure receives the compiled scene → this component → PhysicsRuntime normalization and adapter initialization.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Original source URL, natural width/height and measured viewport bounds.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The source image displayed with an aspect-preserving transform shared by its overlay. Letterboxing belongs to the viewport, not to native geometry.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/29_background.json)

- [Code: apps\web\src\components\FigureViewport.js](contracts/apps/web/src/components/FigureViewport.js)

## 30. PhysicsRuntime normalization and adapter initialization

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** FigureViewport background and layout → this component → Domain solver and actual initial state.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Source-matched scene and figure/container options.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Validated normalized scene, resolved capabilities, matching adapter and initialized runtime. Normalization must not erase provenance or relocate source points.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/30_runtime.json)

- [Code: engine\core\PhysicsRuntime.js](contracts/engine/core/PhysicsRuntime.js)

## 31. Domain solver and actual initial state

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** PhysicsRuntime normalization and adapter initialization → this component → CoordinateMapper: source → overlay → browser.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** The actual scene-derived model parameters, source geometry and any explicit policy values.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Mathematically consistent state/output for those inputs. Correct computation is separate from whether those inputs reconstruct this diagram.

**What correct handling of THIS diagram requires:** Compilation should remain blocked while topology/switch state is ungrounded. A hypothetical corrected ideal open-switch model would have no conducting loop, but that is not a solver output from this trace. Do not present a closed-switch 0.4 A result as actual output.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/31_solver.json)

## 32. CoordinateMapper: source → overlay → browser

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** Domain solver and actual initial state → this component → Actual renderer at t=0 over the original.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Native source coordinates, source dimensions, viewport dimensions, DPR and image rectangle.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Invertible mapping with the same image/overlay scale and offsets. Applying viewToSource(sourceToView(p)) should recover the supplied point within floating-point precision.

**What correct handling of THIS diagram requires:** 12 V, 10 Ω and 20 Ω are printed evidence. The switch must retain its visible gap. No measured current, numerical node coordinates or validated MNA graph is supplied.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/32_mapper.json)

- [Code: engine\core\coordinateMapper.js](contracts/engine/core/coordinateMapper.js)

## 33. Actual renderer at t=0 over the original

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** CoordinateMapper: source → overlay → browser → this component → Activation, motion and reset.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** Initialized runtime output, original background and the measured mapper/DOM geometry.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The rendered source landmarks should coincide with the printed diagram at t=0. This requires correct upstream geometry as well as correct transforms.

**What correct handling of THIS diagram requires:** Keep real wire spans separate from component bodies, switch gap and current annotation. Ground resistor/battery/switch terminals; build resolvable node IDs and relationships without filling gaps with artificial wires.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/33_render.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

## 34. Activation, motion and reset

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** Actual renderer at t=0 over the original → this component → Final observed browser state.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** The initialized scene/state and actual Play/Pause/Reset control actions.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Motion evolves runtime state only; reset restores initial compiled values. Exact 0.5 s / 1 s states cannot be asserted unless their saved timestamps say so.

**What correct handling of THIS diagram requires:** Compilation should remain blocked while topology/switch state is ungrounded. A hypothetical corrected ideal open-switch model would have no conducting loop, but that is not a solver output from this trace. Do not present a closed-switch 0.4 A result as actual output.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/34_motion.json)

- [Code: apps\web\src\main.js](contracts/apps/web/src/main.js)

## Handoff audit: actual output → next actual input

IDENTICAL proves preservation of the supplied data, not correctness. CHANGED means differences were recorded; URL binding, dimension metadata and status changes may be legitimate. The complete JSON contains both values and every changed field.

[Complete handoff comparison](HANDOFFS.json)

| Boundary | Result | Changed paths |

|---|---|---|

| UploadService output → PageIRBuilder asset input | IDENTICAL | None |

| PageIRBuilder output → BookUnderstandingPipeline page input | IDENTICAL | None |

| Semantic BookIR → EvidenceExtractionPipeline book input | IDENTICAL | None |

| Final OCR output → Grounder OCR input | IDENTICAL | None |

| CV output → Grounder CV input | IDENTICAL | None |

| Grounded BookIR → Evidence pipeline returned BookIR | CHANGED | /provenance/evidence_pipeline_latency_ms |

| Evidence BookIR → AutoResolution input (dimension enforcement between) | IDENTICAL | None |

| AutoResolution BookIR → Compiler input (resolution evaluation between) | IDENTICAL | None |

## Runtime subcomponents and capture boundary

| Component | Expected input | Expected output | Actual evidence / gap |

|---|---|---|---|

| validatePhysicsScene | Normalized canonical scene | Validation result / typed issues | NOT EXECUTED for this uploaded circuit. |

| SimulationCapabilityRegistry.resolve | Validated normalized scene | Interactive scene/capabilities | NOT EXECUTED for this uploaded circuit. |

| SolverRegistry.resolve | Interactive scene | Matching domain adapter | NOT EXECUTED for this uploaded circuit. |

| Adapter.initialize | Interactive scene, container and options | Initialized adapter state | NOT EXECUTED for this uploaded circuit. |

| Domain solver | Adapter-derived model arguments | Physics solution/state | NOT EXECUTED for this uploaded circuit. |

| Renderer.render / PendulumSimulation.render | Runtime solution/state and mapper | SVG/canvas output | NOT EXECUTED for this uploaded circuit. |

## Appendix A. Every captured backend component and invocation

The main 34 stages group nested helpers by their role in the data flow. This ledger retains every captured function, including parsing, unit conversion, geometry helpers, registry checks and repeated evaluators. Each call page contains exact input/output/locals and that function’s source contract. Call numbers are entry order, not completed-stage order.

- **ingest_diagram** (1 calls): [1](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- **_get_ingestion_pipeline** (1 calls): [2](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00002__get_ingestion_pipeline/STAGE.html)

- **UploadService.ingest** (1 calls): [3](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

- **compute_sha256** (1 calls): [4](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00004_compute_sha256/STAGE.html)

- **UploadService.get_public_url** (1 calls): [5](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00005_UploadService.get_public_url/STAGE.html)

- **PageIRBuilder.build** (1 calls): [6](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- **BookUnderstandingPipeline.analyze** (1 calls): [7](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- **BookUnderstandingPipeline._get_analyzer** (1 calls): [8](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00008_BookUnderstandingPipeline._get_analyzer/STAGE.html)

- **PhysicsVisionAnalyzer.analyze** (1 calls): [9](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- **GeminiVisionProvider.analyze_diagram** (1 calls): [10](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- **GeminiVisionProvider._get_client** (1 calls): [11](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00011_GeminiVisionProvider._get_client/STAGE.html)

- **Models.generate_content** (1 calls): [12](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

- **Models._generate_content** (1 calls): [13](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00013_Models._generate_content/STAGE.html)

- **_discard_dangling_relationships** (1 calls): [14](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00014__discard_dangling_relationships/STAGE.html)

- **validate_semantic_payload** (1 calls): [15](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- **SemanticConfidence.from_dict** (1 calls): [16](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00016_SemanticConfidence.from_dict/STAGE.html)

- **_validate_confidence** (19 calls): [17](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00017__validate_confidence/STAGE.html), [18](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00018__validate_confidence/STAGE.html), [19](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00019__validate_confidence/STAGE.html), [20](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00020__validate_confidence/STAGE.html), [22](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00022__validate_confidence/STAGE.html), [24](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00024__validate_confidence/STAGE.html), [26](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00026__validate_confidence/STAGE.html), [28](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00028__validate_confidence/STAGE.html), [30](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00030__validate_confidence/STAGE.html), [32](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00032__validate_confidence/STAGE.html), [34](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00034__validate_confidence/STAGE.html), [36](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00036__validate_confidence/STAGE.html), [38](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00038__validate_confidence/STAGE.html), [40](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00040__validate_confidence/STAGE.html), [42](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00042__validate_confidence/STAGE.html), [44](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00044__validate_confidence/STAGE.html), [46](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00046__validate_confidence/STAGE.html), [48](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00048__validate_confidence/STAGE.html), [50](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00050__validate_confidence/STAGE.html)

- **SemanticEntity.from_dict** (5 calls): [21](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00021_SemanticEntity.from_dict/STAGE.html), [23](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00023_SemanticEntity.from_dict/STAGE.html), [25](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00025_SemanticEntity.from_dict/STAGE.html), [27](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00027_SemanticEntity.from_dict/STAGE.html), [29](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00029_SemanticEntity.from_dict/STAGE.html)

- **SemanticRelationship.from_dict** (4 calls): [31](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00031_SemanticRelationship.from_dict/STAGE.html), [33](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00033_SemanticRelationship.from_dict/STAGE.html), [35](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00035_SemanticRelationship.from_dict/STAGE.html), [37](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00037_SemanticRelationship.from_dict/STAGE.html)

- **SemanticVisibleLabel.from_dict** (6 calls): [39](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00039_SemanticVisibleLabel.from_dict/STAGE.html), [41](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00041_SemanticVisibleLabel.from_dict/STAGE.html), [43](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00043_SemanticVisibleLabel.from_dict/STAGE.html), [45](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00045_SemanticVisibleLabel.from_dict/STAGE.html), [47](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00047_SemanticVisibleLabel.from_dict/STAGE.html), [49](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00049_SemanticVisibleLabel.from_dict/STAGE.html)

- **PhysicsVisionAnalyzer._apply_thresholds** (1 calls): [51](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00051_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

- **BookUnderstandingPipeline._build_book_ir_from_result** (1 calls): [52](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00052_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- **SemanticAnalysisResult.is_supported** (1 calls): [53](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00053_SemanticAnalysisResult.is_supported/STAGE.html)

- **EvidenceExtractionPipeline.extract_and_fuse** (1 calls): [54](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- **GrounderRegistry.find_grounder** (1 calls): [55](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00055_GrounderRegistry.find_grounder/STAGE.html)

- **PendulumGrounder.supports** (1 calls): [56](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00056_PendulumGrounder.supports/STAGE.html)

- **ProjectileGrounder.supports** (1 calls): [57](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00057_ProjectileGrounder.supports/STAGE.html)

- **ThinLensGrounder.supports** (1 calls): [58](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00058_ThinLensGrounder.supports/STAGE.html)

- **SphericalMirrorGrounder.supports** (1 calls): [59](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00059_SphericalMirrorGrounder.supports/STAGE.html)

- **InterfaceRefractionGrounder.supports** (1 calls): [60](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00060_InterfaceRefractionGrounder.supports/STAGE.html)

- **PrismGrounder.supports** (1 calls): [61](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00061_PrismGrounder.supports/STAGE.html)

- **CircuitGrounder.supports** (1 calls): [62](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00062_CircuitGrounder.supports/STAGE.html)

- **load_and_validate_source_image** (1 calls): [63](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00063_load_and_validate_source_image/STAGE.html)

- **MultiOCRRouter.available** (1 calls): [64](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00064_MultiOCRRouter.available/STAGE.html)

- **RapidOCRProvider.available** (2 calls): [65](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00065_RapidOCRProvider.available/STAGE.html), [68](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00068_RapidOCRProvider.available/STAGE.html)

- **MultiOCRRouter.extract** (1 calls): [66](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00066_MultiOCRRouter.extract/STAGE.html)

- **RapidOCRProvider.extract** (1 calls): [67](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00067_RapidOCRProvider.extract/STAGE.html)

- **ImageTransform.identity** (2 calls): [69](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00069_ImageTransform.identity/STAGE.html), [118](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00118_ImageTransform.identity/STAGE.html)

- **RapidOCRProvider._get_engine** (1 calls): [70](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00070_RapidOCRProvider._get_engine/STAGE.html)

- **ImageTransform.to_source_point** (52 calls): [71](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00071_ImageTransform.to_source_point/STAGE.html), [72](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00072_ImageTransform.to_source_point/STAGE.html), [73](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00073_ImageTransform.to_source_point/STAGE.html), [74](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00074_ImageTransform.to_source_point/STAGE.html), [77](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00077_ImageTransform.to_source_point/STAGE.html), [78](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00078_ImageTransform.to_source_point/STAGE.html), [79](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00079_ImageTransform.to_source_point/STAGE.html), [80](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00080_ImageTransform.to_source_point/STAGE.html), [83](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00083_ImageTransform.to_source_point/STAGE.html), [84](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00084_ImageTransform.to_source_point/STAGE.html), [85](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00085_ImageTransform.to_source_point/STAGE.html), [86](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00086_ImageTransform.to_source_point/STAGE.html), [89](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00089_ImageTransform.to_source_point/STAGE.html), [90](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00090_ImageTransform.to_source_point/STAGE.html), [91](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00091_ImageTransform.to_source_point/STAGE.html), [92](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00092_ImageTransform.to_source_point/STAGE.html), [95](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00095_ImageTransform.to_source_point/STAGE.html), [96](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00096_ImageTransform.to_source_point/STAGE.html), [97](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00097_ImageTransform.to_source_point/STAGE.html), [98](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00098_ImageTransform.to_source_point/STAGE.html), [101](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00101_ImageTransform.to_source_point/STAGE.html), [102](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00102_ImageTransform.to_source_point/STAGE.html), [103](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00103_ImageTransform.to_source_point/STAGE.html), [104](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00104_ImageTransform.to_source_point/STAGE.html), [107](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00107_ImageTransform.to_source_point/STAGE.html), [108](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00108_ImageTransform.to_source_point/STAGE.html), [109](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00109_ImageTransform.to_source_point/STAGE.html), [110](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00110_ImageTransform.to_source_point/STAGE.html), [120](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00120_ImageTransform.to_source_point/STAGE.html), [121](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00121_ImageTransform.to_source_point/STAGE.html), [122](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00122_ImageTransform.to_source_point/STAGE.html), [123](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00123_ImageTransform.to_source_point/STAGE.html), [127](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00127_ImageTransform.to_source_point/STAGE.html), [128](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00128_ImageTransform.to_source_point/STAGE.html), [129](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00129_ImageTransform.to_source_point/STAGE.html), [130](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00130_ImageTransform.to_source_point/STAGE.html), [134](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00134_ImageTransform.to_source_point/STAGE.html), [135](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00135_ImageTransform.to_source_point/STAGE.html), [136](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00136_ImageTransform.to_source_point/STAGE.html), [137](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00137_ImageTransform.to_source_point/STAGE.html), [141](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00141_ImageTransform.to_source_point/STAGE.html), [142](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00142_ImageTransform.to_source_point/STAGE.html), [143](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00143_ImageTransform.to_source_point/STAGE.html), [144](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00144_ImageTransform.to_source_point/STAGE.html), [148](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00148_ImageTransform.to_source_point/STAGE.html), [149](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00149_ImageTransform.to_source_point/STAGE.html), [150](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00150_ImageTransform.to_source_point/STAGE.html), [151](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00151_ImageTransform.to_source_point/STAGE.html), [155](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00155_ImageTransform.to_source_point/STAGE.html), [156](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00156_ImageTransform.to_source_point/STAGE.html), [157](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00157_ImageTransform.to_source_point/STAGE.html), [158](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00158_ImageTransform.to_source_point/STAGE.html)

- **SourcePolygon.bbox** (13 calls): [75](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00075_SourcePolygon.bbox/STAGE.html), [81](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00081_SourcePolygon.bbox/STAGE.html), [87](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00087_SourcePolygon.bbox/STAGE.html), [93](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00093_SourcePolygon.bbox/STAGE.html), [99](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00099_SourcePolygon.bbox/STAGE.html), [105](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00105_SourcePolygon.bbox/STAGE.html), [111](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00111_SourcePolygon.bbox/STAGE.html), [124](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00124_SourcePolygon.bbox/STAGE.html), [131](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00131_SourcePolygon.bbox/STAGE.html), [138](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00138_SourcePolygon.bbox/STAGE.html), [145](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00145_SourcePolygon.bbox/STAGE.html), [152](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00152_SourcePolygon.bbox/STAGE.html), [159](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00159_SourcePolygon.bbox/STAGE.html)

- **RapidOCRProvider.name** (8 calls): [76](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00076_RapidOCRProvider.name/STAGE.html), [82](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00082_RapidOCRProvider.name/STAGE.html), [88](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00088_RapidOCRProvider.name/STAGE.html), [94](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00094_RapidOCRProvider.name/STAGE.html), [100](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00100_RapidOCRProvider.name/STAGE.html), [106](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00106_RapidOCRProvider.name/STAGE.html), [112](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00112_RapidOCRProvider.name/STAGE.html), [113](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00113_RapidOCRProvider.name/STAGE.html)

- **RapidOCRProvider.model_version** (1 calls): [114](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00114_RapidOCRProvider.model_version/STAGE.html)

- **EasyOCRBanglaProvider.available** (4 calls): [115](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00115_EasyOCRBanglaProvider.available/STAGE.html), [117](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00117_EasyOCRBanglaProvider.available/STAGE.html), [190](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00190_EasyOCRBanglaProvider.available/STAGE.html), [192](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00192_EasyOCRBanglaProvider.available/STAGE.html)

- **EasyOCRBanglaProvider.extract** (1 calls): [116](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00116_EasyOCRBanglaProvider.extract/STAGE.html)

- **EasyOCRBanglaProvider._get_reader** (1 calls): [119](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00119_EasyOCRBanglaProvider._get_reader/STAGE.html)

- **is_bengali_text** (10 calls): [125](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00125_is_bengali_text/STAGE.html), [132](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00132_is_bengali_text/STAGE.html), [139](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00139_is_bengali_text/STAGE.html), [146](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00146_is_bengali_text/STAGE.html), [153](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00153_is_bengali_text/STAGE.html), [160](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00160_is_bengali_text/STAGE.html), [163](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00163_is_bengali_text/STAGE.html), [164](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00164_is_bengali_text/STAGE.html), [165](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00165_is_bengali_text/STAGE.html), [166](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00166_is_bengali_text/STAGE.html)

- **EasyOCRBanglaProvider.name** (7 calls): [126](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00126_EasyOCRBanglaProvider.name/STAGE.html), [133](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00133_EasyOCRBanglaProvider.name/STAGE.html), [140](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00140_EasyOCRBanglaProvider.name/STAGE.html), [147](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00147_EasyOCRBanglaProvider.name/STAGE.html), [154](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00154_EasyOCRBanglaProvider.name/STAGE.html), [161](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00161_EasyOCRBanglaProvider.name/STAGE.html), [162](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00162_EasyOCRBanglaProvider.name/STAGE.html)

- **deduplicate_spatial_tokens** (1 calls): [167](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00167_deduplicate_spatial_tokens/STAGE.html)

- **deduplicate_spatial_tokens.<locals>.<lambda>** (7 calls): [168](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00168_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [169](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00169_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [170](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00170_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [171](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00171_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [172](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00172_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [173](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00173_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [174](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00174_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html)

- **GreekSymbolVisualOCR.extract_symbols** (1 calls): [175](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00175_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- **PhysicsSymbolCandidateResolver.enrich_token** (7 calls): [176](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00176_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [178](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00178_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [180](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00180_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [182](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00182_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [184](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00184_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [186](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00186_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [188](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00188_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- **generate_symbol_alternatives** (7 calls): [177](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00177_generate_symbol_alternatives/STAGE.html), [179](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00179_generate_symbol_alternatives/STAGE.html), [181](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00181_generate_symbol_alternatives/STAGE.html), [183](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00183_generate_symbol_alternatives/STAGE.html), [185](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00185_generate_symbol_alternatives/STAGE.html), [187](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00187_generate_symbol_alternatives/STAGE.html), [189](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00189_generate_symbol_alternatives/STAGE.html)

- **MultiOCRRouter.name** (1 calls): [191](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00191_MultiOCRRouter.name/STAGE.html)

- **GreekSymbolVisualOCR.available** (1 calls): [193](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00193_GreekSymbolVisualOCR.available/STAGE.html)

- **UnavailableFormulaRecognitionProvider.available** (1 calls): [194](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00194_UnavailableFormulaRecognitionProvider.available/STAGE.html)

- **CircuitCVCandidateExtractor.extract** (1 calls): [195](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00195_CircuitCVCandidateExtractor.extract/STAGE.html)

- **preprocess_for_geometry** (1 calls): [196](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00196_preprocess_for_geometry/STAGE.html)

- **preprocess_diagram** (1 calls): [197](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00197_preprocess_diagram/STAGE.html)

- **mask_out_text_regions** (1 calls): [198](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00198_mask_out_text_regions/STAGE.html)

- **math_floor** (14 calls): [199](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00199_math_floor/STAGE.html), [200](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00200_math_floor/STAGE.html), [203](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00203_math_floor/STAGE.html), [204](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00204_math_floor/STAGE.html), [207](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00207_math_floor/STAGE.html), [208](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00208_math_floor/STAGE.html), [211](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00211_math_floor/STAGE.html), [212](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00212_math_floor/STAGE.html), [215](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00215_math_floor/STAGE.html), [216](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00216_math_floor/STAGE.html), [219](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00219_math_floor/STAGE.html), [220](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00220_math_floor/STAGE.html), [223](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00223_math_floor/STAGE.html), [224](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00224_math_floor/STAGE.html)

- **math_ceil** (14 calls): [201](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00201_math_ceil/STAGE.html), [202](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00202_math_ceil/STAGE.html), [205](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00205_math_ceil/STAGE.html), [206](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00206_math_ceil/STAGE.html), [209](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00209_math_ceil/STAGE.html), [210](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00210_math_ceil/STAGE.html), [213](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00213_math_ceil/STAGE.html), [214](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00214_math_ceil/STAGE.html), [217](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00217_math_ceil/STAGE.html), [218](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00218_math_ceil/STAGE.html), [221](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00221_math_ceil/STAGE.html), [222](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00222_math_ceil/STAGE.html), [225](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00225_math_ceil/STAGE.html), [226](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00226_math_ceil/STAGE.html)

- **merge_collinear_lines** (1 calls): [227](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00227_merge_collinear_lines/STAGE.html)

- **point_to_segment_distance** (56 calls): [228](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00228_point_to_segment_distance/STAGE.html), [229](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00229_point_to_segment_distance/STAGE.html), [230](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00230_point_to_segment_distance/STAGE.html), [231](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00231_point_to_segment_distance/STAGE.html), [232](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00232_point_to_segment_distance/STAGE.html), [233](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00233_point_to_segment_distance/STAGE.html), [234](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00234_point_to_segment_distance/STAGE.html), [235](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00235_point_to_segment_distance/STAGE.html), [236](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00236_point_to_segment_distance/STAGE.html), [237](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00237_point_to_segment_distance/STAGE.html), [238](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00238_point_to_segment_distance/STAGE.html), [239](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00239_point_to_segment_distance/STAGE.html), [240](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00240_point_to_segment_distance/STAGE.html), [241](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00241_point_to_segment_distance/STAGE.html), [242](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00242_point_to_segment_distance/STAGE.html), [243](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00243_point_to_segment_distance/STAGE.html), [244](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00244_point_to_segment_distance/STAGE.html), [245](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00245_point_to_segment_distance/STAGE.html), [246](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00246_point_to_segment_distance/STAGE.html), [247](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00247_point_to_segment_distance/STAGE.html), [248](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00248_point_to_segment_distance/STAGE.html), [249](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00249_point_to_segment_distance/STAGE.html), [250](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00250_point_to_segment_distance/STAGE.html), [251](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00251_point_to_segment_distance/STAGE.html), [252](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00252_point_to_segment_distance/STAGE.html), [253](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00253_point_to_segment_distance/STAGE.html), [254](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00254_point_to_segment_distance/STAGE.html), [255](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00255_point_to_segment_distance/STAGE.html), [256](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00256_point_to_segment_distance/STAGE.html), [257](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00257_point_to_segment_distance/STAGE.html), [258](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00258_point_to_segment_distance/STAGE.html), [259](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00259_point_to_segment_distance/STAGE.html), [260](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00260_point_to_segment_distance/STAGE.html), [261](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00261_point_to_segment_distance/STAGE.html), [262](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00262_point_to_segment_distance/STAGE.html), [263](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00263_point_to_segment_distance/STAGE.html), [264](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00264_point_to_segment_distance/STAGE.html), [265](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00265_point_to_segment_distance/STAGE.html), [266](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00266_point_to_segment_distance/STAGE.html), [267](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00267_point_to_segment_distance/STAGE.html), [268](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00268_point_to_segment_distance/STAGE.html), [269](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00269_point_to_segment_distance/STAGE.html), [270](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00270_point_to_segment_distance/STAGE.html), [271](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00271_point_to_segment_distance/STAGE.html), [272](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00272_point_to_segment_distance/STAGE.html), [273](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00273_point_to_segment_distance/STAGE.html), [274](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00274_point_to_segment_distance/STAGE.html), [275](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00275_point_to_segment_distance/STAGE.html), [276](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00276_point_to_segment_distance/STAGE.html), [277](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00277_point_to_segment_distance/STAGE.html), [278](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00278_point_to_segment_distance/STAGE.html), [279](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00279_point_to_segment_distance/STAGE.html), [280](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00280_point_to_segment_distance/STAGE.html), [281](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00281_point_to_segment_distance/STAGE.html), [282](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00282_point_to_segment_distance/STAGE.html), [283](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00283_point_to_segment_distance/STAGE.html)

- **CircuitCVCandidateExtractor.extract.<locals>._cluster_1d** (3 calls): [284](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00284_CircuitCVCandidateExtractor.extract._locals_._cluster_1d/STAGE.html), [285](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00285_CircuitCVCandidateExtractor.extract._locals_._cluster_1d/STAGE.html), [286](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00286_CircuitCVCandidateExtractor.extract._locals_._cluster_1d/STAGE.html)

- **SourcePoint.distance_to** (896 calls): [287](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00287_SourcePoint.distance_to/STAGE.html), [288](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00288_SourcePoint.distance_to/STAGE.html), [289](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00289_SourcePoint.distance_to/STAGE.html), [290](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00290_SourcePoint.distance_to/STAGE.html), [291](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00291_SourcePoint.distance_to/STAGE.html), [292](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00292_SourcePoint.distance_to/STAGE.html), [293](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00293_SourcePoint.distance_to/STAGE.html), [294](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00294_SourcePoint.distance_to/STAGE.html), [295](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00295_SourcePoint.distance_to/STAGE.html), [296](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00296_SourcePoint.distance_to/STAGE.html), [297](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00297_SourcePoint.distance_to/STAGE.html), [298](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00298_SourcePoint.distance_to/STAGE.html), [299](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00299_SourcePoint.distance_to/STAGE.html), [300](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00300_SourcePoint.distance_to/STAGE.html), [301](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00301_SourcePoint.distance_to/STAGE.html), [302](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00302_SourcePoint.distance_to/STAGE.html), [303](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00303_SourcePoint.distance_to/STAGE.html), [304](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00304_SourcePoint.distance_to/STAGE.html), [305](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00305_SourcePoint.distance_to/STAGE.html), [306](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00306_SourcePoint.distance_to/STAGE.html), [307](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00307_SourcePoint.distance_to/STAGE.html), [308](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00308_SourcePoint.distance_to/STAGE.html), [309](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00309_SourcePoint.distance_to/STAGE.html), [310](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00310_SourcePoint.distance_to/STAGE.html), [311](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00311_SourcePoint.distance_to/STAGE.html), [312](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00312_SourcePoint.distance_to/STAGE.html), [313](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00313_SourcePoint.distance_to/STAGE.html), [314](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00314_SourcePoint.distance_to/STAGE.html), [315](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00315_SourcePoint.distance_to/STAGE.html), [316](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00316_SourcePoint.distance_to/STAGE.html), [317](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00317_SourcePoint.distance_to/STAGE.html), [318](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00318_SourcePoint.distance_to/STAGE.html), [319](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00319_SourcePoint.distance_to/STAGE.html), [320](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00320_SourcePoint.distance_to/STAGE.html), [321](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00321_SourcePoint.distance_to/STAGE.html), [322](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00322_SourcePoint.distance_to/STAGE.html), [323](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00323_SourcePoint.distance_to/STAGE.html), [324](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00324_SourcePoint.distance_to/STAGE.html), [325](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00325_SourcePoint.distance_to/STAGE.html), [326](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00326_SourcePoint.distance_to/STAGE.html), [327](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00327_SourcePoint.distance_to/STAGE.html), [328](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00328_SourcePoint.distance_to/STAGE.html), [329](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00329_SourcePoint.distance_to/STAGE.html), [330](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00330_SourcePoint.distance_to/STAGE.html), [331](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00331_SourcePoint.distance_to/STAGE.html), [332](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00332_SourcePoint.distance_to/STAGE.html), [333](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00333_SourcePoint.distance_to/STAGE.html), [334](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00334_SourcePoint.distance_to/STAGE.html), [335](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00335_SourcePoint.distance_to/STAGE.html), [336](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00336_SourcePoint.distance_to/STAGE.html), [337](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00337_SourcePoint.distance_to/STAGE.html), [338](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00338_SourcePoint.distance_to/STAGE.html), [339](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00339_SourcePoint.distance_to/STAGE.html), [340](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00340_SourcePoint.distance_to/STAGE.html), [341](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00341_SourcePoint.distance_to/STAGE.html), [342](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00342_SourcePoint.distance_to/STAGE.html), [343](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00343_SourcePoint.distance_to/STAGE.html), [344](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00344_SourcePoint.distance_to/STAGE.html), [345](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00345_SourcePoint.distance_to/STAGE.html), [346](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00346_SourcePoint.distance_to/STAGE.html), [347](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00347_SourcePoint.distance_to/STAGE.html), [348](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00348_SourcePoint.distance_to/STAGE.html), [349](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00349_SourcePoint.distance_to/STAGE.html), [350](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00350_SourcePoint.distance_to/STAGE.html), [351](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00351_SourcePoint.distance_to/STAGE.html), [352](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00352_SourcePoint.distance_to/STAGE.html), [353](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00353_SourcePoint.distance_to/STAGE.html), [354](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00354_SourcePoint.distance_to/STAGE.html), [355](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00355_SourcePoint.distance_to/STAGE.html), [356](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00356_SourcePoint.distance_to/STAGE.html), [357](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00357_SourcePoint.distance_to/STAGE.html), [358](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00358_SourcePoint.distance_to/STAGE.html), [359](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00359_SourcePoint.distance_to/STAGE.html), [360](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00360_SourcePoint.distance_to/STAGE.html), [361](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00361_SourcePoint.distance_to/STAGE.html), [362](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00362_SourcePoint.distance_to/STAGE.html), [363](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00363_SourcePoint.distance_to/STAGE.html), [364](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00364_SourcePoint.distance_to/STAGE.html), [365](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00365_SourcePoint.distance_to/STAGE.html), [366](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00366_SourcePoint.distance_to/STAGE.html), [367](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00367_SourcePoint.distance_to/STAGE.html), [368](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00368_SourcePoint.distance_to/STAGE.html), [369](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00369_SourcePoint.distance_to/STAGE.html), [370](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00370_SourcePoint.distance_to/STAGE.html), [371](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00371_SourcePoint.distance_to/STAGE.html), [372](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00372_SourcePoint.distance_to/STAGE.html), [373](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00373_SourcePoint.distance_to/STAGE.html), [374](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00374_SourcePoint.distance_to/STAGE.html), [375](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00375_SourcePoint.distance_to/STAGE.html), [376](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00376_SourcePoint.distance_to/STAGE.html), [377](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00377_SourcePoint.distance_to/STAGE.html), [378](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00378_SourcePoint.distance_to/STAGE.html), [379](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00379_SourcePoint.distance_to/STAGE.html), [380](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00380_SourcePoint.distance_to/STAGE.html), [381](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00381_SourcePoint.distance_to/STAGE.html), [382](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00382_SourcePoint.distance_to/STAGE.html), [383](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00383_SourcePoint.distance_to/STAGE.html), [384](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00384_SourcePoint.distance_to/STAGE.html), [385](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00385_SourcePoint.distance_to/STAGE.html), [386](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00386_SourcePoint.distance_to/STAGE.html), [387](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00387_SourcePoint.distance_to/STAGE.html), [388](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00388_SourcePoint.distance_to/STAGE.html), [389](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00389_SourcePoint.distance_to/STAGE.html), [390](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00390_SourcePoint.distance_to/STAGE.html), [391](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00391_SourcePoint.distance_to/STAGE.html), [392](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00392_SourcePoint.distance_to/STAGE.html), [393](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00393_SourcePoint.distance_to/STAGE.html), [394](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00394_SourcePoint.distance_to/STAGE.html), [395](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00395_SourcePoint.distance_to/STAGE.html), [396](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00396_SourcePoint.distance_to/STAGE.html), [397](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00397_SourcePoint.distance_to/STAGE.html), [398](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00398_SourcePoint.distance_to/STAGE.html), [399](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00399_SourcePoint.distance_to/STAGE.html), [400](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00400_SourcePoint.distance_to/STAGE.html), [401](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00401_SourcePoint.distance_to/STAGE.html), [402](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00402_SourcePoint.distance_to/STAGE.html), [403](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00403_SourcePoint.distance_to/STAGE.html), [404](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00404_SourcePoint.distance_to/STAGE.html), [405](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00405_SourcePoint.distance_to/STAGE.html), [406](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00406_SourcePoint.distance_to/STAGE.html), [407](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00407_SourcePoint.distance_to/STAGE.html), [408](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00408_SourcePoint.distance_to/STAGE.html), [409](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00409_SourcePoint.distance_to/STAGE.html), [410](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00410_SourcePoint.distance_to/STAGE.html), [411](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00411_SourcePoint.distance_to/STAGE.html), [412](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00412_SourcePoint.distance_to/STAGE.html), [413](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00413_SourcePoint.distance_to/STAGE.html), [414](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00414_SourcePoint.distance_to/STAGE.html), [415](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00415_SourcePoint.distance_to/STAGE.html), [416](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00416_SourcePoint.distance_to/STAGE.html), [417](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00417_SourcePoint.distance_to/STAGE.html), [418](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00418_SourcePoint.distance_to/STAGE.html), [419](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00419_SourcePoint.distance_to/STAGE.html), [420](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00420_SourcePoint.distance_to/STAGE.html), [421](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00421_SourcePoint.distance_to/STAGE.html), [422](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00422_SourcePoint.distance_to/STAGE.html), [423](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00423_SourcePoint.distance_to/STAGE.html), [424](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00424_SourcePoint.distance_to/STAGE.html), [425](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00425_SourcePoint.distance_to/STAGE.html), [426](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00426_SourcePoint.distance_to/STAGE.html), [427](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00427_SourcePoint.distance_to/STAGE.html), [428](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00428_SourcePoint.distance_to/STAGE.html), [429](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00429_SourcePoint.distance_to/STAGE.html), [430](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00430_SourcePoint.distance_to/STAGE.html), [431](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00431_SourcePoint.distance_to/STAGE.html), [432](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00432_SourcePoint.distance_to/STAGE.html), [433](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00433_SourcePoint.distance_to/STAGE.html), [434](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00434_SourcePoint.distance_to/STAGE.html), [435](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00435_SourcePoint.distance_to/STAGE.html), [436](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00436_SourcePoint.distance_to/STAGE.html), [437](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00437_SourcePoint.distance_to/STAGE.html), [438](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00438_SourcePoint.distance_to/STAGE.html), [439](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00439_SourcePoint.distance_to/STAGE.html), [440](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00440_SourcePoint.distance_to/STAGE.html), [441](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00441_SourcePoint.distance_to/STAGE.html), [442](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00442_SourcePoint.distance_to/STAGE.html), [443](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00443_SourcePoint.distance_to/STAGE.html), [444](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00444_SourcePoint.distance_to/STAGE.html), [445](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00445_SourcePoint.distance_to/STAGE.html), [446](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00446_SourcePoint.distance_to/STAGE.html), [447](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00447_SourcePoint.distance_to/STAGE.html), [448](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00448_SourcePoint.distance_to/STAGE.html), [449](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00449_SourcePoint.distance_to/STAGE.html), [450](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00450_SourcePoint.distance_to/STAGE.html), [451](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00451_SourcePoint.distance_to/STAGE.html), [452](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00452_SourcePoint.distance_to/STAGE.html), [453](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00453_SourcePoint.distance_to/STAGE.html), [454](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00454_SourcePoint.distance_to/STAGE.html), [455](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00455_SourcePoint.distance_to/STAGE.html), [456](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00456_SourcePoint.distance_to/STAGE.html), [457](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00457_SourcePoint.distance_to/STAGE.html), [458](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00458_SourcePoint.distance_to/STAGE.html), [459](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00459_SourcePoint.distance_to/STAGE.html), [460](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00460_SourcePoint.distance_to/STAGE.html), [461](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00461_SourcePoint.distance_to/STAGE.html), [462](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00462_SourcePoint.distance_to/STAGE.html), [463](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00463_SourcePoint.distance_to/STAGE.html), [464](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00464_SourcePoint.distance_to/STAGE.html), [465](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00465_SourcePoint.distance_to/STAGE.html), [466](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00466_SourcePoint.distance_to/STAGE.html), [467](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00467_SourcePoint.distance_to/STAGE.html), [468](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00468_SourcePoint.distance_to/STAGE.html), [469](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00469_SourcePoint.distance_to/STAGE.html), [470](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00470_SourcePoint.distance_to/STAGE.html), [471](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00471_SourcePoint.distance_to/STAGE.html), [472](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00472_SourcePoint.distance_to/STAGE.html), [473](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00473_SourcePoint.distance_to/STAGE.html), [474](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00474_SourcePoint.distance_to/STAGE.html), [475](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00475_SourcePoint.distance_to/STAGE.html), [476](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00476_SourcePoint.distance_to/STAGE.html), [477](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00477_SourcePoint.distance_to/STAGE.html), [478](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00478_SourcePoint.distance_to/STAGE.html), [479](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00479_SourcePoint.distance_to/STAGE.html), [480](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00480_SourcePoint.distance_to/STAGE.html), [481](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00481_SourcePoint.distance_to/STAGE.html), [482](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00482_SourcePoint.distance_to/STAGE.html), [483](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00483_SourcePoint.distance_to/STAGE.html), [484](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00484_SourcePoint.distance_to/STAGE.html), [485](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00485_SourcePoint.distance_to/STAGE.html), [486](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00486_SourcePoint.distance_to/STAGE.html), [487](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00487_SourcePoint.distance_to/STAGE.html), [488](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00488_SourcePoint.distance_to/STAGE.html), [489](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00489_SourcePoint.distance_to/STAGE.html), [490](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00490_SourcePoint.distance_to/STAGE.html), [491](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00491_SourcePoint.distance_to/STAGE.html), [492](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00492_SourcePoint.distance_to/STAGE.html), [493](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00493_SourcePoint.distance_to/STAGE.html), [494](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00494_SourcePoint.distance_to/STAGE.html), [495](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00495_SourcePoint.distance_to/STAGE.html), [496](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00496_SourcePoint.distance_to/STAGE.html), [497](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00497_SourcePoint.distance_to/STAGE.html), [498](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00498_SourcePoint.distance_to/STAGE.html), [499](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00499_SourcePoint.distance_to/STAGE.html), [500](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00500_SourcePoint.distance_to/STAGE.html), [501](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00501_SourcePoint.distance_to/STAGE.html), [502](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00502_SourcePoint.distance_to/STAGE.html), [503](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00503_SourcePoint.distance_to/STAGE.html), [504](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00504_SourcePoint.distance_to/STAGE.html), [505](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00505_SourcePoint.distance_to/STAGE.html), [506](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00506_SourcePoint.distance_to/STAGE.html), [507](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00507_SourcePoint.distance_to/STAGE.html), [508](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00508_SourcePoint.distance_to/STAGE.html), [509](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00509_SourcePoint.distance_to/STAGE.html), [510](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00510_SourcePoint.distance_to/STAGE.html), [511](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00511_SourcePoint.distance_to/STAGE.html), [512](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00512_SourcePoint.distance_to/STAGE.html), [513](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00513_SourcePoint.distance_to/STAGE.html), [514](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00514_SourcePoint.distance_to/STAGE.html), [515](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00515_SourcePoint.distance_to/STAGE.html), [516](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00516_SourcePoint.distance_to/STAGE.html), [517](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00517_SourcePoint.distance_to/STAGE.html), [518](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00518_SourcePoint.distance_to/STAGE.html), [519](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00519_SourcePoint.distance_to/STAGE.html), [520](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00520_SourcePoint.distance_to/STAGE.html), [521](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00521_SourcePoint.distance_to/STAGE.html), [522](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00522_SourcePoint.distance_to/STAGE.html), [523](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00523_SourcePoint.distance_to/STAGE.html), [524](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00524_SourcePoint.distance_to/STAGE.html), [525](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00525_SourcePoint.distance_to/STAGE.html), [526](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00526_SourcePoint.distance_to/STAGE.html), [527](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00527_SourcePoint.distance_to/STAGE.html), [528](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00528_SourcePoint.distance_to/STAGE.html), [529](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00529_SourcePoint.distance_to/STAGE.html), [530](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00530_SourcePoint.distance_to/STAGE.html), [531](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00531_SourcePoint.distance_to/STAGE.html), [532](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00532_SourcePoint.distance_to/STAGE.html), [533](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00533_SourcePoint.distance_to/STAGE.html), [534](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00534_SourcePoint.distance_to/STAGE.html), [535](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00535_SourcePoint.distance_to/STAGE.html), [536](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00536_SourcePoint.distance_to/STAGE.html), [537](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00537_SourcePoint.distance_to/STAGE.html), [538](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00538_SourcePoint.distance_to/STAGE.html), [539](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00539_SourcePoint.distance_to/STAGE.html), [540](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00540_SourcePoint.distance_to/STAGE.html), [541](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00541_SourcePoint.distance_to/STAGE.html), [542](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00542_SourcePoint.distance_to/STAGE.html), [543](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00543_SourcePoint.distance_to/STAGE.html), [544](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00544_SourcePoint.distance_to/STAGE.html), [545](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00545_SourcePoint.distance_to/STAGE.html), [546](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00546_SourcePoint.distance_to/STAGE.html), [547](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00547_SourcePoint.distance_to/STAGE.html), [548](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00548_SourcePoint.distance_to/STAGE.html), [549](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00549_SourcePoint.distance_to/STAGE.html), [550](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00550_SourcePoint.distance_to/STAGE.html), [551](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00551_SourcePoint.distance_to/STAGE.html), [552](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00552_SourcePoint.distance_to/STAGE.html), [553](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00553_SourcePoint.distance_to/STAGE.html), [554](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00554_SourcePoint.distance_to/STAGE.html), [555](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00555_SourcePoint.distance_to/STAGE.html), [556](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00556_SourcePoint.distance_to/STAGE.html), [557](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00557_SourcePoint.distance_to/STAGE.html), [558](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00558_SourcePoint.distance_to/STAGE.html), [559](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00559_SourcePoint.distance_to/STAGE.html), [560](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00560_SourcePoint.distance_to/STAGE.html), [561](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00561_SourcePoint.distance_to/STAGE.html), [562](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00562_SourcePoint.distance_to/STAGE.html), [563](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00563_SourcePoint.distance_to/STAGE.html), [564](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00564_SourcePoint.distance_to/STAGE.html), [565](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00565_SourcePoint.distance_to/STAGE.html), [566](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00566_SourcePoint.distance_to/STAGE.html), [567](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00567_SourcePoint.distance_to/STAGE.html), [568](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00568_SourcePoint.distance_to/STAGE.html), [569](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00569_SourcePoint.distance_to/STAGE.html), [570](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00570_SourcePoint.distance_to/STAGE.html), [571](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00571_SourcePoint.distance_to/STAGE.html), [572](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00572_SourcePoint.distance_to/STAGE.html), [573](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00573_SourcePoint.distance_to/STAGE.html), [574](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00574_SourcePoint.distance_to/STAGE.html), [575](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00575_SourcePoint.distance_to/STAGE.html), [576](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00576_SourcePoint.distance_to/STAGE.html), [577](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00577_SourcePoint.distance_to/STAGE.html), [578](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00578_SourcePoint.distance_to/STAGE.html), [579](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00579_SourcePoint.distance_to/STAGE.html), [580](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00580_SourcePoint.distance_to/STAGE.html), [581](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00581_SourcePoint.distance_to/STAGE.html), [582](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00582_SourcePoint.distance_to/STAGE.html), [583](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00583_SourcePoint.distance_to/STAGE.html), [584](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00584_SourcePoint.distance_to/STAGE.html), [585](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00585_SourcePoint.distance_to/STAGE.html), [586](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00586_SourcePoint.distance_to/STAGE.html), [587](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00587_SourcePoint.distance_to/STAGE.html), [588](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00588_SourcePoint.distance_to/STAGE.html), [589](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00589_SourcePoint.distance_to/STAGE.html), [590](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00590_SourcePoint.distance_to/STAGE.html), [591](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00591_SourcePoint.distance_to/STAGE.html), [592](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00592_SourcePoint.distance_to/STAGE.html), [593](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00593_SourcePoint.distance_to/STAGE.html), [594](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00594_SourcePoint.distance_to/STAGE.html), [595](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00595_SourcePoint.distance_to/STAGE.html), [596](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00596_SourcePoint.distance_to/STAGE.html), [597](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00597_SourcePoint.distance_to/STAGE.html), [598](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00598_SourcePoint.distance_to/STAGE.html), [599](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00599_SourcePoint.distance_to/STAGE.html), [600](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00600_SourcePoint.distance_to/STAGE.html), [601](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00601_SourcePoint.distance_to/STAGE.html), [602](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00602_SourcePoint.distance_to/STAGE.html), [603](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00603_SourcePoint.distance_to/STAGE.html), [604](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00604_SourcePoint.distance_to/STAGE.html), [605](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00605_SourcePoint.distance_to/STAGE.html), [606](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00606_SourcePoint.distance_to/STAGE.html), [607](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00607_SourcePoint.distance_to/STAGE.html), [608](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00608_SourcePoint.distance_to/STAGE.html), [609](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00609_SourcePoint.distance_to/STAGE.html), [610](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00610_SourcePoint.distance_to/STAGE.html), [611](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00611_SourcePoint.distance_to/STAGE.html), [612](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00612_SourcePoint.distance_to/STAGE.html), [613](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00613_SourcePoint.distance_to/STAGE.html), [614](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00614_SourcePoint.distance_to/STAGE.html), [615](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00615_SourcePoint.distance_to/STAGE.html), [616](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00616_SourcePoint.distance_to/STAGE.html), [617](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00617_SourcePoint.distance_to/STAGE.html), [618](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00618_SourcePoint.distance_to/STAGE.html), [619](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00619_SourcePoint.distance_to/STAGE.html), [620](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00620_SourcePoint.distance_to/STAGE.html), [621](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00621_SourcePoint.distance_to/STAGE.html), [622](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00622_SourcePoint.distance_to/STAGE.html), [623](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00623_SourcePoint.distance_to/STAGE.html), [624](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00624_SourcePoint.distance_to/STAGE.html), [625](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00625_SourcePoint.distance_to/STAGE.html), [626](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00626_SourcePoint.distance_to/STAGE.html), [627](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00627_SourcePoint.distance_to/STAGE.html), [628](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00628_SourcePoint.distance_to/STAGE.html), [629](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00629_SourcePoint.distance_to/STAGE.html), [630](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00630_SourcePoint.distance_to/STAGE.html), [631](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00631_SourcePoint.distance_to/STAGE.html), [632](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00632_SourcePoint.distance_to/STAGE.html), [633](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00633_SourcePoint.distance_to/STAGE.html), [634](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00634_SourcePoint.distance_to/STAGE.html), [635](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00635_SourcePoint.distance_to/STAGE.html), [636](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00636_SourcePoint.distance_to/STAGE.html), [637](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00637_SourcePoint.distance_to/STAGE.html), [638](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00638_SourcePoint.distance_to/STAGE.html), [639](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00639_SourcePoint.distance_to/STAGE.html), [640](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00640_SourcePoint.distance_to/STAGE.html), [641](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00641_SourcePoint.distance_to/STAGE.html), [642](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00642_SourcePoint.distance_to/STAGE.html), [643](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00643_SourcePoint.distance_to/STAGE.html), [644](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00644_SourcePoint.distance_to/STAGE.html), [645](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00645_SourcePoint.distance_to/STAGE.html), [646](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00646_SourcePoint.distance_to/STAGE.html), [647](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00647_SourcePoint.distance_to/STAGE.html), [648](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00648_SourcePoint.distance_to/STAGE.html), [649](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00649_SourcePoint.distance_to/STAGE.html), [650](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00650_SourcePoint.distance_to/STAGE.html), [651](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00651_SourcePoint.distance_to/STAGE.html), [652](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00652_SourcePoint.distance_to/STAGE.html), [653](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00653_SourcePoint.distance_to/STAGE.html), [654](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00654_SourcePoint.distance_to/STAGE.html), [655](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00655_SourcePoint.distance_to/STAGE.html), [656](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00656_SourcePoint.distance_to/STAGE.html), [657](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00657_SourcePoint.distance_to/STAGE.html), [658](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00658_SourcePoint.distance_to/STAGE.html), [659](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00659_SourcePoint.distance_to/STAGE.html), [660](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00660_SourcePoint.distance_to/STAGE.html), [661](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00661_SourcePoint.distance_to/STAGE.html), [662](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00662_SourcePoint.distance_to/STAGE.html), [663](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00663_SourcePoint.distance_to/STAGE.html), [664](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00664_SourcePoint.distance_to/STAGE.html), [665](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00665_SourcePoint.distance_to/STAGE.html), [666](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00666_SourcePoint.distance_to/STAGE.html), [667](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00667_SourcePoint.distance_to/STAGE.html), [668](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00668_SourcePoint.distance_to/STAGE.html), [669](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00669_SourcePoint.distance_to/STAGE.html), [670](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00670_SourcePoint.distance_to/STAGE.html), [671](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00671_SourcePoint.distance_to/STAGE.html), [672](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00672_SourcePoint.distance_to/STAGE.html), [673](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00673_SourcePoint.distance_to/STAGE.html), [674](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00674_SourcePoint.distance_to/STAGE.html), [675](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00675_SourcePoint.distance_to/STAGE.html), [676](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00676_SourcePoint.distance_to/STAGE.html), [677](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00677_SourcePoint.distance_to/STAGE.html), [678](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00678_SourcePoint.distance_to/STAGE.html), [679](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00679_SourcePoint.distance_to/STAGE.html), [680](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00680_SourcePoint.distance_to/STAGE.html), [681](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00681_SourcePoint.distance_to/STAGE.html), [682](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00682_SourcePoint.distance_to/STAGE.html), [683](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00683_SourcePoint.distance_to/STAGE.html), [684](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00684_SourcePoint.distance_to/STAGE.html), [685](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00685_SourcePoint.distance_to/STAGE.html), [686](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00686_SourcePoint.distance_to/STAGE.html), [687](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00687_SourcePoint.distance_to/STAGE.html), [688](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00688_SourcePoint.distance_to/STAGE.html), [689](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00689_SourcePoint.distance_to/STAGE.html), [690](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00690_SourcePoint.distance_to/STAGE.html), [691](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00691_SourcePoint.distance_to/STAGE.html), [692](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00692_SourcePoint.distance_to/STAGE.html), [693](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00693_SourcePoint.distance_to/STAGE.html), [694](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00694_SourcePoint.distance_to/STAGE.html), [695](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00695_SourcePoint.distance_to/STAGE.html), [696](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00696_SourcePoint.distance_to/STAGE.html), [697](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00697_SourcePoint.distance_to/STAGE.html), [698](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00698_SourcePoint.distance_to/STAGE.html), [699](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00699_SourcePoint.distance_to/STAGE.html), [700](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00700_SourcePoint.distance_to/STAGE.html), [701](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00701_SourcePoint.distance_to/STAGE.html), [702](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00702_SourcePoint.distance_to/STAGE.html), [703](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00703_SourcePoint.distance_to/STAGE.html), [704](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00704_SourcePoint.distance_to/STAGE.html), [705](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00705_SourcePoint.distance_to/STAGE.html), [706](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00706_SourcePoint.distance_to/STAGE.html), [707](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00707_SourcePoint.distance_to/STAGE.html), [708](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00708_SourcePoint.distance_to/STAGE.html), [709](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00709_SourcePoint.distance_to/STAGE.html), [710](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00710_SourcePoint.distance_to/STAGE.html), [711](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00711_SourcePoint.distance_to/STAGE.html), [712](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00712_SourcePoint.distance_to/STAGE.html), [713](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00713_SourcePoint.distance_to/STAGE.html), [714](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00714_SourcePoint.distance_to/STAGE.html), [715](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00715_SourcePoint.distance_to/STAGE.html), [716](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00716_SourcePoint.distance_to/STAGE.html), [717](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00717_SourcePoint.distance_to/STAGE.html), [718](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00718_SourcePoint.distance_to/STAGE.html), [719](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00719_SourcePoint.distance_to/STAGE.html), [720](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00720_SourcePoint.distance_to/STAGE.html), [721](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00721_SourcePoint.distance_to/STAGE.html), [722](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00722_SourcePoint.distance_to/STAGE.html), [723](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00723_SourcePoint.distance_to/STAGE.html), [724](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00724_SourcePoint.distance_to/STAGE.html), [725](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00725_SourcePoint.distance_to/STAGE.html), [726](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00726_SourcePoint.distance_to/STAGE.html), [727](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00727_SourcePoint.distance_to/STAGE.html), [728](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00728_SourcePoint.distance_to/STAGE.html), [729](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00729_SourcePoint.distance_to/STAGE.html), [730](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00730_SourcePoint.distance_to/STAGE.html), [731](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00731_SourcePoint.distance_to/STAGE.html), [732](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00732_SourcePoint.distance_to/STAGE.html), [733](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00733_SourcePoint.distance_to/STAGE.html), [734](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00734_SourcePoint.distance_to/STAGE.html), [735](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00735_SourcePoint.distance_to/STAGE.html), [736](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00736_SourcePoint.distance_to/STAGE.html), [737](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00737_SourcePoint.distance_to/STAGE.html), [738](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00738_SourcePoint.distance_to/STAGE.html), [739](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00739_SourcePoint.distance_to/STAGE.html), [740](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00740_SourcePoint.distance_to/STAGE.html), [741](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00741_SourcePoint.distance_to/STAGE.html), [742](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00742_SourcePoint.distance_to/STAGE.html), [743](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00743_SourcePoint.distance_to/STAGE.html), [744](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00744_SourcePoint.distance_to/STAGE.html), [745](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00745_SourcePoint.distance_to/STAGE.html), [746](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00746_SourcePoint.distance_to/STAGE.html), [747](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00747_SourcePoint.distance_to/STAGE.html), [748](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00748_SourcePoint.distance_to/STAGE.html), [749](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00749_SourcePoint.distance_to/STAGE.html), [750](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00750_SourcePoint.distance_to/STAGE.html), [751](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00751_SourcePoint.distance_to/STAGE.html), [752](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00752_SourcePoint.distance_to/STAGE.html), [753](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00753_SourcePoint.distance_to/STAGE.html), [754](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00754_SourcePoint.distance_to/STAGE.html), [755](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00755_SourcePoint.distance_to/STAGE.html), [756](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00756_SourcePoint.distance_to/STAGE.html), [757](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00757_SourcePoint.distance_to/STAGE.html), [758](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00758_SourcePoint.distance_to/STAGE.html), [759](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00759_SourcePoint.distance_to/STAGE.html), [760](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00760_SourcePoint.distance_to/STAGE.html), [761](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00761_SourcePoint.distance_to/STAGE.html), [762](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00762_SourcePoint.distance_to/STAGE.html), [763](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00763_SourcePoint.distance_to/STAGE.html), [764](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00764_SourcePoint.distance_to/STAGE.html), [765](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00765_SourcePoint.distance_to/STAGE.html), [766](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00766_SourcePoint.distance_to/STAGE.html), [767](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00767_SourcePoint.distance_to/STAGE.html), [768](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00768_SourcePoint.distance_to/STAGE.html), [769](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00769_SourcePoint.distance_to/STAGE.html), [770](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00770_SourcePoint.distance_to/STAGE.html), [771](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00771_SourcePoint.distance_to/STAGE.html), [772](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00772_SourcePoint.distance_to/STAGE.html), [773](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00773_SourcePoint.distance_to/STAGE.html), [774](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00774_SourcePoint.distance_to/STAGE.html), [775](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00775_SourcePoint.distance_to/STAGE.html), [776](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00776_SourcePoint.distance_to/STAGE.html), [777](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00777_SourcePoint.distance_to/STAGE.html), [778](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00778_SourcePoint.distance_to/STAGE.html), [779](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00779_SourcePoint.distance_to/STAGE.html), [780](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00780_SourcePoint.distance_to/STAGE.html), [781](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00781_SourcePoint.distance_to/STAGE.html), [782](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00782_SourcePoint.distance_to/STAGE.html), [783](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00783_SourcePoint.distance_to/STAGE.html), [784](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00784_SourcePoint.distance_to/STAGE.html), [785](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00785_SourcePoint.distance_to/STAGE.html), [786](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00786_SourcePoint.distance_to/STAGE.html), [787](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00787_SourcePoint.distance_to/STAGE.html), [788](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00788_SourcePoint.distance_to/STAGE.html), [789](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00789_SourcePoint.distance_to/STAGE.html), [790](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00790_SourcePoint.distance_to/STAGE.html), [791](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00791_SourcePoint.distance_to/STAGE.html), [792](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00792_SourcePoint.distance_to/STAGE.html), [793](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00793_SourcePoint.distance_to/STAGE.html), [794](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00794_SourcePoint.distance_to/STAGE.html), [795](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00795_SourcePoint.distance_to/STAGE.html), [796](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00796_SourcePoint.distance_to/STAGE.html), [797](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00797_SourcePoint.distance_to/STAGE.html), [798](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00798_SourcePoint.distance_to/STAGE.html), [799](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00799_SourcePoint.distance_to/STAGE.html), [800](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00800_SourcePoint.distance_to/STAGE.html), [801](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00801_SourcePoint.distance_to/STAGE.html), [802](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00802_SourcePoint.distance_to/STAGE.html), [803](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00803_SourcePoint.distance_to/STAGE.html), [804](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00804_SourcePoint.distance_to/STAGE.html), [805](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00805_SourcePoint.distance_to/STAGE.html), [806](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00806_SourcePoint.distance_to/STAGE.html), [807](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00807_SourcePoint.distance_to/STAGE.html), [808](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00808_SourcePoint.distance_to/STAGE.html), [809](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00809_SourcePoint.distance_to/STAGE.html), [810](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00810_SourcePoint.distance_to/STAGE.html), [811](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00811_SourcePoint.distance_to/STAGE.html), [812](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00812_SourcePoint.distance_to/STAGE.html), [813](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00813_SourcePoint.distance_to/STAGE.html), [814](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00814_SourcePoint.distance_to/STAGE.html), [815](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00815_SourcePoint.distance_to/STAGE.html), [816](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00816_SourcePoint.distance_to/STAGE.html), [817](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00817_SourcePoint.distance_to/STAGE.html), [818](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00818_SourcePoint.distance_to/STAGE.html), [819](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00819_SourcePoint.distance_to/STAGE.html), [820](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00820_SourcePoint.distance_to/STAGE.html), [821](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00821_SourcePoint.distance_to/STAGE.html), [822](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00822_SourcePoint.distance_to/STAGE.html), [823](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00823_SourcePoint.distance_to/STAGE.html), [824](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00824_SourcePoint.distance_to/STAGE.html), [825](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00825_SourcePoint.distance_to/STAGE.html), [826](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00826_SourcePoint.distance_to/STAGE.html), [827](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00827_SourcePoint.distance_to/STAGE.html), [828](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00828_SourcePoint.distance_to/STAGE.html), [829](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00829_SourcePoint.distance_to/STAGE.html), [830](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00830_SourcePoint.distance_to/STAGE.html), [831](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00831_SourcePoint.distance_to/STAGE.html), [832](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00832_SourcePoint.distance_to/STAGE.html), [833](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00833_SourcePoint.distance_to/STAGE.html), [834](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00834_SourcePoint.distance_to/STAGE.html), [835](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00835_SourcePoint.distance_to/STAGE.html), [836](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00836_SourcePoint.distance_to/STAGE.html), [837](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00837_SourcePoint.distance_to/STAGE.html), [838](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00838_SourcePoint.distance_to/STAGE.html), [839](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00839_SourcePoint.distance_to/STAGE.html), [840](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00840_SourcePoint.distance_to/STAGE.html), [841](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00841_SourcePoint.distance_to/STAGE.html), [842](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00842_SourcePoint.distance_to/STAGE.html), [843](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00843_SourcePoint.distance_to/STAGE.html), [844](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00844_SourcePoint.distance_to/STAGE.html), [845](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00845_SourcePoint.distance_to/STAGE.html), [846](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00846_SourcePoint.distance_to/STAGE.html), [847](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00847_SourcePoint.distance_to/STAGE.html), [848](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00848_SourcePoint.distance_to/STAGE.html), [849](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00849_SourcePoint.distance_to/STAGE.html), [850](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00850_SourcePoint.distance_to/STAGE.html), [851](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00851_SourcePoint.distance_to/STAGE.html), [852](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00852_SourcePoint.distance_to/STAGE.html), [853](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00853_SourcePoint.distance_to/STAGE.html), [854](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00854_SourcePoint.distance_to/STAGE.html), [855](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00855_SourcePoint.distance_to/STAGE.html), [856](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00856_SourcePoint.distance_to/STAGE.html), [857](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00857_SourcePoint.distance_to/STAGE.html), [858](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00858_SourcePoint.distance_to/STAGE.html), [859](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00859_SourcePoint.distance_to/STAGE.html), [860](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00860_SourcePoint.distance_to/STAGE.html), [861](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00861_SourcePoint.distance_to/STAGE.html), [862](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00862_SourcePoint.distance_to/STAGE.html), [863](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00863_SourcePoint.distance_to/STAGE.html), [864](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00864_SourcePoint.distance_to/STAGE.html), [865](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00865_SourcePoint.distance_to/STAGE.html), [866](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00866_SourcePoint.distance_to/STAGE.html), [867](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00867_SourcePoint.distance_to/STAGE.html), [868](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00868_SourcePoint.distance_to/STAGE.html), [869](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00869_SourcePoint.distance_to/STAGE.html), [870](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00870_SourcePoint.distance_to/STAGE.html), [871](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00871_SourcePoint.distance_to/STAGE.html), [872](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00872_SourcePoint.distance_to/STAGE.html), [873](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00873_SourcePoint.distance_to/STAGE.html), [874](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00874_SourcePoint.distance_to/STAGE.html), [875](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00875_SourcePoint.distance_to/STAGE.html), [876](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00876_SourcePoint.distance_to/STAGE.html), [877](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00877_SourcePoint.distance_to/STAGE.html), [878](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00878_SourcePoint.distance_to/STAGE.html), [879](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00879_SourcePoint.distance_to/STAGE.html), [880](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00880_SourcePoint.distance_to/STAGE.html), [881](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00881_SourcePoint.distance_to/STAGE.html), [882](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00882_SourcePoint.distance_to/STAGE.html), [883](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00883_SourcePoint.distance_to/STAGE.html), [884](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00884_SourcePoint.distance_to/STAGE.html), [885](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00885_SourcePoint.distance_to/STAGE.html), [886](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00886_SourcePoint.distance_to/STAGE.html), [887](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00887_SourcePoint.distance_to/STAGE.html), [888](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00888_SourcePoint.distance_to/STAGE.html), [889](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00889_SourcePoint.distance_to/STAGE.html), [890](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00890_SourcePoint.distance_to/STAGE.html), [891](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00891_SourcePoint.distance_to/STAGE.html), [892](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00892_SourcePoint.distance_to/STAGE.html), [893](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00893_SourcePoint.distance_to/STAGE.html), [894](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00894_SourcePoint.distance_to/STAGE.html), [895](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00895_SourcePoint.distance_to/STAGE.html), [896](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00896_SourcePoint.distance_to/STAGE.html), [897](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00897_SourcePoint.distance_to/STAGE.html), [898](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00898_SourcePoint.distance_to/STAGE.html), [899](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00899_SourcePoint.distance_to/STAGE.html), [900](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00900_SourcePoint.distance_to/STAGE.html), [901](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00901_SourcePoint.distance_to/STAGE.html), [902](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00902_SourcePoint.distance_to/STAGE.html), [903](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00903_SourcePoint.distance_to/STAGE.html), [904](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00904_SourcePoint.distance_to/STAGE.html), [905](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00905_SourcePoint.distance_to/STAGE.html), [906](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00906_SourcePoint.distance_to/STAGE.html), [907](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00907_SourcePoint.distance_to/STAGE.html), [908](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00908_SourcePoint.distance_to/STAGE.html), [909](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00909_SourcePoint.distance_to/STAGE.html), [910](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00910_SourcePoint.distance_to/STAGE.html), [911](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00911_SourcePoint.distance_to/STAGE.html), [912](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00912_SourcePoint.distance_to/STAGE.html), [913](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00913_SourcePoint.distance_to/STAGE.html), [914](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00914_SourcePoint.distance_to/STAGE.html), [915](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00915_SourcePoint.distance_to/STAGE.html), [916](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00916_SourcePoint.distance_to/STAGE.html), [917](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00917_SourcePoint.distance_to/STAGE.html), [918](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00918_SourcePoint.distance_to/STAGE.html), [919](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00919_SourcePoint.distance_to/STAGE.html), [920](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00920_SourcePoint.distance_to/STAGE.html), [921](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00921_SourcePoint.distance_to/STAGE.html), [922](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00922_SourcePoint.distance_to/STAGE.html), [923](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00923_SourcePoint.distance_to/STAGE.html), [924](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00924_SourcePoint.distance_to/STAGE.html), [925](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00925_SourcePoint.distance_to/STAGE.html), [926](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00926_SourcePoint.distance_to/STAGE.html), [927](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00927_SourcePoint.distance_to/STAGE.html), [928](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00928_SourcePoint.distance_to/STAGE.html), [929](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00929_SourcePoint.distance_to/STAGE.html), [930](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00930_SourcePoint.distance_to/STAGE.html), [931](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00931_SourcePoint.distance_to/STAGE.html), [932](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00932_SourcePoint.distance_to/STAGE.html), [933](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00933_SourcePoint.distance_to/STAGE.html), [934](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00934_SourcePoint.distance_to/STAGE.html), [935](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00935_SourcePoint.distance_to/STAGE.html), [936](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00936_SourcePoint.distance_to/STAGE.html), [937](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00937_SourcePoint.distance_to/STAGE.html), [938](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00938_SourcePoint.distance_to/STAGE.html), [939](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00939_SourcePoint.distance_to/STAGE.html), [940](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00940_SourcePoint.distance_to/STAGE.html), [941](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00941_SourcePoint.distance_to/STAGE.html), [942](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00942_SourcePoint.distance_to/STAGE.html), [943](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00943_SourcePoint.distance_to/STAGE.html), [944](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00944_SourcePoint.distance_to/STAGE.html), [945](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00945_SourcePoint.distance_to/STAGE.html), [946](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00946_SourcePoint.distance_to/STAGE.html), [947](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00947_SourcePoint.distance_to/STAGE.html), [948](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00948_SourcePoint.distance_to/STAGE.html), [949](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00949_SourcePoint.distance_to/STAGE.html), [950](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00950_SourcePoint.distance_to/STAGE.html), [951](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00951_SourcePoint.distance_to/STAGE.html), [952](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00952_SourcePoint.distance_to/STAGE.html), [953](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00953_SourcePoint.distance_to/STAGE.html), [954](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00954_SourcePoint.distance_to/STAGE.html), [955](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00955_SourcePoint.distance_to/STAGE.html), [956](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00956_SourcePoint.distance_to/STAGE.html), [957](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00957_SourcePoint.distance_to/STAGE.html), [958](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00958_SourcePoint.distance_to/STAGE.html), [959](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00959_SourcePoint.distance_to/STAGE.html), [960](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00960_SourcePoint.distance_to/STAGE.html), [961](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00961_SourcePoint.distance_to/STAGE.html), [962](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00962_SourcePoint.distance_to/STAGE.html), [963](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00963_SourcePoint.distance_to/STAGE.html), [964](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00964_SourcePoint.distance_to/STAGE.html), [965](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00965_SourcePoint.distance_to/STAGE.html), [966](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00966_SourcePoint.distance_to/STAGE.html), [967](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00967_SourcePoint.distance_to/STAGE.html), [968](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00968_SourcePoint.distance_to/STAGE.html), [969](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00969_SourcePoint.distance_to/STAGE.html), [970](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00970_SourcePoint.distance_to/STAGE.html), [971](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00971_SourcePoint.distance_to/STAGE.html), [972](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00972_SourcePoint.distance_to/STAGE.html), [973](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00973_SourcePoint.distance_to/STAGE.html), [974](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00974_SourcePoint.distance_to/STAGE.html), [975](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00975_SourcePoint.distance_to/STAGE.html), [976](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00976_SourcePoint.distance_to/STAGE.html), [977](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00977_SourcePoint.distance_to/STAGE.html), [978](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00978_SourcePoint.distance_to/STAGE.html), [979](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00979_SourcePoint.distance_to/STAGE.html), [980](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00980_SourcePoint.distance_to/STAGE.html), [981](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00981_SourcePoint.distance_to/STAGE.html), [982](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00982_SourcePoint.distance_to/STAGE.html), [983](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00983_SourcePoint.distance_to/STAGE.html), [984](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00984_SourcePoint.distance_to/STAGE.html), [985](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00985_SourcePoint.distance_to/STAGE.html), [986](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00986_SourcePoint.distance_to/STAGE.html), [987](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00987_SourcePoint.distance_to/STAGE.html), [988](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00988_SourcePoint.distance_to/STAGE.html), [989](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00989_SourcePoint.distance_to/STAGE.html), [990](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00990_SourcePoint.distance_to/STAGE.html), [991](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00991_SourcePoint.distance_to/STAGE.html), [992](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00992_SourcePoint.distance_to/STAGE.html), [993](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00993_SourcePoint.distance_to/STAGE.html), [994](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00994_SourcePoint.distance_to/STAGE.html), [995](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00995_SourcePoint.distance_to/STAGE.html), [996](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00996_SourcePoint.distance_to/STAGE.html), [997](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00997_SourcePoint.distance_to/STAGE.html), [998](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00998_SourcePoint.distance_to/STAGE.html), [999](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/00999_SourcePoint.distance_to/STAGE.html), [1000](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01000_SourcePoint.distance_to/STAGE.html), [1001](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01001_SourcePoint.distance_to/STAGE.html), [1002](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01002_SourcePoint.distance_to/STAGE.html), [1003](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01003_SourcePoint.distance_to/STAGE.html), [1004](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01004_SourcePoint.distance_to/STAGE.html), [1005](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01005_SourcePoint.distance_to/STAGE.html), [1006](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01006_SourcePoint.distance_to/STAGE.html), [1007](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01007_SourcePoint.distance_to/STAGE.html), [1008](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01008_SourcePoint.distance_to/STAGE.html), [1009](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01009_SourcePoint.distance_to/STAGE.html), [1010](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01010_SourcePoint.distance_to/STAGE.html), [1011](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01011_SourcePoint.distance_to/STAGE.html), [1012](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01012_SourcePoint.distance_to/STAGE.html), [1013](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01013_SourcePoint.distance_to/STAGE.html), [1014](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01014_SourcePoint.distance_to/STAGE.html), [1015](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01015_SourcePoint.distance_to/STAGE.html), [1016](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01016_SourcePoint.distance_to/STAGE.html), [1017](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01017_SourcePoint.distance_to/STAGE.html), [1018](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01018_SourcePoint.distance_to/STAGE.html), [1019](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01019_SourcePoint.distance_to/STAGE.html), [1020](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01020_SourcePoint.distance_to/STAGE.html), [1021](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01021_SourcePoint.distance_to/STAGE.html), [1022](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01022_SourcePoint.distance_to/STAGE.html), [1023](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01023_SourcePoint.distance_to/STAGE.html), [1024](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01024_SourcePoint.distance_to/STAGE.html), [1025](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01025_SourcePoint.distance_to/STAGE.html), [1026](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01026_SourcePoint.distance_to/STAGE.html), [1027](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01027_SourcePoint.distance_to/STAGE.html), [1028](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01028_SourcePoint.distance_to/STAGE.html), [1029](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01029_SourcePoint.distance_to/STAGE.html), [1030](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01030_SourcePoint.distance_to/STAGE.html), [1031](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01031_SourcePoint.distance_to/STAGE.html), [1032](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01032_SourcePoint.distance_to/STAGE.html), [1033](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01033_SourcePoint.distance_to/STAGE.html), [1034](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01034_SourcePoint.distance_to/STAGE.html), [1035](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01035_SourcePoint.distance_to/STAGE.html), [1036](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01036_SourcePoint.distance_to/STAGE.html), [1037](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01037_SourcePoint.distance_to/STAGE.html), [1038](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01038_SourcePoint.distance_to/STAGE.html), [1039](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01039_SourcePoint.distance_to/STAGE.html), [1040](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01040_SourcePoint.distance_to/STAGE.html), [1041](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01041_SourcePoint.distance_to/STAGE.html), [1042](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01042_SourcePoint.distance_to/STAGE.html), [1043](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01043_SourcePoint.distance_to/STAGE.html), [1044](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01044_SourcePoint.distance_to/STAGE.html), [1045](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01045_SourcePoint.distance_to/STAGE.html), [1046](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01046_SourcePoint.distance_to/STAGE.html), [1047](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01047_SourcePoint.distance_to/STAGE.html), [1048](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01048_SourcePoint.distance_to/STAGE.html), [1049](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01049_SourcePoint.distance_to/STAGE.html), [1050](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01050_SourcePoint.distance_to/STAGE.html), [1051](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01051_SourcePoint.distance_to/STAGE.html), [1052](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01052_SourcePoint.distance_to/STAGE.html), [1053](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01053_SourcePoint.distance_to/STAGE.html), [1054](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01054_SourcePoint.distance_to/STAGE.html), [1055](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01055_SourcePoint.distance_to/STAGE.html), [1056](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01056_SourcePoint.distance_to/STAGE.html), [1057](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01057_SourcePoint.distance_to/STAGE.html), [1058](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01058_SourcePoint.distance_to/STAGE.html), [1059](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01059_SourcePoint.distance_to/STAGE.html), [1060](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01060_SourcePoint.distance_to/STAGE.html), [1061](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01061_SourcePoint.distance_to/STAGE.html), [1062](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01062_SourcePoint.distance_to/STAGE.html), [1063](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01063_SourcePoint.distance_to/STAGE.html), [1064](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01064_SourcePoint.distance_to/STAGE.html), [1065](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01065_SourcePoint.distance_to/STAGE.html), [1066](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01066_SourcePoint.distance_to/STAGE.html), [1067](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01067_SourcePoint.distance_to/STAGE.html), [1068](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01068_SourcePoint.distance_to/STAGE.html), [1069](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01069_SourcePoint.distance_to/STAGE.html), [1070](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01070_SourcePoint.distance_to/STAGE.html), [1071](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01071_SourcePoint.distance_to/STAGE.html), [1072](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01072_SourcePoint.distance_to/STAGE.html), [1073](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01073_SourcePoint.distance_to/STAGE.html), [1074](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01074_SourcePoint.distance_to/STAGE.html), [1075](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01075_SourcePoint.distance_to/STAGE.html), [1076](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01076_SourcePoint.distance_to/STAGE.html), [1077](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01077_SourcePoint.distance_to/STAGE.html), [1078](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01078_SourcePoint.distance_to/STAGE.html), [1079](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01079_SourcePoint.distance_to/STAGE.html), [1080](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01080_SourcePoint.distance_to/STAGE.html), [1081](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01081_SourcePoint.distance_to/STAGE.html), [1082](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01082_SourcePoint.distance_to/STAGE.html), [1083](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01083_SourcePoint.distance_to/STAGE.html), [1084](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01084_SourcePoint.distance_to/STAGE.html), [1085](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01085_SourcePoint.distance_to/STAGE.html), [1086](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01086_SourcePoint.distance_to/STAGE.html), [1087](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01087_SourcePoint.distance_to/STAGE.html), [1088](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01088_SourcePoint.distance_to/STAGE.html), [1089](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01089_SourcePoint.distance_to/STAGE.html), [1090](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01090_SourcePoint.distance_to/STAGE.html), [1091](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01091_SourcePoint.distance_to/STAGE.html), [1092](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01092_SourcePoint.distance_to/STAGE.html), [1093](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01093_SourcePoint.distance_to/STAGE.html), [1094](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01094_SourcePoint.distance_to/STAGE.html), [1095](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01095_SourcePoint.distance_to/STAGE.html), [1096](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01096_SourcePoint.distance_to/STAGE.html), [1097](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01097_SourcePoint.distance_to/STAGE.html), [1098](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01098_SourcePoint.distance_to/STAGE.html), [1099](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01099_SourcePoint.distance_to/STAGE.html), [1100](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01100_SourcePoint.distance_to/STAGE.html), [1101](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01101_SourcePoint.distance_to/STAGE.html), [1102](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01102_SourcePoint.distance_to/STAGE.html), [1103](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01103_SourcePoint.distance_to/STAGE.html), [1104](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01104_SourcePoint.distance_to/STAGE.html), [1105](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01105_SourcePoint.distance_to/STAGE.html), [1106](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01106_SourcePoint.distance_to/STAGE.html), [1107](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01107_SourcePoint.distance_to/STAGE.html), [1108](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01108_SourcePoint.distance_to/STAGE.html), [1109](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01109_SourcePoint.distance_to/STAGE.html), [1110](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01110_SourcePoint.distance_to/STAGE.html), [1111](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01111_SourcePoint.distance_to/STAGE.html), [1112](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01112_SourcePoint.distance_to/STAGE.html), [1113](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01113_SourcePoint.distance_to/STAGE.html), [1114](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01114_SourcePoint.distance_to/STAGE.html), [1115](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01115_SourcePoint.distance_to/STAGE.html), [1116](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01116_SourcePoint.distance_to/STAGE.html), [1117](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01117_SourcePoint.distance_to/STAGE.html), [1118](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01118_SourcePoint.distance_to/STAGE.html), [1119](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01119_SourcePoint.distance_to/STAGE.html), [1120](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01120_SourcePoint.distance_to/STAGE.html), [1121](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01121_SourcePoint.distance_to/STAGE.html), [1122](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01122_SourcePoint.distance_to/STAGE.html), [1123](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01123_SourcePoint.distance_to/STAGE.html), [1124](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01124_SourcePoint.distance_to/STAGE.html), [1125](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01125_SourcePoint.distance_to/STAGE.html), [1126](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01126_SourcePoint.distance_to/STAGE.html), [1127](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01127_SourcePoint.distance_to/STAGE.html), [1128](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01128_SourcePoint.distance_to/STAGE.html), [1129](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01129_SourcePoint.distance_to/STAGE.html), [1130](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01130_SourcePoint.distance_to/STAGE.html), [1131](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01131_SourcePoint.distance_to/STAGE.html), [1132](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01132_SourcePoint.distance_to/STAGE.html), [1133](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01133_SourcePoint.distance_to/STAGE.html), [1134](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01134_SourcePoint.distance_to/STAGE.html), [1135](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01135_SourcePoint.distance_to/STAGE.html), [1136](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01136_SourcePoint.distance_to/STAGE.html), [1137](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01137_SourcePoint.distance_to/STAGE.html), [1138](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01138_SourcePoint.distance_to/STAGE.html), [1139](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01139_SourcePoint.distance_to/STAGE.html), [1140](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01140_SourcePoint.distance_to/STAGE.html), [1141](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01141_SourcePoint.distance_to/STAGE.html), [1142](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01142_SourcePoint.distance_to/STAGE.html), [1143](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01143_SourcePoint.distance_to/STAGE.html), [1144](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01144_SourcePoint.distance_to/STAGE.html), [1145](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01145_SourcePoint.distance_to/STAGE.html), [1146](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01146_SourcePoint.distance_to/STAGE.html), [1147](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01147_SourcePoint.distance_to/STAGE.html), [1148](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01148_SourcePoint.distance_to/STAGE.html), [1149](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01149_SourcePoint.distance_to/STAGE.html), [1150](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01150_SourcePoint.distance_to/STAGE.html), [1151](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01151_SourcePoint.distance_to/STAGE.html), [1152](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01152_SourcePoint.distance_to/STAGE.html), [1153](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01153_SourcePoint.distance_to/STAGE.html), [1154](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01154_SourcePoint.distance_to/STAGE.html), [1155](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01155_SourcePoint.distance_to/STAGE.html), [1156](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01156_SourcePoint.distance_to/STAGE.html), [1157](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01157_SourcePoint.distance_to/STAGE.html), [1158](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01158_SourcePoint.distance_to/STAGE.html), [1159](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01159_SourcePoint.distance_to/STAGE.html), [1160](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01160_SourcePoint.distance_to/STAGE.html), [1161](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01161_SourcePoint.distance_to/STAGE.html), [1162](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01162_SourcePoint.distance_to/STAGE.html), [1163](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01163_SourcePoint.distance_to/STAGE.html), [1164](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01164_SourcePoint.distance_to/STAGE.html), [1165](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01165_SourcePoint.distance_to/STAGE.html), [1166](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01166_SourcePoint.distance_to/STAGE.html), [1167](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01167_SourcePoint.distance_to/STAGE.html), [1168](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01168_SourcePoint.distance_to/STAGE.html), [1169](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01169_SourcePoint.distance_to/STAGE.html), [1170](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01170_SourcePoint.distance_to/STAGE.html), [1171](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01171_SourcePoint.distance_to/STAGE.html), [1172](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01172_SourcePoint.distance_to/STAGE.html), [1173](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01173_SourcePoint.distance_to/STAGE.html), [1174](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01174_SourcePoint.distance_to/STAGE.html), [1175](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01175_SourcePoint.distance_to/STAGE.html), [1176](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01176_SourcePoint.distance_to/STAGE.html), [1177](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01177_SourcePoint.distance_to/STAGE.html), [1178](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01178_SourcePoint.distance_to/STAGE.html), [1179](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01179_SourcePoint.distance_to/STAGE.html), [1180](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01180_SourcePoint.distance_to/STAGE.html), [1181](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01181_SourcePoint.distance_to/STAGE.html), [1182](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01182_SourcePoint.distance_to/STAGE.html)

- **CircuitGrounder.ground** (1 calls): [1183](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01183_CircuitGrounder.ground/STAGE.html)

- **CircuitGrounder.fuse** (1 calls): [1184](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01184_CircuitGrounder.fuse/STAGE.html)

- **parse_physical_value_candidate** (11 calls): [1185](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01185_parse_physical_value_candidate/STAGE.html), [1188](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01188_parse_physical_value_candidate/STAGE.html), [1191](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01191_parse_physical_value_candidate/STAGE.html), [1194](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01194_parse_physical_value_candidate/STAGE.html), [1197](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01197_parse_physical_value_candidate/STAGE.html), [1199](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01199_parse_physical_value_candidate/STAGE.html), [1203](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01203_parse_physical_value_candidate/STAGE.html), [1222](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01222_parse_physical_value_candidate/STAGE.html), [1225](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01225_parse_physical_value_candidate/STAGE.html), [1227](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01227_parse_physical_value_candidate/STAGE.html), [1232](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01232_parse_physical_value_candidate/STAGE.html)

- **normalize_ocr_text** (20 calls): [1186](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01186_normalize_ocr_text/STAGE.html), [1187](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01187_normalize_ocr_text/STAGE.html), [1189](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01189_normalize_ocr_text/STAGE.html), [1190](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01190_normalize_ocr_text/STAGE.html), [1192](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01192_normalize_ocr_text/STAGE.html), [1193](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01193_normalize_ocr_text/STAGE.html), [1195](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01195_normalize_ocr_text/STAGE.html), [1196](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01196_normalize_ocr_text/STAGE.html), [1198](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01198_normalize_ocr_text/STAGE.html), [1200](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01200_normalize_ocr_text/STAGE.html), [1201](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01201_normalize_ocr_text/STAGE.html), [1202](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01202_normalize_ocr_text/STAGE.html), [1204](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01204_normalize_ocr_text/STAGE.html), [1223](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01223_normalize_ocr_text/STAGE.html), [1224](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01224_normalize_ocr_text/STAGE.html), [1226](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01226_normalize_ocr_text/STAGE.html), [1228](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01228_normalize_ocr_text/STAGE.html), [1229](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01229_normalize_ocr_text/STAGE.html), [1230](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01230_normalize_ocr_text/STAGE.html), [1233](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01233_normalize_ocr_text/STAGE.html)

- **parse_and_cluster_circuit_tokens** (1 calls): [1205](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01205_parse_and_cluster_circuit_tokens/STAGE.html)

- **CircuitGrounder.fuse.<locals>.<lambda>** (15 calls): [1206](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01206_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1207](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01207_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1208](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01208_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1209](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01209_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1210](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01210_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1211](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01211_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1212](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01212_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1213](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01213_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1214](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01214_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1215](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01215_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1216](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01216_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1217](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01217_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1218](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01218_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1219](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01219_CircuitGrounder.fuse._locals_._lambda_/STAGE.html), [1220](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01220_CircuitGrounder.fuse._locals_._lambda_/STAGE.html)

- **_intermediate_rail_topology** (1 calls): [1221](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01221__intermediate_rail_topology/STAGE.html)

- **ParsedPhysicalValueCandidate.token_id** (1 calls): [1231](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01231_ParsedPhysicalValueCandidate.token_id/STAGE.html)

- **enforce_source_dimensions** (1 calls): [1234](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01234_enforce_source_dimensions/STAGE.html)

- **AutoResolutionEngine.resolve** (1 calls): [1235](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01235_AutoResolutionEngine.resolve/STAGE.html)

- **RequirementRegistry.get_spec** (18 calls): [1236](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01236_RequirementRegistry.get_spec/STAGE.html), [1240](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01240_RequirementRegistry.get_spec/STAGE.html), [1255](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01255_RequirementRegistry.get_spec/STAGE.html), [1258](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01258_RequirementRegistry.get_spec/STAGE.html), [1263](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01263_RequirementRegistry.get_spec/STAGE.html), [1278](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01278_RequirementRegistry.get_spec/STAGE.html), [1288](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01288_RequirementRegistry.get_spec/STAGE.html), [1293](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01293_RequirementRegistry.get_spec/STAGE.html), [1308](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01308_RequirementRegistry.get_spec/STAGE.html), [1311](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01311_RequirementRegistry.get_spec/STAGE.html), [1332](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01332_RequirementRegistry.get_spec/STAGE.html), [1335](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01335_RequirementRegistry.get_spec/STAGE.html), [1350](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01350_RequirementRegistry.get_spec/STAGE.html), [1353](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01353_RequirementRegistry.get_spec/STAGE.html), [1358](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01358_RequirementRegistry.get_spec/STAGE.html), [1373](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01373_RequirementRegistry.get_spec/STAGE.html), [1377](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01377_RequirementRegistry.get_spec/STAGE.html), [1392](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01392_RequirementRegistry.get_spec/STAGE.html)

- **AutoResolutionEngine._normalize_grounded_circuit** (1 calls): [1237](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01237_AutoResolutionEngine._normalize_grounded_circuit/STAGE.html)

- **ReadinessEvaluator.evaluate** (6 calls): [1238](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01238_ReadinessEvaluator.evaluate/STAGE.html), [1261](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01261_ReadinessEvaluator.evaluate/STAGE.html), [1291](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01291_ReadinessEvaluator.evaluate/STAGE.html), [1333](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01333_ReadinessEvaluator.evaluate/STAGE.html), [1356](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01356_ReadinessEvaluator.evaluate/STAGE.html), [1375](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01375_ReadinessEvaluator.evaluate/STAGE.html)

- **ResolutionAnalyzer.analyze** (7 calls): [1239](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01239_ResolutionAnalyzer.analyze/STAGE.html), [1262](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01262_ResolutionAnalyzer.analyze/STAGE.html), [1292](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01292_ResolutionAnalyzer.analyze/STAGE.html), [1310](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01310_ResolutionAnalyzer.analyze/STAGE.html), [1334](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01334_ResolutionAnalyzer.analyze/STAGE.html), [1357](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01357_ResolutionAnalyzer.analyze/STAGE.html), [1376](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01376_ResolutionAnalyzer.analyze/STAGE.html)

- **ResolutionAnalyzer._check_geometry_requirements** (7 calls): [1241](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01241_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1264](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01264_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1294](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01294_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1312](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01312_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1336](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01336_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1359](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01359_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [1378](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01378_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- **ResolutionAnalyzer._check_parameter_requirements** (7 calls): [1242](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01242_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1265](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01265_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1295](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01295_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1313](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01313_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1337](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01337_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1360](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01360_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [1379](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01379_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- **ModelRequirementSpec.required_parameters** (13 calls): [1243](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01243_ModelRequirementSpec.required_parameters/STAGE.html), [1256](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01256_ModelRequirementSpec.required_parameters/STAGE.html), [1266](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01266_ModelRequirementSpec.required_parameters/STAGE.html), [1279](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01279_ModelRequirementSpec.required_parameters/STAGE.html), [1296](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01296_ModelRequirementSpec.required_parameters/STAGE.html), [1309](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01309_ModelRequirementSpec.required_parameters/STAGE.html), [1314](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01314_ModelRequirementSpec.required_parameters/STAGE.html), [1338](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01338_ModelRequirementSpec.required_parameters/STAGE.html), [1351](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01351_ModelRequirementSpec.required_parameters/STAGE.html), [1361](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01361_ModelRequirementSpec.required_parameters/STAGE.html), [1374](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01374_ModelRequirementSpec.required_parameters/STAGE.html), [1380](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01380_ModelRequirementSpec.required_parameters/STAGE.html), [1393](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01393_ModelRequirementSpec.required_parameters/STAGE.html)

- **ResolutionAnalyzer._check_circuit_components** (7 calls): [1244](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01244_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1267](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01267_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1297](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01297_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1315](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01315_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1339](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01339_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1362](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01362_ResolutionAnalyzer._check_circuit_components/STAGE.html), [1381](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01381_ResolutionAnalyzer._check_circuit_components/STAGE.html)

- **UnitEngine.parse_quantity** (21 calls): [1245](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01245_UnitEngine.parse_quantity/STAGE.html), [1247](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01247_UnitEngine.parse_quantity/STAGE.html), [1249](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01249_UnitEngine.parse_quantity/STAGE.html), [1268](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01268_UnitEngine.parse_quantity/STAGE.html), [1270](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01270_UnitEngine.parse_quantity/STAGE.html), [1272](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01272_UnitEngine.parse_quantity/STAGE.html), [1298](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01298_UnitEngine.parse_quantity/STAGE.html), [1300](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01300_UnitEngine.parse_quantity/STAGE.html), [1302](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01302_UnitEngine.parse_quantity/STAGE.html), [1316](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01316_UnitEngine.parse_quantity/STAGE.html), [1318](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01318_UnitEngine.parse_quantity/STAGE.html), [1320](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01320_UnitEngine.parse_quantity/STAGE.html), [1340](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01340_UnitEngine.parse_quantity/STAGE.html), [1342](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01342_UnitEngine.parse_quantity/STAGE.html), [1344](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01344_UnitEngine.parse_quantity/STAGE.html), [1363](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01363_UnitEngine.parse_quantity/STAGE.html), [1365](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01365_UnitEngine.parse_quantity/STAGE.html), [1367](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01367_UnitEngine.parse_quantity/STAGE.html), [1382](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01382_UnitEngine.parse_quantity/STAGE.html), [1384](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01384_UnitEngine.parse_quantity/STAGE.html), [1386](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01386_UnitEngine.parse_quantity/STAGE.html)

- **UnitEngine.lookup_unit** (21 calls): [1246](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01246_UnitEngine.lookup_unit/STAGE.html), [1248](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01248_UnitEngine.lookup_unit/STAGE.html), [1250](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01250_UnitEngine.lookup_unit/STAGE.html), [1269](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01269_UnitEngine.lookup_unit/STAGE.html), [1271](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01271_UnitEngine.lookup_unit/STAGE.html), [1273](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01273_UnitEngine.lookup_unit/STAGE.html), [1299](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01299_UnitEngine.lookup_unit/STAGE.html), [1301](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01301_UnitEngine.lookup_unit/STAGE.html), [1303](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01303_UnitEngine.lookup_unit/STAGE.html), [1317](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01317_UnitEngine.lookup_unit/STAGE.html), [1319](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01319_UnitEngine.lookup_unit/STAGE.html), [1321](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01321_UnitEngine.lookup_unit/STAGE.html), [1341](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01341_UnitEngine.lookup_unit/STAGE.html), [1343](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01343_UnitEngine.lookup_unit/STAGE.html), [1345](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01345_UnitEngine.lookup_unit/STAGE.html), [1364](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01364_UnitEngine.lookup_unit/STAGE.html), [1366](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01366_UnitEngine.lookup_unit/STAGE.html), [1368](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01368_UnitEngine.lookup_unit/STAGE.html), [1383](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01383_UnitEngine.lookup_unit/STAGE.html), [1385](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01385_UnitEngine.lookup_unit/STAGE.html), [1387](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01387_UnitEngine.lookup_unit/STAGE.html)

- **ResolutionAnalyzer._check_optional_parameters** (7 calls): [1251](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01251_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1274](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01274_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1304](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01304_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1322](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01322_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1346](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01346_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1369](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01369_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [1388](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01388_ResolutionAnalyzer._check_optional_parameters/STAGE.html)

- **ModelRequirementSpec.optional_parameters** (7 calls): [1252](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01252_ModelRequirementSpec.optional_parameters/STAGE.html), [1275](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01275_ModelRequirementSpec.optional_parameters/STAGE.html), [1305](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01305_ModelRequirementSpec.optional_parameters/STAGE.html), [1323](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01323_ModelRequirementSpec.optional_parameters/STAGE.html), [1347](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01347_ModelRequirementSpec.optional_parameters/STAGE.html), [1370](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01370_ModelRequirementSpec.optional_parameters/STAGE.html), [1389](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01389_ModelRequirementSpec.optional_parameters/STAGE.html)

- **PolicyRegistry.get_policies_for_subtype** (7 calls): [1253](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01253_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1276](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01276_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1306](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01306_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1324](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01324_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1348](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01348_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1371](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01371_PolicyRegistry.get_policies_for_subtype/STAGE.html), [1390](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01390_PolicyRegistry.get_policies_for_subtype/STAGE.html)

- **PolicyRegistry.list_all** (7 calls): [1254](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01254_PolicyRegistry.list_all/STAGE.html), [1277](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01277_PolicyRegistry.list_all/STAGE.html), [1307](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01307_PolicyRegistry.list_all/STAGE.html), [1325](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01325_PolicyRegistry.list_all/STAGE.html), [1349](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01349_PolicyRegistry.list_all/STAGE.html), [1372](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01372_PolicyRegistry.list_all/STAGE.html), [1391](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01391_PolicyRegistry.list_all/STAGE.html)

- **ResolutionEngine.auto_resolve** (3 calls): [1257](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01257_ResolutionEngine.auto_resolve/STAGE.html), [1287](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01287_ResolutionEngine.auto_resolve/STAGE.html), [1352](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01352_ResolutionEngine.auto_resolve/STAGE.html)

- **CalibrationEngine.derive_for_subtype** (6 calls): [1259](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01259_CalibrationEngine.derive_for_subtype/STAGE.html), [1260](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01260_CalibrationEngine.derive_for_subtype/STAGE.html), [1289](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01289_CalibrationEngine.derive_for_subtype/STAGE.html), [1290](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01290_CalibrationEngine.derive_for_subtype/STAGE.html), [1354](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01354_CalibrationEngine.derive_for_subtype/STAGE.html), [1355](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01355_CalibrationEngine.derive_for_subtype/STAGE.html)

- **PhysicsCompiler.compile** (1 calls): [1280](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01280_PhysicsCompiler.compile/STAGE.html)

- **review_book_ir** (1 calls): [1281](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01281_review_book_ir/STAGE.html)

- **BookIR.from_dict** (2 calls): [1282](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01282_BookIR.from_dict/STAGE.html), [1327](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01327_BookIR.from_dict/STAGE.html)

- **BookEntity.from_dict** (8 calls): [1283](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01283_BookEntity.from_dict/STAGE.html), [1284](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01284_BookEntity.from_dict/STAGE.html), [1285](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01285_BookEntity.from_dict/STAGE.html), [1286](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01286_BookEntity.from_dict/STAGE.html), [1328](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01328_BookEntity.from_dict/STAGE.html), [1329](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01329_BookEntity.from_dict/STAGE.html), [1330](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01330_BookEntity.from_dict/STAGE.html), [1331](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01331_BookEntity.from_dict/STAGE.html)

- **compile_resolved** (1 calls): [1326](../../../../storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/calls/01326_compile_resolved/STAGE.html)

## Appendix B. First failure and propagation

Last known good: Exact source, semantic dc_linear classification and OCR 12 V / 10 Ω / 20 Ω.

First suspicious: Raw line candidates include the current annotation shaft and open-switch arm as wire candidates.

First definitive failure: CV promotes fragmented evidence into full horizontal rails across source gaps and empty interior.

Downstream chain: CircuitGrounder creates R2 at (1149,416), with horizontal terminals (1115,416)/(1183,416), near the OCR label instead of the vertical resistor. It creates R1=(757,255), V1=(231,457), but nodes and component node lists are empty. Renaming semantic entity IDs to R1/R2/V1 leaves old relationship endpoints dangling. The switch is not grounded. Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit. Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.

Separation of failure classes: preprocessing/perception is demonstrated upstream; a shared coordinate conversion error is not demonstrated; numerical solver failure is not established. The circuit never reaches a solver.

## Appendix C. Capture limits

No new run was performed. The recorder captured repository Python boundaries and GenAI model calls, not private neural-library/C internals. JS boundary events, normalized scenes, actual solver outputs and DOM captures exist; separate entry/exit snapshots for every registry/adapter/renderer child function do not. These gaps are labeled, not filled with reconstructed output. Several void JS returns appear as captureError because undefined is not JSON; resulting state is separately recorded. Two class-serialization errors exist in the historical recorder log; integrity verification found the required snapshot files present for every indexed call. No exact expected pixel dataset, mask or numerical physical state has been authored.

[Original trace integrity checks](../../../../storage/generated/debug_traces/20261017/artifact_verification.json)
