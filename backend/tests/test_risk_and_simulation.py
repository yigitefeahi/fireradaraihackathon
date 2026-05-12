from __future__ import annotations

import unittest
from datetime import date, timedelta

from services.agent_service import match_customer_segments
from services.risk_engine import analyze_product_risk
from services.simulation_engine import simulate_action


class RiskAndSimulationUnitTests(unittest.TestCase):
    def _base_product(self) -> dict:
        return {
            "product_id": "PX01",
            "name": "Test Ürün",
            "category": "Meyve",
            "unit_cost": 10.0,
            "unit_price": 20.0,
            "stock_quantity": 50,
            "expiry_date": (date.today() + timedelta(days=2)).isoformat(),
            "supplier": "Demo Supplier",
        }

    def test_expired_product_is_critical_and_fully_risky(self) -> None:
        product = self._base_product()
        product["expiry_date"] = (date.today() - timedelta(days=1)).isoformat()
        analyzed = analyze_product_risk(product, daily_sales_velocity=8.0, today=date.today())
        self.assertEqual(analyzed["risk_level"], "critical")
        self.assertEqual(analyzed["risky_quantity"], float(product["stock_quantity"]))
        self.assertGreaterEqual(analyzed["risk_score"], 75.0)

    def test_low_sales_velocity_increases_risk(self) -> None:
        product = self._base_product()
        slow = analyze_product_risk(product, daily_sales_velocity=0.2, today=date.today())
        fast = analyze_product_risk(product, daily_sales_velocity=12.0, today=date.today())
        self.assertGreater(slow["risk_score"], fast["risk_score"])
        self.assertGreaterEqual(slow["estimated_loss"], fast["estimated_loss"])

    def test_channel_multiplier_changes_expected_sales(self) -> None:
        product = self._base_product()
        analyzed = analyze_product_risk(product, daily_sales_velocity=5.0, today=date.today())
        sms = simulate_action(analyzed, discount_rate=0.20, channel="SMS")
        whatsapp = simulate_action(analyzed, discount_rate=0.20, channel="WhatsApp")
        self.assertGreater(
            whatsapp["with_action"]["expected_units_sold"],
            sms["with_action"]["expected_units_sold"],
        )

    def test_net_impact_is_non_negative_for_strong_action(self) -> None:
        product = self._base_product()
        analyzed = analyze_product_risk(product, daily_sales_velocity=4.0, today=date.today())
        simulation = simulate_action(analyzed, discount_rate=0.35, channel="WhatsApp")
        self.assertGreaterEqual(simulation["impact"]["prevented_loss"], 0.0)
        self.assertGreaterEqual(simulation["impact"]["net_impact"], 0.0)

    def test_operation_cost_is_applied_to_net_impact(self) -> None:
        product = self._base_product()
        analyzed = analyze_product_risk(product, daily_sales_velocity=4.0, today=date.today())
        simulation = simulate_action(analyzed, discount_rate=0.25, channel="SMS")
        impact = simulation["impact"]
        with_action = simulation["with_action"]
        expected_net = round(
            max(
                float(impact["prevented_loss"]) + float(with_action["gross_margin"]) - float(impact["operation_cost"]),
                0.0,
            ),
            2,
        )
        self.assertEqual(round(float(impact["net_impact"]), 2), expected_net)
        self.assertGreater(float(impact["operation_cost"]), 0.0)

    def test_hard_constraint_blocks_aggressive_campaign_for_expired_fish_meat(self) -> None:
        fish = self._base_product()
        fish["category"] = "Balık"
        fish["expiry_date"] = date.today().isoformat()
        analyzed = analyze_product_risk(fish, daily_sales_velocity=2.0, today=date.today())
        simulation = simulate_action(analyzed, discount_rate=0.35, channel="WhatsApp")
        self.assertTrue(simulation["hard_constrained"])
        self.assertEqual(simulation["impact"]["net_impact"], 0.0)
        self.assertIn("güvenli", simulation["recommended_safe_procedure"].lower())

    def test_new_customer_segments_are_targeted(self) -> None:
        product = self._base_product()
        product["category"] = "Sebze"
        analyzed = analyze_product_risk(product, daily_sales_velocity=2.5, today=date.today())
        customers = [
            {
                "customer_id": "C-BULK",
                "name": "Toplu Alım",
                "segment": "bulk_buyer",
                "region": "Kadıköy",
                "preferred_channel": "Email",
                "interest_tags": "",
                "previous_purchase_count": 12,
            },
            {
                "customer_id": "C-COOP",
                "name": "Kooperatif Üyesi",
                "segment": "cooperative_member",
                "region": "Kadıköy",
                "preferred_channel": "WhatsApp",
                "interest_tags": "",
                "previous_purchase_count": 10,
            },
        ]
        matched = match_customer_segments(analyzed, customers)
        segments = set(matched["target_segments"])
        self.assertIn("bulk_buyer", segments)
        self.assertIn("cooperative_member", segments)
        self.assertGreaterEqual(len(matched["target_customers"]), 1)


if __name__ == "__main__":
    unittest.main()
