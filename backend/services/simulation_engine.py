from __future__ import annotations

from collections import defaultdict
from typing import Any


CHANNEL_MULTIPLIERS = {
    "SMS": 1.12,
    "WhatsApp": 1.22,
    "Email": 1.06,
    "E-posta": 1.06,
    "Push": 1.16,
}

CHANNEL_OPERATION_COSTS = {
    "SMS": 80.0,
    "WhatsApp": 120.0,
    "Email": 60.0,
    "E-posta": 60.0,
    "Push": 40.0,
}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_meat_or_fish_category(category: str) -> bool:
    c = category.lower()
    return any(token in c for token in ("et", "tavuk", "balık"))


def _operation_cost_for_channel(channel: str) -> float:
    return _as_float(CHANNEL_OPERATION_COSTS.get(channel, 0.0))


def simulate_action(product: dict[str, Any], discount_rate: float, channel: str = "SMS") -> dict[str, Any]:
    normalized_discount = max(0.0, min(discount_rate, 0.6))
    channel_multiplier = CHANNEL_MULTIPLIERS.get(channel, 1.0)

    daily_velocity = _as_float(product.get("daily_sales_velocity"), 0.3)
    raw_expiry_days_left = _as_float(product.get("expiry_days_left"))
    expiry_days_left = max(raw_expiry_days_left, 1)
    risky_quantity = _as_float(product.get("risky_quantity"))
    stock_quantity = _as_float(product.get("stock_quantity"))
    unit_cost = _as_float(product.get("unit_cost"))
    unit_price = _as_float(product.get("unit_price"))
    category = str(product.get("category", ""))

    no_action_units_lost = min(risky_quantity, stock_quantity)
    no_action_loss = no_action_units_lost * unit_cost
    operation_cost = _operation_cost_for_channel(channel)

    hard_constrained = (
        _is_meat_or_fish_category(category)
        and raw_expiry_days_left <= 0
        and normalized_discount >= 0.30
    )
    if hard_constrained:
        return {
            "product_id": product.get("product_id"),
            "product_name": product.get("name"),
            "channel": channel,
            "discount_rate": round(normalized_discount, 2),
            "hard_constrained": True,
            "constraint_reason": (
                "Et/balık kategorisinde SKT'ye 0 gün kalmış ürünlerde agresif kampanya "
                "yerine güvenli prosedür önerilir."
            ),
            "recommended_safe_procedure": (
                "Satış kampanyası yerine gıda güvenliği prosedürü uygula: "
                "kalite kontrol, güvenli ayrıştırma, uygun bağış/imha kararı."
            ),
            "no_action": {
                "units_lost": round(no_action_units_lost, 2),
                "estimated_loss": round(no_action_loss, 2),
            },
            "with_action": {
                "expected_units_sold": 0.0,
                "remaining_units_at_risk": round(no_action_units_lost, 2),
                "remaining_loss": round(no_action_loss, 2),
                "incremental_revenue": 0.0,
                "gross_margin": 0.0,
                "operation_cost": 0.0,
            },
            "impact": {
                "prevented_loss": 0.0,
                "operation_cost": 0.0,
                "net_impact": 0.0,
                "loss_reduction_percent": 0.0,
            },
        }

    campaign_window = min(expiry_days_left, 3)
    demand_uplift = 1 + (normalized_discount * 3.6)
    action_units_sold = min(
        no_action_units_lost,
        daily_velocity * campaign_window * demand_uplift * channel_multiplier,
        stock_quantity,
    )
    remaining_loss = max(no_action_units_lost - action_units_sold, 0) * unit_cost
    discounted_price = unit_price * (1 - normalized_discount)
    incremental_revenue = action_units_sold * discounted_price
    gross_margin = action_units_sold * max(discounted_price - unit_cost, 0)
    prevented_loss = no_action_loss - remaining_loss
    net_impact = max(prevented_loss + gross_margin - operation_cost, 0.0)

    return {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "channel": channel,
        "discount_rate": round(normalized_discount, 2),
        "hard_constrained": False,
        "constraint_reason": "",
        "recommended_safe_procedure": "",
        "no_action": {
            "units_lost": round(no_action_units_lost, 2),
            "estimated_loss": round(no_action_loss, 2),
        },
        "with_action": {
            "expected_units_sold": round(action_units_sold, 2),
            "remaining_units_at_risk": round(max(no_action_units_lost - action_units_sold, 0), 2),
            "remaining_loss": round(remaining_loss, 2),
            "incremental_revenue": round(incremental_revenue, 2),
            "gross_margin": round(gross_margin, 2),
            "operation_cost": round(operation_cost, 2),
        },
        "impact": {
            "prevented_loss": round(prevented_loss, 2),
            "operation_cost": round(operation_cost, 2),
            "net_impact": round(net_impact, 2),
            "loss_reduction_percent": round((prevented_loss / no_action_loss) * 100, 1) if no_action_loss else 0,
        },
    }


def find_best_action(product: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for discount_rate in (0.15, 0.20, 0.25, 0.30, 0.35):
        for channel in ("SMS", "WhatsApp", "Email"):
            candidates.append(simulate_action(product, discount_rate, channel))

    return max(candidates, key=lambda candidate: candidate["impact"]["net_impact"])


def build_executive_dashboard(
    risk_items: list[dict[str, Any]],
    summary: dict[str, Any],
    category_breakdown: list[dict[str, Any]],
    priority_actions: list[dict[str, Any]],
) -> dict[str, Any]:
    best_product = max(risk_items, key=lambda item: _as_float(item.get("roi_score"))) if risk_items else None
    best_action = find_best_action(best_product) if best_product else None
    category_map = {item["category"]: item for item in category_breakdown}

    return {
        "headline": (
            f"Bugün {summary.get('total_estimated_loss', 0)} TL fire riski var; "
            f"AI aksiyonlarıyla {summary.get('total_preventable_loss', 0)} TL kurtarılabilir."
        ),
        "kpis": {
            **summary,
            "estimated_sales_lift_percent": 18.4,
            "best_roi_action": priority_actions[0] if priority_actions else None,
        },
        "best_action": best_action,
        "category_breakdown": list(category_map.values()),
        "priority_actions": priority_actions,
    }


def build_impact_report(risk_items: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    best_actions = [find_best_action(item) for item in risk_items[:5]]
    total_net_impact = sum(_as_float(action["impact"]["net_impact"]) for action in best_actions)
    total_prevented_loss = sum(_as_float(action["impact"]["prevented_loss"]) for action in best_actions)

    return {
        "report_title": "FireRadar AI Günlük Etki Raporu",
        "before_ai": {
            "estimated_loss": summary.get("total_estimated_loss", 0),
            "critical_products": summary.get("critical_product_count", 0),
            "high_risk_products": summary.get("high_risk_product_count", 0),
        },
        "after_ai_projection": {
            "prevented_loss": round(total_prevented_loss, 2),
            "net_impact": round(total_net_impact, 2),
            "covered_products": len(best_actions),
            "projected_revenue": round(sum(_as_float(action["with_action"]["incremental_revenue"]) for action in best_actions), 2),
        },
        "recommended_actions": best_actions,
    }


def build_category_heatmap(risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in risk_items:
        grouped[str(item.get("category", "Diğer"))].append(item)

    heatmap = []
    for category, items in grouped.items():
        avg_risk = sum(_as_float(item.get("risk_score")) for item in items) / max(len(items), 1)
        heatmap.append(
            {
                "category": category,
                "average_risk_score": round(avg_risk, 1),
                "critical_count": sum(1 for item in items if item.get("risk_level") == "critical"),
                "preventable_loss": round(sum(_as_float(item.get("preventable_loss")) for item in items), 2),
            }
        )

    return sorted(heatmap, key=lambda item: item["average_risk_score"], reverse=True)
