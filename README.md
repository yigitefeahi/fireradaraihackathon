# FireRadar AI

FireRadar AI, gıda KOBİ'leri ve kooperatiflerde son kullanım tarihi yaklaşan ürünleri erken tespit ederek finansal etkiyi hesaplayan ve aksiyon öneren bir yapay zeka destekli operasyonel MVP'dir.

Canlı Demo(netlify): https://fireradaraihackath.netlify.app/?api=https://fireradaraihackathon.onrender.com

Canlı Demo(vercel): https://fireradaraihackathon.vercel.app

<img width="3420" height="1847" alt="AAD1C73D-5FEF-4E00-9FDB-42F0533942F0_1_201_a" src="https://github.com/user-attachments/assets/8f5eeadc-d6cb-4428-8695-7aeb61b34cc4"/>

## Problem ve Çözüm

*   **Problem:** Stok, sipariş, kampanya ve tedarik kararlarının manuel yürütülmesi, firenin geç fark edilmesine ve kayıpların artmasına neden olmaktadır.
*   **Çözüm:** FireRadar AI, tek bir panel üzerinden riskleri hesaplar, en etkili aksiyonları önerir, kampanya ve tedarikçi iletişim taslakları üreterek operasyonel süreçleri hızlandırır.

## Konumlandırma

Risk motoru, simülasyon motoru ve LLM destekli operasyon ajanı entegrasyonu.

## Jüri Değerlendirme Alanları ve FireRadar AI'ın Uygunluğu

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
6.  **Dokümantasyon ve Kod Paylaşımı**
    *   README dosyası, kurulum adımları, mimari genel bakış, API endpointleri ve test süreçlerini kapsamlı bir şekilde açıklar.
  
## Demoda Gösterilemeyen Diğer Sistem Fonksiyonları:

1. Bugün Yapılacaklar ekranı
Bu bölüm günlük görev listesi gibi çalışır. Sistem en acil ürünleri sıraya koyar: hangi ürünü rafa al, kaç indirim yap, müşteriye mesaj gönder gibi. Görev tamamlanınca işaretlenir ve sağ tarafta kurtarılan para, önlenen fire ve CO₂ etkisi görülür.

<img width="3417" height="1813" alt="83E17A67-A3D0-4CD2-AA2D-CC620183A536_1_201_a" src="https://github.com/user-attachments/assets/3dbc624f-ded1-47dd-ad2b-95ad2a6a88cd" />

2. Ana Panel / Günlük Özet ekranı
Bu ekran günün genel durumunu gösterir. Hiçbir şey yapılmazsa ne kadar fire maliyeti oluşabileceğini ve doğru aksiyonlarla ne kadar para kurtarılabileceğini özetler. Aynı zamanda kritik siparişleri ve önümüzdeki haftanın riskli ürünlerini gösterir.

<img width="3420" height="1811" alt="BB838CD8-27DF-4B9B-9E53-018A1E0C10F5_1_201_a" src="https://github.com/user-attachments/assets/285fc44a-3eb9-47c8-93d8-8838ec32c9a9" />

3. Simülasyon ekranı
Burada “İndirim yaparsam ne olur?” sorusunun cevabı görülür. İndirim oranı ve kampanya kanalı seçilir, sistem yaklaşık ne kadar kayıp kurtarılabileceğini hesaplar. Ayrıca müşteriye veya ekibe gönderilecek mesajı da hazırlar.

<img width="3420" height="1850" alt="58A7CEEC-AA17-4286-AEBF-46A7206506FD_1_201_a" src="https://github.com/user-attachments/assets/93126f37-21d1-45b8-8f56-c038af895e9d" />

4. Riskli Ürünler ve Aksiyon ekranı
Bu ekran, hangi ürünlerin acil müdahale istediğini listeler. Kullanıcı ürünleri görür, indirim simülasyonu yapar, müşteriye SMS taslağı hazırlatır veya tedarikçiye karar metni oluşturur. Günlük operasyon için pratik aksiyon ekranı gibi çalışır.

<img width="3420" height="1842" alt="3909C6B1-1FDB-4185-9820-EC77B86E5F5E_1_201_a" src="https://github.com/user-attachments/assets/71d00221-c6e0-4755-80dc-5ab3b11bcd25" />

5. Kanıt / Veri ekranı
Burada sistemin öneriyi kafadan vermediği gösterilir. Hangi ürün, kaç stok var, SKT’ye kaç gün kalmış, risk skoru kaç, tahmini kayıp ne kadar gibi bilgiler kaynaklarıyla birlikte listelenir. Yani kararın arkasındaki veri burada görünür.

<img width="3420" height="1823" alt="870A07A8-24F6-4930-97FE-A21A32680FCB_1_201_a" src="https://github.com/user-attachments/assets/dbfe2dce-ae4d-4428-adce-089e1e060b30" />

6. Tedarikçi Taslağı ekranı
Bu bölüm, seçilen ürün için tedarikçiye ne yazılacağını hazırlar. Mesela stok fazla, satış hızı düşük ya da SKT yaklaşıyorsa sistem “bu siparişi azaltalım veya erteleyelim” diye bir karar çıkarır ve bunu e-posta/metin taslağına dönüştürür.

<img width="3420" height="1597" alt="06DEB17B-F17E-4762-9B1B-FA49D8990470_1_201_a" src="https://github.com/user-attachments/assets/20b73153-55b2-4aec-bc71-114e27e3197e" />

7. FireRadar’a Sor ekranı
Bu ekran, sistemin sohbet asistanı gibi çalışan kısmı. Kullanıcı buraya “Önce hangi ürüne bakayım?” gibi soru yazıyor. Sistem de en riskli ürünü seçip ne yapılması gerektiğini kısa kısa söylüyor: indirim yap, müşteriye mesaj gönder, raf görünürlüğünü artır gibi.

<img width="3420" height="1803" alt="000046F0-FFCF-42FB-BAD8-FEAAE7294179_1_201_a" src="https://github.com/user-attachments/assets/de13ff9d-e6ad-4e1b-80b6-5ee87e9e5cd6" />



## Et ve balık gibi ürünlerde SKT = 0 ve agresif kampanya hard constraint

Gıda güvenliği açısından riskli kategorilerde, özellikle et/balık ürünlerinde SKT=0 durumunda sistem kampanya önermek yerine kalite kontrol, ayrıştırma veya güvenli imha prosedürü önerir.

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

## Demo Çıktıları (Ölçülebilir Etki)

*   Tahmini fire maliyeti (TL)
*   Kurtarılabilir değer (TL)
*   Kurtarılabilir gıda (kg)
*   Önlenebilir CO2 etkisi (kg)
*   Aksiyon bazlı net etki simülasyonu

## Teknolojiler

*   Python
*   FastAPI
*   Uvicorn
*   HTML/CSS/JavaScript
*   Yapay Zeka: Gemini / OpenAI uyumlu LLM katmanı; API anahtarı yoksa deterministik fallback
