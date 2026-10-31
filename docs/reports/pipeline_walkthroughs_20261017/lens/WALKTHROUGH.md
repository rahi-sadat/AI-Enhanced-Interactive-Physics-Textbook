# Convex lens: complete component-by-component debugging walkthrough

Trace ID: `TRACE-LENS-20261016-001-NATIVE-RETRY-20261017`. These documents use the existing live native Windows request from 2026-10-17. No models, detectors or solvers were rerun while writing them. No production fixes were made.

Source reference: A convex lens, horizontal principal axis, upright object to the left between F and 2F, inverted enlarged image to the right beyond 2F, focal markers and principal rays. Printed f=15 cm.

Known and unknown evidence: 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

Expected geometry for this diagram: Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

Expected initial simulation: At t=0 the object should occupy its printed arrow and the image/rays should be compared to the printed image/rays. The actual solver returns real_same_size from assumed u=2f, whereas the source depicts an enlarged image. This demonstrates an input/model mismatch, not an arithmetic failure.

Exact expected coordinates/masks are unavailable: EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS. Expected behavior below is a contract or a qualitative source comparison, never a hand-drawn expected result.

![Unchanged original diagram](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/00_source/original.png)

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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "source": "C:\\Users\\saher\\Downloads\\photo_2026-10-10_12-06-36 (2).jpg",
      "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
      "bytes": 51136
    },
    "metadata": {
      "file_format": "JPEG",
      "encoded_width": 1280,
      "encoded_height": 960,
      "EXIF_orientation": null,
      "orientation": "landscape",
      "decoded_width": 1280,
      "decoded_height": 960,
      "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
      "png_note": "Lossless serialization of OpenCV decoded original JPEG; no resize, crop, redrawing, or orientation edit. Byte-exact original.jpg retained.",
      "decoded_pixels_sha256": "d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5",
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
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207572089",
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
          "src": "blob:http://127.0.0.1:5173/643e338b-5bfb-43b1-ba53-dab43b65cd1a",
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
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startWithFile",
    "phase": "input",
    "wallTime": 3507.800000011921,
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startWithFile",
      "phase": "output",
      "wallTime": 48498.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** One upload operation: first UPLOADING, then a response-governed final state. This outer async call spans the rest of the pipeline; it must not invent a scene locally.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** File → multipart request. The generic JS File snapshot is {}, so use multipart metadata and the byte-exact source, not {} as evidence of an empty file.

[Complete stage input/output bundle](stage_data/01_upload.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 02. HTTP request reaches /api/ingest

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Browser selects the original diagram → this component → Upload persistence and dimension decoding.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "trace_id": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
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
          "51343"
        ],
        [
          "x-physics-trace-id",
          "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017"
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
          "multipart/form-data; boundary=----WebKitFormBoundarynIVac4OG1Nfmfz2B"
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Browser transport → FastAPI handler. Handler parameter is opaque in the profiler; saved multipart bytes are the authoritative payload.

[Complete stage input/output bundle](stage_data/02_http_in.json)

- [Exact multipart body](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/http/1792207574356209400_request_body.bin)

- [HTTP response 1792207574356209400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/http/1792207574356209400_response_body.json)

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
        "bytes": 51136,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c.bin"
      },
      "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
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
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** SourceAsset with storage path/public URL, content hash, native decoded dimensions and original filename.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Encoded bytes are persisted; metadata and an asset ID are added. This is not object detection.

[Complete stage input/output bundle](stage_data/03_asset.json)

- [UploadService.ingest — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

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
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
      },
      "public_url": "/uploads/diagram_dd013d21.jpg"
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
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** SourceAsset → PageIR. The whole image is user-supplied; confidence in that extent does not imply confidence in physics landmarks.

[Complete stage input/output bundle](stage_data/04_page.json)

- [PageIRBuilder.build — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- [Code: ai\ingestion\PageIRBuilder.py](contracts/ai/ingestion/PageIRBuilder.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/actual_overlay_on_source.png)

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
        "bytes": 51136,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c.bin"
      },
      "mime_type": "image/jpeg",
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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
              "bytes": 51136,
              "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
              "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c.bin"
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
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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
            "date": "Sat, 17 Oct 2026 03:26:19 GMT",
            "server": "scaffolding on HTTPServer2",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "x-content-type-options": "nosniff",
            "server-timing": "gfet4t7; dur=3909",
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
                  "text": "{\n  \"classification\": \"supported\",\n  \"isPhysics\": true,\n  \"domain\": \"optics\",\n  \"subtype\": \"thin_lens\",\n  \"confidence\": {\n    \"isPhysics\": 1.0,\n    \"domain\": 1.0,\n    \"subtype\": 1.0,\n    \"overall\": 1.0\n  },\n  \"entities\": [\n    {\n      \"temporaryId\": \"lens_1\",\n      \"role\": \"lens\",\n      \"label\": \"convex lens\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"object_1\",\n      \"role\": \"object\",\n      \"label\": \"Object\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"image_1\",\n      \"role\": \"image\",\n      \"label\": \"Image\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"axis_1\",\n      \"role\": \"optical_axis\",\n      \"label\": \"principal axis\",\n      \"confidence\": 0.95\n    },\n    {\n      \"temporaryId\": \"focal_point_1\",\n      \"role\": \"focal_point\",\n      \"label\": \"F\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"focal_point_2\",\n      \"role\": \"focal_point\",\n      \"label\": \"2F\",\n      \"confidence\": 1.0\n    }\n  ],\n  \"relationships\": [\n    {\n      \"type\": \"forms_image\",\n      \"from\": \"lens_1\",\n      \"to\": \"image_1\",\n      \"confidence\": 1.0\n    },\n    {\n      \"type\": \"refracts\",\n      \"from\": \"object_1\",\n      \"to\": \"lens_1\",\n      \"confidence\": 1.0\n    }\n  ],\n  \"visibleLabels\": [\n    {\n      \"text\": \"Object\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"object_label\"\n    },\n    {\n      \"text\": \"Image\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"image_label\"\n    },\n    {\n      \"text\": \"f = 15 cm\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"focal_length\"\n    },\n    {\n      \"text\": \"2F\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"focal_point_marker\"\n    },\n    {\n      \"text\": \"F\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"focal_point_marker\"\n    },\n    {\n      \"text\": \"O\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"optical_center\"\n    }\n  ],\n  \"candidates\": [],\n  \"notes\": [\n    \"Diagram shows image formation by a convex lens with an object placed beyond 2F.\"\n  ]\n}",
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
        "response_id": "2OrSasbIB9zvg8UP6YC68AU",
        "usage_metadata": {
          "cache_tokens_details": null,
          "cached_content_token_count": null,
          "candidates_token_count": 734,
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
          "total_token_count": 2967,
          "traffic_type": null
        },
        "model_status": null,
        "automatic_function_calling_history": [],
        "parsed": {
          "classification": "supported",
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "confidence": {
            "isPhysics": 1.0,
            "domain": 1.0,
            "subtype": 1.0,
            "overall": 1.0
          },
          "entities": [
            {
              "temporaryId": "lens_1",
              "role": "lens",
              "label": "convex lens",
              "confidence": 1.0
            },
            {
              "temporaryId": "object_1",
              "role": "object",
              "label": "Object",
              "confidence": 1.0
            },
            {
              "temporaryId": "image_1",
              "role": "image",
              "label": "Image",
              "confidence": 1.0
            },
            {
              "temporaryId": "axis_1",
              "role": "optical_axis",
              "label": "principal axis",
              "confidence": 0.95
            },
            {
              "temporaryId": "focal_point_1",
              "role": "focal_point",
              "label": "F",
              "confidence": 1.0
            },
            {
              "temporaryId": "focal_point_2",
              "role": "focal_point",
              "label": "2F",
              "confidence": 1.0
            }
          ],
          "relationships": [
            {
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 1.0
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
              "confidence": 1.0
            }
          ],
          "visibleLabels": [
            {
              "text": "Object",
              "confidence": 1.0,
              "semanticRole": "object_label"
            },
            {
              "text": "Image",
              "confidence": 1.0,
              "semanticRole": "image_label"
            },
            {
              "text": "f = 15 cm",
              "confidence": 1.0,
              "semanticRole": "focal_length"
            },
            {
              "text": "2F",
              "confidence": 1.0,
              "semanticRole": "focal_point_marker"
            },
            {
              "text": "F",
              "confidence": 1.0,
              "semanticRole": "focal_point_marker"
            },
            {
              "text": "O",
              "confidence": 1.0,
              "semanticRole": "optical_center"
            }
          ],
          "candidates": [],
          "notes": [
            "Diagram shows image formation by a convex lens with an object placed beyond 2F."
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Semantic classification, domain/subtype, entity roles and relationships. Numerical physical parameters and authoritative geometry must not originate here.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / thin_lens. Expected semantic content: A convex lens, horizontal principal axis, upright object to the left between F and 2F, inverted enlarged image to the right beyond 2F, focal markers and principal rays. Printed f=15 cm. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Image → model response. SDK/provider-internal preprocessing and private tensors were not exposed; no transform is invented for them.

[Complete stage input/output bundle](stage_data/05_vlm.json)

- [GeminiVisionProvider.analyze_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- [Models.generate_content — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

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
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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
        "domain": "optics",
        "subtype": "thin_lens",
        "confidence": {
          "isPhysics": 1.0,
          "domain": 1.0,
          "subtype": 1.0,
          "overall": 1.0
        },
        "entities": [
          {
            "temporaryId": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 1.0
          },
          {
            "temporaryId": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 1.0
          },
          {
            "temporaryId": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 1.0
          },
          {
            "temporaryId": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95
          },
          {
            "temporaryId": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 1.0
          },
          {
            "temporaryId": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 1.0
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 1.0
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
            "confidence": 1.0
          }
        ],
        "visibleLabels": [
          {
            "text": "Object",
            "confidence": 1.0,
            "semanticRole": "object_label"
          },
          {
            "text": "Image",
            "confidence": 1.0,
            "semanticRole": "image_label"
          },
          {
            "text": "f = 15 cm",
            "confidence": 1.0,
            "semanticRole": "focal_length"
          },
          {
            "text": "2F",
            "confidence": 1.0,
            "semanticRole": "focal_point_marker"
          },
          {
            "text": "F",
            "confidence": 1.0,
            "semanticRole": "focal_point_marker"
          },
          {
            "text": "O",
            "confidence": 1.0,
            "semanticRole": "optical_center"
          }
        ],
        "candidates": [],
        "notes": [
          "Diagram shows image formation by a convex lens with an object placed beyond 2F."
        ]
      }
    }
  },
  {
    "call": "00049_PhysicsVisionAnalyzer._apply_thresholds",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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
      "call": "00049_PhysicsVisionAnalyzer._apply_thresholds",
      "return_value": {
        "classification": "supported",
        "is_physics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / thin_lens. Expected semantic content: A convex lens, horizontal principal axis, upright object to the left between F and 2F, inverted enlarged image to the right beyond 2F, focal markers and principal rays. Printed f=15 cm. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Raw semantic response → validated semantic representation. Compare raw_provider confidence with the capped accepted values.

[Complete stage input/output bundle](stage_data/06_semantic.json)

- [PhysicsVisionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- [validate_semantic_payload — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- [PhysicsVisionAnalyzer._apply_thresholds — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00049_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

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
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
      }
    }
  },
  {
    "call": "00050_BookUnderstandingPipeline._build_book_ir_from_result",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "entities": [
          {
            "temporary_id": "lens_1",
            "role": "lens",
            "label": "convex lens",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "object_1",
            "role": "object",
            "label": "Object",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "image_1",
            "role": "image",
            "label": "Image",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "axis_1",
            "role": "optical_axis",
            "label": "principal axis",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_1",
            "role": "focal_point",
            "label": "F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "focal_point_2",
            "role": "focal_point",
            "label": "2F",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "forms_image",
            "source_id": "lens_1",
            "target_id": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "source_id": "object_1",
            "target_id": "lens_1",
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
      "asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
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
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
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
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00050_BookUnderstandingPipeline._build_book_ir_from_result",
      "return_value": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
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
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
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
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / thin_lens. Expected semantic content: A convex lens, horizontal principal axis, upright object to the left between F and 2F, inverted enlarged image to the right beyond 2F, focal markers and principal rays. Printed f=15 cm. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Semantic roles are assigned durable entity IDs. This BookIR is an intermediate hypothesis, not a runnable simulation.

[Complete stage input/output bundle](stage_data/07_book.json)

- [BookUnderstandingPipeline.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- [BookUnderstandingPipeline._build_book_ir_from_result — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00050_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- [Code: ai\ingestion\BookUnderstandingPipeline.py](contracts/ai/ingestion/BookUnderstandingPipeline.py)

## 08. Evidence dispatch and source decode

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Initial semantic BookIR → this component → RapidOCR: first text/box observations.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00053_GrounderRegistry.find_grounder",
    "value": {
      "domain": "optics",
      "subtype": "thin_lens"
    }
  },
  {
    "call": "00057_load_and_validate_source_image",
    "value": {
      "asset": {
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
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
      "call": "00053_GrounderRegistry.find_grounder",
      "return_value": {
        "type": "ai.evidence.grounding.thin_lens.ThinLensGrounder",
        "not_serialized": true
      }
    },
    {
      "call": "00057_load_and_validate_source_image",
      "return_value": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The matching subtype grounder and the unchanged native BGR image array; decoder dimensions must match the asset.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** The pipeline routes to the domain module. Other grounders may execute supports() checks; their ground() methods are not thereby executed.

[Complete stage input/output bundle](stage_data/08_route.json)

- [GrounderRegistry.find_grounder — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00053_GrounderRegistry.find_grounder/STAGE.html)

- [load_and_validate_source_image — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00057_load_and_validate_source_image/STAGE.html)

- [Code: ai\evidence\grounding\registry.py](contracts/ai/evidence/grounding/registry.py)

- [Code: ai\evidence\transforms.py](contracts/ai/evidence/transforms.py)

## 09. RapidOCR: first text/box observations

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** Evidence dispatch and source decode → this component → EasyOCR: independent OCR candidates.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00061_RapidOCRProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
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
      "call": "00061_RapidOCRProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_001",
            "raw_text": "f = 15 cm",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 933.0,
              "y": 189.0,
              "width": 208.0,
              "height": 55.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 933.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 244.0
                },
                {
                  "x": 933.0,
                  "y": 244.0
                }
              ]
            },
            "confidence": 0.96641,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "Object",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 188.0,
              "y": 220.0,
              "width": 135.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 189.0,
                  "y": 220.0
                },
                {
                  "x": 323.0,
                  "y": 223.0
                },
                {
                  "x": 322.0,
                  "y": 277.0
                },
                {
                  "x": 188.0,
                  "y": 274.0
                }
              ]
            },
            "confidence": 0.9999,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 102.0,
              "y": 449.0,
              "width": 70.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 102.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 500.0
                },
                {
                  "x": 102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99964,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 356.0,
              "y": 451.0,
              "width": 42.0,
              "height": 47.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 361.0,
                  "y": 451.0
                },
                {
                  "x": 398.0,
                  "y": 455.0
                },
                {
                  "x": 393.0,
                  "y": 498.0
                },
                {
                  "x": 356.0,
                  "y": 494.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 849.0,
              "y": 449.0,
              "width": 38.0,
              "height": 43.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 849.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 492.0
                },
                {
                  "x": 849.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.9994,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1102.0,
              "y": 449.0,
              "width": 69.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1102.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 500.0
                },
                {
                  "x": 1102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99972,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Image",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1118.0,
              "y": 646.0,
              "width": 129.0,
              "height": 56.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1120.0,
                  "y": 646.0
                },
                {
                  "x": 1247.0,
                  "y": 652.0
                },
                {
                  "x": 1245.0,
                  "y": 702.0
                },
                {
                  "x": 1118.0,
                  "y": 696.0
                }
              ]
            },
            "confidence": 0.99991,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_008",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 197.0,
              "y": 748.0,
              "width": 859.0,
              "height": 62.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 197.0,
                  "y": 748.0
                },
                {
                  "x": 1056.0,
                  "y": 751.0
                },
                {
                  "x": 1056.0,
                  "y": 810.0
                },
                {
                  "x": 197.0,
                  "y": 807.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_008"
          }
        ],
        "provider": "rapidocr",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "recognizer_language": "latin_digits_ch",
        "latency_ms": 10999.672900012229,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Observed strings, confidence, source-space polygons/boxes and recognizer metadata. Text recognition alone does not locate the physical component represented by a label.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Changes, provenance and possible information loss:** Image → text candidates. Inspect exact source boxes; a correct string can still have a box overlapping diagram geometry.

[Complete stage input/output bundle](stage_data/09_rapid.json)

- [RapidOCRProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00061_RapidOCRProvider.extract/STAGE.html)

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
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
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
            "raw_text": "- = 15 cn",
            "normalized_text": "- = 15 cn",
            "bbox_source_px": {
              "x": 936.0,
              "y": 192.0,
              "width": 202.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 936.0,
                  "y": 192.0
                },
                {
                  "x": 1138.0,
                  "y": 192.0
                },
                {
                  "x": 1138.0,
                  "y": 244.0
                },
                {
                  "x": 936.0,
                  "y": 244.0
                }
              ]
            },
            "confidence": 0.4512488601263927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_001"
          },
          {
            "id": "bn_tok_002",
            "raw_text": "Object",
            "normalized_text": "Object",
            "bbox_source_px": {
              "x": 190.0,
              "y": 224.0,
              "width": 130.0,
              "height": 52.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 190.0,
                  "y": 224.0
                },
                {
                  "x": 320.0,
                  "y": 224.0
                },
                {
                  "x": 320.0,
                  "y": 276.0
                },
                {
                  "x": 190.0,
                  "y": 276.0
                }
              ]
            },
            "confidence": 0.9914211626769536,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_002"
          },
          {
            "id": "bn_tok_003",
            "raw_text": "2F",
            "normalized_text": "2F",
            "bbox_source_px": {
              "x": 105.0,
              "y": 455.0,
              "width": 60.0,
              "height": 40.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 105.0,
                  "y": 455.0
                },
                {
                  "x": 165.0,
                  "y": 455.0
                },
                {
                  "x": 165.0,
                  "y": 495.0
                },
                {
                  "x": 105.0,
                  "y": 495.0
                }
              ]
            },
            "confidence": 0.8996179578342532,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_003"
          },
          {
            "id": "bn_tok_004",
            "raw_text": "2F'",
            "normalized_text": "2F'",
            "bbox_source_px": {
              "x": 1105.0,
              "y": 453.0,
              "width": 60.0,
              "height": 42.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1105.0,
                  "y": 453.0
                },
                {
                  "x": 1165.0,
                  "y": 453.0
                },
                {
                  "x": 1165.0,
                  "y": 495.0
                },
                {
                  "x": 1105.0,
                  "y": 495.0
                }
              ]
            },
            "confidence": 0.44663277239076066,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_004"
          },
          {
            "id": "bn_tok_005",
            "raw_text": "Image",
            "normalized_text": "Image",
            "bbox_source_px": {
              "x": 1119.0,
              "y": 648.0,
              "width": 126.0,
              "height": 54.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1119.0,
                  "y": 648.0
                },
                {
                  "x": 1245.0,
                  "y": 648.0
                },
                {
                  "x": 1245.0,
                  "y": 702.0
                },
                {
                  "x": 1119.0,
                  "y": 702.0
                }
              ]
            },
            "confidence": 0.9998692785481457,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "easyocr_bangla",
            "recognizer_model": "bengali.pth",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_bn_tok_005"
          },
          {
            "id": "bn_tok_006",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": "Fig. 5 Image Formation by a Convex Lens",
            "bbox_source_px": {
              "x": 200.0,
              "y": 753.0,
              "width": 854.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 200.0,
                  "y": 753.0
                },
                {
                  "x": 1054.0,
                  "y": 753.0
                },
                {
                  "x": 1054.0,
                  "y": 810.0
                },
                {
                  "x": 200.0,
                  "y": 810.0
                }
              ]
            },
            "confidence": 0.4902960533785318,
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
        "latency_ms": 22904.142000013962,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Independent text alternatives with confidence and source positions; uncertain alternatives should not silently overwrite stronger evidence.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Changes, provenance and possible information loss:** Alternative OCR supplies competing evidence. Its errors are distinct from whichever result the router actually selects.

[Complete stage input/output bundle](stage_data/10_easy.json)

- [EasyOCRBanglaProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00116_EasyOCRBanglaProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\bangla.py](contracts/ai/evidence/ocr/bangla.py)

## 11. Symbol candidates, deduplication and final OCR

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** EasyOCR: independent OCR candidates → this component → Grayscale, blur and edge extraction.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 11,
  "first_8_records": [
    {
      "call": "00060_MultiOCRRouter.extract",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
          "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
        },
        "source_width": 1280,
        "source_height": 960,
        "region": null
      }
    },
    {
      "call": "00169_deduplicate_spatial_tokens",
      "value": {
        "tokens": [
          {
            "id": "ocr_tok_001",
            "raw_text": "f = 15 cm",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 933.0,
              "y": 189.0,
              "width": 208.0,
              "height": 55.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 933.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 244.0
                },
                {
                  "x": 933.0,
                  "y": 244.0
                }
              ]
            },
            "confidence": 0.96641,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "- = 15 cn",
                "script": "latin",
                "confidence": 0.4512488601263927,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "Object",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 188.0,
              "y": 220.0,
              "width": 135.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 189.0,
                  "y": 220.0
                },
                {
                  "x": 323.0,
                  "y": 223.0
                },
                {
                  "x": 322.0,
                  "y": 277.0
                },
                {
                  "x": 188.0,
                  "y": 274.0
                }
              ]
            },
            "confidence": 0.9999,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Object",
                "script": "latin",
                "confidence": 0.9914211626769536,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 102.0,
              "y": 449.0,
              "width": 70.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 102.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 500.0
                },
                {
                  "x": 102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99964,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F",
                "script": "latin",
                "confidence": 0.8996179578342532,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 356.0,
              "y": 451.0,
              "width": 42.0,
              "height": 47.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 361.0,
                  "y": 451.0
                },
                {
                  "x": 398.0,
                  "y": 455.0
                },
                {
                  "x": 393.0,
                  "y": 498.0
                },
                {
                  "x": 356.0,
                  "y": 494.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 849.0,
              "y": 449.0,
              "width": 38.0,
              "height": 43.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 849.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 492.0
                },
                {
                  "x": 849.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.9994,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1102.0,
              "y": 449.0,
              "width": 69.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1102.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 500.0
                },
                {
                  "x": 1102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99972,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F'",
                "script": "latin",
                "confidence": 0.44663277239076066,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Image",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1118.0,
              "y": 646.0,
              "width": 129.0,
              "height": 56.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1120.0,
                  "y": 646.0
                },
                {
                  "x": 1247.0,
                  "y": 652.0
                },
                {
                  "x": 1245.0,
                  "y": 702.0
                },
                {
                  "x": 1118.0,
                  "y": 696.0
                }
              ]
            },
            "confidence": 0.99991,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Image",
                "script": "latin",
                "confidence": 0.9998692785481457,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_008",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 197.0,
              "y": 748.0,
              "width": 859.0,
              "height": 62.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 197.0,
                  "y": 748.0
                },
                {
                  "x": 1056.0,
                  "y": 751.0
                },
                {
                  "x": 1056.0,
                  "y": 810.0
                },
                {
                  "x": 197.0,
                  "y": 807.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig. 5 Image Formation by a Convex Lens",
                "script": "latin",
                "confidence": 0.4902960533785318,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_008"
          }
        ]
      }
    },
    {
      "call": "00178_GreekSymbolVisualOCR.extract_symbols",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
          "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
        },
        "existing_tokens": [
          {
            "id": "ocr_tok_008",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 197.0,
              "y": 748.0,
              "width": 859.0,
              "height": 62.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 197.0,
                  "y": 748.0
                },
                {
                  "x": 1056.0,
                  "y": 751.0
                },
                {
                  "x": 1056.0,
                  "y": 810.0
                },
                {
                  "x": 197.0,
                  "y": 807.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig. 5 Image Formation by a Convex Lens",
                "script": "latin",
                "confidence": 0.4902960533785318,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_008"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "f = 15 cm",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 933.0,
              "y": 189.0,
              "width": 208.0,
              "height": 55.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 933.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 244.0
                },
                {
                  "x": 933.0,
                  "y": 244.0
                }
              ]
            },
            "confidence": 0.96641,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "- = 15 cn",
                "script": "latin",
                "confidence": 0.4512488601263927,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "Object",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 188.0,
              "y": 220.0,
              "width": 135.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 189.0,
                  "y": 220.0
                },
                {
                  "x": 323.0,
                  "y": 223.0
                },
                {
                  "x": 322.0,
                  "y": 277.0
                },
                {
                  "x": 188.0,
                  "y": 274.0
                }
              ]
            },
            "confidence": 0.9999,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Object",
                "script": "latin",
                "confidence": 0.9914211626769536,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Image",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1118.0,
              "y": 646.0,
              "width": 129.0,
              "height": 56.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1120.0,
                  "y": 646.0
                },
                {
                  "x": 1247.0,
                  "y": 652.0
                },
                {
                  "x": 1245.0,
                  "y": 702.0
                },
                {
                  "x": 1118.0,
                  "y": 696.0
                }
              ]
            },
            "confidence": 0.99991,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Image",
                "script": "latin",
                "confidence": 0.9998692785481457,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 102.0,
              "y": 449.0,
              "width": 70.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 102.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 500.0
                },
                {
                  "x": 102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99964,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F",
                "script": "latin",
                "confidence": 0.8996179578342532,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1102.0,
              "y": 449.0,
              "width": 69.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1102.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 500.0
                },
                {
                  "x": 1102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99972,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F'",
                "script": "latin",
                "confidence": 0.44663277239076066,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 356.0,
              "y": 451.0,
              "width": 42.0,
              "height": 47.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 361.0,
                  "y": 451.0
                },
                {
                  "x": 398.0,
                  "y": 455.0
                },
                {
                  "x": 393.0,
                  "y": 498.0
                },
                {
                  "x": 356.0,
                  "y": 494.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 849.0,
              "y": 449.0,
              "width": 38.0,
              "height": 43.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 849.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 492.0
                },
                {
                  "x": 849.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.9994,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          }
        ],
        "source_width": 1280,
        "source_height": 960
      }
    },
    {
      "call": "00179_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_008",
          "raw_text": "Fig. 5 Image Formation by a Convex Lens",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 197.0,
            "y": 748.0,
            "width": 859.0,
            "height": 62.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 197.0,
                "y": 748.0
              },
              {
                "x": 1056.0,
                "y": 751.0
              },
              {
                "x": 1056.0,
                "y": 810.0
              },
              {
                "x": 197.0,
                "y": 807.0
              }
            ]
          },
          "confidence": 0.99927,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig. 5 Image Formation by a Convex Lens",
              "script": "latin",
              "confidence": 0.4902960533785318,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_008"
        }
      }
    },
    {
      "call": "00181_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_001",
          "raw_text": "f = 15 cm",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 933.0,
            "y": 189.0,
            "width": 208.0,
            "height": 55.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 933.0,
                "y": 189.0
              },
              {
                "x": 1141.0,
                "y": 189.0
              },
              {
                "x": 1141.0,
                "y": 244.0
              },
              {
                "x": 933.0,
                "y": 244.0
              }
            ]
          },
          "confidence": 0.96641,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "- = 15 cn",
              "script": "latin",
              "confidence": 0.4512488601263927,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        }
      }
    },
    {
      "call": "00183_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_002",
          "raw_text": "Object",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 188.0,
            "y": 220.0,
            "width": 135.0,
            "height": 57.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 189.0,
                "y": 220.0
              },
              {
                "x": 323.0,
                "y": 223.0
              },
              {
                "x": 322.0,
                "y": 277.0
              },
              {
                "x": 188.0,
                "y": 274.0
              }
            ]
          },
          "confidence": 0.9999,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Object",
              "script": "latin",
              "confidence": 0.9914211626769536,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      }
    },
    {
      "call": "00185_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_007",
          "raw_text": "Image",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1118.0,
            "y": 646.0,
            "width": 129.0,
            "height": 56.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1120.0,
                "y": 646.0
              },
              {
                "x": 1247.0,
                "y": 652.0
              },
              {
                "x": 1245.0,
                "y": 702.0
              },
              {
                "x": 1118.0,
                "y": 696.0
              }
            ]
          },
          "confidence": 0.99991,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Image",
              "script": "latin",
              "confidence": 0.9998692785481457,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_007"
        }
      }
    },
    {
      "call": "00187_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_003",
          "raw_text": "2F",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 102.0,
            "y": 449.0,
            "width": 70.0,
            "height": 51.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 102.0,
                "y": 449.0
              },
              {
                "x": 172.0,
                "y": 449.0
              },
              {
                "x": 172.0,
                "y": 500.0
              },
              {
                "x": 102.0,
                "y": 500.0
              }
            ]
          },
          "confidence": 0.99964,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "2F",
              "script": "latin",
              "confidence": 0.8996179578342532,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
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
    "count": 11,
    "first_8_records": [
      {
        "call": "00060_MultiOCRRouter.extract",
        "return_value": {
          "status": "success",
          "tokens": [
            {
              "id": "ocr_tok_008",
              "raw_text": "Fig. 5 Image Formation by a Convex Lens",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 197.0,
                "y": 748.0,
                "width": 859.0,
                "height": 62.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 197.0,
                    "y": 748.0
                  },
                  {
                    "x": 1056.0,
                    "y": 751.0
                  },
                  {
                    "x": 1056.0,
                    "y": 810.0
                  },
                  {
                    "x": 197.0,
                    "y": 807.0
                  }
                ]
              },
              "confidence": 0.99927,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Fig. 5 Image Formation by a Convex Lens",
                  "script": "latin",
                  "confidence": 0.4902960533785318,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            },
            {
              "id": "ocr_tok_001",
              "raw_text": "f = 15 cm",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 933.0,
                "y": 189.0,
                "width": 208.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 933.0,
                    "y": 189.0
                  },
                  {
                    "x": 1141.0,
                    "y": 189.0
                  },
                  {
                    "x": 1141.0,
                    "y": 244.0
                  },
                  {
                    "x": 933.0,
                    "y": 244.0
                  }
                ]
              },
              "confidence": 0.96641,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "- = 15 cn",
                  "script": "latin",
                  "confidence": 0.4512488601263927,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "Object",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 188.0,
                "y": 220.0,
                "width": 135.0,
                "height": 57.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 189.0,
                    "y": 220.0
                  },
                  {
                    "x": 323.0,
                    "y": 223.0
                  },
                  {
                    "x": 322.0,
                    "y": 277.0
                  },
                  {
                    "x": 188.0,
                    "y": 274.0
                  }
                ]
              },
              "confidence": 0.9999,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Object",
                  "script": "latin",
                  "confidence": 0.9914211626769536,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            },
            {
              "id": "ocr_tok_007",
              "raw_text": "Image",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1118.0,
                "y": 646.0,
                "width": 129.0,
                "height": 56.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1120.0,
                    "y": 646.0
                  },
                  {
                    "x": 1247.0,
                    "y": 652.0
                  },
                  {
                    "x": 1245.0,
                    "y": 702.0
                  },
                  {
                    "x": 1118.0,
                    "y": 696.0
                  }
                ]
              },
              "confidence": 0.99991,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Image",
                  "script": "latin",
                  "confidence": 0.9998692785481457,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_007"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "2F",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 102.0,
                "y": 449.0,
                "width": 70.0,
                "height": 51.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 102.0,
                    "y": 449.0
                  },
                  {
                    "x": 172.0,
                    "y": 449.0
                  },
                  {
                    "x": 172.0,
                    "y": 500.0
                  },
                  {
                    "x": 102.0,
                    "y": 500.0
                  }
                ]
              },
              "confidence": 0.99964,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "2F",
                  "script": "latin",
                  "confidence": 0.8996179578342532,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "2F",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1102.0,
                "y": 449.0,
                "width": 69.0,
                "height": 51.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1102.0,
                    "y": 449.0
                  },
                  {
                    "x": 1171.0,
                    "y": 449.0
                  },
                  {
                    "x": 1171.0,
                    "y": 500.0
                  },
                  {
                    "x": 1102.0,
                    "y": 500.0
                  }
                ]
              },
              "confidence": 0.99972,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "2F'",
                  "script": "latin",
                  "confidence": 0.44663277239076066,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_004",
              "raw_text": "F",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 356.0,
                "y": 451.0,
                "width": 42.0,
                "height": 47.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 361.0,
                    "y": 451.0
                  },
                  {
                    "x": 398.0,
                    "y": 455.0
                  },
                  {
                    "x": 393.0,
                    "y": 498.0
                  },
                  {
                    "x": 356.0,
                    "y": 494.0
                  }
                ]
              },
              "confidence": 0.99927,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_004"
            },
            {
              "id": "ocr_tok_005",
              "raw_text": "F",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 849.0,
                "y": 449.0,
                "width": 38.0,
                "height": 43.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 849.0,
                    "y": 449.0
                  },
                  {
                    "x": 887.0,
                    "y": 449.0
                  },
                  {
                    "x": 887.0,
                    "y": 492.0
                  },
                  {
                    "x": 849.0,
                    "y": 492.0
                  }
                ]
              },
              "confidence": 0.9994,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_005"
            }
          ],
          "provider": "multi_ocr_router",
          "model": "PP-OCRv6-onnx",
          "package": "rapidocr+easyocr+greek_ocr",
          "package_version": "3.9.2",
          "detector_model": "PP-OCRv6_det_small.onnx",
          "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
          "recognizer_language": "en+bn+el",
          "latency_ms": 35514.12680000067,
          "error": null,
          "metadata": {
            "bangla_available": true,
            "greek_available": true,
            "formula_available": false,
            "regions_count": 8,
            "token_count": 8
          }
        }
      },
      {
        "call": "00169_deduplicate_spatial_tokens",
        "return_value": [
          {
            "id": "ocr_tok_008",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 197.0,
              "y": 748.0,
              "width": 859.0,
              "height": 62.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 197.0,
                  "y": 748.0
                },
                {
                  "x": 1056.0,
                  "y": 751.0
                },
                {
                  "x": 1056.0,
                  "y": 810.0
                },
                {
                  "x": 197.0,
                  "y": 807.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig. 5 Image Formation by a Convex Lens",
                "script": "latin",
                "confidence": 0.4902960533785318,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_008"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "f = 15 cm",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 933.0,
              "y": 189.0,
              "width": 208.0,
              "height": 55.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 933.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 189.0
                },
                {
                  "x": 1141.0,
                  "y": 244.0
                },
                {
                  "x": 933.0,
                  "y": 244.0
                }
              ]
            },
            "confidence": 0.96641,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "- = 15 cn",
                "script": "latin",
                "confidence": 0.4512488601263927,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "Object",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 188.0,
              "y": 220.0,
              "width": 135.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 189.0,
                  "y": 220.0
                },
                {
                  "x": 323.0,
                  "y": 223.0
                },
                {
                  "x": 322.0,
                  "y": 277.0
                },
                {
                  "x": 188.0,
                  "y": 274.0
                }
              ]
            },
            "confidence": 0.9999,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Object",
                "script": "latin",
                "confidence": 0.9914211626769536,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Image",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1118.0,
              "y": 646.0,
              "width": 129.0,
              "height": 56.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1120.0,
                  "y": 646.0
                },
                {
                  "x": 1247.0,
                  "y": 652.0
                },
                {
                  "x": 1245.0,
                  "y": 702.0
                },
                {
                  "x": 1118.0,
                  "y": 696.0
                }
              ]
            },
            "confidence": 0.99991,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Image",
                "script": "latin",
                "confidence": 0.9998692785481457,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 102.0,
              "y": 449.0,
              "width": 70.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 102.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 449.0
                },
                {
                  "x": 172.0,
                  "y": 500.0
                },
                {
                  "x": 102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99964,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F",
                "script": "latin",
                "confidence": 0.8996179578342532,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1102.0,
              "y": 449.0,
              "width": 69.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 1102.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 449.0
                },
                {
                  "x": 1171.0,
                  "y": 500.0
                },
                {
                  "x": 1102.0,
                  "y": 500.0
                }
              ]
            },
            "confidence": 0.99972,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F'",
                "script": "latin",
                "confidence": 0.44663277239076066,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 356.0,
              "y": 451.0,
              "width": 42.0,
              "height": 47.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 361.0,
                  "y": 451.0
                },
                {
                  "x": 398.0,
                  "y": 455.0
                },
                {
                  "x": 393.0,
                  "y": 498.0
                },
                {
                  "x": 356.0,
                  "y": 494.0
                }
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 849.0,
              "y": 449.0,
              "width": 38.0,
              "height": 43.0
            },
            "polygon_source_px": {
              "points": [
                {
                  "x": 849.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 449.0
                },
                {
                  "x": 887.0,
                  "y": 492.0
                },
                {
                  "x": 849.0,
                  "y": 492.0
                }
              ]
            },
            "confidence": 0.9994,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          }
        ]
      },
      {
        "call": "00178_GreekSymbolVisualOCR.extract_symbols",
        "return_value": []
      },
      {
        "call": "00179_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_008",
          "raw_text": "Fig. 5 Image Formation by a Convex Lens",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 197.0,
            "y": 748.0,
            "width": 859.0,
            "height": 62.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 197.0,
                "y": 748.0
              },
              {
                "x": 1056.0,
                "y": 751.0
              },
              {
                "x": 1056.0,
                "y": 810.0
              },
              {
                "x": 197.0,
                "y": 807.0
              }
            ]
          },
          "confidence": 0.99927,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig. 5 Image Formation by a Convex Lens",
              "script": "latin",
              "confidence": 0.4902960533785318,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_008"
        }
      },
      {
        "call": "00181_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_001",
          "raw_text": "f = 15 cm",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 933.0,
            "y": 189.0,
            "width": 208.0,
            "height": 55.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 933.0,
                "y": 189.0
              },
              {
                "x": 1141.0,
                "y": 189.0
              },
              {
                "x": 1141.0,
                "y": 244.0
              },
              {
                "x": 933.0,
                "y": 244.0
              }
            ]
          },
          "confidence": 0.96641,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "- = 15 cn",
              "script": "latin",
              "confidence": 0.4512488601263927,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_001"
        }
      },
      {
        "call": "00183_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_002",
          "raw_text": "Object",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 188.0,
            "y": 220.0,
            "width": 135.0,
            "height": 57.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 189.0,
                "y": 220.0
              },
              {
                "x": 323.0,
                "y": 223.0
              },
              {
                "x": 322.0,
                "y": 277.0
              },
              {
                "x": 188.0,
                "y": 274.0
              }
            ]
          },
          "confidence": 0.9999,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Object",
              "script": "latin",
              "confidence": 0.9914211626769536,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_002"
        }
      },
      {
        "call": "00185_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_007",
          "raw_text": "Image",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1118.0,
            "y": 646.0,
            "width": 129.0,
            "height": 56.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1120.0,
                "y": 646.0
              },
              {
                "x": 1247.0,
                "y": 652.0
              },
              {
                "x": 1245.0,
                "y": 702.0
              },
              {
                "x": 1118.0,
                "y": 696.0
              }
            ]
          },
          "confidence": 0.99991,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Image",
              "script": "latin",
              "confidence": 0.9998692785481457,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_007"
        }
      },
      {
        "call": "00187_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_003",
          "raw_text": "2F",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 102.0,
            "y": 449.0,
            "width": 70.0,
            "height": 51.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 102.0,
                "y": 449.0
              },
              {
                "x": 172.0,
                "y": 449.0
              },
              {
                "x": 172.0,
                "y": 500.0
              },
              {
                "x": 102.0,
                "y": 500.0
              }
            ]
          },
          "confidence": 0.99964,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "2F",
              "script": "latin",
              "confidence": 0.8996179578342532,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        }
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Merged tokens with retained provenance/alternatives. Preserve literal printed values and symbolic quantities. Do not turn L or m into a numerical length or mass.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Changes, provenance and possible information loss:** OCR alternatives → selected token set. PageIR text blocks are filled from these tokens inside the evidence pipeline.

[Complete stage input/output bundle](stage_data/11_ocr.json)

- [MultiOCRRouter.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00060_MultiOCRRouter.extract/STAGE.html)

- [deduplicate_spatial_tokens — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00169_deduplicate_spatial_tokens/STAGE.html)

- [GreekSymbolVisualOCR.extract_symbols — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00178_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00179_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00181_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00183_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00185_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00187_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00189_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00191_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00193_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [Code: ai\evidence\ocr\router.py](contracts/ai/evidence/ocr/router.py)

- [Code: ai\evidence\ocr\greek_symbols.py](contracts/ai/evidence/ocr/greek_symbols.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00060_MultiOCRRouter.extract/actual_overlay_on_source.png)

## 12. Grayscale, blur and edge extraction

**Execution:** EXECUTED. **Verdict:** FRAME PASS / LOSSY PROCESSING.

**Upstream → downstream:** Symbol candidates, deduplication and final OCR → this component → OCR-region suppression before geometry detection.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00202_preprocess_diagram",
    "value": {
      "img_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
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
      "call": "00202_preprocess_diagram",
      "return_value": [
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\01aaa62c2cb5f718906a9b5c457d9a627ef90114f4015e33af095429712318be.npy",
          "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\01aaa62c2cb5f718906a9b5c457d9a627ef90114f4015e33af095429712318be.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\049e9b702cc424677029d5e76feea0a9fc1b4b1c083698c4b84f7b62aafc55ad.npy",
          "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\049e9b702cc424677029d5e76feea0a9fc1b4b1c083698c4b84f7b62aafc55ad.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.npy",
          "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png"
        }
      ]
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Grayscale/blur/edge arrays in the same 1280×960 source frame. Image processing may change intensities, but must not imply a spatial crop/scale that was not performed.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Arrays preserve the source frame. Blur and Canny change image information; no detector correctness is inferred from shape alone.

**Changes, provenance and possible information loss:** Color/intensity information becomes an edge representation. Exact arrays are retained. OpenCV internal per-operation frames were not separately profiled.

[Complete stage input/output bundle](stage_data/12_pre.json)

- [preprocess_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00202_preprocess_diagram/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png)

![01aaa62c2cb5f718906a9b5c457d9a627ef90114f4015e33af095429712318be.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/01aaa62c2cb5f718906a9b5c457d9a627ef90114f4015e33af095429712318be.png)

![049e9b702cc424677029d5e76feea0a9fc1b4b1c083698c4b84f7b62aafc55ad.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/049e9b702cc424677029d5e76feea0a9fc1b4b1c083698c4b84f7b62aafc55ad.png)

![a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png)

## 13. OCR-region suppression before geometry detection

**Execution:** EXECUTED. **Verdict:** FAIL — FIRST PROVEN GEOMETRY LOSS.

**Upstream → downstream:** Grayscale, blur and edge extraction → this component → Domain CV: raw candidates → selected geometry.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00203_mask_out_text_regions",
    "value": {
      "edge_map": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png"
      },
      "ocr_boxes": [
        {
          "x": 197.0,
          "y": 748.0,
          "width": 859.0,
          "height": 62.0
        },
        {
          "x": 933.0,
          "y": 189.0,
          "width": 208.0,
          "height": 55.0
        },
        {
          "x": 188.0,
          "y": 220.0,
          "width": 135.0,
          "height": 57.0
        },
        {
          "x": 1118.0,
          "y": 646.0,
          "width": 129.0,
          "height": 56.0
        },
        {
          "x": 102.0,
          "y": 449.0,
          "width": 70.0,
          "height": 51.0
        },
        {
          "x": 1102.0,
          "y": 449.0,
          "width": 69.0,
          "height": 51.0
        },
        {
          "x": 356.0,
          "y": 451.0,
          "width": 42.0,
          "height": 47.0
        },
        {
          "x": 849.0,
          "y": 449.0,
          "width": 38.0,
          "height": 43.0
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
      "call": "00203_mask_out_text_regions",
      "return_value": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\2916599985fe98e3c82aa6b5d4ec343475d238d578722f40189e9807bee3d784.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\2916599985fe98e3c82aa6b5d4ec343475d238d578722f40189e9807bee3d784.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** An edge map suppressing text while preserving relevant diagram boundaries/rays. This is the registration requirement; the implementation zeros the entire expanded rectangle without distinguishing text from geometry.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Object OCR bbox=(188,220,135,57); margin=4 removes incident-ray pixels adjacent to the label. The removed-edge overlay proves the loss. Its causal connection to the later missing vertical object arrow is not established.

**Changes, provenance and possible information loss:** Every pixel removed by the actual mask is shown in red on the original. A valid OCR box does not guarantee safe geometry suppression.

[Complete stage input/output bundle](stage_data/13_mask.json)

- [mask_out_text_regions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00203_mask_out_text_regions/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![removed_edges_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00203_mask_out_text_regions/removed_edges_on_source.png)

![a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/a1ae1bea1b315185fe87db837f7e8a71f76b53649db277637adfab3637e77831.png)

![2916599985fe98e3c82aa6b5d4ec343475d238d578722f40189e9807bee3d784.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/arrays/2916599985fe98e3c82aa6b5d4ec343475d238d578722f40189e9807bee3d784.png)

## 14. Domain CV: raw candidates → selected geometry

**Execution:** EXECUTED. **Verdict:** FAIL — PERCEPTION / SELECTION.

**Upstream → downstream:** OCR-region suppression before geometry detection → this component → SAM2 segmentation prompted by CV.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00200_ThinLensCVCandidateExtractor.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.npy",
        "image": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017\\arrays\\d3447de7e1291074a182a287c03b2ba24f9ea882846daa5b885d9c1cccdf32f5.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "ocr_boxes": [
        {
          "x": 197.0,
          "y": 748.0,
          "width": 859.0,
          "height": 62.0
        },
        {
          "x": 933.0,
          "y": 189.0,
          "width": 208.0,
          "height": 55.0
        },
        {
          "x": 188.0,
          "y": 220.0,
          "width": 135.0,
          "height": 57.0
        },
        {
          "x": 1118.0,
          "y": 646.0,
          "width": 129.0,
          "height": 56.0
        },
        {
          "x": 102.0,
          "y": 449.0,
          "width": 70.0,
          "height": 51.0
        },
        {
          "x": 1102.0,
          "y": 449.0,
          "width": 69.0,
          "height": 51.0
        },
        {
          "x": 356.0,
          "y": 451.0,
          "width": 42.0,
          "height": 47.0
        },
        {
          "x": 849.0,
          "y": 449.0,
          "width": 38.0,
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
      "call": "00200_ThinLensCVCandidateExtractor.extract",
      "return_value": {
        "optical_axis": {
          "start": {
            "x": 650.0,
            "y": 432.0
          },
          "end": {
            "x": 1124.0,
            "y": 432.0
          }
        },
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        },
        "lens_line": {
          "start": {
            "x": 641.0,
            "y": 423.0
          },
          "end": {
            "x": 641.0,
            "y": 189.0
          }
        },
        "object_arrow": null,
        "image_arrow": {
          "start": {
            "x": 1176.0,
            "y": 607.0
          },
          "end": {
            "x": 1176.0,
            "y": 432.0
          }
        },
        "all_lines": {
          "count": 13,
          "first_8_records": [
            {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 859.0,
                "y": 432.0
              }
            },
            {
              "start": {
                "x": 880.0,
                "y": 435.0
              },
              "end": {
                "x": 1124.0,
                "y": 435.0
              }
            },
            {
              "start": {
                "x": 635.0,
                "y": 278.0
              },
              "end": {
                "x": 860.0,
                "y": 429.0
              }
            },
            {
              "start": {
                "x": 880.0,
                "y": 438.0
              },
              "end": {
                "x": 1181.0,
                "y": 641.0
              }
            },
            {
              "start": {
                "x": 652.0,
                "y": 435.0
              },
              "end": {
                "x": 949.0,
                "y": 550.0
              }
            },
            {
              "start": {
                "x": 641.0,
                "y": 423.0
              },
              "end": {
                "x": 641.0,
                "y": 189.0
              }
            },
            {
              "start": {
                "x": 638.0,
                "y": 680.0
              },
              "end": {
                "x": 638.0,
                "y": 484.0
              }
            },
            {
              "start": {
                "x": 255.0,
                "y": 281.0
              },
              "end": {
                "x": 451.0,
                "y": 281.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Source-supported candidate lines/circles/polygons and selected geometry, with scores, rejection/selection diagnostics and unresolved ambiguity where evidence is insufficient.

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

**Comparison / debugging conclusion:** Returned lens_center=(641,432), lens_line=(641,423)→(641,189), object_arrow=null. The partial line becomes aperture_height_px=234. The original shows an object arrow and a full lens; the selected overlay exposes this loss.

**Changes, provenance and possible information loss:** Candidate generation and selection are distinct. Compare all_candidates_overlay with selected output; inspect locals for fitted lines, rejected candidates and thresholds.

[Complete stage input/output bundle](stage_data/14_cv.json)

- [ThinLensCVCandidateExtractor.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00200_ThinLensCVCandidateExtractor.extract/STAGE.html)

- [Code: ai\evidence\cv\thin_lens_cv.py](contracts/ai/evidence/cv/thin_lens_cv.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00200_ThinLensCVCandidateExtractor.extract/actual_overlay_on_source.png)

![all_candidates_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00200_ThinLensCVCandidateExtractor.extract/all_candidates_overlay.png)

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

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

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
    "call": "00283_ThinLensGrounder.ground",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
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
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
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
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
        "optical_axis": {
          "start": {
            "x": 650.0,
            "y": 432.0
          },
          "end": {
            "x": 1124.0,
            "y": 432.0
          }
        },
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        },
        "lens_line": {
          "start": {
            "x": 641.0,
            "y": 423.0
          },
          "end": {
            "x": 641.0,
            "y": 189.0
          }
        },
        "object_arrow": null,
        "image_arrow": {
          "start": {
            "x": 1176.0,
            "y": 607.0
          },
          "end": {
            "x": 1176.0,
            "y": 432.0
          }
        },
        "all_lines": {
          "count": 13,
          "first_8_records": [
            {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 859.0,
                "y": 432.0
              }
            },
            {
              "start": {
                "x": 880.0,
                "y": 435.0
              },
              "end": {
                "x": 1124.0,
                "y": 435.0
              }
            },
            {
              "start": {
                "x": 635.0,
                "y": 278.0
              },
              "end": {
                "x": 860.0,
                "y": 429.0
              }
            },
            {
              "start": {
                "x": 880.0,
                "y": 438.0
              },
              "end": {
                "x": 1181.0,
                "y": 641.0
              }
            },
            {
              "start": {
                "x": 652.0,
                "y": 435.0
              },
              "end": {
                "x": 949.0,
                "y": 550.0
              }
            },
            {
              "start": {
                "x": 641.0,
                "y": 423.0
              },
              "end": {
                "x": 641.0,
                "y": 189.0
              }
            },
            {
              "start": {
                "x": 638.0,
                "y": 680.0
              },
              "end": {
                "x": 638.0,
                "y": 484.0
              }
            },
            {
              "start": {
                "x": 255.0,
                "y": 281.0
              },
              "end": {
                "x": 451.0,
                "y": 281.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        }
      },
      "ocr_result": {
        "status": "success",
        "tokens": [
          {
            "id": "ocr_tok_008",
            "raw_text": "Fig. 5 Image Formation by a Convex Lens",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 197.0,
              "y": 748.0,
              "width": 859.0,
              "height": 62.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Fig. 5 Image Formation by a Convex Lens",
                "script": "latin",
                "confidence": 0.4902960533785318,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_008"
          },
          {
            "id": "ocr_tok_001",
            "raw_text": "f = 15 cm",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 933.0,
              "y": 189.0,
              "width": 208.0,
              "height": 55.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.96641,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "- = 15 cn",
                "script": "latin",
                "confidence": 0.4512488601263927,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_001"
          },
          {
            "id": "ocr_tok_002",
            "raw_text": "Object",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 188.0,
              "y": 220.0,
              "width": 135.0,
              "height": 57.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.9999,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Object",
                "script": "latin",
                "confidence": 0.9914211626769536,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_002"
          },
          {
            "id": "ocr_tok_007",
            "raw_text": "Image",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1118.0,
              "y": 646.0,
              "width": 129.0,
              "height": 56.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99991,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "Image",
                "script": "latin",
                "confidence": 0.9998692785481457,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_007"
          },
          {
            "id": "ocr_tok_003",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 102.0,
              "y": 449.0,
              "width": 70.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99964,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F",
                "script": "latin",
                "confidence": 0.8996179578342532,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_003"
          },
          {
            "id": "ocr_tok_006",
            "raw_text": "2F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 1102.0,
              "y": 449.0,
              "width": 69.0,
              "height": 51.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99972,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [
              {
                "text": "2F'",
                "script": "latin",
                "confidence": 0.44663277239076066,
                "provider": "easyocr_bangla"
              }
            ],
            "evidence_ref": "evidence_ocr_ocr_tok_006"
          },
          {
            "id": "ocr_tok_004",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 356.0,
              "y": 451.0,
              "width": 42.0,
              "height": 47.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.99927,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_004"
          },
          {
            "id": "ocr_tok_005",
            "raw_text": "F",
            "normalized_text": null,
            "bbox_source_px": {
              "x": 849.0,
              "y": 449.0,
              "width": 38.0,
              "height": 43.0
            },
            "polygon_source_px": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "confidence": 0.9994,
            "script_candidate": "latin",
            "language_candidate": "en",
            "provider": "rapidocr",
            "recognizer_model": "PP-OCRv6_rec_small.onnx",
            "candidate_alternatives": [],
            "evidence_ref": "evidence_ocr_ocr_tok_005"
          }
        ],
        "provider": "multi_ocr_router",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr+easyocr+greek_ocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
        "recognizer_language": "en+bn+el",
        "latency_ms": 35514.12680000067,
        "error": null,
        "metadata": {
          "bangla_available": true,
          "greek_available": true,
          "formula_available": false,
          "regions_count": 8,
          "token_count": 8
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
      "call": "00283_ThinLensGrounder.ground",
      "return_value": {
        "grounded_book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            }
          },
          "resolutions": {},
          "assumptions": [],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
            "entity_id": "lens_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "checks": {
              "lens_center": {
                "x": 641.0,
                "y": 432.0
              }
            },
            "conflicts": [],
            "notes": "Lens center grounded at axis-vertical intersection."
          },
          {
            "entity_id": "axis_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "checks": {
              "axis_y": 432.0
            },
            "conflicts": [],
            "notes": "Principal optical axis grounded."
          },
          {
            "entity_id": "object_1",
            "grounding_state": "unresolved",
            "supporting_evidence": [],
            "checks": {},
            "conflicts": [],
            "notes": "Object arrow not detected."
          }
        ],
        "new_evidence_records": {
          "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750": {
            "id": "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750",
            "method": "classical_cv",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": null,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "thin_lens_cv_extractor",
            "model": null,
            "version": null,
            "payload": {
              "has_optical_axis": true,
              "has_lens_center": true,
              "has_object_arrow": false
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_008": {
            "id": "ev_ocr_ocr_tok_008",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.99927,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Fig. 5 Image Formation by a Convex Lens",
              "bbox": {
                "x": 197.0,
                "y": 748.0,
                "width": 859.0,
                "height": 62.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_001": {
            "id": "ev_ocr_ocr_tok_001",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.96641,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "f = 15 cm",
              "bbox": {
                "x": 933.0,
                "y": 189.0,
                "width": 208.0,
                "height": 55.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_002": {
            "id": "ev_ocr_ocr_tok_002",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.9999,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Object",
              "bbox": {
                "x": 188.0,
                "y": 220.0,
                "width": 135.0,
                "height": 57.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_007": {
            "id": "ev_ocr_ocr_tok_007",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.99991,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Image",
              "bbox": {
                "x": 1118.0,
                "y": 646.0,
                "width": 129.0,
                "height": 56.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_003": {
            "id": "ev_ocr_ocr_tok_003",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.99964,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "2F",
              "bbox": {
                "x": 102.0,
                "y": 449.0,
                "width": 70.0,
                "height": 51.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_006": {
            "id": "ev_ocr_ocr_tok_006",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.99972,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "2F",
              "bbox": {
                "x": 1102.0,
                "y": 449.0,
                "width": 69.0,
                "height": 51.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_004": {
            "id": "ev_ocr_ocr_tok_004",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.99927,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "F",
              "bbox": {
                "x": 356.0,
                "y": 451.0,
                "width": 42.0,
                "height": 47.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_005": {
            "id": "ev_ocr_ocr_tok_005",
            "method": "ocr",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
            "figure_id": "figure_001",
            "confidence": 0.9994,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "F",
              "bbox": {
                "x": 849.0,
                "y": 449.0,
                "width": 38.0,
                "height": 43.0
              }
            },
            "metadata": {}
          }
        },
        "candidate_parameters": [
          {
            "raw_text": "f = 15 cm",
            "numeric_value": 15.0,
            "raw_unit": "cm",
            "canonical_unit": "cm",
            "quantity_candidate": "focal_length",
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.96641
          },
          {
            "raw_text": "- = 15 cn",
            "numeric_value": 15.0,
            "raw_unit": "cn",
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.87
          },
          {
            "raw_text": "2F",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "two_f_symbol",
            "source_ocr_token_id": "ocr_tok_003",
            "confidence": 0.99964
          },
          {
            "raw_text": "2F",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "two_f_symbol",
            "source_ocr_token_id": "ocr_tok_006",
            "confidence": 0.99972
          },
          {
            "raw_text": "F",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "focal_or_force_symbol",
            "source_ocr_token_id": "ocr_tok_004",
            "confidence": 0.99927
          },
          {
            "raw_text": "F",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "focal_or_force_symbol",
            "source_ocr_token_id": "ocr_tok_005",
            "confidence": 0.9994
          }
        ],
        "parameter_associations": [
          {
            "candidate_id": "assoc_f_ocr_tok_001",
            "target_entity_id": "lens_1",
            "target_quantity": "focal_length",
            "value": 15.0,
            "unit": "cm",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_001"
            ],
            "association_checks": {
              "explicit_label": true
            },
            "confidence": 0.96641,
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

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

**Comparison / debugging conclusion:** Grounder retains the center/partial aperture and observes focal_length=0.15 m from OCR, but does not ground the object or printed focal-marker spacing.

**Changes, provenance and possible information loss:** This is where semantic roles become authoritative source coordinates. Inspect grounded_book_ir, diagnostics, candidate_parameters and associations separately.

[Complete stage input/output bundle](stage_data/16_ground.json)

- [ThinLensGrounder.ground — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00283_ThinLensGrounder.ground/STAGE.html)

- [Code: ai\evidence\grounding\thin_lens.py](contracts/ai/evidence/grounding/thin_lens.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00283_ThinLensGrounder.ground/actual_overlay_on_source.png)

## 17. Grounded BookIR and OCR-enriched PageIR

**Execution:** EXECUTED. **Verdict:** FAIL / UPSTREAM DAMAGE PROPAGATES.

**Upstream → downstream:** Semantic-to-spatial grounding and parameter binding → this component → Enforce authoritative source dimensions.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00052_EvidenceExtractionPipeline.extract_and_fuse",
    "value": {
      "asset": {
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
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
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
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
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00052_EvidenceExtractionPipeline.extract_and_fuse",
      "return_value": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.85,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            }
          },
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_001"
              ],
              "confidence": 0.96641,
              "notes": "",
              "policy_id": null,
              "policy_version": null,
              "user_accepted": null,
              "superseded_value": null,
              "derived_from": [
                "ev_ocr_ocr_tok_001"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00052_EvidenceExtractionPipeline.extract_and_fuse",
      "page_ir_after": {
        "version": "1.0",
        "source": {
          "assetId": "dd013d21b8704bd296afcc9dcbc6a750",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_dd013d21.jpg",
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
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
            "id": "ocr_tok_008",
            "text": "Fig. 5 Image Formation by a Convex Lens",
            "x": 197.0,
            "y": 748.0,
            "width": 859.0,
            "height": 62.0,
            "confidence": 0.99927,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_001",
            "text": "f = 15 cm",
            "x": 933.0,
            "y": 189.0,
            "width": 208.0,
            "height": 55.0,
            "confidence": 0.96641,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_002",
            "text": "Object",
            "x": 188.0,
            "y": 220.0,
            "width": 135.0,
            "height": 57.0,
            "confidence": 0.9999,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_007",
            "text": "Image",
            "x": 1118.0,
            "y": 646.0,
            "width": 129.0,
            "height": 56.0,
            "confidence": 0.99991,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_003",
            "text": "2F",
            "x": 102.0,
            "y": 449.0,
            "width": 70.0,
            "height": 51.0,
            "confidence": 0.99964,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_006",
            "text": "2F",
            "x": 1102.0,
            "y": 449.0,
            "width": 69.0,
            "height": 51.0,
            "confidence": 0.99972,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_004",
            "text": "F",
            "x": 356.0,
            "y": 451.0,
            "width": 42.0,
            "height": 47.0,
            "confidence": 0.99927,
            "extraction_method": "ocr"
          },
          {
            "id": "ocr_tok_005",
            "text": "F",
            "x": 849.0,
            "y": 449.0,
            "width": 38.0,
            "height": 43.0,
            "confidence": 0.9994,
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

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

**Comparison / debugging conclusion:** Grounder retains the center/partial aperture and observes focal_length=0.15 m from OCR, but does not ground the object or printed focal-marker spacing.

**Changes, provenance and possible information loss:** The wrapper returns after stages 8–16. Its entry record comes earlier in the profiler, but its output belongs here in the data-flow story.

[Complete stage input/output bundle](stage_data/17_fused.json)

- [EvidenceExtractionPipeline.extract_and_fuse — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00052_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- [Code: ai\evidence\pipeline.py](contracts/ai/evidence/pipeline.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00052_EvidenceExtractionPipeline.extract_and_fuse/actual_overlay_on_source.png)

## 18. Enforce authoritative source dimensions

**Execution:** EXECUTED. **Verdict:** FRAME PASS; GEOMETRY STILL WRONG.

**Upstream → downstream:** Grounded BookIR and OCR-enriched PageIR → this component → Automatic resolution and explicit policy values.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00305_enforce_source_dimensions",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
        "id": "dd013d21b8704bd296afcc9dcbc6a750",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-36 (2).jpg",
        "byte_size": 51136,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_dd013d21.jpg"
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
      "call": "00305_enforce_source_dimensions",
      "return_value": null
    }
  ],
  "in_place_outputs": [
    {
      "call": "00305_enforce_source_dimensions",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Source extent is enforced without correcting the already incorrect landmark/topology evidence.

**Changes, provenance and possible information loss:** Metadata enforcement is not geometric validation. Mutation is recorded in locals_after when the function returns None.

[Complete stage input/output bundle](stage_data/18_dimensions.json)

- [enforce_source_dimensions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00305_enforce_source_dimensions/STAGE.html)

- [Code: ai\ingestion\source_dimensions.py](contracts/ai/ingestion/source_dimensions.py)

## 19. Automatic resolution and explicit policy values

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Enforce authoritative source dimensions → this component → Resolution decisions, units and calibration.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00306_AutoResolutionEngine.resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          }
        },
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00306_AutoResolutionEngine.resolve",
      "return_value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "failures": [],
        "readiness": {
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "ready": true,
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "lens_center",
            "focal_length_px",
            "aperture_height_px"
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** _normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace.

**Changes, provenance and possible information loss:** Inspect field_changes.json for every addition/replacement. Auto-policy execution in this checkout may satisfy requirements without a human decision; that is observed behavior, not approval supplied during tracing.

[Complete stage input/output bundle](stage_data/19_auto.json)

- [AutoResolutionEngine.resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00306_AutoResolutionEngine.resolve/STAGE.html)

- [Every changed field before/after](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00306_AutoResolutionEngine.resolve/field_changes.json)

- [Code: ai\resolution\auto.py](contracts/ai/resolution/auto.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00306_AutoResolutionEngine.resolve/actual_overlay_on_source.png)

## 20. Resolution decisions, units and calibration

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Automatic resolution and explicit policy values → this component → Requirement and ambiguity analysis.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00343_ResolutionEngine.auto_resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
    "call": "00345_CalibrationEngine.derive_for_subtype",
    "value": {
      "subtype": "thin_lens",
      "entities": [
        {
          "id": "lens_1",
          "type": "lens",
          "label": "convex lens",
          "position_source_px": {
            "x": 641.0,
            "y": 432.0,
            "coordinate_space": "source_px",
            "method": "cv_lens_center"
          },
          "geometry": null,
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
          ]
        },
        {
          "id": "object_1",
          "type": "object",
          "label": "Object",
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
          "id": "image_1",
          "type": "image",
          "label": "Image",
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
          "id": "axis_1",
          "type": "optical_axis",
          "label": "principal axis",
          "position_source_px": null,
          "geometry": {
            "start": {
              "x": 650.0,
              "y": 432.0
            },
            "end": {
              "x": 1124.0,
              "y": 432.0
            },
            "length_px": 474.0
          },
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
          ]
        },
        {
          "id": "focal_point_1",
          "type": "focal_point",
          "label": "F",
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
          "id": "focal_point_2",
          "type": "focal_point",
          "label": "2F",
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
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        },
        "aperture_height_px": {
          "value": 234.0,
          "unit": "px",
          "status": "observed",
          "provenance": {
            "source": "diagram_measurement",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.85,
            "notes": "",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "focal_length": {
          "value": 0.15,
          "unit": "m",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.96641,
            "notes": "",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "ev_ocr_ocr_tok_001"
            ]
          }
        },
        "focal_length_px": {
          "value": 117.0,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "policy_id": "policy_normalized_lens_focal_ratio",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "objectDistance": {
          "value": 234.0,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "policy_id": "policy_normalized_lens_object_distance",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "object_height_px": {
          "value": 81.89999999999999,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "policy_id": "policy_normalized_lens_object_height",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        }
      },
      "resolutions": {},
      "geometry": {
        "width": 1280,
        "height": 960,
        "coordinate_space": "source_px",
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        }
      }
    }
  },
  {
    "call": "00356_CalibrationEngine.derive_for_subtype",
    "value": {
      "subtype": "thin_lens",
      "entities": [
        {
          "id": "lens_1",
          "type": "lens",
          "label": "convex lens",
          "position_source_px": {
            "x": 641.0,
            "y": 432.0,
            "coordinate_space": "source_px",
            "method": "cv_lens_center"
          },
          "geometry": null,
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
          ]
        },
        {
          "id": "object_1",
          "type": "object",
          "label": "Object",
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
          "id": "image_1",
          "type": "image",
          "label": "Image",
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
          "id": "axis_1",
          "type": "optical_axis",
          "label": "principal axis",
          "position_source_px": null,
          "geometry": {
            "start": {
              "x": 650.0,
              "y": 432.0
            },
            "end": {
              "x": 1124.0,
              "y": 432.0
            },
            "length_px": 474.0
          },
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
          ]
        },
        {
          "id": "focal_point_1",
          "type": "focal_point",
          "label": "F",
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
          "id": "focal_point_2",
          "type": "focal_point",
          "label": "2F",
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
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        },
        "aperture_height_px": {
          "value": 234.0,
          "unit": "px",
          "status": "observed",
          "provenance": {
            "source": "diagram_measurement",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.85,
            "notes": "",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "focal_length": {
          "value": 0.15,
          "unit": "m",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.96641,
            "notes": "",
            "policy_id": null,
            "policy_version": null,
            "user_accepted": null,
            "superseded_value": null,
            "derived_from": [
              "ev_ocr_ocr_tok_001"
            ]
          }
        },
        "focal_length_px": {
          "value": 117.0,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "policy_id": "policy_normalized_lens_focal_ratio",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "objectDistance": {
          "value": 234.0,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "policy_id": "policy_normalized_lens_object_distance",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        },
        "object_height_px": {
          "value": 81.89999999999999,
          "unit": "px",
          "status": "assumed",
          "provenance": {
            "source": "auto_policy",
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7,
            "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "policy_id": "policy_normalized_lens_object_height",
            "policy_version": "1.0",
            "user_accepted": false,
            "superseded_value": null,
            "derived_from": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          }
        }
      },
      "resolutions": {},
      "geometry": {
        "width": 1280,
        "height": 960,
        "coordinate_space": "source_px",
        "lens_center": {
          "x": 641.0,
          "y": 432.0
        }
      }
    }
  }
]
```

**What it should receive — expected input:** Grounded values, policy resolutions, units and any supported pixel/physical-length pairs.

**What it provides — actual output (selected recorded fields):**

```json
{
  "records": [
    {
      "call": "00343_ResolutionEngine.auto_resolve",
      "return_value": {
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "lens_center",
          "focal_length_px",
          "aperture_height_px"
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
      "call": "00345_CalibrationEngine.derive_for_subtype",
      "return_value": null
    },
    {
      "call": "00356_CalibrationEngine.derive_for_subtype",
      "return_value": null
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Consistent resolved units and explicit calibration provenance. A scale derived using assumed physical length must remain assumption-derived; it is not measured ground truth.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** _normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace.

**Changes, provenance and possible information loss:** Several calls can occur inside auto-resolution. Exact invocation records are kept separately; null return can mean calibration was unavailable, not that a zero scale was measured.

[Complete stage input/output bundle](stage_data/20_calibration.json)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00343_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00345_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00356_CalibrationEngine.derive_for_subtype/STAGE.html)

- [Code: ai\resolution\engine.py](contracts/ai/resolution/engine.py)

- [Code: ai\resolution\calibration.py](contracts/ai/resolution/calibration.py)

## 21. Requirement and ambiguity analysis

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Resolution decisions, units and calibration → this component → Readiness decision.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 9,
  "first_8_records": [
    {
      "call": "00321_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
      "call": "00323_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "required_entities": [
            "lens"
          ],
          "required_geometry": [
            "lens_center"
          ],
          "parameters": {
            "lens_center": {
              "id": "req_lens_center",
              "name": "lens_center",
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
            "focal_length_px": {
              "id": "req_lens_focal_length_px",
              "name": "focal_length_px",
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
            "aperture_height_px": {
              "id": "req_lens_aperture_height_px",
              "name": "aperture_height_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 10.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_standard_lens_aperture",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "lens_type": {
              "id": "req_lens_type",
              "name": "lens_type",
              "dimension": "categorical",
              "required": false,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [
                "convex",
                "concave",
                "converging",
                "diverging"
              ],
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
          "one_of_requirements": [],
          "allowed_policies": [
            "policy_standard_lens_aperture",
            "policy_normalized_lens_focal_ratio",
            "policy_normalized_lens_object_distance",
            "policy_normalized_lens_object_height"
          ],
          "parameter_aliases": {
            "focal_length": "focal_length_px",
            "focalLength": "focal_length_px",
            "f": "focal_length_px",
            "aperture": "aperture_height_px",
            "aperture_height": "aperture_height_px",
            "apertureHeight": "aperture_height_px",
            "optical_center": "lens_center",
            "center": "lens_center"
          },
          "notes": "Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u)."
        },
        "issues": []
      }
    },
    {
      "call": "00324_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "required_entities": [
            "lens"
          ],
          "required_geometry": [
            "lens_center"
          ],
          "parameters": {
            "lens_center": {
              "id": "req_lens_center",
              "name": "lens_center",
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
            "focal_length_px": {
              "id": "req_lens_focal_length_px",
              "name": "focal_length_px",
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
            "aperture_height_px": {
              "id": "req_lens_aperture_height_px",
              "name": "aperture_height_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 10.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_standard_lens_aperture",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "lens_type": {
              "id": "req_lens_type",
              "name": "lens_type",
              "dimension": "categorical",
              "required": false,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [
                "convex",
                "concave",
                "converging",
                "diverging"
              ],
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
          "one_of_requirements": [],
          "allowed_policies": [
            "policy_standard_lens_aperture",
            "policy_normalized_lens_focal_ratio",
            "policy_normalized_lens_object_distance",
            "policy_normalized_lens_object_height"
          ],
          "parameter_aliases": {
            "focal_length": "focal_length_px",
            "focalLength": "focal_length_px",
            "f": "focal_length_px",
            "aperture": "aperture_height_px",
            "aperture_height": "aperture_height_px",
            "apertureHeight": "aperture_height_px",
            "optical_center": "lens_center",
            "center": "lens_center"
          },
          "notes": "Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u)."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "00358_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
      "call": "00360_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "required_entities": [
            "lens"
          ],
          "required_geometry": [
            "lens_center"
          ],
          "parameters": {
            "lens_center": {
              "id": "req_lens_center",
              "name": "lens_center",
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
            "focal_length_px": {
              "id": "req_lens_focal_length_px",
              "name": "focal_length_px",
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
            "aperture_height_px": {
              "id": "req_lens_aperture_height_px",
              "name": "aperture_height_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 10.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_standard_lens_aperture",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "lens_type": {
              "id": "req_lens_type",
              "name": "lens_type",
              "dimension": "categorical",
              "required": false,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [
                "convex",
                "concave",
                "converging",
                "diverging"
              ],
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
          "one_of_requirements": [],
          "allowed_policies": [
            "policy_standard_lens_aperture",
            "policy_normalized_lens_focal_ratio",
            "policy_normalized_lens_object_distance",
            "policy_normalized_lens_object_height"
          ],
          "parameter_aliases": {
            "focal_length": "focal_length_px",
            "focalLength": "focal_length_px",
            "f": "focal_length_px",
            "aperture": "aperture_height_px",
            "aperture_height": "aperture_height_px",
            "apertureHeight": "aperture_height_px",
            "optical_center": "lens_center",
            "center": "lens_center"
          },
          "notes": "Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u)."
        },
        "issues": []
      }
    },
    {
      "call": "00361_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "required_entities": [
            "lens"
          ],
          "required_geometry": [
            "lens_center"
          ],
          "parameters": {
            "lens_center": {
              "id": "req_lens_center",
              "name": "lens_center",
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
            "focal_length_px": {
              "id": "req_lens_focal_length_px",
              "name": "focal_length_px",
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
            "aperture_height_px": {
              "id": "req_lens_aperture_height_px",
              "name": "aperture_height_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 10.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_standard_lens_aperture",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "lens_type": {
              "id": "req_lens_type",
              "name": "lens_type",
              "dimension": "categorical",
              "required": false,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [
                "convex",
                "concave",
                "converging",
                "diverging"
              ],
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
          "one_of_requirements": [],
          "allowed_policies": [
            "policy_standard_lens_aperture",
            "policy_normalized_lens_focal_ratio",
            "policy_normalized_lens_object_distance",
            "policy_normalized_lens_object_height"
          ],
          "parameter_aliases": {
            "focal_length": "focal_length_px",
            "focalLength": "focal_length_px",
            "f": "focal_length_px",
            "aperture": "aperture_height_px",
            "aperture_height": "aperture_height_px",
            "apertureHeight": "aperture_height_px",
            "optical_center": "lens_center",
            "center": "lens_center"
          },
          "notes": "Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u)."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "00410_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
      "call": "00412_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
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
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
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
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policy_id": "policy_normalized_lens_focal_ratio",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policy_id": "policy_normalized_lens_object_distance",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policy_id": "policy_normalized_lens_object_height",
                "policy_version": "1.0",
                "user_accepted": false,
                "superseded_value": null,
                "_nested_fields_in_complete_snapshot": [
                  "evidence_refs",
                  "derived_from"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "position_source_px": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "position_source_px": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "required_entities": [
            "lens"
          ],
          "required_geometry": [
            "lens_center"
          ],
          "parameters": {
            "lens_center": {
              "id": "req_lens_center",
              "name": "lens_center",
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
            "focal_length_px": {
              "id": "req_lens_focal_length_px",
              "name": "focal_length_px",
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
            "aperture_height_px": {
              "id": "req_lens_aperture_height_px",
              "name": "aperture_height_px",
              "dimension": "pixels",
              "required": true,
              "allowed_units": [],
              "canonical_unit": "px",
              "min_value": 10.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_standard_lens_aperture",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "lens_type": {
              "id": "req_lens_type",
              "name": "lens_type",
              "dimension": "categorical",
              "required": false,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": null,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [
                "convex",
                "concave",
                "converging",
                "diverging"
              ],
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
          "one_of_requirements": [],
          "allowed_policies": [
            "policy_standard_lens_aperture",
            "policy_normalized_lens_focal_ratio",
            "policy_normalized_lens_object_distance",
            "policy_normalized_lens_object_height"
          ],
          "parameter_aliases": {
            "focal_length": "focal_length_px",
            "focalLength": "focal_length_px",
            "f": "focal_length_px",
            "aperture": "aperture_height_px",
            "aperture_height": "aperture_height_px",
            "apertureHeight": "aperture_height_px",
            "optical_center": "lens_center",
            "center": "lens_center"
          },
          "notes": "Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u)."
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
    "count": 9,
    "first_8_records": [
      {
        "call": "00321_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "thin_lens",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "lens_center",
            "focal_length_px",
            "aperture_height_px"
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
        "call": "00323_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00324_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00358_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "thin_lens",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "lens_center",
            "focal_length_px",
            "aperture_height_px"
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
        "call": "00360_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00361_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00410_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "thin_lens",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "lens_center",
            "focal_length_px",
            "aperture_height_px"
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
        "call": "00412_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": [
    {
      "call": "00323_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00324_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "NEEDS_REVIEW",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00360_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00361_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00412_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00413_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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

**What it should provide — implemented contract:** Satisfied/missing requirements, issues, blockers and warnings consistent with available evidence. Visual correctness and mere field presence must be evaluated separately.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** _normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** The current analyzer checks required entities/parameters and ambiguity. It does not compare every proposed line or point to image pixels.

[Complete stage input/output bundle](stage_data/21_requirements.json)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00321_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00323_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00324_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00358_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00360_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00361_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00410_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00412_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00413_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [Code: ai\resolution\analyzer.py](contracts/ai/resolution/analyzer.py)

## 22. Readiness decision

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Requirement and ambiguity analysis → this component → PhysicsCompiler entry and gate.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00320_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
    "call": "00357_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
    "call": "00409_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00320_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "lens_center",
          "focal_length_px",
          "aperture_height_px"
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
      "call": "00357_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "lens_center",
          "focal_length_px",
          "aperture_height_px"
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
      "call": "00409_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "lens_center",
          "focal_length_px",
          "aperture_height_px"
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** _normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** All repeated evaluations are recorded. Use the final pre-compile decision as the gate, while retaining earlier decisions to see state changes.

[Complete stage input/output bundle](stage_data/22_readiness.json)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00320_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00357_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00409_ReadinessEvaluator.evaluate/STAGE.html)

- [Code: ai\resolution\evaluator.py](contracts/ai/resolution/evaluator.py)

## 23. PhysicsCompiler entry and gate

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** Readiness decision → this component → Canonical scene construction and schema validation.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00380_PhysicsCompiler.compile",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "call": "00380_PhysicsCompiler.compile",
      "return_value": {
        "status": "READY",
        "scene": {
          "domain": "optics",
          "subtype": "thin_lens",
          "source": {
            "type": "book_figure",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "lensX": 641.0,
            "axisY": 432.0,
            "aperture_height_px": 234.0
          },
          "parameters": {
            "focalLength": {
              "value": 117.0,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policyId": "policy_normalized_lens_focal_ratio",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policyId": "policy_normalized_lens_object_distance",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "objectHeight": {
              "value": -81.89999999999999,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policyId": "policy_normalized_lens_object_height",
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
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "_other_fields_in_complete_snapshot": [
            "schemaVersion",
            "id",
            "coordinateSpace",
            "coordinateSystem",
            "objects",
            "render",
            "elements"
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

**Changes, provenance and possible information loss:** The active compiler implementation is ai/ingestion/PhysicsCompiler.py. The scene_compiler module re-exports it.

[Complete stage input/output bundle](stage_data/23_gate.json)

- [PhysicsCompiler.compile — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00380_PhysicsCompiler.compile/STAGE.html)

- [Code: ai\ingestion\PhysicsCompiler.py](contracts/ai/ingestion/PhysicsCompiler.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00380_PhysicsCompiler.compile/actual_overlay_on_source.png)

## 24. Canonical scene construction and schema validation

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** PhysicsCompiler entry and gate → this component → API response delivered to the browser.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00432_PhysicsCompiler._build_canonical_scene",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "domain": "optics",
      "subtype": "thin_lens"
    }
  },
  {
    "call": "00440_PhysicsCompiler._populate_canonical_lens",
    "value": {
      "scene": {
        "schemaVersion": "1.0",
        "id": "PHY-OPTI-figure_001",
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "objects": [],
        "render": {
          "coordinate_space": "source_px"
        }
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "subtype": "thin_lens"
    }
  },
  {
    "call": "00456_PhysicsCompiler._preserve_parameter_provenance",
    "value": {
      "scene": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "lensX": 641.0,
          "axisY": 432.0,
          "aperture_height_px": 234.0
        },
        "parameters": {
          "focalLength": {
            "value": 117.0,
            "unit": "px",
            "provenance": "observed"
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "provenance": "observed"
          },
          "objectHeight": {
            "value": -81.89999999999999,
            "unit": "px",
            "provenance": "observed"
          }
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements"
        ]
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "thin_lens",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          }
        },
        "parameters": {
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "aperture_height_px": {
            "value": 234.0,
            "unit": "px",
            "status": "observed",
            "provenance": {
              "source": "diagram_measurement",
              "confidence": 0.85,
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
          "focal_length": {
            "value": 0.15,
            "unit": "m",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.96641,
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
          "focal_length_px": {
            "value": 117.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policy_id": "policy_normalized_lens_focal_ratio",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policy_id": "policy_normalized_lens_object_distance",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          },
          "object_height_px": {
            "value": 81.89999999999999,
            "unit": "px",
            "status": "assumed",
            "provenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policy_id": "policy_normalized_lens_object_height",
              "policy_version": "1.0",
              "user_accepted": false,
              "superseded_value": null,
              "_nested_fields_in_complete_snapshot": [
                "evidence_refs",
                "derived_from"
              ]
            }
          }
        },
        "resolutions": {},
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "entities": [
          {
            "id": "lens_1",
            "type": "lens",
            "label": "convex lens",
            "position_source_px": {
              "x": 641.0,
              "y": 432.0,
              "coordinate_space": "source_px",
              "method": "cv_lens_center"
            },
            "geometry": null,
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "object_1",
            "type": "object",
            "label": "Object",
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
            "id": "image_1",
            "type": "image",
            "label": "Image",
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
            "id": "axis_1",
            "type": "optical_axis",
            "label": "principal axis",
            "position_source_px": null,
            "geometry": {
              "start": {
                "x": 650.0,
                "y": 432.0
              },
              "end": {
                "x": 1124.0,
                "y": 432.0
              },
              "length_px": 474.0,
              "_nested_fields_in_complete_snapshot": []
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ]
          },
          {
            "id": "focal_point_1",
            "type": "focal_point",
            "label": "F",
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
            "id": "focal_point_2",
            "type": "focal_point",
            "label": "2F",
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
            "type": "forms_image",
            "from": "lens_1",
            "to": "image_1",
            "confidence": 0.95
          },
          {
            "type": "refracts",
            "from": "object_1",
            "to": "lens_1",
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
      "subtype": "thin_lens"
    }
  },
  {
    "call": "00457_validate_canonical_scene",
    "value": {
      "scene": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "lensX": 641.0,
          "axisY": 432.0,
          "aperture_height_px": 234.0
        },
        "parameters": {
          "focalLength": {
            "value": 117.0,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "objectHeight": {
            "value": -81.89999999999999,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policyId": "policy_normalized_lens_object_height",
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
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements"
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
      "call": "00432_PhysicsCompiler._build_canonical_scene",
      "return_value": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
          "lens_center": {
            "x": 641.0,
            "y": 432.0
          },
          "lensX": 641.0,
          "axisY": 432.0,
          "aperture_height_px": 234.0
        },
        "parameters": {
          "focalLength": {
            "value": 117.0,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7,
              "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "objectDistance": {
            "value": 234.0,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7,
              "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "objectHeight": {
            "value": -81.89999999999999,
            "unit": "px",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7,
              "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          }
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements"
        ]
      }
    },
    {
      "call": "00440_PhysicsCompiler._populate_canonical_lens",
      "return_value": null
    },
    {
      "call": "00456_PhysicsCompiler._preserve_parameter_provenance",
      "return_value": null
    },
    {
      "call": "00457_validate_canonical_scene",
      "return_value": []
    }
  ],
  "in_place_outputs": [
    {
      "call": "00440_PhysicsCompiler._populate_canonical_lens",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-OPTI-figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render"
          ]
        },
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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
      "call": "00456_PhysicsCompiler._preserve_parameter_provenance",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-OPTI-figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render",
            "elements"
          ]
        },
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "status_notes": "Missing focal_length, object_distance, or lens center.",
          "calibration": null,
          "id": "dd013d21b8704bd296afcc9dcbc6a750_figure_001",
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

**What it should provide — implemented contract:** Domain scene objects, parameters and geometry that preserve evidence/provenance and source frame. If model geometry is reconstructed, distinguish it from observed geometry.

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

**Comparison / debugging conclusion:** Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

**Changes, provenance and possible information loss:** Populate methods mutate scene in place and return None. Their real output is locals_after.scene and the enclosing compile result. None is not a failed scene.

[Complete stage input/output bundle](stage_data/24_compile.json)

- [PhysicsCompiler._build_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00432_PhysicsCompiler._build_canonical_scene/STAGE.html)

- [PhysicsCompiler._populate_canonical_lens — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00440_PhysicsCompiler._populate_canonical_lens/STAGE.html)

- [PhysicsCompiler._preserve_parameter_provenance — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00456_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- [validate_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00457_validate_canonical_scene/STAGE.html)

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
        "domain": "optics",
        "status": "ready",
        "scene": {
          "domain": "optics",
          "subtype": "thin_lens",
          "source": {
            "type": "book_figure",
            "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "lensX": 641.0,
            "axisY": 432.0,
            "aperture_height_px": 234.0
          },
          "parameters": {
            "focalLength": {
              "value": 117.0,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policyId": "policy_normalized_lens_focal_ratio",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policyId": "policy_normalized_lens_object_distance",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "objectHeight": {
              "value": -81.89999999999999,
              "unit": "px",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policyId": "policy_normalized_lens_object_height",
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
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "_other_fields_in_complete_snapshot": [
            "schemaVersion",
            "id",
            "coordinateSpace",
            "coordinateSystem",
            "objects",
            "render",
            "elements"
          ]
        },
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "thin_lens",
          "status": "READY_TO_COMPILE",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            }
          },
          "parameters": {
            "lens_center": {
              "x": 641.0,
              "y": 432.0
            },
            "aperture_height_px": {
              "value": 234.0,
              "unit": "px",
              "status": "observed",
              "provenance": {
                "source": "diagram_measurement",
                "confidence": 0.85,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "focal_length": {
              "value": 0.15,
              "unit": "m",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.96641,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "focal_length_px": {
              "value": 117.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                "policyId": "policy_normalized_lens_focal_ratio",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "objectDistance": {
              "value": 234.0,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
                "policyId": "policy_normalized_lens_object_distance",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "object_height_px": {
              "value": 81.89999999999999,
              "unit": "px",
              "status": "assumed",
              "provenance": {
                "source": "auto_policy",
                "confidence": 0.7,
                "notes": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
                "policyId": "policy_normalized_lens_object_height",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            }
          },
          "resolutions": {},
          "assumptions": [
            {
              "parameter": "focal_length_px",
              "policyId": "policy_normalized_lens_focal_ratio",
              "policyVersion": "1.0",
              "value": 117.0,
              "unit": "px",
              "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
              "provenance": "auto_policy",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "confidence": 0.7
            },
            {
              "parameter": "objectDistance",
              "policyId": "policy_normalized_lens_object_distance",
              "policyVersion": "1.0",
              "value": 234.0,
              "unit": "px",
              "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            },
            {
              "parameter": "object_height_px",
              "policyId": "policy_normalized_lens_object_height",
              "policyVersion": "1.0",
              "value": 81.89999999999999,
              "unit": "px",
              "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
              "derivedFrom": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ],
              "provenance": "auto_policy",
              "confidence": 0.7
            }
          ],
          "entities": [
            {
              "id": "lens_1",
              "type": "lens",
              "label": "convex lens",
              "positionSourcePx": {
                "x": 641.0,
                "y": 432.0,
                "coordinate_space": "source_px",
                "method": "cv_lens_center"
              },
              "geometry": null,
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "object_1",
              "type": "object",
              "label": "Object",
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
            },
            {
              "id": "image_1",
              "type": "image",
              "label": "Image",
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
            },
            {
              "id": "axis_1",
              "type": "optical_axis",
              "label": "principal axis",
              "positionSourcePx": null,
              "geometry": {
                "start": {
                  "x": 650.0,
                  "y": 432.0
                },
                "end": {
                  "x": 1124.0,
                  "y": 432.0
                },
                "length_px": 474.0,
                "_nested_fields_in_complete_snapshot": []
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
              ]
            },
            {
              "id": "focal_point_1",
              "type": "focal_point",
              "label": "F",
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
            },
            {
              "id": "focal_point_2",
              "type": "focal_point",
              "label": "2F",
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
              "type": "forms_image",
              "from": "lens_1",
              "to": "image_1",
              "confidence": 0.95
            },
            {
              "type": "refracts",
              "from": "object_1",
              "to": "lens_1",
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
          "id": "dd013d21b8704bd296afcc9dcbc6a750",
          "mimeType": "image/jpeg",
          "originalFilename": "photo_2026-10-10_12-06-36 (2).jpg",
          "byteSize": 51136,
          "width_px": 1280,
          "height_px": 960,
          "sha256": "b1146c485899630e983706b53cce5f2320164bc1d7324bfb1c47ff2b7dab7c5c"
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117.0,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "confidence": 0.7
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234.0,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "derivedFrom": [
              "ev_cv_lens_dd013d21b8704bd296afcc9dcbc6a750"
            ],
            "provenance": "auto_policy",
            "confidence": 0.7
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

**Changes, provenance and possible information loss:** This is the handler return, after nested work. Exact HTTP status/body are retained separately from the Python object.

[Complete stage input/output bundle](stage_data/25_response.json)

- [ingest_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- [HTTP response 1792207574356209400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/http/1792207574356209400_response_body.json)

- [Code: apps\api\main.py](contracts/apps/api/main.py)

## 26. Frontend receives result and selects next state

**Execution:** EXECUTED. **Verdict:** SCENE ACCEPTED.

**Upstream → downstream:** API response delivered to the browser → this component → Review / explicit compile request branch.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 3508.2000000178814,
    "data": [
      "UPLOADING"
    ]
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 48494.40000000596,
    "data": [
      "ANALYZING"
    ]
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._normalizeSceneBackground",
    "phase": "input",
    "wallTime": 48497.5,
    "data": [
      {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
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
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements"
        ]
      }
    ]
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 48498.30000001192,
    "data": [
      "READY_TO_SIMULATE"
    ]
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 48827.70000001788,
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 3508.5,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 48494.80000001192,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._normalizeSceneBackground",
      "phase": "output",
      "wallTime": 48498.20000001788,
      "data": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 48498.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 48827.70000001788,
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

**Changes, provenance and possible information loss:** Only events after startWithFile for this trace are used here. Startup/demo events remain in the raw log but are excluded from this diagram’s runtime evidence.

[Complete stage input/output bundle](stage_data/26_orchestrator.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/27_review.json)

- [HTTP response 1792207574356209400_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/http/1792207574356209400_response_body.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 28. InteractiveFigure receives the compiled scene

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** Review / explicit compile request branch → this component → FigureViewport background and layout.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "InteractiveFigure.load",
    "phase": "input",
    "wallTime": 48515.20000001788,
    "data": [
      {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements",
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "InteractiveFigure.load",
      "phase": "output",
      "wallTime": 48742.09999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A figure bound to the original image, with the correct domain runtime and an initial rendered output. No unrelated demo geometry.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** load performs layout/runtime initialization internally. The t0 event immediately after load is an observed snapshot; exact child JS calls were not all instrumented.

[Complete stage input/output bundle](stage_data/28_figure.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

## 29. FigureViewport background and layout

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** InteractiveFigure receives the compiled scene → this component → PhysicsRuntime normalization and adapter initialization.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "FigureViewport.setBackground",
    "phase": "input",
    "wallTime": 48516.40000000596,
    "data": [
      "/uploads/diagram_dd013d21.jpg",
      1280,
      960
    ]
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "FigureViewport.recalculate",
    "phase": "input",
    "wallTime": 48647.90000000596,
    "data": []
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "FigureViewport.recalculate",
    "phase": "input",
    "wallTime": 48875.70000001788,
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "FigureViewport.recalculate",
      "phase": "output",
      "wallTime": 48703.40000000596,
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "FigureViewport.setBackground",
      "phase": "output",
      "wallTime": 48703.59999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "FigureViewport.recalculate",
      "phase": "output",
      "wallTime": 48876.40000000596,
      "data": {
        "sourceWidth": 1280,
        "sourceHeight": 960,
        "displayWidth": 800,
        "displayHeight": 600,
        "viewportWidth": 1010,
        "viewportHeight": 600,
        "scale": 0.625,
        "offsetX": 105,
        "offsetY": 0,
        "dpr": 1,
        "renderedImageRect": {
          "left": 105,
          "top": 0,
          "width": 800,
          "height": 600
        }
      }
    },
    {
      "measured_image_rect": {
        "x": 139,
        "y": 227,
        "width": 800,
        "height": 600,
        "top": 227,
        "right": 939,
        "bottom": 827,
        "left": 139
      },
      "mapper": {
        "sourceW": 1280,
        "sourceH": 960,
        "viewW": 1010,
        "viewH": 600,
        "dpr": 1,
        "scale": 0.625,
        "renderedW": 800,
        "renderedH": 600,
        "offsetX": 105,
        "offsetY": 0
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The source image displayed with an aspect-preserving transform shared by its overlay. Letterboxing belongs to the viewport, not to native geometry.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Preserve source_px. The measured image rectangle and mapper offsets are shown in the coordinate stage; CSS pixels are not substituted into BookIR.

[Complete stage input/output bundle](stage_data/29_background.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\FigureViewport.js](contracts/apps/web/src/components/FigureViewport.js)

## 30. PhysicsRuntime normalization and adapter initialization

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** FigureViewport background and layout → this component → Domain solver and actual initial state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.load",
    "phase": "input",
    "wallTime": 48713,
    "data": [
      {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements",
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
          "imageUrl": "/uploads/diagram_dd013d21.jpg",
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
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.normalizeScene",
    "phase": "input",
    "wallTime": 48718.80000001192,
    "data": [
      {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements",
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.normalizeScene",
      "phase": "output",
      "wallTime": 48719.09999999404,
      "data": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "objects",
          "render",
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.load",
      "phase": "output",
      "wallTime": 48737.30000001192,
      "data": {
        "domain": "optics",
        "subtype": "thin_lens",
        "time": 0,
        "state": {
          "domain": "optics",
          "subtype": "thin_lens",
          "type": "thin_lens",
          "running": false,
          "focalLength": 117,
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "rayCount": 3,
          "_nested_fields_in_complete_snapshot": [
            "solution"
          ]
        },
        "geometry": {
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageX": 875,
          "imageHeight": 81.89999999999999,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "lensX": 641,
          "axisY": 432,
          "lensType": "convex",
          "mirror": null,
          "prism": null,
          "_nested_fields_in_complete_snapshot": [
            "rays",
            "opticalAxis",
            "landmarks",
            "lens",
            "object",
            "image",
            "handles"
          ]
        },
        "telemetry": {
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageX": 875,
          "imageHeight": 81.89999999999999,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "lensX": 641,
          "axisY": 432,
          "lensType": "convex",
          "imageDistance": 234,
          "objectDistance": 234,
          "focalLength": 117,
          "tir": false,
          "_nested_fields_in_complete_snapshot": [
            "rays"
          ]
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        }
      }
    },
    {
      "actual_runtime_after_load": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-OPTI-figure_001",
          "domain": "optics",
          "subtype": "thin_lens",
          "_nested_fields_in_complete_snapshot": [
            "source",
            "coordinateSpace",
            "coordinateSystem",
            "parameters",
            "assumptions",
            "geometry",
            "objects",
            "render",
            "elements",
            "visual"
          ]
        },
        "output": {
          "domain": "optics",
          "subtype": "thin_lens",
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
          "domain": "optics",
          "subtype": "thin_lens",
          "type": "thin_lens",
          "running": false,
          "focalLength": 117,
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "rayCount": 3,
          "_nested_fields_in_complete_snapshot": [
            "solution"
          ]
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
        "sourceH": 960,
        "renderer": "OpticsRenderer"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Validated normalized scene, resolved capabilities, matching adapter and initialized runtime. Normalization must not erase provenance or relocate source points.

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Registry/capability/adapter child calls are established by runtime source and captured boundary/output. Their independent entry/exit arguments were not recorded; they are not presented as new trace snapshots.

[Complete stage input/output bundle](stage_data/30_runtime.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: engine\core\PhysicsRuntime.js](contracts/engine/core/PhysicsRuntime.js)

## 31. Domain solver and actual initial state

**Execution:** EXECUTED. **Verdict:** OUTPUT OBSERVED; NO NUMERICAL DEFECT PROVEN.

**Upstream → downstream:** PhysicsRuntime normalization and adapter initialization → this component → CoordinateMapper: source → overlay → browser.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "scene_used_by_runtime": {
      "domain": "optics",
      "subtype": "thin_lens",
      "source": {
        "type": "book_figure",
        "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
        "figure_id": "figure_001",
        "width": 1280,
        "height": 960,
        "image_width_px": 1280,
        "image_height_px": 960,
        "image": "/uploads/diagram_dd013d21.jpg"
      },
      "geometry": {
        "width": 1280,
        "height": 960,
        "coordinate_space": "source_px",
        "lens_center": {
          "x": 641,
          "y": 432
        },
        "lensX": 641,
        "axisY": 432,
        "aperture_height_px": 234
      },
      "parameters": {
        "focalLength": {
          "value": 117,
          "unit": "px",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "objectDistance": {
          "value": 234,
          "unit": "px",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "objectHeight": {
          "value": -81.89999999999999,
          "unit": "px",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        }
      },
      "assumptions": [
        {
          "parameter": "focal_length_px",
          "policyId": "policy_normalized_lens_focal_ratio",
          "policyVersion": "1.0",
          "value": 117,
          "unit": "px",
          "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
          "provenance": "auto_policy",
          "confidence": 0.7,
          "_nested_fields_in_complete_snapshot": [
            "derivedFrom"
          ]
        },
        {
          "parameter": "objectDistance",
          "policyId": "policy_normalized_lens_object_distance",
          "policyVersion": "1.0",
          "value": 234,
          "unit": "px",
          "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
          "provenance": "auto_policy",
          "confidence": 0.7,
          "_nested_fields_in_complete_snapshot": [
            "derivedFrom"
          ]
        },
        {
          "parameter": "object_height_px",
          "policyId": "policy_normalized_lens_object_height",
          "policyVersion": "1.0",
          "value": 81.89999999999999,
          "unit": "px",
          "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
          "provenance": "auto_policy",
          "confidence": 0.7,
          "_nested_fields_in_complete_snapshot": [
            "derivedFrom"
          ]
        }
      ],
      "_other_fields_in_complete_snapshot": [
        "schemaVersion",
        "id",
        "coordinateSpace",
        "coordinateSystem",
        "objects",
        "render",
        "elements",
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
        "domain": "optics",
        "subtype": "thin_lens",
        "_other_fields_in_complete_snapshot": [
          "type",
          "running",
          "focalLength",
          "u",
          "v",
          "magnification",
          "imageType",
          "isReal",
          "isInverted",
          "rayCount",
          "solution"
        ]
      },
      "output": {
        "domain": "optics",
        "subtype": "thin_lens",
        "time": 0,
        "state": {
          "domain": "optics",
          "subtype": "thin_lens",
          "type": "thin_lens",
          "running": false,
          "focalLength": 117,
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "rayCount": 3,
          "_nested_fields_in_complete_snapshot": [
            "solution"
          ]
        },
        "geometry": {
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageX": 875,
          "imageHeight": 81.89999999999999,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "lensX": 641,
          "axisY": 432,
          "lensType": "convex",
          "mirror": null,
          "prism": null,
          "_nested_fields_in_complete_snapshot": [
            "rays",
            "opticalAxis",
            "landmarks",
            "lens",
            "object",
            "image",
            "handles"
          ]
        },
        "telemetry": {
          "u": 234,
          "v": 234,
          "magnification": -1,
          "imageX": 875,
          "imageHeight": 81.89999999999999,
          "imageType": "real_same_size",
          "isReal": true,
          "isInverted": true,
          "lensX": 641,
          "axisY": 432,
          "lensType": "convex",
          "imageDistance": 234,
          "objectDistance": 234,
          "focalLength": 117,
          "tir": false,
          "_nested_fields_in_complete_snapshot": [
            "rays"
          ]
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        }
      },
      "mechanics_internal_capture": null
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Mathematically consistent state/output for those inputs. Correct computation is separate from whether those inputs reconstruct this diagram.

**What correct handling of THIS diagram requires:** At t=0 the object should occupy its printed arrow and the image/rays should be compared to the printed image/rays. The actual solver returns real_same_size from assumed u=2f, whereas the source depicts an enlarged image. This demonstrates an input/model mismatch, not an arithmetic failure.

**Comparison / debugging conclusion:** Thin-lens runtime returns u=234, v=234, magnification=−1. No numerical solver defect is established. The actual t=0 renderer makes already incorrect source geometry visible.

**Changes, provenance and possible information loss:** Scene/state/output are actual captures. Exact internal solver-call argument objects were not individually intercepted; no replay or hand-computed replacement is labeled as runtime evidence.

[Complete stage input/output bundle](stage_data/31_solver.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: engine\optics\thinLensEngine.js](contracts/engine/optics/thinLensEngine.js)

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
      "viewH": 600,
      "dpr": 1,
      "scale": 0.625,
      "renderedW": 800,
      "renderedH": 600,
      "offsetX": 105,
      "offsetY": 0
    },
    "image_rect": {
      "x": 139,
      "y": 227,
      "width": 800,
      "height": 600,
      "top": 227,
      "right": 939,
      "bottom": 827,
      "left": 139
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
      "landmarks": {
        "count": 38,
        "first_8_records": [
          {
            "label": "scene.geometry.lens_center",
            "source": {
              "x": 641,
              "y": 432
            },
            "view": {
              "x": 505.625,
              "y": 270
            },
            "overlay": {
              "x": 400.625,
              "y": 270
            },
            "inverse": {
              "x": 641,
              "y": 432
            },
            "browser": {
              "x": 539.625,
              "y": 497
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[0].points[0]",
            "source": {
              "x": 407,
              "y": 350.1
            },
            "view": {
              "x": 359.375,
              "y": 218.8125
            },
            "overlay": {
              "x": 254.375,
              "y": 218.8125
            },
            "inverse": {
              "x": 407,
              "y": 350.1
            },
            "browser": {
              "x": 393.375,
              "y": 445.8125
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[0].points[1]",
            "source": {
              "x": 641,
              "y": 350.1
            },
            "view": {
              "x": 505.625,
              "y": 218.8125
            },
            "overlay": {
              "x": 400.625,
              "y": 218.8125
            },
            "inverse": {
              "x": 641,
              "y": 350.1
            },
            "browser": {
              "x": 539.625,
              "y": 445.8125
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[0].points[2]",
            "source": {
              "x": 1280,
              "y": 797.4
            },
            "view": {
              "x": 905,
              "y": 498.375
            },
            "overlay": {
              "x": 800,
              "y": 498.375
            },
            "inverse": {
              "x": 1280,
              "y": 797.4
            },
            "browser": {
              "x": 939,
              "y": 725.375
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[1].points[0]",
            "source": {
              "x": 407,
              "y": 350.1
            },
            "view": {
              "x": 359.375,
              "y": 218.8125
            },
            "overlay": {
              "x": 254.375,
              "y": 218.8125
            },
            "inverse": {
              "x": 407,
              "y": 350.1
            },
            "browser": {
              "x": 393.375,
              "y": 445.8125
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[1].points[1]",
            "source": {
              "x": 641,
              "y": 432
            },
            "view": {
              "x": 505.625,
              "y": 270
            },
            "overlay": {
              "x": 400.625,
              "y": 270
            },
            "inverse": {
              "x": 641,
              "y": 432
            },
            "browser": {
              "x": 539.625,
              "y": 497
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[1].points[2]",
            "source": {
              "x": 1280,
              "y": 655.65
            },
            "view": {
              "x": 905,
              "y": 409.78125
            },
            "overlay": {
              "x": 800,
              "y": 409.78125
            },
            "inverse": {
              "x": 1280,
              "y": 655.65
            },
            "browser": {
              "x": 939,
              "y": 636.78125
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "runtime.output.state.solution.rays[2].points[0]",
            "source": {
              "x": 407,
              "y": 350.1
            },
            "view": {
              "x": 359.375,
              "y": 218.8125
            },
            "overlay": {
              "x": 254.375,
              "y": 218.8125
            },
            "inverse": {
              "x": 407,
              "y": 350.1
            },
            "browser": {
              "x": 393.375,
              "y": 445.8125
            },
            "_nested_fields_in_complete_snapshot": []
          }
        ],
        "complete_list": "See complete stage bundle / original artifact"
      },
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
            "height": 600,
            "top": 227,
            "right": 1044,
            "bottom": 827,
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
            "height": 600,
            "top": 227,
            "right": 1044,
            "bottom": 827,
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
          "src": "http://127.0.0.1:5173/uploads/diagram_dd013d21.jpg",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 800,
          "height": 600,
          "viewBox": null,
          "rect": {
            "x": 139,
            "y": 227,
            "width": 800,
            "height": 600,
            "top": 227,
            "right": 939,
            "bottom": 827,
            "left": 139
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
            "x": 139,
            "y": 227,
            "width": 800,
            "height": 600,
            "top": 227,
            "right": 939,
            "bottom": 827,
            "left": 139
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        },
        {
          "tag": "svg",
          "id": "",
          "className": "optics-overlay-svg",
          "src": null,
          "viewBox": "0 0 1280 960",
          "rect": {
            "x": 139,
            "y": 227,
            "width": 800,
            "height": 600,
            "top": 227,
            "right": 939,
            "bottom": 827,
            "left": 139
          },
          "_nested_fields_in_complete_snapshot": [
            "width",
            "height",
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "diagram-image",
          "className": "diagram-image",
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207572089",
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
          "src": "blob:http://127.0.0.1:5173/643e338b-5bfb-43b1-ba53-dab43b65cd1a",
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

**What correct handling of THIS diagram requires:** 15 cm is OCR-groundable focal length. Object/lens/image/ray positions and F spacing must be measured from the source. The drawing suggests the between-F-and-2F image-formation case; no exact object distance or annotated pixel coordinates are supplied.

**Comparison / debugging conclusion:** Actual sourceToView/sourceToOverlay and inverse results preserve supplied points. This does not validate the input coordinates against the source.

**Changes, provenance and possible information loss:** sourceToView includes viewport letterboxing; sourceToOverlay omits it because the overlay is already image-aligned. Browser coordinates add the measured image origin. Do not add letterboxing twice.

[Complete stage input/output bundle](stage_data/32_mapper.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: engine\core\coordinateMapper.js](contracts/engine/core/coordinateMapper.js)

## 33. Actual renderer at t=0 over the original

**Execution:** EXECUTED. **Verdict:** FAIL — T=0 SOURCE REGISTRATION.

**Upstream → downstream:** CoordinateMapper: source → overlay → browser → this component → Activation, motion and reset.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "runtime_output": {
      "domain": "optics",
      "subtype": "thin_lens",
      "time": 0,
      "state": {
        "domain": "optics",
        "subtype": "thin_lens",
        "_other_fields_in_complete_snapshot": [
          "type",
          "running",
          "focalLength",
          "u",
          "v",
          "magnification",
          "imageType",
          "isReal",
          "isInverted",
          "rayCount",
          "solution"
        ]
      },
      "geometry": {
        "u": 234,
        "v": 234,
        "magnification": -1,
        "imageX": 875,
        "imageHeight": 81.89999999999999,
        "imageType": "real_same_size",
        "isReal": true,
        "isInverted": true,
        "lensX": 641,
        "axisY": 432,
        "lensType": "convex",
        "rays": [
          {
            "id": "r1",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          },
          {
            "id": "r2",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          },
          {
            "id": "r3",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "opticalAxis",
          "landmarks",
          "lens",
          "mirror",
          "object",
          "image",
          "prism",
          "handles"
        ]
      },
      "telemetry": {
        "u": 234,
        "v": 234,
        "magnification": -1,
        "imageX": 875,
        "imageHeight": 81.89999999999999,
        "imageType": "real_same_size",
        "isReal": true,
        "isInverted": true,
        "lensX": 641,
        "axisY": 432,
        "lensType": "convex",
        "rays": [
          {
            "id": "r1",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          },
          {
            "id": "r2",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          },
          {
            "id": "r3",
            "dashed": false,
            "_nested_fields_in_complete_snapshot": [
              "points"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "imageDistance",
          "objectDistance",
          "focalLength",
          "tir"
        ]
      },
      "events": [],
      "editableParameters": {
        "focalLength": {
          "value": 117,
          "unit": "px",
          "provenance": "auto_policy",
          "editable": true,
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance",
            "control"
          ]
        },
        "objectDistance": {
          "value": 234,
          "unit": "px",
          "provenance": "auto_policy",
          "editable": true,
          "targetId": "object_1",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance",
            "control"
          ]
        },
        "objectHeight": {
          "value": -81.89999999999999,
          "unit": "px",
          "provenance": "auto_policy",
          "editable": true,
          "targetId": "object_1",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance",
            "control"
          ]
        }
      }
    },
    "transforms": [
      {
        "tag": "svg",
        "rect": {
          "x": 139,
          "y": 227,
          "width": 800,
          "height": 600,
          "top": 227,
          "right": 939,
          "bottom": 827,
          "left": 139
        },
        "imageRect": {
          "x": 139,
          "y": 227,
          "width": 800,
          "height": 600,
          "top": 227,
          "right": 939,
          "bottom": 827,
          "left": 139
        },
        "scaleX": 1.6,
        "scaleY": 1.6,
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
      "captured_svg": [
        {
          "original": "<svg class=\"optics-overlay-svg\" viewBox=\"0 0 1280 960\" width=\"800\" height=\"600\" style=\"position: absolute; overflow: visible; pointer-events: none; user-select: none; left: 0px; top: 0px; width: 100%; height: 100%;\"><g class=\"layer-axis\"><line x1=\"0\" y1=\"432\" x2=\"1280\" y2=\"432\" stroke=\"rgba(148, 163, 184, 0.45)\" stroke-width=\"1.5\" stroke-dasharray=\"6 4\"></line></g><g class=\"layer-landmarks\"><circle cx=\"641\" cy=\"432\" r=\"3.5\" fill=\"#38bdf8\"></circle><text x=\"641\" y=\"448\" fill=\"#38bdf8\" font-size=\"12\" text-anchor=\"middle\">O</text><circle cx=\"524\" cy=\"432\" r=\"3\" fill=\"#34d399\"></circle><text x=\"524\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\">F₁</text><circle cx=\"758\" cy=\"432\" r=\"3\" fill=\"#34d399\"></circle><text x=\"758\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\">F₂</text><circle cx=\"407\" cy=\"432\" r=\"3\" fill=\"#34d399\"></circle><text x=\"407\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\">2F₁</text><circle cx=\"875\" cy=\"432\" r=\"3\" fill=\"#34d399\"></circle><text x=\"875\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\">2F₂</text></g><g class=\"layer-shapes\"></g><g class=\"layer-rays\"><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"350.1\" stroke=\"#f59e0b\" stroke-width=\"2\" opacity=\"0.95\"></line><line x1=\"641\" y1=\"350.1\" x2=\"1280\" y2=\"797.4\" stroke=\"#f59e0b\" stroke-width=\"2\" opacity=\"0.95\"></line><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"432\" stroke=\"#38bdf8\" stroke-width=\"2\" opacity=\"0.95\"></line><line x1=\"641\" y1=\"432\" x2=\"1280\" y2=\"655.65\" stroke=\"#38bdf8\" stroke-width=\"2\" opacity=\"0.95\"></line><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"513.9\" stroke=\"#a855f7\" stroke-width=\"2\" opacity=\"0.95\"></line><line x1=\"641\" y1=\"513.9\" x2=\"1280\" y2=\"513.9\" stroke=\"#a855f7\" stroke-width=\"2\" opacity=\"0.95\"></line></g><g class=\"layer-image\"><g class=\"optics-arrow\"><line x1=\"875\" y1=\"432\" x2=\"875\" y2=\"513.9\" stroke=\"#34d399\" stroke-width=\"3\" opacity=\"0.95\"></line><polyline points=\"869,503.5076951545867 875,513.9 881,503.5076951545867\" stroke=\"#34d399\" stroke-width=\"3\" fill=\"none\"></polyline><text x=\"875\" y=\"531.9\" fill=\"#34d399\" font-size=\"11\" font-weight=\"bold\" text-anchor=\"middle\">Real Image</text></g></g><g class=\"layer-object\"><g class=\"optics-arrow\"><line x1=\"407\" y1=\"432\" x2=\"407\" y2=\"350.1\" stroke=\"#38bdf8\" stroke-width=\"3\" opacity=\"0.95\"></line><polyline points=\"413,360.4923048454133 407,350.1 401,360.4923048454133\" stroke=\"#38bdf8\" stroke-width=\"3\" fill=\"none\"></polyline><text x=\"407\" y=\"340.1\" fill=\"#38bdf8\" font-size=\"11\" font-weight=\"bold\" text-anchor=\"middle\">Object</text></g></g><g class=\"layer-handles\" style=\"pointer-events: auto;\"><circle cx=\"407\" cy=\"391.05\" r=\"9\" fill=\"rgba(56, 189, 248, 0.25)\" stroke=\"#38bdf8\" stroke-width=\"2\" cursor=\"ew-resize\" class=\"if-handle if-handle-object-pos\" data-handle=\"object_pos\" data-target-id=\"object_1\" data-param-address=\"objectDistance\"></circle><circle cx=\"407\" cy=\"350.1\" r=\"7\" fill=\"#38bdf8\" stroke=\"#ffffff\" stroke-width=\"2\" cursor=\"ns-resize\" class=\"if-handle if-handle-object-tip\" data-handle=\"object_tip\" data-target-id=\"object_1\" data-param-address=\"objectHeight\"></circle></g></svg>",
          "rendered": "<svg class=\"optics-overlay-svg\" viewBox=\"0 0 1280 960\" width=\"800\" height=\"600\" style=\"position: absolute; overflow: visible; pointer-events: none; user-select: none; left: 0px; top: 0px; width: 800px; height: 600px; fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: block;\" xmlns=\"http://www.w3.org/2000/svg\"><g class=\"layer-axis\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><line x1=\"0\" y1=\"432\" x2=\"1280\" y2=\"432\" stroke=\"rgba(148, 163, 184, 0.45)\" stroke-width=\"1.5\" stroke-dasharray=\"6 4\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgba(148, 163, 184, 0.45); stroke-width: 1.5px; stroke-opacity: 1; stroke-dasharray: 6px, 4px; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></g><g class=\"layer-landmarks\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><circle cx=\"641\" cy=\"432\" r=\"3.5\" fill=\"#38bdf8\" style=\"fill: rgb(56, 189, 248); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"641\" y=\"448\" fill=\"#38bdf8\" font-size=\"12\" text-anchor=\"middle\" style=\"fill: rgb(56, 189, 248); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 400; text-anchor: middle; visibility: visible; display: block;\">O</text><circle cx=\"524\" cy=\"432\" r=\"3\" fill=\"#34d399\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"524\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 400; text-anchor: middle; visibility: visible; display: block;\">F₁</text><circle cx=\"758\" cy=\"432\" r=\"3\" fill=\"#34d399\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"758\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 400; text-anchor: middle; visibility: visible; display: block;\">F₂</text><circle cx=\"407\" cy=\"432\" r=\"3\" fill=\"#34d399\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"407\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 400; text-anchor: middle; visibility: visible; display: block;\">2F₁</text><circle cx=\"875\" cy=\"432\" r=\"3\" fill=\"#34d399\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"875\" y=\"447\" fill=\"#34d399\" font-size=\"11\" text-anchor=\"middle\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 400; text-anchor: middle; visibility: visible; display: block;\">2F₂</text></g><g class=\"layer-shapes\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><g class=\"layer-rays\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"350.1\" stroke=\"#f59e0b\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(245, 158, 11); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"641\" y1=\"350.1\" x2=\"1280\" y2=\"797.4\" stroke=\"#f59e0b\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(245, 158, 11); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"432\" stroke=\"#38bdf8\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"641\" y1=\"432\" x2=\"1280\" y2=\"655.65\" stroke=\"#38bdf8\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"407\" y1=\"350.1\" x2=\"641\" y2=\"513.9\" stroke=\"#a855f7\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(168, 85, 247); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"641\" y1=\"513.9\" x2=\"1280\" y2=\"513.9\" stroke=\"#a855f7\" stroke-width=\"2\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(168, 85, 247); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></g><g class=\"layer-image\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><g class=\"optics-arrow\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><line x1=\"875\" y1=\"432\" x2=\"875\" y2=\"513.9\" stroke=\"#34d399\" stroke-width=\"3\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(52, 211, 153); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><polyline points=\"869,503.5076951545867 875,513.9 881,503.5076951545867\" stroke=\"#34d399\" stroke-width=\"3\" fill=\"none\" style=\"fill: none; fill-opacity: 1; stroke: rgb(52, 211, 153); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"875\" y=\"531.9\" fill=\"#34d399\" font-size=\"11\" font-weight=\"bold\" text-anchor=\"middle\" style=\"fill: rgb(52, 211, 153); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 700; text-anchor: middle; visibility: visible; display: block;\">Real Image</text></g></g><g class=\"layer-object\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><g class=\"optics-arrow\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><line x1=\"407\" y1=\"432\" x2=\"407\" y2=\"350.1\" stroke=\"#38bdf8\" stroke-width=\"3\" opacity=\"0.95\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 0.95; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><polyline points=\"413,360.4923048454133 407,350.1 401,360.4923048454133\" stroke=\"#38bdf8\" stroke-width=\"3\" fill=\"none\" style=\"fill: none; fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><text x=\"407\" y=\"340.1\" fill=\"#38bdf8\" font-size=\"11\" font-weight=\"bold\" text-anchor=\"middle\" style=\"fill: rgb(56, 189, 248); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 700; text-anchor: middle; visibility: visible; display: block;\">Object</text></g></g><g class=\"layer-handles\" style=\"pointer-events: auto; fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><circle cx=\"407\" cy=\"391.05\" r=\"9\" fill=\"rgba(56, 189, 248, 0.25)\" stroke=\"#38bdf8\" stroke-width=\"2\" cursor=\"ew-resize\" class=\"if-handle if-handle-object-pos\" data-handle=\"object_pos\" data-target-id=\"object_1\" data-param-address=\"objectDistance\" style=\"fill: rgba(56, 189, 248, 0.25); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><circle cx=\"407\" cy=\"350.1\" r=\"7\" fill=\"#38bdf8\" stroke=\"#ffffff\" stroke-width=\"2\" cursor=\"ns-resize\" class=\"if-handle if-handle-object-tip\" data-handle=\"object_tip\" data-target-id=\"object_1\" data-param-address=\"objectHeight\" style=\"fill: rgb(56, 189, 248); fill-opacity: 1; stroke: rgb(255, 255, 255); stroke-width: 2px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></g></svg>",
          "viewBox": "0 0 1280 960"
        }
      ],
      "browser_state": {
        "domain": "optics",
        "subtype": "thin_lens",
        "_other_fields_in_complete_snapshot": [
          "type",
          "running",
          "focalLength",
          "u",
          "v",
          "magnification",
          "imageType",
          "isReal",
          "isInverted",
          "rayCount",
          "solution"
        ]
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The rendered source landmarks should coincide with the printed diagram at t=0. This requires correct upstream geometry as well as correct transforms.

**What correct handling of THIS diagram requires:** Ground the whole lens/axis, object base and tip, image base and tip, focal markers and ray paths independently. A missing object detection must remain missing evidence, not become an assumed exploration object.

**Comparison / debugging conclusion:** Thin-lens runtime returns u=234, v=234, magnification=−1. No numerical solver defect is established. The actual t=0 renderer makes already incorrect source geometry visible.

**Changes, provenance and possible information loss:** Overlay image is captured from the actual canvas/SVG and projected back using measured DOM-to-source ratios. No objects were manually repositioned.

[Complete stage input/output bundle](stage_data/33_render.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

![runtime_t0_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/14_renderer/runtime_t0_overlay.png)

## 34. Activation, motion and reset

**Execution:** EXECUTED. **Verdict:** ACTUAL STATE CAPTURED.

**Upstream → downstream:** Actual renderer at t=0 over the original → this component → Final observed browser state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startSimulation",
    "phase": "input",
    "wallTime": 48827.40000000596,
    "data": []
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 48828.30000001192,
    "data": []
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 50281.70000001788,
    "data": []
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.reset",
    "phase": "input",
    "wallTime": 50287.80000001192,
    "data": []
  },
  {
    "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 50914.30000001192,
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
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startSimulation",
      "phase": "output",
      "wallTime": 48827.80000001192,
      "data": {
        "domain": "optics",
        "subtype": "thin_lens",
        "source": {
          "type": "book_figure",
          "source_asset_id": "dd013d21b8704bd296afcc9dcbc6a750",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_dd013d21.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "lens_center": {
            "x": 641,
            "y": 432
          },
          "lensX": 641,
          "axisY": 432,
          "aperture_height_px": 234,
          "_nested_fields_in_complete_snapshot": []
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "focalLength",
            "objectDistance",
            "objectHeight"
          ]
        },
        "assumptions": [
          {
            "parameter": "focal_length_px",
            "policyId": "policy_normalized_lens_focal_ratio",
            "policyVersion": "1.0",
            "value": 117,
            "unit": "px",
            "reason": "Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "objectDistance",
            "policyId": "policy_normalized_lens_object_distance",
            "policyVersion": "1.0",
            "value": 234,
            "unit": "px",
            "reason": "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          },
          {
            "parameter": "object_height_px",
            "policyId": "policy_normalized_lens_object_height",
            "policyVersion": "1.0",
            "value": 81.89999999999999,
            "unit": "px",
            "reason": "Use 35% of the measured lens aperture for an exploration object not printed in the diagram.",
            "provenance": "auto_policy",
            "confidence": 0.7,
            "_nested_fields_in_complete_snapshot": [
              "derivedFrom"
            ]
          }
        ],
        "_other_fields_in_complete_snapshot": [
          "schemaVersion",
          "id",
          "coordinateSpace",
          "coordinateSystem",
          "objects",
          "render",
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 48828.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 50281.70000001788,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.reset",
      "phase": "output",
      "wallTime": 50289.09999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 50914.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "after_play": {
        "traceId": "TRACE-LENS-20261016-001-NATIVE-RETRY-20261017",
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
          "renderer": "OpticsRenderer",
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
              "height": 600,
              "top": 227,
              "right": 1044,
              "bottom": 827,
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
              "height": 600,
              "top": 227,
              "right": 1044,
              "bottom": 827,
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
            "src": "http://127.0.0.1:5173/uploads/diagram_dd013d21.jpg",
            "naturalWidth": 1280,
            "naturalHeight": 960,
            "width": 800,
            "height": 600,
            "viewBox": null,
            "rect": {
              "x": 139,
              "y": 227,
              "width": 800,
              "height": 600,
              "top": 227,
              "right": 939,
              "bottom": 827,
              "left": 139
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
              "x": 139,
              "y": 227,
              "width": 800,
              "height": 600,
              "top": 227,
              "right": 939,
              "bottom": 827,
              "left": 139
            },
            "_nested_fields_in_complete_snapshot": [
              "css"
            ]
          },
          {
            "tag": "svg",
            "id": "",
            "className": "optics-overlay-svg",
            "src": null,
            "viewBox": "0 0 1280 960",
            "rect": {
              "x": 139,
              "y": 227,
              "width": 800,
              "height": 600,
              "top": 227,
              "right": 939,
              "bottom": 827,
              "left": 139
            },
            "_nested_fields_in_complete_snapshot": [
              "width",
              "height",
              "css"
            ]
          },
          {
            "tag": "IMG",
            "id": "diagram-image",
            "className": "diagram-image",
            "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207572089",
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
            "src": "blob:http://127.0.0.1:5173/643e338b-5bfb-43b1-ba53-dab43b65cd1a",
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

**What correct handling of THIS diagram requires:** At t=0 the object should occupy its printed arrow and the image/rays should be compared to the printed image/rays. The actual solver returns real_same_size from assumed u=2f, whereas the source depicts an enlarged image. This demonstrates an input/model mismatch, not an arithmetic failure.

**Comparison / debugging conclusion:** Automatic activation is observed in this checkout. Later frame time is whatever the runtime snapshot records, not an invented exact timestamp.

**Changes, provenance and possible information loss:** The executed main.js path automatically starts after a successful load. Later frames are saved at their actual times. Optics results are static ray solutions rather than pendulum-like time evolution.

[Complete stage input/output bundle](stage_data/34_motion.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/events.json)

- [Actual later browser frame](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/15_browser/runtime_after_play.png)

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

- **ingest_diagram** (1 calls): [1](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- **_get_ingestion_pipeline** (1 calls): [2](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00002__get_ingestion_pipeline/STAGE.html)

- **UploadService.ingest** (1 calls): [3](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

- **compute_sha256** (1 calls): [4](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00004_compute_sha256/STAGE.html)

- **UploadService.get_public_url** (1 calls): [5](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00005_UploadService.get_public_url/STAGE.html)

- **PageIRBuilder.build** (1 calls): [6](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- **BookUnderstandingPipeline.analyze** (1 calls): [7](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- **BookUnderstandingPipeline._get_analyzer** (1 calls): [8](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00008_BookUnderstandingPipeline._get_analyzer/STAGE.html)

- **PhysicsVisionAnalyzer.analyze** (1 calls): [9](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- **GeminiVisionProvider.analyze_diagram** (1 calls): [10](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- **GeminiVisionProvider._get_client** (1 calls): [11](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00011_GeminiVisionProvider._get_client/STAGE.html)

- **Models.generate_content** (1 calls): [12](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

- **Models._generate_content** (1 calls): [13](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00013_Models._generate_content/STAGE.html)

- **_discard_dangling_relationships** (1 calls): [14](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00014__discard_dangling_relationships/STAGE.html)

- **validate_semantic_payload** (1 calls): [15](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- **SemanticConfidence.from_dict** (1 calls): [16](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00016_SemanticConfidence.from_dict/STAGE.html)

- **_validate_confidence** (18 calls): [17](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00017__validate_confidence/STAGE.html), [18](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00018__validate_confidence/STAGE.html), [19](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00019__validate_confidence/STAGE.html), [20](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00020__validate_confidence/STAGE.html), [22](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00022__validate_confidence/STAGE.html), [24](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00024__validate_confidence/STAGE.html), [26](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00026__validate_confidence/STAGE.html), [28](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00028__validate_confidence/STAGE.html), [30](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00030__validate_confidence/STAGE.html), [32](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00032__validate_confidence/STAGE.html), [34](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00034__validate_confidence/STAGE.html), [36](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00036__validate_confidence/STAGE.html), [38](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00038__validate_confidence/STAGE.html), [40](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00040__validate_confidence/STAGE.html), [42](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00042__validate_confidence/STAGE.html), [44](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00044__validate_confidence/STAGE.html), [46](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00046__validate_confidence/STAGE.html), [48](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00048__validate_confidence/STAGE.html)

- **SemanticEntity.from_dict** (6 calls): [21](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00021_SemanticEntity.from_dict/STAGE.html), [23](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00023_SemanticEntity.from_dict/STAGE.html), [25](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00025_SemanticEntity.from_dict/STAGE.html), [27](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00027_SemanticEntity.from_dict/STAGE.html), [29](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00029_SemanticEntity.from_dict/STAGE.html), [31](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00031_SemanticEntity.from_dict/STAGE.html)

- **SemanticRelationship.from_dict** (2 calls): [33](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00033_SemanticRelationship.from_dict/STAGE.html), [35](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00035_SemanticRelationship.from_dict/STAGE.html)

- **SemanticVisibleLabel.from_dict** (6 calls): [37](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00037_SemanticVisibleLabel.from_dict/STAGE.html), [39](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00039_SemanticVisibleLabel.from_dict/STAGE.html), [41](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00041_SemanticVisibleLabel.from_dict/STAGE.html), [43](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00043_SemanticVisibleLabel.from_dict/STAGE.html), [45](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00045_SemanticVisibleLabel.from_dict/STAGE.html), [47](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00047_SemanticVisibleLabel.from_dict/STAGE.html)

- **PhysicsVisionAnalyzer._apply_thresholds** (1 calls): [49](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00049_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

- **BookUnderstandingPipeline._build_book_ir_from_result** (1 calls): [50](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00050_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- **SemanticAnalysisResult.is_supported** (1 calls): [51](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00051_SemanticAnalysisResult.is_supported/STAGE.html)

- **EvidenceExtractionPipeline.extract_and_fuse** (1 calls): [52](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00052_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- **GrounderRegistry.find_grounder** (1 calls): [53](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00053_GrounderRegistry.find_grounder/STAGE.html)

- **PendulumGrounder.supports** (1 calls): [54](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00054_PendulumGrounder.supports/STAGE.html)

- **ProjectileGrounder.supports** (1 calls): [55](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00055_ProjectileGrounder.supports/STAGE.html)

- **ThinLensGrounder.supports** (1 calls): [56](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00056_ThinLensGrounder.supports/STAGE.html)

- **load_and_validate_source_image** (1 calls): [57](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00057_load_and_validate_source_image/STAGE.html)

- **MultiOCRRouter.available** (1 calls): [58](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00058_MultiOCRRouter.available/STAGE.html)

- **RapidOCRProvider.available** (2 calls): [59](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00059_RapidOCRProvider.available/STAGE.html), [62](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00062_RapidOCRProvider.available/STAGE.html)

- **MultiOCRRouter.extract** (1 calls): [60](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00060_MultiOCRRouter.extract/STAGE.html)

- **RapidOCRProvider.extract** (1 calls): [61](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00061_RapidOCRProvider.extract/STAGE.html)

- **ImageTransform.identity** (2 calls): [63](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00063_ImageTransform.identity/STAGE.html), [118](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00118_ImageTransform.identity/STAGE.html)

- **RapidOCRProvider._get_engine** (1 calls): [64](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00064_RapidOCRProvider._get_engine/STAGE.html)

- **ImageTransform.to_source_point** (56 calls): [65](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00065_ImageTransform.to_source_point/STAGE.html), [66](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00066_ImageTransform.to_source_point/STAGE.html), [67](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00067_ImageTransform.to_source_point/STAGE.html), [68](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00068_ImageTransform.to_source_point/STAGE.html), [71](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00071_ImageTransform.to_source_point/STAGE.html), [72](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00072_ImageTransform.to_source_point/STAGE.html), [73](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00073_ImageTransform.to_source_point/STAGE.html), [74](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00074_ImageTransform.to_source_point/STAGE.html), [77](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00077_ImageTransform.to_source_point/STAGE.html), [78](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00078_ImageTransform.to_source_point/STAGE.html), [79](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00079_ImageTransform.to_source_point/STAGE.html), [80](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00080_ImageTransform.to_source_point/STAGE.html), [83](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00083_ImageTransform.to_source_point/STAGE.html), [84](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00084_ImageTransform.to_source_point/STAGE.html), [85](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00085_ImageTransform.to_source_point/STAGE.html), [86](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00086_ImageTransform.to_source_point/STAGE.html), [89](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00089_ImageTransform.to_source_point/STAGE.html), [90](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00090_ImageTransform.to_source_point/STAGE.html), [91](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00091_ImageTransform.to_source_point/STAGE.html), [92](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00092_ImageTransform.to_source_point/STAGE.html), [95](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00095_ImageTransform.to_source_point/STAGE.html), [96](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00096_ImageTransform.to_source_point/STAGE.html), [97](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00097_ImageTransform.to_source_point/STAGE.html), [98](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00098_ImageTransform.to_source_point/STAGE.html), [101](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00101_ImageTransform.to_source_point/STAGE.html), [102](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00102_ImageTransform.to_source_point/STAGE.html), [103](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00103_ImageTransform.to_source_point/STAGE.html), [104](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00104_ImageTransform.to_source_point/STAGE.html), [107](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00107_ImageTransform.to_source_point/STAGE.html), [108](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00108_ImageTransform.to_source_point/STAGE.html), [109](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00109_ImageTransform.to_source_point/STAGE.html), [110](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00110_ImageTransform.to_source_point/STAGE.html), [120](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00120_ImageTransform.to_source_point/STAGE.html), [121](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00121_ImageTransform.to_source_point/STAGE.html), [122](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00122_ImageTransform.to_source_point/STAGE.html), [123](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00123_ImageTransform.to_source_point/STAGE.html), [127](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00127_ImageTransform.to_source_point/STAGE.html), [128](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00128_ImageTransform.to_source_point/STAGE.html), [129](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00129_ImageTransform.to_source_point/STAGE.html), [130](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00130_ImageTransform.to_source_point/STAGE.html), [134](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00134_ImageTransform.to_source_point/STAGE.html), [135](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00135_ImageTransform.to_source_point/STAGE.html), [136](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00136_ImageTransform.to_source_point/STAGE.html), [137](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00137_ImageTransform.to_source_point/STAGE.html), [141](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00141_ImageTransform.to_source_point/STAGE.html), [142](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00142_ImageTransform.to_source_point/STAGE.html), [143](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00143_ImageTransform.to_source_point/STAGE.html), [144](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00144_ImageTransform.to_source_point/STAGE.html), [148](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00148_ImageTransform.to_source_point/STAGE.html), [149](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00149_ImageTransform.to_source_point/STAGE.html), [150](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00150_ImageTransform.to_source_point/STAGE.html), [151](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00151_ImageTransform.to_source_point/STAGE.html), [155](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00155_ImageTransform.to_source_point/STAGE.html), [156](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00156_ImageTransform.to_source_point/STAGE.html), [157](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00157_ImageTransform.to_source_point/STAGE.html), [158](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00158_ImageTransform.to_source_point/STAGE.html)

- **SourcePolygon.bbox** (14 calls): [69](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00069_SourcePolygon.bbox/STAGE.html), [75](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00075_SourcePolygon.bbox/STAGE.html), [81](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00081_SourcePolygon.bbox/STAGE.html), [87](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00087_SourcePolygon.bbox/STAGE.html), [93](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00093_SourcePolygon.bbox/STAGE.html), [99](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00099_SourcePolygon.bbox/STAGE.html), [105](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00105_SourcePolygon.bbox/STAGE.html), [111](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00111_SourcePolygon.bbox/STAGE.html), [124](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00124_SourcePolygon.bbox/STAGE.html), [131](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00131_SourcePolygon.bbox/STAGE.html), [138](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00138_SourcePolygon.bbox/STAGE.html), [145](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00145_SourcePolygon.bbox/STAGE.html), [152](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00152_SourcePolygon.bbox/STAGE.html), [159](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00159_SourcePolygon.bbox/STAGE.html)

- **RapidOCRProvider.name** (9 calls): [70](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00070_RapidOCRProvider.name/STAGE.html), [76](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00076_RapidOCRProvider.name/STAGE.html), [82](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00082_RapidOCRProvider.name/STAGE.html), [88](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00088_RapidOCRProvider.name/STAGE.html), [94](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00094_RapidOCRProvider.name/STAGE.html), [100](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00100_RapidOCRProvider.name/STAGE.html), [106](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00106_RapidOCRProvider.name/STAGE.html), [112](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00112_RapidOCRProvider.name/STAGE.html), [113](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00113_RapidOCRProvider.name/STAGE.html)

- **RapidOCRProvider.model_version** (1 calls): [114](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00114_RapidOCRProvider.model_version/STAGE.html)

- **EasyOCRBanglaProvider.available** (4 calls): [115](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00115_EasyOCRBanglaProvider.available/STAGE.html), [117](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00117_EasyOCRBanglaProvider.available/STAGE.html), [195](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00195_EasyOCRBanglaProvider.available/STAGE.html), [197](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00197_EasyOCRBanglaProvider.available/STAGE.html)

- **EasyOCRBanglaProvider.extract** (1 calls): [116](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00116_EasyOCRBanglaProvider.extract/STAGE.html)

- **EasyOCRBanglaProvider._get_reader** (1 calls): [119](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00119_EasyOCRBanglaProvider._get_reader/STAGE.html)

- **is_bengali_text** (12 calls): [125](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00125_is_bengali_text/STAGE.html), [132](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00132_is_bengali_text/STAGE.html), [139](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00139_is_bengali_text/STAGE.html), [146](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00146_is_bengali_text/STAGE.html), [153](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00153_is_bengali_text/STAGE.html), [160](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00160_is_bengali_text/STAGE.html), [163](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00163_is_bengali_text/STAGE.html), [164](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00164_is_bengali_text/STAGE.html), [165](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00165_is_bengali_text/STAGE.html), [166](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00166_is_bengali_text/STAGE.html), [167](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00167_is_bengali_text/STAGE.html), [168](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00168_is_bengali_text/STAGE.html)

- **EasyOCRBanglaProvider.name** (7 calls): [126](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00126_EasyOCRBanglaProvider.name/STAGE.html), [133](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00133_EasyOCRBanglaProvider.name/STAGE.html), [140](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00140_EasyOCRBanglaProvider.name/STAGE.html), [147](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00147_EasyOCRBanglaProvider.name/STAGE.html), [154](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00154_EasyOCRBanglaProvider.name/STAGE.html), [161](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00161_EasyOCRBanglaProvider.name/STAGE.html), [162](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00162_EasyOCRBanglaProvider.name/STAGE.html)

- **deduplicate_spatial_tokens** (1 calls): [169](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00169_deduplicate_spatial_tokens/STAGE.html)

- **deduplicate_spatial_tokens.<locals>.<lambda>** (8 calls): [170](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00170_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [171](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00171_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [172](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00172_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [173](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00173_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [174](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00174_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [175](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00175_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [176](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00176_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [177](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00177_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html)

- **GreekSymbolVisualOCR.extract_symbols** (1 calls): [178](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00178_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- **PhysicsSymbolCandidateResolver.enrich_token** (8 calls): [179](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00179_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [181](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00181_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [183](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00183_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [185](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00185_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [187](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00187_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [189](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00189_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [191](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00191_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [193](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00193_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- **generate_symbol_alternatives** (8 calls): [180](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00180_generate_symbol_alternatives/STAGE.html), [182](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00182_generate_symbol_alternatives/STAGE.html), [184](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00184_generate_symbol_alternatives/STAGE.html), [186](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00186_generate_symbol_alternatives/STAGE.html), [188](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00188_generate_symbol_alternatives/STAGE.html), [190](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00190_generate_symbol_alternatives/STAGE.html), [192](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00192_generate_symbol_alternatives/STAGE.html), [194](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00194_generate_symbol_alternatives/STAGE.html)

- **MultiOCRRouter.name** (1 calls): [196](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00196_MultiOCRRouter.name/STAGE.html)

- **GreekSymbolVisualOCR.available** (1 calls): [198](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00198_GreekSymbolVisualOCR.available/STAGE.html)

- **UnavailableFormulaRecognitionProvider.available** (1 calls): [199](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00199_UnavailableFormulaRecognitionProvider.available/STAGE.html)

- **ThinLensCVCandidateExtractor.extract** (1 calls): [200](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00200_ThinLensCVCandidateExtractor.extract/STAGE.html)

- **preprocess_for_geometry** (1 calls): [201](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00201_preprocess_for_geometry/STAGE.html)

- **preprocess_diagram** (1 calls): [202](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00202_preprocess_diagram/STAGE.html)

- **mask_out_text_regions** (1 calls): [203](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00203_mask_out_text_regions/STAGE.html)

- **math_floor** (16 calls): [204](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00204_math_floor/STAGE.html), [205](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00205_math_floor/STAGE.html), [208](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00208_math_floor/STAGE.html), [209](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00209_math_floor/STAGE.html), [212](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00212_math_floor/STAGE.html), [213](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00213_math_floor/STAGE.html), [216](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00216_math_floor/STAGE.html), [217](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00217_math_floor/STAGE.html), [220](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00220_math_floor/STAGE.html), [221](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00221_math_floor/STAGE.html), [224](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00224_math_floor/STAGE.html), [225](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00225_math_floor/STAGE.html), [228](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00228_math_floor/STAGE.html), [229](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00229_math_floor/STAGE.html), [232](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00232_math_floor/STAGE.html), [233](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00233_math_floor/STAGE.html)

- **math_ceil** (16 calls): [206](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00206_math_ceil/STAGE.html), [207](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00207_math_ceil/STAGE.html), [210](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00210_math_ceil/STAGE.html), [211](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00211_math_ceil/STAGE.html), [214](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00214_math_ceil/STAGE.html), [215](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00215_math_ceil/STAGE.html), [218](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00218_math_ceil/STAGE.html), [219](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00219_math_ceil/STAGE.html), [222](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00222_math_ceil/STAGE.html), [223](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00223_math_ceil/STAGE.html), [226](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00226_math_ceil/STAGE.html), [227](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00227_math_ceil/STAGE.html), [230](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00230_math_ceil/STAGE.html), [231](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00231_math_ceil/STAGE.html), [234](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00234_math_ceil/STAGE.html), [235](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00235_math_ceil/STAGE.html)

- **merge_collinear_lines** (1 calls): [236](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00236_merge_collinear_lines/STAGE.html)

- **point_to_segment_distance** (27 calls): [237](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00237_point_to_segment_distance/STAGE.html), [238](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00238_point_to_segment_distance/STAGE.html), [239](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00239_point_to_segment_distance/STAGE.html), [240](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00240_point_to_segment_distance/STAGE.html), [241](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00241_point_to_segment_distance/STAGE.html), [242](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00242_point_to_segment_distance/STAGE.html), [243](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00243_point_to_segment_distance/STAGE.html), [244](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00244_point_to_segment_distance/STAGE.html), [245](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00245_point_to_segment_distance/STAGE.html), [246](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00246_point_to_segment_distance/STAGE.html), [247](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00247_point_to_segment_distance/STAGE.html), [248](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00248_point_to_segment_distance/STAGE.html), [249](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00249_point_to_segment_distance/STAGE.html), [250](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00250_point_to_segment_distance/STAGE.html), [251](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00251_point_to_segment_distance/STAGE.html), [252](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00252_point_to_segment_distance/STAGE.html), [253](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00253_point_to_segment_distance/STAGE.html), [254](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00254_point_to_segment_distance/STAGE.html), [255](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00255_point_to_segment_distance/STAGE.html), [256](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00256_point_to_segment_distance/STAGE.html), [257](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00257_point_to_segment_distance/STAGE.html), [258](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00258_point_to_segment_distance/STAGE.html), [259](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00259_point_to_segment_distance/STAGE.html), [260](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00260_point_to_segment_distance/STAGE.html), [261](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00261_point_to_segment_distance/STAGE.html), [262](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00262_point_to_segment_distance/STAGE.html), [263](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00263_point_to_segment_distance/STAGE.html)

- **SourceLine.length_px** (9 calls): [264](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00264_SourceLine.length_px/STAGE.html), [266](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00266_SourceLine.length_px/STAGE.html), [268](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00268_SourceLine.length_px/STAGE.html), [270](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00270_SourceLine.length_px/STAGE.html), [274](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00274_SourceLine.length_px/STAGE.html), [276](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00276_SourceLine.length_px/STAGE.html), [278](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00278_SourceLine.length_px/STAGE.html), [281](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00281_SourceLine.length_px/STAGE.html), [285](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00285_SourceLine.length_px/STAGE.html)

- **SourcePoint.distance_to** (9 calls): [265](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00265_SourcePoint.distance_to/STAGE.html), [267](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00267_SourcePoint.distance_to/STAGE.html), [269](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00269_SourcePoint.distance_to/STAGE.html), [271](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00271_SourcePoint.distance_to/STAGE.html), [275](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00275_SourcePoint.distance_to/STAGE.html), [277](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00277_SourcePoint.distance_to/STAGE.html), [279](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00279_SourcePoint.distance_to/STAGE.html), [282](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00282_SourcePoint.distance_to/STAGE.html), [286](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00286_SourcePoint.distance_to/STAGE.html)

- **ThinLensCVCandidateExtractor.extract.<locals>.<lambda>** (3 calls): [272](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00272_ThinLensCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [273](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00273_ThinLensCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [280](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00280_ThinLensCVCandidateExtractor.extract._locals_._lambda_/STAGE.html)

- **ThinLensGrounder.ground** (1 calls): [283](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00283_ThinLensGrounder.ground/STAGE.html)

- **ThinLensGrounder.fuse** (1 calls): [284](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00284_ThinLensGrounder.fuse/STAGE.html)

- **parse_physical_value_candidate** (8 calls): [287](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00287_parse_physical_value_candidate/STAGE.html), [289](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00289_parse_physical_value_candidate/STAGE.html), [293](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00293_parse_physical_value_candidate/STAGE.html), [295](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00295_parse_physical_value_candidate/STAGE.html), [297](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00297_parse_physical_value_candidate/STAGE.html), [299](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00299_parse_physical_value_candidate/STAGE.html), [301](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00301_parse_physical_value_candidate/STAGE.html), [303](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00303_parse_physical_value_candidate/STAGE.html)

- **normalize_ocr_text** (9 calls): [288](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00288_normalize_ocr_text/STAGE.html), [290](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00290_normalize_ocr_text/STAGE.html), [291](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00291_normalize_ocr_text/STAGE.html), [294](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00294_normalize_ocr_text/STAGE.html), [296](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00296_normalize_ocr_text/STAGE.html), [298](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00298_normalize_ocr_text/STAGE.html), [300](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00300_normalize_ocr_text/STAGE.html), [302](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00302_normalize_ocr_text/STAGE.html), [304](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00304_normalize_ocr_text/STAGE.html)

- **ParsedPhysicalValueCandidate.token_id** (1 calls): [292](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00292_ParsedPhysicalValueCandidate.token_id/STAGE.html)

- **enforce_source_dimensions** (1 calls): [305](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00305_enforce_source_dimensions/STAGE.html)

- **AutoResolutionEngine.resolve** (1 calls): [306](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00306_AutoResolutionEngine.resolve/STAGE.html)

- **RequirementRegistry.get_spec** (8 calls): [307](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00307_RequirementRegistry.get_spec/STAGE.html), [322](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00322_RequirementRegistry.get_spec/STAGE.html), [335](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00335_RequirementRegistry.get_spec/STAGE.html), [344](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00344_RequirementRegistry.get_spec/STAGE.html), [359](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00359_RequirementRegistry.get_spec/STAGE.html), [372](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00372_RequirementRegistry.get_spec/STAGE.html), [411](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00411_RequirementRegistry.get_spec/STAGE.html), [424](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00424_RequirementRegistry.get_spec/STAGE.html)

- **_grounded_value** (2 calls): [308](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00308__grounded_value/STAGE.html), [309](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00309__grounded_value/STAGE.html)

- **_inside_source** (2 calls): [310](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00310__inside_source/STAGE.html), [315](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00315__inside_source/STAGE.html)

- **AutoResolutionEngine._normalize_lens_focal_length** (1 calls): [311](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00311_AutoResolutionEngine._normalize_lens_focal_length/STAGE.html)

- **PolicyRegistry.get_policy** (8 calls): [312](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00312_PolicyRegistry.get_policy/STAGE.html), [316](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00316_PolicyRegistry.get_policy/STAGE.html), [318](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00318_PolicyRegistry.get_policy/STAGE.html), [346](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00346_PolicyRegistry.get_policy/STAGE.html), [348](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00348_PolicyRegistry.get_policy/STAGE.html), [350](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00350_PolicyRegistry.get_policy/STAGE.html), [352](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00352_PolicyRegistry.get_policy/STAGE.html), [354](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00354_PolicyRegistry.get_policy/STAGE.html)

- **PolicyRegistry.get** (8 calls): [313](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00313_PolicyRegistry.get/STAGE.html), [317](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00317_PolicyRegistry.get/STAGE.html), [319](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00319_PolicyRegistry.get/STAGE.html), [347](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00347_PolicyRegistry.get/STAGE.html), [349](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00349_PolicyRegistry.get/STAGE.html), [351](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00351_PolicyRegistry.get/STAGE.html), [353](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00353_PolicyRegistry.get/STAGE.html), [355](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00355_PolicyRegistry.get/STAGE.html)

- **AutoResolutionEngine._normalize_lens_exploration_object** (1 calls): [314](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00314_AutoResolutionEngine._normalize_lens_exploration_object/STAGE.html)

- **ReadinessEvaluator.evaluate** (3 calls): [320](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00320_ReadinessEvaluator.evaluate/STAGE.html), [357](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00357_ReadinessEvaluator.evaluate/STAGE.html), [409](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00409_ReadinessEvaluator.evaluate/STAGE.html)

- **ResolutionAnalyzer.analyze** (3 calls): [321](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00321_ResolutionAnalyzer.analyze/STAGE.html), [358](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00358_ResolutionAnalyzer.analyze/STAGE.html), [410](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00410_ResolutionAnalyzer.analyze/STAGE.html)

- **ResolutionAnalyzer._check_geometry_requirements** (3 calls): [323](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00323_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [360](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00360_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [412](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00412_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- **ResolutionAnalyzer._check_parameter_requirements** (3 calls): [324](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00324_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [361](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00361_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [413](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00413_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- **ModelRequirementSpec.required_parameters** (6 calls): [325](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00325_ModelRequirementSpec.required_parameters/STAGE.html), [336](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00336_ModelRequirementSpec.required_parameters/STAGE.html), [362](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00362_ModelRequirementSpec.required_parameters/STAGE.html), [373](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00373_ModelRequirementSpec.required_parameters/STAGE.html), [414](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00414_ModelRequirementSpec.required_parameters/STAGE.html), [425](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00425_ModelRequirementSpec.required_parameters/STAGE.html)

- **ResolutionAnalyzer._check_optional_parameters** (3 calls): [326](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00326_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [363](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00363_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [415](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00415_ResolutionAnalyzer._check_optional_parameters/STAGE.html)

- **ModelRequirementSpec.optional_parameters** (3 calls): [327](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00327_ModelRequirementSpec.optional_parameters/STAGE.html), [364](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00364_ModelRequirementSpec.optional_parameters/STAGE.html), [416](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00416_ModelRequirementSpec.optional_parameters/STAGE.html)

- **PolicyRegistry.find_policy** (3 calls): [328](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00328_PolicyRegistry.find_policy/STAGE.html), [365](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00365_PolicyRegistry.find_policy/STAGE.html), [417](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00417_PolicyRegistry.find_policy/STAGE.html)

- **PolicyRegistry.find_policies_for_parameter** (3 calls): [329](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00329_PolicyRegistry.find_policies_for_parameter/STAGE.html), [366](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00366_PolicyRegistry.find_policies_for_parameter/STAGE.html), [418](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00418_PolicyRegistry.find_policies_for_parameter/STAGE.html)

- **PolicyRegistry.get_policies_for_subtype** (3 calls): [330](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00330_PolicyRegistry.get_policies_for_subtype/STAGE.html), [367](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00367_PolicyRegistry.get_policies_for_subtype/STAGE.html), [419](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00419_PolicyRegistry.get_policies_for_subtype/STAGE.html)

- **PolicyRegistry.list_all** (3 calls): [331](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00331_PolicyRegistry.list_all/STAGE.html), [368](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00368_PolicyRegistry.list_all/STAGE.html), [420](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00420_PolicyRegistry.list_all/STAGE.html)

- **ResolutionPolicy.policy_id** (9 calls): [332](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00332_ResolutionPolicy.policy_id/STAGE.html), [333](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00333_ResolutionPolicy.policy_id/STAGE.html), [334](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00334_ResolutionPolicy.policy_id/STAGE.html), [369](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00369_ResolutionPolicy.policy_id/STAGE.html), [370](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00370_ResolutionPolicy.policy_id/STAGE.html), [371](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00371_ResolutionPolicy.policy_id/STAGE.html), [421](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00421_ResolutionPolicy.policy_id/STAGE.html), [422](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00422_ResolutionPolicy.policy_id/STAGE.html), [423](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00423_ResolutionPolicy.policy_id/STAGE.html)

- **UnitEngine.parse_quantity** (6 calls): [337](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00337_UnitEngine.parse_quantity/STAGE.html), [340](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00340_UnitEngine.parse_quantity/STAGE.html), [374](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00374_UnitEngine.parse_quantity/STAGE.html), [377](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00377_UnitEngine.parse_quantity/STAGE.html), [426](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00426_UnitEngine.parse_quantity/STAGE.html), [429](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00429_UnitEngine.parse_quantity/STAGE.html)

- **UnitEngine.lookup_unit** (6 calls): [338](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00338_UnitEngine.lookup_unit/STAGE.html), [341](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00341_UnitEngine.lookup_unit/STAGE.html), [375](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00375_UnitEngine.lookup_unit/STAGE.html), [378](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00378_UnitEngine.lookup_unit/STAGE.html), [427](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00427_UnitEngine.lookup_unit/STAGE.html), [430](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00430_UnitEngine.lookup_unit/STAGE.html)

- **UnitEngine.validate_range** (6 calls): [339](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00339_UnitEngine.validate_range/STAGE.html), [342](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00342_UnitEngine.validate_range/STAGE.html), [376](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00376_UnitEngine.validate_range/STAGE.html), [379](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00379_UnitEngine.validate_range/STAGE.html), [428](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00428_UnitEngine.validate_range/STAGE.html), [431](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00431_UnitEngine.validate_range/STAGE.html)

- **ResolutionEngine.auto_resolve** (1 calls): [343](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00343_ResolutionEngine.auto_resolve/STAGE.html)

- **CalibrationEngine.derive_for_subtype** (2 calls): [345](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00345_CalibrationEngine.derive_for_subtype/STAGE.html), [356](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00356_CalibrationEngine.derive_for_subtype/STAGE.html)

- **PhysicsCompiler.compile** (1 calls): [380](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00380_PhysicsCompiler.compile/STAGE.html)

- **PhysicsCompiler._validate_grounding** (1 calls): [381](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00381_PhysicsCompiler._validate_grounding/STAGE.html)

- **PhysicsCompiler._extract_source_dimensions** (2 calls): [382](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00382_PhysicsCompiler._extract_source_dimensions/STAGE.html), [433](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00433_PhysicsCompiler._extract_source_dimensions/STAGE.html)

- **PhysicsCompiler._extract_raw_val** (17 calls): [383](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00383_PhysicsCompiler._extract_raw_val/STAGE.html), [384](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00384_PhysicsCompiler._extract_raw_val/STAGE.html), [386](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00386_PhysicsCompiler._extract_raw_val/STAGE.html), [387](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00387_PhysicsCompiler._extract_raw_val/STAGE.html), [392](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00392_PhysicsCompiler._extract_raw_val/STAGE.html), [402](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00402_PhysicsCompiler._extract_raw_val/STAGE.html), [404](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00404_PhysicsCompiler._extract_raw_val/STAGE.html), [434](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00434_PhysicsCompiler._extract_raw_val/STAGE.html), [435](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00435_PhysicsCompiler._extract_raw_val/STAGE.html), [437](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00437_PhysicsCompiler._extract_raw_val/STAGE.html), [438](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00438_PhysicsCompiler._extract_raw_val/STAGE.html), [443](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00443_PhysicsCompiler._extract_raw_val/STAGE.html), [445](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00445_PhysicsCompiler._extract_raw_val/STAGE.html), [447](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00447_PhysicsCompiler._extract_raw_val/STAGE.html), [451](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00451_PhysicsCompiler._extract_raw_val/STAGE.html), [454](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00454_PhysicsCompiler._extract_raw_val/STAGE.html), [455](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00455_PhysicsCompiler._extract_raw_val/STAGE.html)

- **_first_not_none** (15 calls): [385](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00385__first_not_none/STAGE.html), [388](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00388__first_not_none/STAGE.html), [390](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00390__first_not_none/STAGE.html), [393](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00393__first_not_none/STAGE.html), [396](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00396__first_not_none/STAGE.html), [400](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00400__first_not_none/STAGE.html), [405](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00405__first_not_none/STAGE.html), [406](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00406__first_not_none/STAGE.html), [436](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00436__first_not_none/STAGE.html), [439](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00439__first_not_none/STAGE.html), [441](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00441__first_not_none/STAGE.html), [444](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00444__first_not_none/STAGE.html), [446](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00446__first_not_none/STAGE.html), [449](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00449__first_not_none/STAGE.html), [453](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00453__first_not_none/STAGE.html)

- **PhysicsCompiler._validate_parameters** (1 calls): [389](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00389_PhysicsCompiler._validate_parameters/STAGE.html)

- **PhysicsCompiler._extract_point** (5 calls): [391](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00391_PhysicsCompiler._extract_point/STAGE.html), [401](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00401_PhysicsCompiler._extract_point/STAGE.html), [403](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00403_PhysicsCompiler._extract_point/STAGE.html), [442](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00442_PhysicsCompiler._extract_point/STAGE.html), [450](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00450_PhysicsCompiler._extract_point/STAGE.html)

- **_extract_val_and_unit** (3 calls): [394](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00394__extract_val_and_unit/STAGE.html), [397](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00397__extract_val_and_unit/STAGE.html), [407](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00407__extract_val_and_unit/STAGE.html)

- **_validate_and_convert_unit** (3 calls): [395](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00395__validate_and_convert_unit/STAGE.html), [398](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00398__validate_and_convert_unit/STAGE.html), [408](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00408__validate_and_convert_unit/STAGE.html)

- **PhysicsCompiler._find_entity** (3 calls): [399](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00399_PhysicsCompiler._find_entity/STAGE.html), [448](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00448_PhysicsCompiler._find_entity/STAGE.html), [452](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00452_PhysicsCompiler._find_entity/STAGE.html)

- **PhysicsCompiler._build_canonical_scene** (1 calls): [432](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00432_PhysicsCompiler._build_canonical_scene/STAGE.html)

- **PhysicsCompiler._populate_canonical_lens** (1 calls): [440](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00440_PhysicsCompiler._populate_canonical_lens/STAGE.html)

- **PhysicsCompiler._preserve_parameter_provenance** (1 calls): [456](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00456_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- **validate_canonical_scene** (1 calls): [457](../../../../storage/generated/debug_traces/20261016/TRACE-LENS-20261016-001-NATIVE-RETRY-20261017/calls/00457_validate_canonical_scene/STAGE.html)

## Appendix B. First failure and propagation

Last known good: Source identity, semantic subtype and selected OCR focal-length text (15 cm).

First suspicious: Secondary OCR misreads the focal label; router retains the correct RapidOCR result. The Object OCR box (188,220,135,57) is valid text evidence, but its four-pixel expansion reaches adjacent ray geometry.

First definitive failure: OCR edge masking erases part of the incident ray beside the Object label; CV subsequently omits the printed object arrow and selects a partial lens centerline.

Downstream chain: Grounder retains the center/partial aperture and observes focal_length=0.15 m from OCR, but does not ground the object or printed focal-marker spacing. _normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace. Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.

Separation of failure classes: preprocessing/perception is demonstrated upstream; a shared coordinate conversion error is not demonstrated; numerical solver failure is not established. The circuit never reaches a solver.

## Appendix C. Capture limits

No new run was performed. The recorder captured repository Python boundaries and GenAI model calls, not private neural-library/C internals. JS boundary events, normalized scenes, actual solver outputs and DOM captures exist; separate entry/exit snapshots for every registry/adapter/renderer child function do not. These gaps are labeled, not filled with reconstructed output. Several void JS returns appear as captureError because undefined is not JSON; resulting state is separately recorded. Two class-serialization errors exist in the historical recorder log; integrity verification found the required snapshot files present for every indexed call. No exact expected pixel dataset, mask or numerical physical state has been authored.

[Original trace integrity checks](../../../../storage/generated/debug_traces/20261017/artifact_verification.json)
