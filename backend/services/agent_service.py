from __future__ import annotations

from typing import Any

from services.simulation_engine import simulate_action


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    return int(round(_as_float(value, default)))


def _discount_percent(product: dict[str, Any]) -> int:
    return _as_int(_as_float(product.get("discount_recommendation")) * 100)


def build_decision_explanation(product: dict[str, Any]) -> dict[str, Any]:
    stock = _as_int(product.get("stock_quantity"))
    velocity = _as_float(product.get("daily_sales_velocity"))
    expiry_days = _as_int(product.get("expiry_days_left"))
    risky_quantity = _as_float(product.get("risky_quantity"))
    estimated_loss = _as_float(product.get("estimated_loss"))
    preventable_loss = _as_float(product.get("preventable_loss"))
    discount = _discount_percent(product)
    confidence_score = min(
        96,
        max(52, _as_int(product.get("risk_score")) + (8 if preventable_loss > 500 else 0)),
    )
    has_core_data = all(
        product.get(field) is not None
        for field in ("stock_quantity", "expiry_date", "daily_sales_velocity", "estimated_loss")
    )
    data_quality = "Yüksek" if has_core_data and velocity > 0 else "Orta"
    confidence_reason = (
        "Ürünün stok, son tüketim tarihi ve son 10 günlük satış geçmişi verisi mevcut olduğu için öneri güvenilir."
        if data_quality == "Yüksek"
        else "Bazı veri alanları sınırlı olduğu için öneri temkinli yorumlanmalıdır."
    )

    return {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "decision_summary": f"{product.get('name')} bugün aksiyon gerektiren ürünlerden biri.",
        "why_critical": (
            f"Son tüketim tarihine {expiry_days} gün kaldı ve mevcut satış hızı "
            "stokun tamamını zamanında eritmek için yeterli görünmüyor."
        ),
        "evidence": [
            f"Stok: {stock} adet",
            f"Günlük satış hızı: {round(velocity, 1)} adet",
            f"Son tüketim tarihine kalan süre: {expiry_days} gün",
            f"Tahmini riskli miktar: {round(risky_quantity, 1)} adet",
            f"Tahmini kayıp: {round(estimated_loss, 2)} TL",
        ],
        "recommended_action": f"%{discount} indirim + WhatsApp kampanyası + raf önü konumlandırma",
        "expected_result": (
            f"Yaklaşık {round(product.get('expected_units_saved', 0), 1)} adet ürün satılabilir "
            f"ve {round(preventable_loss, 2)} TL kayıp önlenebilir."
        ),
        "confidence_score": confidence_score,
        "data_quality": data_quality,
        "confidence_reason": confidence_reason,
    }


def compare_actions(product: dict[str, Any]) -> dict[str, Any]:
    action_definitions = [
        ("no_action", 0.0, "Yok", "Aksiyon yok"),
        ("small_discount_sms", 0.15, "SMS", "%15 indirim + SMS"),
        ("medium_discount_whatsapp", 0.25, "WhatsApp", "%25 indirim + WhatsApp"),
        ("aggressive_discount_whatsapp", 0.35, "WhatsApp", "%35 indirim + WhatsApp"),
        ("bundle_campaign", 0.20, "WhatsApp", "%20 indirim + bundle"),
        ("local_delivery_push", 0.20, "Push", "%20 indirim + yakın bölge teslimat mesajı"),
    ]

    comparison = []
    for action_key, discount_rate, channel, action_name in action_definitions:
        if action_key == "no_action":
            no_action_loss = _as_float(product.get("estimated_loss"))
            result = {
                "action_name": action_name,
                "action_key": action_key,
                "discount_rate": 0,
                "channel": channel,
                "expected_units_sold": 0,
                "prevented_loss": 0,
                "incremental_revenue": 0,
                "gross_margin": 0,
                "remaining_loss": round(no_action_loss, 2),
                "loss_reduction_percent": 0,
                "net_impact": 0,
                "operation_cost": 0,
                "confidence": 92,
                "why_this_action": "Baz senaryo olarak referans alınır; operasyonel maliyet yoktur.",
                "hard_constraint_applied": False,
                "constraint_reason": "",
                "pros": ["Ek operasyon gerekmez", "İndirim maliyeti oluşmaz"],
                "cons": ["Fire riski devam eder", "Müşteri talebi tetiklenmez"],
            }
        else:
            simulation = simulate_action(product, discount_rate, channel)
            hard_constraint_applied = bool(simulation.get("hard_constrained"))
            why_this_action = _action_why_text(action_key, simulation)
            confidence = _action_confidence(product, simulation, action_key)
            result = {
                "action_name": action_name,
                "action_key": action_key,
                "discount_rate": discount_rate,
                "channel": channel,
                "expected_units_sold": simulation["with_action"]["expected_units_sold"],
                "prevented_loss": simulation["impact"]["prevented_loss"],
                "incremental_revenue": simulation["with_action"]["incremental_revenue"],
                "gross_margin": simulation["with_action"]["gross_margin"],
                "remaining_loss": simulation["with_action"]["remaining_loss"],
                "loss_reduction_percent": simulation["impact"]["loss_reduction_percent"],
                "net_impact": simulation["impact"]["net_impact"],
                "operation_cost": simulation["impact"].get("operation_cost", 0),
                "confidence": confidence,
                "why_this_action": why_this_action,
                "hard_constraint_applied": hard_constraint_applied,
                "constraint_reason": simulation.get("constraint_reason", ""),
                "recommended_safe_procedure": simulation.get("recommended_safe_procedure", ""),
                "pros": _action_pros(action_key),
                "cons": _action_cons(action_key),
            }
        comparison.append(result)

    best_action = max(
        comparison,
        key=lambda item: (item["net_impact"], item["loss_reduction_percent"]),
    )

    return {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "best_action": best_action["action_key"],
        "best_action_label": best_action["action_name"],
        "comparison": comparison,
    }


def _action_why_text(action_key: str, simulation: dict[str, Any]) -> str:
    if simulation.get("hard_constrained"):
        return "Gıda güvenliği kuralı nedeniyle agresif kampanya yerine güvenli prosedür zorunlu."
    net = _as_float(simulation.get("impact", {}).get("net_impact"))
    reduced = _as_float(simulation.get("impact", {}).get("loss_reduction_percent"))
    operation_cost = _as_float(simulation.get("impact", {}).get("operation_cost"))
    return (
        f"Beklenen net etki {round(net, 2)} TL, kayıp azaltımı %{round(reduced, 1)} "
        f"ve operasyon maliyeti {round(operation_cost, 2)} TL."
    )


def _action_confidence(product: dict[str, Any], simulation: dict[str, Any], action_key: str) -> int:
    if simulation.get("hard_constrained"):
        return 98
    base = 60
    risk_score = _as_float(product.get("risk_score"))
    loss_reduction = _as_float(simulation.get("impact", {}).get("loss_reduction_percent"))
    net_impact = _as_float(simulation.get("impact", {}).get("net_impact"))
    if risk_score >= 75:
        base += 8
    if loss_reduction >= 35:
        base += 10
    if net_impact >= 1000:
        base += 8
    if action_key in {"bundle_campaign", "local_delivery_push"}:
        base -= 4
    return int(max(52, min(96, round(base))))


def _action_pros(action_key: str) -> list[str]:
    pros = {
        "small_discount_sms": ["Hızlı uygulanır", "Düşük indirimle marj korunur"],
        "medium_discount_whatsapp": ["Müşteri erişimi güçlüdür", "İndirim dengelidir"],
        "aggressive_discount_whatsapp": ["Fireyi hızlı azaltır", "Acil ürünler için etkilidir"],
        "bundle_campaign": ["Sepet tutarını artırabilir", "Yan ürün satışını destekler"],
        "local_delivery_push": ["Yakın müşteriyi hızlı tetikler", "Bugün teslimat algısı yaratır"],
    }
    return pros.get(action_key, [])


def _action_cons(action_key: str) -> list[str]:
    cons = {
        "small_discount_sms": ["Acil ürünlerde yavaş kalabilir"],
        "medium_discount_whatsapp": ["Mesaj listesi doğru seçilmeli"],
        "aggressive_discount_whatsapp": ["Birim marj düşer"],
        "bundle_campaign": ["Raf ve kasa ekibi hazırlık yapmalı"],
        "local_delivery_push": ["Teslimat kapasitesi kontrol edilmeli"],
    }
    return cons.get(action_key, [])


def build_rescue_playbook(product: dict[str, Any]) -> dict[str, Any]:
    category = str(product.get("category", "")).lower()
    name = product.get("name")

    if "meyve" in category:
        playbook = {
            "primary_playbook": f"{name} ürününü kahvaltı sepetine ek ürün olarak öner.",
            "secondary_playbook": "Yakın bölgedeki sağlıklı yaşam müşterilerine smoothie paketi öner.",
            "emergency_playbook": "Gün sonuna kadar satılmazsa reçel üretimi veya bağış kanalına yönlendir.",
            "suggested_bundle": f"{name} + yoğurt + granola kahvaltı paketi",
            "ideal_customer_segment": "healthy_living ve discount_sensitive",
            "best_channel": "WhatsApp",
            "message_angle": "Taze ürün, bugün teslimat ve sınırlı stok vurgusu",
        }
    elif "sebze" in category:
        playbook = {
            "primary_playbook": f"{name} ile günlük salata paketi oluştur.",
            "secondary_playbook": "Restoran veya toplu alım yapan müşterilere özel fiyat öner.",
            "emergency_playbook": "Gün sonunda taze sepet veya bağış kanalına yönlendir.",
            "suggested_bundle": f"{name} + yeşillik + sos salata paketi",
            "ideal_customer_segment": "family ve healthy_living",
            "best_channel": "WhatsApp",
            "message_angle": "Bugün taze, pratik yemek hazırlığı ve avantajlı paket",
        }
    elif "süt" in category or "kahvaltılık" in category:
        playbook = {
            "primary_playbook": "Kahvaltı bundle kampanyasına dahil et.",
            "secondary_playbook": "Aile müşterilerine 2 al 1 indirim mesajı gönder.",
            "emergency_playbook": "Gün sonunda personel satışı veya bağış seçeneğini hazırla.",
            "suggested_bundle": f"{name} + yumurta + ekmek kahvaltı paketi",
            "ideal_customer_segment": "family ve loyal",
            "best_channel": "SMS",
            "message_angle": "Aile kahvaltısı, taze ürün ve bugün avantajı",
        }
    elif "et" in category or "tavuk" in category or "balık" in category:
        expiry_days = _as_int(product.get("expiry_days_left"))
        emergency = (
            "Güvenli tüketim süresi içindeyse gün sonu hızlı satış yap; süre aşılırsa satış önerme ve imha/bağış prosedürünü uygula."
            if expiry_days <= 1
            else "Güvenli saklama uyarısıyla gün sonu hızlı teslimat kampanyası yap."
        )
        playbook = {
            "primary_playbook": "Bugün tüketim vurgusuyla hızlı indirim uygula.",
            "secondary_playbook": "Restoran/toplu alım müşterilerine özel teklif hazırla.",
            "emergency_playbook": emergency,
            "suggested_bundle": f"{name} + salata + içecek akşam yemeği paketi",
            "ideal_customer_segment": "premium ve nearby",
            "best_channel": "WhatsApp",
            "message_angle": "Bugün tüketim, güvenli saklama ve hızlı teslimat",
        }
    elif "fırın" in category:
        playbook = {
            "primary_playbook": "Gün sonu paketi olarak konumlandır.",
            "secondary_playbook": "Kafe/restoran müşterilerine toplu paket öner.",
            "emergency_playbook": "Kapanışa yakın bağış veya personel satış kanalına yönlendir.",
            "suggested_bundle": f"{name} + kahve/çay gün sonu paketi",
            "ideal_customer_segment": "discount_sensitive ve nearby",
            "best_channel": "Push",
            "message_angle": "Gün sonu fırsatı ve sınırlı stok",
        }
    else:
        playbook = {
            "primary_playbook": "Ürünü görünür rafa al ve kısa süreli indirim uygula.",
            "secondary_playbook": "Sadakat müşterilerine hedefli mesaj gönder.",
            "emergency_playbook": "Gün sonunda bağış veya bundle kanalına yönlendir.",
            "suggested_bundle": f"{name} + tamamlayıcı ürün paketi",
            "ideal_customer_segment": "loyal ve discount_sensitive",
            "best_channel": "SMS",
            "message_angle": "Bugüne özel avantaj ve sınırlı stok",
        }

    donation_options = {
        "meyve": "Reçel/smoothie üretimi veya uygun bağış kanalı",
        "sebze": "Salata paketi, restoran/toplu alım veya uygun bağış kanalı",
        "süt": "Kahvaltı paketi, personel satışı veya uygun bağış kanalı",
        "fırın": "Gün sonu paketi, kafe satışı veya uygun bağış kanalı",
        "et": "Sadece güvenli tüketim süresi içindeyse hızlı satış; aksi halde satış önerme",
        "balık": "Sadece güvenli tüketim süresi içindeyse hızlı satış; aksi halde satış önerme",
    }
    secondary_use = "Uygun bağış veya ikincil kullanım kanalını değerlendir."
    for key, value in donation_options.items():
        if key in category:
            secondary_use = value
            break

    return {
        "product_id": product.get("product_id"),
        "product_name": name,
        "donation_or_secondary_use": secondary_use,
        **playbook,
    }


def match_customer_segments(product: dict[str, Any], customers: list[dict[str, Any]]) -> dict[str, Any]:
    category = str(product.get("category", "")).lower()
    target_segments = _segments_for_category(category)
    target_customers = []

    for customer in customers:
        segment = str(customer.get("segment", ""))
        tags = str(customer.get("interest_tags", "")).lower()
        region = str(customer.get("region", ""))
        if segment in target_segments or any(tag in tags for tag in _tags_for_category(category)):
            channel = customer.get("preferred_channel", "SMS")
            target_customers.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "customer_name": customer.get("name"),
                    "segment": segment,
                    "region": region,
                    "reason": _customer_reason(customer, product),
                    "channel": channel,
                    "message": _personalized_message(customer, product),
                }
            )

    target_customers = sorted(
        target_customers,
        key=lambda item: _as_float(
            next(
                (customer.get("previous_purchase_count") for customer in customers if customer.get("customer_id") == item["customer_id"]),
                0,
            )
        ),
        reverse=True,
    )[:5]

    return {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "target_segments": target_segments,
        "target_customers": target_customers,
        "reason": "Ürün kategorisi, müşteri segmenti, ilgi etiketleri ve tercih edilen kanal birlikte değerlendirildi.",
        "suggested_channel": target_customers[0]["channel"] if target_customers else "SMS",
        "personalized_message": target_customers[0]["message"] if target_customers else "",
    }


def _segments_for_category(category: str) -> list[str]:
    if "meyve" in category or "sebze" in category:
        return [
            "healthy_living",
            "discount_sensitive",
            "nearby",
            "freshness_intent",
            "cooperative_member",
            "bulk_buyer",
        ]
    if "süt" in category or "kahvaltılık" in category:
        return [
            "family",
            "loyal",
            "discount_sensitive",
            "freshness_intent",
            "cooperative_member",
            "cafe_owner",
        ]
    if "et" in category or "tavuk" in category or "balık" in category:
        return ["premium", "family", "nearby", "freshness_intent", "bulk_buyer", "cafe_owner"]
    if "fırın" in category:
        return ["nearby", "discount_sensitive", "loyal", "cafe_owner", "bulk_buyer"]
    if "hazır" in category:
        return ["discount_sensitive", "nearby", "family", "cafe_owner", "bulk_buyer"]
    if "kooperatif" in category:
        return ["cooperative_member", "loyal", "healthy_living", "freshness_intent"]
    return ["loyal", "discount_sensitive", "nearby", "freshness_intent"]


def _tags_for_category(category: str) -> list[str]:
    if "meyve" in category:
        return ["meyve", "smoothie", "healthy", "sağlıklı"]
    if "sebze" in category:
        return ["sebze", "salata", "healthy", "vegan"]
    if "süt" in category:
        return ["kahvaltı", "süt", "yoğurt", "peynir"]
    if "et" in category or "tavuk" in category or "balık" in category:
        return ["et", "protein", "akşam", "balık"]
    return ["indirim", "fırsat"]


def _customer_reason(customer: dict[str, Any], product: dict[str, Any]) -> str:
    return (
        f"{customer.get('segment')} segmentinde, {customer.get('region')} bölgesinde "
        f"ve {customer.get('previous_purchase_count')} geçmiş alışveriş kaydı var."
    )


def _personalized_message(customer: dict[str, Any], product: dict[str, Any]) -> str:
    discount = _discount_percent(product)
    first_name = str(customer.get("name", "Merhaba")).split()[0]
    return (
        f"Merhaba {first_name}, bugün {product.get('name')} için %{discount} özel fırsat var. "
        "Taze ürün, sınırlı stok ve bugün teslim/alım avantajını kaçırmayın."
    )


def build_before_after_impact(risk_items: list[dict[str, Any]]) -> dict[str, Any]:
    before_ai_estimated_loss = sum(_as_float(item.get("estimated_loss")) for item in risk_items)
    preventable_loss = sum(_as_float(item.get("preventable_loss")) for item in risk_items)
    preventable_waste_kg = sum(_as_float(item.get("preventable_waste_kg")) for item in risk_items)
    preventable_co2_kg = sum(_as_float(item.get("preventable_co2_kg")) for item in risk_items)
    rescued_product_count = sum(1 for item in risk_items if _as_float(item.get("preventable_loss")) > 0)
    after_ai_remaining_loss = max(before_ai_estimated_loss - preventable_loss, 0)

    return {
        "before_ai_estimated_loss": round(before_ai_estimated_loss, 2),
        "after_ai_remaining_loss": round(after_ai_remaining_loss, 2),
        "preventable_loss": round(preventable_loss, 2),
        "preventable_waste_kg": round(preventable_waste_kg, 2),
        "preventable_co2_kg": round(preventable_co2_kg, 2),
        "rescued_product_count": rescued_product_count,
        "one_sentence_impact": (
            f"FireRadar AI bugün {round(preventable_loss, 2)} TL kaybı, "
            f"{round(preventable_waste_kg, 2)} kg gıda firesini ve "
            f"{round(preventable_co2_kg, 2)} kg CO₂ etkisini önleyebilir."
        ),
    }
