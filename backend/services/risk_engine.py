from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from math import ceil
from typing import Any, Optional

from services.data_loader import get_today


def _to_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    raise ValueError(f"Unsupported date value: {value!r}")


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _discount_recommendation(risk_score: float, expiry_days_left: int) -> float:
    if expiry_days_left <= 1 or risk_score >= 85:
        return 0.35
    if risk_score >= 75:
        return 0.30
    if risk_score >= 60:
        return 0.25
    if risk_score >= 45:
        return 0.15
    return 0.0


def _impact_label(preventable_loss: float, roi_score: float) -> str:
    if preventable_loss >= 1500 or roi_score >= 90:
        return "game_changer"
    if preventable_loss >= 700 or roi_score >= 70:
        return "high_impact"
    if preventable_loss >= 250 or roi_score >= 45:
        return "quick_win"
    return "monitor"


def _estimated_unit_weight_kg(product: dict[str, Any]) -> float:
    name = str(product.get("name", "")).lower()
    category = str(product.get("category", "")).lower()

    if "500g" in name or "500 g" in name:
        return 0.5
    if "300g" in name or "300 g" in name:
        return 0.3
    if "250g" in name or "250 g" in name:
        return 0.25
    if "1kg" in name or "1 kg" in name:
        return 1.0
    if "1l" in name or "1 l" in name:
        return 1.0
    if "15li" in name:
        return 0.9
    if "meyve" in category or "sebze" in category:
        return 0.5
    if "et" in category or "tavuk" in category or "balık" in category:
        return 0.45
    if "süt" in category:
        return 0.75
    return 0.4


def _co2_factor_by_category(category: str) -> float:
    category = category.lower()
    if "et" in category or "tavuk" in category:
        return 6.9
    if "balık" in category:
        return 5.4
    if "süt" in category or "kahvaltılık" in category:
        return 2.8
    if "meyve" in category:
        return 1.1
    return 1.8


def _risk_weights_by_category(category: str) -> tuple[float, float, float]:
    c = category.lower()
    if "et" in c or "tavuk" in c or "balık" in c:
        return 0.45, 0.35, 0.20
    if "fırın" in c or "hazır yemek" in c:
        return 0.40, 0.35, 0.25
    if "kooperatif" in c:
        return 0.30, 0.35, 0.35
    if "süt" in c:
        return 0.38, 0.34, 0.28
    return 0.35, 0.35, 0.30


def calculate_daily_sales_velocity(
    sales_history: list[dict[str, Any]],
) -> dict[str, float]:
    quantities_by_product: dict[str, float] = defaultdict(float)
    active_days_by_product: dict[str, set[str]] = defaultdict(set)

    for sale in sales_history:
        product_id = str(sale.get("product_id", ""))
        quantity = _as_float(sale.get("quantity_sold"))
        sale_date = str(sale.get("date", ""))

        if not product_id:
            continue

        quantities_by_product[product_id] += quantity
        if sale_date:
            active_days_by_product[product_id].add(sale_date)

    velocities: dict[str, float] = {}
    for product_id, total_quantity in quantities_by_product.items():
        day_count = max(len(active_days_by_product[product_id]), 1)
        velocities[product_id] = max(total_quantity / day_count, 0.1)

    return velocities


def analyze_product_risk(
    product: dict[str, Any],
    daily_sales_velocity: float,
    today: Optional[date] = None,
) -> dict[str, Any]:
    today = today or get_today()
    expiry_date = _to_date(product["expiry_date"])
    stock_quantity = _as_float(product.get("stock_quantity"))
    unit_cost = _as_float(product.get("unit_cost"))
    unit_price = _as_float(product.get("unit_price"))

    expiry_days_left = (expiry_date - today).days
    safe_velocity = max(daily_sales_velocity, 0.1)
    estimated_days_to_sell = ceil(stock_quantity / safe_velocity) if stock_quantity else 0

    sellable_until_expiry = max(expiry_days_left, 0) * safe_velocity
    risky_quantity = max(stock_quantity - sellable_until_expiry, 0)
    if expiry_days_left < 0:
        risky_quantity = stock_quantity

    estimated_loss = risky_quantity * unit_cost
    estimated_revenue_at_risk = risky_quantity * unit_price

    expiry_pressure = 100 if expiry_days_left <= 0 else max(0, 100 - (expiry_days_left * 4))
    sell_through_pressure = min((estimated_days_to_sell / max(expiry_days_left, 1)) * 45, 100)
    quantity_pressure = min((risky_quantity / max(stock_quantity, 1)) * 100, 100)
    w_expiry, w_sell_through, w_quantity = _risk_weights_by_category(str(product.get("category", "")))
    risk_score = round(
        (expiry_pressure * w_expiry)
        + (sell_through_pressure * w_sell_through)
        + (quantity_pressure * w_quantity),
        1,
    )

    if risk_score >= 75:
        risk_level = "critical"
        recommended_action = "Acil indirim, bundle kampanya ve personel uyarısı başlat."
    elif risk_score >= 55:
        risk_level = "high"
        recommended_action = "Bugün kampanya mesajı gönder ve raf önceliğini artır."
    elif risk_score >= 35:
        risk_level = "medium"
        recommended_action = "Satış hızını takip et, küçük promosyon veya çapraz satış öner."
    else:
        risk_level = "low"
        recommended_action = "Normal satış akışını sürdür."

    discount_recommendation = _discount_recommendation(risk_score, expiry_days_left)
    action_window_days = max(min(expiry_days_left, 3), 1)
    uplift_multiplier = 1 + (discount_recommendation * 3.2)
    expected_units_saved = min(
        risky_quantity,
        safe_velocity * action_window_days * uplift_multiplier,
        stock_quantity,
    )
    preventable_loss = expected_units_saved * unit_cost
    unit_weight_kg = _estimated_unit_weight_kg(product)
    estimated_waste_kg = risky_quantity * unit_weight_kg
    preventable_waste_kg = expected_units_saved * unit_weight_kg
    co2_factor = _co2_factor_by_category(str(product.get("category", "")))
    estimated_co2_kg = estimated_waste_kg * co2_factor
    preventable_co2_kg = preventable_waste_kg * co2_factor
    discounted_unit_price = unit_price * (1 - discount_recommendation)
    projected_revenue = expected_units_saved * discounted_unit_price
    projected_margin = expected_units_saved * max(discounted_unit_price - unit_cost, 0)
    roi_score = min(
        100,
        (preventable_loss * 0.055) + (projected_margin * 0.025) + (risk_score * 0.45),
    )
    impact_label = _impact_label(preventable_loss, roi_score)

    return {
        **product,
        "daily_sales_velocity": round(safe_velocity, 2),
        "expiry_days_left": expiry_days_left,
        "estimated_days_to_sell": estimated_days_to_sell,
        "risky_quantity": round(risky_quantity, 2),
        "estimated_loss": round(estimated_loss, 2),
        "estimated_revenue_at_risk": round(estimated_revenue_at_risk, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "discount_recommendation": round(discount_recommendation, 2),
        "expected_units_saved": round(expected_units_saved, 2),
        "preventable_loss": round(preventable_loss, 2),
        "estimated_waste_kg": round(estimated_waste_kg, 2),
        "preventable_waste_kg": round(preventable_waste_kg, 2),
        "estimated_co2_kg": round(estimated_co2_kg, 2),
        "preventable_co2_kg": round(preventable_co2_kg, 2),
        "projected_revenue": round(projected_revenue, 2),
        "projected_margin": round(projected_margin, 2),
        "roi_score": round(roi_score, 1),
        "impact_label": impact_label,
    }


def analyze_inventory_risk(
    products: list[dict[str, Any]],
    sales_history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    velocities = calculate_daily_sales_velocity(sales_history)

    risk_items = [
        analyze_product_risk(
            product=product,
            daily_sales_velocity=velocities.get(str(product.get("product_id")), 0.3),
        )
        for product in products
    ]

    return sorted(risk_items, key=lambda item: item["risk_score"], reverse=True)


def build_risk_summary(risk_items: list[dict[str, Any]]) -> dict[str, Any]:
    total_risky_quantity = sum(_as_float(item.get("risky_quantity")) for item in risk_items)
    total_estimated_loss = sum(_as_float(item.get("estimated_loss")) for item in risk_items)
    total_revenue_at_risk = sum(_as_float(item.get("estimated_revenue_at_risk")) for item in risk_items)
    total_preventable_loss = sum(_as_float(item.get("preventable_loss")) for item in risk_items)
    projected_revenue = sum(_as_float(item.get("projected_revenue")) for item in risk_items)
    projected_margin = sum(_as_float(item.get("projected_margin")) for item in risk_items)
    total_estimated_waste_kg = sum(_as_float(item.get("estimated_waste_kg")) for item in risk_items)
    total_preventable_waste_kg = sum(_as_float(item.get("preventable_waste_kg")) for item in risk_items)
    total_estimated_co2_kg = sum(_as_float(item.get("estimated_co2_kg")) for item in risk_items)
    total_preventable_co2_kg = sum(_as_float(item.get("preventable_co2_kg")) for item in risk_items)
    critical_count = sum(1 for item in risk_items if item.get("risk_level") == "critical")
    high_risk_count = sum(1 for item in risk_items if item.get("risk_level") in {"critical", "high"})
    average_roi_score = (
        sum(_as_float(item.get("roi_score")) for item in risk_items) / len(risk_items)
        if risk_items
        else 0
    )

    return {
        "total_products": len(risk_items),
        "total_risky_quantity": round(total_risky_quantity, 2),
        "total_estimated_loss": round(total_estimated_loss, 2),
        "total_revenue_at_risk": round(total_revenue_at_risk, 2),
        "total_preventable_loss": round(total_preventable_loss, 2),
        "projected_revenue": round(projected_revenue, 2),
        "projected_margin": round(projected_margin, 2),
        "total_estimated_waste_kg": round(total_estimated_waste_kg, 2),
        "total_preventable_waste_kg": round(total_preventable_waste_kg, 2),
        "total_estimated_co2_kg": round(total_estimated_co2_kg, 2),
        "total_preventable_co2_kg": round(total_preventable_co2_kg, 2),
        "average_roi_score": round(average_roi_score, 1),
        "critical_product_count": critical_count,
        "high_risk_product_count": high_risk_count,
    }


def get_high_risk_products(risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in risk_items
        if item.get("risk_level") in {"critical", "high"} or _as_float(item.get("risk_score")) >= 55
    ]


def build_category_breakdown(risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}

    for item in risk_items:
        category = str(item.get("category", "Diğer"))
        if category not in categories:
            categories[category] = {
                "category": category,
                "product_count": 0,
                "estimated_loss": 0.0,
                "preventable_loss": 0.0,
                "max_risk_score": 0.0,
            }

        categories[category]["product_count"] += 1
        categories[category]["estimated_loss"] += _as_float(item.get("estimated_loss"))
        categories[category]["preventable_loss"] += _as_float(item.get("preventable_loss"))
        categories[category]["max_risk_score"] = max(
            categories[category]["max_risk_score"],
            _as_float(item.get("risk_score")),
        )

    return sorted(
        [
            {
                **category,
                "estimated_loss": round(category["estimated_loss"], 2),
                "preventable_loss": round(category["preventable_loss"], 2),
                "max_risk_score": round(category["max_risk_score"], 1),
            }
            for category in categories.values()
        ],
        key=lambda item: item["estimated_loss"],
        reverse=True,
    )


def build_priority_actions(risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_items = sorted(
        risk_items,
        key=lambda item: (_as_float(item.get("roi_score")), _as_float(item.get("preventable_loss"))),
        reverse=True,
    )

    actions = []
    for item in priority_items[:5]:
        discount = int(_as_float(item.get("discount_recommendation")) * 100)
        actions.append(
            {
                "product_id": item.get("product_id"),
                "product_name": item.get("name"),
                "action": f"%{discount} indirim + raf önü + hedefli SMS",
                "deadline": "Bugün" if _as_float(item.get("expiry_days_left")) <= 3 else "48 saat içinde",
                "expected_impact": round(_as_float(item.get("preventable_loss")), 2),
                "roi_score": round(_as_float(item.get("roi_score")), 1),
                "impact_label": item.get("impact_label"),
            }
        )

    return actions
