import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


class StubPolicyAnalyzer:
    model = "test-model"

    def analyze_text(self, text):
        excerpt = "We collect your name"
        return {
            "summary": "The policy describes collection, sharing, and reader choices.",
            "key_points": [{"explanation": "Contact details are collected.", "evidence_excerpt": excerpt}],
            "things_to_review": [],
            "reader_questions": ["How can I exercise the choices described?"],
        }


class ResponseContractTests(unittest.TestCase):
    def test_response_matches_summary_contract(self):
        root = Path(__file__).resolve().parents[2]
        request_fixture = json.loads((root / "fixtures" / "analysis-request.sample.json").read_text(encoding="utf-8"))
        schema = json.loads((root / "contracts" / "analysis-response.schema.json").read_text(encoding="utf-8"))
        app = create_app({"AI_ANALYZER": StubPolicyAnalyzer()})
        app.config.update(TESTING=True)
        response = app.test_client().post("/api/v1/analyses", json=request_fixture)
        body = response.get_json()

        self.assertEqual(200, response.status_code)
        for field in schema["required"]:
            self.assertIn(field, body)
        self.assertEqual("test-model", body["model"])
        self.assertTrue(body["key_points"][0]["evidence_excerpt"])
        self.assertIn("not legal advice", body["disclaimer"])
