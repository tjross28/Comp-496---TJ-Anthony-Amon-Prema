import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True, RATE_LIMIT=20, RATE_WINDOW_SECONDS=60)
        self.client = app.test_client()
        fixture = Path(__file__).resolve().parents[2] / "fixtures" / "analysis-request.sample.json"
        self.payload = json.loads(fixture.read_text(encoding="utf-8"))

    def test_health_check(self):
        response = self.client.get("/healthz")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.get_json()["status"])

    def test_analysis_returns_structured_evidence_backed_response(self):
        response = self.client.post("/api/v1/analyses", json=self.payload)
        body = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertEqual("0.1.0", body["engine_version"])
        self.assertIn("trust_score", body)
        self.assertTrue(body["findings"][0]["evidence"])
        self.assertIn("not legal advice", body["disclaimer"])

    def test_invalid_payload_has_safe_structured_error(self):
        response = self.client.post("/api/v1/analyses", json={"document_id": "missing"})
        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_analysis_request", response.get_json()["error"]["code"])

    def test_non_json_payload_is_rejected(self):
        response = self.client.post("/api/v1/analyses", data="not-json", content_type="text/plain")
        self.assertEqual(415, response.status_code)
        self.assertEqual("unsupported_media_type", response.get_json()["error"]["code"])

    def test_api_token_is_required_when_configured(self):
        app = create_app()
        app.config.update(TESTING=True, ANALYSIS_API_TOKEN="test-token")
        client = app.test_client()
        self.assertEqual(401, client.post("/api/v1/analyses", json=self.payload).status_code)
        self.assertEqual(200, client.post("/api/v1/analyses", json=self.payload, headers={"X-Analysis-Token": "test-token"}).status_code)

    def test_rate_limit_rejects_excess_requests(self):
        app = create_app()
        app.config.update(TESTING=True, RATE_LIMIT=1, RATE_WINDOW_SECONDS=60)
        client = app.test_client()
        self.assertEqual(200, client.post("/api/v1/analyses", json=self.payload).status_code)
        response = client.post("/api/v1/analyses", json=self.payload)
        self.assertEqual(429, response.status_code)
        self.assertEqual("rate_limited", response.get_json()["error"]["code"])


if __name__ == "__main__":
    unittest.main()
