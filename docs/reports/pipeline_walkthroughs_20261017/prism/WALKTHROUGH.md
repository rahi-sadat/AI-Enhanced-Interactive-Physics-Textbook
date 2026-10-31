# Glass prism: complete component-by-component debugging walkthrough

Trace ID: `TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017`. These documents use the existing live native Windows request from 2026-10-17. No models, detectors or solvers were rerun while writing them. No production fixes were made.

Source reference: A triangular glass prism with A=60°, an incident ray, internal and emergent rays, face normals, and symbolic incidence/refraction/emergence/deviation angles.

Known and unknown evidence: 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

Expected geometry for this diagram: Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

Expected initial simulation: At t=0 the prism polygon and ray segments should be compared with the printed paths. If a physical model with assumed n disagrees with the schematic, expose that disagreement; do not claim the computed path is observed source geometry.

Exact expected coordinates/masks are unavailable: EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS. Expected behavior below is a contract or a qualitative source comparison, never a hand-drawn expected result.

![Unchanged original diagram](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/00_source/original.png)

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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "source": "C:\\Users\\saher\\Downloads\\photo_2026-10-10_12-06-37.jpg",
      "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
      "bytes": 59343
    },
    "metadata": {
      "file_format": "JPEG",
      "encoded_width": 1280,
      "encoded_height": 960,
      "EXIF_orientation": null,
      "orientation": "landscape",
      "decoded_width": 1280,
      "decoded_height": 960,
      "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
      "png_note": "Lossless serialization of OpenCV decoded original JPEG; no resize, crop, redrawing, or orientation edit. Byte-exact original.jpg retained.",
      "decoded_pixels_sha256": "dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb",
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
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207801526",
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
          "src": "blob:http://127.0.0.1:5173/782199ea-9e13-4271-86f0-8964fb495844",
          "naturalWidth": 1280,
          "naturalHeight": 960,
          "width": 224,
          "height": 168,
          "viewBox": null,
          "rect": {
            "x": 596,
            "y": 249.5,
            "width": 226,
            "height": 170,
            "top": 249.5,
            "right": 822,
            "bottom": 419.5,
            "left": 596
          },
          "_nested_fields_in_complete_snapshot": [
            "css"
          ]
        }
      ]
    }
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startWithFile",
    "phase": "input",
    "wallTime": 3188.2000000178814,
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startWithFile",
      "phase": "output",
      "wallTime": 34133.40000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** One upload operation: first UPLOADING, then a response-governed final state. This outer async call spans the rest of the pipeline; it must not invent a scene locally.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** File → multipart request. The generic JS File snapshot is {}, so use multipart metadata and the byte-exact source, not {} as evidence of an empty file.

[Complete stage input/output bundle](stage_data/01_upload.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 02. HTTP request reaches /api/ingest

**Execution:** EXECUTED. **Verdict:** PASS.

**Upstream → downstream:** Browser selects the original diagram → this component → Upload persistence and dimension decoding.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "trace_id": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
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
          "59546"
        ],
        [
          "x-physics-trace-id",
          "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017"
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
          "multipart/form-data; boundary=----WebKitFormBoundaryJiLVBViOZwT647Df"
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Browser transport → FastAPI handler. Handler parameter is opaque in the profiler; saved multipart bytes are the authoritative payload.

[Complete stage input/output bundle](stage_data/02_http_in.json)

- [Exact multipart body](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/http/1792207803683424300_request_body.bin)

- [HTTP response 1792207803683424300_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/http/1792207803683424300_response_body.json)

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
        "bytes": 59343,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2.bin"
      },
      "original_filename": "photo_2026-10-10_12-06-37.jpg",
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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** SourceAsset with storage path/public URL, content hash, native decoded dimensions and original filename.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** Encoded bytes are persisted; metadata and an asset ID are added. This is not object detection.

[Complete stage input/output bundle](stage_data/03_asset.json)

- [UploadService.ingest — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
      },
      "public_url": "/uploads/diagram_2a50897a.jpg"
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
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** SourceAsset → PageIR. The whole image is user-supplied; confidence in that extent does not imply confidence in physics landmarks.

[Complete stage input/output bundle](stage_data/04_page.json)

- [PageIRBuilder.build — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- [Code: ai\ingestion\PageIRBuilder.py](contracts/ai/ingestion/PageIRBuilder.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/actual_overlay_on_source.png)

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
        "bytes": 59343,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2.bin"
      },
      "mime_type": "image/jpeg",
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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
              "bytes": 59343,
              "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
              "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2.bin"
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
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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
            "date": "Sat, 17 Oct 2026 03:30:09 GMT",
            "server": "scaffolding on HTTPServer2",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "x-content-type-options": "nosniff",
            "server-timing": "gfet4t7; dur=5413",
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
                  "text": "{\n  \"classification\": \"supported\",\n  \"isPhysics\": true,\n  \"domain\": \"optics\",\n  \"subtype\": \"prism\",\n  \"confidence\": {\n    \"isPhysics\": 1.0,\n    \"domain\": 1.0,\n    \"subtype\": 1.0,\n    \"overall\": 1.0\n  },\n  \"entities\": [\n    {\n      \"temporaryId\": \"prism_1\",\n      \"role\": \"prism_body\",\n      \"label\": \"Glass Prism\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"ray_1\",\n      \"role\": \"incident_ray\",\n      \"label\": \"Incident ray\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"ray_2\",\n      \"role\": \"refracted_ray\",\n      \"confidence\": 0.95\n    },\n    {\n      \"temporaryId\": \"ray_3\",\n      \"role\": \"emergent_ray\",\n      \"label\": \"Emergent ray\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"normal_1\",\n      \"role\": \"normal_line\",\n      \"label\": \"N1\",\n      \"confidence\": 1.0\n    },\n    {\n      \"temporaryId\": \"normal_2\",\n      \"role\": \"normal_line\",\n      \"label\": \"N2\",\n      \"confidence\": 1.0\n    }\n  ],\n  \"relationships\": [\n    {\n      \"type\": \"refracts_at\",\n      \"from\": \"ray_1\",\n      \"to\": \"prism_1\",\n      \"confidence\": 0.95\n    },\n    {\n      \"type\": \"refracts_at\",\n      \"from\": \"prism_1\",\n      \"to\": \"ray_3\",\n      \"confidence\": 0.95\n    }\n  ],\n  \"visibleLabels\": [\n    {\n      \"text\": \"A = 60°\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"prism_angle\"\n    },\n    {\n      \"text\": \"i\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle_of_incidence\"\n    },\n    {\n      \"text\": \"r1\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle_of_refraction\"\n    },\n    {\n      \"text\": \"r2\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle_of_incidence_internal\"\n    },\n    {\n      \"text\": \"e\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle_of_emergence\"\n    },\n    {\n      \"text\": \"δ\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"angle_of_deviation\"\n    },\n    {\n      \"text\": \"Fig. 8 Refraction through a Prism\",\n      \"confidence\": 1.0,\n      \"semanticRole\": \"caption\"\n    }\n  ],\n  \"candidates\": [],\n  \"notes\": [\n    \"Standard textbook diagram of light refraction through a triangular glass prism.\"\n  ]\n}",
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
        "response_id": "vevSas3FFbiX4-EPwZaMiAg",
        "usage_metadata": {
          "cache_tokens_details": null,
          "cached_content_token_count": null,
          "candidates_token_count": 777,
          "candidates_tokens_details": null,
          "prompt_token_count": 2233,
          "prompt_tokens_details": [
            {
              "modality": "IMAGE",
              "token_count": 1064
            },
            {
              "modality": "TEXT",
              "token_count": 1169
            }
          ],
          "thoughts_token_count": null,
          "tool_use_prompt_token_count": null,
          "tool_use_prompt_tokens_details": null,
          "total_token_count": 3010,
          "traffic_type": null
        },
        "model_status": null,
        "automatic_function_calling_history": [],
        "parsed": {
          "classification": "supported",
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "confidence": {
            "isPhysics": 1.0,
            "domain": 1.0,
            "subtype": 1.0,
            "overall": 1.0
          },
          "entities": [
            {
              "temporaryId": "prism_1",
              "role": "prism_body",
              "label": "Glass Prism",
              "confidence": 1.0
            },
            {
              "temporaryId": "ray_1",
              "role": "incident_ray",
              "label": "Incident ray",
              "confidence": 1.0
            },
            {
              "temporaryId": "ray_2",
              "role": "refracted_ray",
              "confidence": 0.95
            },
            {
              "temporaryId": "ray_3",
              "role": "emergent_ray",
              "label": "Emergent ray",
              "confidence": 1.0
            },
            {
              "temporaryId": "normal_1",
              "role": "normal_line",
              "label": "N1",
              "confidence": 1.0
            },
            {
              "temporaryId": "normal_2",
              "role": "normal_line",
              "label": "N2",
              "confidence": 1.0
            }
          ],
          "relationships": [
            {
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
              "confidence": 0.95
            }
          ],
          "visibleLabels": [
            {
              "text": "A = 60°",
              "confidence": 1.0,
              "semanticRole": "prism_angle"
            },
            {
              "text": "i",
              "confidence": 1.0,
              "semanticRole": "angle_of_incidence"
            },
            {
              "text": "r1",
              "confidence": 1.0,
              "semanticRole": "angle_of_refraction"
            },
            {
              "text": "r2",
              "confidence": 1.0,
              "semanticRole": "angle_of_incidence_internal"
            },
            {
              "text": "e",
              "confidence": 1.0,
              "semanticRole": "angle_of_emergence"
            },
            {
              "text": "δ",
              "confidence": 1.0,
              "semanticRole": "angle_of_deviation"
            },
            {
              "text": "Fig. 8 Refraction through a Prism",
              "confidence": 1.0,
              "semanticRole": "caption"
            }
          ],
          "candidates": [],
          "notes": [
            "Standard textbook diagram of light refraction through a triangular glass prism."
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Semantic classification, domain/subtype, entity roles and relationships. Numerical physical parameters and authoritative geometry must not originate here.

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / prism. Expected semantic content: A triangular glass prism with A=60°, an incident ray, internal and emergent rays, face normals, and symbolic incidence/refraction/emergence/deviation angles. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Image → model response. SDK/provider-internal preprocessing and private tensors were not exposed; no transform is invented for them.

[Complete stage input/output bundle](stage_data/05_vlm.json)

- [GeminiVisionProvider.analyze_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- [Models.generate_content — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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
        "subtype": "prism",
        "confidence": {
          "isPhysics": 1.0,
          "domain": 1.0,
          "subtype": 1.0,
          "overall": 1.0
        },
        "entities": [
          {
            "temporaryId": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 1.0
          },
          {
            "temporaryId": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 1.0
          },
          {
            "temporaryId": "ray_2",
            "role": "refracted_ray",
            "confidence": 0.95
          },
          {
            "temporaryId": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 1.0
          },
          {
            "temporaryId": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 1.0
          },
          {
            "temporaryId": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 1.0
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
            "confidence": 0.95
          }
        ],
        "visibleLabels": [
          {
            "text": "A = 60°",
            "confidence": 1.0,
            "semanticRole": "prism_angle"
          },
          {
            "text": "i",
            "confidence": 1.0,
            "semanticRole": "angle_of_incidence"
          },
          {
            "text": "r1",
            "confidence": 1.0,
            "semanticRole": "angle_of_refraction"
          },
          {
            "text": "r2",
            "confidence": 1.0,
            "semanticRole": "angle_of_incidence_internal"
          },
          {
            "text": "e",
            "confidence": 1.0,
            "semanticRole": "angle_of_emergence"
          },
          {
            "text": "δ",
            "confidence": 1.0,
            "semanticRole": "angle_of_deviation"
          },
          {
            "text": "Fig. 8 Refraction through a Prism",
            "confidence": 1.0,
            "semanticRole": "caption"
          }
        ],
        "candidates": [],
        "notes": [
          "Standard textbook diagram of light refraction through a triangular glass prism."
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
        "domain": "optics",
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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
        "domain": "optics",
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / prism. Expected semantic content: A triangular glass prism with A=60°, an incident ray, internal and emergent rays, face normals, and symbolic incidence/refraction/emergence/deviation angles. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Raw semantic response → validated semantic representation. Compare raw_provider confidence with the capped accepted values.

[Complete stage input/output bundle](stage_data/06_semantic.json)

- [PhysicsVisionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- [validate_semantic_payload — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- [PhysicsVisionAnalyzer._apply_thresholds — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00051_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

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
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
      }
    }
  },
  {
    "call": "00052_BookUnderstandingPipeline._build_book_ir_from_result",
    "value": {
      "result": {
        "classification": "supported",
        "is_physics": true,
        "domain": "optics",
        "subtype": "prism",
        "entities": [
          {
            "temporary_id": "prism_1",
            "role": "prism_body",
            "label": "Glass Prism",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_1",
            "role": "incident_ray",
            "label": "Incident ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_2",
            "role": "refracted_ray",
            "label": null,
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "ray_3",
            "role": "emergent_ray",
            "label": "Emergent ray",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_1",
            "role": "normal_line",
            "label": "N1",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          },
          {
            "temporary_id": "normal_2",
            "role": "normal_line",
            "label": "N2",
            "confidence": 0.95,
            "approx_bbox": null,
            "precision": "approximate"
          }
        ],
        "relationships": [
          {
            "type": "refracts_at",
            "source_id": "ray_1",
            "target_id": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "source_id": "prism_1",
            "target_id": "ray_3",
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
      "asset_id": "2a50897a2e704e7aa51642dab568571b",
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
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
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
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
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
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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

**What correct handling of THIS diagram requires:** Expected accepted classification: supported; isPhysics=true; domain/subtype=optics / prism. Expected semantic content: A triangular glass prism with A=60°, an incident ray, internal and emergent rays, face normals, and symbolic incidence/refraction/emergence/deviation angles. These are semantic roles/labels, not authorization to supply numerical parameters or precise positions.

**Comparison / debugging conclusion:** Accepted domain/subtype agrees with the source. Semantic-only output is appropriate here; missing source geometry is intentional. Raw provider confidence can be 1.0; accepted confidence is capped by validation.

**Changes, provenance and possible information loss:** Semantic roles are assigned durable entity IDs. This BookIR is an intermediate hypothesis, not a runnable simulation.

[Complete stage input/output bundle](stage_data/07_book.json)

- [BookUnderstandingPipeline.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- [BookUnderstandingPipeline._build_book_ir_from_result — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00052_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

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
      "domain": "optics",
      "subtype": "prism"
    }
  },
  {
    "call": "00062_load_and_validate_source_image",
    "value": {
      "asset": {
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
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
        "type": "ai.evidence.grounding.prism.PrismGrounder",
        "not_serialized": true
      }
    },
    {
      "call": "00062_load_and_validate_source_image",
      "return_value": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The matching subtype grounder and the unchanged native BGR image array; decoder dimensions must match the asset.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Original identity and native dimensions are preserved. This pass applies to transport/frame integrity, not landmark accuracy.

**Changes, provenance and possible information loss:** The pipeline routes to the domain module. Other grounders may execute supports() checks; their ground() methods are not thereby executed.

[Complete stage input/output bundle](stage_data/08_route.json)

- [GrounderRegistry.find_grounder — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00055_GrounderRegistry.find_grounder/STAGE.html)

- [load_and_validate_source_image — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00062_load_and_validate_source_image/STAGE.html)

- [Code: ai\evidence\grounding\registry.py](contracts/ai/evidence/grounding/registry.py)

- [Code: ai\evidence\transforms.py](contracts/ai/evidence/transforms.py)

## 09. RapidOCR: first text/box observations

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** Evidence dispatch and source decode → this component → EasyOCR: independent OCR candidates.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00066_RapidOCRProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
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
      "call": "00066_RapidOCRProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_001",
              "raw_text": "A=60°",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 556.0,
                    "y": 187.0
                  },
                  {
                    "x": 683.0,
                    "y": 184.0
                  },
                  {
                    "x": 684.0,
                    "y": 230.0
                  },
                  {
                    "x": 557.0,
                    "y": 233.0
                  }
                ]
              },
              "confidence": 0.98817,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "N1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 272.0,
                    "y": 225.0
                  },
                  {
                    "x": 334.0,
                    "y": 231.0
                  },
                  {
                    "x": 328.0,
                    "y": 286.0
                  },
                  {
                    "x": 267.0,
                    "y": 280.0
                  }
                ]
              },
              "confidence": 0.9941,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 47.0,
                    "y": 342.0
                  },
                  {
                    "x": 262.0,
                    "y": 346.0
                  },
                  {
                    "x": 261.0,
                    "y": 397.0
                  },
                  {
                    "x": 46.0,
                    "y": 393.0
                  }
                ]
              },
              "confidence": 0.99992,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_004",
              "raw_text": "δ",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1086.0,
                "y": 392.0,
                "width": 49.0,
                "height": 64.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1090.0,
                    "y": 392.0
                  },
                  {
                    "x": 1135.0,
                    "y": 395.0
                  },
                  {
                    "x": 1131.0,
                    "y": 456.0
                  },
                  {
                    "x": 1086.0,
                    "y": 453.0
                  }
                ]
              },
              "confidence": 0.99967,
              "script_candidate": "greek",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_004"
            },
            {
              "id": "ocr_tok_005",
              "raw_text": "r1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 500.0,
                "y": 412.0,
                "width": 56.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 500.0,
                    "y": 412.0
                  },
                  {
                    "x": 556.0,
                    "y": 412.0
                  },
                  {
                    "x": 556.0,
                    "y": 465.0
                  },
                  {
                    "x": 500.0,
                    "y": 465.0
                  }
                ]
              },
              "confidence": 0.98446,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_005"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "21",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 738.0,
                    "y": 482.0
                  },
                  {
                    "x": 771.0,
                    "y": 465.0
                  },
                  {
                    "x": 801.0,
                    "y": 524.0
                  },
                  {
                    "x": 768.0,
                    "y": 541.0
                  }
                ]
              },
              "confidence": 0.74629,
              "script_candidate": "numeric",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_007",
              "raw_text": "e",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 909.0,
                "y": 518.0,
                "width": 34.0,
                "height": 36.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 909.0,
                    "y": 518.0
                  },
                  {
                    "x": 943.0,
                    "y": 518.0
                  },
                  {
                    "x": 943.0,
                    "y": 554.0
                  },
                  {
                    "x": 909.0,
                    "y": 554.0
                  }
                ]
              },
              "confidence": 0.99829,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_007"
            },
            {
              "id": "ocr_tok_008",
              "raw_text": "N2",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 739.0,
                    "y": 541.0
                  },
                  {
                    "x": 815.0,
                    "y": 552.0
                  },
                  {
                    "x": 806.0,
                    "y": 614.0
                  },
                  {
                    "x": 730.0,
                    "y": 603.0
                  }
                ]
              },
              "confidence": 0.95735,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "provider": "rapidocr",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx",
        "recognizer_language": "latin_digits_ch",
        "latency_ms": 2518.7927999941166,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Observed strings, confidence, source-space polygons/boxes and recognizer metadata. Text recognition alone does not locate the physical component represented by a label.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Changes, provenance and possible information loss:** Image → text candidates. Inspect exact source boxes; a correct string can still have a box overlapping diagram geometry.

[Complete stage input/output bundle](stage_data/09_rapid.json)

- [RapidOCRProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00066_RapidOCRProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\rapidocr.py](contracts/ai/evidence/ocr/rapidocr.py)

## 10. EasyOCR: independent OCR candidates

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** RapidOCR: first text/box observations → this component → Symbol candidates, deduplication and final OCR.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00139_EasyOCRBanglaProvider.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
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
      "call": "00139_EasyOCRBanglaProvider.extract",
      "return_value": {
        "status": "success",
        "tokens": {
          "count": 9,
          "first_8_records": [
            {
              "id": "bn_tok_001",
              "raw_text": "A = 60",
              "normalized_text": "A = 60",
              "bbox_source_px": {
                "x": 565.0,
                "y": 189.0,
                "width": 104.0,
                "height": 40.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 565.0,
                    "y": 189.0
                  },
                  {
                    "x": 669.0,
                    "y": 189.0
                  },
                  {
                    "x": 669.0,
                    "y": 229.0
                  },
                  {
                    "x": 565.0,
                    "y": 229.0
                  }
                ]
              },
              "confidence": 0.4305139943295405,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_001"
            },
            {
              "id": "bn_tok_002",
              "raw_text": "N",
              "normalized_text": "N",
              "bbox_source_px": {
                "x": 274.0,
                "y": 232.0,
                "width": 54.0,
                "height": 50.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 274.0,
                    "y": 232.0
                  },
                  {
                    "x": 328.0,
                    "y": 232.0
                  },
                  {
                    "x": 328.0,
                    "y": 282.0
                  },
                  {
                    "x": 274.0,
                    "y": 282.0
                  }
                ]
              },
              "confidence": 0.38066897407738054,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_002"
            },
            {
              "id": "bn_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": "Incident ray",
              "bbox_source_px": {
                "x": 48.0,
                "y": 346.0,
                "width": 215.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 48.0,
                    "y": 346.0
                  },
                  {
                    "x": 263.0,
                    "y": 346.0
                  },
                  {
                    "x": 263.0,
                    "y": 399.0
                  },
                  {
                    "x": 48.0,
                    "y": 399.0
                  }
                ]
              },
              "confidence": 0.9437185399289797,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_003"
            },
            {
              "id": "bn_tok_004",
              "raw_text": "12",
              "normalized_text": "12",
              "bbox_source_px": {
                "x": 749.0,
                "y": 477.0,
                "width": 42.0,
                "height": 48.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 749.0,
                    "y": 477.0
                  },
                  {
                    "x": 791.0,
                    "y": 477.0
                  },
                  {
                    "x": 791.0,
                    "y": 525.0
                  },
                  {
                    "x": 749.0,
                    "y": 525.0
                  }
                ]
              },
              "confidence": 0.637097448320458,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_004"
            },
            {
              "id": "bn_tok_005",
              "raw_text": "N2",
              "normalized_text": "N2",
              "bbox_source_px": {
                "x": 750.0,
                "y": 554.0,
                "width": 54.0,
                "height": 52.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 750.0,
                    "y": 554.0
                  },
                  {
                    "x": 804.0,
                    "y": 554.0
                  },
                  {
                    "x": 804.0,
                    "y": 606.0
                  },
                  {
                    "x": 750.0,
                    "y": 606.0
                  }
                ]
              },
              "confidence": 0.8088539617403547,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_005"
            },
            {
              "id": "bn_tok_006",
              "raw_text": "Glass Prism",
              "normalized_text": "Glass Prism",
              "bbox_source_px": {
                "x": 506.0,
                "y": 614.0,
                "width": 243.0,
                "height": 54.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 506.0,
                    "y": 614.0
                  },
                  {
                    "x": 749.0,
                    "y": 614.0
                  },
                  {
                    "x": 749.0,
                    "y": 668.0
                  },
                  {
                    "x": 506.0,
                    "y": 668.0
                  }
                ]
              },
              "confidence": 0.987817609320542,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_006"
            },
            {
              "id": "bn_tok_007",
              "raw_text": "Emergent ray",
              "normalized_text": "Emergent ray",
              "bbox_source_px": {
                "x": 1019.0,
                "y": 607.0,
                "width": 241.0,
                "height": 56.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1019.0,
                    "y": 607.0
                  },
                  {
                    "x": 1260.0,
                    "y": 607.0
                  },
                  {
                    "x": 1260.0,
                    "y": 663.0
                  },
                  {
                    "x": 1019.0,
                    "y": 663.0
                  }
                ]
              },
              "confidence": 0.6244371543696388,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_007"
            },
            {
              "id": "bn_tok_008",
              "raw_text": "৪ Refraction through a Prism",
              "normalized_text": "৪ Refraction through a Prism",
              "bbox_source_px": {
                "x": 392.0,
                "y": 842.0,
                "width": 564.0,
                "height": 54.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 392.0,
                    "y": 842.0
                  },
                  {
                    "x": 956.0,
                    "y": 842.0
                  },
                  {
                    "x": 956.0,
                    "y": 896.0
                  },
                  {
                    "x": 392.0,
                    "y": 896.0
                  }
                ]
              },
              "confidence": 0.4997823913889772,
              "script_candidate": "bengali",
              "language_candidate": "bn",
              "provider": "easyocr_bangla",
              "recognizer_model": "bengali.pth",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_bn_tok_008"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "provider": "easyocr_bangla",
        "model": "bengali.pth",
        "package": "easyocr",
        "package_version": "1.7.2",
        "detector_model": "craft_mlt_25k.pth",
        "recognizer_model": "bengali.pth",
        "recognizer_language": "bn+en",
        "latency_ms": 15897.389899997506,
        "error": null,
        "metadata": {}
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Independent text alternatives with confidence and source positions; uncertain alternatives should not silently overwrite stronger evidence.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Changes, provenance and possible information loss:** Alternative OCR supplies competing evidence. Its errors are distinct from whichever result the router actually selects.

[Complete stage input/output bundle](stage_data/10_easy.json)

- [EasyOCRBanglaProvider.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00139_EasyOCRBanglaProvider.extract/STAGE.html)

- [Code: ai\evidence\ocr\bangla.py](contracts/ai/evidence/ocr/bangla.py)

## 11. Symbol candidates, deduplication and final OCR

**Execution:** EXECUTED. **Verdict:** OBSERVED / REVIEW ALTERNATIVES.

**Upstream → downstream:** EasyOCR: independent OCR candidates → this component → Grayscale, blur and edge extraction.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 14,
  "first_8_records": [
    {
      "call": "00065_MultiOCRRouter.extract",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
          "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
        },
        "source_width": 1280,
        "source_height": 960,
        "region": null
      }
    },
    {
      "call": "00215_deduplicate_spatial_tokens",
      "value": {
        "tokens": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_001",
              "raw_text": "A=60°",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 556.0,
                    "y": 187.0
                  },
                  {
                    "x": 683.0,
                    "y": 184.0
                  },
                  {
                    "x": 684.0,
                    "y": 230.0
                  },
                  {
                    "x": 557.0,
                    "y": 233.0
                  }
                ]
              },
              "confidence": 0.98817,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "A = 60",
                  "script": "latin",
                  "confidence": 0.4305139943295405,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "N1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 272.0,
                    "y": 225.0
                  },
                  {
                    "x": 334.0,
                    "y": 231.0
                  },
                  {
                    "x": 328.0,
                    "y": 286.0
                  },
                  {
                    "x": 267.0,
                    "y": 280.0
                  }
                ]
              },
              "confidence": 0.9941,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N",
                  "script": "latin",
                  "confidence": 0.38066897407738054,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 47.0,
                    "y": 342.0
                  },
                  {
                    "x": 262.0,
                    "y": 346.0
                  },
                  {
                    "x": 261.0,
                    "y": 397.0
                  },
                  {
                    "x": 46.0,
                    "y": 393.0
                  }
                ]
              },
              "confidence": 0.99992,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Incident ray",
                  "script": "latin",
                  "confidence": 0.9437185399289797,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_004",
              "raw_text": "δ",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1086.0,
                "y": 392.0,
                "width": 49.0,
                "height": 64.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1090.0,
                    "y": 392.0
                  },
                  {
                    "x": 1135.0,
                    "y": 395.0
                  },
                  {
                    "x": 1131.0,
                    "y": 456.0
                  },
                  {
                    "x": 1086.0,
                    "y": 453.0
                  }
                ]
              },
              "confidence": 0.99967,
              "script_candidate": "greek",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_004"
            },
            {
              "id": "ocr_tok_005",
              "raw_text": "r1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 500.0,
                "y": 412.0,
                "width": 56.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 500.0,
                    "y": 412.0
                  },
                  {
                    "x": 556.0,
                    "y": 412.0
                  },
                  {
                    "x": 556.0,
                    "y": 465.0
                  },
                  {
                    "x": 500.0,
                    "y": 465.0
                  }
                ]
              },
              "confidence": 0.98446,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_005"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "21",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 738.0,
                    "y": 482.0
                  },
                  {
                    "x": 771.0,
                    "y": 465.0
                  },
                  {
                    "x": 801.0,
                    "y": 524.0
                  },
                  {
                    "x": 768.0,
                    "y": 541.0
                  }
                ]
              },
              "confidence": 0.74629,
              "script_candidate": "numeric",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "12",
                  "script": "latin",
                  "confidence": 0.637097448320458,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_007",
              "raw_text": "e",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 909.0,
                "y": 518.0,
                "width": 34.0,
                "height": 36.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 909.0,
                    "y": 518.0
                  },
                  {
                    "x": 943.0,
                    "y": 518.0
                  },
                  {
                    "x": 943.0,
                    "y": 554.0
                  },
                  {
                    "x": 909.0,
                    "y": 554.0
                  }
                ]
              },
              "confidence": 0.99829,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [],
              "evidence_ref": "evidence_ocr_ocr_tok_007"
            },
            {
              "id": "ocr_tok_008",
              "raw_text": "N2",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 739.0,
                    "y": 541.0
                  },
                  {
                    "x": 815.0,
                    "y": 552.0
                  },
                  {
                    "x": 806.0,
                    "y": 614.0
                  },
                  {
                    "x": 730.0,
                    "y": 603.0
                  }
                ]
              },
              "confidence": 0.95735,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N2",
                  "script": "latin",
                  "confidence": 0.8088539617403547,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        }
      }
    },
    {
      "call": "00227_GreekSymbolVisualOCR.extract_symbols",
      "value": {
        "image_bgr": {
          "shape": [
            960,
            1280,
            3
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
          "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
        },
        "existing_tokens": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_011",
              "raw_text": "Fig. 8 Refraction through a Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 290.0,
                "y": 837.0,
                "width": 669.0,
                "height": 62.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 290.0,
                    "y": 837.0
                  },
                  {
                    "x": 959.0,
                    "y": 840.0
                  },
                  {
                    "x": 959.0,
                    "y": 899.0
                  },
                  {
                    "x": 290.0,
                    "y": 896.0
                  }
                ]
              },
              "confidence": 0.98457,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Fig",
                  "script": "latin",
                  "confidence": 0.9989254357832382,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_011"
            },
            {
              "id": "ocr_tok_009",
              "raw_text": "Glass Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 506.0,
                "y": 613.0,
                "width": 245.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 506.0,
                    "y": 613.0
                  },
                  {
                    "x": 751.0,
                    "y": 615.0
                  },
                  {
                    "x": 751.0,
                    "y": 666.0
                  },
                  {
                    "x": 506.0,
                    "y": 664.0
                  }
                ]
              },
              "confidence": 0.99989,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Glass Prism",
                  "script": "latin",
                  "confidence": 0.987817609320542,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_009"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 47.0,
                    "y": 342.0
                  },
                  {
                    "x": 262.0,
                    "y": 346.0
                  },
                  {
                    "x": 261.0,
                    "y": 397.0
                  },
                  {
                    "x": 46.0,
                    "y": 393.0
                  }
                ]
              },
              "confidence": 0.99992,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Incident ray",
                  "script": "latin",
                  "confidence": 0.9437185399289797,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_010",
              "raw_text": "Emergent ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1022.0,
                "y": 610.0,
                "width": 238.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1023.0,
                    "y": 610.0
                  },
                  {
                    "x": 1260.0,
                    "y": 615.0
                  },
                  {
                    "x": 1259.0,
                    "y": 659.0
                  },
                  {
                    "x": 1022.0,
                    "y": 654.0
                  }
                ]
              },
              "confidence": 0.99521,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Emergent ray",
                  "script": "latin",
                  "confidence": 0.6244371543696388,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_010"
            },
            {
              "id": "ocr_tok_001",
              "raw_text": "A=60°",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 556.0,
                    "y": 187.0
                  },
                  {
                    "x": 683.0,
                    "y": 184.0
                  },
                  {
                    "x": 684.0,
                    "y": 230.0
                  },
                  {
                    "x": 557.0,
                    "y": 233.0
                  }
                ]
              },
              "confidence": 0.98817,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "A = 60",
                  "script": "latin",
                  "confidence": 0.4305139943295405,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_008",
              "raw_text": "N2",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 739.0,
                    "y": 541.0
                  },
                  {
                    "x": 815.0,
                    "y": 552.0
                  },
                  {
                    "x": 806.0,
                    "y": 614.0
                  },
                  {
                    "x": 730.0,
                    "y": 603.0
                  }
                ]
              },
              "confidence": 0.95735,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N2",
                  "script": "latin",
                  "confidence": 0.8088539617403547,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "21",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 738.0,
                    "y": 482.0
                  },
                  {
                    "x": 771.0,
                    "y": 465.0
                  },
                  {
                    "x": 801.0,
                    "y": 524.0
                  },
                  {
                    "x": 768.0,
                    "y": 541.0
                  }
                ]
              },
              "confidence": 0.74629,
              "script_candidate": "numeric",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "12",
                  "script": "latin",
                  "confidence": 0.637097448320458,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "N1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 272.0,
                    "y": 225.0
                  },
                  {
                    "x": 334.0,
                    "y": 231.0
                  },
                  {
                    "x": 328.0,
                    "y": 286.0
                  },
                  {
                    "x": 267.0,
                    "y": 280.0
                  }
                ]
              },
              "confidence": 0.9941,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N",
                  "script": "latin",
                  "confidence": 0.38066897407738054,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "source_width": 1280,
        "source_height": 960
      }
    },
    {
      "call": "00228_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_011",
          "raw_text": "Fig. 8 Refraction through a Prism",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 290.0,
            "y": 837.0,
            "width": 669.0,
            "height": 62.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 290.0,
                "y": 837.0
              },
              {
                "x": 959.0,
                "y": 840.0
              },
              {
                "x": 959.0,
                "y": 899.0
              },
              {
                "x": 290.0,
                "y": 896.0
              }
            ]
          },
          "confidence": 0.98457,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9989254357832382,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_011"
        }
      }
    },
    {
      "call": "00230_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_009",
          "raw_text": "Glass Prism",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 506.0,
            "y": 613.0,
            "width": 245.0,
            "height": 53.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 506.0,
                "y": 613.0
              },
              {
                "x": 751.0,
                "y": 615.0
              },
              {
                "x": 751.0,
                "y": 666.0
              },
              {
                "x": 506.0,
                "y": 664.0
              }
            ]
          },
          "confidence": 0.99989,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Glass Prism",
              "script": "latin",
              "confidence": 0.987817609320542,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_009"
        }
      }
    },
    {
      "call": "00232_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_003",
          "raw_text": "Incident ray",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 46.0,
            "y": 342.0,
            "width": 216.0,
            "height": 55.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 47.0,
                "y": 342.0
              },
              {
                "x": 262.0,
                "y": 346.0
              },
              {
                "x": 261.0,
                "y": 397.0
              },
              {
                "x": 46.0,
                "y": 393.0
              }
            ]
          },
          "confidence": 0.99992,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Incident ray",
              "script": "latin",
              "confidence": 0.9437185399289797,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        }
      }
    },
    {
      "call": "00234_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_010",
          "raw_text": "Emergent ray",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1022.0,
            "y": 610.0,
            "width": 238.0,
            "height": 49.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1023.0,
                "y": 610.0
              },
              {
                "x": 1260.0,
                "y": 615.0
              },
              {
                "x": 1259.0,
                "y": 659.0
              },
              {
                "x": 1022.0,
                "y": 654.0
              }
            ]
          },
          "confidence": 0.99521,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Emergent ray",
              "script": "latin",
              "confidence": 0.6244371543696388,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_010"
        }
      }
    },
    {
      "call": "00236_PhysicsSymbolCandidateResolver.enrich_token",
      "value": {
        "token": {
          "id": "ocr_tok_001",
          "raw_text": "A=60°",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 556.0,
            "y": 184.0,
            "width": 128.0,
            "height": 49.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 556.0,
                "y": 187.0
              },
              {
                "x": 683.0,
                "y": 184.0
              },
              {
                "x": 684.0,
                "y": 230.0
              },
              {
                "x": 557.0,
                "y": 233.0
              }
            ]
          },
          "confidence": 0.98817,
          "script_candidate": "mixed",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "A = 60",
              "script": "latin",
              "confidence": 0.4305139943295405,
              "provider": "easyocr_bangla"
            }
          ],
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
    "count": 14,
    "first_8_records": [
      {
        "call": "00065_MultiOCRRouter.extract",
        "return_value": {
          "status": "success",
          "tokens": {
            "count": 11,
            "first_8_records": [
              {
                "id": "ocr_tok_011",
                "raw_text": "Fig. 8 Refraction through a Prism",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 290.0,
                  "y": 837.0,
                  "width": 669.0,
                  "height": 62.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 290.0,
                      "y": 837.0
                    },
                    {
                      "x": 959.0,
                      "y": 840.0
                    },
                    {
                      "x": 959.0,
                      "y": 899.0
                    },
                    {
                      "x": 290.0,
                      "y": 896.0
                    }
                  ]
                },
                "confidence": 0.98457,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "Fig",
                    "script": "latin",
                    "confidence": 0.9989254357832382,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_011"
              },
              {
                "id": "ocr_tok_009",
                "raw_text": "Glass Prism",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 506.0,
                  "y": 613.0,
                  "width": 245.0,
                  "height": 53.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 506.0,
                      "y": 613.0
                    },
                    {
                      "x": 751.0,
                      "y": 615.0
                    },
                    {
                      "x": 751.0,
                      "y": 666.0
                    },
                    {
                      "x": 506.0,
                      "y": 664.0
                    }
                  ]
                },
                "confidence": 0.99989,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "Glass Prism",
                    "script": "latin",
                    "confidence": 0.987817609320542,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_009"
              },
              {
                "id": "ocr_tok_003",
                "raw_text": "Incident ray",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 46.0,
                  "y": 342.0,
                  "width": 216.0,
                  "height": 55.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 47.0,
                      "y": 342.0
                    },
                    {
                      "x": 262.0,
                      "y": 346.0
                    },
                    {
                      "x": 261.0,
                      "y": 397.0
                    },
                    {
                      "x": 46.0,
                      "y": 393.0
                    }
                  ]
                },
                "confidence": 0.99992,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "Incident ray",
                    "script": "latin",
                    "confidence": 0.9437185399289797,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_003"
              },
              {
                "id": "ocr_tok_010",
                "raw_text": "Emergent ray",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 1022.0,
                  "y": 610.0,
                  "width": 238.0,
                  "height": 49.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 1023.0,
                      "y": 610.0
                    },
                    {
                      "x": 1260.0,
                      "y": 615.0
                    },
                    {
                      "x": 1259.0,
                      "y": 659.0
                    },
                    {
                      "x": 1022.0,
                      "y": 654.0
                    }
                  ]
                },
                "confidence": 0.99521,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "Emergent ray",
                    "script": "latin",
                    "confidence": 0.6244371543696388,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_010"
              },
              {
                "id": "ocr_tok_001",
                "raw_text": "A=60°",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 556.0,
                  "y": 184.0,
                  "width": 128.0,
                  "height": 49.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 556.0,
                      "y": 187.0
                    },
                    {
                      "x": 683.0,
                      "y": 184.0
                    },
                    {
                      "x": 684.0,
                      "y": 230.0
                    },
                    {
                      "x": 557.0,
                      "y": 233.0
                    }
                  ]
                },
                "confidence": 0.98817,
                "script_candidate": "mixed",
                "language_candidate": "und",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "A = 60",
                    "script": "latin",
                    "confidence": 0.4305139943295405,
                    "provider": "easyocr_bangla"
                  },
                  {
                    "text": "Δ = 60°",
                    "script": "greek",
                    "name": "confusable_var_delta",
                    "confidence": 0.791,
                    "provider": "equation_symbol_resolver"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_001"
              },
              {
                "id": "ocr_tok_008",
                "raw_text": "N2",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 730.0,
                  "y": 541.0,
                  "width": 85.0,
                  "height": 73.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 739.0,
                      "y": 541.0
                    },
                    {
                      "x": 815.0,
                      "y": 552.0
                    },
                    {
                      "x": 806.0,
                      "y": 614.0
                    },
                    {
                      "x": 730.0,
                      "y": 603.0
                    }
                  ]
                },
                "confidence": 0.95735,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "N2",
                    "script": "latin",
                    "confidence": 0.8088539617403547,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_008"
              },
              {
                "id": "ocr_tok_006",
                "raw_text": "21",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 738.0,
                  "y": 465.0,
                  "width": 63.0,
                  "height": 76.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 738.0,
                      "y": 482.0
                    },
                    {
                      "x": 771.0,
                      "y": 465.0
                    },
                    {
                      "x": 801.0,
                      "y": 524.0
                    },
                    {
                      "x": 768.0,
                      "y": 541.0
                    }
                  ]
                },
                "confidence": 0.74629,
                "script_candidate": "numeric",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "12",
                    "script": "latin",
                    "confidence": 0.637097448320458,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_006"
              },
              {
                "id": "ocr_tok_002",
                "raw_text": "N1",
                "normalized_text": null,
                "bbox_source_px": {
                  "x": 267.0,
                  "y": 225.0,
                  "width": 67.0,
                  "height": 61.0
                },
                "polygon_source_px": {
                  "points": [
                    {
                      "x": 272.0,
                      "y": 225.0
                    },
                    {
                      "x": 334.0,
                      "y": 231.0
                    },
                    {
                      "x": 328.0,
                      "y": 286.0
                    },
                    {
                      "x": 267.0,
                      "y": 280.0
                    }
                  ]
                },
                "confidence": 0.9941,
                "script_candidate": "latin",
                "language_candidate": "en",
                "provider": "rapidocr",
                "recognizer_model": "PP-OCRv6_rec_small.onnx",
                "candidate_alternatives": [
                  {
                    "text": "N",
                    "script": "latin",
                    "confidence": 0.38066897407738054,
                    "provider": "easyocr_bangla"
                  }
                ],
                "evidence_ref": "evidence_ocr_ocr_tok_002"
              }
            ],
            "complete_list": "See complete stage bundle / original artifact"
          },
          "provider": "multi_ocr_router",
          "model": "PP-OCRv6-onnx",
          "package": "rapidocr+easyocr+greek_ocr",
          "package_version": "3.9.2",
          "detector_model": "PP-OCRv6_det_small.onnx",
          "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
          "recognizer_language": "en+bn+el",
          "latency_ms": 19624.66850000783,
          "error": null,
          "metadata": {
            "bangla_available": true,
            "greek_available": true,
            "formula_available": false,
            "regions_count": 11,
            "token_count": 11
          }
        }
      },
      {
        "call": "00215_deduplicate_spatial_tokens",
        "return_value": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_011",
              "raw_text": "Fig. 8 Refraction through a Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 290.0,
                "y": 837.0,
                "width": 669.0,
                "height": 62.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 290.0,
                    "y": 837.0
                  },
                  {
                    "x": 959.0,
                    "y": 840.0
                  },
                  {
                    "x": 959.0,
                    "y": 899.0
                  },
                  {
                    "x": 290.0,
                    "y": 896.0
                  }
                ]
              },
              "confidence": 0.98457,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Fig",
                  "script": "latin",
                  "confidence": 0.9989254357832382,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_011"
            },
            {
              "id": "ocr_tok_009",
              "raw_text": "Glass Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 506.0,
                "y": 613.0,
                "width": 245.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 506.0,
                    "y": 613.0
                  },
                  {
                    "x": 751.0,
                    "y": 615.0
                  },
                  {
                    "x": 751.0,
                    "y": 666.0
                  },
                  {
                    "x": 506.0,
                    "y": 664.0
                  }
                ]
              },
              "confidence": 0.99989,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Glass Prism",
                  "script": "latin",
                  "confidence": 0.987817609320542,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_009"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 47.0,
                    "y": 342.0
                  },
                  {
                    "x": 262.0,
                    "y": 346.0
                  },
                  {
                    "x": 261.0,
                    "y": 397.0
                  },
                  {
                    "x": 46.0,
                    "y": 393.0
                  }
                ]
              },
              "confidence": 0.99992,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Incident ray",
                  "script": "latin",
                  "confidence": 0.9437185399289797,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_010",
              "raw_text": "Emergent ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1022.0,
                "y": 610.0,
                "width": 238.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 1023.0,
                    "y": 610.0
                  },
                  {
                    "x": 1260.0,
                    "y": 615.0
                  },
                  {
                    "x": 1259.0,
                    "y": 659.0
                  },
                  {
                    "x": 1022.0,
                    "y": 654.0
                  }
                ]
              },
              "confidence": 0.99521,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Emergent ray",
                  "script": "latin",
                  "confidence": 0.6244371543696388,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_010"
            },
            {
              "id": "ocr_tok_001",
              "raw_text": "A=60°",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 556.0,
                    "y": 187.0
                  },
                  {
                    "x": 683.0,
                    "y": 184.0
                  },
                  {
                    "x": 684.0,
                    "y": 230.0
                  },
                  {
                    "x": 557.0,
                    "y": 233.0
                  }
                ]
              },
              "confidence": 0.98817,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "A = 60",
                  "script": "latin",
                  "confidence": 0.4305139943295405,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_008",
              "raw_text": "N2",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 739.0,
                    "y": 541.0
                  },
                  {
                    "x": 815.0,
                    "y": 552.0
                  },
                  {
                    "x": 806.0,
                    "y": 614.0
                  },
                  {
                    "x": 730.0,
                    "y": 603.0
                  }
                ]
              },
              "confidence": 0.95735,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N2",
                  "script": "latin",
                  "confidence": 0.8088539617403547,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "21",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 738.0,
                    "y": 482.0
                  },
                  {
                    "x": 771.0,
                    "y": 465.0
                  },
                  {
                    "x": 801.0,
                    "y": 524.0
                  },
                  {
                    "x": 768.0,
                    "y": 541.0
                  }
                ]
              },
              "confidence": 0.74629,
              "script_candidate": "numeric",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "12",
                  "script": "latin",
                  "confidence": 0.637097448320458,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "N1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              },
              "polygon_source_px": {
                "points": [
                  {
                    "x": 272.0,
                    "y": 225.0
                  },
                  {
                    "x": 334.0,
                    "y": 231.0
                  },
                  {
                    "x": 328.0,
                    "y": 286.0
                  },
                  {
                    "x": 267.0,
                    "y": 280.0
                  }
                ]
              },
              "confidence": 0.9941,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N",
                  "script": "latin",
                  "confidence": 0.38066897407738054,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        }
      },
      {
        "call": "00227_GreekSymbolVisualOCR.extract_symbols",
        "return_value": []
      },
      {
        "call": "00228_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_011",
          "raw_text": "Fig. 8 Refraction through a Prism",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 290.0,
            "y": 837.0,
            "width": 669.0,
            "height": 62.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 290.0,
                "y": 837.0
              },
              {
                "x": 959.0,
                "y": 840.0
              },
              {
                "x": 959.0,
                "y": 899.0
              },
              {
                "x": 290.0,
                "y": 896.0
              }
            ]
          },
          "confidence": 0.98457,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Fig",
              "script": "latin",
              "confidence": 0.9989254357832382,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_011"
        }
      },
      {
        "call": "00230_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_009",
          "raw_text": "Glass Prism",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 506.0,
            "y": 613.0,
            "width": 245.0,
            "height": 53.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 506.0,
                "y": 613.0
              },
              {
                "x": 751.0,
                "y": 615.0
              },
              {
                "x": 751.0,
                "y": 666.0
              },
              {
                "x": 506.0,
                "y": 664.0
              }
            ]
          },
          "confidence": 0.99989,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Glass Prism",
              "script": "latin",
              "confidence": 0.987817609320542,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_009"
        }
      },
      {
        "call": "00232_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_003",
          "raw_text": "Incident ray",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 46.0,
            "y": 342.0,
            "width": 216.0,
            "height": 55.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 47.0,
                "y": 342.0
              },
              {
                "x": 262.0,
                "y": 346.0
              },
              {
                "x": 261.0,
                "y": 397.0
              },
              {
                "x": 46.0,
                "y": 393.0
              }
            ]
          },
          "confidence": 0.99992,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Incident ray",
              "script": "latin",
              "confidence": 0.9437185399289797,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_003"
        }
      },
      {
        "call": "00234_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_010",
          "raw_text": "Emergent ray",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 1022.0,
            "y": 610.0,
            "width": 238.0,
            "height": 49.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 1023.0,
                "y": 610.0
              },
              {
                "x": 1260.0,
                "y": 615.0
              },
              {
                "x": 1259.0,
                "y": 659.0
              },
              {
                "x": 1022.0,
                "y": 654.0
              }
            ]
          },
          "confidence": 0.99521,
          "script_candidate": "latin",
          "language_candidate": "en",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "Emergent ray",
              "script": "latin",
              "confidence": 0.6244371543696388,
              "provider": "easyocr_bangla"
            }
          ],
          "evidence_ref": "evidence_ocr_ocr_tok_010"
        }
      },
      {
        "call": "00236_PhysicsSymbolCandidateResolver.enrich_token",
        "return_value": {
          "id": "ocr_tok_001",
          "raw_text": "A=60°",
          "normalized_text": null,
          "bbox_source_px": {
            "x": 556.0,
            "y": 184.0,
            "width": 128.0,
            "height": 49.0
          },
          "polygon_source_px": {
            "points": [
              {
                "x": 556.0,
                "y": 187.0
              },
              {
                "x": 683.0,
                "y": 184.0
              },
              {
                "x": 684.0,
                "y": 230.0
              },
              {
                "x": 557.0,
                "y": 233.0
              }
            ]
          },
          "confidence": 0.98817,
          "script_candidate": "mixed",
          "language_candidate": "und",
          "provider": "rapidocr",
          "recognizer_model": "PP-OCRv6_rec_small.onnx",
          "candidate_alternatives": [
            {
              "text": "A = 60",
              "script": "latin",
              "confidence": 0.4305139943295405,
              "provider": "easyocr_bangla"
            },
            {
              "text": "Δ = 60°",
              "script": "greek",
              "name": "confusable_var_delta",
              "confidence": 0.791,
              "provider": "equation_symbol_resolver"
            }
          ],
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compare the literal source labels with the retained tokens below. A wrong alternative is not necessarily the selected output. 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Changes, provenance and possible information loss:** OCR alternatives → selected token set. PageIR text blocks are filled from these tokens inside the evidence pipeline.

[Complete stage input/output bundle](stage_data/11_ocr.json)

- [MultiOCRRouter.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00065_MultiOCRRouter.extract/STAGE.html)

- [deduplicate_spatial_tokens — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00215_deduplicate_spatial_tokens/STAGE.html)

- [GreekSymbolVisualOCR.extract_symbols — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00227_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00228_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00230_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00232_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00234_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00236_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00238_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00240_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00242_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00244_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00246_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [PhysicsSymbolCandidateResolver.enrich_token — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00248_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- [Code: ai\evidence\ocr\router.py](contracts/ai/evidence/ocr/router.py)

- [Code: ai\evidence\ocr\greek_symbols.py](contracts/ai/evidence/ocr/greek_symbols.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00065_MultiOCRRouter.extract/actual_overlay_on_source.png)

## 12. Grayscale, blur and edge extraction

**Execution:** EXECUTED. **Verdict:** FRAME PASS / LOSSY PROCESSING.

**Upstream → downstream:** Symbol candidates, deduplication and final OCR → this component → OCR-region suppression before geometry detection.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00257_preprocess_diagram",
    "value": {
      "img_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
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
      "call": "00257_preprocess_diagram",
      "return_value": [
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\5fdd5c9c8b422b328e3ac3d76d5a8358750ec14459bdb5d8875203d2a0e31b8f.npy",
          "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\5fdd5c9c8b422b328e3ac3d76d5a8358750ec14459bdb5d8875203d2a0e31b8f.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\382429cea8660cf69538cc31b70fb042454fd787cfac57c755b30c3bf7c4f05b.npy",
          "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\382429cea8660cf69538cc31b70fb042454fd787cfac57c755b30c3bf7c4f05b.png"
        },
        {
          "shape": [
            960,
            1280
          ],
          "dtype": "uint8",
          "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.npy",
          "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png"
        }
      ]
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Grayscale/blur/edge arrays in the same 1280×960 source frame. Image processing may change intensities, but must not imply a spatial crop/scale that was not performed.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Arrays preserve the source frame. Blur and Canny change image information; no detector correctness is inferred from shape alone.

**Changes, provenance and possible information loss:** Color/intensity information becomes an edge representation. Exact arrays are retained. OpenCV internal per-operation frames were not separately profiled.

[Complete stage input/output bundle](stage_data/12_pre.json)

- [preprocess_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00257_preprocess_diagram/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png)

![5fdd5c9c8b422b328e3ac3d76d5a8358750ec14459bdb5d8875203d2a0e31b8f.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/5fdd5c9c8b422b328e3ac3d76d5a8358750ec14459bdb5d8875203d2a0e31b8f.png)

![382429cea8660cf69538cc31b70fb042454fd787cfac57c755b30c3bf7c4f05b.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/382429cea8660cf69538cc31b70fb042454fd787cfac57c755b30c3bf7c4f05b.png)

![0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png)

## 13. OCR-region suppression before geometry detection

**Execution:** EXECUTED. **Verdict:** FAIL — FIRST PROVEN GEOMETRY LOSS.

**Upstream → downstream:** Grayscale, blur and edge extraction → this component → Domain CV: raw candidates → selected geometry.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00258_mask_out_text_regions",
    "value": {
      "edge_map": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png"
      },
      "ocr_boxes": {
        "count": 11,
        "first_8_records": [
          {
            "x": 290.0,
            "y": 837.0,
            "width": 669.0,
            "height": 62.0
          },
          {
            "x": 506.0,
            "y": 613.0,
            "width": 245.0,
            "height": 53.0
          },
          {
            "x": 46.0,
            "y": 342.0,
            "width": 216.0,
            "height": 55.0
          },
          {
            "x": 1022.0,
            "y": 610.0,
            "width": 238.0,
            "height": 49.0
          },
          {
            "x": 556.0,
            "y": 184.0,
            "width": 128.0,
            "height": 49.0
          },
          {
            "x": 730.0,
            "y": 541.0,
            "width": 85.0,
            "height": 73.0
          },
          {
            "x": 738.0,
            "y": 465.0,
            "width": 63.0,
            "height": 76.0
          },
          {
            "x": 267.0,
            "y": 225.0,
            "width": 67.0,
            "height": 61.0
          }
        ],
        "complete_list": "See complete stage bundle / original artifact"
      },
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
      "call": "00258_mask_out_text_regions",
      "return_value": {
        "shape": [
          960,
          1280
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\9c95b9ebf40ef7bb1629c3e99f0ea0e4b4f82a63ab990a53e73247918f0303bf.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\9c95b9ebf40ef7bb1629c3e99f0ea0e4b4f82a63ab990a53e73247918f0303bf.png"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** An edge map suppressing text while preserving relevant diagram boundaries/rays. This is the registration requirement; the implementation zeros the entire expanded rectangle without distinguishing text from geometry.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** A=60° bbox=(556,184,128,49); margin=4 removes prism-side pixels. Other masks remove angle/normal strokes. This is an earlier loss than the wrong base inference; it is not proven to be the sole cause of contour failure.

**Changes, provenance and possible information loss:** Every pixel removed by the actual mask is shown in red on the original. A valid OCR box does not guarantee safe geometry suppression.

[Complete stage input/output bundle](stage_data/13_mask.json)

- [mask_out_text_regions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00258_mask_out_text_regions/STAGE.html)

- [Code: ai\evidence\cv\preprocessing.py](contracts/ai/evidence/cv/preprocessing.py)

![removed_edges_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00258_mask_out_text_regions/removed_edges_on_source.png)

![0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/0e417d279fcb2057428cdfca04c1ed2851801fa2eca349581f032b71ee467b60.png)

![9c95b9ebf40ef7bb1629c3e99f0ea0e4b4f82a63ab990a53e73247918f0303bf.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/arrays/9c95b9ebf40ef7bb1629c3e99f0ea0e4b4f82a63ab990a53e73247918f0303bf.png)

## 14. Domain CV: raw candidates → selected geometry

**Execution:** EXECUTED. **Verdict:** FAIL — PERCEPTION / SELECTION.

**Upstream → downstream:** OCR-region suppression before geometry detection → this component → SAM2 segmentation prompted by CV.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00255_PrismCVCandidateExtractor.extract",
    "value": {
      "image_bgr": {
        "shape": [
          960,
          1280,
          3
        ],
        "dtype": "uint8",
        "artifact": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.npy",
        "image": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017\\arrays\\dfdfab3de47c738590a8f6dce298a93d8d7ffd9c30ad72aa75d561565c537eeb.png"
      },
      "source_width": 1280,
      "source_height": 960,
      "ocr_boxes": {
        "count": 11,
        "first_8_records": [
          {
            "x": 290.0,
            "y": 837.0,
            "width": 669.0,
            "height": 62.0
          },
          {
            "x": 506.0,
            "y": 613.0,
            "width": 245.0,
            "height": 53.0
          },
          {
            "x": 46.0,
            "y": 342.0,
            "width": 216.0,
            "height": 55.0
          },
          {
            "x": 1022.0,
            "y": 610.0,
            "width": 238.0,
            "height": 49.0
          },
          {
            "x": 556.0,
            "y": 184.0,
            "width": 128.0,
            "height": 49.0
          },
          {
            "x": 730.0,
            "y": 541.0,
            "width": 85.0,
            "height": 73.0
          },
          {
            "x": 738.0,
            "y": 465.0,
            "width": 63.0,
            "height": 76.0
          },
          {
            "x": 267.0,
            "y": 225.0,
            "width": 67.0,
            "height": 61.0
          }
        ],
        "complete_list": "See complete stage bundle / original artifact"
      }
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
      "call": "00255_PrismCVCandidateExtractor.extract",
      "return_value": {
        "prism_polygon": {
          "points": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ]
        },
        "apex": {
          "x": 621.3,
          "y": 80.9
        },
        "base_line": {
          "start": {
            "x": 229.2,
            "y": 757.0
          },
          "end": {
            "x": 1003.9,
            "y": 757.0
          }
        },
        "rays": {
          "count": 47,
          "first_8_records": [
            {
              "start": {
                "x": 226.0,
                "y": 771.0
              },
              "end": {
                "x": 450.0,
                "y": 383.0
              }
            },
            {
              "start": {
                "x": 220.0,
                "y": 771.0
              },
              "end": {
                "x": 439.0,
                "y": 391.0
              }
            },
            {
              "start": {
                "x": 221.0,
                "y": 766.0
              },
              "end": {
                "x": 529.0,
                "y": 766.0
              }
            },
            {
              "start": {
                "x": 139.0,
                "y": 434.0
              },
              "end": {
                "x": 267.0,
                "y": 411.0
              }
            },
            {
              "start": {
                "x": 489.0,
                "y": 772.0
              },
              "end": {
                "x": 784.0,
                "y": 772.0
              }
            },
            {
              "start": {
                "x": 688.0,
                "y": 206.0
              },
              "end": {
                "x": 821.0,
                "y": 437.0
              }
            },
            {
              "start": {
                "x": 785.0,
                "y": 773.0
              },
              "end": {
                "x": 1015.0,
                "y": 773.0
              }
            },
            {
              "start": {
                "x": 524.0,
                "y": 767.0
              },
              "end": {
                "x": 812.0,
                "y": 767.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "incident_ray": {
          "start": {
            "x": 47.0,
            "y": 456.0
          },
          "end": {
            "x": 237.0,
            "y": 420.0
          }
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Source-supported candidate lines/circles/polygons and selected geometry, with scores, rejection/selection diagnostics and unresolved ambiguity where evidence is insufficient.

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

**Comparison / debugging conclusion:** Fallback left_max_y=771 and right_max_y=743 yield base_y=(771+743)/2=757. Actual horizontal base candidates remain around y=766–773 in the same output. Returned vertices are (621.3,80.9),(229.2,757),(1003.9,757). The selected polygon visibly lies above the printed base. Incident segment (47,456)→(237,420) is retained correctly.

**Changes, provenance and possible information loss:** Candidate generation and selection are distinct. Compare all_candidates_overlay with selected output; inspect locals for fitted lines, rejected candidates and thresholds.

[Complete stage input/output bundle](stage_data/14_cv.json)

- [PrismCVCandidateExtractor.extract — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00255_PrismCVCandidateExtractor.extract/STAGE.html)

- [Code: ai\evidence\cv\prism_cv.py](contracts/ai/evidence/cv/prism_cv.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00255_PrismCVCandidateExtractor.extract/actual_overlay_on_source.png)

![all_candidates_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00255_PrismCVCandidateExtractor.extract/all_candidates_overlay.png)

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

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

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
    "call": "00321_PrismGrounder.ground",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
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
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
        "prism_polygon": {
          "points": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ]
        },
        "apex": {
          "x": 621.3,
          "y": 80.9
        },
        "base_line": {
          "start": {
            "x": 229.2,
            "y": 757.0
          },
          "end": {
            "x": 1003.9,
            "y": 757.0
          }
        },
        "rays": {
          "count": 47,
          "first_8_records": [
            {
              "start": {
                "x": 226.0,
                "y": 771.0
              },
              "end": {
                "x": 450.0,
                "y": 383.0
              }
            },
            {
              "start": {
                "x": 220.0,
                "y": 771.0
              },
              "end": {
                "x": 439.0,
                "y": 391.0
              }
            },
            {
              "start": {
                "x": 221.0,
                "y": 766.0
              },
              "end": {
                "x": 529.0,
                "y": 766.0
              }
            },
            {
              "start": {
                "x": 139.0,
                "y": 434.0
              },
              "end": {
                "x": 267.0,
                "y": 411.0
              }
            },
            {
              "start": {
                "x": 489.0,
                "y": 772.0
              },
              "end": {
                "x": 784.0,
                "y": 772.0
              }
            },
            {
              "start": {
                "x": 688.0,
                "y": 206.0
              },
              "end": {
                "x": 821.0,
                "y": 437.0
              }
            },
            {
              "start": {
                "x": 785.0,
                "y": 773.0
              },
              "end": {
                "x": 1015.0,
                "y": 773.0
              }
            },
            {
              "start": {
                "x": 524.0,
                "y": 767.0
              },
              "end": {
                "x": 812.0,
                "y": 767.0
              }
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "incident_ray": {
          "start": {
            "x": 47.0,
            "y": 456.0
          },
          "end": {
            "x": 237.0,
            "y": 420.0
          }
        }
      },
      "ocr_result": {
        "status": "success",
        "tokens": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_011",
              "raw_text": "Fig. 8 Refraction through a Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 290.0,
                "y": 837.0,
                "width": 669.0,
                "height": 62.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.98457,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Fig",
                  "script": "latin",
                  "confidence": 0.9989254357832382,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_011"
            },
            {
              "id": "ocr_tok_009",
              "raw_text": "Glass Prism",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 506.0,
                "y": 613.0,
                "width": 245.0,
                "height": 53.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.99989,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Glass Prism",
                  "script": "latin",
                  "confidence": 0.987817609320542,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_009"
            },
            {
              "id": "ocr_tok_003",
              "raw_text": "Incident ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.99992,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Incident ray",
                  "script": "latin",
                  "confidence": 0.9437185399289797,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_003"
            },
            {
              "id": "ocr_tok_010",
              "raw_text": "Emergent ray",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 1022.0,
                "y": 610.0,
                "width": 238.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.99521,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "Emergent ray",
                  "script": "latin",
                  "confidence": 0.6244371543696388,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_010"
            },
            {
              "id": "ocr_tok_001",
              "raw_text": "A=60°",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.98817,
              "script_candidate": "mixed",
              "language_candidate": "und",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "A = 60",
                  "script": "latin",
                  "confidence": 0.4305139943295405,
                  "provider": "easyocr_bangla"
                },
                {
                  "text": "Δ = 60°",
                  "script": "greek",
                  "name": "confusable_var_delta",
                  "confidence": 0.791,
                  "provider": "equation_symbol_resolver"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_001"
            },
            {
              "id": "ocr_tok_008",
              "raw_text": "N2",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.95735,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N2",
                  "script": "latin",
                  "confidence": 0.8088539617403547,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_008"
            },
            {
              "id": "ocr_tok_006",
              "raw_text": "21",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.74629,
              "script_candidate": "numeric",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "12",
                  "script": "latin",
                  "confidence": 0.637097448320458,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_006"
            },
            {
              "id": "ocr_tok_002",
              "raw_text": "N1",
              "normalized_text": null,
              "bbox_source_px": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              },
              "polygon_source_px": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "confidence": 0.9941,
              "script_candidate": "latin",
              "language_candidate": "en",
              "provider": "rapidocr",
              "recognizer_model": "PP-OCRv6_rec_small.onnx",
              "candidate_alternatives": [
                {
                  "text": "N",
                  "script": "latin",
                  "confidence": 0.38066897407738054,
                  "provider": "easyocr_bangla"
                }
              ],
              "evidence_ref": "evidence_ocr_ocr_tok_002"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
        "provider": "multi_ocr_router",
        "model": "PP-OCRv6-onnx",
        "package": "rapidocr+easyocr+greek_ocr",
        "package_version": "3.9.2",
        "detector_model": "PP-OCRv6_det_small.onnx",
        "recognizer_model": "PP-OCRv6_rec_small.onnx+bengali.pth",
        "recognizer_language": "en+bn+el",
        "latency_ms": 19624.66850000783,
        "error": null,
        "metadata": {
          "bangla_available": true,
          "greek_available": true,
          "formula_available": false,
          "regions_count": 11,
          "token_count": 11
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
      "call": "00321_PrismGrounder.ground",
      "return_value": {
        "grounded_book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
            "entity_id": "prism_1",
            "grounding_state": "grounded",
            "supporting_evidence": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ],
            "checks": {
              "vertex_count": 3
            },
            "conflicts": [],
            "notes": "Prism triangular body grounded."
          }
        ],
        "new_evidence_records": {
          "ev_cv_prism_2a50897a2e704e7aa51642dab568571b": {
            "id": "ev_cv_prism_2a50897a2e704e7aa51642dab568571b",
            "method": "classical_cv",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": null,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "prism_cv_extractor",
            "model": null,
            "version": null,
            "payload": {
              "has_polygon": true,
              "has_apex": true
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_011": {
            "id": "ev_ocr_ocr_tok_011",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.98457,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Fig. 8 Refraction through a Prism",
              "bbox": {
                "x": 290.0,
                "y": 837.0,
                "width": 669.0,
                "height": 62.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_009": {
            "id": "ev_ocr_ocr_tok_009",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.99989,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Glass Prism",
              "bbox": {
                "x": 506.0,
                "y": 613.0,
                "width": 245.0,
                "height": 53.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_003": {
            "id": "ev_ocr_ocr_tok_003",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.99992,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Incident ray",
              "bbox": {
                "x": 46.0,
                "y": 342.0,
                "width": 216.0,
                "height": 55.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_010": {
            "id": "ev_ocr_ocr_tok_010",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.99521,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "Emergent ray",
              "bbox": {
                "x": 1022.0,
                "y": 610.0,
                "width": 238.0,
                "height": 49.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_001": {
            "id": "ev_ocr_ocr_tok_001",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.98817,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "A=60°",
              "bbox": {
                "x": 556.0,
                "y": 184.0,
                "width": 128.0,
                "height": 49.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_008": {
            "id": "ev_ocr_ocr_tok_008",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.95735,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "N2",
              "bbox": {
                "x": 730.0,
                "y": 541.0,
                "width": 85.0,
                "height": 73.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_006": {
            "id": "ev_ocr_ocr_tok_006",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.74629,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "21",
              "bbox": {
                "x": 738.0,
                "y": 465.0,
                "width": 63.0,
                "height": 76.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_002": {
            "id": "ev_ocr_ocr_tok_002",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.9941,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "N1",
              "bbox": {
                "x": 267.0,
                "y": 225.0,
                "width": 67.0,
                "height": 61.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_004": {
            "id": "ev_ocr_ocr_tok_004",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.99967,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "δ",
              "bbox": {
                "x": 1086.0,
                "y": 392.0,
                "width": 49.0,
                "height": 64.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_005": {
            "id": "ev_ocr_ocr_tok_005",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.98446,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "r1",
              "bbox": {
                "x": 500.0,
                "y": 412.0,
                "width": 56.0,
                "height": 53.0
              }
            },
            "metadata": {}
          },
          "ev_ocr_ocr_tok_007": {
            "id": "ev_ocr_ocr_tok_007",
            "method": "ocr",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
            "figure_id": "figure_001",
            "confidence": 0.99829,
            "verified": false,
            "coordinate_space": "source_px",
            "provider": "multi_ocr_router",
            "model": null,
            "version": null,
            "payload": {
              "raw_text": "e",
              "bbox": {
                "x": 909.0,
                "y": 518.0,
                "width": 34.0,
                "height": 36.0
              }
            },
            "metadata": {}
          }
        },
        "candidate_parameters": [
          {
            "raw_text": "A=60°",
            "numeric_value": 60.0,
            "raw_unit": "°",
            "canonical_unit": "°",
            "quantity_candidate": "angle",
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.98817
          },
          {
            "raw_text": "A = 60",
            "numeric_value": 60.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.889
          },
          {
            "raw_text": "Δ = 60°",
            "numeric_value": 60.0,
            "raw_unit": "°",
            "canonical_unit": "°",
            "quantity_candidate": "angle",
            "source_ocr_token_id": "ocr_tok_001",
            "confidence": 0.889
          },
          {
            "raw_text": "12",
            "numeric_value": 12.0,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": null,
            "source_ocr_token_id": "ocr_tok_006",
            "confidence": 0.672
          },
          {
            "raw_text": "r1",
            "numeric_value": null,
            "raw_unit": null,
            "canonical_unit": null,
            "quantity_candidate": "resistor_label",
            "source_ocr_token_id": "ocr_tok_005",
            "confidence": 0.98446
          }
        ],
        "parameter_associations": [
          {
            "candidate_id": "assoc_apex_ocr_tok_001",
            "target_entity_id": "prism_1",
            "target_quantity": "apex_angle",
            "value": 60.0,
            "unit": "deg",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_001"
            ],
            "association_checks": {
              "explicit_label": true
            },
            "confidence": 0.98817,
            "diagnostics": {}
          },
          {
            "candidate_id": "assoc_apex_ocr_tok_001",
            "target_entity_id": "prism_1",
            "target_quantity": "apex_angle",
            "value": 60.0,
            "unit": "deg",
            "state": "associated",
            "supporting_evidence": [
              "ev_ocr_ocr_tok_001"
            ],
            "association_checks": {
              "explicit_label": true
            },
            "confidence": 0.889,
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

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

**Comparison / debugging conclusion:** Grounder preserves polygon and incident ray, records OCR apex angle=60°, but does not ground internal/emergent ray entities. Raw detected ray segments remain in evidence, not constraints for the runtime solution.

**Changes, provenance and possible information loss:** This is where semantic roles become authoritative source coordinates. Inspect grounded_book_ir, diagnostics, candidate_parameters and associations separately.

[Complete stage input/output bundle](stage_data/16_ground.json)

- [PrismGrounder.ground — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00321_PrismGrounder.ground/STAGE.html)

- [Code: ai\evidence\grounding\prism.py](contracts/ai/evidence/grounding/prism.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00321_PrismGrounder.ground/actual_overlay_on_source.png)

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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
      },
      "page_ir": {
        "version": "1.0",
        "source": {
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {},
        "parameters": {},
        "resolutions": {},
        "assumptions": [],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
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
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_001"
              ],
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "evidence_refs": [
                "ev_ocr_ocr_tok_001"
              ],
              "confidence": 0.889,
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "polygon": {
                "_nested_fields_in_complete_snapshot": [
                  "points"
                ]
              },
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              }
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
          "assetId": "2a50897a2e704e7aa51642dab568571b",
          "width_px": 1280,
          "height_px": 960,
          "mimeType": "image/jpeg",
          "url": "/uploads/diagram_2a50897a.jpg",
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
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
        "text_blocks": {
          "count": 11,
          "first_8_records": [
            {
              "id": "ocr_tok_011",
              "text": "Fig. 8 Refraction through a Prism",
              "x": 290.0,
              "y": 837.0,
              "width": 669.0,
              "height": 62.0,
              "confidence": 0.98457,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_009",
              "text": "Glass Prism",
              "x": 506.0,
              "y": 613.0,
              "width": 245.0,
              "height": 53.0,
              "confidence": 0.99989,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_003",
              "text": "Incident ray",
              "x": 46.0,
              "y": 342.0,
              "width": 216.0,
              "height": 55.0,
              "confidence": 0.99992,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_010",
              "text": "Emergent ray",
              "x": 1022.0,
              "y": 610.0,
              "width": 238.0,
              "height": 49.0,
              "confidence": 0.99521,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_001",
              "text": "A=60°",
              "x": 556.0,
              "y": 184.0,
              "width": 128.0,
              "height": 49.0,
              "confidence": 0.98817,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_008",
              "text": "N2",
              "x": 730.0,
              "y": 541.0,
              "width": 85.0,
              "height": 73.0,
              "confidence": 0.95735,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_006",
              "text": "21",
              "x": 738.0,
              "y": 465.0,
              "width": 63.0,
              "height": 76.0,
              "confidence": 0.74629,
              "extraction_method": "ocr"
            },
            {
              "id": "ocr_tok_002",
              "text": "N1",
              "x": 267.0,
              "y": 225.0,
              "width": 67.0,
              "height": 61.0,
              "confidence": 0.9941,
              "extraction_method": "ocr"
            }
          ],
          "complete_list": "See complete stage bundle / original artifact"
        },
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

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

**Comparison / debugging conclusion:** Grounder preserves polygon and incident ray, records OCR apex angle=60°, but does not ground internal/emergent ray entities. Raw detected ray segments remain in evidence, not constraints for the runtime solution.

**Changes, provenance and possible information loss:** The wrapper returns after stages 8–16. Its entry record comes earlier in the profiler, but its output belongs here in the data-flow story.

[Complete stage input/output bundle](stage_data/17_fused.json)

- [EvidenceExtractionPipeline.extract_and_fuse — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- [Code: ai\evidence\pipeline.py](contracts/ai/evidence/pipeline.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/actual_overlay_on_source.png)

## 18. Enforce authoritative source dimensions

**Execution:** EXECUTED. **Verdict:** FRAME PASS; GEOMETRY STILL WRONG.

**Upstream → downstream:** Grounded BookIR and OCR-enriched PageIR → this component → Automatic resolution and explicit policy values.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00354_enforce_source_dimensions",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
        "id": "2a50897a2e704e7aa51642dab568571b",
        "mime_type": "image/jpeg",
        "original_filename": "photo_2026-10-10_12-06-37.jpg",
        "byte_size": 59343,
        "width_px": 1280,
        "height_px": 960,
        "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2",
        "storage_path": "D:\\AugmentedPhysics\\storage\\uploads\\diagram_2a50897a.jpg"
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
      "call": "00354_enforce_source_dimensions",
      "return_value": null
    }
  ],
  "in_place_outputs": [
    {
      "call": "00354_enforce_source_dimensions",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Source extent is enforced without correcting the already incorrect landmark/topology evidence.

**Changes, provenance and possible information loss:** Metadata enforcement is not geometric validation. Mutation is recorded in locals_after when the function returns None.

[Complete stage input/output bundle](stage_data/18_dimensions.json)

- [enforce_source_dimensions — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00354_enforce_source_dimensions/STAGE.html)

- [Code: ai\ingestion\source_dimensions.py](contracts/ai/ingestion/source_dimensions.py)

## 19. Automatic resolution and explicit policy values

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Enforce authoritative source dimensions → this component → Resolution decisions, units and calibration.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00355_AutoResolutionEngine.resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
      "call": "00355_AutoResolutionEngine.resolve",
      "return_value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "failures": [],
        "readiness": {
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "ready": true,
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "n",
            "apex_angle_deg"
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray.

**Changes, provenance and possible information loss:** Inspect field_changes.json for every addition/replacement. Auto-policy execution in this checkout may satisfy requirements without a human decision; that is observed behavior, not approval supplied during tracing.

[Complete stage input/output bundle](stage_data/19_auto.json)

- [AutoResolutionEngine.resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00355_AutoResolutionEngine.resolve/STAGE.html)

- [Every changed field before/after](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00355_AutoResolutionEngine.resolve/field_changes.json)

- [Code: ai\resolution\auto.py](contracts/ai/resolution/auto.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00355_AutoResolutionEngine.resolve/actual_overlay_on_source.png)

## 20. Resolution decisions, units and calibration

**Execution:** EXECUTED. **Verdict:** ASSUMPTIONS / UNRESOLVED EVIDENCE.

**Upstream → downstream:** Automatic resolution and explicit policy values → this component → Requirement and ambiguity analysis.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00368_ResolutionEngine.apply_resolution",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
    "call": "00376_CalibrationEngine.derive_for_subtype",
    "value": {
      "subtype": "prism",
      "entities": [
        {
          "id": "prism_1",
          "type": "prism_body",
          "label": "Glass Prism",
          "position_source_px": {
            "x": 621.3,
            "y": 80.9,
            "coordinate_space": "source_px",
            "method": "cv_prism_apex"
          },
          "geometry": {
            "polygon": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "bounds": {
              "x": 229.2,
              "y": 80.9,
              "width": 774.7,
              "height": 676.1
            }
          },
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
          ]
        },
        {
          "id": "ray_1",
          "type": "incident_ray",
          "label": "Incident ray",
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
          "id": "ray_2",
          "type": "refracted_ray",
          "label": null,
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
          "id": "ray_3",
          "type": "emergent_ray",
          "label": "Emergent ray",
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
          "id": "normal_1",
          "type": "normal_line",
          "label": "N1",
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
          "id": "normal_2",
          "type": "normal_line",
          "label": "N2",
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
        "apex_angle": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "apex_angle_deg": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "n": 1.52
      },
      "resolutions": {
        "n": {
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
        "coordinate_space": "source_px",
        "vertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "ray_origin": {
          "x": 47.0,
          "y": 456.0
        },
        "rayOrigin": {
          "x": 47.0,
          "y": 456.0
        },
        "ray_direction": {
          "x": 0.9825,
          "y": -0.1862
        },
        "rayDirection": {
          "x": 0.9825,
          "y": -0.1862
        }
      }
    }
  },
  {
    "call": "00423_ResolutionEngine.auto_resolve",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
    "call": "00425_CalibrationEngine.derive_for_subtype",
    "value": {
      "subtype": "prism",
      "entities": [
        {
          "id": "prism_1",
          "type": "prism_body",
          "label": "Glass Prism",
          "position_source_px": {
            "x": 621.3,
            "y": 80.9,
            "coordinate_space": "source_px",
            "method": "cv_prism_apex"
          },
          "geometry": {
            "polygon": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "bounds": {
              "x": 229.2,
              "y": 80.9,
              "width": 774.7,
              "height": 676.1
            }
          },
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
          ]
        },
        {
          "id": "ray_1",
          "type": "incident_ray",
          "label": "Incident ray",
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
          "id": "ray_2",
          "type": "refracted_ray",
          "label": null,
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
          "id": "ray_3",
          "type": "emergent_ray",
          "label": "Emergent ray",
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
          "id": "normal_1",
          "type": "normal_line",
          "label": "N1",
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
          "id": "normal_2",
          "type": "normal_line",
          "label": "N2",
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
        "apex_angle": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "apex_angle_deg": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "n": 1.52
      },
      "resolutions": {
        "n": {
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
        "coordinate_space": "source_px",
        "vertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "ray_origin": {
          "x": 47.0,
          "y": 456.0
        },
        "rayOrigin": {
          "x": 47.0,
          "y": 456.0
        },
        "ray_direction": {
          "x": 0.9825,
          "y": -0.1862
        },
        "rayDirection": {
          "x": 0.9825,
          "y": -0.1862
        }
      }
    }
  },
  {
    "call": "00436_CalibrationEngine.derive_for_subtype",
    "value": {
      "subtype": "prism",
      "entities": [
        {
          "id": "prism_1",
          "type": "prism_body",
          "label": "Glass Prism",
          "position_source_px": {
            "x": 621.3,
            "y": 80.9,
            "coordinate_space": "source_px",
            "method": "cv_prism_apex"
          },
          "geometry": {
            "polygon": {
              "_nested_fields_in_complete_snapshot": [
                "points"
              ]
            },
            "bounds": {
              "x": 229.2,
              "y": 80.9,
              "width": 774.7,
              "height": 676.1
            }
          },
          "attributes": {
            "confidence": 0.95,
            "precision": "approximate",
            "vlmLocalizationVerified": false
          },
          "evidence_refs": [
            "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
          ]
        },
        {
          "id": "ray_1",
          "type": "incident_ray",
          "label": "Incident ray",
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
          "id": "ray_2",
          "type": "refracted_ray",
          "label": null,
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
          "id": "ray_3",
          "type": "emergent_ray",
          "label": "Emergent ray",
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
          "id": "normal_1",
          "type": "normal_line",
          "label": "N1",
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
          "id": "normal_2",
          "type": "normal_line",
          "label": "N2",
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
        "apex_angle": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "apex_angle_deg": {
          "value": 60.0,
          "unit": "deg",
          "status": "observed",
          "provenance": {
            "source": "ocr",
            "evidence_refs": [
              "ev_ocr_ocr_tok_001"
            ],
            "confidence": 0.889,
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
        "n": 1.52
      },
      "resolutions": {
        "n": {
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
        "coordinate_space": "source_px",
        "vertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757.0
          },
          {
            "x": 1003.9,
            "y": 757.0
          }
        ],
        "ray_origin": {
          "x": 47.0,
          "y": 456.0
        },
        "rayOrigin": {
          "x": 47.0,
          "y": 456.0
        },
        "ray_direction": {
          "x": 0.9825,
          "y": -0.1862
        },
        "rayDirection": {
          "x": 0.9825,
          "y": -0.1862
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
      "call": "00368_ResolutionEngine.apply_resolution",
      "return_value": {
        "success": true,
        "parameter_name": "n",
        "resolved_value": 1.52,
        "canonical_unit": "",
        "original_entered_value": "1.52",
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
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "ready": true,
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "n",
            "apex_angle_deg"
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
      "call": "00376_CalibrationEngine.derive_for_subtype",
      "return_value": null
    },
    {
      "call": "00423_ResolutionEngine.auto_resolve",
      "return_value": {
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "n",
          "apex_angle_deg"
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
      "call": "00425_CalibrationEngine.derive_for_subtype",
      "return_value": null
    },
    {
      "call": "00436_CalibrationEngine.derive_for_subtype",
      "return_value": null
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** Consistent resolved units and explicit calibration provenance. A scale derived using assumed physical length must remain assumption-derived; it is not measured ground truth.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray.

**Changes, provenance and possible information loss:** Several calls can occur inside auto-resolution. Exact invocation records are kept separately; null return can mean calibration was unavailable, not that a zero scale was measured.

[Complete stage input/output bundle](stage_data/20_calibration.json)

- [ResolutionEngine.apply_resolution — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00368_ResolutionEngine.apply_resolution/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00376_CalibrationEngine.derive_for_subtype/STAGE.html)

- [ResolutionEngine.auto_resolve — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00423_ResolutionEngine.auto_resolve/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00425_CalibrationEngine.derive_for_subtype/STAGE.html)

- [CalibrationEngine.derive_for_subtype — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00436_CalibrationEngine.derive_for_subtype/STAGE.html)

- [Code: ai\resolution\engine.py](contracts/ai/resolution/engine.py)

- [Code: ai\resolution\calibration.py](contracts/ai/resolution/calibration.py)

## 21. Requirement and ambiguity analysis

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Resolution decisions, units and calibration → this component → Readiness decision.

**What it receives — actual input (selected recorded fields):**

```json
{
  "count": 12,
  "first_8_records": [
    {
      "call": "00378_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
      "call": "00380_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "subtype": "prism",
          "required_entities": [
            "prism_body"
          ],
          "required_geometry": [
            "vertices",
            "ray_origin",
            "ray_direction"
          ],
          "parameters": {
            "n": {
              "id": "req_prism_n",
              "name": "n",
              "dimension": "refractive_index",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": 1.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_crown_glass_refractive_index",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "apex_angle_deg": {
              "id": "req_prism_apex_angle",
              "name": "apex_angle_deg",
              "dimension": "angle",
              "required": true,
              "allowed_units": [
                "deg",
                "degree",
                "°"
              ],
              "canonical_unit": "deg",
              "min_value": 1.0,
              "max_value": 179.0,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_prism_apex_angle",
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
            "policy_crown_glass_refractive_index",
            "policy_prism_apex_angle",
            "policy_normalized_prism_incident_ray"
          ],
          "parameter_aliases": {
            "apex_angle": "apex_angle_deg",
            "apexAngle": "apex_angle_deg",
            "A": "apex_angle_deg",
            "refractive_index": "n",
            "refractiveIndex": "n",
            "rayOrigin": "ray_origin",
            "rayDirection": "ray_direction",
            "prismVertices": "vertices"
          },
          "notes": "Triangular/polygonal prism refraction with angle of deviation δ."
        },
        "issues": []
      }
    },
    {
      "call": "00381_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "subtype": "prism",
          "required_entities": [
            "prism_body"
          ],
          "required_geometry": [
            "vertices",
            "ray_origin",
            "ray_direction"
          ],
          "parameters": {
            "n": {
              "id": "req_prism_n",
              "name": "n",
              "dimension": "refractive_index",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": 1.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_crown_glass_refractive_index",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "apex_angle_deg": {
              "id": "req_prism_apex_angle",
              "name": "apex_angle_deg",
              "dimension": "angle",
              "required": true,
              "allowed_units": [
                "deg",
                "degree",
                "°"
              ],
              "canonical_unit": "deg",
              "min_value": 1.0,
              "max_value": 179.0,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_prism_apex_angle",
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
            "policy_crown_glass_refractive_index",
            "policy_prism_apex_angle",
            "policy_normalized_prism_incident_ray"
          ],
          "parameter_aliases": {
            "apex_angle": "apex_angle_deg",
            "apexAngle": "apex_angle_deg",
            "A": "apex_angle_deg",
            "refractive_index": "n",
            "refractiveIndex": "n",
            "rayOrigin": "ray_origin",
            "rayDirection": "ray_direction",
            "prismVertices": "vertices"
          },
          "notes": "Triangular/polygonal prism refraction with angle of deviation δ."
        },
        "issues": [],
        "satisfied_reqs": [],
        "missing_reqs": []
      }
    },
    {
      "call": "00401_ResolutionAnalyzer.analyze",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
      "call": "00403_ResolutionAnalyzer._check_geometry_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "subtype": "prism",
          "required_entities": [
            "prism_body"
          ],
          "required_geometry": [
            "vertices",
            "ray_origin",
            "ray_direction"
          ],
          "parameters": {
            "n": {
              "id": "req_prism_n",
              "name": "n",
              "dimension": "refractive_index",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": 1.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_crown_glass_refractive_index",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "apex_angle_deg": {
              "id": "req_prism_apex_angle",
              "name": "apex_angle_deg",
              "dimension": "angle",
              "required": true,
              "allowed_units": [
                "deg",
                "degree",
                "°"
              ],
              "canonical_unit": "deg",
              "min_value": 1.0,
              "max_value": 179.0,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_prism_apex_angle",
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
            "policy_crown_glass_refractive_index",
            "policy_prism_apex_angle",
            "policy_normalized_prism_incident_ray"
          ],
          "parameter_aliases": {
            "apex_angle": "apex_angle_deg",
            "apexAngle": "apex_angle_deg",
            "A": "apex_angle_deg",
            "refractive_index": "n",
            "refractiveIndex": "n",
            "rayOrigin": "ray_origin",
            "rayDirection": "ray_direction",
            "prismVertices": "vertices"
          },
          "notes": "Triangular/polygonal prism refraction with angle of deviation δ."
        },
        "issues": []
      }
    },
    {
      "call": "00404_ResolutionAnalyzer._check_parameter_requirements",
      "value": {
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "subtype": "prism",
          "required_entities": [
            "prism_body"
          ],
          "required_geometry": [
            "vertices",
            "ray_origin",
            "ray_direction"
          ],
          "parameters": {
            "n": {
              "id": "req_prism_n",
              "name": "n",
              "dimension": "refractive_index",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": 1.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_crown_glass_refractive_index",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "apex_angle_deg": {
              "id": "req_prism_apex_angle",
              "name": "apex_angle_deg",
              "dimension": "angle",
              "required": true,
              "allowed_units": [
                "deg",
                "degree",
                "°"
              ],
              "canonical_unit": "deg",
              "min_value": 1.0,
              "max_value": 179.0,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_prism_apex_angle",
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
            "policy_crown_glass_refractive_index",
            "policy_prism_apex_angle",
            "policy_normalized_prism_incident_ray"
          ],
          "parameter_aliases": {
            "apex_angle": "apex_angle_deg",
            "apexAngle": "apex_angle_deg",
            "A": "apex_angle_deg",
            "refractive_index": "n",
            "refractiveIndex": "n",
            "rayOrigin": "ray_origin",
            "rayDirection": "ray_direction",
            "prismVertices": "vertices"
          },
          "notes": "Triangular/polygonal prism refraction with angle of deviation δ."
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
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
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
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "position_source_px": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidence_refs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "subtype": "prism",
          "required_entities": [
            "prism_body"
          ],
          "required_geometry": [
            "vertices",
            "ray_origin",
            "ray_direction"
          ],
          "parameters": {
            "n": {
              "id": "req_prism_n",
              "name": "n",
              "dimension": "refractive_index",
              "required": true,
              "allowed_units": [],
              "canonical_unit": null,
              "min_value": 1.0,
              "max_value": null,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": false,
              "default_policy_id": "policy_crown_glass_refractive_index",
              "_other_fields_in_complete_snapshot": [
                "prompt_question",
                "prompt_question_bn",
                "help_text",
                "is_scale_dependent"
              ]
            },
            "apex_angle_deg": {
              "id": "req_prism_apex_angle",
              "name": "apex_angle_deg",
              "dimension": "angle",
              "required": true,
              "allowed_units": [
                "deg",
                "degree",
                "°"
              ],
              "canonical_unit": "deg",
              "min_value": 1.0,
              "max_value": 179.0,
              "allow_zero": false,
              "allowed_categories": [],
              "can_derive_from_geometry": true,
              "default_policy_id": "policy_prism_apex_angle",
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
            "policy_crown_glass_refractive_index",
            "policy_prism_apex_angle",
            "policy_normalized_prism_incident_ray"
          ],
          "parameter_aliases": {
            "apex_angle": "apex_angle_deg",
            "apexAngle": "apex_angle_deg",
            "A": "apex_angle_deg",
            "refractive_index": "n",
            "refractiveIndex": "n",
            "rayOrigin": "ray_origin",
            "rayDirection": "ray_direction",
            "prismVertices": "vertices"
          },
          "notes": "Triangular/polygonal prism refraction with angle of deviation δ."
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
    "count": 12,
    "first_8_records": [
      {
        "call": "00378_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "prism",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "n",
            "apex_angle_deg"
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
        "call": "00380_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00381_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00401_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "prism",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "n",
            "apex_angle_deg"
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
        "call": "00403_ResolutionAnalyzer._check_geometry_requirements",
        "return_value": null
      },
      {
        "call": "00404_ResolutionAnalyzer._check_parameter_requirements",
        "return_value": null
      },
      {
        "call": "00438_ResolutionAnalyzer.analyze",
        "return_value": {
          "subtype": "prism",
          "blockers": [],
          "warnings": [],
          "missing_requirements": [],
          "satisfied_requirements": [
            "n",
            "apex_angle_deg"
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
      }
    ],
    "complete_list": "See complete stage bundle / original artifact"
  },
  "in_place_outputs": [
    {
      "call": "00380_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00381_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "NEEDS_REVIEW",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00403_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00404_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00486_ResolutionAnalyzer._check_geometry_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00487_ResolutionAnalyzer._check_parameter_requirements",
      "post_call_locals": {
        "book_ir": {
          "version": "1.0",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** The current analyzer checks required entities/parameters and ambiguity. It does not compare every proposed line or point to image pixels.

[Complete stage input/output bundle](stage_data/21_requirements.json)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00378_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00380_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00381_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00401_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00403_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00404_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00438_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00440_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00441_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [ResolutionAnalyzer.analyze — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00484_ResolutionAnalyzer.analyze/STAGE.html)

- [ResolutionAnalyzer._check_geometry_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00486_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- [ResolutionAnalyzer._check_parameter_requirements — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00487_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- [Code: ai\resolution\analyzer.py](contracts/ai/resolution/analyzer.py)

## 22. Readiness decision

**Execution:** EXECUTED. **Verdict:** RUNNABLE ≠ SOURCE-REGISTERED.

**Upstream → downstream:** Requirement and ambiguity analysis → this component → PhysicsCompiler entry and gate.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00377_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "NEEDS_REVIEW",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
    "call": "00400_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
    "call": "00483_ReadinessEvaluator.evaluate",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
      "call": "00377_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "n",
          "apex_angle_deg"
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
      "call": "00400_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "n",
          "apex_angle_deg"
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
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "n",
          "apex_angle_deg"
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
      "call": "00483_ReadinessEvaluator.evaluate",
      "return_value": {
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "ready": true,
        "blockers": [],
        "warnings": [],
        "missing_requirements": [],
        "satisfied_requirements": [
          "n",
          "apex_angle_deg"
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray. The accepted requirement set and all blockers/warnings are in the actual outputs below.

**Changes, provenance and possible information loss:** All repeated evaluations are recorded. Use the final pre-compile decision as the gate, while retaining earlier decisions to see state changes.

[Complete stage input/output bundle](stage_data/22_readiness.json)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00377_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00400_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00437_ReadinessEvaluator.evaluate/STAGE.html)

- [ReadinessEvaluator.evaluate — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00483_ReadinessEvaluator.evaluate/STAGE.html)

- [Code: ai\resolution\evaluator.py](contracts/ai/resolution/evaluator.py)

## 23. PhysicsCompiler entry and gate

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** Readiness decision → this component → Canonical scene construction and schema validation.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00460_PhysicsCompiler.compile",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
      "call": "00460_PhysicsCompiler.compile",
      "return_value": {
        "status": "READY",
        "scene": {
          "domain": "optics",
          "subtype": "prism",
          "source": {
            "type": "book_figure",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            },
            "apex_angle_deg": 60.0
          },
          "parameters": {
            "refractiveIndex": {
              "value": 1.52,
              "unit": "",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_crown_glass_refractive_index)",
                "policyId": "policy_crown_glass_refractive_index",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "apexAngle": {
              "value": 60.0,
              "unit": "deg",
              "provenance": "ocr",
              "evidenceProvenance": {
                "source": "ocr",
                "confidence": 0.889,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            }
          },
          "assumptions": [
            {
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

**Changes, provenance and possible information loss:** The active compiler implementation is ai/ingestion/PhysicsCompiler.py. The scene_compiler module re-exports it.

[Complete stage input/output bundle](stage_data/23_gate.json)

- [PhysicsCompiler.compile — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00460_PhysicsCompiler.compile/STAGE.html)

- [Code: ai\ingestion\PhysicsCompiler.py](contracts/ai/ingestion/PhysicsCompiler.py)

![actual_overlay_on_source.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00460_PhysicsCompiler.compile/actual_overlay_on_source.png)

## 24. Canonical scene construction and schema validation

**Execution:** EXECUTED. **Verdict:** PROPAGATED / RECONSTRUCTED GEOMETRY.

**Upstream → downstream:** PhysicsCompiler entry and gate → this component → API response delivered to the browser.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "call": "00506_PhysicsCompiler._build_canonical_scene",
    "value": {
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
      "subtype": "prism"
    }
  },
  {
    "call": "00514_PhysicsCompiler._populate_canonical_prism",
    "value": {
      "scene": {
        "schemaVersion": "1.0",
        "id": "PHY-OPTI-figure_001",
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
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
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
    "call": "00529_PhysicsCompiler._preserve_parameter_provenance",
    "value": {
      "scene": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60.0
        },
        "parameters": {
          "refractiveIndex": {
            "value": 1.52,
            "unit": "",
            "provenance": "observed"
          },
          "apexAngle": {
            "value": 60.0,
            "unit": "deg",
            "provenance": "observed"
          }
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements"
        ]
      },
      "book_ir": {
        "isPhysics": true,
        "domain": "optics",
        "subtype": "prism",
        "status": "READY_TO_COMPILE",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          }
        },
        "parameters": {
          "apex_angle": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "apex_angle_deg": {
            "value": 60.0,
            "unit": "deg",
            "status": "observed",
            "provenance": {
              "source": "ocr",
              "confidence": 0.889,
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
          "n": 1.52
        },
        "resolutions": {
          "n": {
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
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
            "provenance": "auto_policy",
            "confidence": 0.8
          }
        ],
        "entities": [
          {
            "id": "prism_1",
            "type": "prism_body",
            "label": "Glass Prism",
            "position_source_px": {
              "x": 621.3,
              "y": 80.9,
              "coordinate_space": "source_px",
              "method": "cv_prism_apex"
            },
            "geometry": {
              "bounds": {
                "x": 229.2,
                "y": 80.9,
                "width": 774.7,
                "height": 676.1
              },
              "_nested_fields_in_complete_snapshot": [
                "polygon"
              ]
            },
            "attributes": {
              "confidence": 0.95,
              "precision": "approximate",
              "vlmLocalizationVerified": false
            },
            "evidence_refs": [
              "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
            ]
          },
          {
            "id": "ray_1",
            "type": "incident_ray",
            "label": "Incident ray",
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
            "id": "ray_2",
            "type": "refracted_ray",
            "label": null,
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
            "id": "ray_3",
            "type": "emergent_ray",
            "label": "Emergent ray",
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
            "id": "normal_1",
            "type": "normal_line",
            "label": "N1",
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
            "id": "normal_2",
            "type": "normal_line",
            "label": "N2",
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
            "type": "refracts_at",
            "from": "ray_1",
            "to": "prism_1",
            "confidence": 0.95
          },
          {
            "type": "refracts_at",
            "from": "prism_1",
            "to": "ray_3",
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
      "subtype": "prism"
    }
  },
  {
    "call": "00530_validate_canonical_scene",
    "value": {
      "scene": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60.0
        },
        "parameters": {
          "refractiveIndex": {
            "value": 1.52,
            "unit": "",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_crown_glass_refractive_index)",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "userAccepted": false,
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          },
          "apexAngle": {
            "value": 60.0,
            "unit": "deg",
            "provenance": "ocr",
            "evidenceProvenance": {
              "source": "ocr",
              "confidence": 0.889,
              "notes": "",
              "_nested_fields_in_complete_snapshot": [
                "evidenceRefs",
                "derivedFrom"
              ]
            }
          }
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
      "call": "00506_PhysicsCompiler._build_canonical_scene",
      "return_value": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
          "vertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "prismVertices": [
            {
              "x": 621.3,
              "y": 80.9
            },
            {
              "x": 229.2,
              "y": 757.0
            },
            {
              "x": 1003.9,
              "y": 757.0
            }
          ],
          "ray_origin": {
            "x": 47.0,
            "y": 456.0
          },
          "rayOrigin": {
            "x": 47.0,
            "y": 456.0
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60.0
        },
        "parameters": {
          "refractiveIndex": {
            "value": 1.52,
            "unit": "",
            "provenance": "auto_policy",
            "evidenceProvenance": {
              "source": "auto_policy",
              "evidenceRefs": [],
              "derivedFrom": [],
              "confidence": 0.8,
              "notes": "Resolved via policy_default (policy: policy_crown_glass_refractive_index)",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "userAccepted": false
            }
          },
          "apexAngle": {
            "value": 60.0,
            "unit": "deg",
            "provenance": "ocr",
            "evidenceProvenance": {
              "source": "ocr",
              "evidenceRefs": [
                "ev_ocr_ocr_tok_001"
              ],
              "derivedFrom": [
                "ev_ocr_ocr_tok_001"
              ],
              "confidence": 0.889,
              "notes": ""
            }
          }
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements"
        ]
      }
    },
    {
      "call": "00514_PhysicsCompiler._populate_canonical_prism",
      "return_value": null
    },
    {
      "call": "00529_PhysicsCompiler._preserve_parameter_provenance",
      "return_value": null
    },
    {
      "call": "00530_validate_canonical_scene",
      "return_value": []
    }
  ],
  "in_place_outputs": [
    {
      "call": "00514_PhysicsCompiler._populate_canonical_prism",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-OPTI-figure_001",
          "domain": "optics",
          "subtype": "prism",
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
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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
      "call": "00529_PhysicsCompiler._preserve_parameter_provenance",
      "post_call_locals": {
        "scene": {
          "schemaVersion": "1.0",
          "id": "PHY-OPTI-figure_001",
          "domain": "optics",
          "subtype": "prism",
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
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "page_ir_version": "1.0",
          "figure_id": "figure_001",
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "status_notes": "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification.",
          "calibration": null,
          "id": "2a50897a2e704e7aa51642dab568571b_figure_001",
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

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

**Comparison / debugging conclusion:** Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

**Changes, provenance and possible information loss:** Populate methods mutate scene in place and return None. Their real output is locals_after.scene and the enclosing compile result. None is not a failed scene.

[Complete stage input/output bundle](stage_data/24_compile.json)

- [PhysicsCompiler._build_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00506_PhysicsCompiler._build_canonical_scene/STAGE.html)

- [PhysicsCompiler._populate_canonical_prism — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00514_PhysicsCompiler._populate_canonical_prism/STAGE.html)

- [PhysicsCompiler._preserve_parameter_provenance — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00529_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- [validate_canonical_scene — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00530_validate_canonical_scene/STAGE.html)

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
          "subtype": "prism",
          "source": {
            "type": "book_figure",
            "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            },
            "apex_angle_deg": 60.0
          },
          "parameters": {
            "refractiveIndex": {
              "value": 1.52,
              "unit": "",
              "provenance": "auto_policy",
              "evidenceProvenance": {
                "source": "auto_policy",
                "confidence": 0.8,
                "notes": "Resolved via policy_default (policy: policy_crown_glass_refractive_index)",
                "policyId": "policy_crown_glass_refractive_index",
                "policyVersion": "1.0",
                "userAccepted": false,
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "apexAngle": {
              "value": 60.0,
              "unit": "deg",
              "provenance": "ocr",
              "evidenceProvenance": {
                "source": "ocr",
                "confidence": 0.889,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            }
          },
          "assumptions": [
            {
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
            "elements"
          ]
        },
        "book_ir": {
          "isPhysics": true,
          "domain": "optics",
          "subtype": "prism",
          "status": "READY_TO_COMPILE",
          "geometry": {
            "width": 1280,
            "height": 960,
            "coordinate_space": "source_px",
            "vertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "prismVertices": [
              {
                "x": 621.3,
                "y": 80.9
              },
              {
                "x": 229.2,
                "y": 757.0
              },
              {
                "x": 1003.9,
                "y": 757.0
              }
            ],
            "ray_origin": {
              "x": 47.0,
              "y": 456.0
            },
            "rayOrigin": {
              "x": 47.0,
              "y": 456.0
            },
            "ray_direction": {
              "x": 0.9825,
              "y": -0.1862
            },
            "rayDirection": {
              "x": 0.9825,
              "y": -0.1862
            }
          },
          "parameters": {
            "apex_angle": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "apex_angle_deg": {
              "value": 60.0,
              "unit": "deg",
              "status": "observed",
              "provenance": {
                "source": "ocr",
                "confidence": 0.889,
                "notes": "",
                "_nested_fields_in_complete_snapshot": [
                  "evidenceRefs",
                  "derivedFrom"
                ]
              }
            },
            "n": 1.52
          },
          "resolutions": {
            "n": {
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
              "parameter": "n",
              "policyId": "policy_crown_glass_refractive_index",
              "policyVersion": "1.0",
              "value": 1.52,
              "unit": null,
              "reason": "Refractive index of standard optical crown glass (n = 1.52).",
              "provenance": "auto_policy",
              "confidence": 0.8
            }
          ],
          "entities": [
            {
              "id": "prism_1",
              "type": "prism_body",
              "label": "Glass Prism",
              "positionSourcePx": {
                "x": 621.3,
                "y": 80.9,
                "coordinate_space": "source_px",
                "method": "cv_prism_apex"
              },
              "geometry": {
                "bounds": {
                  "x": 229.2,
                  "y": 80.9,
                  "width": 774.7,
                  "height": 676.1
                },
                "_nested_fields_in_complete_snapshot": [
                  "polygon"
                ]
              },
              "attributes": {
                "confidence": 0.95,
                "precision": "approximate",
                "vlmLocalizationVerified": false
              },
              "evidenceRefs": [
                "ev_cv_prism_2a50897a2e704e7aa51642dab568571b"
              ]
            },
            {
              "id": "ray_1",
              "type": "incident_ray",
              "label": "Incident ray",
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
              "id": "ray_2",
              "type": "refracted_ray",
              "label": null,
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
              "id": "ray_3",
              "type": "emergent_ray",
              "label": "Emergent ray",
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
              "id": "normal_1",
              "type": "normal_line",
              "label": "N1",
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
              "id": "normal_2",
              "type": "normal_line",
              "label": "N2",
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
              "type": "refracts_at",
              "from": "ray_1",
              "to": "prism_1",
              "confidence": 0.95
            },
            {
              "type": "refracts_at",
              "from": "prism_1",
              "to": "ray_3",
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
          "id": "2a50897a2e704e7aa51642dab568571b",
          "mimeType": "image/jpeg",
          "originalFilename": "photo_2026-10-10_12-06-37.jpg",
          "byteSize": 59343,
          "width_px": 1280,
          "height_px": 960,
          "sha256": "59aaf1ff61b692e086a588d9916227a1fc3720e8135095484f99abb335739cd2"
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

**Changes, provenance and possible information loss:** This is the handler return, after nested work. Exact HTTP status/body are retained separately from the Python object.

[Complete stage input/output bundle](stage_data/25_response.json)

- [ingest_diagram — exact input/output/locals/contract](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- [HTTP response 1792207803683424300_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/http/1792207803683424300_response_body.json)

- [Code: apps\api\main.py](contracts/apps/api/main.py)

## 26. Frontend receives result and selects next state

**Execution:** EXECUTED. **Verdict:** SCENE ACCEPTED.

**Upstream → downstream:** API response delivered to the browser → this component → Review / explicit compile request branch.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 3191.2000000178814,
    "data": [
      "UPLOADING"
    ]
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 34126.70000001788,
    "data": [
      "ANALYZING"
    ]
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._normalizeSceneBackground",
    "phase": "input",
    "wallTime": 34130.59999999404,
    "data": [
      {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
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
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements"
        ]
      }
    ]
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 34133.20000001788,
    "data": [
      "READY_TO_SIMULATE"
    ]
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator._setState",
    "phase": "input",
    "wallTime": 34336,
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 3191.4000000059605,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 34126.90000000596,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._normalizeSceneBackground",
      "phase": "output",
      "wallTime": 34133,
      "data": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 34133.30000001192,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator._setState",
      "phase": "output",
      "wallTime": 34336,
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

**Changes, provenance and possible information loss:** Only events after startWithFile for this trace are used here. Startup/demo events remain in the raw log but are excluded from this diagram’s runtime evidence.

[Complete stage input/output bundle](stage_data/26_orchestrator.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** No output exists for this diagram at this component. The expected contract is described for debugging, not reported as an executed result.

**Changes, provenance and possible information loss:** No transformation, mutation or output was produced by this component for this diagram: the branch was not reached. Expected behavior above is a contract, not an observed result.

[Complete stage input/output bundle](stage_data/27_review.json)

- [HTTP response 1792207803683424300_response_body.json](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/http/1792207803683424300_response_body.json)

- [Code: apps\web\src\features\simulations\core\SimulationOrchestrator.js](contracts/apps/web/src/features/simulations/core/SimulationOrchestrator.js)

## 28. InteractiveFigure receives the compiled scene

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** Review / explicit compile request branch → this component → FigureViewport background and layout.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "InteractiveFigure.load",
    "phase": "input",
    "wallTime": 34144.80000001192,
    "data": [
      {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "InteractiveFigure.load",
      "phase": "output",
      "wallTime": 34307.5,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** A figure bound to the original image, with the correct domain runtime and an initial rendered output. No unrelated demo geometry.

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** load performs layout/runtime initialization internally. The t0 event immediately after load is an observed snapshot; exact child JS calls were not all instrumented.

[Complete stage input/output bundle](stage_data/28_figure.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

## 29. FigureViewport background and layout

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** InteractiveFigure receives the compiled scene → this component → PhysicsRuntime normalization and adapter initialization.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "FigureViewport.setBackground",
    "phase": "input",
    "wallTime": 34145.40000000596,
    "data": [
      "/uploads/diagram_2a50897a.jpg",
      1280,
      960
    ]
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "FigureViewport.recalculate",
    "phase": "input",
    "wallTime": 34216.80000001192,
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "FigureViewport.recalculate",
      "phase": "output",
      "wallTime": 34276.09999999404,
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "FigureViewport.setBackground",
      "phase": "output",
      "wallTime": 34276.20000001788,
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Preserve source_px. The measured image rectangle and mapper offsets are shown in the coordinate stage; CSS pixels are not substituted into BookIR.

[Complete stage input/output bundle](stage_data/29_background.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

- [Code: apps\web\src\components\FigureViewport.js](contracts/apps/web/src/components/FigureViewport.js)

## 30. PhysicsRuntime normalization and adapter initialization

**Execution:** EXECUTED. **Verdict:** EXECUTED; UPSTREAM REGISTRATION FAILURE.

**Upstream → downstream:** FigureViewport background and layout → this component → Domain solver and actual initial state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.load",
    "phase": "input",
    "wallTime": 34286.09999999404,
    "data": [
      {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "imageUrl": "/uploads/diagram_2a50897a.jpg",
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
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.normalizeScene",
    "phase": "input",
    "wallTime": 34291.40000000596,
    "data": [
      {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.normalizeScene",
      "phase": "output",
      "wallTime": 34291.70000001788,
      "data": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.load",
      "phase": "output",
      "wallTime": 34305.09999999404,
      "data": {
        "domain": "optics",
        "subtype": "prism",
        "time": 0,
        "state": {
          "domain": "optics",
          "subtype": "prism",
          "type": "prism",
          "running": false,
          "incidenceAngle_deg": 40.842553023013416,
          "refractedAngle_deg": 25.48353691375652,
          "deviationAngle_deg": 39.754070946628936,
          "refractiveIndex": 1.52,
          "criticalAngle_deg": 41.139510414899156,
          "tir": false,
          "rayCount": 3,
          "_nested_fields_in_complete_snapshot": [
            "solution"
          ]
        },
        "geometry": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "opticalAxis": null,
          "lens": null,
          "mirror": null,
          "object": null,
          "image": null,
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays",
            "landmarks",
            "prismPolygon",
            "prism",
            "handles"
          ]
        },
        "telemetry": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "incidenceAngle_deg": 40.842553023013416,
          "refractedAngle_deg": 25.48353691375652,
          "deviationAngle_deg": 39.754070946628936,
          "refractiveIndex": 1.52,
          "criticalAngle_deg": 41.139510414899156,
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays"
          ]
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex"
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
          "subtype": "prism",
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
          "subtype": "prism",
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
          "subtype": "prism",
          "type": "prism",
          "running": false,
          "incidenceAngle_deg": 40.842553023013416,
          "refractedAngle_deg": 25.48353691375652,
          "deviationAngle_deg": 39.754070946628936,
          "refractiveIndex": 1.52,
          "criticalAngle_deg": 41.139510414899156,
          "tir": false,
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** The source-matched scene reaches the expected runtime. No new source-coordinate displacement was established at this boundary. See exact normalized scene and DOM evidence.

**Changes, provenance and possible information loss:** Registry/capability/adapter child calls are established by runtime source and captured boundary/output. Their independent entry/exit arguments were not recorded; they are not presented as new trace snapshots.

[Complete stage input/output bundle](stage_data/30_runtime.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

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
      "subtype": "prism",
      "source": {
        "type": "book_figure",
        "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
        "figure_id": "figure_001",
        "width": 1280,
        "height": 960,
        "image_width_px": 1280,
        "image_height_px": 960,
        "image": "/uploads/diagram_2a50897a.jpg"
      },
      "geometry": {
        "width": 1280,
        "height": 960,
        "coordinate_space": "source_px",
        "vertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757
          },
          {
            "x": 1003.9,
            "y": 757
          }
        ],
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757
          },
          {
            "x": 1003.9,
            "y": 757
          }
        ],
        "ray_origin": {
          "x": 47,
          "y": 456
        },
        "rayOrigin": {
          "x": 47,
          "y": 456
        },
        "ray_direction": {
          "x": 0.9825,
          "y": -0.1862
        },
        "rayDirection": {
          "x": 0.9825,
          "y": -0.1862
        },
        "apex_angle_deg": 60
      },
      "parameters": {
        "refractiveIndex": {
          "value": 1.52,
          "unit": "",
          "provenance": "auto_policy",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        },
        "apexAngle": {
          "value": 60,
          "unit": "deg",
          "provenance": "ocr",
          "_nested_fields_in_complete_snapshot": [
            "evidenceProvenance"
          ]
        }
      },
      "assumptions": [
        {
          "parameter": "n",
          "policyId": "policy_crown_glass_refractive_index",
          "policyVersion": "1.0",
          "value": 1.52,
          "unit": null,
          "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
        "subtype": "prism",
        "type": "prism",
        "running": false,
        "incidenceAngle_deg": 40.842553023013416,
        "refractedAngle_deg": 25.48353691375652,
        "deviationAngle_deg": 39.754070946628936,
        "refractiveIndex": 1.52,
        "criticalAngle_deg": 41.139510414899156,
        "tir": false,
        "rayCount": 3,
        "solution": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays"
          ]
        }
      },
      "output": {
        "domain": "optics",
        "subtype": "prism",
        "time": 0,
        "state": {
          "domain": "optics",
          "subtype": "prism",
          "type": "prism",
          "running": false,
          "incidenceAngle_deg": 40.842553023013416,
          "refractedAngle_deg": 25.48353691375652,
          "deviationAngle_deg": 39.754070946628936,
          "refractiveIndex": 1.52,
          "criticalAngle_deg": 41.139510414899156,
          "tir": false,
          "rayCount": 3,
          "_nested_fields_in_complete_snapshot": [
            "solution"
          ]
        },
        "geometry": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "opticalAxis": null,
          "lens": null,
          "mirror": null,
          "object": null,
          "image": null,
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays",
            "landmarks",
            "prismPolygon",
            "prism",
            "handles"
          ]
        },
        "telemetry": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "incidenceAngle_deg": 40.842553023013416,
          "refractedAngle_deg": 25.48353691375652,
          "deviationAngle_deg": 39.754070946628936,
          "refractiveIndex": 1.52,
          "criticalAngle_deg": 41.139510414899156,
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays"
          ]
        },
        "events": [],
        "editableParameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex"
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

**What correct handling of THIS diagram requires:** At t=0 the prism polygon and ray segments should be compared with the printed paths. If a physical model with assumed n disagrees with the schematic, expose that disagreement; do not claim the computed path is observed source geometry.

**Comparison / debugging conclusion:** Optics runtime reports incidence=40.842553023013416°, refraction=25.48353691375652°, deviation=39.754070946628936°, no TIR. Exact solver output and actual SVG are saved.

**Changes, provenance and possible information loss:** Scene/state/output are actual captures. Exact internal solver-call argument objects were not individually intercepted; no replay or hand-computed replacement is labeled as runtime evidence.

[Complete stage input/output bundle](stage_data/31_solver.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: engine\optics\prismEngine.js](contracts/engine/optics/prismEngine.js)

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
      "landmarks": {
        "count": 66,
        "first_8_records": [
          {
            "label": "scene.geometry.vertices[0]",
            "source": {
              "x": 621.3,
              "y": 80.9
            },
            "view": {
              "x": 495.65,
              "y": 40.45
            },
            "overlay": {
              "x": 310.65,
              "y": 40.45
            },
            "inverse": {
              "x": 621.3,
              "y": 80.9
            },
            "browser": {
              "x": 529.65,
              "y": 267.45
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.vertices[1]",
            "source": {
              "x": 229.2,
              "y": 757
            },
            "view": {
              "x": 299.6,
              "y": 378.5
            },
            "overlay": {
              "x": 114.6,
              "y": 378.5
            },
            "inverse": {
              "x": 229.20000000000005,
              "y": 757
            },
            "browser": {
              "x": 333.6,
              "y": 605.5
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.vertices[2]",
            "source": {
              "x": 1003.9,
              "y": 757
            },
            "view": {
              "x": 686.95,
              "y": 378.5
            },
            "overlay": {
              "x": 501.95,
              "y": 378.5
            },
            "inverse": {
              "x": 1003.9000000000001,
              "y": 757
            },
            "browser": {
              "x": 720.95,
              "y": 605.5
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.prismVertices[0]",
            "source": {
              "x": 621.3,
              "y": 80.9
            },
            "view": {
              "x": 495.65,
              "y": 40.45
            },
            "overlay": {
              "x": 310.65,
              "y": 40.45
            },
            "inverse": {
              "x": 621.3,
              "y": 80.9
            },
            "browser": {
              "x": 529.65,
              "y": 267.45
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.prismVertices[1]",
            "source": {
              "x": 229.2,
              "y": 757
            },
            "view": {
              "x": 299.6,
              "y": 378.5
            },
            "overlay": {
              "x": 114.6,
              "y": 378.5
            },
            "inverse": {
              "x": 229.20000000000005,
              "y": 757
            },
            "browser": {
              "x": 333.6,
              "y": 605.5
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.prismVertices[2]",
            "source": {
              "x": 1003.9,
              "y": 757
            },
            "view": {
              "x": 686.95,
              "y": 378.5
            },
            "overlay": {
              "x": 501.95,
              "y": 378.5
            },
            "inverse": {
              "x": 1003.9000000000001,
              "y": 757
            },
            "browser": {
              "x": 720.95,
              "y": 605.5
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.ray_origin",
            "source": {
              "x": 47,
              "y": 456
            },
            "view": {
              "x": 208.5,
              "y": 228
            },
            "overlay": {
              "x": 23.5,
              "y": 228
            },
            "inverse": {
              "x": 47,
              "y": 456
            },
            "browser": {
              "x": 242.5,
              "y": 455
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "label": "scene.geometry.rayOrigin",
            "source": {
              "x": 47,
              "y": 456
            },
            "view": {
              "x": 208.5,
              "y": 228
            },
            "overlay": {
              "x": 23.5,
              "y": 228
            },
            "inverse": {
              "x": 47,
              "y": 456
            },
            "browser": {
              "x": 242.5,
              "y": 455
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
          "src": "http://127.0.0.1:5173/uploads/diagram_2a50897a.jpg",
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
          "tag": "svg",
          "id": "",
          "className": "optics-overlay-svg",
          "src": null,
          "viewBox": "0 0 1280 960",
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
            "width",
            "height",
            "css"
          ]
        },
        {
          "tag": "IMG",
          "id": "diagram-image",
          "className": "diagram-image",
          "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207801526",
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
          "src": "blob:http://127.0.0.1:5173/782199ea-9e13-4271-86f0-8964fb495844",
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

**What correct handling of THIS diagram requires:** 60° is printed apex-angle evidence. Vertices and rays require source measurement. No numerical refractive index is printed. An assumed index must not be described as measured from this diagram.

**Comparison / debugging conclusion:** Actual sourceToView/sourceToOverlay and inverse results preserve supplied points. This does not validate the input coordinates against the source.

**Changes, provenance and possible information loss:** sourceToView includes viewport letterboxing; sourceToOverlay omits it because the overlay is already image-aligned. Browser coordinates add the measured image origin. Do not add letterboxing twice.

[Complete stage input/output bundle](stage_data/32_mapper.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

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
      "subtype": "prism",
      "time": 0,
      "state": {
        "domain": "optics",
        "subtype": "prism",
        "type": "prism",
        "running": false,
        "incidenceAngle_deg": 40.842553023013416,
        "refractedAngle_deg": 25.48353691375652,
        "deviationAngle_deg": 39.754070946628936,
        "refractiveIndex": 1.52,
        "criticalAngle_deg": 41.139510414899156,
        "tir": false,
        "rayCount": 3,
        "solution": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays"
          ]
        }
      },
      "geometry": {
        "hitPrism": true,
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757
          },
          {
            "x": 1003.9,
            "y": 757
          }
        ],
        "tir": false,
        "hit1": {
          "x": 447.8163870862532,
          "y": 380.0386653684882
        },
        "hit2": {
          "x": 807.0350434576367,
          "y": 409.11605562391077
        },
        "N1": {
          "x": -0.8650522896672732,
          "y": -0.5016817079996121
        },
        "N2": {
          "x": 0.870310991441359,
          "y": -0.49250256666981806
        },
        "I0": {
          "x": 0.9825114512376967,
          "y": -0.1862021701989406
        },
        "I_internal": {
          "x": 0.9967398674939832,
          "y": 0.0806823186830715
        },
        "segments": [
          {
            "type": "incident",
            "start": {
              "x": 47,
              "y": 456
            },
            "end": {
              "x": 447.8163870862532,
              "y": 380.0386653684882
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "type": "internal",
            "start": {
              "x": 447.8163870862532,
              "y": 380.0386653684882
            },
            "end": {
              "x": 807.0350434576367,
              "y": 409.11605562391077
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "type": "emergent",
            "start": {
              "x": 807.0350434576367,
              "y": 409.11605562391077
            },
            "end": {
              "x": 1280,
              "y": 671.531350909933
            },
            "_nested_fields_in_complete_snapshot": []
          }
        ],
        "normals": [
          {
            "p1": {
              "x": 417.53955694789863,
              "y": 362.47980558850173
            },
            "p2": {
              "x": 478.09321722460777,
              "y": 397.59752514847463
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "p1": {
              "x": 837.4959281580842,
              "y": 391.87846579046715
            },
            "p2": {
              "x": 776.5741587571891,
              "y": 426.3536454573544
            },
            "_nested_fields_in_complete_snapshot": []
          }
        ],
        "angles": {
          "i1Deg": 40.842553023013416,
          "r1Deg": 25.48353691375652,
          "deviationDeg": 39.754070946628936,
          "criticalAngleDeg": 41.139510414899156
        },
        "_other_fields_in_complete_snapshot": [
          "rays",
          "opticalAxis",
          "landmarks",
          "lens",
          "mirror",
          "object",
          "image",
          "prismPolygon",
          "prism",
          "handles"
        ]
      },
      "telemetry": {
        "hitPrism": true,
        "prismVertices": [
          {
            "x": 621.3,
            "y": 80.9
          },
          {
            "x": 229.2,
            "y": 757
          },
          {
            "x": 1003.9,
            "y": 757
          }
        ],
        "tir": false,
        "hit1": {
          "x": 447.8163870862532,
          "y": 380.0386653684882
        },
        "hit2": {
          "x": 807.0350434576367,
          "y": 409.11605562391077
        },
        "N1": {
          "x": -0.8650522896672732,
          "y": -0.5016817079996121
        },
        "N2": {
          "x": 0.870310991441359,
          "y": -0.49250256666981806
        },
        "I0": {
          "x": 0.9825114512376967,
          "y": -0.1862021701989406
        },
        "I_internal": {
          "x": 0.9967398674939832,
          "y": 0.0806823186830715
        },
        "segments": [
          {
            "type": "incident",
            "start": {
              "x": 47,
              "y": 456
            },
            "end": {
              "x": 447.8163870862532,
              "y": 380.0386653684882
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "type": "internal",
            "start": {
              "x": 447.8163870862532,
              "y": 380.0386653684882
            },
            "end": {
              "x": 807.0350434576367,
              "y": 409.11605562391077
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "type": "emergent",
            "start": {
              "x": 807.0350434576367,
              "y": 409.11605562391077
            },
            "end": {
              "x": 1280,
              "y": 671.531350909933
            },
            "_nested_fields_in_complete_snapshot": []
          }
        ],
        "normals": [
          {
            "p1": {
              "x": 417.53955694789863,
              "y": 362.47980558850173
            },
            "p2": {
              "x": 478.09321722460777,
              "y": 397.59752514847463
            },
            "_nested_fields_in_complete_snapshot": []
          },
          {
            "p1": {
              "x": 837.4959281580842,
              "y": 391.87846579046715
            },
            "p2": {
              "x": 776.5741587571891,
              "y": 426.3536454573544
            },
            "_nested_fields_in_complete_snapshot": []
          }
        ],
        "angles": {
          "i1Deg": 40.842553023013416,
          "r1Deg": 25.48353691375652,
          "deviationDeg": 39.754070946628936,
          "criticalAngleDeg": 41.139510414899156
        },
        "_other_fields_in_complete_snapshot": [
          "rays",
          "incidenceAngle_deg",
          "refractedAngle_deg",
          "deviationAngle_deg",
          "refractiveIndex",
          "criticalAngle_deg"
        ]
      },
      "events": [],
      "editableParameters": {
        "refractiveIndex": {
          "value": 1.52,
          "unit": "",
          "provenance": "auto_policy",
          "editable": true,
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
      "captured_svg": [
        {
          "original": "<svg class=\"optics-overlay-svg\" viewBox=\"0 0 1280 960\" width=\"640\" height=\"480\" style=\"position: absolute; overflow: visible; pointer-events: none; user-select: none; left: 0px; top: 0px; width: 100%; height: 100%;\"><g class=\"layer-axis\"></g><g class=\"layer-landmarks\"></g><g class=\"layer-shapes\"><polygon points=\"621.3,80.9 229.2,757 1003.9,757\" fill=\"rgba(56, 189, 248, 0.16)\" stroke=\"#38bdf8\" stroke-width=\"2.5\" stroke-linejoin=\"round\"></polygon><line x1=\"417.53955694789863\" y1=\"362.47980558850173\" x2=\"478.09321722460777\" y2=\"397.59752514847463\" stroke=\"rgba(148, 163, 184, 0.65)\" stroke-width=\"1.5\" stroke-dasharray=\"4 4\"></line><line x1=\"837.4959281580842\" y1=\"391.87846579046715\" x2=\"776.5741587571891\" y2=\"426.3536454573544\" stroke=\"rgba(148, 163, 184, 0.65)\" stroke-width=\"1.5\" stroke-dasharray=\"4 4\"></line></g><g class=\"layer-rays\"><line x1=\"47\" y1=\"456\" x2=\"447.8163870862532\" y2=\"380.0386653684882\" stroke=\"#f59e0b\" stroke-width=\"3\" stroke-linecap=\"round\"></line><line x1=\"447.8163870862532\" y1=\"380.0386653684882\" x2=\"807.0350434576367\" y2=\"409.11605562391077\" stroke=\"#38bdf8\" stroke-width=\"3\" stroke-linecap=\"round\"></line><line x1=\"807.0350434576367\" y1=\"409.11605562391077\" x2=\"1280\" y2=\"671.531350909933\" stroke=\"#34d399\" stroke-width=\"3\" stroke-linecap=\"round\"></line></g><g class=\"layer-image\"></g><g class=\"layer-object\"></g><g class=\"layer-handles\" style=\"pointer-events: auto;\"></g></svg>",
          "rendered": "<svg class=\"optics-overlay-svg\" viewBox=\"0 0 1280 960\" width=\"640\" height=\"480\" style=\"position: absolute; overflow: visible; pointer-events: none; user-select: none; left: 0px; top: 0px; width: 640px; height: 480px; fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: block;\" xmlns=\"http://www.w3.org/2000/svg\"><g class=\"layer-axis\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><g class=\"layer-landmarks\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><g class=\"layer-shapes\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><polygon points=\"621.3,80.9 229.2,757 1003.9,757\" fill=\"rgba(56, 189, 248, 0.16)\" stroke=\"#38bdf8\" stroke-width=\"2.5\" stroke-linejoin=\"round\" style=\"fill: rgba(56, 189, 248, 0.16); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 2.5px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"417.53955694789863\" y1=\"362.47980558850173\" x2=\"478.09321722460777\" y2=\"397.59752514847463\" stroke=\"rgba(148, 163, 184, 0.65)\" stroke-width=\"1.5\" stroke-dasharray=\"4 4\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgba(148, 163, 184, 0.65); stroke-width: 1.5px; stroke-opacity: 1; stroke-dasharray: 4px, 4px; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"837.4959281580842\" y1=\"391.87846579046715\" x2=\"776.5741587571891\" y2=\"426.3536454573544\" stroke=\"rgba(148, 163, 184, 0.65)\" stroke-width=\"1.5\" stroke-dasharray=\"4 4\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgba(148, 163, 184, 0.65); stroke-width: 1.5px; stroke-opacity: 1; stroke-dasharray: 4px, 4px; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></g><g class=\"layer-rays\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"><line x1=\"47\" y1=\"456\" x2=\"447.8163870862532\" y2=\"380.0386653684882\" stroke=\"#f59e0b\" stroke-width=\"3\" stroke-linecap=\"round\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(245, 158, 11); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: round; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"447.8163870862532\" y1=\"380.0386653684882\" x2=\"807.0350434576367\" y2=\"409.11605562391077\" stroke=\"#38bdf8\" stroke-width=\"3\" stroke-linecap=\"round\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(56, 189, 248); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: round; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><line x1=\"807.0350434576367\" y1=\"409.11605562391077\" x2=\"1280\" y2=\"671.531350909933\" stroke=\"#34d399\" stroke-width=\"3\" stroke-linecap=\"round\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: rgb(52, 211, 153); stroke-width: 3px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: round; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></g><g class=\"layer-image\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><g class=\"layer-object\" style=\"fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/><g class=\"layer-handles\" style=\"pointer-events: auto; fill: rgb(0, 0, 0); fill-opacity: 1; stroke: none; stroke-width: 1px; stroke-opacity: 1; stroke-dasharray: none; stroke-linecap: butt; opacity: 1; font-family: Inter, system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 400; text-anchor: start; visibility: visible; display: inline;\"/></svg>",
          "viewBox": "0 0 1280 960"
        }
      ],
      "browser_state": {
        "domain": "optics",
        "subtype": "prism",
        "type": "prism",
        "running": false,
        "incidenceAngle_deg": 40.842553023013416,
        "refractedAngle_deg": 25.48353691375652,
        "deviationAngle_deg": 39.754070946628936,
        "refractiveIndex": 1.52,
        "criticalAngle_deg": 41.139510414899156,
        "tir": false,
        "rayCount": 3,
        "solution": {
          "hitPrism": true,
          "tir": false,
          "hit1": {
            "x": 447.8163870862532,
            "y": 380.0386653684882
          },
          "hit2": {
            "x": 807.0350434576367,
            "y": 409.11605562391077
          },
          "N1": {
            "x": -0.8650522896672732,
            "y": -0.5016817079996121
          },
          "N2": {
            "x": 0.870310991441359,
            "y": -0.49250256666981806
          },
          "I0": {
            "x": 0.9825114512376967,
            "y": -0.1862021701989406
          },
          "I_internal": {
            "x": 0.9967398674939832,
            "y": 0.0806823186830715
          },
          "_nested_fields_in_complete_snapshot": [
            "prismVertices",
            "segments",
            "normals",
            "angles",
            "rays"
          ]
        }
      }
    }
  ],
  "in_place_outputs": []
}
```

**What it should provide — implemented contract:** The rendered source landmarks should coincide with the printed diagram at t=0. This requires correct upstream geometry as well as correct transforms.

**What correct handling of THIS diagram requires:** Preserve the triangle sides/base and distinguish incident/internal/emergent rays from body edges and normal lines. Use observed base evidence rather than averaging unrelated side-segment extents.

**Comparison / debugging conclusion:** Optics runtime reports incidence=40.842553023013416°, refraction=25.48353691375652°, deviation=39.754070946628936°, no TIR. Exact solver output and actual SVG are saved.

**Changes, provenance and possible information loss:** Overlay image is captured from the actual canvas/SVG and projected back using measured DOM-to-source ratios. No objects were manually repositioned.

[Complete stage input/output bundle](stage_data/33_render.json)

- [Actual coordinate/landmark audit](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/coordinate_audit.json)

- [Renderer snapshot](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/runtime_t0_capture.json)

- [Code: apps\web\src\components\InteractiveFigure.js](contracts/apps/web/src/components/InteractiveFigure.js)

![runtime_t0_overlay.png](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/14_renderer/runtime_t0_overlay.png)

## 34. Activation, motion and reset

**Execution:** EXECUTED. **Verdict:** ACTUAL STATE CAPTURED.

**Upstream → downstream:** Actual renderer at t=0 over the original → this component → Final observed browser state.

**What it receives — actual input (selected recorded fields):**

```json
[
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "SimulationOrchestrator.startSimulation",
    "phase": "input",
    "wallTime": 34335.90000000596,
    "data": []
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 34336.5,
    "data": []
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 114744.5,
    "data": []
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.reset",
    "phase": "input",
    "wallTime": 114749.09999999404,
    "data": []
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.reset",
    "phase": "input",
    "wallTime": 196816.5,
    "data": []
  },
  {
    "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
    "component": "PhysicsRuntime.start",
    "phase": "input",
    "wallTime": 197262.70000001788,
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
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "SimulationOrchestrator.startSimulation",
      "phase": "output",
      "wallTime": 34336.20000001788,
      "data": {
        "domain": "optics",
        "subtype": "prism",
        "source": {
          "type": "book_figure",
          "source_asset_id": "2a50897a2e704e7aa51642dab568571b",
          "figure_id": "figure_001",
          "width": 1280,
          "height": 960,
          "image_width_px": 1280,
          "image_height_px": 960,
          "image": "/uploads/diagram_2a50897a.jpg"
        },
        "geometry": {
          "width": 1280,
          "height": 960,
          "coordinate_space": "source_px",
          "ray_origin": {
            "x": 47,
            "y": 456
          },
          "rayOrigin": {
            "x": 47,
            "y": 456
          },
          "ray_direction": {
            "x": 0.9825,
            "y": -0.1862
          },
          "rayDirection": {
            "x": 0.9825,
            "y": -0.1862
          },
          "apex_angle_deg": 60,
          "_nested_fields_in_complete_snapshot": [
            "vertices",
            "prismVertices"
          ]
        },
        "parameters": {
          "_nested_fields_in_complete_snapshot": [
            "refractiveIndex",
            "apexAngle"
          ]
        },
        "assumptions": [
          {
            "parameter": "n",
            "policyId": "policy_crown_glass_refractive_index",
            "policyVersion": "1.0",
            "value": 1.52,
            "unit": null,
            "reason": "Refractive index of standard optical crown glass (n = 1.52).",
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
          "elements",
          "visual"
        ]
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 34336.59999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 114744.70000001788,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.reset",
      "phase": "output",
      "wallTime": 114749.80000001192,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.reset",
      "phase": "output",
      "wallTime": 196818.59999999404,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
      "component": "PhysicsRuntime.start",
      "phase": "output",
      "wallTime": 197262.70000001788,
      "data": {
        "captureError": "SyntaxError: \"undefined\" is not valid JSON"
      }
    },
    {
      "after_play": {
        "traceId": "TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017",
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
            "src": "http://127.0.0.1:5173/uploads/diagram_2a50897a.jpg",
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
            "tag": "svg",
            "id": "",
            "className": "optics-overlay-svg",
            "src": null,
            "viewBox": "0 0 1280 960",
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
              "width",
              "height",
              "css"
            ]
          },
          {
            "tag": "IMG",
            "id": "diagram-image",
            "className": "diagram-image",
            "src": "http://127.0.0.1:5173/scenes/kinematics/with_spring.png?t=1792207801526",
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
            "src": "blob:http://127.0.0.1:5173/782199ea-9e13-4271-86f0-8964fb495844",
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

**What correct handling of THIS diagram requires:** At t=0 the prism polygon and ray segments should be compared with the printed paths. If a physical model with assumed n disagrees with the schematic, expose that disagreement; do not claim the computed path is observed source geometry.

**Comparison / debugging conclusion:** Automatic activation is observed in this checkout. Later frame time is whatever the runtime snapshot records, not an invented exact timestamp.

**Changes, provenance and possible information loss:** The executed main.js path automatically starts after a successful load. Later frames are saved at their actual times. Optics results are static ray solutions rather than pendulum-like time evolution.

[Complete stage input/output bundle](stage_data/34_motion.json)

- [Original frontend events (includes startup events; this stage bundle filters them)](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/events.json)

- [Actual later browser frame](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/15_browser/runtime_after_play.png)

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

- **ingest_diagram** (1 calls): [1](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00001_ingest_diagram/STAGE.html)

- **_get_ingestion_pipeline** (1 calls): [2](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00002__get_ingestion_pipeline/STAGE.html)

- **UploadService.ingest** (1 calls): [3](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00003_UploadService.ingest/STAGE.html)

- **compute_sha256** (1 calls): [4](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00004_compute_sha256/STAGE.html)

- **UploadService.get_public_url** (1 calls): [5](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00005_UploadService.get_public_url/STAGE.html)

- **PageIRBuilder.build** (1 calls): [6](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00006_PageIRBuilder.build/STAGE.html)

- **BookUnderstandingPipeline.analyze** (1 calls): [7](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00007_BookUnderstandingPipeline.analyze/STAGE.html)

- **BookUnderstandingPipeline._get_analyzer** (1 calls): [8](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00008_BookUnderstandingPipeline._get_analyzer/STAGE.html)

- **PhysicsVisionAnalyzer.analyze** (1 calls): [9](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00009_PhysicsVisionAnalyzer.analyze/STAGE.html)

- **GeminiVisionProvider.analyze_diagram** (1 calls): [10](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00010_GeminiVisionProvider.analyze_diagram/STAGE.html)

- **GeminiVisionProvider._get_client** (1 calls): [11](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00011_GeminiVisionProvider._get_client/STAGE.html)

- **Models.generate_content** (1 calls): [12](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00012_Models.generate_content/STAGE.html)

- **Models._generate_content** (1 calls): [13](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00013_Models._generate_content/STAGE.html)

- **_discard_dangling_relationships** (1 calls): [14](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00014__discard_dangling_relationships/STAGE.html)

- **validate_semantic_payload** (1 calls): [15](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00015_validate_semantic_payload/STAGE.html)

- **SemanticConfidence.from_dict** (1 calls): [16](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00016_SemanticConfidence.from_dict/STAGE.html)

- **_validate_confidence** (19 calls): [17](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00017__validate_confidence/STAGE.html), [18](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00018__validate_confidence/STAGE.html), [19](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00019__validate_confidence/STAGE.html), [20](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00020__validate_confidence/STAGE.html), [22](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00022__validate_confidence/STAGE.html), [24](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00024__validate_confidence/STAGE.html), [26](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00026__validate_confidence/STAGE.html), [28](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00028__validate_confidence/STAGE.html), [30](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00030__validate_confidence/STAGE.html), [32](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00032__validate_confidence/STAGE.html), [34](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00034__validate_confidence/STAGE.html), [36](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00036__validate_confidence/STAGE.html), [38](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00038__validate_confidence/STAGE.html), [40](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00040__validate_confidence/STAGE.html), [42](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00042__validate_confidence/STAGE.html), [44](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00044__validate_confidence/STAGE.html), [46](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00046__validate_confidence/STAGE.html), [48](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00048__validate_confidence/STAGE.html), [50](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00050__validate_confidence/STAGE.html)

- **SemanticEntity.from_dict** (6 calls): [21](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00021_SemanticEntity.from_dict/STAGE.html), [23](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00023_SemanticEntity.from_dict/STAGE.html), [25](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00025_SemanticEntity.from_dict/STAGE.html), [27](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00027_SemanticEntity.from_dict/STAGE.html), [29](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00029_SemanticEntity.from_dict/STAGE.html), [31](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00031_SemanticEntity.from_dict/STAGE.html)

- **SemanticRelationship.from_dict** (2 calls): [33](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00033_SemanticRelationship.from_dict/STAGE.html), [35](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00035_SemanticRelationship.from_dict/STAGE.html)

- **SemanticVisibleLabel.from_dict** (7 calls): [37](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00037_SemanticVisibleLabel.from_dict/STAGE.html), [39](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00039_SemanticVisibleLabel.from_dict/STAGE.html), [41](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00041_SemanticVisibleLabel.from_dict/STAGE.html), [43](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00043_SemanticVisibleLabel.from_dict/STAGE.html), [45](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00045_SemanticVisibleLabel.from_dict/STAGE.html), [47](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00047_SemanticVisibleLabel.from_dict/STAGE.html), [49](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00049_SemanticVisibleLabel.from_dict/STAGE.html)

- **PhysicsVisionAnalyzer._apply_thresholds** (1 calls): [51](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00051_PhysicsVisionAnalyzer._apply_thresholds/STAGE.html)

- **BookUnderstandingPipeline._build_book_ir_from_result** (1 calls): [52](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00052_BookUnderstandingPipeline._build_book_ir_from_result/STAGE.html)

- **SemanticAnalysisResult.is_supported** (1 calls): [53](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00053_SemanticAnalysisResult.is_supported/STAGE.html)

- **EvidenceExtractionPipeline.extract_and_fuse** (1 calls): [54](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00054_EvidenceExtractionPipeline.extract_and_fuse/STAGE.html)

- **GrounderRegistry.find_grounder** (1 calls): [55](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00055_GrounderRegistry.find_grounder/STAGE.html)

- **PendulumGrounder.supports** (1 calls): [56](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00056_PendulumGrounder.supports/STAGE.html)

- **ProjectileGrounder.supports** (1 calls): [57](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00057_ProjectileGrounder.supports/STAGE.html)

- **ThinLensGrounder.supports** (1 calls): [58](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00058_ThinLensGrounder.supports/STAGE.html)

- **SphericalMirrorGrounder.supports** (1 calls): [59](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00059_SphericalMirrorGrounder.supports/STAGE.html)

- **InterfaceRefractionGrounder.supports** (1 calls): [60](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00060_InterfaceRefractionGrounder.supports/STAGE.html)

- **PrismGrounder.supports** (1 calls): [61](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00061_PrismGrounder.supports/STAGE.html)

- **load_and_validate_source_image** (1 calls): [62](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00062_load_and_validate_source_image/STAGE.html)

- **MultiOCRRouter.available** (1 calls): [63](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00063_MultiOCRRouter.available/STAGE.html)

- **RapidOCRProvider.available** (2 calls): [64](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00064_RapidOCRProvider.available/STAGE.html), [67](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00067_RapidOCRProvider.available/STAGE.html)

- **MultiOCRRouter.extract** (1 calls): [65](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00065_MultiOCRRouter.extract/STAGE.html)

- **RapidOCRProvider.extract** (1 calls): [66](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00066_RapidOCRProvider.extract/STAGE.html)

- **ImageTransform.identity** (2 calls): [68](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00068_ImageTransform.identity/STAGE.html), [141](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00141_ImageTransform.identity/STAGE.html)

- **RapidOCRProvider._get_engine** (1 calls): [69](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00069_RapidOCRProvider._get_engine/STAGE.html)

- **ImageTransform.to_source_point** (80 calls): [70](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00070_ImageTransform.to_source_point/STAGE.html), [71](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00071_ImageTransform.to_source_point/STAGE.html), [72](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00072_ImageTransform.to_source_point/STAGE.html), [73](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00073_ImageTransform.to_source_point/STAGE.html), [76](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00076_ImageTransform.to_source_point/STAGE.html), [77](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00077_ImageTransform.to_source_point/STAGE.html), [78](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00078_ImageTransform.to_source_point/STAGE.html), [79](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00079_ImageTransform.to_source_point/STAGE.html), [82](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00082_ImageTransform.to_source_point/STAGE.html), [83](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00083_ImageTransform.to_source_point/STAGE.html), [84](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00084_ImageTransform.to_source_point/STAGE.html), [85](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00085_ImageTransform.to_source_point/STAGE.html), [88](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00088_ImageTransform.to_source_point/STAGE.html), [89](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00089_ImageTransform.to_source_point/STAGE.html), [90](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00090_ImageTransform.to_source_point/STAGE.html), [91](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00091_ImageTransform.to_source_point/STAGE.html), [94](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00094_ImageTransform.to_source_point/STAGE.html), [95](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00095_ImageTransform.to_source_point/STAGE.html), [96](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00096_ImageTransform.to_source_point/STAGE.html), [97](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00097_ImageTransform.to_source_point/STAGE.html), [100](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00100_ImageTransform.to_source_point/STAGE.html), [101](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00101_ImageTransform.to_source_point/STAGE.html), [102](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00102_ImageTransform.to_source_point/STAGE.html), [103](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00103_ImageTransform.to_source_point/STAGE.html), [106](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00106_ImageTransform.to_source_point/STAGE.html), [107](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00107_ImageTransform.to_source_point/STAGE.html), [108](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00108_ImageTransform.to_source_point/STAGE.html), [109](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00109_ImageTransform.to_source_point/STAGE.html), [112](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00112_ImageTransform.to_source_point/STAGE.html), [113](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00113_ImageTransform.to_source_point/STAGE.html), [114](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00114_ImageTransform.to_source_point/STAGE.html), [115](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00115_ImageTransform.to_source_point/STAGE.html), [118](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00118_ImageTransform.to_source_point/STAGE.html), [119](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00119_ImageTransform.to_source_point/STAGE.html), [120](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00120_ImageTransform.to_source_point/STAGE.html), [121](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00121_ImageTransform.to_source_point/STAGE.html), [124](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00124_ImageTransform.to_source_point/STAGE.html), [125](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00125_ImageTransform.to_source_point/STAGE.html), [126](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00126_ImageTransform.to_source_point/STAGE.html), [127](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00127_ImageTransform.to_source_point/STAGE.html), [130](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00130_ImageTransform.to_source_point/STAGE.html), [131](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00131_ImageTransform.to_source_point/STAGE.html), [132](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00132_ImageTransform.to_source_point/STAGE.html), [133](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00133_ImageTransform.to_source_point/STAGE.html), [143](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00143_ImageTransform.to_source_point/STAGE.html), [144](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00144_ImageTransform.to_source_point/STAGE.html), [145](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00145_ImageTransform.to_source_point/STAGE.html), [146](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00146_ImageTransform.to_source_point/STAGE.html), [150](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00150_ImageTransform.to_source_point/STAGE.html), [151](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00151_ImageTransform.to_source_point/STAGE.html), [152](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00152_ImageTransform.to_source_point/STAGE.html), [153](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00153_ImageTransform.to_source_point/STAGE.html), [157](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00157_ImageTransform.to_source_point/STAGE.html), [158](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00158_ImageTransform.to_source_point/STAGE.html), [159](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00159_ImageTransform.to_source_point/STAGE.html), [160](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00160_ImageTransform.to_source_point/STAGE.html), [164](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00164_ImageTransform.to_source_point/STAGE.html), [165](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00165_ImageTransform.to_source_point/STAGE.html), [166](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00166_ImageTransform.to_source_point/STAGE.html), [167](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00167_ImageTransform.to_source_point/STAGE.html), [171](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00171_ImageTransform.to_source_point/STAGE.html), [172](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00172_ImageTransform.to_source_point/STAGE.html), [173](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00173_ImageTransform.to_source_point/STAGE.html), [174](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00174_ImageTransform.to_source_point/STAGE.html), [178](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00178_ImageTransform.to_source_point/STAGE.html), [179](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00179_ImageTransform.to_source_point/STAGE.html), [180](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00180_ImageTransform.to_source_point/STAGE.html), [181](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00181_ImageTransform.to_source_point/STAGE.html), [185](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00185_ImageTransform.to_source_point/STAGE.html), [186](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00186_ImageTransform.to_source_point/STAGE.html), [187](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00187_ImageTransform.to_source_point/STAGE.html), [188](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00188_ImageTransform.to_source_point/STAGE.html), [192](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00192_ImageTransform.to_source_point/STAGE.html), [193](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00193_ImageTransform.to_source_point/STAGE.html), [194](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00194_ImageTransform.to_source_point/STAGE.html), [195](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00195_ImageTransform.to_source_point/STAGE.html), [199](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00199_ImageTransform.to_source_point/STAGE.html), [200](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00200_ImageTransform.to_source_point/STAGE.html), [201](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00201_ImageTransform.to_source_point/STAGE.html), [202](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00202_ImageTransform.to_source_point/STAGE.html)

- **SourcePolygon.bbox** (22 calls): [74](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00074_SourcePolygon.bbox/STAGE.html), [80](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00080_SourcePolygon.bbox/STAGE.html), [86](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00086_SourcePolygon.bbox/STAGE.html), [92](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00092_SourcePolygon.bbox/STAGE.html), [98](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00098_SourcePolygon.bbox/STAGE.html), [104](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00104_SourcePolygon.bbox/STAGE.html), [110](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00110_SourcePolygon.bbox/STAGE.html), [116](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00116_SourcePolygon.bbox/STAGE.html), [122](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00122_SourcePolygon.bbox/STAGE.html), [128](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00128_SourcePolygon.bbox/STAGE.html), [134](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00134_SourcePolygon.bbox/STAGE.html), [147](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00147_SourcePolygon.bbox/STAGE.html), [154](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00154_SourcePolygon.bbox/STAGE.html), [161](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00161_SourcePolygon.bbox/STAGE.html), [168](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00168_SourcePolygon.bbox/STAGE.html), [175](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00175_SourcePolygon.bbox/STAGE.html), [182](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00182_SourcePolygon.bbox/STAGE.html), [189](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00189_SourcePolygon.bbox/STAGE.html), [196](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00196_SourcePolygon.bbox/STAGE.html), [203](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00203_SourcePolygon.bbox/STAGE.html), [323](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00323_SourcePolygon.bbox/STAGE.html), [324](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00324_SourcePolygon.bbox/STAGE.html)

- **RapidOCRProvider.name** (12 calls): [75](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00075_RapidOCRProvider.name/STAGE.html), [81](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00081_RapidOCRProvider.name/STAGE.html), [87](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00087_RapidOCRProvider.name/STAGE.html), [93](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00093_RapidOCRProvider.name/STAGE.html), [99](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00099_RapidOCRProvider.name/STAGE.html), [105](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00105_RapidOCRProvider.name/STAGE.html), [111](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00111_RapidOCRProvider.name/STAGE.html), [117](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00117_RapidOCRProvider.name/STAGE.html), [123](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00123_RapidOCRProvider.name/STAGE.html), [129](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00129_RapidOCRProvider.name/STAGE.html), [135](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00135_RapidOCRProvider.name/STAGE.html), [136](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00136_RapidOCRProvider.name/STAGE.html)

- **RapidOCRProvider.model_version** (1 calls): [137](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00137_RapidOCRProvider.model_version/STAGE.html)

- **EasyOCRBanglaProvider.available** (4 calls): [138](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00138_EasyOCRBanglaProvider.available/STAGE.html), [140](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00140_EasyOCRBanglaProvider.available/STAGE.html), [250](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00250_EasyOCRBanglaProvider.available/STAGE.html), [252](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00252_EasyOCRBanglaProvider.available/STAGE.html)

- **EasyOCRBanglaProvider.extract** (1 calls): [139](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00139_EasyOCRBanglaProvider.extract/STAGE.html)

- **EasyOCRBanglaProvider._get_reader** (1 calls): [142](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00142_EasyOCRBanglaProvider._get_reader/STAGE.html)

- **is_bengali_text** (17 calls): [148](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00148_is_bengali_text/STAGE.html), [155](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00155_is_bengali_text/STAGE.html), [162](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00162_is_bengali_text/STAGE.html), [169](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00169_is_bengali_text/STAGE.html), [176](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00176_is_bengali_text/STAGE.html), [183](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00183_is_bengali_text/STAGE.html), [190](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00190_is_bengali_text/STAGE.html), [197](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00197_is_bengali_text/STAGE.html), [204](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00204_is_bengali_text/STAGE.html), [207](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00207_is_bengali_text/STAGE.html), [208](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00208_is_bengali_text/STAGE.html), [209](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00209_is_bengali_text/STAGE.html), [210](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00210_is_bengali_text/STAGE.html), [211](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00211_is_bengali_text/STAGE.html), [212](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00212_is_bengali_text/STAGE.html), [213](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00213_is_bengali_text/STAGE.html), [214](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00214_is_bengali_text/STAGE.html)

- **EasyOCRBanglaProvider.name** (10 calls): [149](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00149_EasyOCRBanglaProvider.name/STAGE.html), [156](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00156_EasyOCRBanglaProvider.name/STAGE.html), [163](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00163_EasyOCRBanglaProvider.name/STAGE.html), [170](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00170_EasyOCRBanglaProvider.name/STAGE.html), [177](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00177_EasyOCRBanglaProvider.name/STAGE.html), [184](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00184_EasyOCRBanglaProvider.name/STAGE.html), [191](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00191_EasyOCRBanglaProvider.name/STAGE.html), [198](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00198_EasyOCRBanglaProvider.name/STAGE.html), [205](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00205_EasyOCRBanglaProvider.name/STAGE.html), [206](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00206_EasyOCRBanglaProvider.name/STAGE.html)

- **deduplicate_spatial_tokens** (1 calls): [215](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00215_deduplicate_spatial_tokens/STAGE.html)

- **deduplicate_spatial_tokens.<locals>.<lambda>** (11 calls): [216](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00216_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [217](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00217_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [218](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00218_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [219](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00219_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [220](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00220_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [221](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00221_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [222](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00222_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [223](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00223_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [224](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00224_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [225](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00225_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html), [226](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00226_deduplicate_spatial_tokens._locals_._lambda_/STAGE.html)

- **GreekSymbolVisualOCR.extract_symbols** (1 calls): [227](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00227_GreekSymbolVisualOCR.extract_symbols/STAGE.html)

- **PhysicsSymbolCandidateResolver.enrich_token** (11 calls): [228](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00228_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [230](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00230_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [232](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00232_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [234](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00234_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [236](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00236_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [238](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00238_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [240](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00240_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [242](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00242_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [244](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00244_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [246](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00246_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html), [248](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00248_PhysicsSymbolCandidateResolver.enrich_token/STAGE.html)

- **generate_symbol_alternatives** (11 calls): [229](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00229_generate_symbol_alternatives/STAGE.html), [231](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00231_generate_symbol_alternatives/STAGE.html), [233](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00233_generate_symbol_alternatives/STAGE.html), [235](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00235_generate_symbol_alternatives/STAGE.html), [237](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00237_generate_symbol_alternatives/STAGE.html), [239](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00239_generate_symbol_alternatives/STAGE.html), [241](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00241_generate_symbol_alternatives/STAGE.html), [243](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00243_generate_symbol_alternatives/STAGE.html), [245](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00245_generate_symbol_alternatives/STAGE.html), [247](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00247_generate_symbol_alternatives/STAGE.html), [249](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00249_generate_symbol_alternatives/STAGE.html)

- **MultiOCRRouter.name** (1 calls): [251](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00251_MultiOCRRouter.name/STAGE.html)

- **GreekSymbolVisualOCR.available** (1 calls): [253](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00253_GreekSymbolVisualOCR.available/STAGE.html)

- **UnavailableFormulaRecognitionProvider.available** (1 calls): [254](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00254_UnavailableFormulaRecognitionProvider.available/STAGE.html)

- **PrismCVCandidateExtractor.extract** (1 calls): [255](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00255_PrismCVCandidateExtractor.extract/STAGE.html)

- **preprocess_for_geometry** (1 calls): [256](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00256_preprocess_for_geometry/STAGE.html)

- **preprocess_diagram** (1 calls): [257](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00257_preprocess_diagram/STAGE.html)

- **mask_out_text_regions** (1 calls): [258](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00258_mask_out_text_regions/STAGE.html)

- **math_floor** (22 calls): [259](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00259_math_floor/STAGE.html), [260](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00260_math_floor/STAGE.html), [263](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00263_math_floor/STAGE.html), [264](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00264_math_floor/STAGE.html), [267](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00267_math_floor/STAGE.html), [268](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00268_math_floor/STAGE.html), [271](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00271_math_floor/STAGE.html), [272](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00272_math_floor/STAGE.html), [275](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00275_math_floor/STAGE.html), [276](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00276_math_floor/STAGE.html), [279](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00279_math_floor/STAGE.html), [280](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00280_math_floor/STAGE.html), [283](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00283_math_floor/STAGE.html), [284](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00284_math_floor/STAGE.html), [287](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00287_math_floor/STAGE.html), [288](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00288_math_floor/STAGE.html), [291](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00291_math_floor/STAGE.html), [292](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00292_math_floor/STAGE.html), [295](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00295_math_floor/STAGE.html), [296](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00296_math_floor/STAGE.html), [299](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00299_math_floor/STAGE.html), [300](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00300_math_floor/STAGE.html)

- **math_ceil** (22 calls): [261](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00261_math_ceil/STAGE.html), [262](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00262_math_ceil/STAGE.html), [265](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00265_math_ceil/STAGE.html), [266](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00266_math_ceil/STAGE.html), [269](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00269_math_ceil/STAGE.html), [270](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00270_math_ceil/STAGE.html), [273](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00273_math_ceil/STAGE.html), [274](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00274_math_ceil/STAGE.html), [277](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00277_math_ceil/STAGE.html), [278](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00278_math_ceil/STAGE.html), [281](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00281_math_ceil/STAGE.html), [282](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00282_math_ceil/STAGE.html), [285](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00285_math_ceil/STAGE.html), [286](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00286_math_ceil/STAGE.html), [289](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00289_math_ceil/STAGE.html), [290](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00290_math_ceil/STAGE.html), [293](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00293_math_ceil/STAGE.html), [294](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00294_math_ceil/STAGE.html), [297](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00297_math_ceil/STAGE.html), [298](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00298_math_ceil/STAGE.html), [301](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00301_math_ceil/STAGE.html), [302](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00302_math_ceil/STAGE.html)

- **PrismCVCandidateExtractor.extract.<locals>._filter_dominant** (2 calls): [303](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00303_PrismCVCandidateExtractor.extract._locals_._filter_dominant/STAGE.html), [304](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00304_PrismCVCandidateExtractor.extract._locals_._filter_dominant/STAGE.html)

- **PrismCVCandidateExtractor.extract.<locals>._fit_line** (2 calls): [305](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00305_PrismCVCandidateExtractor.extract._locals_._fit_line/STAGE.html), [306](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00306_PrismCVCandidateExtractor.extract._locals_._fit_line/STAGE.html)

- **PrismCVCandidateExtractor.extract.<locals>._intersect** (3 calls): [307](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00307_PrismCVCandidateExtractor.extract._locals_._intersect/STAGE.html), [308](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00308_PrismCVCandidateExtractor.extract._locals_._intersect/STAGE.html), [309](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00309_PrismCVCandidateExtractor.extract._locals_._intersect/STAGE.html)

- **PrismCVCandidateExtractor.extract.<locals>.<lambda>** (11 calls): [310](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00310_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [311](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00311_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [312](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00312_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [313](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00313_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [314](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00314_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [315](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00315_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [316](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00316_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [317](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00317_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [318](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00318_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [319](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00319_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html), [320](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00320_PrismCVCandidateExtractor.extract._locals_._lambda_/STAGE.html)

- **PrismGrounder.ground** (1 calls): [321](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00321_PrismGrounder.ground/STAGE.html)

- **PrismGrounder.fuse** (1 calls): [322](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00322_PrismGrounder.fuse/STAGE.html)

- **parse_physical_value_candidate** (11 calls): [325](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00325_parse_physical_value_candidate/STAGE.html), [328](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00328_parse_physical_value_candidate/STAGE.html), [330](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00330_parse_physical_value_candidate/STAGE.html), [332](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00332_parse_physical_value_candidate/STAGE.html), [334](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00334_parse_physical_value_candidate/STAGE.html), [340](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00340_parse_physical_value_candidate/STAGE.html), [342](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00342_parse_physical_value_candidate/STAGE.html), [345](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00345_parse_physical_value_candidate/STAGE.html), [348](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00348_parse_physical_value_candidate/STAGE.html), [350](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00350_parse_physical_value_candidate/STAGE.html), [352](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00352_parse_physical_value_candidate/STAGE.html)

- **normalize_ocr_text** (16 calls): [326](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00326_normalize_ocr_text/STAGE.html), [327](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00327_normalize_ocr_text/STAGE.html), [329](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00329_normalize_ocr_text/STAGE.html), [331](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00331_normalize_ocr_text/STAGE.html), [333](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00333_normalize_ocr_text/STAGE.html), [335](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00335_normalize_ocr_text/STAGE.html), [336](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00336_normalize_ocr_text/STAGE.html), [337](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00337_normalize_ocr_text/STAGE.html), [341](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00341_normalize_ocr_text/STAGE.html), [343](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00343_normalize_ocr_text/STAGE.html), [344](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00344_normalize_ocr_text/STAGE.html), [346](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00346_normalize_ocr_text/STAGE.html), [347](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00347_normalize_ocr_text/STAGE.html), [349](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00349_normalize_ocr_text/STAGE.html), [351](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00351_normalize_ocr_text/STAGE.html), [353](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00353_normalize_ocr_text/STAGE.html)

- **ParsedPhysicalValueCandidate.token_id** (2 calls): [338](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00338_ParsedPhysicalValueCandidate.token_id/STAGE.html), [339](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00339_ParsedPhysicalValueCandidate.token_id/STAGE.html)

- **enforce_source_dimensions** (1 calls): [354](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00354_enforce_source_dimensions/STAGE.html)

- **AutoResolutionEngine.resolve** (1 calls): [355](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00355_AutoResolutionEngine.resolve/STAGE.html)

- **RequirementRegistry.get_spec** (11 calls): [356](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00356_RequirementRegistry.get_spec/STAGE.html), [369](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00369_RequirementRegistry.get_spec/STAGE.html), [379](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00379_RequirementRegistry.get_spec/STAGE.html), [389](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00389_RequirementRegistry.get_spec/STAGE.html), [402](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00402_RequirementRegistry.get_spec/STAGE.html), [412](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00412_RequirementRegistry.get_spec/STAGE.html), [424](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00424_RequirementRegistry.get_spec/STAGE.html), [439](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00439_RequirementRegistry.get_spec/STAGE.html), [449](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00449_RequirementRegistry.get_spec/STAGE.html), [485](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00485_RequirementRegistry.get_spec/STAGE.html), [495](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00495_RequirementRegistry.get_spec/STAGE.html)

- **AutoResolutionEngine._normalize_prism_ray** (1 calls): [357](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00357_AutoResolutionEngine._normalize_prism_ray/STAGE.html)

- **_grounded_value** (4 calls): [358](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00358__grounded_value/STAGE.html), [359](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00359__grounded_value/STAGE.html), [360](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00360__grounded_value/STAGE.html), [361](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00361__grounded_value/STAGE.html)

- **_inside_source** (4 calls): [362](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00362__inside_source/STAGE.html), [363](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00363__inside_source/STAGE.html), [364](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00364__inside_source/STAGE.html), [365](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00365__inside_source/STAGE.html)

- **PolicyRegistry.get_policy** (10 calls): [366](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00366_PolicyRegistry.get_policy/STAGE.html), [390](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00390_PolicyRegistry.get_policy/STAGE.html), [413](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00413_PolicyRegistry.get_policy/STAGE.html), [426](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00426_PolicyRegistry.get_policy/STAGE.html), [428](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00428_PolicyRegistry.get_policy/STAGE.html), [430](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00430_PolicyRegistry.get_policy/STAGE.html), [432](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00432_PolicyRegistry.get_policy/STAGE.html), [434](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00434_PolicyRegistry.get_policy/STAGE.html), [450](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00450_PolicyRegistry.get_policy/STAGE.html), [496](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00496_PolicyRegistry.get_policy/STAGE.html)

- **PolicyRegistry.get** (10 calls): [367](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00367_PolicyRegistry.get/STAGE.html), [391](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00391_PolicyRegistry.get/STAGE.html), [414](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00414_PolicyRegistry.get/STAGE.html), [427](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00427_PolicyRegistry.get/STAGE.html), [429](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00429_PolicyRegistry.get/STAGE.html), [431](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00431_PolicyRegistry.get/STAGE.html), [433](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00433_PolicyRegistry.get/STAGE.html), [435](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00435_PolicyRegistry.get/STAGE.html), [451](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00451_PolicyRegistry.get/STAGE.html), [497](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00497_PolicyRegistry.get/STAGE.html)

- **ResolutionEngine.apply_resolution** (1 calls): [368](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00368_ResolutionEngine.apply_resolution/STAGE.html)

- **ModelRequirementSpec.canonicalize_parameter** (1 calls): [370](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00370_ModelRequirementSpec.canonicalize_parameter/STAGE.html)

- **UnitEngine.parse_quantity** (9 calls): [371](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00371_UnitEngine.parse_quantity/STAGE.html), [393](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00393_UnitEngine.parse_quantity/STAGE.html), [397](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00397_UnitEngine.parse_quantity/STAGE.html), [416](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00416_UnitEngine.parse_quantity/STAGE.html), [420](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00420_UnitEngine.parse_quantity/STAGE.html), [453](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00453_UnitEngine.parse_quantity/STAGE.html), [457](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00457_UnitEngine.parse_quantity/STAGE.html), [499](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00499_UnitEngine.parse_quantity/STAGE.html), [503](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00503_UnitEngine.parse_quantity/STAGE.html)

- **UnitEngine.lookup_unit** (14 calls): [372](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00372_UnitEngine.lookup_unit/STAGE.html), [373](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00373_UnitEngine.lookup_unit/STAGE.html), [394](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00394_UnitEngine.lookup_unit/STAGE.html), [395](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00395_UnitEngine.lookup_unit/STAGE.html), [398](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00398_UnitEngine.lookup_unit/STAGE.html), [417](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00417_UnitEngine.lookup_unit/STAGE.html), [418](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00418_UnitEngine.lookup_unit/STAGE.html), [421](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00421_UnitEngine.lookup_unit/STAGE.html), [454](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00454_UnitEngine.lookup_unit/STAGE.html), [455](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00455_UnitEngine.lookup_unit/STAGE.html), [458](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00458_UnitEngine.lookup_unit/STAGE.html), [500](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00500_UnitEngine.lookup_unit/STAGE.html), [501](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00501_UnitEngine.lookup_unit/STAGE.html), [504](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00504_UnitEngine.lookup_unit/STAGE.html)

- **UnitEngine.validate_range** (9 calls): [374](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00374_UnitEngine.validate_range/STAGE.html), [396](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00396_UnitEngine.validate_range/STAGE.html), [399](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00399_UnitEngine.validate_range/STAGE.html), [419](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00419_UnitEngine.validate_range/STAGE.html), [422](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00422_UnitEngine.validate_range/STAGE.html), [456](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00456_UnitEngine.validate_range/STAGE.html), [459](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00459_UnitEngine.validate_range/STAGE.html), [502](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00502_UnitEngine.validate_range/STAGE.html), [505](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00505_UnitEngine.validate_range/STAGE.html)

- **ResolutionDecision.model_dump** (1 calls): [375](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00375_ResolutionDecision.model_dump/STAGE.html)

- **CalibrationEngine.derive_for_subtype** (3 calls): [376](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00376_CalibrationEngine.derive_for_subtype/STAGE.html), [425](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00425_CalibrationEngine.derive_for_subtype/STAGE.html), [436](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00436_CalibrationEngine.derive_for_subtype/STAGE.html)

- **ReadinessEvaluator.evaluate** (4 calls): [377](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00377_ReadinessEvaluator.evaluate/STAGE.html), [400](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00400_ReadinessEvaluator.evaluate/STAGE.html), [437](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00437_ReadinessEvaluator.evaluate/STAGE.html), [483](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00483_ReadinessEvaluator.evaluate/STAGE.html)

- **ResolutionAnalyzer.analyze** (4 calls): [378](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00378_ResolutionAnalyzer.analyze/STAGE.html), [401](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00401_ResolutionAnalyzer.analyze/STAGE.html), [438](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00438_ResolutionAnalyzer.analyze/STAGE.html), [484](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00484_ResolutionAnalyzer.analyze/STAGE.html)

- **ResolutionAnalyzer._check_geometry_requirements** (4 calls): [380](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00380_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [403](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00403_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [440](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00440_ResolutionAnalyzer._check_geometry_requirements/STAGE.html), [486](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00486_ResolutionAnalyzer._check_geometry_requirements/STAGE.html)

- **ResolutionAnalyzer._check_parameter_requirements** (4 calls): [381](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00381_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [404](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00404_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [441](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00441_ResolutionAnalyzer._check_parameter_requirements/STAGE.html), [487](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00487_ResolutionAnalyzer._check_parameter_requirements/STAGE.html)

- **ModelRequirementSpec.required_parameters** (8 calls): [382](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00382_ModelRequirementSpec.required_parameters/STAGE.html), [392](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00392_ModelRequirementSpec.required_parameters/STAGE.html), [405](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00405_ModelRequirementSpec.required_parameters/STAGE.html), [415](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00415_ModelRequirementSpec.required_parameters/STAGE.html), [442](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00442_ModelRequirementSpec.required_parameters/STAGE.html), [452](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00452_ModelRequirementSpec.required_parameters/STAGE.html), [488](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00488_ModelRequirementSpec.required_parameters/STAGE.html), [498](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00498_ModelRequirementSpec.required_parameters/STAGE.html)

- **ResolutionAnalyzer._check_optional_parameters** (4 calls): [383](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00383_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [406](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00406_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [443](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00443_ResolutionAnalyzer._check_optional_parameters/STAGE.html), [489](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00489_ResolutionAnalyzer._check_optional_parameters/STAGE.html)

- **ModelRequirementSpec.optional_parameters** (4 calls): [384](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00384_ModelRequirementSpec.optional_parameters/STAGE.html), [407](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00407_ModelRequirementSpec.optional_parameters/STAGE.html), [444](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00444_ModelRequirementSpec.optional_parameters/STAGE.html), [490](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00490_ModelRequirementSpec.optional_parameters/STAGE.html)

- **PolicyRegistry.get_policies_for_subtype** (4 calls): [385](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00385_PolicyRegistry.get_policies_for_subtype/STAGE.html), [408](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00408_PolicyRegistry.get_policies_for_subtype/STAGE.html), [445](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00445_PolicyRegistry.get_policies_for_subtype/STAGE.html), [491](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00491_PolicyRegistry.get_policies_for_subtype/STAGE.html)

- **PolicyRegistry.list_all** (4 calls): [386](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00386_PolicyRegistry.list_all/STAGE.html), [409](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00409_PolicyRegistry.list_all/STAGE.html), [446](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00446_PolicyRegistry.list_all/STAGE.html), [492](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00492_PolicyRegistry.list_all/STAGE.html)

- **ResolutionPolicy.policy_id** (8 calls): [387](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00387_ResolutionPolicy.policy_id/STAGE.html), [388](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00388_ResolutionPolicy.policy_id/STAGE.html), [410](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00410_ResolutionPolicy.policy_id/STAGE.html), [411](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00411_ResolutionPolicy.policy_id/STAGE.html), [447](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00447_ResolutionPolicy.policy_id/STAGE.html), [448](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00448_ResolutionPolicy.policy_id/STAGE.html), [493](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00493_ResolutionPolicy.policy_id/STAGE.html), [494](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00494_ResolutionPolicy.policy_id/STAGE.html)

- **ResolutionEngine.auto_resolve** (1 calls): [423](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00423_ResolutionEngine.auto_resolve/STAGE.html)

- **PhysicsCompiler.compile** (1 calls): [460](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00460_PhysicsCompiler.compile/STAGE.html)

- **PhysicsCompiler._validate_grounding** (1 calls): [461](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00461_PhysicsCompiler._validate_grounding/STAGE.html)

- **PhysicsCompiler._extract_source_dimensions** (2 calls): [462](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00462_PhysicsCompiler._extract_source_dimensions/STAGE.html), [507](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00507_PhysicsCompiler._extract_source_dimensions/STAGE.html)

- **PhysicsCompiler._extract_raw_val** (16 calls): [463](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00463_PhysicsCompiler._extract_raw_val/STAGE.html), [464](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00464_PhysicsCompiler._extract_raw_val/STAGE.html), [466](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00466_PhysicsCompiler._extract_raw_val/STAGE.html), [467](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00467_PhysicsCompiler._extract_raw_val/STAGE.html), [471](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00471_PhysicsCompiler._extract_raw_val/STAGE.html), [473](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00473_PhysicsCompiler._extract_raw_val/STAGE.html), [479](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00479_PhysicsCompiler._extract_raw_val/STAGE.html), [482](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00482_PhysicsCompiler._extract_raw_val/STAGE.html), [508](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00508_PhysicsCompiler._extract_raw_val/STAGE.html), [509](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00509_PhysicsCompiler._extract_raw_val/STAGE.html), [511](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00511_PhysicsCompiler._extract_raw_val/STAGE.html), [512](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00512_PhysicsCompiler._extract_raw_val/STAGE.html), [516](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00516_PhysicsCompiler._extract_raw_val/STAGE.html), [518](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00518_PhysicsCompiler._extract_raw_val/STAGE.html), [524](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00524_PhysicsCompiler._extract_raw_val/STAGE.html), [527](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00527_PhysicsCompiler._extract_raw_val/STAGE.html)

- **_first_not_none** (14 calls): [465](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00465__first_not_none/STAGE.html), [468](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00468__first_not_none/STAGE.html), [470](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00470__first_not_none/STAGE.html), [472](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00472__first_not_none/STAGE.html), [474](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00474__first_not_none/STAGE.html), [477](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00477__first_not_none/STAGE.html), [480](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00480__first_not_none/STAGE.html), [510](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00510__first_not_none/STAGE.html), [513](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00513__first_not_none/STAGE.html), [515](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00515__first_not_none/STAGE.html), [517](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00517__first_not_none/STAGE.html), [519](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00519__first_not_none/STAGE.html), [522](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00522__first_not_none/STAGE.html), [525](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00525__first_not_none/STAGE.html)

- **PhysicsCompiler._validate_parameters** (1 calls): [469](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00469_PhysicsCompiler._validate_parameters/STAGE.html)

- **_extract_val_and_unit** (2 calls): [475](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00475__extract_val_and_unit/STAGE.html), [520](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00520__extract_val_and_unit/STAGE.html)

- **_validate_and_convert_unit** (2 calls): [476](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00476__validate_and_convert_unit/STAGE.html), [521](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00521__validate_and_convert_unit/STAGE.html)

- **PhysicsCompiler._extract_point** (4 calls): [478](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00478_PhysicsCompiler._extract_point/STAGE.html), [481](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00481_PhysicsCompiler._extract_point/STAGE.html), [523](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00523_PhysicsCompiler._extract_point/STAGE.html), [526](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00526_PhysicsCompiler._extract_point/STAGE.html)

- **PhysicsCompiler._build_canonical_scene** (1 calls): [506](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00506_PhysicsCompiler._build_canonical_scene/STAGE.html)

- **PhysicsCompiler._populate_canonical_prism** (1 calls): [514](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00514_PhysicsCompiler._populate_canonical_prism/STAGE.html)

- **PhysicsCompiler._find_entity** (1 calls): [528](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00528_PhysicsCompiler._find_entity/STAGE.html)

- **PhysicsCompiler._preserve_parameter_provenance** (1 calls): [529](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00529_PhysicsCompiler._preserve_parameter_provenance/STAGE.html)

- **validate_canonical_scene** (1 calls): [530](../../../../storage/generated/debug_traces/20261016/TRACE-PRISM-20261016-004-NATIVE-RETRY-20261017/calls/00530_validate_canonical_scene/STAGE.html)

## Appendix B. First failure and propagation

Last known good: Exact source, correct prism semantics and OCR A=60°. Raw edges before OCR suppression retain the source boundaries.

First suspicious: The axis-aligned A=60° OCR box (556,184,128,49) and its four-pixel expansion intersect the slanted prism boundary. Later contour detection yields best_area=0; rays also includes body edges and normals.

First definitive failure: OCR edge masking erases prism-side pixels around A=60°; CV then infers an incorrect base from sloped-segment extents.

Downstream chain: Grounder preserves polygon and incident ray, records OCR apex angle=60°, but does not ground internal/emergent ray entities. Raw detected ray segments remain in evidence, not constraints for the runtime solution. A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray. Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.

Separation of failure classes: preprocessing/perception is demonstrated upstream; a shared coordinate conversion error is not demonstrated; numerical solver failure is not established. The circuit never reaches a solver.

## Appendix C. Capture limits

No new run was performed. The recorder captured repository Python boundaries and GenAI model calls, not private neural-library/C internals. JS boundary events, normalized scenes, actual solver outputs and DOM captures exist; separate entry/exit snapshots for every registry/adapter/renderer child function do not. These gaps are labeled, not filled with reconstructed output. Several void JS returns appear as captureError because undefined is not JSON; resulting state is separately recorded. Two class-serialization errors exist in the historical recorder log; integrity verification found the required snapshot files present for every indexed call. No exact expected pixel dataset, mask or numerical physical state has been authored.

[Original trace integrity checks](../../../../storage/generated/debug_traces/20261017/artifact_verification.json)
