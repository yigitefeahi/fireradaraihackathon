# FireRadar AI

FireRadar AI, gıda KOBİ'leri ve kooperatiflerde son kullanım tarihi yaklaşan ürünleri erken tespit ederek finansal etkiyi hesaplayan ve aksiyon öneren bir yapay zeka destekli operasyonel MVP'dir.

<img width="1277" height="822" alt="image" src="https://github.com/user-attachments/assets/56241a6e-8a2e-4e9e-8309-831ccdfeacb3" />

## Problem ve Çözüm

*   **Problem:** Stok, sipariş, kampanya ve tedarik kararlarının manuel yürütülmesi, firenin geç fark edilmesine ve kayıpların artmasına neden olmaktadır.
*   **Çözüm:** FireRadar AI, tek bir panel üzerinden riskleri hesaplar, en etkili aksiyonları önerir, kampanya ve tedarikçi iletişim taslakları üreterek operasyonel süreçleri hızlandırır.

## Konumlandırma

Risk motoru, simülasyon motoru ve LLM destekli operasyon ajanı entegrasyonu.

## Jüri Değerlendirme Alanları ve FireRadar AI'ın Katkısı

FireRadar AI projesi, değerlendirme kriterlerine aşağıdaki yaklaşımlarla katkı sağlamaktadır:

1.  **Problem Tanımı ve Değer Önerisi**
    *   `backend/services/risk_engine.py` modülü, ürün bazında fire riskini detaylı bir şekilde hesaplar.
    *   `frontend/index.html` ana paneli, kullanıcının "bugün ne yapmalıyım" sorusuna odaklanarak hızlı ve etkili aksiyon önerileri sunar.
2.  **Yapay Zeka Kullanımının Doğruluğu**
    *   LLM (Büyük Dil Modeli), karar motorundan gelen sayısal çıktılar üzerinden anlamlı ve bağlamsal metinler üretir (`backend/services/ai_service.py`).
    *   API anahtarı bulunmadığında dahi demo sürekliliğini sağlamak amacıyla bir geri dönüş (fallback) mekanizması devreye girer.
3.  **Teknik Uygulama ve Mimari**
    *   Proje, FastAPI tabanlı bir backend, modüler servisler ve sade bir frontend mimarisi üzerine kurulmuştur.
    *   `main.py` dosyası, endpoint orkestrasyonunu yönetirken, servisler alan odaklı (domain-driven) bir yaklaşımla tasarlanmıştır.
4.  **Ürünleşme ve Kullanıcı Deneyimi**
    *   Tek ekran üzerinden KPI takibi, simülasyon yapma, aksiyon seçimi ve ajan çalıştırma gibi temel işlevler sunulur.
    *   Kullanıcı dostu hata mesajları ve API bağlantı sorunları için fallback metinleri mevcuttur.
5.  **Yenilikçilik**
    *   FireRadar AI, sadece bir chatbot olmanın ötesinde; risk skoru hesaplama, net etki simülasyonu, ROI benzeri önceliklendirme ve fire/kg/CO2 etkisini bir arada değerlendirme gibi yenilikçi özellikler sunar.
6.  **Çalışabilirlik**
    *   Uçtan uca demo akışı yerel ortamda sorunsuz bir şekilde çalışmaktadır.
    *   `backend/tests` dizini altında API sözleşmesi (contract) ve birim testleri (unit tests) bulunmaktadır.
7.  **Dokümantasyon ve Kod Paylaşımı**
    *   README dosyası, kurulum adımları, mimari genel bakış, API endpointleri ve test süreçlerini kapsamlı bir şekilde açıklar.

<img width="1106" height="826" alt="image" src="https://github.com/user-attachments/assets/03318036-a9d4-4bfb-a8c5-116d55486fd7" />

## MVP Kapsamı

*   Ürün bazlı risk analizi
*   Tahmini fire maliyeti ve kurtarılabilir değer
*   Aksiyon karşılaştırması ve en iyi aksiyon seçimi
*   Segment bazlı kampanya metni ve tedarikçi mail taslağı
*   Aksiyon loglama (`pending/sent/failed/completed`)
*   Webhook dispatch ile "aksiyon alabilen" entegrasyon kanıtı

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

*   **Backend:** FastAPI + Python
*   **Frontend:** HTML/CSS/JavaScript
*   **Veri:** CSV tabanlı demo veri
*   **Yapay Zeka:** OpenAI veya Gemini (anahtar yoksa deterministik fallback)

## Yapay Zeka Kullanım Alanları

FireRadar AI, yapay zekayı aşağıdaki alanlarda etkin bir şekilde kullanır:

*   Günlük özet metni oluşturma
*   Kampanya mesajı varyantları üretme
*   Tedarikçi sipariş mail taslağı hazırlama
*   Chat asistanı ve demo pitch metni oluşturma

**Not:** Sayısal kararlar ve risk/simülasyon motoru tarafından üretilen temel analizler, sistemin çekirdeğini oluşturur. Büyük Dil Modelleri (LLM) ise bu kararların metinsel olarak ifade edilmesi, kampanya ve iletişim taslaklarının oluşturulması gibi metin katmanı işlevlerini yerine getirir. İstenildiği takdirde, LLM'ler karar alma süreçlerine daha derinlemesine entegre edilebilir.

## Karar Mantığı (Motor Kuralları)

LLM sadece metin üretir; karar seçimi backend motoru tarafında şu kurallarla yapılır:

1.  Stok, SKT ve son dönem satış hızından ürün bazlı `risk_score` hesaplanır.
2.  Kategoriye göre risk ağırlıkları değişir (et/balıkta SKT baskısı daha yüksek).
3.  Fire maliyeti, kurtarılabilir değer, kg fire ve CO2 etkisi birlikte hesaplanır.
4.  Her ürün için birden fazla aksiyon senaryosu (indirim + kanal) simüle edilir.
5.  Simülasyonda kanal bazlı operasyon maliyeti uygulanır (SMS/WhatsApp/E-posta/Push).
6.  `net_impact = prevented_loss + gross_margin - operation_cost` formülü kullanılır.
7.  Et/balık kategorisinde SKT=0 ve agresif kampanya durumunda hard constraint devreye girer.
8.  Hard constraint durumunda kampanya yerine güvenli prosedür (kalite kontrol/ayrıştırma) önerilir.
9.  Müşteri hedefleme, kategori + segment + ilgi etiketi + kanal tercihi ile yapılır.
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

## Ortam Değişkenleri

Backend için gerekli ortam değişkenleri aşağıda listelenmiştir:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
AI_TIMEOUT_SECONDS=20
DEMO_PRODUCT_ID=P001

# CORS: Üretim ortamı için en az birini ayarlayın
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain
CORS_ORIGIN_REGEX=^https://.*\\.netlify\\.app$
FRONTEND_URL=https://your-frontend-domain
```

## API Özeti

### Genel Endpointler:

*   `GET /`
*   `GET /risk-analysis`
*   `GET /executive-dashboard`
*   `GET /operations-snapshot`
*   `GET /before-after-impact`
*   `GET /impact-report`

### Ürün Bazlı Endpointler:

*   `GET /decision-explanation/{product_id}`
*   `GET /action-comparison/{product_id}`
*   `GET /segment-matches/{product_id}`
*   `GET /supplier-decision/{product_id}`
*   `GET /recommendation-evidence/{product_id}`

### Agent ve Aksiyon Endpointleri:

*   `GET /run-agent/{product_id}` (Sadece okuma önizlemesi, log yazmaz)
*   `POST /run-agent/{product_id}` (Aksiyonu yürütür, isteğe bağlı log yazar)
*   `POST /actions/log`
*   `GET /actions/log`
*   `POST /actions/dispatch-webhook`

### Üretim/Simülasyon Endpointleri:

*   `POST /simulate-action`
*   `POST /generate-action-plan`
*   `POST /generate-campaign-message`
*   `POST /generate-supplier-order`
*   `POST /ask-ai`
*   `POST /generate-demo-pitch`

## Hızlı Smoke Test

```bash
curl http://localhost:8000/risk-analysis
curl http://localhost:8000/run-agent/P001
curl -X POST http://localhost:8000/run-agent/P001 -H "Content-Type: application/json" -d '{"log_actions":true}'
curl -X POST http://localhost:8000/actions/dispatch-webhook -H "Content-Type: application/json" -d '{"webhook_url":"http://127.0.0.1:9/hook","product_id":"P001"}'
curl http://localhost:8000/actions/log
```

## Testler

```bash
cd backend
python3 -m unittest tests/test_api_contracts.py tests/test_risk_and_simulation.py
```

## Demo Çıktıları (Ölçülebilir Etki)

*   Tahmini fire maliyeti (TL)
*   Kurtarılabilir değer (TL)
*   Kurtarılabilir gıda (kg)
*   Önlenebilir CO2 etkisi (kg)
*   Aksiyon bazlı net etki simülasyonu

## Teknolojiler

*   Python 3
*   FastAPI
*   Uvicorn
*   HTML/CSS/JavaScript
*   Google Generative AI SDK

## Tedarikçi Mesajı Taslağı 

FireRadar AI, belirlenen aksiyonlar doğrultusunda tedarikçilere gönderilecek sipariş mesaj taslaklarını otomatik olarak oluşturur. Bu özellik, operasyonel süreçleri hızlandırarak manuel hata riskini azaltır ve tedarikçi iletişiminizi standartlaştırır.

<img width="342" height="555" alt="image" src="https://github.com/user-attachments/assets/ee1275c3-decb-41b3-9c94-a18b79297447" />



