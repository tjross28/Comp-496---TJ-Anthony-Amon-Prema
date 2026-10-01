import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


class ResponseContractTests(unittest.TestCase):
    def test_end_to_end_response_has_contract_required_fields_and_valid_evidence_links(self):
        root = Path(__file__).resolve().parents[2]
        request_fixture = json.loads((root / "fixtures" / "analysis-request.sample.json").read_text(encoding="utf-8"))
        schema = json.loads((root / "contracts" / "analysis-response.schema.json").read_text(encoding="utf-8"))
        app = create_app()
        app.config.update(TESTING=True)
        response = app.test_client().post("/api/v1/analyses", json=request_fixture)
        body = response.get_json()

        self.assertEqual(200, response.status_code)
        for field in schema["required"]:
            self.assertIn(field, body)
        self.assertEqual(5, len(body["categories"]))
        self.assertAlmostEqual(1.0, sum(category["weight"] for category in body["categories"]))
        clause_ids = {clause["clause_id"] for clause in request_fixture["clauses"]}
        for finding in body["findings"]:
            self.assertTrue(finding["evidence"])
            self.assertTrue({item["clause_id"] for item in finding["evidence"]}.issubset(clause_ids))
        self.assertIn("not legal advice", body["disclaimer"])
