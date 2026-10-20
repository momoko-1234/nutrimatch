import json
from pathlib import Path
import unittest

from fastapi.testclient import TestClient
from app.main import app


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.payload = json.loads((Path(__file__).resolve().parents[2] / "examples/profile.json").read_text(encoding="utf-8"))

    def test_health(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")

    def test_report_contract(self):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        report = response.json()
        self.assertEqual(len(report["nutrientRecommendations"]), 8)
        self.assertEqual(report["localAI"]["status"], "disabled")
        self.assertIn("B Complex", report["coveredNutrients"])
        self.assertEqual(report["currentSupplementReview"][0]["productId"], "dhc-b-complex")

    def test_invalid_age_rejected(self):
        self.payload["profile"]["age"] = 0
        self.assertEqual(self.client.post("/api/analyze", json=self.payload).status_code, 422)

    def test_coverage_lowers_priority(self):
        with_product = self.client.post("/api/analyze", json=self.payload).json()
        self.payload["current_supplements"] = []
        without_product = self.client.post("/api/analyze", json=self.payload).json()
        def score(report):
            return next(item["score"] for item in report["nutrientRecommendations"] if item["nutrient"] == "B Complex")
        self.assertLess(score(with_product), score(without_product))


if __name__ == "__main__":
    unittest.main()
