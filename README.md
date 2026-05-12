# FireRadar AI

FireRadar AI, gıda KOBİ'leri ve kooperatiflerde son kullanım tarihi yaklaşan ürünleri erken tespit edip finansal etkiyi hesaplayan ve aksiyon öneren bir AI operasyon MVP'sidir.

<img width="1277" height="822" alt="image" src="https://github.com/user-attachments/assets/56241a6e-8a2e-4e9e-8309-831ccdfeacb3" />


## Problem ve Çözüm 

- Problem: Stok, sipariş, kampanya ve tedarik kararlarının manuel yürütülmesi fireyi geç fark ettiriyor ve kaybı artırıyor.
- Çözüm: FireRadar tek panelde risk hesaplayıp en etkili aksiyonu öneriyor, kampanya/tedarik iletişim taslağı üretip operasyonu hızlandırıyor.

## Konumlandırma

Risk motoru + simülasyon motoru + LLM destekli operasyon ajanı.

## Jüri Kriteri -> Bizdeki Karşılığı

1. Problem Tanımı ve Değer Önerisi
   - `backend/services/risk_engine.py` fire riskini ürün bazında hesaplar.
   - `frontend/index.html` ana panelde "bugün ne yapmalıyım" akışına odaklanır.
2. AI Kullanımının Doğruluğu
   - LLM, karar motorundan gelen sayısal çıktı üzerinden metin üretir (`backend/services/ai_service.py`).
   - API key yoksa fallback devreye girer; demo sürekliliği korunur.
3. Teknik Uygulama ve Mimari
   - FastAPI backend + modüler servisler + sade frontend.
   - `main.py` endpoint orkestrasyonu, servisler domain mantığı.
4. Ürünleşme ve Kullanıcı Deneyimi
   - Tek ekran KPI + simüle et + aksiyon seç + ajan çalıştır.
   - Hata mesajları ve API bağlantı fallback metinleri mevcut.
5. Yenilikçilik
   - Sadece chatbot değil: risk skoru + net etki simülasyonu + ROI benzeri öncelik + fire/kg/CO2 birlikte.
6. Çalışabilirlik
   - Uçtan uca demo akışı localde çalışır.
   - `backend/tests` altında API contract ve unit testler vardır.
7. Dokümantasyon ve Kod Paylaşımı
   - README kurulum, mimari, endpoint ve test adımlarını kapsar.

<img width="1106" height="826" alt="image" src="https://github.com/user-attachments/assets/03318036-a9d4-4bfb-a8c5-116d55486fd7" />


## MVP Kapsamı

- Ürün bazlı risk analizi
- Tahmini fire maliyeti ve kurtarılabilir değer
- Aksiyon karşılaştırması ve en iyi aksiyon seçimi
- Segment bazlı kampanya metni ve tedarikçi mail taslağı
- Aksiyon loglama (`pending/sent/failed/completed`)
- Webhook dispatch ile "aksiyon alabilen" entegrasyon kanıtı

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
- Veri: CSV tabanlı demo veri
- AI: OpenAI veya Gemini (anahtar yoksa deterministic fallback)

## AI Nerede Kullanılıyor?

- Günlük özet metni
- Kampanya mesajı varyantları
- Tedarikçi sipariş mail taslağı
- Chat asistanı ve demo pitch metni

Not: Sayısal kararlar risk/simülasyon motorunda üretilir, LLM metin katmanıdır.

## Decision Logic (Motor Kuralları)

LLM sadece metin üretir; karar seçimi backend motoru tarafında şu kurallarla yapılır:

1. Stok, SKT ve son dönem satış hızından ürün bazlı `risk_score` hesaplanır.
2. Kategoriye göre risk ağırlıkları değişir (et/balıkta SKT baskısı daha yüksek).
3. Fire maliyeti, kurtarılabilir değer, kg fire ve CO2 etkisi birlikte hesaplanır.
4. Her ürün için birden fazla aksiyon senaryosu (indirim + kanal) simüle edilir.
5. Simülasyonda kanal bazlı operasyon maliyeti uygulanır (SMS/WhatsApp/E-posta/Push).
6. `net_impact = prevented_loss + gross_margin - operation_cost` formülü kullanılır.
7. Et/balık kategorisinde SKT=0 ve agresif kampanya durumunda hard constraint devreye girer.
8. Hard constraint durumunda kampanya yerine güvenli prosedür (kalite kontrol/ayrıştırma) önerilir.
9. Müşteri hedefleme, kategori + segment + ilgi etiketi + kanal tercihi ile yapılır.
10. Nihai seçim, net etki ve kayıp azaltım yüzdesine göre sıralanarak belirlenir.

<img width="1232" height="752" alt="image" src="https://github.com/user-attachments/assets/f074aaf6-12c3-4d52-adab-c097c6dd7d77" />


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

Tarayıcı:

```text
http://localhost:5173/?api=http://localhost:8000
```

## Env Değişkenleri

Backend için:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
AI_TIMEOUT_SECONDS=20
DEMO_PRODUCT_ID=P001

# CORS: production için en az birini ayarlayın
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain
CORS_ORIGIN_REGEX=^https://.*\\.netlify\\.app$
FRONTEND_URL=https://your-frontend-domain
```

## API Özeti

Genel:

- `GET /`
- `GET /risk-analysis`
- `GET /executive-dashboard`
- `GET /operations-snapshot`
- `GET /before-after-impact`
- `GET /impact-report`

Ürün bazlı:

- `GET /decision-explanation/{product_id}`
- `GET /action-comparison/{product_id}`
- `GET /segment-matches/{product_id}`
- `GET /supplier-decision/{product_id}`
- `GET /recommendation-evidence/{product_id}`

Agent ve aksiyon:

- `GET /run-agent/{product_id}` (read-only preview, log yazmaz)
- `POST /run-agent/{product_id}` (execute, isteğe bağlı log yazar)
- `POST /actions/log`
- `GET /actions/log`
- `POST /actions/dispatch-webhook`

Üretim/simülasyon:

- `POST /simulate-action`
- `POST /generate-action-plan`
- `POST /generate-campaign-message`
- `POST /generate-supplier-order`
- `POST /ask-ai`
- `POST /generate-demo-pitch`

## Hızlı Smoke Test

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

## Demo Çıktıları (Ölçülebilir Etki)

- Tahmini fire maliyeti (TL)
- Kurtarılabilir değer (TL)
- Kurtarılabilir gıda (kg)
- Önlenebilir CO2 etkisi (kg)
- Aksiyon bazlı net etki simülasyonu

## Teknolojiler

- Python 3
- FastAPI
- Uvicorn
- HTML/CSS/JavaScript
- OpenAI SDK
- Google Generative AI SDK
