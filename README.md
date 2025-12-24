# Sürekli Faiz ve Tarihsel Yatırım Karşılaştırma Simülasyonları

Bu repository iki farklı finansal simülasyon içerir:

1. **Gerçek tarihsel verilerle Altın vs Mevduat Faizi karşılaştırması**
2. **Diferansiyel denklemlerle sürekli bileşik faiz modeli**

Uygulamalar **Streamlit** ile geliştirilmiştir ve etkileşimli olarak çalışır.

---

## 📌 İçerik

- Gerçek piyasa verileri (Yahoo Finance)
- Sürekli bileşik faiz modeli (dS/dt = rS + k)
- Aylık / yıllık faiz ve nakit akışı desteği
- Grafikler ve özet finansal metrikler
- Eğitim ve analiz amaçlı finansal simülasyonlar

---

## 🔹 1. Gerçek Tarihsel Verilerle: Altın mı, Faiz mi?

### 📅 Açıklama
Bu uygulama **tahmini değil**, tamamen **gerçek geçmiş veriler** ile çalışır.

- **Altın (ONS)** → `GC=F`
- **Dolar/TL** → `TRY=X`

verileri Yahoo Finance üzerinden çekilir ve:

- Başlangıç sermayesi
- Aylık düzenli yatırım
- Ortalama mevduat faizi

parametreleriyle **altın yatırımı** ve **mevduat faizi** karşılaştırılır.

### 🧮 Hesaplama Mantığı
- Altın yatırımı gram bazında tutulur
- Gram altın TL hesabı:  
  `(Ons Altın × USD/TRY) / 31.1035`
- Mevduat faizi günlük bileşik olarak işler
- Aylık düzenli ekleme her iki yatırım için de uygulanır

### 📈 Çıktılar
- Toplam yatırılan ana para
- Altın portföyü değeri
- Faiz portföyü değeri
- Hangisinin daha kârlı olduğu
- Zaman içindeki değişimi gösteren grafik

---

## 🔹 2. Sürekli Bileşik Faiz (Diferansiyel Denklem Modeli)

### 📐 Matematiksel Model
Bu uygulama aşağıdaki diferansiyel denklemi çözer:

