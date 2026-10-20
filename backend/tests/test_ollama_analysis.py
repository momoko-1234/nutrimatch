"""Run with python -m unittest discover -s tests from backend/."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import requests

from app.schemas import AnalyzeRequest
from app.services.personalized_advice import build_personalized_advice
from app.services.ollama_analysis import add_local_analysis


class LocalAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.payload = AnalyzeRequest(profile={"age": 34, "sex": "female",
            "height_cm": 165, "weight_kg": 58, "routine": "late_sleep"},
            health_goals=["sleep"], use_ollama=True)
        self.result = build_personalized_advice(self.payload)
        self.settings = SimpleNamespace(ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5:7b", ollama_timeout_seconds=120)
        self.config = patch("app.services.ollama_analysis.get_settings", return_value=self.settings)
        self.config.start()
        self.addCleanup(self.config.stop)

    @patch("app.services.ollama_analysis.requests.Session")
    def test_disabled_does_not_contact_model(self, factory):
        self.payload.use_ollama = False
        self.assertEqual(add_local_analysis(self.payload, self.result).localAI.status, "disabled")
        factory.assert_not_called()

    @patch("app.services.ollama_analysis.requests.Session")
    def test_success_preserves_rule_results(self, factory):
        before = self.result.model_dump(exclude={"localAI"})
        client = factory.return_value.__enter__.return_value
        client.post.return_value.json.return_value = {"done": True, "message": {"content": "請維持均衡飲食。"}}
        output = add_local_analysis(self.payload, self.result)
        self.assertEqual(output.localAI.status, "success")
        self.assertEqual(output.model_dump(exclude={"localAI"}), before)
        self.assertFalse(client.trust_env)
        self.assertFalse(client.post.call_args.kwargs["allow_redirects"])

    @patch("app.services.ollama_analysis.requests.Session")
    def test_timeout_keeps_report(self, factory):
        factory.return_value.__enter__.return_value.post.side_effect = requests.Timeout()
        output = add_local_analysis(self.payload, self.result)
        self.assertEqual(output.localAI.status, "unavailable")
        self.assertTrue(output.nutrientRecommendations)

    @patch("app.services.ollama_analysis.requests.Session")
    def test_malformed_response_keeps_report(self, factory):
        factory.return_value.__enter__.return_value.post.return_value.json.return_value = {}
        self.assertEqual(add_local_analysis(self.payload, self.result).localAI.status, "unavailable")

    @patch("app.services.ollama_analysis.requests.Session")
    def test_remote_url_is_rejected(self, factory):
        self.settings.ollama_base_url = "https://example.com"
        self.assertEqual(add_local_analysis(self.payload, self.result).localAI.status, "unavailable")
        factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
