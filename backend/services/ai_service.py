from __future__ import annotations

import asyncio
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv


load_dotenv()


class AIService:
    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.timeout_seconds = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))

    @property
    def has_external_provider(self) -> bool:
        return bool(self.openai_api_key or self.gemini_api_key or self.groq_api_key)

    async def complete(self, prompt: str) -> str:
        if self.provider == "groq" and self.groq_api_key:
            response = await self._run_with_timeout(self._complete_with_groq, prompt)
            if response:
                return response

        if self.provider == "gemini" and self.gemini_api_key:
            response = await self._run_with_timeout(self._complete_with_gemini, prompt)
            if response:
                return response

        if self.provider == "openai" and self.openai_api_key:
            response = await self._run_with_timeout(self._complete_with_openai, prompt)
            if response:
                return response

        # Cross-provider fallback for production resilience.
        if self.groq_api_key:
            response = await self._run_with_timeout(self._complete_with_groq, prompt)
            if response:
                return response

        if self.openai_api_key:
            response = await self._run_with_timeout(self._complete_with_openai, prompt)
            if response:
                return response

        if self.gemini_api_key:
            response = await self._run_with_timeout(self._complete_with_gemini, prompt)
            if response:
                return response

        return self._fallback_answer(prompt)

    async def _run_with_timeout(self, func, prompt: str) -> Optional[str]:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(func, prompt),
                timeout=max(self.timeout_seconds, 1.0),
            )
        except (TimeoutError, asyncio.TimeoutError):
            return None

    def _complete_with_openai(self, prompt: str) -> Optional[str]:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FireRadar AI, a Turkish AI operations copilot for grocery retailers. "
                            "Answer with quantified impact, clear next actions, and a confident hackathon demo tone."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return response.choices[0].message.content
        except Exception:
            return None

    def _complete_with_groq(self, prompt: str) -> Optional[str]:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.groq_api_key,
                base_url=self.groq_base_url,
            )
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FireRadar AI, a Turkish AI operations copilot for grocery retailers. "
                            "Answer with quantified impact, clear next actions, and a confident hackathon demo tone."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return response.choices[0].message.content
        except Exception:
            return None

    def _complete_with_gemini(self, prompt: str) -> Optional[str]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            return None

    def _fallback_answer(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        ctx = _extract_product_context(prompt)
        question = _extract_question_from_chat_prompt(prompt)
        question_lower = question.lower()
        product_name = ctx.get("product_name") or "Seçili ürün"
        risk_score = ctx.get("risk_score") or "-"
        preventable_loss = ctx.get("preventable_loss") or "-"
        discount = ctx.get("discount_percent") or "20"
        action = ctx.get("recommended_action") or "hedefli kampanya + görünür raf"
        channel = ctx.get("channel_hint") or "SMS"

        if "sen fireradar ai asistanısın" in prompt_lower:
            if "1 cümle" in question_lower or "tek cümle" in question_lower:
                return (
                    f"{product_name} ürünü risk skoru {risk_score} ile bugün öncelikli; "
                    f"hedefli %{discount} indirim + {channel} aksiyonuyla yaklaşık {preventable_loss} TL kayıp önlenebilir."
                )
            if "şiir" in question_lower:
                return (
                    "Bu asistan operasyon odaklı çalışır; şiir yerine doğrudan uygulanacak aksiyon öneriyorum:\n"
                    f"1) {product_name} için %{discount} indirim aç.\n"
                    f"2) {channel} kanalından hedef segmente kampanya geç.\n"
                    f"3) 2 saat sonra satış hızını kontrol et ve gerekirse bundle'a geç."
                )
            return (
                "Kısa yanıt: Öncelik, risk skoru yüksek ve kurtarılabilir değeri yüksek üründe.\n\n"
                f"Seçili ürün: {product_name} (risk: {risk_score}).\n\n"
                "İlk 3 aksiyon:\n"
                f"1) %{discount} indirim uygula.\n"
                f"2) {channel} ile hedef müşterilere mesaj gönder.\n"
                "3) Raf önü görünürlüğü artır ve 2-3 saatlik satış takibi yap.\n\n"
                f"Tahmini etki: yaklaşık {preventable_loss} TL kayıp azaltımı."
            )

        if "demo pitch" in prompt_lower or "jüri" in prompt_lower:
            return (
                "FireRadar AI, marketlerin her sabah fire riskini finansal etkiye çeviren bir karar motorudur.\n\n"
                f"Bugünkü demoda {product_name} için risk skoru {risk_score} ve kurtarılabilir değer "
                f"{preventable_loss} TL seviyesinde. Sistem %{discount} indirim ve {channel} kanalını öneriyor. "
                "Mağaza müdürü tek ekranda hangi ürüne, kaç saat içinde, hangi mesajla aksiyon alacağını görüyor.\n\n"
                "Değer önerisi net: daha az fire, daha hızlı satış, daha iyi müşteri hedefleme ve ölçülebilir "
                "operasyon etkisi. FireRadar AI sadece raporlamaz; aksiyon önerir, simüle eder ve kampanyayı üretir."
            )
        if "kampanya" in prompt_lower or "message" in prompt_lower:
            if "posta" in prompt_lower or "e-posta" in prompt_lower or "konu:" in prompt_lower:
                return (
                    f"Konu: {product_name} için bugün %{discount} fırsat\n\n"
                    "Merhaba,\n\n"
                    f"{product_name} ürününde fireyi azaltmak için bugün %{discount} oranlı avantajımız başladı. "
                    "Yereldeki mağaza ve teslim seçeneklerimiz için bugün stokların en taze olduğunu hatırlatırız.\n\n"
                    "Çok yakında görüşmek dileği ile,\n"
                    "İşletme ekibi — FireRadar\n"
                    "---\n"
                    f"Konu: {product_name} için son gün kontrollü kampanya\n\n"
                    "Merhaba,\n\n"
                    f"{product_name} stoğunu sağlıklı tüketmek için kısa süreli %{discount} destek uyguluyoruz.\n\n"
                    "İyi alışverişler.\n\n"
                    "---\n"
                    f"Konu: {product_name} kampanya özeti\n\n"
                    "Merhaba,\n\n"
                    f"Risk skoru {risk_score} seviyesinde olan {product_name} için kampanyayı bugün aktif ediyoruz.\n\n"
                    "Teşekkürler."
                )
            if "whatsapp" in prompt_lower:
                return (
                    f"WhatsApp taslağı:\nSelam, {product_name} için bugün %{discount} fırsat var. "
                    "Taze üründe yakınınıza uğrayın veya seçili pakette geçerlidir.\n"
                    "---\n"
                    f"{product_name} kampanyası bugün açıldı — stok sınırlı, gelebilir misin?\n"
                    "---\n"
                    f"{product_name} için önerilen aksiyon: {action}. Detay için mağazaya gelebilirsin."
                )
            return (
                f"SMS taslağı: {product_name} ürününde bugün %{discount} kampanya başladı, stok sınırlı.\n"
                "---\n"
                f"SMS: Risk skoru {risk_score}. {product_name} için bugün kampanyayı değerlendirin.\n"
                "---\n"
                f"SMS: {preventable_loss} TL kaybı önlemek için {product_name} kampanyası aktiftir."
            )
        if "tedarikçi" in prompt_lower or "sipariş" in prompt_lower:
            return (
                "Merhaba,\n\n"
                f"Stok dengesini korumak için {product_name} ürününde önerilen aksiyonumuz: {action}. "
                "Buna göre yeni sipariş planını netleştirmek istiyoruz. Uygun teslimat tarihi, güncel birim fiyat "
                "ve minimum sipariş miktarı bilgisini paylaşabilir misiniz?\n\n"
                "Teşekkürler."
            )
        if "aksiyon" in prompt_lower or "plan" in prompt_lower:
            return (
                "AI aksiyon planı:\n"
                f"1) İlk 30 dakikada {product_name} ürününü raf önüne taşı.\n"
                f"2) Önerilen %{discount} indirimi uygula ve fiyat etiketini görünür yap.\n"
                f"3) {channel} kanalından hedef müşteriye kampanya gönder.\n"
                "4) Öğlen satış hızını kontrol et; hedefin altında kalırsa bundle kampanyaya geç.\n"
                f"5) Gün sonunda kalan stoğu güvenli prosedürle yönet; hedef {preventable_loss} TL kaybı önlemek."
            )
        if "özet" in prompt_lower or "summary" in prompt_lower:
            return (
                f"Günlük AI özeti: {product_name} için risk skoru {risk_score}; "
                f"yaklaşık {preventable_loss} TL kurtarılabilir değer var. "
                f"Öncelikli aksiyon: %{discount} indirim + {channel} kampanyası + görünür raf."
            )
        return (
            "Demo AI cevabı: API anahtarı bulunmadığı için kural tabanlı yanıt üretiyorum. "
            f"Seçili ürün: {product_name} | Risk skoru: {risk_score} | Kurtarılabilir: {preventable_loss} TL | "
            f"Öneri: %{discount} indirim + {channel}."
        )


def _extract_product_context(prompt: str) -> dict[str, str]:
    context = {
        "product_name": "",
        "risk_score": "",
        "preventable_loss": "",
        "discount_percent": "",
        "recommended_action": "",
        "channel_hint": "",
    }
    text = str(prompt or "")
    m_name = re.search(r"Ürün:\s*([^|\n]+)", text)
    m_risk = re.search(r"Risk skoru:\s*([^|\n]+)", text)
    m_preventable = re.search(r"Kurtarılabilir zarar:\s*([^|\n]+)\s*TL", text)
    m_discount = re.search(r"Önerilen indirim:\s*%([0-9]+)", text)
    m_action = re.search(r"Öneri:\s*([^|\n]+)", text)
    m_channel = re.search(r"Kanal:\s*([^\n]+)", text)
    if m_name:
        context["product_name"] = m_name.group(1).strip()
    if m_risk:
        context["risk_score"] = m_risk.group(1).strip()
    if m_preventable:
        context["preventable_loss"] = m_preventable.group(1).strip()
    if m_discount:
        context["discount_percent"] = m_discount.group(1).strip()
    if m_action:
        context["recommended_action"] = m_action.group(1).strip()
    if m_channel:
        context["channel_hint"] = m_channel.group(1).strip()
    if not context["channel_hint"]:
        if "whatsapp" in text.lower():
            context["channel_hint"] = "WhatsApp"
        elif "e-posta" in text.lower() or "email" in text.lower():
            context["channel_hint"] = "E-posta"
        else:
            context["channel_hint"] = "SMS"
    return context


def _extract_question_from_chat_prompt(prompt: str) -> str:
    text = str(prompt or "")
    m = re.search(r"Soru:\s*\n(.+?)\n\n", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def _format_product(product: Optional[dict[str, Any]]) -> str:
    if not product:
        return "Ürün seçilmedi."

    return (
        f"Ürün: {product.get('name')} | Kategori: {product.get('category')} | "
        f"Stok: {product.get('stock_quantity')} | Risk skoru: {product.get('risk_score')} | "
        f"Risk seviyesi: {product.get('risk_level')} | Tahmini zarar: {product.get('estimated_loss')} TL | "
        f"Kurtarılabilir zarar: {product.get('preventable_loss')} TL | "
        f"Önerilen indirim: %{int(float(product.get('discount_recommendation') or 0) * 100)} | "
        f"ROI skoru: {product.get('roi_score')} | "
        f"Öneri: {product.get('recommended_action')}"
    )


def build_daily_summary_prompt(summary: dict[str, Any], high_risk_products: list[dict[str, Any]]) -> str:
    products_text = "\n".join(_format_product(product) for product in high_risk_products[:5])
    return f"""
FireRadar günlük fire risk özetini Türkçe yaz. Cevap yöneticiye sunulacak kadar net olsun:
- toplam risk
- kurtarılabilir zarar
- ilk 3 aksiyon
- beklenen iş etkisi

Genel metrikler:
{summary}

Yüksek riskli ürünler:
{products_text}
""".strip()


def build_action_plan_prompt(product: Optional[dict[str, Any]]) -> str:
    return f"""
Aşağıdaki ürün için uygulanabilir, saat bazlı ve ölçülebilir bir fire azaltma aksiyon planı üret.
Plan; indirim, raf konumu, hedef müşteri segmenti, kampanya kanalı ve beklenen finansal etki içersin.
{_format_product(product)}
""".strip()


def build_campaign_prompt(product: Optional[dict[str, Any]], channel: str = "SMS", tone: str = "friendly") -> str:
    ch = channel or "SMS"
    rules = (
        "WhatsApp: 2–4 çok kısa cümle, günlük konuşma, abartılı emoji kullanma, net CTA.",
        "SMS: tek SMS bloğu, yaklaşık 300 karaktere kadar Türkçe, gereksiz şişirme yok.",
        "E-posta: önce tek satır 'Konu:' sonra selamlama, 2 kısa paragraf ve kibar kapanış; profesyonel imza hissi.",
    )
    ch_low = ch.lower().replace(" ", "")
    if "posta" in ch_low or "mail" in ch_low:
        matched = rules[2]
    elif "whatsapp" in ch_low:
        matched = rules[0]
    else:
        matched = rules[1]
    return f"""
Türkçe kampanya çıktısı üret.

Kanal kuralları: {matched}

Riskli ürün verisi ve ton:
- Kanal: {ch}
- Ton: {tone}

Kullanıcıya gösterilecek: {ch} için 3 alternatif kampanya taslağı. Her taslağı "---" ile ayır.

Ürün ve risk verisi:
{_format_product(product)}
""".strip()


def build_supplier_order_prompt(product: Optional[dict[str, Any]], draft: dict[str, Any]) -> str:
    return f"""
Aşağıdaki ürün ve taslak bilgiye göre tedarikçiye gönderilecek kısa, saygılı ve anlaşılır Türkçe sipariş maili yaz.
Teknik terim kullanma. Ürün adı, önerilen adet ve teslimat talebi net olsun.

Ürün:
{_format_product(product)}

Taslak:
{draft}
""".strip()


def build_chat_prompt(
    question: str,
    summary: dict[str, Any],
    high_risk_products: list[dict[str, Any]],
    selected_product: Optional[dict[str, Any]] = None,
) -> str:
    products_text = "\n".join(_format_product(product) for product in high_risk_products[:8])
    selected_text = _format_product(selected_product) if selected_product else "Kullanıcı özel ürün seçmedi."
    return f"""
Sen FireRadar AI asistanısın. Kullanıcının sorusunu Türkçe, net ve operasyonel cevapla.
Yanıtlarında şu formatı koru:
1) Kısa yanıt (1-2 cümle)
2) Seçili ürüne özel yorum (varsa)
3) Hemen uygulanacak ilk 3 aksiyon (numaralı)
4) Beklenen finansal etki (TL)

Kurallar:
- Sayısal veri varsa tahmini TL etkisini mutlaka yaz.
- Kullanıcı sorusu belirsizse önce en yüksek riskli ürünü önceliklendir.
- Veri yoksa uydurma üretme; bunu açıkça belirt.

Soru:
{question}

Kullanıcının seçtiği ürün:
{selected_text}

Güncel risk özeti:
{summary}

Yüksek riskli ürünler:
{products_text}
""".strip()


def build_demo_pitch_prompt(
    summary: dict[str, Any],
    high_risk_products: list[dict[str, Any]],
    impact_report: dict[str, Any],
) -> str:
    products_text = "\n".join(_format_product(product) for product in high_risk_products[:4])
    return f"""
Jüriye sunulacak 60 saniyelik FireRadar AI demo pitch metni yaz.
Türkçe olsun, problem, çözüm, AI farkı, ölçülebilir etki ve kapanış cümlesi içersin.

Risk özeti:
{summary}

Etki raporu:
{impact_report}

Öne çıkan ürünler:
{products_text}
""".strip()
