from __future__ import annotations

from math import ceil
from typing import Any, Optional


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_agent_activity(summary: dict[str, Any], risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_item = risk_items[0] if risk_items else {}
    return [
        {
            "title": "Stok ve son tüketim tarihlerini okudu",
            "detail": f"{summary.get('total_products', 0)} ürünün stok, maliyet, fiyat ve son tüketim tarihini kontrol etti.",
            "status": "done",
        },
        {
            "title": "Son 10 günlük satış hızını hesapladı",
            "detail": "CSV satış geçmişinden her ürünün günlük satış hızını çıkardı.",
            "status": "done",
        },
        {
            "title": "Fire riskini ve TL kaybını çıkardı",
            "detail": f"Bugün önce bakılması gereken {summary.get('high_risk_product_count', 0)} ürün ve {summary.get('total_estimated_loss', 0)} TL fire maliyeti buldu.",
            "status": "done",
        },
        {
            "title": "6 farklı aksiyonu simüle etti",
            "detail": "Aksiyon yok, SMS indirimi, WhatsApp indirimi, agresif indirim, bundle ve yakın bölge mesajını karşılaştırdı.",
            "status": "done",
        },
        {
            "title": "En yüksek net etkiye sahip aksiyonu seçti",
            "detail": (
                f"Önce {top_item.get('name', 'en riskli ürün')} için indirim, görünür raf ve müşteri mesajı öneriyor."
            ),
            "status": "done",
        },
        {
            "title": "Hedef müşteri segmentini belirledi",
            "detail": "Müşteri segmenti, ilgi etiketleri, bölge ve kanal tercihini birlikte kullandı.",
            "status": "done",
        },
        {
            "title": "Kampanya ve tedarikçi mesajlarını hazırladı",
            "detail": "Müşteri mesajı ve siparişi azaltma/artırma kararını operasyona hazır hale getirdi.",
            "status": "done",
        },
    ]


def build_daily_work_plan(risk_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for index, item in enumerate(risk_items[:5], start=1):
        discount = int(_as_float(item.get("discount_recommendation")) * 100)
        expiry_days = int(_as_float(item.get("expiry_days_left")))
        urgency = "Hemen şimdi" if expiry_days <= 2 else "Bugün içinde"

        plan.append(
            {
                "order": index,
                "product_id": item.get("product_id"),
                "product_name": item.get("name"),
                "urgency": urgency,
                "task": f"{item.get('name')} ürününü görünür rafa al ve %{discount} indirim etiketi koy.",
                "customer_action": "Uygun müşterilere kısa kampanya mesajı gönder.",
                "why": (
                    f"{expiry_days} gün kaldı; yaklaşık {item.get('preventable_loss')} TL kayıp kurtarılabilir."
                ),
            }
        )

    return plan


def build_supplier_decision(product: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not product:
        return {
            "supplier_action_type": "no_product",
            "recommended_quantity_change": 0,
            "reason": "Ürün seçilmedi.",
            "email_subject": "Sipariş kararı oluşturulamadı",
            "email_body": "Ürün seçilmediği için tedarikçi mesajı hazırlanamadı.",
        }

    daily_velocity = _as_float(product.get("daily_sales_velocity"), 1)
    stock_quantity = _as_float(product.get("stock_quantity"))
    min_stock_threshold = _as_float(product.get("min_stock_threshold"), daily_velocity * 3)
    risky_quantity = _as_float(product.get("risky_quantity"))
    risk_score = _as_float(product.get("risk_score"))
    supplier = product.get("supplier", "Tedarikçi")
    name = product.get("name", "ürün")

    if risk_score >= 55 and risky_quantity > max(daily_velocity * 2, 4):
        quantity_change = -max(ceil(risky_quantity * 0.5), 1)
        action_type = "reduce_or_delay_order"
        reason = "Stok fazlası ve yakın tarihli fire riski görünüyor; yeni siparişi azaltmak veya ertelemek daha güvenli."
        subject = f"{name} siparişini azaltma/erteleme talebi"
        body = (
            f"Merhaba {supplier},\n\n"
            f"{name} ürünü için bu hafta satış hızı beklenenin altında kaldı ve mevcut stokta fire riski oluştu. "
            "Bu nedenle planlanan yeni siparişi azaltmak veya bir sonraki teslimata ertelemek istiyoruz.\n\n"
            f"Önerilen değişiklik: {abs(quantity_change)} adet azaltma/erteleme.\n\n"
            "Uygunluk durumunuzu paylaşabilir misiniz?\n\n"
            "Teşekkürler."
        )
    elif stock_quantity <= min_stock_threshold and daily_velocity >= max(min_stock_threshold / 3, 1):
        quantity_change = max(ceil(daily_velocity * 7 - stock_quantity), 5)
        action_type = "increase_order"
        reason = "Stok düşük ve satış hızı güçlü; ek sipariş stok dışı kalma riskini azaltır."
        subject = f"{name} için ek sipariş talebi"
        body = (
            f"Merhaba {supplier},\n\n"
            f"{name} ürününde talep güçlü ve mevcut stok minimum seviyeye yaklaştı. "
            f"Bu nedenle {quantity_change} adet ek sipariş geçmek istiyoruz.\n\n"
            "En yakın teslimat tarihi ve güncel birim fiyat bilgisini paylaşabilir misiniz?\n\n"
            "Teşekkürler."
        )
    else:
        quantity_change = 0
        action_type = "keep_order"
        reason = "Stok ve satış hızı dengeli; siparişte büyük değişiklik gerekmiyor."
        subject = f"{name} sipariş planı bilgilendirme"
        body = (
            f"Merhaba {supplier},\n\n"
            f"{name} ürünü için mevcut stok ve satış hızı şu anda dengeli görünüyor. "
            "Bu hafta sipariş planında değişiklik yapmadan devam etmeyi düşünüyoruz.\n\n"
            "Teslimat planında değişiklik varsa bilgi verebilir misiniz?\n\n"
            "Teşekkürler."
        )

    return {
        "supplier": supplier,
        "product_id": product.get("product_id"),
        "product_name": name,
        "supplier_action_type": action_type,
        "recommended_quantity_change": quantity_change,
        "reason": reason,
        "email_subject": subject,
        "email_body": body,
        "subject": subject,
        "body": body,
        "recommended_quantity": abs(quantity_change),
    }


def build_supplier_order(product: Optional[dict[str, Any]]) -> dict[str, Any]:
    return build_supplier_decision(product)
