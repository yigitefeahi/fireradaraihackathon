from __future__ import annotations

import sys
import unittest
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app  # noqa: E402


class FireRadarApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_risk_analysis_schema_and_basic_calculation(self) -> None:
        response = self.client.get("/risk-analysis")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        for key in ("date", "summary", "items", "category_breakdown", "priority_actions"):
            self.assertIn(key, payload)

        items = payload["items"]
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)

        sample = items[0]
        for key in (
            "product_id",
            "name",
            "estimated_loss",
            "risk_score",
            "risk_level",
            "preventable_loss",
        ):
            self.assertIn(key, sample)

        total_estimated_loss = payload["summary"]["total_estimated_loss"]
        recomputed_loss = round(sum(float(item.get("estimated_loss", 0)) for item in items), 2)
        self.assertAlmostEqual(float(total_estimated_loss), recomputed_loss, places=2)

    def test_run_agent_response_contract(self) -> None:
        response = self.client.post("/run-agent/P001", json={"log_actions": True})
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        required_keys = {
            "product_risk_analysis",
            "loss_estimation",
            "action_comparison",
            "best_action_recommendation",
            "customer_segment",
            "campaign_message",
            "supplier_email_draft",
            "agent_explanation",
            "action_logs",
            "assumptions",
        }
        self.assertTrue(required_keys.issubset(payload.keys()))
        self.assertEqual(payload["product_risk_analysis"]["product_id"], "P001")
        self.assertIsInstance(payload["action_logs"], list)
        self.assertIsInstance(payload["assumptions"], list)
        self.assertGreaterEqual(len(payload["assumptions"]), 2)
        self.assertGreaterEqual(len(payload["action_logs"]), 1)
        self.assertTrue(all("status" in log for log in payload["action_logs"]))

    def test_run_agent_get_preview_has_no_logs(self) -> None:
        response = self.client.get("/run-agent/P001")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("logs_written", payload)
        self.assertFalse(payload["logs_written"])
        self.assertEqual(payload["action_logs"], [])

    def test_actions_log_create_and_list(self) -> None:
        marker = f"test-log-{uuid.uuid4()}"
        create_response = self.client.post(
            "/actions/log",
            json={
                "action_type": "unit_test",
                "message": marker,
                "product_id": "P001",
                "metadata": {"source": "test"},
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created_log = create_response.json()["log"]
        self.assertEqual(created_log["message"], marker)
        self.assertIn("status", created_log)

        list_response = self.client.get("/actions/log?limit=200")
        self.assertEqual(list_response.status_code, 200)
        payload = list_response.json()
        self.assertIn("items", payload)
        self.assertIn("total", payload)
        self.assertGreaterEqual(payload["total"], 1)
        self.assertTrue(any(item.get("message") == marker for item in payload["items"]))

    def test_dispatch_webhook_records_failed_delivery_status(self) -> None:
        response = self.client.post(
            "/actions/dispatch-webhook",
            json={
                "webhook_url": "http://127.0.0.1:9/hook",
                "product_id": "P001",
                "event_type": "campaign_dispatch",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn(payload.get("delivery_status"), {"sent", "failed"})
        self.assertIn("log", payload)
        self.assertIn(payload["log"].get("status"), {"sent", "failed"})

    def test_invalid_product_returns_404(self) -> None:
        response = self.client.get("/decision-explanation/DOES_NOT_EXIST")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertIn("detail", payload)

    def test_ask_ai_returns_answer_shape(self) -> None:
        response = self.client.post(
            "/ask-ai",
            json={"question": "Bugün önce ne yapayım?", "product_id": "P001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("provider", payload)
        self.assertIn("answer", payload)
        self.assertIn("context_product_id", payload)
        self.assertEqual(payload["context_product_id"], "P001")
        self.assertIsInstance(payload["answer"], str)
        self.assertGreater(len(payload["answer"].strip()), 0)


if __name__ == "__main__":
    unittest.main()
