from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional
from urllib import error as urllib_error
from urllib import request as urllib_request
import json


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        origins.append(frontend_url.rstrip("/"))
    return origins


def _parse_cors_origin_regex() -> Optional[str]:
    raw = os.getenv("CORS_ORIGIN_REGEX", "").strip()
    if raw:
        return raw
    return r"^https://.*\.netlify\.app$"


def _normalize_campaign_channel(raw: Optional[str]) -> str:
    base = str(raw or "SMS").strip()
    c = base.lower().replace(" ", "")
    if c in {"sms", "text"}:
        return "SMS"
    if c in {"whatsapp", "wa"}:
        return "WhatsApp"
    if c in {"email", "eposta", "e-posta", "e‑posta"} or "posta" in c:
        return "E-posta"
    return base or "SMS"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.ai_service import (
    AIService,
    build_action_plan_prompt,
    build_campaign_prompt,
    build_chat_prompt,
    build_daily_summary_prompt,
    build_demo_pitch_prompt,
    build_supplier_order_prompt,
)
from services.agent_service import (
    build_before_after_impact,
    build_decision_explanation,
    build_rescue_playbook,
    compare_actions,
    match_customer_segments,
)
from services.data_loader import load_all_data, today_iso
from services.insights_service import (
    build_operations_snapshot,
    build_recommendation_evidence_facts,
    enrich_supplier_decision,
)
from services.operations_service import (
    build_agent_activity,
    build_daily_work_plan,
    build_supplier_decision,
    build_supplier_order,
)
from services.risk_engine import (
    analyze_inventory_risk,
    build_category_breakdown,
    build_priority_actions,
    build_risk_summary,
    get_high_risk_products,
)
from services.simulation_engine import (
    build_category_heatmap,
    build_executive_dashboard,
    build_impact_report,
    simulate_action,
)
from services.action_log_store import ActionLogStore


app = FastAPI(title="FireRadar AI API", version="1.0.0")
ai_service = AIService()
DEMO_PRODUCT_ID = os.getenv("DEMO_PRODUCT_ID", "P001")
ACTION_LOG_DB_PATH = Path(__file__).resolve().parent / "data" / "action_logs.db"
action_log_store = ActionLogStore(ACTION_LOG_DB_PATH)
ALLOWED_CORS_ORIGINS = _parse_cors_origins()
ALLOWED_CORS_REGEX = _parse_cors_origin_regex()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_origin_regex=ALLOWED_CORS_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductRequest(BaseModel):
    product_id: Optional[str] = None


class CampaignRequest(BaseModel):
    product_id: Optional[str] = None
    channel: str = "SMS"
    tone: str = "friendly"


class AskAIRequest(BaseModel):
    question: str
    product_id: Optional[str] = None


class SimulationRequest(BaseModel):
    product_id: Optional[str] = None
    discount_rate: float = 0.25
    channel: str = "SMS"


class ActionLogRequest(BaseModel):
    action_type: str = Field(min_length=1)
    message: str = Field(min_length=1)
    product_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class RunAgentRequest(BaseModel):
    log_actions: bool = True


class WebhookDispatchRequest(BaseModel):
    webhook_url: str = Field(min_length=8)
    product_id: Optional[str] = None
    event_type: str = "campaign_dispatch"


def _risk_context() -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    summary = build_risk_summary(risk_items)
    high_risk_products = get_high_risk_products(risk_items)
    return risk_items, summary, high_risk_products


def _select_product(risk_items: list[dict[str, Any]], product_id: Optional[str]) -> Optional[dict[str, Any]]:
    if product_id:
        return next((item for item in risk_items if str(item.get("product_id")) == product_id), None)
    return risk_items[0] if risk_items else None


def _require_product(risk_items: list[dict[str, Any]], product_id: Optional[str]) -> dict[str, Any]:
    product = _select_product(risk_items, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    return product


def _log_action(
    action_type: str,
    message: str,
    product_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    status: str = "completed",
) -> dict[str, Any]:
    return action_log_store.create(
        action_type=action_type,
        message=message,
        product_id=product_id,
        metadata=metadata,
        status=status,
    )


def _dispatch_webhook(url: str, payload: dict[str, Any], timeout_seconds: float = 8.0) -> tuple[bool, str]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        url=url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib_request.urlopen(req, timeout=max(timeout_seconds, 1.0)) as response:
            code = int(getattr(response, "status", 0) or 0)
            if 200 <= code < 300:
                return True, f"Webhook teslim edildi (HTTP {code})."
            return False, f"Webhook yanıtı başarısız (HTTP {code})."
    except urllib_error.HTTPError as exc:
        return False, f"Webhook HTTP hatası: {exc.code}"
    except urllib_error.URLError as exc:
        return False, f"Webhook bağlantı hatası: {exc.reason}"
    except Exception:
        return False, "Webhook gönderimi beklenmedik bir hata verdi."


async def _run_agent_internal(product_id: str, log_actions: bool) -> dict[str, Any]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    summary = build_risk_summary(risk_items)
    product = _require_product(risk_items, product_id)

    decision = build_decision_explanation(product)
    comparison = compare_actions(product)
    segments = match_customer_segments(product, data["customers"])

    best_action = next(
        (item for item in comparison.get("comparison", []) if item.get("action_key") == comparison.get("best_action")),
        {},
    )

    campaign_channel = segments.get("suggested_channel", "SMS")
    campaign_prompt = build_campaign_prompt(product, channel=campaign_channel, tone="samimi")
    campaign_message = await ai_service.complete(campaign_prompt)

    supplier_base = build_supplier_order(product)
    supplier_enriched = enrich_supplier_decision(product, {**supplier_base})
    supplier_prompt = build_supplier_order_prompt(product, supplier_enriched)
    supplier_body = await ai_service.complete(supplier_prompt)
    supplier_email = {
        **supplier_enriched,
        "body": supplier_body or supplier_enriched.get("body"),
    }

    logs: list[dict[str, Any]] = []
    if log_actions:
        logs = [
            _log_action(
                action_type="high_risk_flagged",
                product_id=product.get("product_id"),
                message="Yüksek riskli ürün işaretlendi",
                metadata={
                    "product_name": product.get("name"),
                    "risk_score": product.get("risk_score"),
                    "risk_level": product.get("risk_level"),
                },
            ),
            _log_action(
                action_type="discount_action_suggested",
                product_id=product.get("product_id"),
                message="İndirim aksiyonu önerildi",
                metadata={
                    "discount_rate": best_action.get("discount_rate"),
                    "channel": best_action.get("channel"),
                    "best_action": best_action.get("action_name"),
                },
            ),
            _log_action(
                action_type="campaign_message_generated",
                product_id=product.get("product_id"),
                message="Kampanya mesajı oluşturuldu",
                metadata={
                    "channel": campaign_channel,
                },
            ),
            _log_action(
                action_type="supplier_mail_prepared",
                product_id=product.get("product_id"),
                message="Tedarikçi maili hazırlandı",
                metadata={
                    "supplier": supplier_email.get("supplier"),
                    "subject": supplier_email.get("email_subject"),
                },
            ),
        ]

    return {
        "date": today_iso(),
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "positioning": "Risk motoru + simülasyon motoru + LLM destekli operasyon ajanı",
        "demo_product_id": DEMO_PRODUCT_ID,
        "logs_written": log_actions,
        "product_risk_analysis": {
            "product_id": product.get("product_id"),
            "product_name": product.get("name"),
            "risk_level": product.get("risk_level"),
            "risk_score": product.get("risk_score"),
            "expiry_days_left": product.get("expiry_days_left"),
            "stock_quantity": product.get("stock_quantity"),
            "daily_sales_velocity": product.get("daily_sales_velocity"),
        },
        "loss_estimation": {
            "estimated_loss": product.get("estimated_loss"),
            "estimated_revenue_at_risk": product.get("estimated_revenue_at_risk"),
            "preventable_loss": product.get("preventable_loss"),
            "summary_total_estimated_loss": summary.get("total_estimated_loss"),
        },
        "action_comparison": comparison,
        "best_action_recommendation": {
            "action_key": best_action.get("action_key"),
            "action_name": best_action.get("action_name"),
            "channel": best_action.get("channel"),
            "discount_rate": best_action.get("discount_rate"),
            "net_impact": best_action.get("net_impact"),
            "operation_cost": best_action.get("operation_cost"),
            "loss_reduction_percent": best_action.get("loss_reduction_percent"),
            "confidence": best_action.get("confidence"),
            "why_this_action": best_action.get("why_this_action"),
            "hard_constraint_applied": best_action.get("hard_constraint_applied", False),
            "constraint_reason": best_action.get("constraint_reason", ""),
            "recommended_safe_procedure": best_action.get("recommended_safe_procedure", ""),
        },
        "customer_segment": {
            "target_segments": segments.get("target_segments"),
            "target_customers": segments.get("target_customers", [])[:3],
            "reason": segments.get("reason"),
        },
        "campaign_message": campaign_message,
        "supplier_email_draft": {
            "subject": supplier_email.get("email_subject"),
            "body": supplier_email.get("body"),
            "recommended_quantity_change": supplier_email.get("recommended_quantity_change"),
            "reason": supplier_email.get("reason"),
        },
        "agent_explanation": (
            f"{product.get('name')} için risk motoru fire olasılığını ve kayıp miktarını hesapladı, "
            "simülasyon motoru aksiyonları karşılaştırdı, LLM katmanı kampanya ve tedarikçi iletişimini hazırladı."
        ),
        "assumptions": [
            "Kampanya operasyon maliyeti kanal bazlı sabit varsayılır (SMS: 80 TL, WhatsApp: 120 TL, E-posta: 60 TL, Push: 40 TL).",
            "Satış hızı son dönem satış geçmişinden hesaplanan günlük ortalamadır.",
            "Aksiyon etki penceresi ürün SKT süresine bağlı olarak en fazla 3 gün kabul edilir.",
            "Et/balık kategorisinde SKT'ye 0 gün kalan ürünlerde agresif kampanya gıda güvenliği nedeniyle kısıtlanır.",
        ],
        "action_logs": logs,
        "decision_explanation": decision,
    }


@app.get("/")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "FireRadar AI API",
        "positioning": "Risk motoru + simülasyon motoru + LLM destekli operasyon ajanı",
        "ai_provider": ai_service.provider,
        "ai_external_ready": ai_service.has_external_provider,
        "demo_product_id": DEMO_PRODUCT_ID,
        "recommended_llm_note": (
            "YZTA için Gemini kullanılabilir: AI_PROVIDER=gemini ve GEMINI_API_KEY veya OPENAI ile devam."
        ),
    }


@app.post("/actions/log")
def create_action_log(request: ActionLogRequest) -> dict[str, Any]:
    entry = _log_action(
        action_type=request.action_type,
        message=request.message,
        product_id=request.product_id,
        metadata=request.metadata,
    )
    return {
        "status": "ok",
        "log": entry,
    }


@app.get("/actions/log")
def get_action_logs(limit: int = 50) -> dict[str, Any]:
    return {
        "items": action_log_store.list(limit=limit),
        "total": action_log_store.count(),
    }


@app.get("/operations-snapshot")
def get_operations_snapshot() -> dict[str, Any]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    return build_operations_snapshot(data, risk_items, today_iso())


@app.get("/recommendation-evidence/{product_id}")
def get_recommendation_evidence(product_id: str) -> dict[str, Any]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    product = _require_product(risk_items, product_id)
    return build_recommendation_evidence_facts(product, data)


@app.get("/inventory")
def get_inventory() -> dict[str, Any]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    return {
        "date": today_iso(),
        "items": risk_items,
    }


@app.get("/risk-analysis")
def get_risk_analysis() -> dict[str, Any]:
    risk_items, summary, _ = _risk_context()
    return {
        "date": today_iso(),
        "summary": summary,
        "items": risk_items,
        "category_breakdown": build_category_breakdown(risk_items),
        "priority_actions": build_priority_actions(risk_items),
    }


@app.get("/daily-summary")
async def get_daily_summary() -> dict[str, Any]:
    _, summary, high_risk_products = _risk_context()
    prompt = build_daily_summary_prompt(summary, high_risk_products)
    ai_summary = await ai_service.complete(prompt)
    return {
        "date": today_iso(),
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "summary": summary,
        "message": ai_summary,
    }


@app.get("/high-risk-products")
def high_risk_products() -> dict[str, Any]:
    _, _, high_risk_items = _risk_context()
    return {
        "date": today_iso(),
        "items": high_risk_items,
    }


@app.get("/executive-dashboard")
def get_executive_dashboard() -> dict[str, Any]:
    risk_items, summary, _ = _risk_context()
    category_breakdown = build_category_breakdown(risk_items)
    priority_actions = build_priority_actions(risk_items)
    return {
        "date": today_iso(),
        "dashboard": build_executive_dashboard(
            risk_items,
            summary,
            category_breakdown,
            priority_actions,
        ),
        "category_heatmap": build_category_heatmap(risk_items),
        "agent_activity": build_agent_activity(summary, risk_items),
        "daily_work_plan": build_daily_work_plan(risk_items),
    }


@app.get("/agent-activity")
def get_agent_activity() -> dict[str, Any]:
    risk_items, summary, _ = _risk_context()
    return {
        "date": today_iso(),
        "steps": build_agent_activity(summary, risk_items),
    }


@app.get("/daily-work-plan")
def get_daily_work_plan() -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    return {
        "date": today_iso(),
        "items": build_daily_work_plan(risk_items),
    }


@app.post("/simulate-action")
def simulate_product_action(request: SimulationRequest) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _require_product(risk_items, request.product_id)

    ch_raw = (request.channel or "SMS").strip()
    lc = ch_raw.lower()
    if lc in {"email", "e-posta", "eposta"}:
        ch = "E-posta"
    elif lc == "whatsapp":
        ch = "WhatsApp"
    elif lc == "sms":
        ch = "SMS"
    elif lc == "push":
        ch = "Push"
    else:
        ch = ch_raw
    return simulate_action(product, request.discount_rate, ch)


@app.get("/decision-explanation/{product_id}")
def get_decision_explanation(product_id: str) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _require_product(risk_items, product_id)
    return build_decision_explanation(product)


@app.get("/action-comparison/{product_id}")
def get_action_comparison(product_id: str) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _require_product(risk_items, product_id)
    return compare_actions(product)


@app.get("/rescue-playbook/{product_id}")
def get_rescue_playbook(product_id: str) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _require_product(risk_items, product_id)
    return build_rescue_playbook(product)


@app.get("/segment-matches/{product_id}")
def get_segment_matches(product_id: str) -> dict[str, Any]:
    data = load_all_data()
    risk_items = analyze_inventory_risk(data["products"], data["sales_history"])
    product = _require_product(risk_items, product_id)
    return match_customer_segments(product, data["customers"])


@app.get("/before-after-impact")
def get_before_after_impact() -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    return {
        "date": today_iso(),
        "impact": build_before_after_impact(risk_items),
    }


@app.post("/generate-supplier-order")
async def generate_supplier_order(request: ProductRequest) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _select_product(risk_items, request.product_id)
    base = build_supplier_order(product)
    draft = enrich_supplier_decision(product, {**base}) if product else base
    prompt = build_supplier_order_prompt(product, draft)
    ai_body = await ai_service.complete(prompt)

    return {
        "product": product,
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "supplier_order": {
            **draft,
            "body": ai_body or draft.get("body"),
        },
    }


@app.get("/supplier-decision/{product_id}")
def get_supplier_decision(product_id: str) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _require_product(risk_items, product_id)
    return enrich_supplier_decision(product, build_supplier_decision(product))


@app.get("/impact-report")
def get_impact_report() -> dict[str, Any]:
    risk_items, summary, _ = _risk_context()
    return {
        "date": today_iso(),
        "impact_report": build_impact_report(risk_items, summary),
    }


@app.post("/generate-action-plan")
async def generate_action_plan(request: ProductRequest) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _select_product(risk_items, request.product_id)
    prompt = build_action_plan_prompt(product)
    plan = await ai_service.complete(prompt)
    return {
        "product": product,
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "action_plan": plan,
    }


@app.post("/generate-campaign-message")
async def generate_campaign_message(request: CampaignRequest) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _select_product(risk_items, request.product_id)
    channel = _normalize_campaign_channel(request.channel)
    prompt = build_campaign_prompt(product, channel=channel, tone=request.tone)
    message = await ai_service.complete(prompt)
    return {
        "product": product,
        "channel": channel,
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "campaign_message": message,
    }


@app.post("/ask-ai")
async def ask_ai(request: AskAIRequest) -> dict[str, Any]:
    risk_items, summary, high_risk_products = _risk_context()
    # Chatbot is intentionally pinned to the demo product context for a consistent hackathon flow.
    selected_product = _select_product(risk_items, DEMO_PRODUCT_ID)
    prompt = build_chat_prompt(
        request.question,
        summary,
        high_risk_products,
        selected_product=selected_product,
    )
    answer = await ai_service.complete(prompt)
    return {
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "answer": answer,
        "context_product_id": selected_product.get("product_id") if selected_product else None,
    }


@app.post("/generate-demo-pitch")
async def generate_demo_pitch() -> dict[str, Any]:
    risk_items, summary, high_risk_products = _risk_context()
    impact_report = build_impact_report(risk_items, summary)
    prompt = build_demo_pitch_prompt(summary, high_risk_products, impact_report)
    pitch = await ai_service.complete(prompt)
    return {
        "provider": ai_service.provider if ai_service.has_external_provider else "fallback",
        "pitch": pitch,
        "impact_report": impact_report,
    }


@app.get("/run-agent/{product_id}")
async def run_agent_preview(product_id: str) -> dict[str, Any]:
    # GET endpoint is intentionally read-only to avoid accidental writes on browser refresh.
    return await _run_agent_internal(product_id=product_id, log_actions=False)


@app.post("/run-agent/{product_id}")
async def run_agent_execute(product_id: str, request: RunAgentRequest) -> dict[str, Any]:
    return await _run_agent_internal(product_id=product_id, log_actions=request.log_actions)


@app.post("/actions/dispatch-webhook")
async def dispatch_action_webhook(request: WebhookDispatchRequest) -> dict[str, Any]:
    risk_items, _, _ = _risk_context()
    product = _select_product(risk_items, request.product_id)
    payload = {
        "event_type": request.event_type,
        "sent_at": today_iso(),
        "product": {
            "product_id": product.get("product_id") if product else request.product_id,
            "product_name": product.get("name") if product else None,
            "risk_level": product.get("risk_level") if product else None,
            "risk_score": product.get("risk_score") if product else None,
            "estimated_loss": product.get("estimated_loss") if product else None,
            "preventable_loss": product.get("preventable_loss") if product else None,
        },
    }

    pending_log = _log_action(
        action_type="webhook_dispatch_requested",
        product_id=request.product_id,
        message="Webhook dispatch kuyruğa alındı",
        metadata={
            "webhook_url": request.webhook_url,
            "event_type": request.event_type,
        },
        status="pending",
    )

    ok, detail = _dispatch_webhook(request.webhook_url, payload)
    final_status = "sent" if ok else "failed"
    updated_log = action_log_store.update_status(pending_log["id"], final_status)

    return {
        "status": "ok" if ok else "failed",
        "detail": detail,
        "delivery_status": final_status,
        "log": updated_log,
        "payload_preview": payload,
    }
