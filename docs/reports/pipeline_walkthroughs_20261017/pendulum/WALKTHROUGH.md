# Simple pendulum: complete component-by-component debugging walkthrough

Trace ID: `TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017`. These documents use the existing live native Windows request from 2026-10-17. No models, detectors or solvers were rerun while writing them. No production fixes were made.

Source reference: A fixed mounting point on a horizontal support, a string to a bob displaced to the right, a vertical reference, and symbolic θ, L and m labels.

Known and unknown evidence: The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

Expected geometry for this diagram: The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

Expected initial simulation: At t=0 pivot and bob should register to their printed locations. Motion should pivot around that fixed point. No exact period can be asserted from the symbolic source alone.

Exact expected coordinates/masks are unavailable: EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS. Expected behavior below is a contract or a qualitative source comparison, never a hand-drawn expected result.

![Unchanged original diagram](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/00_source/original.png)

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
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "source": "C:\\Users\\saher\\Downloads\\photo_2026-10-10_12-06-38 (2).jpg",
      "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
      "bytes": 35941
    },
    "metadata": {
      "file_format": "JPEG",
      "encoded_width": 1280,
      "encoded_height": 960,
      "EXIF_orientation": null,
      "orientation": "landscape",
      "decoded_width": 1280,
      "decoded_height": 960,
      "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
      "png_note": "Lossless serialization of OpenCV decoded original JPEG; no resize, crop, redrawing, or orientation edit. Byte-exact original.jpg retained.",
      "decoded_pixels_sha256": "3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371",
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
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207719361",
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
          "src": "blob:http://127.0.0.1:5173/f8ff3d99-1bd9-49c8-a52e-2d44432341f5",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 224,
          "height": 168,
          "viewBox": null,
          "rect": {
            "x": 597.3489379882812,
            "y": 260.460693359375,
            "width": 223.3021240234375,
            "height": 167.9705810546875,
            "top": 260.460693359375,
            "right": 820.6510620117188,
            "bottom": 428.4312744140625,
            "left": 597.3489379882812
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        }
      ]
    }
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startWithFile",
    "phase": "input",
    "wallTime": 3076.2000000178814,
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
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startWithFile",
      "phase": "output",
      "wallTime": 40546,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** One upload operation: first UPLOADING, then a response-governed final state. This outer async call spans the rest of the pipeline; it must not invent a scene locally.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** File → multipart request. The generic JS File snapshot is {}, so use multipart metadata and the byte-exact source, not {} as evidence of an empty file.

[Complete stage input/output bundle](stage_data/01_upload.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 02. HTTP request reaches /api/ingest

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Browser selects the original diagram → this component → Upload persistence and dimension decoding.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "trace_id": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
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
          "36148"
        ],
        [
          "x-physics-trace-id",
          "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017"
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
          "multipart/form-data; boundary=----WebKitFormBoundaryrx39iXeMm3TRiQMw"
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Browser transport → FastAPI handler. Handler parameter is opaque in the profiler; saved multipart bytes are the authoritative payload.

[Complete stage input/output bundle](stage_data/02_http_in.json)

- [Exact multipart body](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/http/1792207721065423100_request_body.bin)

- [HTTP response 1792207721065423100_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/http/1792207721065423100_response_body.json)

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
        "bytes": 35941,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd.bin"
      },
      "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
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
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** SourceAsset with storage path/public URL, content hash, native decoded dimensions and original filename.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Encoded bytes are persisted; metadata and an asset ID are added. This is not object detection.

[Complete stage input/output bundle](stage_data/03_asset.json)

- [UploadService.ingest — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

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
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
      },
      "public_url": "/uploads/diagram_25c3ba19.jpg"
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
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** SourceAsset → PageIR. The whole image is user-supplied; confidence in that extent does not imply confidence in physics landmarks.

[Complete stage input/output bundle](stage_data/04_page.json)

- [PageIRBuilder.build — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- [Code: ai\ingestion\PageIRBuilder.py](contracts/ai/ingestion/PageIRBuilder.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/actual_overlay_on_source.png)

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
        "bytes": 35941,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd.bin"
      },
      "mime_type": "image/jpeg",
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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
              "bytes": 35941,
              "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
              "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd.bin"
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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
            "date": "Sat, 17 Oct 2026 03:28:44 GMT",
            "server": "scaffolding on HTTPServer2",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "x-content-type-options": "nosniff",
            "server-timing": "gfet4t7; dur=3244",
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
                  "text": "{\n  \"classification\": \"supported\",\n  \"isPhysics\": true,\n  \"domain\": \"mechanics\",\n  \"subtype\": \"pendulum\",\n  \"confidence\": {\n    \"isPhysics\": 1.0,\n    \"domain\": 1.0,\n    \"subtype\": 1.0,\n    \"overall\": 1.0\n  },\n  \"entities\": [\n    {\n      \"temporaryId\": \"pivot_1\",\n      \"role\": \"pivot\",\n      \"label\": \"pivot\",\n      \"confidence\": 0.95\n    },\n    {\n      \"temporaryId\": \"bob_1\",\n      \"role\": \"bob\",\n      \"label\": \"m\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"string_1\",\n      \"role\": \"string\",\n      \"label\": \"L\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"ref_1\",\n      \"role\": \"vertical_reference\",\n      \"label\": \"vertical_line\",\n      \"confidence\": 0.95\n    }\n  ],\n  \"relationships\": [\n    {\n      \"type\": \"connected_to\",\n      \"from\": \"bob_1\",\n      \"to\": \"string_1\",\n      \"confidence\": 1.0\n    },\n    {\n      \"type\": \"connected_to\",\n      \"from\": \"string_1\",\n      \"to\": \"pivot_1\",\n      \"confidence\": 1.0\n    }\n  ],\n  \"visibleLabels\": [\n    {\n      \"text\": \"θ\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle\"\n    },\n    {\n      \"text\": \"L\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"length\"\n    },\n    {\n      \"text\": \"m\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"mass\"\n    },\n    {\n      \"text\": \"Fig. 1 Simple Pendulum\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"caption\"\n    }\n  ],\n  \"candidates\": [],\n  \"notes\": [\n    \"The image is a standard textbook diagram of a simple pendulum.\"\n  ]\n}",
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
        "response_id": "auvSasGCH9zvg8UPzcW52AE",
        "usage_metadata": {
          "cache_tokens_details": null,
          "cached_content_token_count": null,
          "candidates_token_count": 546,
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
          "total_token_count": 2779,
          "traffic_type": null
        },
        "model_status": null,
        "automatic_function_calling_history": [],
        "parsed": {
          "classification": "supported",
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "confidence": {
            "isPhysics": 1.0,
            "domain": 1.0,
            "subtype": 1.0,
            "overall": 1.0
          },
          "entities": [
            {
              "temporaryId": "pivot_1",
              "role": "pivot",
              "label": "pivot",
              "confidence": 0.95
            },
            {
              "temporaryId": "bob_1",
              "role": "bob",
              "label": "m",
              "confidence": 1.0
            },
            {
              "temporaryId": "string_1",
              "role": "string",
              "label": "L",
              "confidence": 1.0
            },
            {
              "temporaryId": "ref_1",
              "role": "vertical_reference",
              "label": "vertical_line",
              "confidence": 0.95
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 1.0
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
              "confidence": 1.0
            }
          ],
          "visibleLabels": [
            {
              "text": "θ",
              "confidence": 1.0,
              "semanticRole": "angle"
            },
            {
              "text": "L",
              "confidence": 1.0,
              "semanticRole": "length"
            },
            {
              "text": "m",
              "confidence": 1.0,
              "semanticRole": "mass"
            },
            {
              "text": "Fig. 1 Simple Pendulum",
              "confidence": 1.0,
              "semanticRole": "caption"
            }
          ],
          "candidates": [],
          "notes": [
            "The image is a standard textbook diagram of a simple pendulum."
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Semantic classification, domain/subtype, entity roles and relationships. Numerical physical parameters and authoritative geometry must not originate here.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=mechanics / pendulum. Expected semantic content: A fixed mounting point on a horizontal support, a string to a bob displaced to the right, a vertical reference, and symbolic θ, L and m labels. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Image → model response. SDK/provider-internal preprocessing and private tensors were not exposed; no transform is invented for them.

[Complete stage input/output bundle](stage_data/05_vlm.json)

- [GeminiVisionProvider.analyze_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- [Models.generate_content — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

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
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "confidence": {
          "isPhysics": 1.0,
          "domain": 1.0,
          "subtype": 1.0,
          "overall": 1.0
        },
        "entities": [
          {
            "temporaryId": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95
          },
          {
            "temporaryId": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 1.0
          },
          {
            "temporaryId": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 1.0
          },
          {
            "temporaryId": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 1.0
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 1.0
          }
        ],
        "visibleLabels": [
          {
            "text": "θ",
            "confidence": 1.0,
            "semanticRole": "angle"
          },
          {
            "text": "L",
            "confidence": 1.0,
            "semanticRole": "length"
          },
          {
            "text": "m",
            "confidence": 1.0,
            "semanticRole": "mass"
          },
          {
            "text": "Fig. 1 Simple Pendulum",
            "confidence": 1.0,
            "semanticRole": "caption"
          }
        ],
        "candidates": [],
        "notes": [
          "The image is a standard textbook diagram of a simple pendulum."
        ]
      }
    }
  },
  {
    "call": "00041_PhysicsVisionAnalyzer._apply_thresholds",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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
      "call": "00041_PhysicsVisionAnalyzer._apply_thresholds",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=mechanics / pendulum. Expected semantic content: A fixed mounting point on a horizontal support, a string to a bob displaced to the right, a vertical reference, and symbolic θ, L and m labels. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Raw semantic response → validated semantic representation. Compare raw_provider confidence with the capped accepted values.

[Complete stage input/output bundle](stage_data/06_semantic.json)

- [PhysicsVisionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- [validate_semantic_payload — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- [PhysicsVisionAnalyzer._apply_thresholds — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00041_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

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
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
      }
    }
  },
  {
    "call": "00042_BookUnderstandingPipeline._build_book_ir_from_result",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "entities": [
          {
            "temporary_id": "pivot_1",
            "role": "pivot",
            "label": "pivot",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "bob_1",
            "role": "bob",
            "label": "m",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "string_1",
            "role": "string",
            "label": "L",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ref_1",
            "role": "vertical_reference",
            "label": "vertical_line",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "source_id": "bob_1",
            "target_id": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "source_id": "string_1",
            "target_id": "pivot_1",
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
      "asset_id": "25c3ba19a02041ee9ec790156fc87e44",
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
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
            "id": "bob_1",
            "type": "bob",
            "label": "m",
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
            "id": "string_1",
            "type": "string",
            "label": "L",
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
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
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
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
      "call": "00042_BookUnderstandingPipeline._build_book_ir_from_result",
      "return_value": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
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
            "id": "bob_1",
            "type": "bob",
            "label": "m",
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
            "id": "string_1",
            "type": "string",
            "label": "L",
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
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
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
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=mechanics / pendulum. Expected semantic content: A fixed mounting point on a horizontal support, a string to a bob displaced to the right, a vertical reference, and symbolic θ, L and m labels. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Semantic roles are assigned durable entity IDs. This BookIR is an intermediate hypothesis, not a runnable simulation.

[Complete stage input/output bundle](stage_data/07_book.json)

- [BookUnderstandingPipeline.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- [BookUnderstandingPipeline._build_book_ir_from_result — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00042_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- [Code: ai\ingestion\BookUnderstandingPipeline.py](contracts/ai/ingestion/BookUnderstandingPipeline.py)

## 08. Evidence dispatch and source decode

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Initial semantic BookIR → this component → RapidOCR: first text/box observations.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00045_GrounderRegistry.find_grounder",
    "value": {
      "domain": "mechanics",
      "subtype": "pendulum"
    }
  },
  {
    "call": "00047_load_and_validate_source_image",
    "value": {
      "asset": {
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
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
      "call": "00045_GrounderRegistry.find_grounder",
      "return_value": {
        "type": "ai.evidence.grounding.pendulum.PendulumGrounder",
        "not_serialized": true
      }
    },
    {
      "call": "00047_load_and_validate_source_image",
      "return_value": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The matching subtype grounder and the unchanged native BGR image array; decoder dimensions must match the asset.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** The pipeline routes to the domain module. Other grounders may execute supports() checks; their ground() methods are not thereby executed.

[Complete stage input/output bundle](stage_data/08_route.json)

- [GrounderRegistry.find_grounder — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00045_GrounderRegistry.find_grounder/STAGE.html)

- [load_and_validate_source_image — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00047_load_and_validate_source_image/STAGE.html)

- [Code: ai\evidence\grounding\registry.py](contracts/ai/evidence/grounding/registry.py)

- [Code: ai\evidence\transforms.py](contracts/ai/evidence/transforms.py)

## 09. RapidOCR: first text/box observations

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** Evidence dispatch and source decode → this component → EasyOCR: independent OCR candidates.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00051_RapidOCRProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
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
      "call": "00051_RapidOCRProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_001",
            "raw_text": "L",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 738.0,
              "y": 357.0,
              "width": 55.0,
              "height": 61.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 738.0,
                  "y": 357.0
                },
                {
                  "x": 793.0,
                  "y": 357.0
                },
                {
                  "x": 793.0,
                  "y": 418.0
                },
                {
                  "x": 738.0,
                  "y": 418.0
                }
              ]
            },
            "confidence": 0.99996,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "m",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 896.0,
              "y": 632.0,
              "width": 63.0,
              "height": 50.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 896.0,
                  "y": 632.0
                },
                {
                  "x": 959.0,
                  "y": 632.0
                },
                {
                  "x": 959.0,
                  "y": 682.0
                },
                {
                  "x": 896.0,
                  "y": 682.0
                }
              ]
            },
            "confidence": 0.99987,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "Fig. 1 Simple Pendulum",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 338.0,
              "y": 827.0,
              "width": 599.0,
              "height": 78.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 338.0,
                  "y": 827.0
                },
                {
                  "x": 937.0,
                  "y": 829.0
                },
                {
                  "x": 937.0,
                  "y": 905.0
                },
                {
                  "x": 338.0,
                  "y": 903.0
                }
              ]
            },
            "confidence": 0.98953,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          }
        ],
        "provider": "rapidocr",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "recognizer_language": "latin_digits_ch",
        "latency_ms": 1312.7447000006214,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Observed strings, confidence, source-space polygons/boxes and recognizer metadata. Text recognition alone does not locate the physical component represented by a label.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Changes, provenance and possible information loss:** Image → text candidates. Inspect exact source boxes; a correct string can still have a box overlapping diagram geometry.

[Complete stage input/output bundle](stage_data/09_rapid.json)

- [RapidOCRProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00051_RapidOCRProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\rapidocr.py](contracts/ai/evidence/ocr/rapidocr.py)

## 10. EasyOCR: independent OCR candidates

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** RapidOCR: first text/box observations → this component → Symbol candidates, deduplication and final OCR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00076_EasyOCRBanglaProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
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
      "call": "00076_EasyOCRBanglaProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "bn_tok_001",
            "raw_text": "]",
            "normalized_text": "]",
            "bbox_source_px": {
              "x": 745.0,
              "y": 365.0,
              "width": 42.0,
              "height": 46.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 745.0,
                  "y": 365.0
                },
                {
                  "x": 787.0,
                  "y": 365.0
                },
                {
                  "x": 787.0,
                  "y": 411.0
                },
                {
                  "x": 745.0,
                  "y": 411.0
                }
              ]
            },
            "confidence": 0.47404840130162995,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_001"
          },
          {
            "id": "bn_tok_002",
            "raw_text": "171",
            "normalized_text": "171",
            "bbox_source_px": {
              "x": 901.0,
              "y": 637.0,
              "width": 54.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 901.0,
                  "y": 637.0
                },
                {
                  "x": 955.0,
                  "y": 637.0
                },
                {
                  "x": 955.0,
                  "y": 677.0
                },
                {
                  "x": 901.0,
                  "y": 677.0
                }
              ]
            },
            "confidence": 0.5532381496450604,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_002"
          },
          {
            "id": "bn_tok_003",
            "raw_text": "1",
            "normalized_text": "1",
            "bbox_source_px": {
              "x": 460.0,
              "y": 842.0,
              "width": 30.0,
              "height": 44.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 460.0,
                  "y": 842.0
                },
                {
                  "x": 490.0,
                  "y": 842.0
                },
                {
                  "x": 490.0,
                  "y": 886.0
                },
                {
                  "x": 460.0,
                  "y": 886.0
                }
              ]
            },
            "confidence": 0.9184493511196798,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_003"
          },
          {
            "id": "bn_tok_004",
            "raw_text": "Simple Pendulum",
            "normalized_text": "Simple Pendulum",
            "bbox_source_px": {
              "x": 515.0,
              "y": 833.0,
              "width": 419.0,
              "height": 72.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 515.0,
                  "y": 833.0
                },
                {
                  "x": 934.0,
                  "y": 833.0
                },
                {
                  "x": 934.0,
                  "y": 905.0
                },
                {
                  "x": 515.0,
                  "y": 905.0
                }
              ]
            },
            "confidence": 0.6770280394889222,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_004"
          },
          {
            "id": "bn_tok_005",
            "raw_text": "Fig",
            "normalized_text": "Fig",
            "bbox_source_px": {
              "x": 336.3652731356703,
              "y": 827.0766894303488,
              "width": 123.26945372865941,
              "height": 80.84662113930244
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 349.96667006423115,
                  "y": 827.0766894303488
                },
                {
                  "x": 459.6347268643297,
                  "y": 846.7683191456346
                },
                {
                  "x": 446.03332993576885,
                  "y": 907.9233105696512
                },
                {
                  "x": 336.3652731356703,
                  "y": 888.2316808543654
                }
              ]
            },
            "confidence": 0.9781465020509537,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_005"
          }
        ],
        "provider": "easyocr_bangla",
        "model": "bengali.pth",
        "package": "easyocr",
        "package_version": "1.7.2",
        "detector_model": "craft_mlt_25k.pth",
        "recognizer_model": "bengali.pth",
        "recognizer_language": "bn+en",
        "latency_ms": 11361.621800024295,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Independent text alternatives with confidence and source positions; uncertain alternatives should not silently overwrite stronger evidence.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Changes, provenance and possible information loss:** Alternative OCR supplies competing evidence. Its errors are distinct from whichever result the router actually selects.

[Complete stage input/output bundle](stage_data/10_easy.json)

- [EasyOCRBanglaProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00076_EasyOCRBanglaProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\bangla.py](contracts/ai/evidence/ocr/bangla.py)

## 11. Symbol candidates, deduplication and final OCR

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** EasyOCR: independent OCR candidates → this component → Grayscale, blur and edge extraction.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00050_MultiOCRRouter.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "region": null
    }
  },
  {
    "call": "00119_deduplicate_spatial_tokens",
    "value": {
      "tokens": [
        {
          "id": "ocr_tok_001",
          "raw_text": "L",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 738.0,
            "y": 357.0,
            "width": 55.0,
            "height": 61.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 738.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 418.0
              },
              {
                "x": 738.0,
                "y": 418.0
              }
            ]
          },
          "confidence": 0.99996,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "]",
              "script": "latin",
              "confidence": 0.47404840130162995,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        },
        {
          "id": "ocr_tok_002",
          "raw_text": "m",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 896.0,
            "y": 632.0,
            "width": 63.0,
            "height": 50.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 896.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 682.0
              },
              {
                "x": 896.0,
                "y": 682.0
              }
            ]
          },
          "confidence": 0.99987,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "171",
              "script": "latin",
              "confidence": 0.5532381496450604,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        },
        {
          "id": "ocr_tok_003",
          "raw_text": "Fig. 1 Simple Pendulum",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 338.0,
            "y": 827.0,
            "width": 599.0,
            "height": 78.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 338.0,
                "y": 827.0
              },
              {
                "x": 937.0,
                "y": 829.0
              },
              {
                "x": 937.0,
                "y": 905.0
              },
              {
                "x": 338.0,
                "y": 903.0
              }
            ]
          },
          "confidence": 0.98953,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9781465020509537,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        }
      ]
    }
  },
  {
    "call": "00123_GreekSymbolVisualOCR.extract_symbols",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      },
      "existing_tokens": [
        {
          "id": "ocr_tok_003",
          "raw_text": "Fig. 1 Simple Pendulum",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 338.0,
            "y": 827.0,
            "width": 599.0,
            "height": 78.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 338.0,
                "y": 827.0
              },
              {
                "x": 937.0,
                "y": 829.0
              },
              {
                "x": 937.0,
                "y": 905.0
              },
              {
                "x": 338.0,
                "y": 903.0
              }
            ]
          },
          "confidence": 0.98953,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9781465020509537,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        },
        {
          "id": "ocr_tok_001",
          "raw_text": "L",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 738.0,
            "y": 357.0,
            "width": 55.0,
            "height": 61.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 738.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 418.0
              },
              {
                "x": 738.0,
                "y": 418.0
              }
            ]
          },
          "confidence": 0.99996,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "]",
              "script": "latin",
              "confidence": 0.47404840130162995,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        },
        {
          "id": "ocr_tok_002",
          "raw_text": "m",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 896.0,
            "y": 632.0,
            "width": 63.0,
            "height": 50.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 896.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 682.0
              },
              {
                "x": 896.0,
                "y": 682.0
              }
            ]
          },
          "confidence": 0.99987,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "171",
              "script": "latin",
              "confidence": 0.5532381496450604,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      ],
      "source_width": 1280,
      "source_height": 960
    }
  },
  {
    "call": "00124_PhysicsSymbolCandidateResolver.enrich_token",
    "value": {
      "token": {
        "id": "ocr_tok_003",
        "raw_text": "Fig. 1 Simple Pendulum",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 338.0,
          "y": 827.0,
          "width": 599.0,
          "height": 78.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 338.0,
              "y": 827.0
            },
            {
              "x": 937.0,
              "y": 829.0
            },
            {
              "x": 937.0,
              "y": 905.0
            },
            {
              "x": 338.0,
              "y": 903.0
            }
          ]
        },
        "confidence": 0.98953,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "Fig",
            "script": "latin",
            "confidence": 0.9781465020509537,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_003"
      }
    }
  },
  {
    "call": "00126_PhysicsSymbolCandidateResolver.enrich_token",
    "value": {
      "token": {
        "id": "ocr_tok_001",
        "raw_text": "L",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 738.0,
          "y": 357.0,
          "width": 55.0,
          "height": 61.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 738.0,
              "y": 357.0
            },
            {
              "x": 793.0,
              "y": 357.0
            },
            {
              "x": 793.0,
              "y": 418.0
            },
            {
              "x": 738.0,
              "y": 418.0
            }
          ]
        },
        "confidence": 0.99996,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "]",
            "script": "latin",
            "confidence": 0.47404840130162995,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_001"
      }
    }
  },
  {
    "call": "00128_PhysicsSymbolCandidateResolver.enrich_token",
    "value": {
      "token": {
        "id": "ocr_tok_002",
        "raw_text": "m",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 896.0,
          "y": 632.0,
          "width": 63.0,
          "height": 50.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 896.0,
              "y": 632.0
            },
            {
              "x": 959.0,
              "y": 632.0
            },
            {
              "x": 959.0,
              "y": 682.0
            },
            {
              "x": 896.0,
              "y": 682.0
            }
          ]
        },
        "confidence": 0.99987,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "171",
            "script": "latin",
            "confidence": 0.5532381496450604,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_002"
      }
    }
  },
  {
    "call": "00130_PhysicsSymbolCandidateResolver.enrich_token",
    "value": {
      "token": {
        "id": "ocr_tok_greek_theta_597_270",
        "raw_text": "θ",
        "normalized_text": "θ",
        "bbox_source_px": {
          "x": 597.0,
          "y": 270.0,
          "width": 28.0,
          "height": 43.0
        },
        "polygon_source_px": null,
        "confidence": 0.96,
        "script_candidate": "greek",
        "language_candidate": "el",
        "provider": "greek_symbol_ocr",
        "recognizer_model": "visual_topology_matcher",
        "candidate_alternatives": [],
        "evidence_ref": ""
      }
    }
  }
]
```

**What it should receive — expected input:** Provider token candidates, spatial overlap information and symbol alternatives.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00050_MultiOCRRouter.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_003",
            "raw_text": "Fig. 1 Simple Pendulum",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 338.0,
              "y": 827.0,
              "width": 599.0,
              "height": 78.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 338.0,
                  "y": 827.0
                },
                {
                  "x": 937.0,
                  "y": 829.0
                },
                {
                  "x": 937.0,
                  "y": 905.0
                },
                {
                  "x": 338.0,
                  "y": 903.0
                }
              ]
            },
            "confidence": 0.98953,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9781465020509537,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "L",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 738.0,
              "y": 357.0,
              "width": 55.0,
              "height": 61.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 738.0,
                  "y": 357.0
                },
                {
                  "x": 793.0,
                  "y": 357.0
                },
                {
                  "x": 793.0,
                  "y": 418.0
                },
                {
                  "x": 738.0,
                  "y": 418.0
                }
              ]
            },
            "confidence": 0.99996,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "]",
                "script": "latin",
                "confidence": 0.47404840130162995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "m",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 896.0,
              "y": 632.0,
              "width": 63.0,
              "height": 50.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 896.0,
                  "y": 632.0
                },
                {
                  "x": 959.0,
                  "y": 632.0
                },
                {
                  "x": 959.0,
                  "y": 682.0
                },
                {
                  "x": 896.0,
                  "y": 682.0
                }
              ]
            },
            "confidence": 0.99987,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "171",
                "script": "latin",
                "confidence": 0.5532381496450604,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_greek_theta_597_270",
            "raw_text": "θ",
            "normalized_text": "θ",
            "bbox_source_px": {
              "x": 597.0,
              "y": 270.0,
              "width": 28.0,
              "height": 43.0
            },
            "polygon_source_px": null,
            "confidence": 0.96,
            "script_candidate": "greek",
            "language_candidate": "el",
            "provider": "greek_symbol_ocr",
            "recognizer_model": "visual_topology_matcher",
            "candidate_alternatives": [
              {
                "text": "θ",
                "script": "greek",
                "name": "theta",
                "confidence": 0.96,
                "provider": "symbol_engine"
              }
            ],
            "evidence_ref": ""
          }
        ],
        "provider": "multi_ocr_router",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr+easyocr+greek_ocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
        "recognizer_language": "en+bn+el",
        "latency_ms": 13201.892899989616,
        "error": null,
        "metadata": {
          "bangla_available": true,
          "greek_available": true,
          "formula_available": false,
          "regions_count": 3,
          "token_count": 4
        }
      }
    },
    {
      "call": "00119_deduplicate_spatial_tokens",
      "return_value": [
        {
          "id": "ocr_tok_003",
          "raw_text": "Fig. 1 Simple Pendulum",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 338.0,
            "y": 827.0,
            "width": 599.0,
            "height": 78.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 338.0,
                "y": 827.0
              },
              {
                "x": 937.0,
                "y": 829.0
              },
              {
                "x": 937.0,
                "y": 905.0
              },
              {
                "x": 338.0,
                "y": 903.0
              }
            ]
          },
          "confidence": 0.98953,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9781465020509537,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        },
        {
          "id": "ocr_tok_001",
          "raw_text": "L",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 738.0,
            "y": 357.0,
            "width": 55.0,
            "height": 61.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 738.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 357.0
              },
              {
                "x": 793.0,
                "y": 418.0
              },
              {
                "x": 738.0,
                "y": 418.0
              }
            ]
          },
          "confidence": 0.99996,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "]",
              "script": "latin",
              "confidence": 0.47404840130162995,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        },
        {
          "id": "ocr_tok_002",
          "raw_text": "m",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 896.0,
            "y": 632.0,
            "width": 63.0,
            "height": 50.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 896.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 632.0
              },
              {
                "x": 959.0,
                "y": 682.0
              },
              {
                "x": 896.0,
                "y": 682.0
              }
            ]
          },
          "confidence": 0.99987,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "171",
              "script": "latin",
              "confidence": 0.5532381496450604,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      ]
    },
    {
      "call": "00123_GreekSymbolVisualOCR.extract_symbols",
      "return_value": [
        {
          "id": "ocr_tok_greek_theta_597_270",
          "raw_text": "θ",
          "normalized_text": "θ",
          "bbox_source_px": {
            "x": 597.0,
            "y": 270.0,
            "width": 28.0,
            "height": 43.0
          },
          "polygon_source_px": null,
          "confidence": 0.96,
          "script_candidate": "greek",
          "language_candidate": "el",
          "provider": "greek_symbol_ocr",
          "recognizer_model": "visual_topology_matcher",
          "candidate_alternatives": [],
          "evidence_ref": ""
        }
      ]
    },
    {
      "call": "00124_PhysicsSymbolCandidateResolver.enrich_token",
      "return_value": {
        "id": "ocr_tok_003",
        "raw_text": "Fig. 1 Simple Pendulum",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 338.0,
          "y": 827.0,
          "width": 599.0,
          "height": 78.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 338.0,
              "y": 827.0
            },
            {
              "x": 937.0,
              "y": 829.0
            },
            {
              "x": 937.0,
              "y": 905.0
            },
            {
              "x": 338.0,
              "y": 903.0
            }
          ]
        },
        "confidence": 0.98953,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "Fig",
            "script": "latin",
            "confidence": 0.9781465020509537,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_003"
      }
    },
    {
      "call": "00126_PhysicsSymbolCandidateResolver.enrich_token",
      "return_value": {
        "id": "ocr_tok_001",
        "raw_text": "L",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 738.0,
          "y": 357.0,
          "width": 55.0,
          "height": 61.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 738.0,
              "y": 357.0
            },
            {
              "x": 793.0,
              "y": 357.0
            },
            {
              "x": 793.0,
              "y": 418.0
            },
            {
              "x": 738.0,
              "y": 418.0
            }
          ]
        },
        "confidence": 0.99996,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "]",
            "script": "latin",
            "confidence": 0.47404840130162995,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_001"
      }
    },
    {
      "call": "00128_PhysicsSymbolCandidateResolver.enrich_token",
      "return_value": {
        "id": "ocr_tok_002",
        "raw_text": "m",
        "normalized_text": null,
        "bbox_source_px": {
          "x": 896.0,
          "y": 632.0,
          "width": 63.0,
          "height": 50.0
        },
        "polygon_source_px": {
          "points": [
            {
              "x": 896.0,
              "y": 632.0
            },
            {
              "x": 959.0,
              "y": 632.0
            },
            {
              "x": 959.0,
              "y": 682.0
            },
            {
              "x": 896.0,
              "y": 682.0
            }
          ]
        },
        "confidence": 0.99987,
        "script_candidate": "latin",
        "language_candidate": "en",
        "provider": "rapidocr",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "candidate_alternatives": [
          {
            "text": "171",
            "script": "latin",
            "confidence": 0.5532381496450604,
            "provider": "easyocr_bangla"
          }
        ],
        "evidence_ref": "evidence_ocr_ocr_tok_002"
      }
    },
    {
      "call": "00130_PhysicsSymbolCandidateResolver.enrich_token",
      "return_value": {
        "id": "ocr_tok_greek_theta_597_270",
        "raw_text": "θ",
        "normalized_text": "θ",
        "bbox_source_px": {
          "x": 597.0,
          "y": 270.0,
          "width": 28.0,
          "height": 43.0
        },
        "polygon_source_px": null,
        "confidence": 0.96,
        "script_candidate": "greek",
        "language_candidate": "el",
        "provider": "greek_symbol_ocr",
        "recognizer_model": "visual_topology_matcher",
        "candidate_alternatives": [
          {
            "text": "θ",
            "script": "greek",
            "name": "theta",
            "confidence": 0.96,
            "provider": "symbol_engine"
          }
        ],
        "evidence_ref": ""
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Merged tokens with retained provenance/alternatives. Preserve literal printed values and symbolic quantities. Do not turn L or m into a numerical length or mass.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Changes, provenance and possible information loss:** OCR alternatives → selected token set. PageIR text blocks are filled from these tokens inside the evidence pipeline.

[Complete stage input/output bundle](stage_data/11_ocr.json)

- [MultiOCRRouter.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00050_MultiOCRRouter.extract/STAGE.html)

- [deduplicate_spatial_tokens — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00119_deduplicate_spatial_tokens/STAGE.html)

- [GreekSymbolVisualOCR.extract_symbols — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00123_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00124_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00126_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00128_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00130_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [Code: ai\evidence\ocr\router.py](contracts/ai/evidence/ocr/router.py)

- [Code: ai\evidence\ocr\greek_symbols.py](contracts/ai/evidence/ocr/greek_symbols.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00050_MultiOCRRouter.extract/actual_overlay_on_source.png)

## 12. Grayscale, blur and edge extraction

**Execution:** EXECUTED. **Verdict:** FRAME PASS / LOSSY PROCESSING.

**Upstream → downstream:** Symbol candidates, deduplication and final OCR → this component → OCR-region suppression before geometry detection.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00138_preprocess_diagram",
    "value": {
      "img_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      },
      "blur_ksize": [
        5,
        5
      ],
      "blur_sigma": 1.0,
      "canny_thresh1": 40.0,
      "canny_thresh2": 120.0
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
      "call": "00138_preprocess_diagram",
      "return_value": [
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\b0bb9f4dfdaec3e62977a1b7cf7e07bccf73574dd48f5d271ebf46798fd8bd5d.npy",
          "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\b0bb9f4dfdaec3e62977a1b7cf7e07bccf73574dd48f5d271ebf46798fd8bd5d.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\8f76790a0e563430bf9c8870945eed89bcae3a7add1182a441171c62ccd6de6e.npy",
          "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\8f76790a0e563430bf9c8870945eed89bcae3a7add1182a441171c62ccd6de6e.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.npy",
          "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png"
        }
      ]
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Grayscale/blur/edge arrays in the same 1280×960 source frame. Image processing may change intensities, but must not imply a spatial crop/scale that was not performed.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Arrays preserve the source frame. Blur and Canny change image information; no detector correctness is inferred from shape alone.

**Changes, provenance and possible information loss:** Color/intensity information becomes an edge representation. Exact arrays are retained. OpenCV internal per-operation frames were not separately profiled.

[Complete stage input/output bundle](stage_data/12_pre.json)

- [preprocess_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00138_preprocess_diagram/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png)

![b0bb9f4dfdaec3e62977a1b7cf7e07bccf73574dd48f5d271ebf46798fd8bd5d.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/b0bb9f4dfdaec3e62977a1b7cf7e07bccf73574dd48f5d271ebf46798fd8bd5d.png)

![8f76790a0e563430bf9c8870945eed89bcae3a7add1182a441171c62ccd6de6e.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/8f76790a0e563430bf9c8870945eed89bcae3a7add1182a441171c62ccd6de6e.png)

![c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png)

## 13. OCR-region suppression before geometry detection

**Execution:** EXECUTED. **Verdict:** NO EARLIER GEOMETRIC FAILURE DEMONSTRATED.

**Upstream → downstream:** Grayscale, blur and edge extraction → this component → Domain CV: raw candidates → selected geometry.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00139_mask_out_text_regions",
    "value": {
      "edge_map": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png"
      },
      "ocr_boxes": [
        {
          "x": 338.0,
          "y": 827.0,
          "width": 599.0,
          "height": 78.0
        },
        {
          "x": 738.0,
          "y": 357.0,
          "width": 55.0,
          "height": 61.0
        },
        {
          "x": 896.0,
          "y": 632.0,
          "width": 63.0,
          "height": 50.0
        },
        {
          "x": 597.0,
          "y": 270.0,
          "width": 28.0,
          "height": 43.0
        }
      ],
      "margin_px": 2
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
      "call": "00139_mask_out_text_regions",
      "return_value": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** An edge map suppressing text while preserving relevant diagram boundaries/rays. This is the registration requirement; the implementation zeros the entire expanded rectangle without distinguishing text from geometry.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Removed-edge overlay was inspected. No earlier failure explaining the later rail/pivot error is established by this mask capture.

**Changes, provenance and possible information loss:** Every pixel removed by the actual mask is shown in red on the original. A valid OCR box does not guarantee safe geometry suppression.

[Complete stage input/output bundle](stage_data/13_mask.json)

- [mask_out_text_regions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00139_mask_out_text_regions/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![removed_edges_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00139_mask_out_text_regions/removed_edges_on_source.png)

![c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/c7d30679d1eec7505681d33ae65f6ce3a13d410da195e74601769a64017a8923.png)

![7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/arrays/7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.png)

## 14. Domain CV: raw candidates → selected geometry

**Execution:** EXECUTED. **Verdict:** FAIL — PERCEPTION / SELECTION.

**Upstream → downstream:** OCR-region suppression before geometry detection → this component → SAM2 segmentation prompted by CV.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00137_PendulumCVCandidateExtractor.extract_candidates",
    "value": {
      "img_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "ocr_boxes": [
        {
          "x": 338.0,
          "y": 827.0,
          "width": 599.0,
          "height": 78.0
        },
        {
          "x": 738.0,
          "y": 357.0,
          "width": 55.0,
          "height": 61.0
        },
        {
          "x": 896.0,
          "y": 632.0,
          "width": 63.0,
          "height": 50.0
        },
        {
          "x": 597.0,
          "y": 270.0,
          "width": 28.0,
          "height": 43.0
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
      "call": "00137_PendulumCVCandidateExtractor.extract_candidates",
      "return_value": {
        "all_circles": {
          "count": 18,
          "first_8_records": [
            {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094
            },
            {
              "center": {
                "x": 571.1147334653926,
                "y": 164.0757964347032
              },
              "radius_px": 91.9470552672825,
              "bounds": {
                "x": 479.16767819811014,
                "y": 72.1287411674207,
                "width": 183.894110534565,
                "height": 183.894110534565
              },
              "initial_radius": 87.71499633789062
            },
            {
              "center": {
                "x": 655.0319384260869,
                "y": 134.6649499092607
              },
              "radius_px": 70.03571393799845,
              "bounds": {
                "x": 584.9962244880884,
                "y": 64.62923597126226,
                "width": 140.0714278759969,
                "height": 140.0714278759969
              },
              "initial_radius": 73.56999969482422
            },
            {
              "center": {
                "x": 596.3270581458659,
                "y": 224.44527219440852
              },
              "radius_px": 35.84310957893747,
              "bounds": {
                "x": 560.4839485669283,
                "y": 188.60216261547106,
                "width": 71.68621915787494,
                "height": 71.68621915787494
              },
              "initial_radius": 34.93000030517578
            },
            {
              "center": {
                "x": 590.0557212477751,
                "y": 282.59074774758096
              },
              "radius_px": 31.563455909281895,
              "bounds": {
                "x": 558.4922653384932,
                "y": 251.02729183829908,
                "width": 63.12691181856379,
                "height": 63.12691181856379
              },
              "initial_radius": 32.744998931884766
            },
            {
              "center": {
                "x": 638.0950823036292,
                "y": 298.775292891693
              },
              "radius_px": 36.79998802429366,
              "bounds": {
                "x": 601.2950942793356,
                "y": 261.97530486739936,
                "width": 73.59997604858732,
                "height": 73.59997604858732
              },
              "initial_radius": 39.18499755859375
            },
            {
              "center": {
                "x": 414.6893717395315,
                "y": 864.7054522078654
              },
              "radius_px": 25.818906653177198,
              "bounds": {
                "x": 388.87046508635433,
                "y": 838.8865455546882,
                "width": 51.637813306354396,
                "height": 51.637813306354396
              },
              "initial_radius": 26.190000534057617
            },
            {
              "center": {
                "x": 511.0339222222365,
                "y": 124.67930940645624
              },
              "radius_px": 56.28152089013627,
              "bounds": {
                "x": 454.75240133210025,
                "y": 68.39778851631996,
                "width": 112.56304178027254,
                "height": 112.56304178027254
              },
              "initial_radius": 53.904998779296875
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "pin_candidates": [
          {
            "center": {
              "x": 611.0,
              "y": 291.0
            },
            "radius_px": 22.47230339050293,
            "bounds": {
              "x": 588.5276966094971,
              "y": 268.52769660949707,
              "width": 44.94460678100586,
              "height": 44.94460678100586
            },
            "initial_radius": 22.47230339050293
          },
          {
            "center": {
              "x": 609.5,
              "y": 300.5
            },
            "radius_px": 10.12432861328125,
            "bounds": {
              "x": 599.3756713867188,
              "y": 290.37567138671875,
              "width": 20.2486572265625,
              "height": 20.2486572265625
            },
            "initial_radius": 10.12432861328125
          },
          {
            "center": {
              "x": 611.5,
              "y": 280.5
            },
            "radius_px": 9.617792129516602,
            "bounds": {
              "x": 601.8822078704834,
              "y": 270.8822078704834,
              "width": 19.235584259033203,
              "height": 19.235584259033203
            },
            "initial_radius": 9.617792129516602
          }
        ],
        "all_lines": {
          "count": 9,
          "first_8_records": [
            {
              "start": {
                "x": 606.0,
                "y": 166.0
              },
              "end": {
                "x": 831.0,
                "y": 617.0
              },
              "length_px": 504.00992053728464,
              "dx": 225.0,
              "dy": 451.0
            },
            {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "dx": 0.0,
              "dy": 713.0
            },
            {
              "start": {
                "x": 553.0,
                "y": 70.0
              },
              "end": {
                "x": 826.0,
                "y": 619.0
              },
              "length_px": 613.1313073070074,
              "dx": 273.0,
              "dy": 549.0
            },
            {
              "start": {
                "x": 565.0,
                "y": 112.0
              },
              "end": {
                "x": 565.0,
                "y": 775.0
              },
              "length_px": 663.0,
              "dx": 0.0,
              "dy": 663.0
            },
            {
              "start": {
                "x": 556.0,
                "y": 67.0
              },
              "end": {
                "x": 830.0,
                "y": 617.0
              },
              "length_px": 614.4721311825297,
              "dx": 274.0,
              "dy": 550.0
            },
            {
              "start": {
                "x": 563.0,
                "y": 131.0
              },
              "end": {
                "x": 563.0,
                "y": 775.0
              },
              "length_px": 644.0,
              "dx": 0.0,
              "dy": 644.0
            },
            {
              "start": {
                "x": 614.0,
                "y": 192.0
              },
              "end": {
                "x": 692.0,
                "y": 347.0
              },
              "length_px": 173.5194513592064,
              "dx": 78.0,
              "dy": 155.0
            },
            {
              "start": {
                "x": 635.0,
                "y": 859.0
              },
              "end": {
                "x": 557.0,
                "y": 871.0
              },
              "length_px": 78.91767862779544,
              "dx": -78.0,
              "dy": 12.0
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "support_lines": [
          {
            "start": {
              "x": 577.0,
              "y": 96.0
            },
            "end": {
              "x": 699.0,
              "y": 96.0
            },
            "length_px": 122.0,
            "y_avg": 96.0
          },
          {
            "start": {
              "x": 428.0,
              "y": 92.0
            },
            "end": {
              "x": 700.0,
              "y": 92.0
            },
            "length_px": 272.0,
            "y_avg": 92.0
          },
          {
            "start": {
              "x": 428.0,
              "y": 96.0
            },
            "end": {
              "x": 550.0,
              "y": 96.0
            },
            "length_px": 122.0,
            "y_avg": 96.0
          }
        ],
        "paired_candidates": [
          {
            "score": 138.51394009521402,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "visible_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.4721311825297,
              "length_to_bob_center_px": 634.6110579092531,
              "subpixel_dir": [
                0.44636405018201547,
                0.8948514595758935
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 16.761888060919276,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.0285119516699126,
            "diameter_to_string_ratio": 0.12054171332723161
          },
          {
            "score": 136.88279171681498,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 88.07255651467977
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8736064266867,
                "y": 615.8903635249438
              },
              "visible_start": {
                "x": 553.0,
                "y": 70.0
              },
              "visible_end": {
                "x": 826.0,
                "y": 619.0
              },
              "visible_length_px": 613.1313073070074,
              "length_to_bob_center_px": 626.6907312655134,
              "subpixel_dir": [
                0.44525125688807304,
                0.89540567244104
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 88.07255651467977
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 7.927443485320225,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.2838199349269033,
            "diameter_to_string_ratio": 0.1208053195161496
          },
          {
            "score": 133.0607012108778,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 75.69595223419401
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8424517397193,
                "y": 615.9058738304373
              },
              "visible_start": {
                "x": 606.0,
                "y": 166.0
              },
              "visible_end": {
                "x": 831.0,
                "y": 617.0
              },
              "visible_length_px": 504.00992053728464,
              "length_to_bob_center_px": 637.7934475642318,
              "subpixel_dir": [
                0.44609248511533034,
                0.8949868684643527
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 75.69595223419401
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 20.30404776580599,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.34947914676966,
            "diameter_to_string_ratio": 0.14696044753567142
          }
        ],
        "best_proposal": {
          "score": 138.51394009521402,
          "bob": {
            "center": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "radius_px": 37.03476174228877,
            "bounds": {
              "x": 804.3286188987023,
              "y": 612.0167375242029,
              "width": 74.06952348457754,
              "height": 74.06952348457754
            },
            "initial_radius": 38.724998474121094
          },
          "string": {
            "start": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "end": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "attachment_point": {
              "x": 824.8323943921771,
              "y": 615.910888666359
            },
            "visible_start": {
              "x": 556.0,
              "y": 67.0
            },
            "visible_end": {
              "x": 830.0,
              "y": 617.0
            },
            "visible_length_px": 614.4721311825297,
            "length_to_bob_center_px": 634.6110579092531,
            "subpixel_dir": [
              0.44636405018201547,
              0.8948514595758935
            ]
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072
          },
          "pivot_validation": {
            "method": "vertical_reference_intersection",
            "vref_residual_px": 0.0,
            "support_residual_px": 16.761888060919276,
            "string_fit_residual_px": 0.0,
            "is_geometrically_consistent": true
          },
          "dist_to_perimeter": 3.0285119516699126,
          "diameter_to_string_ratio": 0.12054171332723161
        },
        "vertical_reference": {
          "start": {
            "x": 562.0,
            "y": 61.0
          },
          "end": {
            "x": 562.0,
            "y": 774.0
          }
        },
        "angle_marker": null,
        "edge_map": {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.npy",
          "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.png"
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Source-supported candidate lines/circles/polygons and selected geometry, with scores, rejection/selection diagnostics and unresolved ambiguity where evidence is insufficient.

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** Selected pivot=(562,79.23811193908072), bob=(841.3633806409911,649.0514992664916), radius=37.03476174228877. Method vertical_reference_intersection reports support_residual_px=16.761888060919276 yet is_geometrically_consistent=true. The consistency predicate checks vertical-reference and string residuals but omits support_residual. The source and selected overlay show the misplaced mounting point.

**Changes, provenance and possible information loss:** Candidate generation and selection are distinct. Compare all_candidates_overlay with selected output; inspect locals for fitted lines, rejected candidates and thresholds.

[Complete stage input/output bundle](stage_data/14_cv.json)

- [PendulumCVCandidateExtractor.extract_candidates — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00137_PendulumCVCandidateExtractor.extract_candidates/STAGE.html)

- [Code: ai\evidence\cv\pendulum_cv.py](contracts/ai/evidence/cv/pendulum_cv.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00137_PendulumCVCandidateExtractor.extract_candidates/actual_overlay_on_source.png)

![all_candidates_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00137_PendulumCVCandidateExtractor.extract_candidates/all_candidates_overlay.png)

## 15. SAM2 segmentation prompted by CV

**Execution:** EXECUTED. **Verdict:** BOB SUPPORT ONLY.

**Upstream → downstream:** Domain CV: raw candidates → selected geometry → this component → Semantic-to-spatial grounding and parameter binding.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00332_SAM2SegmentationProvider.segment",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.npy",
        "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\3e310ca53c41125e946e53b1d45a74ab931279617dc9f54b348d1e3e17353371.png"
      },
      "prompt": {
        "box": {
          "x": 804.3286188987023,
          "y": 612.0167375242029,
          "width": 74.06952348457754,
          "height": 74.06952348457754
        },
        "points": [
          [
            841.3633806409911,
            649.0514992664916
          ]
        ],
        "labels": [
          1
        ]
      },
      "source_width": 1280,
      "source_height": 960,
      "entity_id": "bob"
    }
  }
]
```

**What it should receive — expected input:** Source image plus the actual CV-provided box/point prompts, with prompt provenance.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00332_SAM2SegmentationProvider.segment",
      "return_value": {
        "status": "success",
        "masks": [
          {
            "source_asset_id": null,
            "model": "sam2.1_hiera_tiny",
            "source_width": 1280,
            "source_height": 960,
            "_other_fields_in_complete_snapshot": [
              "id",
              "figure_id",
              "bbox_source_px",
              "centroid_source_px",
              "area_px",
              "rle_counts",
              "polygon_approx",
              "confidence",
              "provider",
              "prompt_provenance",
              "verified"
            ]
          }
        ],
        "provider": "sam2.1",
        "model": "sam2.1_hiera_tiny",
        "latency_ms": 11867.196100007277,
        "error": null
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Segmentation mask, score, centroid, area and source bbox. Segmentation only supports the prompted object; it cannot certify unrelated geometry.

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px.

**Changes, provenance and possible information loss:** This active implementation invokes SAM2 only when a best_proposal.bob exists. Absence in optics/circuits is NOT EXECUTED, not a segmentation failure.

[Complete stage input/output bundle](stage_data/15_sam.json)

- [SAM2SegmentationProvider.segment — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00332_SAM2SegmentationProvider.segment/STAGE.html)

- [Code: ai\evidence\segmentation\sam2_provider.py](contracts/ai/evidence/segmentation/sam2_provider.py)

![actual_mask_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00332_SAM2SegmentationProvider.segment/actual_mask_on_source.png)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00332_SAM2SegmentationProvider.segment/actual_overlay_on_source.png)

## 16. Semantic-to-spatial grounding and parameter binding

**Execution:** EXECUTED. **Verdict:** FAIL / UPSTREAM DAMAGE PROPAGATES.

**Upstream → downstream:** SAM2 segmentation prompted by CV → this component → Grounded BookIR and OCR-enriched PageIR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00339_PendulumGrounder.ground",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
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
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
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
            "id": "bob_1",
            "type": "bob",
            "label": "m",
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
            "id": "string_1",
            "type": "string",
            "label": "L",
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
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
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
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
        "all_circles": {
          "count": 18,
          "first_8_records": [
            {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094
            },
            {
              "center": {
                "x": 571.1147334653926,
                "y": 164.0757964347032
              },
              "radius_px": 91.9470552672825,
              "bounds": {
                "x": 479.16767819811014,
                "y": 72.1287411674207,
                "width": 183.894110534565,
                "height": 183.894110534565
              },
              "initial_radius": 87.71499633789062
            },
            {
              "center": {
                "x": 655.0319384260869,
                "y": 134.6649499092607
              },
              "radius_px": 70.03571393799845,
              "bounds": {
                "x": 584.9962244880884,
                "y": 64.62923597126226,
                "width": 140.0714278759969,
                "height": 140.0714278759969
              },
              "initial_radius": 73.56999969482422
            },
            {
              "center": {
                "x": 596.3270581458659,
                "y": 224.44527219440852
              },
              "radius_px": 35.84310957893747,
              "bounds": {
                "x": 560.4839485669283,
                "y": 188.60216261547106,
                "width": 71.68621915787494,
                "height": 71.68621915787494
              },
              "initial_radius": 34.93000030517578
            },
            {
              "center": {
                "x": 590.0557212477751,
                "y": 282.59074774758096
              },
              "radius_px": 31.563455909281895,
              "bounds": {
                "x": 558.4922653384932,
                "y": 251.02729183829908,
                "width": 63.12691181856379,
                "height": 63.12691181856379
              },
              "initial_radius": 32.744998931884766
            },
            {
              "center": {
                "x": 638.0950823036292,
                "y": 298.775292891693
              },
              "radius_px": 36.79998802429366,
              "bounds": {
                "x": 601.2950942793356,
                "y": 261.97530486739936,
                "width": 73.59997604858732,
                "height": 73.59997604858732
              },
              "initial_radius": 39.18499755859375
            },
            {
              "center": {
                "x": 414.6893717395315,
                "y": 864.7054522078654
              },
              "radius_px": 25.818906653177198,
              "bounds": {
                "x": 388.87046508635433,
                "y": 838.8865455546882,
                "width": 51.637813306354396,
                "height": 51.637813306354396
              },
              "initial_radius": 26.190000534057617
            },
            {
              "center": {
                "x": 511.0339222222365,
                "y": 124.67930940645624
              },
              "radius_px": 56.28152089013627,
              "bounds": {
                "x": 454.75240133210025,
                "y": 68.39778851631996,
                "width": 112.56304178027254,
                "height": 112.56304178027254
              },
              "initial_radius": 53.904998779296875
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "pin_candidates": [
          {
            "center": {
              "x": 611.0,
              "y": 291.0
            },
            "radius_px": 22.47230339050293,
            "bounds": {
              "x": 588.5276966094971,
              "y": 268.52769660949707,
              "width": 44.94460678100586,
              "height": 44.94460678100586
            },
            "initial_radius": 22.47230339050293
          },
          {
            "center": {
              "x": 609.5,
              "y": 300.5
            },
            "radius_px": 10.12432861328125,
            "bounds": {
              "x": 599.3756713867188,
              "y": 290.37567138671875,
              "width": 20.2486572265625,
              "height": 20.2486572265625
            },
            "initial_radius": 10.12432861328125
          },
          {
            "center": {
              "x": 611.5,
              "y": 280.5
            },
            "radius_px": 9.617792129516602,
            "bounds": {
              "x": 601.8822078704834,
              "y": 270.8822078704834,
              "width": 19.235584259033203,
              "height": 19.235584259033203
            },
            "initial_radius": 9.617792129516602
          }
        ],
        "all_lines": {
          "count": 9,
          "first_8_records": [
            {
              "start": {
                "x": 606.0,
                "y": 166.0
              },
              "end": {
                "x": 831.0,
                "y": 617.0
              },
              "length_px": 504.00992053728464,
              "dx": 225.0,
              "dy": 451.0
            },
            {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "dx": 0.0,
              "dy": 713.0
            },
            {
              "start": {
                "x": 553.0,
                "y": 70.0
              },
              "end": {
                "x": 826.0,
                "y": 619.0
              },
              "length_px": 613.1313073070074,
              "dx": 273.0,
              "dy": 549.0
            },
            {
              "start": {
                "x": 565.0,
                "y": 112.0
              },
              "end": {
                "x": 565.0,
                "y": 775.0
              },
              "length_px": 663.0,
              "dx": 0.0,
              "dy": 663.0
            },
            {
              "start": {
                "x": 556.0,
                "y": 67.0
              },
              "end": {
                "x": 830.0,
                "y": 617.0
              },
              "length_px": 614.4721311825297,
              "dx": 274.0,
              "dy": 550.0
            },
            {
              "start": {
                "x": 563.0,
                "y": 131.0
              },
              "end": {
                "x": 563.0,
                "y": 775.0
              },
              "length_px": 644.0,
              "dx": 0.0,
              "dy": 644.0
            },
            {
              "start": {
                "x": 614.0,
                "y": 192.0
              },
              "end": {
                "x": 692.0,
                "y": 347.0
              },
              "length_px": 173.5194513592064,
              "dx": 78.0,
              "dy": 155.0
            },
            {
              "start": {
                "x": 635.0,
                "y": 859.0
              },
              "end": {
                "x": 557.0,
                "y": 871.0
              },
              "length_px": 78.91767862779544,
              "dx": -78.0,
              "dy": 12.0
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "support_lines": [
          {
            "start": {
              "x": 577.0,
              "y": 96.0
            },
            "end": {
              "x": 699.0,
              "y": 96.0
            },
            "length_px": 122.0,
            "y_avg": 96.0
          },
          {
            "start": {
              "x": 428.0,
              "y": 92.0
            },
            "end": {
              "x": 700.0,
              "y": 92.0
            },
            "length_px": 272.0,
            "y_avg": 92.0
          },
          {
            "start": {
              "x": 428.0,
              "y": 96.0
            },
            "end": {
              "x": 550.0,
              "y": 96.0
            },
            "length_px": 122.0,
            "y_avg": 96.0
          }
        ],
        "paired_candidates": [
          {
            "score": 138.51394009521402,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094,
              "_nested_fields_in_complete_snapshot": []
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "visible_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.4721311825297,
              "length_to_bob_center_px": 634.6110579092531,
              "_nested_fields_in_complete_snapshot": [
                "subpixel_dir"
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 16.761888060919276,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.0285119516699126,
            "diameter_to_string_ratio": 0.12054171332723161
          },
          {
            "score": 136.88279171681498,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094,
              "_nested_fields_in_complete_snapshot": []
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 88.07255651467977
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8736064266867,
                "y": 615.8903635249438
              },
              "visible_start": {
                "x": 553.0,
                "y": 70.0
              },
              "visible_end": {
                "x": 826.0,
                "y": 619.0
              },
              "visible_length_px": 613.1313073070074,
              "length_to_bob_center_px": 626.6907312655134,
              "_nested_fields_in_complete_snapshot": [
                "subpixel_dir"
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 88.07255651467977
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 7.927443485320225,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.2838199349269033,
            "diameter_to_string_ratio": 0.1208053195161496
          },
          {
            "score": 133.0607012108778,
            "bob": {
              "center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "radius_px": 37.03476174228877,
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "initial_radius": 38.724998474121094,
              "_nested_fields_in_complete_snapshot": []
            },
            "string": {
              "start": {
                "x": 562.0,
                "y": 75.69595223419401
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "attachment_point": {
                "x": 824.8424517397193,
                "y": 615.9058738304373
              },
              "visible_start": {
                "x": 606.0,
                "y": 166.0
              },
              "visible_end": {
                "x": 831.0,
                "y": 617.0
              },
              "visible_length_px": 504.00992053728464,
              "length_to_bob_center_px": 637.7934475642318,
              "_nested_fields_in_complete_snapshot": [
                "subpixel_dir"
              ]
            },
            "pivot": {
              "x": 562.0,
              "y": 75.69595223419401
            },
            "pivot_validation": {
              "method": "vertical_reference_intersection",
              "vref_residual_px": 0.0,
              "support_residual_px": 20.30404776580599,
              "string_fit_residual_px": 0.0,
              "is_geometrically_consistent": true
            },
            "dist_to_perimeter": 3.34947914676966,
            "diameter_to_string_ratio": 0.14696044753567142
          }
        ],
        "best_proposal": {
          "score": 138.51394009521402,
          "bob": {
            "center": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "radius_px": 37.03476174228877,
            "bounds": {
              "x": 804.3286188987023,
              "y": 612.0167375242029,
              "width": 74.06952348457754,
              "height": 74.06952348457754
            },
            "initial_radius": 38.724998474121094
          },
          "string": {
            "start": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "end": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "attachment_point": {
              "x": 824.8323943921771,
              "y": 615.910888666359
            },
            "visible_start": {
              "x": 556.0,
              "y": 67.0
            },
            "visible_end": {
              "x": 830.0,
              "y": 617.0
            },
            "visible_length_px": 614.4721311825297,
            "length_to_bob_center_px": 634.6110579092531,
            "subpixel_dir": [
              0.44636405018201547,
              0.8948514595758935
            ]
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072
          },
          "pivot_validation": {
            "method": "vertical_reference_intersection",
            "vref_residual_px": 0.0,
            "support_residual_px": 16.761888060919276,
            "string_fit_residual_px": 0.0,
            "is_geometrically_consistent": true
          },
          "dist_to_perimeter": 3.0285119516699126,
          "diameter_to_string_ratio": 0.12054171332723161
        },
        "vertical_reference": {
          "start": {
            "x": 562.0,
            "y": 61.0
          },
          "end": {
            "x": 562.0,
            "y": 774.0
          }
        },
        "angle_marker": null,
        "edge_map": {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.npy",
          "image": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017\\arrays\\7d736214b3c297eecbabe2429111ab4441689718e8109ef11b71a00fbdf8937a.png"
        }
      },
      "ocr_result": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_003",
            "raw_text": "Fig. 1 Simple Pendulum",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 338.0,
              "y": 827.0,
              "width": 599.0,
              "height": 78.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.98953,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig",
                "script": "latin",
                "confidence": 0.9781465020509537,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "L",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 738.0,
              "y": 357.0,
              "width": 55.0,
              "height": 61.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99996,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "]",
                "script": "latin",
                "confidence": 0.47404840130162995,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "m",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 896.0,
              "y": 632.0,
              "width": 63.0,
              "height": 50.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99987,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "171",
                "script": "latin",
                "confidence": 0.5532381496450604,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_greek_theta_597_270",
            "raw_text": "θ",
            "normalized_text": "θ",
            "bbox_source_px": {
              "x": 597.0,
              "y": 270.0,
              "width": 28.0,
              "height": 43.0
            },
            "polygon_source_px": null,
            "confidence": 0.96,
            "script_candidate": "greek",
            "language_candidate": "el",
            "provider": "greek_symbol_ocr",
            "recognizer_model": "visual_topology_matcher",
            "candidate_alternatives": [
              {
                "text": "θ",
                "script": "greek",
                "name": "theta",
                "confidence": 0.96,
                "provider": "symbol_engine"
              }
            ],
            "evidence_ref": ""
          }
        ],
        "provider": "multi_ocr_router",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr+easyocr+greek_ocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
        "recognizer_language": "en+bn+el",
        "latency_ms": 13201.892899989616,
        "error": null,
        "metadata": {
          "bangla_available": true,
          "greek_available": true,
          "formula_available": false,
          "regions_count": 3,
          "token_count": 4
        }
      },
      "seg_result": {
        "status": "success",
        "masks": [
          {
            "source_asset_id": null,
            "model": "sam2.1_hiera_tiny",
            "source_width": 1280,
            "source_height": 960,
            "_other_fields_in_complete_snapshot": [
              "id",
              "figure_id",
              "bbox_source_px",
              "centroid_source_px",
              "area_px",
              "rle_counts",
              "polygon_approx",
              "confidence",
              "provider",
              "prompt_provenance",
              "verified"
            ]
          }
        ],
        "provider": "sam2.1",
        "model": "sam2.1_hiera_tiny",
        "latency_ms": 11867.196100007277,
        "error": null
      },
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
      "call": "00339_PendulumGrounder.ground",
      "return_value": {
        "grounded_book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
            "entity_id": "bob_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ],
            "checks": {
              "cv_center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "sam_centroid": {
                "x": 841.8054054054054,
                "y": 650.2034594594595
              },
              "center_distance_px": 1.23,
              "tolerance_px": 14.81
            },
            "conflicts": [],
            "notes": "CV circle and SAM 2 mask centroids agree within tolerance and pass consistency checks."
          },
          {
            "entity_id": "string_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ],
            "checks": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61
            },
            "conflicts": [],
            "notes": "String verified and connected to bob candidate."
          },
          {
            "entity_id": "pivot_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ],
            "checks": {
              "pivot": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "vertical_reference_x": 562.0,
              "vref_residual_px": 0.0,
              "support_residual_px": 16.761888060919276,
              "string_fit_residual_px": 0.0
            },
            "conflicts": [],
            "notes": "Pivot grounded at multi-constraint suspension junction."
          },
          {
            "entity_id": "ref_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ],
            "checks": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0
            },
            "conflicts": [],
            "notes": "Vertical reference dashed line detected and grounded."
          }
        ],
        "new_evidence_records": {
          "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44": {
            "id": "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
            "method": "classical_cv",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.85,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "opencv_hough_tls",
            "model": null,
            "version": null,
            "payload": {
              "bob_center": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "bob_radius_px": 37.03476174228877,
              "string_start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "string_end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "string_length_px": 634.6110579092531,
              "pivot": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "vertical_reference": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "metadata": {}
          },
          "ev_seg_bob_mask_bob_53389": {
            "id": "ev_seg_bob_mask_bob_53389",
            "method": "segmentation",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.9772201180458069,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "sam2.1",
            "model": "sam2.1_hiera_tiny",
            "version": null,
            "payload": {
              "centroid": {
                "x": 841.8054054054054,
                "y": 650.2034594594595
              },
              "area_px": 4625.0,
              "bounds": {
                "x": 804.0,
                "y": 612.0,
                "width": 75.0,
                "height": 76.0
              },
              "mask_id": "mask_bob_53389"
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_003": {
            "id": "ev_ocr_ocr_tok_003",
            "method": "ocr",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.98953,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Fig. 1 Simple Pendulum",
              "normalized_text": null,
              "bbox": {
                "x": 338.0,
                "y": 827.0,
                "width": 599.0,
                "height": 78.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_001": {
            "id": "ev_ocr_ocr_tok_001",
            "method": "ocr",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.99996,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "L",
              "normalized_text": null,
              "bbox": {
                "x": 738.0,
                "y": 357.0,
                "width": 55.0,
                "height": 61.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_002": {
            "id": "ev_ocr_ocr_tok_002",
            "method": "ocr",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.99987,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "m",
              "normalized_text": null,
              "bbox": {
                "x": 896.0,
                "y": 632.0,
                "width": 63.0,
                "height": 50.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_greek_theta_597_270": {
            "id": "ev_ocr_ocr_tok_greek_theta_597_270",
            "method": "ocr",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "confidence": 0.96,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "θ",
              "normalized_text": "θ",
              "bbox": {
                "x": 597.0,
                "y": 270.0,
                "width": 28.0,
                "height": 43.0
              }
            },
            "metadata": {}
          }
        },
        "candidate_parameters": [
          {
            "raw_text": "L",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "length_symbol",
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.99996
          },
          {
            "raw_text": "m",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "mass_symbol",
            "source_ocr_token_id": "ocr_tok_002",
            "confidence": 0.99987
          },
          {
            "raw_text": "θ",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "angle_symbol",
            "source_ocr_token_id": "ocr_tok_greek_theta_597_270",
            "confidence": 0.96
          }
        ],
        "parameter_associations": []
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Entities bound to supported source geometry; numeric OCR values attached to the correct entity with units/evidence; relationships still resolve after any entity changes. Unresolved evidence stays unresolved.

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px.

**Changes, provenance and possible information loss:** This is where semantic roles become authoritative source coordinates. Inspect grounded_book_ir, diagnostics, candidate_parameters and associations separately.

[Complete stage input/output bundle](stage_data/16_ground.json)

- [PendulumGrounder.ground — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00339_PendulumGrounder.ground/STAGE.html)

- [Code: ai\evidence\grounding\pendulum.py](contracts/ai/evidence/grounding/pendulum.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00339_PendulumGrounder.ground/actual_overlay_on_source.png)

## 17. Grounded BookIR and OCR-enriched PageIR

**Execution:** EXECUTED. **Verdict:** FAIL / UPSTREAM DAMAGE PROPAGATES.

**Upstream → downstream:** Semantic-to-spatial grounding and parameter binding → this component → Enforce authoritative source dimensions.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00044_EvidenceExtractionPipeline.extract_and_fuse",
    "value": {
      "asset": {
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
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
            "id": "bob_1",
            "type": "bob",
            "label": "m",
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
            "id": "string_1",
            "type": "string",
            "label": "L",
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
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
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
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
      "call": "00044_EvidenceExtractionPipeline.extract_and_fuse",
      "return_value": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.95
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.92
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "effective_pendulum": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "_nested_fields_in_complete_snapshot": []
              },
              "visible_string": {
                "start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "length_px": 614.47,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed"
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
      "call": "00044_EvidenceExtractionPipeline.extract_and_fuse",
      "page_ir_after": {
        "version": "1.0",
        "source": {
          "assetId": "25c3ba19a02041ee9ec790156fc87e44",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_25c3ba19.jpg",
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
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
            "id": "ocr_tok_003",
            "text": "Fig. 1 Simple Pendulum",
            "x": 338.0,
            "y": 827.0,
            "width": 599.0,
            "height": 78.0,
            "confidence": 0.98953,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_001",
            "text": "L",
            "x": 738.0,
            "y": 357.0,
            "width": 55.0,
            "height": 61.0,
            "confidence": 0.99996,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_002",
            "text": "m",
            "x": 896.0,
            "y": 632.0,
            "width": 63.0,
            "height": 50.0,
            "confidence": 0.99987,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_greek_theta_597_270",
            "text": "θ",
            "x": 597.0,
            "y": 270.0,
            "width": 28.0,
            "height": 43.0,
            "confidence": 0.96,
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

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px.

**Changes, provenance and possible information loss:** The wrapper returns after stages 8–16. Its entry record comes earlier in the profiler, but its output belongs here in the data-flow story.

[Complete stage input/output bundle](stage_data/17_fused.json)

- [EvidenceExtractionPipeline.extract_and_fuse — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00044_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- [Code: ai\evidence\pipeline.py](contracts/ai/evidence/pipeline.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00044_EvidenceExtractionPipeline.extract_and_fuse/actual_overlay_on_source.png)

## 18. Enforce authoritative source dimensions

**Execution:** EXECUTED. **Verdict:** FRAME PASS; GEOMETRY STILL WRONG.

**Upstream → downstream:** Grounded BookIR and OCR-enriched PageIR → this component → Automatic resolution and explicit policy values.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00362_enforce_source_dimensions",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
        "id": "25c3ba19a02041ee9ec790156fc87e44",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-38 (2).jpg",
        "byte_size": 35941,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_25c3ba19.jpg"
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
      "call": "00362_enforce_source_dimensions",
      "return_value": null
    }
  ],
  "in_place_outputs": [
    {
      "call": "00362_enforce_source_dimensions",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
          "calibration": null,
          "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Source extent is enforced without correcting the already incorrect landmark/topology evidence.

**Changes, provenance and possible information loss:** Metadata enforcement is not geometric validation. Mutation is recorded in locals_after when the function returns None.

[Complete stage input/output bundle](stage_data/18_dimensions.json)

- [enforce_source_dimensions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00362_enforce_source_dimensions/STAGE.html)

- [Code: ai\ingestion\source_dimensions.py](contracts/ai/ingestion/source_dimensions.py)

## 19. Automatic resolution and explicit policy values

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Enforce authoritative source dimensions → this component → Resolution decisions, units and calibration.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00363_AutoResolutionEngine.resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
      "call": "00363_AutoResolutionEngine.resolve",
      "return_value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0,
            "mass": 1.0,
            "length": 1.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "mass": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "length": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [
            {
              "parameter": "gravity",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "value": 9.80665,
              "unit": "m/s²",
              "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "damping",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "value": 0.0,
              "unit": "1/s",
              "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "mass",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "kg",
              "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "length",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "m",
              "reason": "Standard 1.0 m simple pendulum string length.",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
              "confidence": 0.95
            }
          ],
          "calibration": {
            "pixels_per_meter": 634.61,
            "meters_per_pixel": 0.0015757709459352988,
            "reference_pixel_span": 634.61,
            "reference_physical_m": 1.0,
            "reference_parameter": "length",
            "provenance": {
              "source": "derived_calibration",
              "evidence_refs": [
                "string_1",
                "auto_policy_standard_pendulum_length"
              ],
              "confidence": 0.99,
              "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "string_1",
                "auto_policy_standard_pendulum_length"
              ]
            },
            "pixels_per_meter_x": 634.61,
            "pixels_per_meter_y": 634.61
          },
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
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "failures": [],
        "readiness": {
          "subtype": "pendulum",
          "status": "READY_TO_COMPILE",
          "ready": true,
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity",
            "mass",
            "damping",
            "length"
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale.

**Changes, provenance and possible information loss:** Inspect field_changes.json for every addition/replacement. Auto-policy execution in this checkout may satisfy requirements without a human decision; that is observed behavior, not approval supplied during tracing.

[Complete stage input/output bundle](stage_data/19_auto.json)

- [AutoResolutionEngine.resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00363_AutoResolutionEngine.resolve/STAGE.html)

- [Every changed field before/after](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00363_AutoResolutionEngine.resolve/field_changes.json)

- [Code: ai\resolution\auto.py](contracts/ai/resolution/auto.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00363_AutoResolutionEngine.resolve/actual_overlay_on_source.png)

## 20. Resolution decisions, units and calibration

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Automatic resolution and explicit policy values → this component → Requirement and ambiguity analysis.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 12,
  "first_8_records": [
    {
      "call": "00375_ResolutionEngine.apply_resolution",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
                "policy_id": null,
                "policy_version": null,
                "user_accepted": null,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
        "decision": {
          "source": "policy_default",
          "_other_fields_in_complete_snapshot": [
            "id",
            "requirement_id",
            "parameter_name",
            "value",
            "unit",
            "raw_input",
            "policy_id",
            "policy_version",
            "superseded_value",
            "evidence_refs",
            "timestamp",
            "notes",
            "target_subtype",
            "resolved_value",
            "canonical_unit",
            "original_entered_value",
            "original_unit",
            "resolution_source",
            "user_accepted",
            "resolved_by"
          ]
        }
      }
    },
    {
      "call": "00382_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "pendulum",
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "effective_pendulum": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "_nested_fields_in_complete_snapshot": []
              },
              "visible_string": {
                "start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "length_px": 614.47,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed"
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.95
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.92
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          },
          "gravity": 9.80665
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        }
      }
    },
    {
      "call": "00429_ResolutionEngine.apply_resolution",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
        "decision": {
          "source": "policy_default",
          "_other_fields_in_complete_snapshot": [
            "id",
            "requirement_id",
            "parameter_name",
            "value",
            "unit",
            "raw_input",
            "policy_id",
            "policy_version",
            "superseded_value",
            "evidence_refs",
            "timestamp",
            "notes",
            "target_subtype",
            "resolved_value",
            "canonical_unit",
            "original_entered_value",
            "original_unit",
            "resolution_source",
            "user_accepted",
            "resolved_by"
          ]
        }
      }
    },
    {
      "call": "00436_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "pendulum",
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "effective_pendulum": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "_nested_fields_in_complete_snapshot": []
              },
              "visible_string": {
                "start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "length_px": 614.47,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed"
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.95
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.92
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          },
          "gravity": 9.80665,
          "damping": 0.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        }
      }
    },
    {
      "call": "00483_ResolutionEngine.apply_resolution",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
        "decision": {
          "source": "policy_default",
          "_other_fields_in_complete_snapshot": [
            "id",
            "requirement_id",
            "parameter_name",
            "value",
            "unit",
            "raw_input",
            "policy_id",
            "policy_version",
            "superseded_value",
            "evidence_refs",
            "timestamp",
            "notes",
            "target_subtype",
            "resolved_value",
            "canonical_unit",
            "original_entered_value",
            "original_unit",
            "resolution_source",
            "user_accepted",
            "resolved_by"
          ]
        }
      }
    },
    {
      "call": "00490_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "pendulum",
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "effective_pendulum": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "_nested_fields_in_complete_snapshot": []
              },
              "visible_string": {
                "start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "length_px": 614.47,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed"
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.95
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.92
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          },
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        }
      }
    },
    {
      "call": "00537_ResolutionEngine.apply_resolution",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0,
            "mass": 1.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "mass": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
        "decision": {
          "source": "policy_default",
          "_other_fields_in_complete_snapshot": [
            "id",
            "requirement_id",
            "parameter_name",
            "value",
            "unit",
            "raw_input",
            "policy_id",
            "policy_version",
            "superseded_value",
            "evidence_refs",
            "timestamp",
            "notes",
            "target_subtype",
            "resolved_value",
            "canonical_unit",
            "original_entered_value",
            "original_unit",
            "resolution_source",
            "user_accepted",
            "resolved_by"
          ]
        }
      }
    },
    {
      "call": "00544_CalibrationEngine.derive_for_subtype",
      "value": {
        "subtype": "pendulum",
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "effective_pendulum": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "_nested_fields_in_complete_snapshot": []
              },
              "visible_string": {
                "start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "length_px": 614.47,
                "_nested_fields_in_complete_snapshot": []
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed"
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.95
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ],
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389"
              ]
            }
          },
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.92
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ],
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          },
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
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
    "count": 12,
    "first_8_records": [
      {
        "call": "00375_ResolutionEngine.apply_resolution",
        "return_value": {
          "success": true,
          "parameter_name": "gravity",
          "resolved_value": 9.80665,
          "canonical_unit": "m/s²",
          "original_entered_value": "9.80665",
          "resolution": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirement_id",
              "parameter_name",
              "value",
              "unit",
              "raw_input",
              "policy_id",
              "policy_version",
              "superseded_value",
              "evidence_refs",
              "timestamp",
              "notes",
              "target_subtype",
              "resolved_value",
              "canonical_unit",
              "original_entered_value",
              "original_unit",
              "resolution_source",
              "user_accepted",
              "resolved_by"
            ]
          },
          "readiness_report": {
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "ready": false,
            "blockers": [
              "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
              "Subtype requires 'damping'. No visual/OCR value found. Explicit policy 'Ideal Undamped Oscillation' (0.0 1/s) is available.",
              "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
              "Simulation requires length or pixels_per_meter."
            ],
            "warnings": [],
            "missing_requirements": [
              "mass",
              "damping",
              "length"
            ],
            "satisfied_requirements": [
              "pivot",
              "bob_position",
              "string_length_px",
              "bob_radius_px",
              "gravity"
            ],
            "_other_fields_in_complete_snapshot": [
              "book_ir_status",
              "book_ir_id",
              "resolved_requirements",
              "policy_assumptions",
              "unresolved_ambiguities",
              "calibration_status"
            ]
          },
          "error": null
        }
      },
      {
        "call": "00382_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "00429_ResolutionEngine.apply_resolution",
        "return_value": {
          "success": true,
          "parameter_name": "damping",
          "resolved_value": 0.0,
          "canonical_unit": "1/s",
          "original_entered_value": "0.0",
          "resolution": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirement_id",
              "parameter_name",
              "value",
              "unit",
              "raw_input",
              "policy_id",
              "policy_version",
              "superseded_value",
              "evidence_refs",
              "timestamp",
              "notes",
              "target_subtype",
              "resolved_value",
              "canonical_unit",
              "original_entered_value",
              "original_unit",
              "resolution_source",
              "user_accepted",
              "resolved_by"
            ]
          },
          "readiness_report": {
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "ready": false,
            "blockers": [
              "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
              "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
              "Simulation requires length or pixels_per_meter."
            ],
            "warnings": [],
            "missing_requirements": [
              "mass",
              "length"
            ],
            "satisfied_requirements": [
              "pivot",
              "bob_position",
              "string_length_px",
              "bob_radius_px",
              "gravity",
              "damping"
            ],
            "_other_fields_in_complete_snapshot": [
              "book_ir_status",
              "book_ir_id",
              "resolved_requirements",
              "policy_assumptions",
              "unresolved_ambiguities",
              "calibration_status"
            ]
          },
          "error": null
        }
      },
      {
        "call": "00436_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "00483_ResolutionEngine.apply_resolution",
        "return_value": {
          "success": true,
          "parameter_name": "mass",
          "resolved_value": 1.0,
          "canonical_unit": "kg",
          "original_entered_value": "1.0",
          "resolution": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirement_id",
              "parameter_name",
              "value",
              "unit",
              "raw_input",
              "policy_id",
              "policy_version",
              "superseded_value",
              "evidence_refs",
              "timestamp",
              "notes",
              "target_subtype",
              "resolved_value",
              "canonical_unit",
              "original_entered_value",
              "original_unit",
              "resolution_source",
              "user_accepted",
              "resolved_by"
            ]
          },
          "readiness_report": {
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "ready": false,
            "blockers": [
              "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
              "Simulation requires length or pixels_per_meter."
            ],
            "warnings": [],
            "missing_requirements": [
              "length"
            ],
            "satisfied_requirements": [
              "pivot",
              "bob_position",
              "string_length_px",
              "bob_radius_px",
              "gravity",
              "mass",
              "damping"
            ],
            "_other_fields_in_complete_snapshot": [
              "book_ir_status",
              "book_ir_id",
              "resolved_requirements",
              "policy_assumptions",
              "unresolved_ambiguities",
              "calibration_status"
            ]
          },
          "error": null
        }
      },
      {
        "call": "00490_CalibrationEngine.derive_for_subtype",
        "return_value": null
      },
      {
        "call": "00537_ResolutionEngine.apply_resolution",
        "return_value": {
          "success": true,
          "parameter_name": "length",
          "resolved_value": 1.0,
          "canonical_unit": "m",
          "original_entered_value": "1.0",
          "resolution": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirement_id",
              "parameter_name",
              "value",
              "unit",
              "raw_input",
              "policy_id",
              "policy_version",
              "superseded_value",
              "evidence_refs",
              "timestamp",
              "notes",
              "target_subtype",
              "resolved_value",
              "canonical_unit",
              "original_entered_value",
              "original_unit",
              "resolution_source",
              "user_accepted",
              "resolved_by"
            ]
          },
          "readiness_report": {
            "subtype": "pendulum",
            "status": "READY_TO_COMPILE",
            "ready": true,
            "blockers": [],
            "warnings": [],
            "missing_requirements": [],
            "satisfied_requirements": [
              "pivot",
              "bob_position",
              "string_length_px",
              "bob_radius_px",
              "gravity",
              "mass",
              "damping",
              "length"
            ],
            "_other_fields_in_complete_snapshot": [
              "book_ir_status",
              "book_ir_id",
              "resolved_requirements",
              "policy_assumptions",
              "unresolved_ambiguities",
              "calibration_status"
            ]
          },
          "error": null
        }
      },
      {
        "call": "00544_CalibrationEngine.derive_for_subtype",
        "return_value": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        }
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Consistent resolved units and explicit calibration provenance. A scale derived using assumed physical length must remain assumption-derived; it is not measured ground truth.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale.

**Changes, provenance and possible information loss:** Several calls can occur inside auto-resolution. Exact invocation records are kept separately; null return can mean calibration was unavailable, not that a zero scale was measured.

[Complete stage input/output bundle](stage_data/20_calibration.json)

- [ResolutionEngine.apply_resolution — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00375_ResolutionEngine.apply_resolution/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00382_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.apply_resolution — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00429_ResolutionEngine.apply_resolution/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00436_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.apply_resolution — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00483_ResolutionEngine.apply_resolution/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00490_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.apply_resolution — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00537_ResolutionEngine.apply_resolution/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00544_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_calibration — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00545_CalibrationEngine.derive_calibration/STAGE.html)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00636_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00638_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_calibration — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00639_CalibrationEngine.derive_calibration/STAGE.html)

- [Code: ai\resolution\engine.py](contracts/ai/resolution/engine.py)

- [Code: ai\resolution\calibration.py](contracts/ai/resolution/calibration.py)

## 21. Requirement and ambiguity analysis

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Resolution decisions, units and calibration → this component → Readiness decision.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 21,
  "first_8_records": [
    {
      "call": "00384_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
      "call": "00386_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
          "domain": "mechanics",
          "subtype": "pendulum",
          "required_entities": [
            "pivot",
            "bob",
            "string"
          ],
          "required_geometry": [
            "pivot",
            "bob_center",
            "string_length_px",
            "bob_radius_px"
          ],
          "parameters": {
            "pivot": {
              "id": "req_pendulum_pivot",
              "name": "pivot",
              "dimension": "point_2d",
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
            "bob_position": {
              "id": "req_pendulum_bob_position",
              "name": "bob_position",
              "dimension": "point_2d",
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
            "string_length_px": {
              "id": "req_pendulum_string_length_px",
              "name": "string_length_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "bob_radius_px": {
              "id": "req_pendulum_bob_radius_px",
              "name": "bob_radius_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "gravity": {
              "id": "req_pendulum_gravity",
              "name": "gravity",
              "dimension": "acceleration",
              "required": true,
              "allowed_units": [
                "m/s²",
                "m/s^2",
                "m/s2",
                "cm/s²"
              ],
              "canonical_unit": "m/s²",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_earth_gravity",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "mass": {
              "id": "req_pendulum_mass",
              "name": "mass",
              "dimension": "mass",
              "required": true,
              "allowed_units": [
                "kg",
                "g",
                "kilogram",
                "gram"
              ],
              "canonical_unit": "kg",
              "min_value": 0.0001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_standard_mass",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "damping": {
              "id": "req_pendulum_damping",
              "name": "damping",
              "dimension": "damping",
              "required": true,
              "allowed_units": [
                "1/s",
                "s^-1",
                "s_inv",
                "hz"
              ],
              "canonical_unit": "1/s",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_zero_damping",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "length": {
              "id": "req_pendulum_length",
              "name": "length",
              "dimension": "length",
              "required": true,
              "allowed_units": [
                "m",
                "cm",
                "mm",
                "meter",
                "centimeter"
              ],
              "canonical_unit": "m",
              "min_value": 0.001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "pixels_per_meter": {
              "id": "req_pendulum_pixels_per_meter",
              "name": "pixels_per_meter",
              "dimension": "pixels_per_meter",
              "required": false,
              "allowed_units": [],
              "canonical_unit": "px/m",
              "min_value": 0.01,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
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
          "one_of_requirements": [
            [
              "length",
              "pixels_per_meter"
            ]
          ],
          "allowed_policies": [
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_standard_pendulum_length"
          ],
          "parameter_aliases": {
            "bob_center": "bob_position",
            "length_m": "length",
            "string_length": "string_length_px",
            "length_px": "string_length_px",
            "gravity_m_s2": "gravity",
            "damping_s_inv": "damping",
            "mass_kg": "mass"
          },
          "notes": "Simple planar gravity pendulum running analytical RK4 dynamics."
        },
        "issues": []
      }
    },
    {
      "call": "00387_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
          "domain": "mechanics",
          "subtype": "pendulum",
          "required_entities": [
            "pivot",
            "bob",
            "string"
          ],
          "required_geometry": [
            "pivot",
            "bob_center",
            "string_length_px",
            "bob_radius_px"
          ],
          "parameters": {
            "pivot": {
              "id": "req_pendulum_pivot",
              "name": "pivot",
              "dimension": "point_2d",
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
            "bob_position": {
              "id": "req_pendulum_bob_position",
              "name": "bob_position",
              "dimension": "point_2d",
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
            "string_length_px": {
              "id": "req_pendulum_string_length_px",
              "name": "string_length_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "bob_radius_px": {
              "id": "req_pendulum_bob_radius_px",
              "name": "bob_radius_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "gravity": {
              "id": "req_pendulum_gravity",
              "name": "gravity",
              "dimension": "acceleration",
              "required": true,
              "allowed_units": [
                "m/s²",
                "m/s^2",
                "m/s2",
                "cm/s²"
              ],
              "canonical_unit": "m/s²",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_earth_gravity",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "mass": {
              "id": "req_pendulum_mass",
              "name": "mass",
              "dimension": "mass",
              "required": true,
              "allowed_units": [
                "kg",
                "g",
                "kilogram",
                "gram"
              ],
              "canonical_unit": "kg",
              "min_value": 0.0001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_standard_mass",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "damping": {
              "id": "req_pendulum_damping",
              "name": "damping",
              "dimension": "damping",
              "required": true,
              "allowed_units": [
                "1/s",
                "s^-1",
                "s_inv",
                "hz"
              ],
              "canonical_unit": "1/s",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_zero_damping",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "length": {
              "id": "req_pendulum_length",
              "name": "length",
              "dimension": "length",
              "required": true,
              "allowed_units": [
                "m",
                "cm",
                "mm",
                "meter",
                "centimeter"
              ],
              "canonical_unit": "m",
              "min_value": 0.001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "pixels_per_meter": {
              "id": "req_pendulum_pixels_per_meter",
              "name": "pixels_per_meter",
              "dimension": "pixels_per_meter",
              "required": false,
              "allowed_units": [],
              "canonical_unit": "px/m",
              "min_value": 0.01,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
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
          "one_of_requirements": [
            [
              "length",
              "pixels_per_meter"
            ]
          ],
          "allowed_policies": [
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_standard_pendulum_length"
          ],
          "parameter_aliases": {
            "bob_center": "bob_position",
            "length_m": "length",
            "string_length": "string_length_px",
            "length_px": "string_length_px",
            "gravity_m_s2": "gravity",
            "damping_s_inv": "damping",
            "mass_kg": "mass"
          },
          "notes": "Simple planar gravity pendulum running analytical RK4 dynamics."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "00438_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
      "call": "00440_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
          "domain": "mechanics",
          "subtype": "pendulum",
          "required_entities": [
            "pivot",
            "bob",
            "string"
          ],
          "required_geometry": [
            "pivot",
            "bob_center",
            "string_length_px",
            "bob_radius_px"
          ],
          "parameters": {
            "pivot": {
              "id": "req_pendulum_pivot",
              "name": "pivot",
              "dimension": "point_2d",
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
            "bob_position": {
              "id": "req_pendulum_bob_position",
              "name": "bob_position",
              "dimension": "point_2d",
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
            "string_length_px": {
              "id": "req_pendulum_string_length_px",
              "name": "string_length_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "bob_radius_px": {
              "id": "req_pendulum_bob_radius_px",
              "name": "bob_radius_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "gravity": {
              "id": "req_pendulum_gravity",
              "name": "gravity",
              "dimension": "acceleration",
              "required": true,
              "allowed_units": [
                "m/s²",
                "m/s^2",
                "m/s2",
                "cm/s²"
              ],
              "canonical_unit": "m/s²",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_earth_gravity",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "mass": {
              "id": "req_pendulum_mass",
              "name": "mass",
              "dimension": "mass",
              "required": true,
              "allowed_units": [
                "kg",
                "g",
                "kilogram",
                "gram"
              ],
              "canonical_unit": "kg",
              "min_value": 0.0001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_standard_mass",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "damping": {
              "id": "req_pendulum_damping",
              "name": "damping",
              "dimension": "damping",
              "required": true,
              "allowed_units": [
                "1/s",
                "s^-1",
                "s_inv",
                "hz"
              ],
              "canonical_unit": "1/s",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_zero_damping",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "length": {
              "id": "req_pendulum_length",
              "name": "length",
              "dimension": "length",
              "required": true,
              "allowed_units": [
                "m",
                "cm",
                "mm",
                "meter",
                "centimeter"
              ],
              "canonical_unit": "m",
              "min_value": 0.001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "pixels_per_meter": {
              "id": "req_pendulum_pixels_per_meter",
              "name": "pixels_per_meter",
              "dimension": "pixels_per_meter",
              "required": false,
              "allowed_units": [],
              "canonical_unit": "px/m",
              "min_value": 0.01,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
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
          "one_of_requirements": [
            [
              "length",
              "pixels_per_meter"
            ]
          ],
          "allowed_policies": [
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_standard_pendulum_length"
          ],
          "parameter_aliases": {
            "bob_center": "bob_position",
            "length_m": "length",
            "string_length": "string_length_px",
            "length_px": "string_length_px",
            "gravity_m_s2": "gravity",
            "damping_s_inv": "damping",
            "mass_kg": "mass"
          },
          "notes": "Simple planar gravity pendulum running analytical RK4 dynamics."
        },
        "issues": []
      }
    },
    {
      "call": "00441_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
          "domain": "mechanics",
          "subtype": "pendulum",
          "required_entities": [
            "pivot",
            "bob",
            "string"
          ],
          "required_geometry": [
            "pivot",
            "bob_center",
            "string_length_px",
            "bob_radius_px"
          ],
          "parameters": {
            "pivot": {
              "id": "req_pendulum_pivot",
              "name": "pivot",
              "dimension": "point_2d",
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
            "bob_position": {
              "id": "req_pendulum_bob_position",
              "name": "bob_position",
              "dimension": "point_2d",
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
            "string_length_px": {
              "id": "req_pendulum_string_length_px",
              "name": "string_length_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "bob_radius_px": {
              "id": "req_pendulum_bob_radius_px",
              "name": "bob_radius_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "gravity": {
              "id": "req_pendulum_gravity",
              "name": "gravity",
              "dimension": "acceleration",
              "required": true,
              "allowed_units": [
                "m/s²",
                "m/s^2",
                "m/s2",
                "cm/s²"
              ],
              "canonical_unit": "m/s²",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_earth_gravity",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "mass": {
              "id": "req_pendulum_mass",
              "name": "mass",
              "dimension": "mass",
              "required": true,
              "allowed_units": [
                "kg",
                "g",
                "kilogram",
                "gram"
              ],
              "canonical_unit": "kg",
              "min_value": 0.0001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_standard_mass",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "damping": {
              "id": "req_pendulum_damping",
              "name": "damping",
              "dimension": "damping",
              "required": true,
              "allowed_units": [
                "1/s",
                "s^-1",
                "s_inv",
                "hz"
              ],
              "canonical_unit": "1/s",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_zero_damping",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "length": {
              "id": "req_pendulum_length",
              "name": "length",
              "dimension": "length",
              "required": true,
              "allowed_units": [
                "m",
                "cm",
                "mm",
                "meter",
                "centimeter"
              ],
              "canonical_unit": "m",
              "min_value": 0.001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "pixels_per_meter": {
              "id": "req_pendulum_pixels_per_meter",
              "name": "pixels_per_meter",
              "dimension": "pixels_per_meter",
              "required": false,
              "allowed_units": [],
              "canonical_unit": "px/m",
              "min_value": 0.01,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
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
          "one_of_requirements": [
            [
              "length",
              "pixels_per_meter"
            ]
          ],
          "allowed_policies": [
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_standard_pendulum_length"
          ],
          "parameter_aliases": {
            "bob_center": "bob_position",
            "length_m": "length",
            "string_length": "string_length_px",
            "length_px": "string_length_px",
            "gravity_m_s2": "gravity",
            "damping_s_inv": "damping",
            "mass_kg": "mass"
          },
          "notes": "Simple planar gravity pendulum running analytical RK4 dynamics."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "00492_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0,
            "mass": 1.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "mass": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
      "call": "00494_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
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
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
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
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
            "gravity": 9.80665,
            "damping": 0.0,
            "mass": 1.0
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "mass": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "position_source_px": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "position_source_px": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "position_source_px": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
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
          "domain": "mechanics",
          "subtype": "pendulum",
          "required_entities": [
            "pivot",
            "bob",
            "string"
          ],
          "required_geometry": [
            "pivot",
            "bob_center",
            "string_length_px",
            "bob_radius_px"
          ],
          "parameters": {
            "pivot": {
              "id": "req_pendulum_pivot",
              "name": "pivot",
              "dimension": "point_2d",
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
            "bob_position": {
              "id": "req_pendulum_bob_position",
              "name": "bob_position",
              "dimension": "point_2d",
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
            "string_length_px": {
              "id": "req_pendulum_string_length_px",
              "name": "string_length_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "bob_radius_px": {
              "id": "req_pendulum_bob_radius_px",
              "name": "bob_radius_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 1.0,
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
            "gravity": {
              "id": "req_pendulum_gravity",
              "name": "gravity",
              "dimension": "acceleration",
              "required": true,
              "allowed_units": [
                "m/s²",
                "m/s^2",
                "m/s2",
                "cm/s²"
              ],
              "canonical_unit": "m/s²",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_earth_gravity",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "mass": {
              "id": "req_pendulum_mass",
              "name": "mass",
              "dimension": "mass",
              "required": true,
              "allowed_units": [
                "kg",
                "g",
                "kilogram",
                "gram"
              ],
              "canonical_unit": "kg",
              "min_value": 0.0001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_standard_mass",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "damping": {
              "id": "req_pendulum_damping",
              "name": "damping",
              "dimension": "damping",
              "required": true,
              "allowed_units": [
                "1/s",
                "s^-1",
                "s_inv",
                "hz"
              ],
              "canonical_unit": "1/s",
              "min_value": 0.0,
              "max_value": null,
              "allow_zero": true,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_zero_damping",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "length": {
              "id": "req_pendulum_length",
              "name": "length",
              "dimension": "length",
              "required": true,
              "allowed_units": [
                "m",
                "cm",
                "mm",
                "meter",
                "centimeter"
              ],
              "canonical_unit": "m",
              "min_value": 0.001,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": null,
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "pixels_per_meter": {
              "id": "req_pendulum_pixels_per_meter",
              "name": "pixels_per_meter",
              "dimension": "pixels_per_meter",
              "required": false,
              "allowed_units": [],
              "canonical_unit": "px/m",
              "min_value": 0.01,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
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
          "one_of_requirements": [
            [
              "length",
              "pixels_per_meter"
            ]
          ],
          "allowed_policies": [
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_standard_pendulum_length"
          ],
          "parameter_aliases": {
            "bob_center": "bob_position",
            "length_m": "length",
            "string_length": "string_length_px",
            "length_px": "string_length_px",
            "gravity_m_s2": "gravity",
            "damping_s_inv": "damping",
            "mass_kg": "mass"
          },
          "notes": "Simple planar gravity pendulum running analytical RK4 dynamics."
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
    "count": 21,
    "first_8_records": [
      {
        "call": "00384_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "pendulum",
          "blockers": [
            "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
            "Subtype requires 'damping'. No visual/OCR value found. Explicit policy 'Ideal Undamped Oscillation' (0.0 1/s) is available.",
            "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
            "Simulation requires length or pixels_per_meter."
          ],
          "warnings": [],
          "missing_requirements": [
            "mass",
            "damping",
            "length"
          ],
          "satisfied_requirements": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity"
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
        "call": "00386_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00387_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00438_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "pendulum",
          "blockers": [
            "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
            "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
            "Simulation requires length or pixels_per_meter."
          ],
          "warnings": [],
          "missing_requirements": [
            "mass",
            "length"
          ],
          "satisfied_requirements": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity",
            "damping"
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
        "call": "00440_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00441_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00492_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "pendulum",
          "blockers": [
            "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
            "Simulation requires length or pixels_per_meter."
          ],
          "warnings": [],
          "missing_requirements": [
            "length"
          ],
          "satisfied_requirements": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity",
            "mass",
            "damping"
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
        "call": "00494_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": {
    "count": 14,
    "first_8_records": [
      {
        "call": "00386_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00387_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00440_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00441_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00494_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00495_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "calibration": null,
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
        "call": "00549_ResolutionAnalyzer._check_geometry_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
              "parameter_provenance",
              "calibration"
            ]
          }
        }
      },
      {
        "call": "00550_ResolutionAnalyzer._check_parameter_requirements",
        "post_call_locals": {
          "book_ir": {
            "version": "1.0",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "page_ir_version": "1.0",
            "figure_id": "figure_001",
            "domain": "mechanics",
            "subtype": "pendulum",
            "status": "NEEDS_REVIEW",
            "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
            "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
              "parameter_provenance",
              "calibration"
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** The current analyzer checks required entities/parameters and ambiguity. It does not compare every proposed line or point to image pixels.

[Complete stage input/output bundle](stage_data/21_requirements.json)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00384_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00386_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00387_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00438_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00440_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00441_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00492_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00494_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00495_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00547_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00549_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00550_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00592_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00594_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00595_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00655_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00657_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00658_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00732_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00734_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00735_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [Code: ai\resolution\analyzer.py](contracts/ai/resolution/analyzer.py)

## 22. Readiness decision

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Requirement and ambiguity analysis → this component → PhysicsCompiler entry and gate.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00383_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
    "call": "00437_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
    "call": "00491_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
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
    "call": "00546_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
    "call": "00591_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
    "call": "00654_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
    "call": "00731_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
      "mutate_status": false
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
      "call": "00383_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
          "Subtype requires 'damping'. No visual/OCR value found. Explicit policy 'Ideal Undamped Oscillation' (0.0 1/s) is available.",
          "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
          "Simulation requires length or pixels_per_meter."
        ],
        "warnings": [],
        "missing_requirements": [
          "mass",
          "damping",
          "length"
        ],
        "satisfied_requirements": [
          "pivot",
          "bob_position",
          "string_length_px",
          "bob_radius_px",
          "gravity"
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
      "call": "00437_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Subtype requires 'mass'. No visual/OCR value found. Explicit policy 'Standard Unit Mass' (1.0 kg) is available.",
          "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
          "Simulation requires length or pixels_per_meter."
        ],
        "warnings": [],
        "missing_requirements": [
          "mass",
          "length"
        ],
        "satisfied_requirements": [
          "pivot",
          "bob_position",
          "string_length_px",
          "bob_radius_px",
          "gravity",
          "damping"
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
      "call": "00491_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "ready": false,
        "blockers": [
          "Subtype requires 'length'. No visual/OCR value found. Explicit policy 'Standard Pendulum String Length' (1.0 m) is available.",
          "Simulation requires length or pixels_per_meter."
        ],
        "warnings": [],
        "missing_requirements": [
          "length"
        ],
        "satisfied_requirements": [
          "pivot",
          "bob_position",
          "string_length_px",
          "bob_radius_px",
          "gravity",
          "mass",
          "damping"
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
      "call": "00546_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "pivot",
          "bob_position",
          "string_length_px",
          "bob_radius_px",
          "gravity",
          "mass",
          "damping",
          "length"
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
      "call": "00591_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "pivot",
          "bob_position",
          "string_length_px",
          "bob_radius_px",
          "gravity",
          "mass",
          "damping",
          "length"
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
      "call": "00654_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": {
          "count": 9,
          "first_8_records": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity",
            "mass",
            "damping",
            "length"
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
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
      "call": "00731_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": {
          "count": 9,
          "first_8_records": [
            "pivot",
            "bob_position",
            "string_length_px",
            "bob_radius_px",
            "gravity",
            "mass",
            "damping",
            "length"
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** All repeated evaluations are recorded. Use the final pre-compile decision as the gate, while retaining earlier decisions to see state changes.

[Complete stage input/output bundle](stage_data/22_readiness.json)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00383_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00437_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00491_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00546_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00591_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00654_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00731_ReadinessEvaluator.evaluate/STAGE.html)

- [Code: ai\resolution\evaluator.py](contracts/ai/resolution/evaluator.py)

## 23. PhysicsCompiler entry and gate

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** Readiness decision → this component → Canonical scene construction and schema validation.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00697_PhysicsCompiler.compile",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
      "call": "00697_PhysicsCompiler.compile",
      "return_value": {
        "status": "READY",
        "scene": {
          "domain": "mechanics",
          "subtype": "pendulum",
          "source": {
            "type": "book_figure",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "width": 1280.0,
            "height": 960.0,
            "image_width_px": 1280.0,
            "image_height_px": 960.0
          },
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "bob_center": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "string_length_px": 634.61,
            "length_px": 634.61,
            "bob_radius_px": 37.03476174228877
          },
          "parameters": {
            "length": {
              "value": 1.0,
              "unit": "m",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_standard_pendulum_length)",
                "policyId": "policy_standard_pendulum_length",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "gravity": {
              "value": 9.80665,
              "unit": "m/s²",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_earth_gravity)",
                "policyId": "policy_earth_gravity",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "initialAngle": {
              "value": 26.117406100584446,
              "unit": "°",
              "provenance": "observed"
            },
            "mass": {
              "value": 1.0,
              "unit": "kg",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_standard_mass)",
                "policyId": "policy_standard_mass",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "damping": {
              "value": 0.0,
              "unit": "1/s",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_zero_damping)",
                "policyId": "policy_zero_damping",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            }
          },
          "assumptions": [
            {
              "parameter": "gravity",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "value": 9.80665,
              "unit": "m/s²",
              "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "damping",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "value": 0.0,
              "unit": "1/s",
              "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "mass",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "kg",
              "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "length",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "m",
              "reason": "Standard 1.0 m simple pendulum string length.",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "_other_fields_in_complete_snapshot": [
            "schemaVersion",
            "id",
            "coordinateSpace",
            "coordinateSystem",
            "objects",
            "render",
            "environment"
          ]
        },
        "issues": [],
        "book_ir_status": "READY_TO_COMPILE"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A typed failure with scene=null when not ready, or a canonical PhysicsScene with source identity, units and provenance. Never manufacture an executable scene from a blocked case.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

**Changes, provenance and possible information loss:** The active compiler implementation is ai/ingestion/PhysicsCompiler.py. The scene_compiler module re-exports it.

[Complete stage input/output bundle](stage_data/23_gate.json)

- [PhysicsCompiler.compile — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00697_PhysicsCompiler.compile/STAGE.html)

- [Code: ai\ingestion\PhysicsCompiler.py](contracts/ai/ingestion/PhysicsCompiler.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00697_PhysicsCompiler.compile/actual_overlay_on_source.png)

## 24. Canonical scene construction and schema validation

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** PhysicsCompiler entry and gate → this component → API response delivered to the browser.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00774_PhysicsCompiler._build_canonical_scene",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
      "domain": "mechanics",
      "subtype": "pendulum"
    }
  },
  {
    "call": "00782_PhysicsCompiler._populate_canonical_pendulum",
    "value": {
      "scene": {
        "schemaVersion": "1.0",
        "id": "PHY-MECH-figure_001",
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0
        },
        "coordinateSpace": {
          "type": "source_px",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0,
          "unit": "px"
        },
        "coordinateSystem": {
          "type": "source_px",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0,
          "unit": "px"
        },
        "parameters": {},
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "objects": [],
        "render": {
          "coordinate_space": "source_px"
        }
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
    "call": "00806_PhysicsCompiler._preserve_parameter_provenance",
    "value": {
      "scene": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877
        },
        "parameters": {
          "length": {
            "value": 1.0,
            "unit": "m",
            "provenance": "observed"
          },
          "gravity": {
            "value": 9.80665,
            "unit": "m/s²",
            "provenance": "assumed"
          },
          "initialAngle": {
            "value": 26.117406100584446,
            "unit": "°",
            "provenance": "observed"
          },
          "mass": {
            "value": 1.0,
            "unit": "kg",
            "provenance": "assumed"
          },
          "damping": {
            "value": 0.0,
            "unit": "1/s",
            "provenance": "assumed"
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment"
        ]
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px"
        },
        "parameters": {
          "bob_radius_px": {
            "value": 37.03476174228877,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
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
          "bob_position": {
            "x": 841.3633806409911,
            "y": 649.0514992664916,
            "provenance": {
              "source": "cv_sam_fused",
              "confidence": 0.95,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "string_length_px": {
            "value": 634.61,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.92,
              "notes": "Derived from verified pivot and bob center.",
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
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072,
            "provenance": {
              "source": "cv",
              "confidence": 0.92,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs"
              ]
            }
          },
          "visual_angle_deg": {
            "value": 26.12,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "derived",
              "confidence": 0.88,
              "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
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
          "gravity": 9.80665,
          "damping": 0.0,
          "mass": 1.0,
          "length": 1.0,
          "pixels_per_meter": 634.61
        },
        "resolutions": {
          "gravity": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "damping": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "mass": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          },
          "length": {
            "source": "policy_default",
            "_other_fields_in_complete_snapshot": [
              "id",
              "requirementId",
              "parameterName",
              "value",
              "resolvedValue",
              "unit",
              "canonicalUnit",
              "rawInput",
              "originalEnteredValue",
              "resolutionSource",
              "policyId",
              "policyVersion",
              "supersededValue",
              "evidenceRefs",
              "timestamp",
              "notes",
              "userAccepted",
              "resolvedBy"
            ]
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "pivot_1",
            "type": "pivot",
            "label": "pivot",
            "position_source_px": {
              "x": 562.0,
              "y": 79.23811193908072,
              "coordinate_space": "source_px",
              "method": "vertical_reference_intersection"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          },
          {
            "id": "bob_1",
            "type": "bob",
            "label": "m",
            "position_source_px": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "coordinate_space": "source_px",
              "method": "fused_cv_sam",
              "center_agreement_distance_px": 1.23
            },
            "geometry": {
              "bounds": {
                "x": 804.3286188987023,
                "y": 612.0167375242029,
                "width": 74.06952348457754,
                "height": 74.06952348457754
              },
              "radius_px": 37.03476174228877,
              "mask_ref": "mask_bob_53389",
              "area_px": 4625.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_seg_bob_mask_bob_53389",
              "ev_ocr_ocr_tok_002"
            ]
          },
          {
            "id": "string_1",
            "type": "string",
            "label": "L",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 79.23811193908072
              },
              "end": {
                "x": 841.3633806409911,
                "y": 649.0514992664916
              },
              "length_px": 634.61,
              "visible_string_start": {
                "x": 556.0,
                "y": 67.0
              },
              "visible_string_end": {
                "x": 830.0,
                "y": 617.0
              },
              "visible_length_px": 614.47,
              "effective_length_px": 634.61,
              "attachment_point": {
                "x": 824.8323943921771,
                "y": 615.910888666359
              },
              "_nested_fields_in_complete_snapshot": [
                "effective_pendulum",
                "visible_string"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
              "ev_ocr_ocr_tok_001"
            ]
          },
          {
            "id": "ref_1",
            "type": "vertical_reference",
            "label": "vertical_line",
            "position_source_px": {
              "x": 562.0,
              "y": 61.0,
              "coordinate_space": "source_px",
              "method": "line_detection"
            },
            "geometry": {
              "start": {
                "x": 562.0,
                "y": 61.0
              },
              "end": {
                "x": 562.0,
                "y": 774.0
              },
              "length_px": 713.0,
              "style": "dashed",
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
            ]
          }
        ],
        "relationships": [
          {
            "type": "connected_to",
            "from": "bob_1",
            "to": "string_1",
            "confidence": 0.95
          },
          {
            "type": "connected_to",
            "from": "string_1",
            "to": "pivot_1",
            "confidence": 0.95
          }
        ],
        "calibration": {
          "pixels_per_meter": 634.61,
          "meters_per_pixel": 0.0015757709459352988,
          "reference_pixel_span": 634.61,
          "reference_physical_m": 1.0,
          "reference_parameter": "length",
          "provenance": {
            "source": "derived_calibration",
            "evidence_refs": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ],
            "confidence": 0.99,
            "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "string_1",
              "auto_policy_standard_pendulum_length"
            ]
          },
          "pixels_per_meter_x": 634.61,
          "pixels_per_meter_y": 634.61
        },
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
      "subtype": "pendulum"
    }
  },
  {
    "call": "00807_validate_canonical_scene",
    "value": {
      "scene": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877
        },
        "parameters": {
          "length": {
            "value": 1.0,
            "unit": "m",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_standard_pendulum_length)",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "gravity": {
            "value": 9.80665,
            "unit": "m/s²",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_earth_gravity)",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "initialAngle": {
            "value": 26.117406100584446,
            "unit": "°",
            "provenance": "observed"
          },
          "mass": {
            "value": 1.0,
            "unit": "kg",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_standard_mass)",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "damping": {
            "value": 0.0,
            "unit": "1/s",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_zero_damping)",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment"
        ]
      }
    }
  }
]
```

**What it should receive — expected input:** Validated BookIR and an initially empty canonical scene structure.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00774_PhysicsCompiler._build_canonical_scene",
      "return_value": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280.0,
          "height": 960.0,
          "image_width_px": 1280.0,
          "image_height_px": 960.0
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562.0,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877
        },
        "parameters": {
          "length": {
            "value": 1.0,
            "unit": "m",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [],
              "derivedFrom": [],
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_standard_pendulum_length)",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "gravity": {
            "value": 9.80665,
            "unit": "m/s²",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [],
              "derivedFrom": [],
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_earth_gravity)",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "initialAngle": {
            "value": 26.117406100584446,
            "unit": "°",
            "provenance": "observed"
          },
          "mass": {
            "value": 1.0,
            "unit": "kg",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [],
              "derivedFrom": [],
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_standard_mass)",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "damping": {
            "value": 0.0,
            "unit": "1/s",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [],
              "derivedFrom": [],
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_zero_damping)",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          }
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment"
        ]
      }
    },
    {
      "call": "00782_PhysicsCompiler._populate_canonical_pendulum",
      "return_value": null
    },
    {
      "call": "00806_PhysicsCompiler._preserve_parameter_provenance",
      "return_value": null
    },
    {
      "call": "00807_validate_canonical_scene",
      "return_value": []
    }
  ],
  "in_place_outputs": [
    {
      "call": "00782_PhysicsCompiler._populate_canonical_pendulum",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-MECH-figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render",
            "environment"
          ]
        },
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "READY_TO_COMPILE",
          "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
          "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
            "parameter_provenance",
            "calibration"
          ]
        }
      }
    },
    {
      "call": "00806_PhysicsCompiler._preserve_parameter_provenance",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-MECH-figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render",
            "environment"
          ]
        },
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "READY_TO_COMPILE",
          "status_notes": "Visual evidence extracted; ready for compiler parameter verification.",
          "id": "25c3ba19a02041ee9ec790156fc87e44_figure_001",
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
            "parameter_provenance",
            "calibration"
          ]
        }
      }
    }
  ]
}
```

**What it should provide — implemented contract:** Domain scene objects, parameters and geometry that preserve evidence/provenance and source frame. If model geometry is reconstructed, distinguish it from observed geometry.

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

**Changes, provenance and possible information loss:** Populate methods mutate scene in place and return None. Their real output is locals_after.scene and the enclosing compile result. None is not a failed scene.

[Complete stage input/output bundle](stage_data/24_compile.json)

- [PhysicsCompiler._build_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00774_PhysicsCompiler._build_canonical_scene/STAGE.html)

- [PhysicsCompiler._populate_canonical_pendulum — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00782_PhysicsCompiler._populate_canonical_pendulum/STAGE.html)

- [PhysicsCompiler._preserve_parameter_provenance — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00806_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- [validate_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00807_validate_canonical_scene/STAGE.html)

- [Code: ai\ingestion\PhysicsCompiler.py](contracts/ai/ingestion/PhysicsCompiler.py)

## 25. API response delivered to the browser

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

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
        "domain": "mechanics",
        "status": "ready",
        "scene": {
          "domain": "mechanics",
          "subtype": "pendulum",
          "source": {
            "type": "book_figure",
            "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
            "figure_id": "figure_001",
            "width": 1280.0,
            "height": 960.0,
            "image_width_px": 1280.0,
            "image_height_px": 960.0
          },
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072
            },
            "bob_center": {
              "x": 841.3633806409911,
              "y": 649.0514992664916
            },
            "string_length_px": 634.61,
            "length_px": 634.61,
            "bob_radius_px": 37.03476174228877
          },
          "parameters": {
            "length": {
              "value": 1.0,
              "unit": "m",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_standard_pendulum_length)",
                "policyId": "policy_standard_pendulum_length",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "gravity": {
              "value": 9.80665,
              "unit": "m/s²",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_earth_gravity)",
                "policyId": "policy_earth_gravity",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "initialAngle": {
              "value": 26.117406100584446,
              "unit": "°",
              "provenance": "observed"
            },
            "mass": {
              "value": 1.0,
              "unit": "kg",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_standard_mass)",
                "policyId": "policy_standard_mass",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "damping": {
              "value": 0.0,
              "unit": "1/s",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_zero_damping)",
                "policyId": "policy_zero_damping",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            }
          },
          "assumptions": [
            {
              "parameter": "gravity",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "value": 9.80665,
              "unit": "m/s²",
              "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "damping",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "value": 0.0,
              "unit": "1/s",
              "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "mass",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "kg",
              "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "length",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "m",
              "reason": "Standard 1.0 m simple pendulum string length.",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "_other_fields_in_complete_snapshot": [
            "schemaVersion",
            "id",
            "coordinateSpace",
            "coordinateSystem",
            "objects",
            "render",
            "environment"
          ]
        },
        "book_ir": {
          "isPhysics": true,
          "domain": "mechanics",
          "subtype": "pendulum",
          "status": "READY_TO_COMPILE",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px"
          },
          "parameters": {
            "bob_radius_px": {
              "value": 37.03476174228877,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "bob_position": {
              "x": 841.3633806409911,
              "y": 649.0514992664916,
              "provenance": {
                "source": "cv_sam_fused",
                "confidence": 0.95,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "string_length_px": {
              "value": 634.61,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.92,
                "notes": "Derived from verified pivot and bob center.",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "pivot": {
              "x": 562.0,
              "y": 79.23811193908072,
              "provenance": {
                "source": "cv",
                "confidence": 0.92,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs"
                ]
              }
            },
            "visual_angle_deg": {
              "value": 26.12,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "derived",
                "confidence": 0.88,
                "notes": "Derived geometrically from pivot-to-bob vector relative to downward vertical.",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "gravity": 9.80665,
            "damping": 0.0,
            "mass": 1.0,
            "length": 1.0,
            "pixels_per_meter": 634.61
          },
          "resolutions": {
            "gravity": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "damping": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "mass": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            },
            "length": {
              "source": "policy_default",
              "_other_fields_in_complete_snapshot": [
                "id",
                "requirementId",
                "parameterName",
                "value",
                "resolvedValue",
                "unit",
                "canonicalUnit",
                "rawInput",
                "originalEnteredValue",
                "resolutionSource",
                "policyId",
                "policyVersion",
                "supersededValue",
                "evidenceRefs",
                "timestamp",
                "notes",
                "userAccepted",
                "resolvedBy"
              ]
            }
          },
          "assumptions": [
            {
              "parameter": "gravity",
              "policyId": "policy_earth_gravity",
              "policyVersion": "1.0",
              "value": 9.80665,
              "unit": "m/s²",
              "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "damping",
              "policyId": "policy_zero_damping",
              "policyVersion": "1.0",
              "value": 0.0,
              "unit": "1/s",
              "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "mass",
              "policyId": "policy_standard_mass",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "kg",
              "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
              "provenance": "auto_policy",
              "confidence": 0.8
            },
            {
              "parameter": "length",
              "policyId": "policy_standard_pendulum_length",
              "policyVersion": "1.0",
              "value": 1.0,
              "unit": "m",
              "reason": "Standard 1.0 m simple pendulum string length.",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "pivot_1",
              "type": "pivot",
              "label": "pivot",
              "positionSourcePx": {
                "x": 562.0,
                "y": 79.23811193908072,
                "coordinate_space": "source_px",
                "method": "vertical_reference_intersection"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            },
            {
              "id": "bob_1",
              "type": "bob",
              "label": "m",
              "positionSourcePx": {
                "x": 841.3633806409911,
                "y": 649.0514992664916,
                "coordinate_space": "source_px",
                "method": "fused_cv_sam",
                "center_agreement_distance_px": 1.23
              },
              "geometry": {
                "bounds": {
                  "x": 804.3286188987023,
                  "y": 612.0167375242029,
                  "width": 74.06952348457754,
                  "height": 74.06952348457754
                },
                "radius_px": 37.03476174228877,
                "mask_ref": "mask_bob_53389",
                "area_px": 4625.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_seg_bob_mask_bob_53389",
                "ev_ocr_ocr_tok_002"
              ]
            },
            {
              "id": "string_1",
              "type": "string",
              "label": "L",
              "positionSourcePx": null,
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 79.23811193908072
                },
                "end": {
                  "x": 841.3633806409911,
                  "y": 649.0514992664916
                },
                "length_px": 634.61,
                "visible_string_start": {
                  "x": 556.0,
                  "y": 67.0
                },
                "visible_string_end": {
                  "x": 830.0,
                  "y": 617.0
                },
                "visible_length_px": 614.47,
                "effective_length_px": 634.61,
                "attachment_point": {
                  "x": 824.8323943921771,
                  "y": 615.910888666359
                },
                "_nested_fields_in_complete_snapshot": [
                  "effective_pendulum",
                  "visible_string"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44",
                "ev_ocr_ocr_tok_001"
              ]
            },
            {
              "id": "ref_1",
              "type": "vertical_reference",
              "label": "vertical_line",
              "positionSourcePx": {
                "x": 562.0,
                "y": 61.0,
                "coordinate_space": "source_px",
                "method": "line_detection"
              },
              "geometry": {
                "start": {
                  "x": 562.0,
                  "y": 61.0
                },
                "end": {
                  "x": 562.0,
                  "y": 774.0
                },
                "length_px": 713.0,
                "style": "dashed",
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_pendulum_25c3ba19a02041ee9ec790156fc87e44"
              ]
            }
          ],
          "relationships": [
            {
              "type": "connected_to",
              "from": "bob_1",
              "to": "string_1",
              "confidence": 0.95
            },
            {
              "type": "connected_to",
              "from": "string_1",
              "to": "pivot_1",
              "confidence": 0.95
            }
          ],
          "calibration": {
            "pixels_per_meter": 634.61,
            "meters_per_pixel": 0.0015757709459352988,
            "reference_pixel_span": 634.61,
            "reference_physical_m": 1.0,
            "reference_parameter": "length",
            "provenance": {
              "source": "derived_calibration",
              "evidenceRefs": [
                "string_1",
                "auto_policy_standard_pendulum_length"
              ],
              "derivedFrom": [
                "string_1",
                "auto_policy_standard_pendulum_length"
              ],
              "confidence": 0.99,
              "notes": "Derived scale: 634.61 px/m (x: 634.61, y: 634.61) from 634.6 px = 1.0 m (length)"
            },
            "pixels_per_meter_x": 634.61,
            "pixels_per_meter_y": 634.61
          },
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
          "id": "25c3ba19a02041ee9ec790156fc87e44",
          "mimeType": "image/jpeg",
          "originalFilename": "photo_2026-10-10_12-06-38 (2).jpg",
          "byteSize": 35941,
          "width_px": 1280,
          "height_px": 960,
          "sha256": "b5341f3eb014fc45df72b93b37fefc2de5adee3e4db4e11ec3949bc9475a78fd"
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0.0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1.0,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
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

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

**Changes, provenance and possible information loss:** This is the handler return, after nested work. Exact HTTP status/body are retained separately from the Python object.

[Complete stage input/output bundle](stage_data/25_response.json)

- [ingest_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- [HTTP response 1792207721065423100_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/http/1792207721065423100_response_body.json)

- [Code: apps\api\main.py](contracts/apps/api/main.py)

## 26. Frontend receives result and selects next state

**Execution:** EXECUTED. **Verdict:** SCENE ACCEPTED.

**Upstream → downstream:** API response delivered to the browser → this component → Review / explicit compile request branch.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 3076.5,
    "data": [
      "UPLOADING"
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 40542.90000000596,
    "data": [
      "ANALYZING"
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._normalizeSceneBackground",
    "phase": "input",
    "wallTime": 40544.80000001192,
    "data": [
      {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment"
        ]
      }
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 40546,
    "data": [
      "READY_TO_SIMULATE"
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 40886.70000001788,
    "data": [
      "SIMULATING"
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
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 3076.9000000059605,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 40542.90000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._normalizeSceneBackground",
      "phase": "output",
      "wallTime": 40545.80000001192,
      "data": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 40546,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 40886.80000001192,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "final_orchestrator_state": "SIMULATING",
      "currentError": null
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Preserved source URL/frame and readiness-governed state. Needs-review cases should expose review issues without falsely activating an uploaded simulation.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

**Changes, provenance and possible information loss:** Only events after startWithFile for this trace are used here. Startup/demo events remain in the raw log but are excluded from this diagram’s runtime evidence.

[Complete stage input/output bundle](stage_data/26_orchestrator.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 27. Review / explicit compile request branch

**Execution:** NOT EXECUTED. **Verdict:** NOT EXECUTED.

**Upstream → downstream:** Frontend receives result and selects next state → this component → InteractiveFigure receives the compiled scene.

**What it receives — actual input (selected recorded fields):**

```json
[]
```

**What it should receive — expected input:** A needs-review BookIR and subsequent actual browser review/compile requests, if any.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Review should list blockers; compile must reject unresolved evidence and keep scene=null. No synthetic user corrections are supplied in this trace.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/27_review.json)

- [HTTP response 1792207721065423100_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/http/1792207721065423100_response_body.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 28. InteractiveFigure receives the compiled scene

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** Review / explicit compile request branch → this component → FigureViewport background and layout.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "InteractiveFigure.load",
    "phase": "input",
    "wallTime": 40551.30000001192,
    "data": [
      {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      }
    ]
  }
]
```

**What it should receive — expected input:** The source-matched canonical scene approved by the backend.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "InteractiveFigure.load",
      "phase": "output",
      "wallTime": 40870.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A figure bound to the original image, with the correct domain runtime and an initial rendered output. No unrelated demo geometry.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** load performs layout/runtime initialization internally. The t0 event immediately after load is an observed snapshot; exact child JS calls were not all instrumented.

[Complete stage input/output bundle](stage_data/28_figure.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

## 29. FigureViewport background and layout

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** InteractiveFigure receives the compiled scene → this component → PhysicsRuntime normalization and adapter initialization.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "FigureViewport.setBackground",
    "phase": "input",
    "wallTime": 40552,
    "data": [
      "/uploads/diagram_25c3ba19.jpg",
      1280,
      960
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "FigureViewport.recalculate",
    "phase": "input",
    "wallTime": 40694.40000000596,
    "data": []
  }
]
```

**What it should receive — expected input:** Original source URL, natural width/height and measured viewport bounds.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "FigureViewport.recalculate",
      "phase": "output",
      "wallTime": 40830.09999999404,
      "data": {
        "sourceWidth": 1280,
        "sourceHeight": 960,
        "displayWidth": 640,
        "displayHeight": 480,
        "viewportWidth": 1010,
        "viewportHeight": 480,
        "scale": 0.5,
        "offsetX": 185,
        "offsetY": 0,
        "dpr": 1,
        "renderedImageRect": {
          "left": 185,
          "top": 0,
          "width": 640,
          "height": 480
        }
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "FigureViewport.setBackground",
      "phase": "output",
      "wallTime": 40830.20000001788,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "measured_image_rect": {
        "x": 219,
        "y": 227,
        "width": 640,
        "height": 480,
        "top": 227,
        "right": 859,
        "bottom": 707,
        "left": 219
      },
      "mapper": {
        "sourceW": 1280,
        "sourceH": 960,
        "viewW": 1010,
        "viewH": 480,
        "dpr": 1,
        "scale": 0.5,
        "renderedW": 640,
        "renderedH": 480,
        "offsetX": 185,
        "offsetY": 0
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The source image displayed with an aspect-preserving transform shared by its overlay. Letterboxing belongs to the viewport, not to native geometry.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Preserve source_px. The measured image rectangle and mapper offsets are shown in the coordinate stage; CSS pixels are not substituted into BookIR.

[Complete stage input/output bundle](stage_data/29_background.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\FigureViewport.js](contracts/apps/web/src/components/FigureViewport.js)

## 30. PhysicsRuntime normalization and adapter initialization

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** FigureViewport background and layout → this component → Domain solver and actual initial state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.load",
    "phase": "input",
    "wallTime": 40832.70000001788,
    "data": [
      {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      },
      {
        "tag": "DIV"
      },
      {
        "viewport": {
          "sourceW": 1280,
          "sourceH": 960,
          "imageUrl": "/uploads/diagram_25c3ba19.jpg",
          "showInspectAnchors": false,
          "_nested_fields_in_complete_snapshot": [
            "host",
            "mapper",
            "listeners",
            "calibrationAnchors",
            "_dom",
            "_resizeObserver"
          ]
        },
        "renderContext": {
          "sourceWidth": 1280,
          "sourceHeight": 960,
          "displayWidth": 640,
          "displayHeight": 480,
          "viewportWidth": 1010,
          "viewportHeight": 480,
          "scale": 0.5,
          "offsetX": 185,
          "offsetY": 0,
          "dpr": 1,
          "_nested_fields_in_complete_snapshot": [
            "renderedImageRect"
          ]
        }
      }
    ]
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.normalizeScene",
    "phase": "input",
    "wallTime": 40839.59999999404,
    "data": [
      {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      }
    ]
  }
]
```

**What it should receive — expected input:** Source-matched scene and figure/container options.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.normalizeScene",
      "phase": "output",
      "wallTime": 40840.09999999404,
      "data": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.load",
      "phase": "output",
      "wallTime": 40869.40000000596,
      "data": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "time": 0,
        "state": {
          "domain": "mechanics",
          "type": "pendulum",
          "subtype": "pendulum",
          "running": false,
          "time": 0,
          "thetaDeg": 26.1,
          "thetaRad": 0.4558,
          "omega": 0,
          "speed": 0,
          "length": 1,
          "gravity": 9.81,
          "potentialEnergy": 1,
          "kineticEnergy": 0,
          "totalEnergy": 1,
          "calibrated": true
        },
        "geometry": {
          "thetaRad": 0.45553093477052004,
          "lengthM": 1,
          "xM": 0,
          "yM": 0
        },
        "telemetry": {
          "domain": "mechanics",
          "type": "pendulum",
          "subtype": "pendulum",
          "running": false,
          "time": 0,
          "thetaDeg": 26.1,
          "thetaRad": 0.4558,
          "omega": 0,
          "speed": 0,
          "length": 1,
          "gravity": 9.81,
          "potentialEnergy": 1,
          "kineticEnergy": 0,
          "totalEnergy": 1,
          "calibrated": true
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "initialAngle"
          ]
        }
      }
    },
    {
      "actual_runtime_after_load": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-MECH-figure_001",
          "domain": "mechanics",
          "subtype": "pendulum",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render",
            "environment",
            "visual"
          ]
        },
        "output": {
          "domain": "mechanics",
          "subtype": "pendulum",
          "time": 0,
          "_nested_fields_in_complete_snapshot": [
            "state",
            "geometry",
            "telemetry",
            "events",
            "editableParameters"
          ]
        },
        "state": {
          "domain": "mechanics",
          "type": "pendulum",
          "subtype": "pendulum",
          "running": false,
          "time": 0,
          "thetaDeg": 26.1,
          "thetaRad": 0.4558,
          "omega": 0,
          "speed": 0,
          "length": 1,
          "gravity": 9.81,
          "potentialEnergy": 1,
          "kineticEnergy": 0,
          "totalEnergy": 1,
          "calibrated": true
        },
        "mapper": {
          "sourceW": 1280,
          "sourceH": 960,
          "viewW": 1010,
          "viewH": 480,
          "dpr": 1,
          "scale": 0.5,
          "renderedW": 640,
          "renderedH": 480,
          "offsetX": 185,
          "offsetY": 0
        },
        "sourceW": 1280,
        "sourceH": 960
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Validated normalized scene, resolved capabilities, matching adapter and initialized runtime. Normalization must not erase provenance or relocate source points.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Registry/capability/adapter child calls are established by runtime source and captured boundary/output. Their independent entry/exit arguments were not recorded; they are not presented as new trace snapshots.

[Complete stage input/output bundle](stage_data/30_runtime.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: engine\core\PhysicsRuntime.js](contracts/engine/core/PhysicsRuntime.js)

## 31. Domain solver and actual initial state

**Execution:** EXECUTED. **Verdict:** OUTPUT OBSERVED; NO NUMERICAL DEFECT PROVEN.

**Upstream → downstream:** PhysicsRuntime normalization and adapter initialization → this component → CoordinateMapper: source → overlay → browser.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "scene_used_by_runtime": {
      "domain": "mechanics",
      "subtype": "pendulum",
      "source": {
        "type": "book_figure",
        "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
        "figure_id": "figure_001",
        "width": 1280,
        "height": 960,
        "image_width_px": 1280,
        "image_height_px": 960,
        "image": "/uploads/diagram_25c3ba19.jpg"
      },
      "geometry": {
        "width": 1280,
        "height": 960,
        "coordinate_space": "source_px",
        "pivot": {
          "x": 562,
          "y": 79.23811193908072
        },
        "bob_center": {
          "x": 841.3633806409911,
          "y": 649.0514992664916
        },
        "string_length_px": 634.61,
        "length_px": 634.61,
        "bob_radius_px": 37.03476174228877
      },
      "parameters": {
        "length": {
          "value": 1,
          "unit": "m",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "gravity": {
          "value": 9.80665,
          "unit": "m/s²",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "initialAngle": {
          "value": 26.117406100584446,
          "unit": "°",
          "provenance": "observed"
        },
        "mass": {
          "value": 1,
          "unit": "kg",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "damping": {
          "value": 0,
          "unit": "1/s",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        }
      },
      "assumptions": [
        {
          "parameter": "gravity",
          "policyId": "policy_earth_gravity",
          "policyVersion": "1.0",
          "value": 9.80665,
          "unit": "m/s²",
          "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
          "provenance": "auto_policy",
          "confidence": 0.8
        },
        {
          "parameter": "damping",
          "policyId": "policy_zero_damping",
          "policyVersion": "1.0",
          "value": 0,
          "unit": "1/s",
          "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
          "provenance": "auto_policy",
          "confidence": 0.8
        },
        {
          "parameter": "mass",
          "policyId": "policy_standard_mass",
          "policyVersion": "1.0",
          "value": 1,
          "unit": "kg",
          "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
          "provenance": "auto_policy",
          "confidence": 0.8
        },
        {
          "parameter": "length",
          "policyId": "policy_standard_pendulum_length",
          "policyVersion": "1.0",
          "value": 1,
          "unit": "m",
          "reason": "Standard 1.0 m simple pendulum string length.",
          "provenance": "auto_policy",
          "confidence": 0.8
        }
      ],
      "_other_fields_in_complete_snapshot": [
        "schemaVersion",
        "id",
        "coordinateSpace",
        "coordinateSystem",
        "objects",
        "render",
        "environment",
        "visual"
      ]
    }
  }
]
```

**What it should receive — expected input:** The actual scene-derived model parameters, source geometry and any explicit policy values.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "state": {
        "domain": "mechanics",
        "type": "pendulum",
        "subtype": "pendulum",
        "running": false,
        "time": 0,
        "thetaDeg": 26.1,
        "thetaRad": 0.4558,
        "omega": 0,
        "speed": 0,
        "length": 1,
        "gravity": 9.81,
        "potentialEnergy": 1,
        "kineticEnergy": 0,
        "totalEnergy": 1,
        "calibrated": true
      },
      "output": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "time": 0,
        "state": {
          "domain": "mechanics",
          "type": "pendulum",
          "subtype": "pendulum",
          "running": false,
          "time": 0,
          "thetaDeg": 26.1,
          "thetaRad": 0.4558,
          "omega": 0,
          "speed": 0,
          "length": 1,
          "gravity": 9.81,
          "potentialEnergy": 1,
          "kineticEnergy": 0,
          "totalEnergy": 1,
          "calibrated": true
        },
        "geometry": {
          "thetaRad": 0.45553093477052004,
          "lengthM": 1,
          "xM": 0,
          "yM": 0
        },
        "telemetry": {
          "domain": "mechanics",
          "type": "pendulum",
          "subtype": "pendulum",
          "running": false,
          "time": 0,
          "thetaDeg": 26.1,
          "thetaRad": 0.4558,
          "omega": 0,
          "speed": 0,
          "length": 1,
          "gravity": 9.81,
          "potentialEnergy": 1,
          "kineticEnergy": 0,
          "totalEnergy": 1,
          "calibrated": true
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "initialAngle"
          ]
        }
      },
      "mechanics_internal_capture": {
        "geometry": {
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_radius_px": 37.03476174228877,
          "string_length_px": 634.61,
          "length_px": 634.61,
          "_nested_fields_in_complete_snapshot": []
        },
        "theta": 0.45583472853565193,
        "bobSource": {
          "x": 841.3629149366802,
          "y": 649.0505493762439
        },
        "mapper": {
          "scale": 0.5,
          "scaleX": 0.5,
          "scaleY": 0.5,
          "offsetX": 0,
          "offsetY": 0,
          "sourceW": 1280,
          "sourceH": 960,
          "viewW": 640,
          "viewH": 480,
          "_nested_fields_in_complete_snapshot": [
            "sourceToView",
            "viewToSource",
            "sourceLengthToView",
            "viewLengthToSource"
          ]
        },
        "kernel": {
          "lengthM": 1,
          "g": 9.80665,
          "theta0": 0.45583472853565193,
          "omega0": 0,
          "massKg": 1,
          "damping": 0,
          "theta": 0.45583472853565193,
          "omega": 0,
          "simTime": 0,
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "stringLengthPx": 634.61,
          "bobRadiusPx": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Mathematically consistent state/output for those inputs. Correct computation is separate from whether those inputs reconstruct this diagram.

**What correct handling of THIS diagram requires:** At t=0 pivot and bob should register to their printed locations. Motion should pivot around that fixed point. No exact period can be asserted from the symbolic source alone.

**Comparison / debugging conclusion:** MechanicsAdapter → PendulumKernel / PendulumSimulation. t=0 bob is source-aligned while pivot is above the printed support. No integration defect is established; physical time-scale accuracy has no numeric source ground truth.

**Changes, provenance and possible information loss:** Scene/state/output are actual captures. Exact internal solver-call argument objects were not individually intercepted; no replay or hand-computed replacement is labeled as runtime evidence.

[Complete stage input/output bundle](stage_data/31_solver.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: engine\mechanics\MechanicsAdapter.js](contracts/engine/mechanics/MechanicsAdapter.js)

## 32. CoordinateMapper: source → overlay → browser

**Execution:** EXECUTED. **Verdict:** MAPPING PASS FOR CAPTURED LANDMARKS.

**Upstream → downstream:** Domain solver and actual initial state → this component → Actual renderer at t=0 over the original.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "mapper": {
      "sourceW": 1280,
      "sourceH": 960,
      "viewW": 1010,
      "viewH": 480,
      "dpr": 1,
      "scale": 0.5,
      "renderedW": 640,
      "renderedH": 480,
      "offsetX": 185,
      "offsetY": 0
    },
    "image_rect": {
      "x": 219,
      "y": 227,
      "width": 640,
      "height": 480,
      "top": 227,
      "right": 859,
      "bottom": 707,
      "left": 219
    },
    "browser": {
      "devicePixelRatio": 1,
      "innerWidth": 1418,
      "innerHeight": 1002,
      "outerWidth": 1440,
      "outerHeight": 1100,
      "scrollX": 0,
      "scrollY": 0,
      "visualViewport": {
        "width": 1418,
        "height": 1002,
        "scale": 1,
        "offsetLeft": 0,
        "offsetTop": 0
      }
    }
  }
]
```

**What it should receive — expected input:** Native source coordinates, source dimensions, viewport dimensions, DPR and image rectangle.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "landmarks": [
        {
          "label": "scene.geometry.pivot",
          "source": {
            "x": 562,
            "y": 79.23811193908072
          },
          "view": {
            "x": 466,
            "y": 39.61905596954036
          },
          "overlay": {
            "x": 281,
            "y": 39.61905596954036
          },
          "inverse": {
            "x": 562,
            "y": 79.23811193908072
          },
          "browser": {
            "x": 500,
            "y": 266.61905596954034
          },
          "_nested_fields_in_complete_snapshot": []
        },
        {
          "label": "scene.geometry.bob_center",
          "source": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "view": {
            "x": 605.6816903204956,
            "y": 324.5257496332458
          },
          "overlay": {
            "x": 420.68169032049553,
            "y": 324.5257496332458
          },
          "inverse": {
            "x": 841.3633806409912,
            "y": 649.0514992664916
          },
          "browser": {
            "x": 639.6816903204956,
            "y": 551.5257496332458
          },
          "_nested_fields_in_complete_snapshot": []
        },
        {
          "label": "sim.geometry.pivot",
          "source": {
            "x": 562,
            "y": 79.23811193908072
          },
          "view": {
            "x": 466,
            "y": 39.61905596954036
          },
          "overlay": {
            "x": 281,
            "y": 39.61905596954036
          },
          "inverse": {
            "x": 562,
            "y": 79.23811193908072
          },
          "browser": {
            "x": 500,
            "y": 266.61905596954034
          },
          "_nested_fields_in_complete_snapshot": []
        },
        {
          "label": "sim.getBobSourcePosition()",
          "source": {
            "x": 841.3629149366802,
            "y": 649.0505493762439
          },
          "view": {
            "x": 605.6814574683401,
            "y": 324.52527468812195
          },
          "overlay": {
            "x": 420.6814574683401,
            "y": 324.52527468812195
          },
          "inverse": {
            "x": 841.3629149366802,
            "y": 649.0505493762439
          },
          "browser": {
            "x": 639.6814574683401,
            "y": 551.525274688122
          },
          "_nested_fields_in_complete_snapshot": []
        }
      ],
      "DOM_elements": [
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
          "src": "http://127.0.0.1:5173/uploads/diagram_25c3ba19.jpg",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 640,
          "height": 480,
          "viewBox": null,
          "rect": {
            "x": 219,
            "y": 227,
            "width": 640,
            "height": 480,
            "top": 227,
            "right": 859,
            "bottom": 707,
            "left": 219
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
            "x": 219,
            "y": 227,
            "width": 640,
            "height": 480,
            "top": 227,
            "right": 859,
            "bottom": 707,
            "left": 219
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
          "width": 640,
          "height": 480,
          "viewBox": null,
          "rect": {
            "x": 219,
            "y": 227,
            "width": 640,
            "height": 480,
            "top": 227,
            "right": 859,
            "bottom": 707,
            "left": 219
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "diagram-image",
          "className": "diagram-image",
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207719361",
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
          "src": "blob:http://127.0.0.1:5173/f8ff3d99-1bd9-49c8-a52e-2d44432341f5",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 1280,
          "height": 960,
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
        }
      ]
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Invertible mapping with the same image/overlay scale and offsets. Applying viewToSource(sourceToView(p)) should recover the supplied point within floating-point precision.

**What correct handling of THIS diagram requires:** The source supplies no numerical L, m or θ. Pivot, bob, radius and initial visual angle can be grounded geometrically. Meter scale, mass and gravity require explicit assumptions or other evidence.

**Comparison / debugging conclusion:** Actual sourceToView/sourceToOverlay and inverse results preserve supplied points. This does not validate the input coordinates against the source.

**Changes, provenance and possible information loss:** sourceToView includes viewport letterboxing; sourceToOverlay omits it because the overlay is already image-aligned. Browser coordinates add the measured image origin. Do not add letterboxing twice.

[Complete stage input/output bundle](stage_data/32_mapper.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: engine\core\coordinateMapper.js](contracts/engine/core/coordinateMapper.js)

## 33. Actual renderer at t=0 over the original

**Execution:** EXECUTED. **Verdict:** FAIL — T=0 SOURCE REGISTRATION.

**Upstream → downstream:** CoordinateMapper: source → overlay → browser → this component → Activation, motion and reset.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "runtime_output": {
      "domain": "mechanics",
      "subtype": "pendulum",
      "time": 0,
      "state": {
        "domain": "mechanics",
        "type": "pendulum",
        "subtype": "pendulum",
        "running": false,
        "time": 0,
        "thetaDeg": 26.1,
        "thetaRad": 0.4558,
        "omega": 0,
        "speed": 0,
        "length": 1,
        "gravity": 9.81,
        "potentialEnergy": 1,
        "kineticEnergy": 0,
        "totalEnergy": 1,
        "calibrated": true
      },
      "geometry": {
        "thetaRad": 0.45553093477052004,
        "lengthM": 1,
        "xM": 0,
        "yM": 0
      },
      "telemetry": {
        "domain": "mechanics",
        "type": "pendulum",
        "subtype": "pendulum",
        "running": false,
        "time": 0,
        "thetaDeg": 26.1,
        "thetaRad": 0.4558,
        "omega": 0,
        "speed": 0,
        "length": 1,
        "gravity": 9.81,
        "potentialEnergy": 1,
        "kineticEnergy": 0,
        "totalEnergy": 1,
        "calibrated": true
      },
      "events": [],
      "editableParameters": {
        "length": {
          "value": 1,
          "unit": "m",
          "provenance": "auto_policy",
          "editable": true,
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance",
            "control"
          ]
        },
        "initialAngle": {
          "value": 26.117406100584446,
          "unit": "°",
          "provenance": "observed",
          "editable": true,
          "targetId": "bob_1",
          "_nested_fields_in_complete_snapshot": [
            "control"
          ]
        }
      }
    },
    "transforms": [
      {
        "tag": "CANVAS",
        "rect": {
          "x": 219,
          "y": 227,
          "width": 640,
          "height": 480,
          "top": 227,
          "right": 859,
          "bottom": 707,
          "left": 219
        },
        "imageRect": {
          "x": 219,
          "y": 227,
          "width": 640,
          "height": 480,
          "top": 227,
          "right": 859,
          "bottom": 707,
          "left": 219
        },
        "scaleX": 2,
        "scaleY": 2,
        "dest": {
          "x": 0,
          "y": 0,
          "width": 1280,
          "height": 960
        }
      }
    ]
  }
]
```

**What it should receive — expected input:** Initialized runtime output, original background and the measured mapper/DOM geometry.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "captured_svg": [],
      "browser_state": {
        "domain": "mechanics",
        "type": "pendulum",
        "subtype": "pendulum",
        "running": false,
        "time": 0,
        "thetaDeg": 26.1,
        "thetaRad": 0.4558,
        "omega": 0,
        "speed": 0,
        "length": 1,
        "gravity": 9.81,
        "potentialEnergy": 1,
        "kineticEnergy": 0,
        "totalEnergy": 1,
        "calibrated": true
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The rendered source landmarks should coincide with the printed diagram at t=0. This requires correct upstream geometry as well as correct transforms.

**What correct handling of THIS diagram requires:** The pivot must agree with the mounting point/support; the string must connect that pivot to the bob. Bob segmentation is not evidence for the pivot. Record disagreement rather than accepting inconsistent constraints.

**Comparison / debugging conclusion:** MechanicsAdapter → PendulumKernel / PendulumSimulation. t=0 bob is source-aligned while pivot is above the printed support. No integration defect is established; physical time-scale accuracy has no numeric source ground truth.

**Changes, provenance and possible information loss:** Overlay image is captured from the actual canvas/SVG and projected back using measured DOM-to-source ratios. No objects were manually repositioned.

[Complete stage input/output bundle](stage_data/33_render.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

![runtime_t0_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/14_renderer/runtime_t0_overlay.png)

## 34. Activation, motion and reset

**Execution:** EXECUTED. **Verdict:** ACTUAL STATE CAPTURED.

**Upstream → downstream:** Actual renderer at t=0 over the original → this component → Final observed browser state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startSimulation",
    "phase": "input",
    "wallTime": 40886.59999999404,
    "data": []
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 40887.20000001788,
    "data": []
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.reset",
    "phase": "input",
    "wallTime": 42441.70000001788,
    "data": []
  },
  {
    "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 43056.59999999404,
    "data": []
  }
]
```

**What it should receive — expected input:** The initialized scene/state and actual Play/Pause/Reset control actions.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startSimulation",
      "phase": "output",
      "wallTime": 40887,
      "data": {
        "domain": "mechanics",
        "subtype": "pendulum",
        "source": {
          "type": "book_figure",
          "source_asset_id": "25c3ba19a02041ee9ec790156fc87e44",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_25c3ba19.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "pivot": {
            "x": 562,
            "y": 79.23811193908072
          },
          "bob_center": {
            "x": 841.3633806409911,
            "y": 649.0514992664916
          },
          "string_length_px": 634.61,
          "length_px": 634.61,
          "bob_radius_px": 37.03476174228877,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "length",
            "gravity",
            "initialAngle",
            "mass",
            "damping"
          ]
        },
        "assumptions": [
          {
            "parameter": "gravity",
            "policyId": "policy_earth_gravity",
            "policyVersion": "1.0",
            "value": 9.80665,
            "unit": "m/s²",
            "reason": "Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "damping",
            "policyId": "policy_zero_damping",
            "policyVersion": "1.0",
            "value": 0,
            "unit": "1/s",
            "reason": "Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "mass",
            "policyId": "policy_standard_mass",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "kg",
            "reason": "Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
            "provenance": "auto_policy",
            "confidence": 0.8
          },
          {
            "parameter": "length",
            "policyId": "policy_standard_pendulum_length",
            "policyVersion": "1.0",
            "value": 1,
            "unit": "m",
            "reason": "Standard 1.0 m simple pendulum string length.",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "environment",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 40888.59999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.reset",
      "phase": "output",
      "wallTime": 42442.90000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 43057.5,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "after_play": {
        "traceId": "TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017",
        "orchestrator": {
          "state": "SIMULATING",
          "currentError": null,
          "reviewState": null,
          "readinessReport": null,
          "_nested_fields_in_complete_snapshot": [
            "bookIR",
            "pageIR",
            "compiledScene",
            "sourceAsset"
          ]
        },
        "figure": {
          "sourceW": 1280,
          "sourceH": 960,
          "_nested_fields_in_complete_snapshot": [
            "scene",
            "output",
            "state",
            "mapper"
          ]
        },
        "browser": {
          "devicePixelRatio": 1,
          "innerWidth": 1418,
          "innerHeight": 1002,
          "outerWidth": 1440,
          "outerHeight": 1100,
          "scrollX": 0,
          "scrollY": 0,
          "_nested_fields_in_complete_snapshot": [
            "visualViewport"
          ]
        },
        "elements": [
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
            "src": "http://127.0.0.1:5173/uploads/diagram_25c3ba19.jpg",
            "naturalWidth": 1280,
            "naturalHeight": 960,
            "width": 640,
            "height": 480,
            "viewBox": null,
            "rect": {
              "x": 219,
              "y": 227,
              "width": 640,
              "height": 480,
              "top": 227,
              "right": 859,
              "bottom": 707,
              "left": 219
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
              "x": 219,
              "y": 227,
              "width": 640,
              "height": 480,
              "top": 227,
              "right": 859,
              "bottom": 707,
              "left": 219
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
            "width": 640,
            "height": 480,
            "viewBox": null,
            "rect": {
              "x": 219,
              "y": 227,
              "width": 640,
              "height": 480,
              "top": 227,
              "right": 859,
              "bottom": 707,
              "left": 219
            },
            "_nested_fields_in_complete_snapshot": [
              "css"
            ]
          },
          {
            "tag": "IMG",
            "id": "diagram-image",
            "className": "diagram-image",
            "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207719361",
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
            "src": "blob:http://127.0.0.1:5173/f8ff3d99-1bd9-49c8-a52e-2d44432341f5",
            "naturalWidth": 1280,
            "naturalHeight": 960,
            "width": 1280,
            "height": 960,
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
          }
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Motion evolves runtime state only; reset restores initial compiled values. Exact 0.5 s / 1 s states cannot be asserted unless their saved timestamps say so.

**What correct handling of THIS diagram requires:** At t=0 pivot and bob should register to their printed locations. Motion should pivot around that fixed point. No exact period can be asserted from the symbolic source alone.

**Comparison / debugging conclusion:** Automatic activation is observed in this checkout. Later frame time is whatever the runtime snapshot records, not an invented exact timestamp.

**Changes, provenance and possible information loss:** The executed main.js path automatically starts after a successful load. Later frames are saved at their actual times. Optics results are static ray solutions rather than pendulum-like time evolution.

[Complete stage input/output bundle](stage_data/34_motion.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/events.json)

- [Actual later browser frame](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/15_browser/runtime_after_play.png)

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

| SAM2 output → Grounder segmentation input | IDENTICAL | None |

| Grounded BookIR → Evidence pipeline returned BookIR | CHANGED | /provenance/evidence_pipeline_latency_ms |

| Evidence BookIR → AutoResolution input (dimension enforcement between) | IDENTICAL | None |

| AutoResolution BookIR → Compiler input (resolution evaluation between) | CHANGED | /parameters/pixels_per_meter |

| Compiler scene → Runtime normalization input (API/frontend URL binding between) | CHANGED | /source/image, /visual |

## Runtime subcomponents and capture boundary

| Component | Expected input | Expected output | Actual evidence / gap |

|---|---|---|---|

| validatePhysicsScene | Normalized canonical scene | Validation result / typed issues | Not separately intercepted; successful load shows continuation, not a saved validation-result object. |

| SimulationCapabilityRegistry.resolve | Validated normalized scene | Interactive scene/capabilities | No separate before/after capture. Use PhysicsRuntime source and actual runtime boundary; do not assume its output equals its input. |

| SolverRegistry.resolve | Interactive scene | Matching domain adapter | No separately serialized adapter return. Runtime domain/output and the executed load path establish the adapter route. |

| Adapter.initialize | Interactive scene, container and options | Initialized adapter state | Initial runtime output/state is captured, but this child call’s exact argument object is not separately recorded. |

| Domain solver | Adapter-derived model arguments | Physics solution/state | Actual solution/state is captured. Exact internal solver-call arguments are not a separate artifact. |

| Renderer.render / PendulumSimulation.render | Runtime solution/state and mapper | SVG/canvas output | Actual SVG/canvas and DOM measurements are captured; per-draw-call arguments are not. |

## Appendix A. Every captured backend component and invocation

The main 34 stages group nested helpers by their role in the data flow. This ledger retains every captured function, including parsing, unit conversion, geometry helpers, registry checks and repeated evaluators. Each call page contains exact input/output/locals and that function’s source contract. Call numbers are entry order, not completed-stage order.

- **ingest_diagram** (1 calls): [1](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- **_get_ingestion_pipeline** (1 calls): [2](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00002__get_ingestion_pipeline/STAGE.html)

- **UploadService.ingest** (1 calls): [3](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

- **compute_sha256** (1 calls): [4](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00004_compute_sha256/STAGE.html)

- **UploadService.get_public_url** (1 calls): [5](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00005_UploadService.get_public_url/STAGE.html)

- **PageIRBuilder.build** (1 calls): [6](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- **BookUnderstandingPipeline.analyze** (1 calls): [7](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- **BookUnderstandingPipeline._get_analyzer** (1 calls): [8](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00008_BookUnderstandingPipeline._get_analyzer/STAGE.html)

- **PhysicsVisionAnalyzer.analyze** (1 calls): [9](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- **GeminiVisionProvider.analyze_diagram** (1 calls): [10](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- **GeminiVisionProvider._get_client** (1 calls): [11](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00011_GeminiVisionProvider._get_client/STAGE.html)

- **Models.generate_content** (1 calls): [12](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

- **Models._generate_content** (1 calls): [13](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00013_Models._generate_content/STAGE.html)

- **_discard_dangling_relationships** (1 calls): [14](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00014__discard_dangling_relationships/STAGE.html)

- **validate_semantic_payload** (1 calls): [15](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- **SemanticConfidence.from_dict** (1 calls): [16](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00016_SemanticConfidence.from_dict/STAGE.html)

- **_validate_confidence** (14 calls): [17](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00017__validate_confidence/STAGE.html), [18](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00018__validate_confidence/STAGE.html), [19](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00019__validate_confidence/STAGE.html), [20](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00020__validate_confidence/STAGE.html), [22](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00022__validate_confidence/STAGE.html), [24](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00024__validate_confidence/STAGE.html), [26](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00026__validate_confidence/STAGE.html), [28](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00028__validate_confidence/STAGE.html), [30](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00030__validate_confidence/STAGE.html), [32](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00032__validate_confidence/STAGE.html), [34](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00034__validate_confidence/STAGE.html), [36](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00036__validate_confidence/STAGE.html), [38](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00038__validate_confidence/STAGE.html), [40](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00040__validate_confidence/STAGE.html)

- **SemanticEntity.from_dict** (4 calls): [21](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00021_SemanticEntity.from_dict/STAGE.html), [23](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00023_SemanticEntity.from_dict/STAGE.html), [25](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00025_SemanticEntity.from_dict/STAGE.html), [27](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00027_SemanticEntity.from_dict/STAGE.html)

- **SemanticRelationship.from_dict** (2 calls): [29](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00029_SemanticRelationship.from_dict/STAGE.html), [31](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00031_SemanticRelationship.from_dict/STAGE.html)

- **SemanticVisibleLabel.from_dict** (4 calls): [33](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00033_SemanticVisibleLabel.from_dict/STAGE.html), [35](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00035_SemanticVisibleLabel.from_dict/STAGE.html), [37](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00037_SemanticVisibleLabel.from_dict/STAGE.html), [39](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00039_SemanticVisibleLabel.from_dict/STAGE.html)

- **PhysicsVisionAnalyzer._apply_thresholds** (1 calls): [41](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00041_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

- **BookUnderstandingPipeline._build_book_ir_from_result** (1 calls): [42](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00042_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- **SemanticAnalysisResult.is_supported** (1 calls): [43](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00043_SemanticAnalysisResult.is_supported/STAGE.html)

- **EvidenceExtractionPipeline.extract_and_fuse** (1 calls): [44](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00044_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- **GrounderRegistry.find_grounder** (1 calls): [45](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00045_GrounderRegistry.find_grounder/STAGE.html)

- **PendulumGrounder.supports** (1 calls): [46](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00046_PendulumGrounder.supports/STAGE.html)

- **load_and_validate_source_image** (1 calls): [47](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00047_load_and_validate_source_image/STAGE.html)

- **MultiOCRRouter.available** (1 calls): [48](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00048_MultiOCRRouter.available/STAGE.html)

- **RapidOCRProvider.available** (2 calls): [49](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00049_RapidOCRProvider.available/STAGE.html), [52](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00052_RapidOCRProvider.available/STAGE.html)

- **MultiOCRRouter.extract** (1 calls): [50](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00050_MultiOCRRouter.extract/STAGE.html)

- **RapidOCRProvider.extract** (1 calls): [51](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00051_RapidOCRProvider.extract/STAGE.html)

- **ImageTransform.identity** (2 calls): [53](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00053_ImageTransform.identity/STAGE.html), [78](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00078_ImageTransform.identity/STAGE.html)

- **RapidOCRProvider._get_engine** (1 calls): [54](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00054_RapidOCRProvider._get_engine/STAGE.html)

- **ImageTransform.to_source_point** (32 calls): [55](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00055_ImageTransform.to_source_point/STAGE.html), [56](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00056_ImageTransform.to_source_point/STAGE.html), [57](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00057_ImageTransform.to_source_point/STAGE.html), [58](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00058_ImageTransform.to_source_point/STAGE.html), [61](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00061_ImageTransform.to_source_point/STAGE.html), [62](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00062_ImageTransform.to_source_point/STAGE.html), [63](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00063_ImageTransform.to_source_point/STAGE.html), [64](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00064_ImageTransform.to_source_point/STAGE.html), [67](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00067_ImageTransform.to_source_point/STAGE.html), [68](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00068_ImageTransform.to_source_point/STAGE.html), [69](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00069_ImageTransform.to_source_point/STAGE.html), [70](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00070_ImageTransform.to_source_point/STAGE.html), [80](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00080_ImageTransform.to_source_point/STAGE.html), [81](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00081_ImageTransform.to_source_point/STAGE.html), [82](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00082_ImageTransform.to_source_point/STAGE.html), [83](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00083_ImageTransform.to_source_point/STAGE.html), [87](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00087_ImageTransform.to_source_point/STAGE.html), [88](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00088_ImageTransform.to_source_point/STAGE.html), [89](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00089_ImageTransform.to_source_point/STAGE.html), [90](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00090_ImageTransform.to_source_point/STAGE.html), [94](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00094_ImageTransform.to_source_point/STAGE.html), [95](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00095_ImageTransform.to_source_point/STAGE.html), [96](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00096_ImageTransform.to_source_point/STAGE.html), [97](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00097_ImageTransform.to_source_point/STAGE.html), [101](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00101_ImageTransform.to_source_point/STAGE.html), [102](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00102_ImageTransform.to_source_point/STAGE.html), [103](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00103_ImageTransform.to_source_point/STAGE.html), [104](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00104_ImageTransform.to_source_point/STAGE.html), [108](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00108_ImageTransform.to_source_point/STAGE.html), [109](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00109_ImageTransform.to_source_point/STAGE.html), [110](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00110_ImageTransform.to_source_point/STAGE.html), [111](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00111_ImageTransform.to_source_point/STAGE.html)

- **SourcePolygon.bbox** (8 calls): [59](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00059_SourcePolygon.bbox/STAGE.html), [65](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00065_SourcePolygon.bbox/STAGE.html), [71](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00071_SourcePolygon.bbox/STAGE.html), [84](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00084_SourcePolygon.bbox/STAGE.html), [91](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00091_SourcePolygon.bbox/STAGE.html), [98](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00098_SourcePolygon.bbox/STAGE.html), [105](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00105_SourcePolygon.bbox/STAGE.html), [112](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00112_SourcePolygon.bbox/STAGE.html)

- **RapidOCRProvider.name** (4 calls): [60](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00060_RapidOCRProvider.name/STAGE.html), [66](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00066_RapidOCRProvider.name/STAGE.html), [72](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00072_RapidOCRProvider.name/STAGE.html), [73](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00073_RapidOCRProvider.name/STAGE.html)

- **RapidOCRProvider.model_version** (1 calls): [74](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00074_RapidOCRProvider.model_version/STAGE.html)

- **EasyOCRBanglaProvider.available** (4 calls): [75](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00075_EasyOCRBanglaProvider.available/STAGE.html), [77](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00077_EasyOCRBanglaProvider.available/STAGE.html), [132](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00132_EasyOCRBanglaProvider.available/STAGE.html), [134](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00134_EasyOCRBanglaProvider.available/STAGE.html)

- **EasyOCRBanglaProvider.extract** (1 calls): [76](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00076_EasyOCRBanglaProvider.extract/STAGE.html)

- **EasyOCRBanglaProvider._get_reader** (1 calls): [79](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00079_EasyOCRBanglaProvider._get_reader/STAGE.html)

- **is_bengali_text** (8 calls): [85](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00085_is_bengali_text/STAGE.html), [92](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00092_is_bengali_text/STAGE.html), [99](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00099_is_bengali_text/STAGE.html), [106](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00106_is_bengali_text/STAGE.html), [113](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00113_is_bengali_text/STAGE.html), [116](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00116_is_bengali_text/STAGE.html), [117](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00117_is_bengali_text/STAGE.html), [118](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00118_is_bengali_text/STAGE.html)

- **EasyOCRBanglaProvider.name** (6 calls): [86](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00086_EasyOCRBanglaProvider.name/STAGE.html), [93](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00093_EasyOCRBanglaProvider.name/STAGE.html), [100](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00100_EasyOCRBanglaProvider.name/STAGE.html), [107](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00107_EasyOCRBanglaProvider.name/STAGE.html), [114](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00114_EasyOCRBanglaProvider.name/STAGE.html), [115](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00115_EasyOCRBanglaProvider.name/STAGE.html)

- **deduplicate_spatial_tokens** (1 calls): [119](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00119_deduplicate_spatial_tokens/STAGE.html)

- **deduplicate_spatial_tokens.<locals>.<lambda>** (3 calls): [120](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00120_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [121](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00121_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [122](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00122_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html)

- **GreekSymbolVisualOCR.extract_symbols** (1 calls): [123](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00123_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- **PhysicsSymbolCandidateResolver.enrich_token** (4 calls): [124](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00124_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [126](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00126_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [128](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00128_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [130](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00130_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- **generate_symbol_alternatives** (4 calls): [125](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00125_generate_symbol_alternatives/STAGE.html), [127](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00127_generate_symbol_alternatives/STAGE.html), [129](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00129_generate_symbol_alternatives/STAGE.html), [131](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00131_generate_symbol_alternatives/STAGE.html)

- **MultiOCRRouter.name** (1 calls): [133](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00133_MultiOCRRouter.name/STAGE.html)

- **GreekSymbolVisualOCR.available** (1 calls): [135](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00135_GreekSymbolVisualOCR.available/STAGE.html)

- **UnavailableFormulaRecognitionProvider.available** (1 calls): [136](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00136_UnavailableFormulaRecognitionProvider.available/STAGE.html)

- **PendulumCVCandidateExtractor.extract_candidates** (1 calls): [137](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00137_PendulumCVCandidateExtractor.extract_candidates/STAGE.html)

- **preprocess_diagram** (1 calls): [138](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00138_preprocess_diagram/STAGE.html)

- **mask_out_text_regions** (1 calls): [139](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00139_mask_out_text_regions/STAGE.html)

- **math_floor** (8 calls): [140](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00140_math_floor/STAGE.html), [141](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00141_math_floor/STAGE.html), [144](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00144_math_floor/STAGE.html), [145](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00145_math_floor/STAGE.html), [148](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00148_math_floor/STAGE.html), [149](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00149_math_floor/STAGE.html), [152](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00152_math_floor/STAGE.html), [153](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00153_math_floor/STAGE.html)

- **math_ceil** (8 calls): [142](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00142_math_ceil/STAGE.html), [143](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00143_math_ceil/STAGE.html), [146](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00146_math_ceil/STAGE.html), [147](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00147_math_ceil/STAGE.html), [150](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00150_math_ceil/STAGE.html), [151](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00151_math_ceil/STAGE.html), [154](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00154_math_ceil/STAGE.html), [155](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00155_math_ceil/STAGE.html)

- **fit_circle_subpixel** (15 calls): [156](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00156_fit_circle_subpixel/STAGE.html), [157](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00157_fit_circle_subpixel/STAGE.html), [158](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00158_fit_circle_subpixel/STAGE.html), [159](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00159_fit_circle_subpixel/STAGE.html), [160](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00160_fit_circle_subpixel/STAGE.html), [161](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00161_fit_circle_subpixel/STAGE.html), [162](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00162_fit_circle_subpixel/STAGE.html), [163](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00163_fit_circle_subpixel/STAGE.html), [164](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00164_fit_circle_subpixel/STAGE.html), [165](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00165_fit_circle_subpixel/STAGE.html), [166](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00166_fit_circle_subpixel/STAGE.html), [167](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00167_fit_circle_subpixel/STAGE.html), [168](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00168_fit_circle_subpixel/STAGE.html), [169](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00169_fit_circle_subpixel/STAGE.html), [185](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00185_fit_circle_subpixel/STAGE.html)

- **SourcePoint.distance_to** (106 calls): [170](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00170_SourcePoint.distance_to/STAGE.html), [171](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00171_SourcePoint.distance_to/STAGE.html), [172](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00172_SourcePoint.distance_to/STAGE.html), [173](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00173_SourcePoint.distance_to/STAGE.html), [174](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00174_SourcePoint.distance_to/STAGE.html), [175](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00175_SourcePoint.distance_to/STAGE.html), [176](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00176_SourcePoint.distance_to/STAGE.html), [177](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00177_SourcePoint.distance_to/STAGE.html), [178](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00178_SourcePoint.distance_to/STAGE.html), [179](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00179_SourcePoint.distance_to/STAGE.html), [180](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00180_SourcePoint.distance_to/STAGE.html), [181](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00181_SourcePoint.distance_to/STAGE.html), [182](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00182_SourcePoint.distance_to/STAGE.html), [183](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00183_SourcePoint.distance_to/STAGE.html), [184](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00184_SourcePoint.distance_to/STAGE.html), [233](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00233_SourcePoint.distance_to/STAGE.html), [234](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00234_SourcePoint.distance_to/STAGE.html), [235](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00235_SourcePoint.distance_to/STAGE.html), [236](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00236_SourcePoint.distance_to/STAGE.html), [237](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00237_SourcePoint.distance_to/STAGE.html), [238](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00238_SourcePoint.distance_to/STAGE.html), [239](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00239_SourcePoint.distance_to/STAGE.html), [240](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00240_SourcePoint.distance_to/STAGE.html), [241](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00241_SourcePoint.distance_to/STAGE.html), [242](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00242_SourcePoint.distance_to/STAGE.html), [243](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00243_SourcePoint.distance_to/STAGE.html), [244](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00244_SourcePoint.distance_to/STAGE.html), [245](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00245_SourcePoint.distance_to/STAGE.html), [246](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00246_SourcePoint.distance_to/STAGE.html), [247](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00247_SourcePoint.distance_to/STAGE.html), [252](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00252_SourcePoint.distance_to/STAGE.html), [254](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00254_SourcePoint.distance_to/STAGE.html), [255](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00255_SourcePoint.distance_to/STAGE.html), [256](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00256_SourcePoint.distance_to/STAGE.html), [257](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00257_SourcePoint.distance_to/STAGE.html), [258](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00258_SourcePoint.distance_to/STAGE.html), [259](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00259_SourcePoint.distance_to/STAGE.html), [260](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00260_SourcePoint.distance_to/STAGE.html), [261](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00261_SourcePoint.distance_to/STAGE.html), [262](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00262_SourcePoint.distance_to/STAGE.html), [263](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00263_SourcePoint.distance_to/STAGE.html), [264](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00264_SourcePoint.distance_to/STAGE.html), [265](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00265_SourcePoint.distance_to/STAGE.html), [266](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00266_SourcePoint.distance_to/STAGE.html), [267](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00267_SourcePoint.distance_to/STAGE.html), [268](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00268_SourcePoint.distance_to/STAGE.html), [269](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00269_SourcePoint.distance_to/STAGE.html), [270](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00270_SourcePoint.distance_to/STAGE.html), [271](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00271_SourcePoint.distance_to/STAGE.html), [272](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00272_SourcePoint.distance_to/STAGE.html), [273](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00273_SourcePoint.distance_to/STAGE.html), [274](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00274_SourcePoint.distance_to/STAGE.html), [276](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00276_SourcePoint.distance_to/STAGE.html), [277](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00277_SourcePoint.distance_to/STAGE.html), [278](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00278_SourcePoint.distance_to/STAGE.html), [279](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00279_SourcePoint.distance_to/STAGE.html), [280](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00280_SourcePoint.distance_to/STAGE.html), [281](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00281_SourcePoint.distance_to/STAGE.html), [282](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00282_SourcePoint.distance_to/STAGE.html), [283](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00283_SourcePoint.distance_to/STAGE.html), [284](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00284_SourcePoint.distance_to/STAGE.html), [285](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00285_SourcePoint.distance_to/STAGE.html), [286](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00286_SourcePoint.distance_to/STAGE.html), [287](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00287_SourcePoint.distance_to/STAGE.html), [288](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00288_SourcePoint.distance_to/STAGE.html), [289](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00289_SourcePoint.distance_to/STAGE.html), [290](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00290_SourcePoint.distance_to/STAGE.html), [291](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00291_SourcePoint.distance_to/STAGE.html), [292](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00292_SourcePoint.distance_to/STAGE.html), [293](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00293_SourcePoint.distance_to/STAGE.html), [294](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00294_SourcePoint.distance_to/STAGE.html), [295](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00295_SourcePoint.distance_to/STAGE.html), [296](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00296_SourcePoint.distance_to/STAGE.html), [298](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00298_SourcePoint.distance_to/STAGE.html), [299](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00299_SourcePoint.distance_to/STAGE.html), [300](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00300_SourcePoint.distance_to/STAGE.html), [301](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00301_SourcePoint.distance_to/STAGE.html), [302](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00302_SourcePoint.distance_to/STAGE.html), [303](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00303_SourcePoint.distance_to/STAGE.html), [304](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00304_SourcePoint.distance_to/STAGE.html), [305](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00305_SourcePoint.distance_to/STAGE.html), [306](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00306_SourcePoint.distance_to/STAGE.html), [307](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00307_SourcePoint.distance_to/STAGE.html), [308](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00308_SourcePoint.distance_to/STAGE.html), [309](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00309_SourcePoint.distance_to/STAGE.html), [310](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00310_SourcePoint.distance_to/STAGE.html), [311](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00311_SourcePoint.distance_to/STAGE.html), [312](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00312_SourcePoint.distance_to/STAGE.html), [313](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00313_SourcePoint.distance_to/STAGE.html), [314](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00314_SourcePoint.distance_to/STAGE.html), [315](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00315_SourcePoint.distance_to/STAGE.html), [316](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00316_SourcePoint.distance_to/STAGE.html), [317](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00317_SourcePoint.distance_to/STAGE.html), [318](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00318_SourcePoint.distance_to/STAGE.html), [319](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00319_SourcePoint.distance_to/STAGE.html), [320](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00320_SourcePoint.distance_to/STAGE.html), [321](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00321_SourcePoint.distance_to/STAGE.html), [322](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00322_SourcePoint.distance_to/STAGE.html), [323](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00323_SourcePoint.distance_to/STAGE.html), [324](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00324_SourcePoint.distance_to/STAGE.html), [325](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00325_SourcePoint.distance_to/STAGE.html), [326](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00326_SourcePoint.distance_to/STAGE.html), [341](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00341_SourcePoint.distance_to/STAGE.html), [342](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00342_SourcePoint.distance_to/STAGE.html), [343](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00343_SourcePoint.distance_to/STAGE.html), [352](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00352_SourcePoint.distance_to/STAGE.html)

- **distance_pt** (47 calls): [186](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00186_distance_pt/STAGE.html), [187](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00187_distance_pt/STAGE.html), [188](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00188_distance_pt/STAGE.html), [189](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00189_distance_pt/STAGE.html), [190](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00190_distance_pt/STAGE.html), [191](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00191_distance_pt/STAGE.html), [192](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00192_distance_pt/STAGE.html), [193](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00193_distance_pt/STAGE.html), [194](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00194_distance_pt/STAGE.html), [195](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00195_distance_pt/STAGE.html), [196](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00196_distance_pt/STAGE.html), [197](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00197_distance_pt/STAGE.html), [198](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00198_distance_pt/STAGE.html), [199](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00199_distance_pt/STAGE.html), [200](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00200_distance_pt/STAGE.html), [201](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00201_distance_pt/STAGE.html), [202](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00202_distance_pt/STAGE.html), [203](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00203_distance_pt/STAGE.html), [204](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00204_distance_pt/STAGE.html), [205](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00205_distance_pt/STAGE.html), [206](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00206_distance_pt/STAGE.html), [207](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00207_distance_pt/STAGE.html), [208](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00208_distance_pt/STAGE.html), [209](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00209_distance_pt/STAGE.html), [210](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00210_distance_pt/STAGE.html), [211](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00211_distance_pt/STAGE.html), [212](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00212_distance_pt/STAGE.html), [213](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00213_distance_pt/STAGE.html), [214](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00214_distance_pt/STAGE.html), [215](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00215_distance_pt/STAGE.html), [216](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00216_distance_pt/STAGE.html), [217](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00217_distance_pt/STAGE.html), [218](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00218_distance_pt/STAGE.html), [219](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00219_distance_pt/STAGE.html), [220](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00220_distance_pt/STAGE.html), [221](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00221_distance_pt/STAGE.html), [222](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00222_distance_pt/STAGE.html), [223](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00223_distance_pt/STAGE.html), [224](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00224_distance_pt/STAGE.html), [225](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00225_distance_pt/STAGE.html), [226](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00226_distance_pt/STAGE.html), [227](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00227_distance_pt/STAGE.html), [228](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00228_distance_pt/STAGE.html), [229](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00229_distance_pt/STAGE.html), [230](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00230_distance_pt/STAGE.html), [231](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00231_distance_pt/STAGE.html), [232](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00232_distance_pt/STAGE.html)

- **PendulumCVCandidateExtractor.extract_candidates.<locals>.<lambda>** (7 calls): [248](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00248_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [249](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00249_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [250](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00250_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [251](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00251_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [327](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00327_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [328](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00328_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html), [329](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00329_PendulumCVCandidateExtractor.extract_candidates._locals_._lambda_/STAGE.html)

- **fit_line_subpixel** (3 calls): [253](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00253_fit_line_subpixel/STAGE.html), [275](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00275_fit_line_subpixel/STAGE.html), [297](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00297_fit_line_subpixel/STAGE.html)

- **SAM2SegmentationProvider.available** (2 calls): [330](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00330_SAM2SegmentationProvider.available/STAGE.html), [333](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00333_SAM2SegmentationProvider.available/STAGE.html)

- **SAM2SegmentationProvider._ensure_sam2_on_path** (3 calls): [331](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00331_SAM2SegmentationProvider._ensure_sam2_on_path/STAGE.html), [334](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00334_SAM2SegmentationProvider._ensure_sam2_on_path/STAGE.html), [336](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00336_SAM2SegmentationProvider._ensure_sam2_on_path/STAGE.html)

- **SAM2SegmentationProvider.segment** (1 calls): [332](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00332_SAM2SegmentationProvider.segment/STAGE.html)

- **SAM2SegmentationProvider._get_predictor** (1 calls): [335](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00335_SAM2SegmentationProvider._get_predictor/STAGE.html)

- **SAM2SegmentationProvider.name** (2 calls): [337](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00337_SAM2SegmentationProvider.name/STAGE.html), [338](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00338_SAM2SegmentationProvider.name/STAGE.html)

- **PendulumGrounder.ground** (1 calls): [339](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00339_PendulumGrounder.ground/STAGE.html)

- **SourceLine.length_px** (1 calls): [340](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00340_SourceLine.length_px/STAGE.html)

- **PendulumGrounder.ground.<locals>._get_coord** (8 calls): [344](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00344_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [345](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00345_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [346](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00346_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [347](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00347_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [348](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00348_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [349](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00349_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [350](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00350_PendulumGrounder.ground._locals_._get_coord/STAGE.html), [351](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00351_PendulumGrounder.ground._locals_._get_coord/STAGE.html)

- **parse_physical_value_candidate** (4 calls): [353](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00353_parse_physical_value_candidate/STAGE.html), [356](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00356_parse_physical_value_candidate/STAGE.html), [358](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00358_parse_physical_value_candidate/STAGE.html), [360](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00360_parse_physical_value_candidate/STAGE.html)

- **normalize_ocr_text** (5 calls): [354](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00354_normalize_ocr_text/STAGE.html), [355](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00355_normalize_ocr_text/STAGE.html), [357](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00357_normalize_ocr_text/STAGE.html), [359](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00359_normalize_ocr_text/STAGE.html), [361](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00361_normalize_ocr_text/STAGE.html)

- **enforce_source_dimensions** (1 calls): [362](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00362_enforce_source_dimensions/STAGE.html)

- **AutoResolutionEngine.resolve** (1 calls): [363](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00363_AutoResolutionEngine.resolve/STAGE.html)

- **RequirementRegistry.get_spec** (20 calls): [364](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00364_RequirementRegistry.get_spec/STAGE.html), [376](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00376_RequirementRegistry.get_spec/STAGE.html), [385](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00385_RequirementRegistry.get_spec/STAGE.html), [413](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00413_RequirementRegistry.get_spec/STAGE.html), [430](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00430_RequirementRegistry.get_spec/STAGE.html), [439](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00439_RequirementRegistry.get_spec/STAGE.html), [461](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00461_RequirementRegistry.get_spec/STAGE.html), [484](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00484_RequirementRegistry.get_spec/STAGE.html), [493](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00493_RequirementRegistry.get_spec/STAGE.html), [509](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00509_RequirementRegistry.get_spec/STAGE.html), [538](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00538_RequirementRegistry.get_spec/STAGE.html), [548](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00548_RequirementRegistry.get_spec/STAGE.html), [558](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00558_RequirementRegistry.get_spec/STAGE.html), [593](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00593_RequirementRegistry.get_spec/STAGE.html), [603](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00603_RequirementRegistry.get_spec/STAGE.html), [637](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00637_RequirementRegistry.get_spec/STAGE.html), [656](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00656_RequirementRegistry.get_spec/STAGE.html), [664](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00664_RequirementRegistry.get_spec/STAGE.html), [733](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00733_RequirementRegistry.get_spec/STAGE.html), [741](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00741_RequirementRegistry.get_spec/STAGE.html)

- **_grounded_value** (6 calls): [365](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00365__grounded_value/STAGE.html), [366](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00366__grounded_value/STAGE.html), [367](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00367__grounded_value/STAGE.html), [368](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00368__grounded_value/STAGE.html), [369](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00369__grounded_value/STAGE.html), [371](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00371__grounded_value/STAGE.html)

- **_inside_source** (2 calls): [370](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00370__inside_source/STAGE.html), [372](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00372__inside_source/STAGE.html)

- **PolicyRegistry.get_policy** (33 calls): [373](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00373_PolicyRegistry.get_policy/STAGE.html), [414](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00414_PolicyRegistry.get_policy/STAGE.html), [427](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00427_PolicyRegistry.get_policy/STAGE.html), [462](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00462_PolicyRegistry.get_policy/STAGE.html), [464](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00464_PolicyRegistry.get_policy/STAGE.html), [481](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00481_PolicyRegistry.get_policy/STAGE.html), [510](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00510_PolicyRegistry.get_policy/STAGE.html), [512](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00512_PolicyRegistry.get_policy/STAGE.html), [514](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00514_PolicyRegistry.get_policy/STAGE.html), [535](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00535_PolicyRegistry.get_policy/STAGE.html), [559](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00559_PolicyRegistry.get_policy/STAGE.html), [561](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00561_PolicyRegistry.get_policy/STAGE.html), [563](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00563_PolicyRegistry.get_policy/STAGE.html), [565](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00565_PolicyRegistry.get_policy/STAGE.html), [604](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00604_PolicyRegistry.get_policy/STAGE.html), [606](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00606_PolicyRegistry.get_policy/STAGE.html), [608](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00608_PolicyRegistry.get_policy/STAGE.html), [610](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00610_PolicyRegistry.get_policy/STAGE.html), [640](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00640_PolicyRegistry.get_policy/STAGE.html), [642](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00642_PolicyRegistry.get_policy/STAGE.html), [644](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00644_PolicyRegistry.get_policy/STAGE.html), [646](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00646_PolicyRegistry.get_policy/STAGE.html), [648](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00648_PolicyRegistry.get_policy/STAGE.html), [650](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00650_PolicyRegistry.get_policy/STAGE.html), [652](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00652_PolicyRegistry.get_policy/STAGE.html), [665](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00665_PolicyRegistry.get_policy/STAGE.html), [667](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00667_PolicyRegistry.get_policy/STAGE.html), [669](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00669_PolicyRegistry.get_policy/STAGE.html), [671](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00671_PolicyRegistry.get_policy/STAGE.html), [742](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00742_PolicyRegistry.get_policy/STAGE.html), [744](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00744_PolicyRegistry.get_policy/STAGE.html), [746](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00746_PolicyRegistry.get_policy/STAGE.html), [748](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00748_PolicyRegistry.get_policy/STAGE.html)

- **PolicyRegistry.get** (33 calls): [374](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00374_PolicyRegistry.get/STAGE.html), [415](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00415_PolicyRegistry.get/STAGE.html), [428](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00428_PolicyRegistry.get/STAGE.html), [463](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00463_PolicyRegistry.get/STAGE.html), [465](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00465_PolicyRegistry.get/STAGE.html), [482](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00482_PolicyRegistry.get/STAGE.html), [511](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00511_PolicyRegistry.get/STAGE.html), [513](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00513_PolicyRegistry.get/STAGE.html), [515](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00515_PolicyRegistry.get/STAGE.html), [536](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00536_PolicyRegistry.get/STAGE.html), [560](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00560_PolicyRegistry.get/STAGE.html), [562](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00562_PolicyRegistry.get/STAGE.html), [564](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00564_PolicyRegistry.get/STAGE.html), [566](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00566_PolicyRegistry.get/STAGE.html), [605](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00605_PolicyRegistry.get/STAGE.html), [607](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00607_PolicyRegistry.get/STAGE.html), [609](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00609_PolicyRegistry.get/STAGE.html), [611](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00611_PolicyRegistry.get/STAGE.html), [641](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00641_PolicyRegistry.get/STAGE.html), [643](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00643_PolicyRegistry.get/STAGE.html), [645](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00645_PolicyRegistry.get/STAGE.html), [647](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00647_PolicyRegistry.get/STAGE.html), [649](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00649_PolicyRegistry.get/STAGE.html), [651](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00651_PolicyRegistry.get/STAGE.html), [653](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00653_PolicyRegistry.get/STAGE.html), [666](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00666_PolicyRegistry.get/STAGE.html), [668](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00668_PolicyRegistry.get/STAGE.html), [670](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00670_PolicyRegistry.get/STAGE.html), [672](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00672_PolicyRegistry.get/STAGE.html), [743](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00743_PolicyRegistry.get/STAGE.html), [745](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00745_PolicyRegistry.get/STAGE.html), [747](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00747_PolicyRegistry.get/STAGE.html), [749](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00749_PolicyRegistry.get/STAGE.html)

- **ResolutionEngine.apply_resolution** (4 calls): [375](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00375_ResolutionEngine.apply_resolution/STAGE.html), [429](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00429_ResolutionEngine.apply_resolution/STAGE.html), [483](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00483_ResolutionEngine.apply_resolution/STAGE.html), [537](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00537_ResolutionEngine.apply_resolution/STAGE.html)

- **ModelRequirementSpec.canonicalize_parameter** (4 calls): [377](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00377_ModelRequirementSpec.canonicalize_parameter/STAGE.html), [431](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00431_ModelRequirementSpec.canonicalize_parameter/STAGE.html), [485](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00485_ModelRequirementSpec.canonicalize_parameter/STAGE.html), [539](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00539_ModelRequirementSpec.canonicalize_parameter/STAGE.html)

- **UnitEngine.parse_quantity** (40 calls): [378](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00378_UnitEngine.parse_quantity/STAGE.html), [417](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00417_UnitEngine.parse_quantity/STAGE.html), [420](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00420_UnitEngine.parse_quantity/STAGE.html), [423](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00423_UnitEngine.parse_quantity/STAGE.html), [432](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00432_UnitEngine.parse_quantity/STAGE.html), [467](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00467_UnitEngine.parse_quantity/STAGE.html), [470](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00470_UnitEngine.parse_quantity/STAGE.html), [473](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00473_UnitEngine.parse_quantity/STAGE.html), [477](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00477_UnitEngine.parse_quantity/STAGE.html), [486](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00486_UnitEngine.parse_quantity/STAGE.html), [517](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00517_UnitEngine.parse_quantity/STAGE.html), [520](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00520_UnitEngine.parse_quantity/STAGE.html), [523](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00523_UnitEngine.parse_quantity/STAGE.html), [527](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00527_UnitEngine.parse_quantity/STAGE.html), [531](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00531_UnitEngine.parse_quantity/STAGE.html), [540](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00540_UnitEngine.parse_quantity/STAGE.html), [568](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00568_UnitEngine.parse_quantity/STAGE.html), [571](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00571_UnitEngine.parse_quantity/STAGE.html), [574](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00574_UnitEngine.parse_quantity/STAGE.html), [578](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00578_UnitEngine.parse_quantity/STAGE.html), [582](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00582_UnitEngine.parse_quantity/STAGE.html), [586](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00586_UnitEngine.parse_quantity/STAGE.html), [613](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00613_UnitEngine.parse_quantity/STAGE.html), [616](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00616_UnitEngine.parse_quantity/STAGE.html), [619](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00619_UnitEngine.parse_quantity/STAGE.html), [623](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00623_UnitEngine.parse_quantity/STAGE.html), [627](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00627_UnitEngine.parse_quantity/STAGE.html), [631](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00631_UnitEngine.parse_quantity/STAGE.html), [674](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00674_UnitEngine.parse_quantity/STAGE.html), [677](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00677_UnitEngine.parse_quantity/STAGE.html), [680](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00680_UnitEngine.parse_quantity/STAGE.html), [684](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00684_UnitEngine.parse_quantity/STAGE.html), [688](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00688_UnitEngine.parse_quantity/STAGE.html), [692](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00692_UnitEngine.parse_quantity/STAGE.html), [751](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00751_UnitEngine.parse_quantity/STAGE.html), [754](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00754_UnitEngine.parse_quantity/STAGE.html), [757](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00757_UnitEngine.parse_quantity/STAGE.html), [761](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00761_UnitEngine.parse_quantity/STAGE.html), [765](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00765_UnitEngine.parse_quantity/STAGE.html), [769](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00769_UnitEngine.parse_quantity/STAGE.html)

- **UnitEngine.lookup_unit** (62 calls): [379](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00379_UnitEngine.lookup_unit/STAGE.html), [418](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00418_UnitEngine.lookup_unit/STAGE.html), [421](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00421_UnitEngine.lookup_unit/STAGE.html), [424](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00424_UnitEngine.lookup_unit/STAGE.html), [425](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00425_UnitEngine.lookup_unit/STAGE.html), [433](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00433_UnitEngine.lookup_unit/STAGE.html), [468](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00468_UnitEngine.lookup_unit/STAGE.html), [471](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00471_UnitEngine.lookup_unit/STAGE.html), [474](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00474_UnitEngine.lookup_unit/STAGE.html), [475](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00475_UnitEngine.lookup_unit/STAGE.html), [478](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00478_UnitEngine.lookup_unit/STAGE.html), [479](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00479_UnitEngine.lookup_unit/STAGE.html), [487](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00487_UnitEngine.lookup_unit/STAGE.html), [518](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00518_UnitEngine.lookup_unit/STAGE.html), [521](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00521_UnitEngine.lookup_unit/STAGE.html), [524](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00524_UnitEngine.lookup_unit/STAGE.html), [525](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00525_UnitEngine.lookup_unit/STAGE.html), [528](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00528_UnitEngine.lookup_unit/STAGE.html), [529](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00529_UnitEngine.lookup_unit/STAGE.html), [532](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00532_UnitEngine.lookup_unit/STAGE.html), [533](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00533_UnitEngine.lookup_unit/STAGE.html), [541](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00541_UnitEngine.lookup_unit/STAGE.html), [569](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00569_UnitEngine.lookup_unit/STAGE.html), [572](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00572_UnitEngine.lookup_unit/STAGE.html), [575](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00575_UnitEngine.lookup_unit/STAGE.html), [576](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00576_UnitEngine.lookup_unit/STAGE.html), [579](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00579_UnitEngine.lookup_unit/STAGE.html), [580](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00580_UnitEngine.lookup_unit/STAGE.html), [583](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00583_UnitEngine.lookup_unit/STAGE.html), [584](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00584_UnitEngine.lookup_unit/STAGE.html), [587](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00587_UnitEngine.lookup_unit/STAGE.html), [588](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00588_UnitEngine.lookup_unit/STAGE.html), [614](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00614_UnitEngine.lookup_unit/STAGE.html), [617](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00617_UnitEngine.lookup_unit/STAGE.html), [620](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00620_UnitEngine.lookup_unit/STAGE.html), [621](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00621_UnitEngine.lookup_unit/STAGE.html), [624](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00624_UnitEngine.lookup_unit/STAGE.html), [625](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00625_UnitEngine.lookup_unit/STAGE.html), [628](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00628_UnitEngine.lookup_unit/STAGE.html), [629](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00629_UnitEngine.lookup_unit/STAGE.html), [632](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00632_UnitEngine.lookup_unit/STAGE.html), [633](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00633_UnitEngine.lookup_unit/STAGE.html), [675](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00675_UnitEngine.lookup_unit/STAGE.html), [678](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00678_UnitEngine.lookup_unit/STAGE.html), [681](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00681_UnitEngine.lookup_unit/STAGE.html), [682](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00682_UnitEngine.lookup_unit/STAGE.html), [685](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00685_UnitEngine.lookup_unit/STAGE.html), [686](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00686_UnitEngine.lookup_unit/STAGE.html), [689](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00689_UnitEngine.lookup_unit/STAGE.html), [690](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00690_UnitEngine.lookup_unit/STAGE.html), [693](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00693_UnitEngine.lookup_unit/STAGE.html), [694](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00694_UnitEngine.lookup_unit/STAGE.html), [752](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00752_UnitEngine.lookup_unit/STAGE.html), [755](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00755_UnitEngine.lookup_unit/STAGE.html), [758](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00758_UnitEngine.lookup_unit/STAGE.html), [759](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00759_UnitEngine.lookup_unit/STAGE.html), [762](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00762_UnitEngine.lookup_unit/STAGE.html), [763](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00763_UnitEngine.lookup_unit/STAGE.html), [766](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00766_UnitEngine.lookup_unit/STAGE.html), [767](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00767_UnitEngine.lookup_unit/STAGE.html), [770](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00770_UnitEngine.lookup_unit/STAGE.html), [771](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00771_UnitEngine.lookup_unit/STAGE.html)

- **UnitEngine.validate_range** (40 calls): [380](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00380_UnitEngine.validate_range/STAGE.html), [419](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00419_UnitEngine.validate_range/STAGE.html), [422](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00422_UnitEngine.validate_range/STAGE.html), [426](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00426_UnitEngine.validate_range/STAGE.html), [434](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00434_UnitEngine.validate_range/STAGE.html), [469](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00469_UnitEngine.validate_range/STAGE.html), [472](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00472_UnitEngine.validate_range/STAGE.html), [476](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00476_UnitEngine.validate_range/STAGE.html), [480](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00480_UnitEngine.validate_range/STAGE.html), [488](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00488_UnitEngine.validate_range/STAGE.html), [519](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00519_UnitEngine.validate_range/STAGE.html), [522](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00522_UnitEngine.validate_range/STAGE.html), [526](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00526_UnitEngine.validate_range/STAGE.html), [530](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00530_UnitEngine.validate_range/STAGE.html), [534](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00534_UnitEngine.validate_range/STAGE.html), [542](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00542_UnitEngine.validate_range/STAGE.html), [570](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00570_UnitEngine.validate_range/STAGE.html), [573](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00573_UnitEngine.validate_range/STAGE.html), [577](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00577_UnitEngine.validate_range/STAGE.html), [581](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00581_UnitEngine.validate_range/STAGE.html), [585](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00585_UnitEngine.validate_range/STAGE.html), [589](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00589_UnitEngine.validate_range/STAGE.html), [615](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00615_UnitEngine.validate_range/STAGE.html), [618](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00618_UnitEngine.validate_range/STAGE.html), [622](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00622_UnitEngine.validate_range/STAGE.html), [626](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00626_UnitEngine.validate_range/STAGE.html), [630](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00630_UnitEngine.validate_range/STAGE.html), [634](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00634_UnitEngine.validate_range/STAGE.html), [676](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00676_UnitEngine.validate_range/STAGE.html), [679](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00679_UnitEngine.validate_range/STAGE.html), [683](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00683_UnitEngine.validate_range/STAGE.html), [687](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00687_UnitEngine.validate_range/STAGE.html), [691](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00691_UnitEngine.validate_range/STAGE.html), [695](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00695_UnitEngine.validate_range/STAGE.html), [753](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00753_UnitEngine.validate_range/STAGE.html), [756](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00756_UnitEngine.validate_range/STAGE.html), [760](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00760_UnitEngine.validate_range/STAGE.html), [764](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00764_UnitEngine.validate_range/STAGE.html), [768](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00768_UnitEngine.validate_range/STAGE.html), [772](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00772_UnitEngine.validate_range/STAGE.html)

- **ResolutionDecision.model_dump** (4 calls): [381](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00381_ResolutionDecision.model_dump/STAGE.html), [435](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00435_ResolutionDecision.model_dump/STAGE.html), [489](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00489_ResolutionDecision.model_dump/STAGE.html), [543](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00543_ResolutionDecision.model_dump/STAGE.html)

- **CalibrationEngine.derive_for_subtype** (5 calls): [382](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00382_CalibrationEngine.derive_for_subtype/STAGE.html), [436](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00436_CalibrationEngine.derive_for_subtype/STAGE.html), [490](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00490_CalibrationEngine.derive_for_subtype/STAGE.html), [544](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00544_CalibrationEngine.derive_for_subtype/STAGE.html), [638](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00638_CalibrationEngine.derive_for_subtype/STAGE.html)

- **ReadinessEvaluator.evaluate** (7 calls): [383](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00383_ReadinessEvaluator.evaluate/STAGE.html), [437](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00437_ReadinessEvaluator.evaluate/STAGE.html), [491](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00491_ReadinessEvaluator.evaluate/STAGE.html), [546](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00546_ReadinessEvaluator.evaluate/STAGE.html), [591](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00591_ReadinessEvaluator.evaluate/STAGE.html), [654](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00654_ReadinessEvaluator.evaluate/STAGE.html), [731](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00731_ReadinessEvaluator.evaluate/STAGE.html)

- **ResolutionAnalyzer.analyze** (7 calls): [384](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00384_ResolutionAnalyzer.analyze/STAGE.html), [438](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00438_ResolutionAnalyzer.analyze/STAGE.html), [492](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00492_ResolutionAnalyzer.analyze/STAGE.html), [547](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00547_ResolutionAnalyzer.analyze/STAGE.html), [592](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00592_ResolutionAnalyzer.analyze/STAGE.html), [655](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00655_ResolutionAnalyzer.analyze/STAGE.html), [732](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00732_ResolutionAnalyzer.analyze/STAGE.html)

- **ResolutionAnalyzer._check_geometry_requirements** (7 calls): [386](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00386_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [440](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00440_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [494](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00494_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [549](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00549_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [594](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00594_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [657](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00657_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [734](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00734_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- **ResolutionAnalyzer._check_parameter_requirements** (7 calls): [387](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00387_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [441](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00441_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [495](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00495_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [550](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00550_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [595](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00595_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [658](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00658_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [735](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00735_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- **ModelRequirementSpec.required_parameters** (14 calls): [388](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00388_ModelRequirementSpec.required_parameters/STAGE.html), [416](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00416_ModelRequirementSpec.required_parameters/STAGE.html), [442](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00442_ModelRequirementSpec.required_parameters/STAGE.html), [466](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00466_ModelRequirementSpec.required_parameters/STAGE.html), [496](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00496_ModelRequirementSpec.required_parameters/STAGE.html), [516](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00516_ModelRequirementSpec.required_parameters/STAGE.html), [551](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00551_ModelRequirementSpec.required_parameters/STAGE.html), [567](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00567_ModelRequirementSpec.required_parameters/STAGE.html), [596](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00596_ModelRequirementSpec.required_parameters/STAGE.html), [612](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00612_ModelRequirementSpec.required_parameters/STAGE.html), [659](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00659_ModelRequirementSpec.required_parameters/STAGE.html), [673](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00673_ModelRequirementSpec.required_parameters/STAGE.html), [736](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00736_ModelRequirementSpec.required_parameters/STAGE.html), [750](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00750_ModelRequirementSpec.required_parameters/STAGE.html)

- **ResolutionAnalyzer._find_unverified_ocr_candidate** (6 calls): [389](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00389_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html), [395](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00395_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html), [401](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00401_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html), [443](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00443_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html), [449](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00449_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html), [497](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00497_ResolutionAnalyzer._find_unverified_ocr_candidate/STAGE.html)

- **ModelRequirementSpec.allowed_units** (6 calls): [390](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00390_ModelRequirementSpec.allowed_units/STAGE.html), [396](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00396_ModelRequirementSpec.allowed_units/STAGE.html), [402](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00402_ModelRequirementSpec.allowed_units/STAGE.html), [444](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00444_ModelRequirementSpec.allowed_units/STAGE.html), [450](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00450_ModelRequirementSpec.allowed_units/STAGE.html), [498](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00498_ModelRequirementSpec.allowed_units/STAGE.html)

- **ModelRequirementSpec.expected_dimensions** (6 calls): [391](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00391_ModelRequirementSpec.expected_dimensions/STAGE.html), [397](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00397_ModelRequirementSpec.expected_dimensions/STAGE.html), [403](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00403_ModelRequirementSpec.expected_dimensions/STAGE.html), [445](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00445_ModelRequirementSpec.expected_dimensions/STAGE.html), [451](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00451_ModelRequirementSpec.expected_dimensions/STAGE.html), [499](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00499_ModelRequirementSpec.expected_dimensions/STAGE.html)

- **PolicyRegistry.find_policy** (11 calls): [392](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00392_PolicyRegistry.find_policy/STAGE.html), [398](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00398_PolicyRegistry.find_policy/STAGE.html), [404](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00404_PolicyRegistry.find_policy/STAGE.html), [409](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00409_PolicyRegistry.find_policy/STAGE.html), [446](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00446_PolicyRegistry.find_policy/STAGE.html), [452](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00452_PolicyRegistry.find_policy/STAGE.html), [457](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00457_PolicyRegistry.find_policy/STAGE.html), [500](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00500_PolicyRegistry.find_policy/STAGE.html), [505](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00505_PolicyRegistry.find_policy/STAGE.html), [554](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00554_PolicyRegistry.find_policy/STAGE.html), [599](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00599_PolicyRegistry.find_policy/STAGE.html)

- **PolicyRegistry.find_policies_for_parameter** (11 calls): [393](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00393_PolicyRegistry.find_policies_for_parameter/STAGE.html), [399](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00399_PolicyRegistry.find_policies_for_parameter/STAGE.html), [405](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00405_PolicyRegistry.find_policies_for_parameter/STAGE.html), [410](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00410_PolicyRegistry.find_policies_for_parameter/STAGE.html), [447](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00447_PolicyRegistry.find_policies_for_parameter/STAGE.html), [453](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00453_PolicyRegistry.find_policies_for_parameter/STAGE.html), [458](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00458_PolicyRegistry.find_policies_for_parameter/STAGE.html), [501](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00501_PolicyRegistry.find_policies_for_parameter/STAGE.html), [506](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00506_PolicyRegistry.find_policies_for_parameter/STAGE.html), [555](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00555_PolicyRegistry.find_policies_for_parameter/STAGE.html), [600](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00600_PolicyRegistry.find_policies_for_parameter/STAGE.html)

- **ResolutionPolicy.policy_id** (6 calls): [394](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00394_ResolutionPolicy.policy_id/STAGE.html), [400](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00400_ResolutionPolicy.policy_id/STAGE.html), [406](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00406_ResolutionPolicy.policy_id/STAGE.html), [448](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00448_ResolutionPolicy.policy_id/STAGE.html), [454](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00454_ResolutionPolicy.policy_id/STAGE.html), [502](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00502_ResolutionPolicy.policy_id/STAGE.html)

- **ResolutionAnalyzer._check_optional_parameters** (7 calls): [407](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00407_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [455](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00455_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [503](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00503_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [552](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00552_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [597](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00597_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [660](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00660_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [737](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00737_ResolutionAnalyzer._check_optional_parameters/STAGE.html)

- **ModelRequirementSpec.optional_parameters** (7 calls): [408](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00408_ModelRequirementSpec.optional_parameters/STAGE.html), [456](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00456_ModelRequirementSpec.optional_parameters/STAGE.html), [504](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00504_ModelRequirementSpec.optional_parameters/STAGE.html), [553](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00553_ModelRequirementSpec.optional_parameters/STAGE.html), [598](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00598_ModelRequirementSpec.optional_parameters/STAGE.html), [661](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00661_ModelRequirementSpec.optional_parameters/STAGE.html), [738](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00738_ModelRequirementSpec.optional_parameters/STAGE.html)

- **PolicyRegistry.get_policies_for_subtype** (7 calls): [411](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00411_PolicyRegistry.get_policies_for_subtype/STAGE.html), [459](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00459_PolicyRegistry.get_policies_for_subtype/STAGE.html), [507](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00507_PolicyRegistry.get_policies_for_subtype/STAGE.html), [556](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00556_PolicyRegistry.get_policies_for_subtype/STAGE.html), [601](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00601_PolicyRegistry.get_policies_for_subtype/STAGE.html), [662](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00662_PolicyRegistry.get_policies_for_subtype/STAGE.html), [739](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00739_PolicyRegistry.get_policies_for_subtype/STAGE.html)

- **PolicyRegistry.list_all** (7 calls): [412](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00412_PolicyRegistry.list_all/STAGE.html), [460](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00460_PolicyRegistry.list_all/STAGE.html), [508](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00508_PolicyRegistry.list_all/STAGE.html), [557](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00557_PolicyRegistry.list_all/STAGE.html), [602](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00602_PolicyRegistry.list_all/STAGE.html), [663](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00663_PolicyRegistry.list_all/STAGE.html), [740](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00740_PolicyRegistry.list_all/STAGE.html)

- **CalibrationEngine.derive_calibration** (2 calls): [545](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00545_CalibrationEngine.derive_calibration/STAGE.html), [639](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00639_CalibrationEngine.derive_calibration/STAGE.html)

- **ProvenanceRecord.model_dump** (5 calls): [590](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00590_ProvenanceRecord.model_dump/STAGE.html), [635](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00635_ProvenanceRecord.model_dump/STAGE.html), [696](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00696_ProvenanceRecord.model_dump/STAGE.html), [773](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00773_ProvenanceRecord.model_dump/STAGE.html), [808](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00808_ProvenanceRecord.model_dump/STAGE.html)

- **ResolutionEngine.auto_resolve** (1 calls): [636](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00636_ResolutionEngine.auto_resolve/STAGE.html)

- **PhysicsCompiler.compile** (1 calls): [697](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00697_PhysicsCompiler.compile/STAGE.html)

- **PhysicsCompiler._validate_grounding** (1 calls): [698](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00698_PhysicsCompiler._validate_grounding/STAGE.html)

- **PhysicsCompiler._extract_source_dimensions** (2 calls): [699](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00699_PhysicsCompiler._extract_source_dimensions/STAGE.html), [775](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00775_PhysicsCompiler._extract_source_dimensions/STAGE.html)

- **PhysicsCompiler._extract_raw_val** (15 calls): [700](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00700_PhysicsCompiler._extract_raw_val/STAGE.html), [701](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00701_PhysicsCompiler._extract_raw_val/STAGE.html), [703](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00703_PhysicsCompiler._extract_raw_val/STAGE.html), [704](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00704_PhysicsCompiler._extract_raw_val/STAGE.html), [709](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00709_PhysicsCompiler._extract_raw_val/STAGE.html), [712](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00712_PhysicsCompiler._extract_raw_val/STAGE.html), [776](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00776_PhysicsCompiler._extract_raw_val/STAGE.html), [777](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00777_PhysicsCompiler._extract_raw_val/STAGE.html), [779](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00779_PhysicsCompiler._extract_raw_val/STAGE.html), [780](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00780_PhysicsCompiler._extract_raw_val/STAGE.html), [785](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00785_PhysicsCompiler._extract_raw_val/STAGE.html), [788](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00788_PhysicsCompiler._extract_raw_val/STAGE.html), [790](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00790_PhysicsCompiler._extract_raw_val/STAGE.html), [792](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00792_PhysicsCompiler._extract_raw_val/STAGE.html), [803](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00803_PhysicsCompiler._extract_raw_val/STAGE.html)

- **_first_not_none** (22 calls): [702](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00702__first_not_none/STAGE.html), [705](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00705__first_not_none/STAGE.html), [707](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00707__first_not_none/STAGE.html), [710](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00710__first_not_none/STAGE.html), [713](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00713__first_not_none/STAGE.html), [716](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00716__first_not_none/STAGE.html), [719](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00719__first_not_none/STAGE.html), [722](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00722__first_not_none/STAGE.html), [725](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00725__first_not_none/STAGE.html), [727](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00727__first_not_none/STAGE.html), [728](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00728__first_not_none/STAGE.html), [778](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00778__first_not_none/STAGE.html), [781](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00781__first_not_none/STAGE.html), [783](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00783__first_not_none/STAGE.html), [786](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00786__first_not_none/STAGE.html), [789](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00789__first_not_none/STAGE.html), [791](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00791__first_not_none/STAGE.html), [793](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00793__first_not_none/STAGE.html), [796](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00796__first_not_none/STAGE.html), [799](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00799__first_not_none/STAGE.html), [802](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00802__first_not_none/STAGE.html), [804](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00804__first_not_none/STAGE.html)

- **PhysicsCompiler._validate_parameters** (1 calls): [706](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00706_PhysicsCompiler._validate_parameters/STAGE.html)

- **PhysicsCompiler._extract_point** (4 calls): [708](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00708_PhysicsCompiler._extract_point/STAGE.html), [711](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00711_PhysicsCompiler._extract_point/STAGE.html), [784](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00784_PhysicsCompiler._extract_point/STAGE.html), [787](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00787_PhysicsCompiler._extract_point/STAGE.html)

- **_extract_val_and_unit** (9 calls): [714](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00714__extract_val_and_unit/STAGE.html), [717](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00717__extract_val_and_unit/STAGE.html), [720](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00720__extract_val_and_unit/STAGE.html), [723](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00723__extract_val_and_unit/STAGE.html), [726](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00726__extract_val_and_unit/STAGE.html), [729](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00729__extract_val_and_unit/STAGE.html), [794](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00794__extract_val_and_unit/STAGE.html), [797](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00797__extract_val_and_unit/STAGE.html), [800](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00800__extract_val_and_unit/STAGE.html)

- **_validate_and_convert_unit** (8 calls): [715](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00715__validate_and_convert_unit/STAGE.html), [718](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00718__validate_and_convert_unit/STAGE.html), [721](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00721__validate_and_convert_unit/STAGE.html), [724](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00724__validate_and_convert_unit/STAGE.html), [730](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00730__validate_and_convert_unit/STAGE.html), [795](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00795__validate_and_convert_unit/STAGE.html), [798](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00798__validate_and_convert_unit/STAGE.html), [801](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00801__validate_and_convert_unit/STAGE.html)

- **PhysicsCompiler._build_canonical_scene** (1 calls): [774](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00774_PhysicsCompiler._build_canonical_scene/STAGE.html)

- **PhysicsCompiler._populate_canonical_pendulum** (1 calls): [782](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00782_PhysicsCompiler._populate_canonical_pendulum/STAGE.html)

- **PhysicsCompiler._find_entity** (1 calls): [805](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00805_PhysicsCompiler._find_entity/STAGE.html)

- **PhysicsCompiler._preserve_parameter_provenance** (1 calls): [806](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00806_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- **validate_canonical_scene** (1 calls): [807](../../../../storage/generated/debug_traces/20261016/TRACE-PENDULUM-20261016-003-NATIVE-RETRY-20261017/calls/00807_validate_canonical_scene/STAGE.html)

## Appendix B. First failure and propagation

Last known good: Exact source, correct semantic pendulum roles and symbolic OCR; no printed numeric length/mass is claimed.

First suspicious: Selected visible string begins at (556,67), extending into the mounting hatch region.

First definitive failure: CV accepts a pivot above the detected support while reporting the disagreement in its own validation metadata.

Downstream chain: SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px. Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale. Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.

Separation of failure classes: preprocessing/perception is demonstrated upstream; a shared coordinate conversion error is not demonstrated; numerical solver failure is not established. The circuit never reaches a solver.

## Appendix C. Capture limits

No new run was performed. The recorder captured repository Python boundaries and GenAI model calls, not private neural-library/C internals. JS boundary events, normalized scenes, actual solver outputs and DOM captures exist; separate entry/exit snapshots for every registry/adapter/renderer child function do not. These gaps are labeled, not filled with reconstructed output. Several void JS returns appear as captureError because undefined is not JSON; resulting state is separately recorded. Two class-serialization errors exist in the historical recorder log; integrity verification found the required snapshot files present for every indexed call. No exact expected pixel dataset, mask or numerical physical state has been authored.

[Original trace integrity checks](../../../../storage/generated/debug_traces/20261017/artifact_verification.json)
