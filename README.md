# FireRadar AI

FireRadar AI, gida KOBI'leri ve kooperatiflerde son kullanim tarihi yaklasan urunleri erken tespit edip finansal etkiyi hesaplayan ve aksiyon oneren bir AI operasyon MVP'sidir.

## Problem ve Cozum (1 Cumle)

- Problem: Stok, siparis, kampanya ve tedarik kararlarinin manuel yurutulmesi fireyi gec fark ettiriyor ve kaybi artiriyor.
- Cozum: FireRadar tek panelde risk hesaplayip en etkili aksiyonu oneriyor, kampanya/tedarik iletisim taslagi uretip operasyonu hizlandiriyor.

## Konumlandirma

Risk motoru + simulasyon motoru + LLM destekli operasyon ajani.

## Juri Kriteri -> Bizdeki Karsiligi

1. Problem Tanimi ve Deger Onerisi
   - `backend/services/risk_engine.py` fire riskini urun bazinda hesaplar.
   - `frontend/index.html` ana panelde "bugun ne yapmaliyim" akisina odaklanir.
2. AI Kullaniminin Dogrulugu
   - LLM, karar motorundan gelen sayisal cikti uzerinden metin uretir (`backend/services/ai_service.py`).
   - API key yoksa fallback devreye girer; demo surekliligi korunur.
3. Teknik Uygulama ve Mimari
   - FastAPI backend + moduler servisler + sade frontend.
   - `main.py` endpoint orkestrasyonu, servisler domain mantigi.
4. Urunlesme ve Kullanici Deneyimi
   - Tek ekran KPI + simule et + aksiyon sec + ajan calistir.
   - Hata mesajlari ve API baglanti fallback metinleri mevcut.
5. Yenilikcilik
   - Sadece chatbot degil: risk skoru + net etki simulasyonu + ROI benzeri oncelik + fire/kg/CO2 birlikte.
6. Calisabilirlik
   - Uctan uca demo akisi localde calisir.
   - `backend/tests` altinda API contract ve unit testler vardir.
7. Dokumantasyon ve Kod Paylasimi
   - README kurulum, mimari, endpoint ve test adimlarini kapsar.

## MVP Kapsami

- Urun bazli risk analizi
- Tahmini fire maliyeti ve kurtarilabilir deger
- Aksiyon karsilastirmasi ve en iyi aksiyon secimi
- Segment bazli kampanya metni ve tedarikci mail taslagi
- Aksiyon loglama (`pending/sent/failed/completed`)
- Webhook dispatch ile "aksiyon alabilen" entegrasyon kaniti

## Teknik Mimari

```text
CSV Demo Data
    ->
Risk Engine (risk_score, estimated_loss, preventable_loss)
    ->
Simulation Engine (channel + discount impact)
    ->
Agent Orchestration (action comparison, best action)
    ->
LLM Layer (campaign/supplier/summary/chat)
    ->
Action Log + Webhook Dispatch
```

- Backend: FastAPI + Python
- Frontend: HTML/CSS/JavaScript
- Veri: CSV tabanli demo veri
- AI: OpenAI veya Gemini (anahtar yoksa deterministic fallback)

## AI Nerede Kullaniliyor?

- Gunluk ozet metni
- Kampanya mesaji varyantlari
- Tedarikci siparis mail taslagi
- Chat asistani ve demo pitch metni

Not: Sayisal kararlar risk/simulasyon motorunda uretilir, LLM metin katmanidir.

## Decision Logic (Motor Kurallari)

LLM sadece metin uretir; karar secimi backend motoru tarafinda su kurallarla yapilir:

1. Stok, SKT ve son donem satis hizindan urun bazli `risk_score` hesaplanir.
2. Kategoriye gore risk agirliklari degisir (et/balikta SKT baskisi daha yuksek).
3. Fire maliyeti, kurtarilabilir deger, kg fire ve CO2 etkisi birlikte hesaplanir.
4. Her urun icin birden fazla aksiyon senaryosu (indirim + kanal) simule edilir.
5. Simulasyonda kanal bazli operasyon maliyeti uygulanir (SMS/WhatsApp/E-posta/Push).
6. `net_impact = prevented_loss + gross_margin - operation_cost` formulu kullanilir.
7. Et/balik kategorisinde SKT=0 ve agresif kampanya durumunda hard constraint devreye girer.
8. Hard constraint durumunda kampanya yerine guvenli prosedur (kalite kontrol/ayristirma) onerilir.
9. Musteri hedefleme, kategori + segment + ilgi etiketi + kanal tercihi ile yapilir.
10. Nihai secim, net etki ve kayip azaltim yuzdesine gore siralanarak belirlenir.

## Kurulum

### 1) Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
python3 -m http.server 5173
```

Tarayici:

```text
http://localhost:5173/?api=http://localhost:8000
```

## Env Degiskenleri

Backend icin:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
AI_TIMEOUT_SECONDS=20
DEMO_PRODUCT_ID=P001

# CORS: production icin en az birini ayarlayin
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain
CORS_ORIGIN_REGEX=^https://.*\\.netlify\\.app$
FRONTEND_URL=https://your-frontend-domain
```

## API Ozeti

Genel:

- `GET /`
- `GET /risk-analysis`
- `GET /executive-dashboard`
- `GET /operations-snapshot`
- `GET /before-after-impact`
- `GET /impact-report`

Urun bazli:

- `GET /decision-explanation/{product_id}`
- `GET /action-comparison/{product_id}`
- `GET /segment-matches/{product_id}`
- `GET /supplier-decision/{product_id}`
- `GET /recommendation-evidence/{product_id}`

Agent ve aksiyon:

- `GET /run-agent/{product_id}` (read-only preview, log yazmaz)
- `POST /run-agent/{product_id}` (execute, istege bagli log yazar)
- `POST /actions/log`
- `GET /actions/log`
- `POST /actions/dispatch-webhook`

Uretim/simulasyon:

- `POST /simulate-action`
- `POST /generate-action-plan`
- `POST /generate-campaign-message`
- `POST /generate-supplier-order`
- `POST /ask-ai`
- `POST /generate-demo-pitch`

## Hizli Smoke Test

```bash
curl http://localhost:8000/risk-analysis
curl http://localhost:8000/run-agent/P001
curl -X POST http://localhost:8000/run-agent/P001 -H "Content-Type: application/json" -d '{"log_actions":true}'
curl -X POST http://localhost:8000/actions/dispatch-webhook -H "Content-Type: application/json" -d '{"webhook_url":"http://127.0.0.1:9/hook","product_id":"P001"}'
curl http://localhost:8000/actions/log
```

## Test

```bash
cd backend
python3 -m unittest tests/test_api_contracts.py tests/test_risk_and_simulation.py
```

## Demo Ciktilari (Olculebilir Etki)

- Tahmini fire maliyeti (TL)
- Kurtarilabilir deger (TL)
- Kurtarilabilir gida (kg)
- Onlenebilir CO2 etkisi (kg)
- Aksiyon bazli net etki simulasyonu

## Teknolojiler

- Python 3
- FastAPI
- Uvicorn
- HTML/CSS/JavaScript
- OpenAI SDK
- Google Generative AI SDK
