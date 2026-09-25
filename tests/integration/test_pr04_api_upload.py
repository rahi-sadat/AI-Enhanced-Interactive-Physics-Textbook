"""Integration tests for PR-04: Real Image Ingestion API (/api/ingest).

Covers §25 of PR-04 specification:
- End-to-end HTTP multipart upload of arbitrary, unseen images
- Exact byte preservation and SHA-256 verification
- Native image dimensions (source_px) survival in SourceAsset and PageIR
- Honest UNRESOLVED status in BookIR (zero physics fabrication)
- No PhysicsScene created for unknown images
- Storage persistence and public URL resolution
- Validation error handling for non-image / corrupted payloads
"""

import io
import hashlib
import unittest
from PIL import Image

from fastapi.testclient import TestClient
from apps.api.main import app


class TestPR04ApiUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def _create_test_image(self, width: int, height: int, fmt: str = "PNG", color=(100, 150, 200)) -> bytes:
        img = Image.new("RGB", (width, height), color=color)
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()

    def test_01_ingest_health(self):
        """GET /api/ingest/health returns available=True and PR-04 info."""
        res = self.client.get("/api/ingest/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("available"))
        self.assertEqual(data.get("pipeline"), "PR-04")

    def test_02_upload_arbitrary_png_bytes(self):
        """POST /api/ingest with unseen PNG verifies full pipeline contract."""
        width, height = 480, 320
        raw_bytes = self._create_test_image(width, height, fmt="PNG", color=(70, 130, 180))
        expected_sha = hashlib.sha256(raw_bytes).hexdigest()

        response = self.client.post(
            "/api/ingest",
            files={"file": ("unseen_textbook_diag.png", raw_bytes, "image/png")}
        )

        self.assertEqual(response.status_code, 200, f"Upload failed: {response.text}")
        payload = response.json()

        # 1. Pipeline status
        self.assertTrue(payload["success"])
        self.assertEqual(payload["pipeline"], "PR-04")
        self.assertTrue(payload["image_url"].startswith("/"))

        # 2. SourceAsset
        asset = payload["source_asset"]
        self.assertEqual(asset["sha256"], expected_sha)
        self.assertEqual(asset["width_px"], width)
        self.assertEqual(asset["height_px"], height)
        self.assertEqual(asset["byteSize"], len(raw_bytes))
        self.assertEqual(asset["mimeType"], "image/png")
        self.assertEqual(asset["originalFilename"], "unseen_textbook_diag.png")

        # 3. PageIR
        page_ir = payload["page_ir"]
        self.assertEqual(page_ir["source"]["width_px"], width)
        self.assertEqual(page_ir["source"]["height_px"], height)
        self.assertEqual(page_ir["coordinateSpace"]["type"], "source_px")
        self.assertEqual(len(page_ir["figures"]), 1)
        fig = page_ir["figures"][0]
        self.assertEqual(fig["detectionMethod"], "user_supplied")
        self.assertEqual(fig["pageX"], 0.0)
        self.assertEqual(fig["pageY"], 0.0)
        self.assertEqual(fig["width"], float(width))
        self.assertEqual(fig["height"], float(height))

        # 4. BookIR (Honest UNRESOLVED — no fake physics invented)
        book_ir = payload["book_ir"]
        self.assertIsNone(book_ir["domain"])
        self.assertIsNone(book_ir["subtype"])
        self.assertEqual(book_ir["status"], "UNRESOLVED")
        self.assertEqual(book_ir["entities"], [])
        self.assertEqual(book_ir["parameters"], {})

        # 5. PhysicsCompilerResult (No fake scene)
        compiler = payload["compiler"]
        self.assertEqual(compiler["status"], "UNRESOLVED")
        self.assertIsNone(compiler["scene"])
        self.assertGreater(len(compiler["issues"]), 0)

        # 6. Top-level convenience fields
        self.assertEqual(payload["status"], "unresolved")
        self.assertIsNone(payload["domain"])
        self.assertIsNone(payload["scenario"])
        self.assertIsNone(payload["scene"])
        self.assertEqual(payload["width"], width)
        self.assertEqual(payload["height"], height)

    def test_03_upload_second_unseen_jpeg_image(self):
        """POST /api/ingest with second unseen JPEG image (different dims & format)."""
        width, height = 720, 405
        raw_bytes = self._create_test_image(width, height, fmt="JPEG", color=(220, 80, 50))
        expected_sha = hashlib.sha256(raw_bytes).hexdigest()

        response = self.client.post(
            "/api/ingest",
            files={"file": ("page_42_exercise.jpg", raw_bytes, "image/jpeg")}
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        asset = payload["source_asset"]
        self.assertEqual(asset["sha256"], expected_sha)
        self.assertEqual(asset["width_px"], width)
        self.assertEqual(asset["height_px"], height)
        self.assertEqual(asset["mimeType"], "image/jpeg")
        self.assertEqual(payload["book_ir"]["status"], "UNRESOLVED")
        self.assertIsNone(payload["book_ir"]["domain"])
        self.assertIsNone(payload["compiler"]["scene"])

    def test_04_different_images_have_different_identities(self):
        """Two different images produce distinct SourceAssets and hashes."""
        img1 = self._create_test_image(100, 100, color=(10, 20, 30))
        img2 = self._create_test_image(100, 100, color=(40, 50, 60))

        res1 = self.client.post("/api/ingest", files={"file": ("img1.png", img1, "image/png")})
        res2 = self.client.post("/api/ingest", files={"file": ("img2.png", img2, "image/png")})

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        sha1 = res1.json()["source_asset"]["sha256"]
        sha2 = res2.json()["source_asset"]["sha256"]
        self.assertNotEqual(sha1, sha2)
        id1 = res1.json()["source_asset"]["id"]
        id2 = res2.json()["source_asset"]["id"]
        self.assertNotEqual(id1, id2)

    def test_05_corrupt_payload_rejected(self):
        """POST /api/ingest with corrupted byte sequence returns 422 Unprocessable Entity."""
        corrupt_bytes = b"NOT_A_VALID_IMAGE_DATA_STREAM_123456"
        response = self.client.post(
            "/api/ingest",
            files={"file": ("corrupt.png", corrupt_bytes, "image/png")}
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("could not decode image", response.text.lower())

    def test_06_unsupported_mime_rejected(self):
        """POST /api/ingest with unsupported MIME type returns 422."""
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        response = self.client.post(
            "/api/ingest",
            files={"file": ("document.pdf", pdf_bytes, "application/pdf")}
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("unsupported mime type", response.text.lower())

    def test_07_oversized_file_rejected(self):
        """UploadService rejects data exceeding MAX_BYTE_SIZE (50 MB)."""
        from ai.ingestion.UploadService import UploadValidationError, UploadService, MAX_BYTE_SIZE
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = UploadService(storage_dir=Path(tmpdir) / "store", public_dir=Path(tmpdir) / "pub")
            with self.assertRaises(UploadValidationError) as ctx:
                # Test check logic directly without allocating 51MB in memory
                oversized_bytes = b"X" * (MAX_BYTE_SIZE + 10)
                svc.ingest(oversized_bytes, "huge.png", "image/png")
            self.assertIn("too large", str(ctx.exception).lower())

    def test_08_unseen_fixtures_corpus(self):
        """All unseen fixture categories pass through pipeline with honest UNRESOLVED BookIR."""
        from pathlib import Path
        unseen_base = Path("tests/fixtures/unseen")
        fixtures = [
            ("mechanics/pendulum_sketch_raw.png", 800, 600),
            ("optics/lens_diagram_exercise.png", 900, 450),
            ("circuits/resistor_network_handdrawn.png", 600, 600),
            ("unrelated/landscape_photo.jpg", 400, 500),
        ]
        for rel_path, expected_w, expected_h in fixtures:
            file_path = unseen_base / rel_path
            self.assertTrue(file_path.exists(), f"Fixture {file_path} not found")
            with open(file_path, "rb") as f:
                data = f.read()

            mime = "image/png" if file_path.suffix == ".png" else "image/jpeg"
            res = self.client.post(
                "/api/ingest",
                files={"file": (file_path.name, data, mime)}
            )
            self.assertEqual(res.status_code, 200, f"Failed for {rel_path}: {res.text}")
            payload = res.json()

            # Verifications:
            # 1. Native dimensions preserved
            self.assertEqual(payload["source_asset"]["width_px"], expected_w)
            self.assertEqual(payload["source_asset"]["height_px"], expected_h)
            self.assertEqual(payload["page_ir"]["source"]["width_px"], expected_w)

            # 2. Honest UNRESOLVED status — zero physics invented based on filename or folder
            self.assertEqual(payload["book_ir"]["status"], "UNRESOLVED")
            self.assertIsNone(payload["book_ir"]["domain"])
            self.assertIsNone(payload["book_ir"]["subtype"])
            self.assertEqual(payload["compiler"]["status"], "UNRESOLVED")
            self.assertIsNone(payload["compiler"]["scene"])


if __name__ == "__main__":
    unittest.main()

