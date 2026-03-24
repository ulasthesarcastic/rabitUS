# rabitUS — Proje Kararları

## Ürün Tanımı

**Tek cümle:**
> API'si olan veya olmayan iki sistemi, RQL ile tanımlayıp, yazılımcı gerektirmeden entegre eden platform.

**Kategori:** Low-code Integration Platform (iPaaS)

**Hedef pazar:** Global

---

## Kullanıcı Profili

Teknik ama yazılımcı olmayan entegrasyon uzmanı:
- API nedir biliyor, JSON görmekten korkmaz
- SQL yazmak zorunda kalmamalı
- Entegrasyon mantığını biliyor, kod yazmadan flow tasarlayabilmeli

**Kullanıcı değil:**
- Son kullanıcı (satıcı, muhasebeci)
- Yazılımcı

---

## Bağlantı Türleri

| Kaynak | Hedef |
|---|---|
| REST API | REST API |
| REST API | Veritabanı (DB) |
| Veritabanı | REST API |
| Veritabanı | Veritabanı |

> Not: Bir sistemin API'si olmasa bile, DB'sine direkt yazılabilir. DB credentials müşterinin sorumluluğundadır.

---

## RQL — rabitUS Query Language

Kullanıcının entegrasyonu tanımladığı basit, özgün dil. JQL'den (Jira Query Language) ilham alınmıştır.

### Sözdizimi

```rql
# Bağlantı tanımı
SOURCE api:trendyol/orders
TARGET db:logo/tbl_fatura

# Alan mapping
source.siparis_no → target.fatura_no
source.musteri_adi → target.cari_unvan
source.tutar → target.toplam_tutar

# Logic
IF source.tutar > 1000 THEN target.kategori = "premium"
IF source.odeme_turu = "kapida" THEN target.odeme_kodu = "KD"
IF source.musteri_id IS EMPTY THEN SKIP

# Tetikleyici
TRIGGER every 15min
```

### RQL Operatörleri (MVP)
- `>`, `<`, `=`, `!=`
- `IS EMPTY`, `IS NOT EMPTY`
- `THEN`, `SKIP`

### Tetikleyiciler (MVP)
- `TRIGGER every Xmin` — periyodik (her X dakikada bir)
- `TRIGGER every Xhour` — saatlik
- `TRIGGER manual` — kullanıcı tetikler (test için)

---

## Kullanıcı Akışı

1. **Bağlantı tanımla** — API endpoint veya DB credentials gir
2. **RQL yaz** — mapping, logic, tetikleyici
3. **Test et** — gerçek veriyle dene, hataları gör
4. **Canlıya al** — tetikleyici devreye girer
5. **İzle** — log, hata takibi, kaç kayıt geçti

---

## Teknik Kararlar

| Konu | Karar |
|---|---|
| Backend | Python + FastAPI |
| Frontend | React |
| Dağıtım | On-premise (Docker) |
| Lisans yönetimi | rabitUS cloud (merkezi) |
| Geliştirme önceliği | Hızlı MVP |

### Neden On-Premise?
- Kurumsal müşteri verisini dışarı çıkarmak istemiyor
- DB credentials güvenliği
- "Veriniz dışarı çıkmıyor" güven argümanı

### Neden Python?
- Hızlı MVP geliştirme
- RQL parser yazmak kolay
- DB ve API bağlantıları için zengin kütüphane ekosistemi
- Go: ikinci versiyonda değerlendirilebilir

---

## Rakip Analizi Özeti

| Platform | Neden rabitUS değil? |
|---|---|
| Zapier / Make | Hazır connector listesine bağımlı, Türkiye sistemleri yok |
| MuleSoft / Boomi | Çok teknik, kurumsal fiyat |
| Workato | Yılık $10K+, teknik ekip gerektirir |
| NiFi | SQL/Java bilgisi gerekiyor, çok karmaşık |
| Türkiye alternatifleri | Sadece e-ticaret odaklı, KOBİ için uygun değil |

**rabitUS farkı:**
- Türkiye'ye özel sistemler (Logo, Netsis, e-fatura, Trendyol vb.) için hazır şablonlar
- RQL ile özgün kullanıcı deneyimi
- API'si olmayan sistemi DB üzerinden bağlayabilme
- On-premise, veri dışarı çıkmıyor
- KOBİ'ye uygun fiyat

---

## 🗺️ Yol Haritası (MVP Sonrası)

- [ ] Hata yönetimi — belirli sayıda retry, sonra e-posta bildirimi
- [ ] Webhook / event tabanlı tetikleyici
- [ ] DB trigger
- [ ] AI destekli RQL üretimi (doğal dilden RQL'e)
- [ ] Go backend (performans optimizasyonu)
- [ ] Türkiye'ye özel hazır şablonlar (Logo, Netsis, e-fatura, Trendyol)

---

## Repo Yapısı

```
rabitUS/
├── backend/          # Python + FastAPI
│   ├── main.py
│   ├── rql/          # RQL parser motoru
│   ├── connectors/   # API ve DB bağlantıları
│   ├── engine/       # Flow çalıştırıcı
│   └── requirements.txt
├── frontend/         # React
│   ├── src/
│   └── package.json
├── docs/             # Kararlar, RQL spec, mimari
│   └── decisions.md  # Bu dosya
├── docker-compose.yml
├── start.sh
└── README.md
```

---

## İsim ve Marka

- **Şirket adı:** rabitUS
- **Yazılış:** rabitUS (US büyük harf)
- **Köken:** Osmanlıca "rabıta" (bağ, bağlantı) + İngilizce "rabbit" (hız) + "US"
- **Domain:** rabitus.com (alındı)
- **Ürün dili:** RQL — rabitUS Query Language

---

*Son güncelleme: Mart 2026*
