from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_order_date(order: dict[str, Any]) -> Optional[datetime]:
    raw = order.get("date")
    if not raw:
        return None
    s = str(raw)
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s[:10].replace("/", "-"), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s[:10])
    except ValueError:
        return None


def build_inventory_signals(product: dict[str, Any]) -> dict[str, Any]:
    stock = _as_float(product.get("stock_quantity"))
    threshold = _as_float(product.get("min_stock_threshold"), 0)
    velocity = max(_as_float(product.get("daily_sales_velocity")), 0.01)
    days_cover = stock / velocity if velocity else 0
    expiry_days = int(_as_float(product.get("expiry_days_left"), 999))
    return {
        "stock_quantity": int(stock) if stock == int(stock) else stock,
        "min_stock_threshold": threshold,
        "daily_sales_velocity": round(velocity, 2),
        "days_of_cover": round(days_cover, 1),
        "below_min_threshold": threshold > 0 and stock <= threshold,
        "near_critical_stock": threshold > 0 and stock <= threshold * 1.15,
        "expiry_days_left": expiry_days,
        "critical_expiry_window": expiry_days <= 4,
        "stock_status": "critical_low"
        if (threshold > 0 and stock <= threshold)
        else "watch"
        if (threshold > 0 and stock <= threshold * 1.15)
        else "ok",
    }


def enrich_supplier_decision(product: Optional[dict[str, Any]], decision: dict[str, Any]) -> dict[str, Any]:
    if not product:
        return decision
    signals = build_inventory_signals(product)
    qc = decision.get("recommended_quantity_change")
    try:
        qc_num = int(qc) if qc is not None else 0
    except (TypeError, ValueError):
        qc_num = 0
    decision = {**decision, "inventory_signals": signals}
    action = decision.get("supplier_action_type")
    if action == "increase_order" and qc_num > 0:
        decision["suggested_next_order_qty"] = abs(qc_num)
    elif action == "reduce_or_delay_order" and qc_num < 0:
        decision["suggested_next_order_qty"] = abs(qc_num)
        decision["suggested_adjustment_note"] = "Bir sonraki siparişte bu kadar birim düşüş veya erteleme önerilir."
    else:
        decision["suggested_next_order_qty"] = 0
    return decision


def _customer_lookup(customers: list[dict[str, Any]]) -> dict[str, str]:
    mp: dict[str, str] = {}
    for c in customers:
        cid = str(c.get("customer_id", "") or "")
        name = str(c.get("customer_name") or c.get("name") or "Müşteri")
        if cid:
            mp[cid] = name
    return mp


def build_order_pulse(
    orders: list[dict[str, Any]],
    customers: list[dict[str, Any]],
    today_str: str,
) -> dict[str, Any]:
    try:
        today = datetime.strptime(today_str[:10], "%Y-%m-%d").date()
    except ValueError:
        today = datetime.now().date()

    names = _customer_lookup(customers)
    window_start = today - timedelta(days=14)

    counts = {"preparing": 0, "delivered": 0, "cancelled": 0}
    preparing_today = 0
    delay_watch: list[dict[str, Any]] = []

    for order in orders:
        od = _parse_order_date(order)
        if od is None:
            continue
        od_date = od.date()
        status = str(order.get("status", "")).lower()
        in_window = od_date >= window_start

        if status == "preparing":
            counts["preparing"] += 1
            sla_due = od_date + timedelta(days=2)
            days_waiting = (today - od_date).days
            late = today > sla_due
            at_risk = days_waiting >= 2 and today >= od_date + timedelta(days=1)

            delay_level = "none"
            if late:
                delay_level = "critical"
            elif at_risk:
                delay_level = "warning"

            cid = str(order.get("customer_id", ""))
            pname = names.get(cid, cid or "Müşteri")
            product_id = str(order.get("product_id", ""))
            oid = str(order.get("order_id", ""))

            notify = ""
            if delay_level != "none":
                notify = (
                    f"Merhaba {pname}, {oid} numaralı siparişinizi hazırlıyoruz. "
                    f"Planlanan teslim penceresi aşıldığı için kusura bakmayın; "
                    f"paket çıkışını önceliklendirdik ve aynı gün içinde sizi bilgilendireceğiz."
                    if delay_level == "critical"
                    else (
                        f"Merhaba {pname}, {oid} siparişiniz hazırlık aşamasında; "
                        f"yarın teslim için kuryeye aktarılacak."
                    )
                )

            row = {
                "order_id": oid,
                "product_id": product_id,
                "customer_name": pname,
                "status": status,
                "order_date": od_date.isoformat(),
                "expected_dispatch_by": sla_due.isoformat(),
                "delay_risk_level": delay_level,
                "days_waiting": days_waiting,
                "customer_notify_draft": notify,
            }

            if delay_level != "none":
                delay_watch.append(row)

            if od_date == today and status == "preparing":
                preparing_today += 1

        elif status == "delivered" and in_window:
            counts["delivered"] += 1
        elif status == "cancelled" and in_window:
            counts["cancelled"] += 1

    delay_watch = sorted(delay_watch, key=lambda x: (x["delay_risk_level"] != "critical", -x["days_waiting"]))[:12]

    return {
        "as_of_date": today_str,
        "summary": {
            "preparing": counts["preparing"],
            "preparing_started_today": preparing_today,
            "recent_delivered_14d": counts["delivered"],
            "recent_cancelled_14d": counts["cancelled"],
            "delay_flagged_orders": sum(1 for d in delay_watch if d["delay_risk_level"] == "critical"),
        },
        "delay_watch": delay_watch,
    }


def build_analytics_pulse(risk_items: list[dict[str, Any]]) -> dict[str, Any]:
    if not risk_items:
        return {
            "expiring_critical_7d": [],
            "high_velocity_watch": [],
            "footnote": "",
        }

    by_expiry = sorted(
        [r for r in risk_items if _as_float(r.get("expiry_days_left")) <= 7],
        key=lambda r: (_as_float(r.get("expiry_days_left")), -_as_float(r.get("preventable_loss"))),
    )[:6]

    expiring_critical_7d = [
        {
            "product_id": r.get("product_id"),
            "name": r.get("name"),
            "expiry_days_left": int(_as_float(r.get("expiry_days_left"))),
            "preventable_loss": round(_as_float(r.get("preventable_loss")), 0),
            "risk_level": r.get("risk_level"),
        }
        for r in by_expiry
    ]

    velocity_watch = []
    for r in risk_items:
        v = _as_float(r.get("daily_sales_velocity"))
        exp_days = _as_float(r.get("expiry_days_left"))
        if exp_days <= 14 and v < 5 and exp_days <= 12:
            velocity_watch.append(
                {
                    "product_id": r.get("product_id"),
                    "name": r.get("name"),
                    "daily_sales_velocity": round(v, 2),
                    "note": "Düşük satış hızı + yakın tarih kombinasyonu",
                }
            )
    velocity_watch = velocity_watch[:5]

    footnote = (
        "Önümüzdeki haftanın risk sıralaması: SKT yakınlığı ve kurtarılabilir zarar için risk motoru çıktısı."
    )

    return {
        "expiring_critical_7d": expiring_critical_7d,
        "high_velocity_watch": velocity_watch,
        "footnote": footnote,
    }


def build_recommendation_evidence_facts(
    product: dict[str, Any],
    data: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    pid = str(product.get("product_id", ""))
    orders = data.get("orders") or []
    recent_orders = [o for o in orders if str(o.get("product_id")) == pid][-5:]

    facts: list[dict[str, str]] = [
        {"label": "Ürün", "value": f"{product.get('name')} ({pid})", "source": "products.csv"},
        {"label": "Kategori & tedarikçi", "value": f"{product.get('category')} · {product.get('supplier')}", "source": "products.csv"},
        {"label": "Stok (adet)", "value": str(product.get("stock_quantity")), "source": "products.csv"},
        {"label": "Minimum stok eşiği", "value": str(product.get("min_stock_threshold")), "source": "products.csv"},
        {"label": "SKT’ye kalan gün", "value": str(int(_as_float(product.get("expiry_days_left")))), "source": "products.csv + sistem tarihi"},
        {"label": "Günlük satış hızı (son dönem)", "value": f"{_as_float(product.get('daily_sales_velocity')):.2f} adet/gün", "source": "sales_history.csv"},
        {"label": "Risk skoru", "value": str(int(_as_float(product.get("risk_score")))), "source": "risk_engine"},
        {"label": "Tahmini fire maliyeti", "value": f"{_as_float(product.get('estimated_loss')):.0f} TL", "source": "risk_engine"},
        {"label": "Kurtarılabilir değer", "value": f"{_as_float(product.get('preventable_loss')):.0f} TL", "source": "risk_engine"},
        {"label": "Önerilen indirim", "value": f"%{int(_as_float(product.get('discount_recommendation')) * 100)}", "source": "risk_engine"},
    ]

    if recent_orders:
        facts.append(
            {
                "label": "Son sipariş kayıtları",
                "value": f"{len(recent_orders)} ilgili satır (ör. {recent_orders[-1].get('order_id')})",
                "source": "orders.csv",
            }
        )

    return {
        "product_id": pid,
        "facts": facts,
        "data_sources": ["products.csv", "sales_history.csv", "orders.csv", "risk_engine"],
    }


def build_operations_snapshot(
    data: dict[str, list[dict[str, Any]]],
    risk_items: list[dict[str, Any]],
    today_str: str,
) -> dict[str, Any]:
    order_pulse = build_order_pulse(data.get("orders") or [], data.get("customers") or [], today_str)
    analytics = build_analytics_pulse(risk_items)
    return {
        "date": today_str,
        "orders": order_pulse,
        "analytics": analytics,
    }
