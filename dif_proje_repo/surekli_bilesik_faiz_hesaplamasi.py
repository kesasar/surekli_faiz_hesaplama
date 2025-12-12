import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Sayfa Ayarları
st.set_page_config(page_title="Sürekli Bileşik Faiz Modeli (Dinamik Finansal Modelleme)", layout="centered")

st.title("📈 Diferansiyel Denklemlerle Finansal Modelleme")
st.markdown("""
Bu simülasyon, bir yatırımın veya borcun sürekli bileşik faiz altındaki değişimini tanımlayan 
***dS/dt = rS + k*** diferansiyel denkleminin çözümünü görselleştirir. 
Parametre girişlerini **Aylık** veya **Yıllık** bazda seçebilirsiniz.
""")

# --- SOL MENÜ (PARAMETRE GİRİŞİ) ---
st.sidebar.header("Parametreler")

# 1. Başlangıç Sermayesi
S0 = st.sidebar.number_input("Başlangıç Sermayesi (S0)", value=10000, step=1000, 
                             help="Yatırımın başlangıçtaki miktarı.")

# --------------------------
st.sidebar.markdown("---") 
# --------------------------

# --- 1. YILLIK/AYLIK FAİZ SEÇİMİ VE HESAPLAMASI ---
st.sidebar.subheader("1. Faiz Oranı Giriş Tipi")
faiz_tipi = st.sidebar.radio(
    "Faiz Oranını Nasıl Gireceksiniz?",
    ('Aylık (%)', 'Yıllık (%)'),
    index=1 # Varsayılan olarak Yıllık seçili
)

# 2. Faiz Oranı Girişi
if faiz_tipi == 'Aylık (%)':
    r_girdi_percent = st.sidebar.slider("Aylık Faiz Oranı (%)", 
                                        min_value=0.01, max_value=2.0, 
                                        value=0.66, step=0.01, 
                                        help="Yıllık faizi 12'ye bölerek girin. (r / 12)")
    r_aylik = r_girdi_percent / 100 # Hesaplamada kullanılacak aylık ondalık oran
    r_yillik_percent = r_aylik * 12 # Basit çarpımla yıllık karşılığı
else: # Yıllık (%) seçiliyse
    r_girdi_percent = st.sidebar.slider("Yıllık Faiz Oranı (%)", 
                                        min_value=0.1, max_value=30.0, 
                                        value=8.0, step=0.1, 
                                        help="Yıllık faiz oranını girin. Örn: 8.0")
    # HATA DÜZELTİLDİ: Tüm parantezler kontrol edildi.
    r_aylik = (r_girdi_percent / 100) / 12 # Yıllık oranı 12'ye bölerek aylık ondalık oran bulunur
    r_yillik_percent = r_girdi_percent # Yıllık giriş direkt yansıtılır
    
# Görüntülenen Oranlar
st.sidebar.markdown(f"**Hesaplanan Aylık Faiz Oranı:** %{(r_aylik * 100):.4f}")
st.sidebar.markdown(f"**Girdiğiniz/Yansıyan Yıllık Faiz Oranı:** %{r_yillik_percent:.2f}")

# --------------------------
st.sidebar.markdown("---") 
# --------------------------

# --- 2. YILLIK/AYLIK NAKİT AKIŞI SEÇİMİ VE HESAPLAMASI ---
st.sidebar.subheader("2. Nakit Akışı (k) Giriş Tipi")
k_tipi = st.sidebar.radio(
    "Nakit Akışını Nasıl Gireceksiniz?",
    ('Aylık Nakit Akışı', 'Yıllık Nakit Akışı'),
    index=0 # Varsayılan olarak Aylık seçili
)

# 3. Nakit Akışı Girişi
if k_tipi == 'Aylık Nakit Akışı':
    k_girdi = st.sidebar.number_input("Aylık Nakit Akışı (k)", 
                                      value=166, step=10, 
                                      help="Her ay düzenli olarak yatırılan/çekilen miktar.")
    k_aylik = k_girdi # Hesaplamada kullanılacak aylık k
    k_yillik = k_aylik * 12 # Basit çarpımla yıllık karşılığı
    
else: # Yıllık Nakit Akışı seçiliyse
    k_girdi = st.sidebar.number_input("Yıllık Nakit Akışı", 
                                      value=2000, step=100, 
                                      help="Yıl boyunca toplam yatırılan/çekilen miktar.")
    k_aylik = k_girdi / 12 # Yıllık miktarı 12'ye bölerek aylık k bulunur
    k_yillik = k_girdi # Yıllık giriş direkt yansıtılır

# Görüntülenen Nakit Akışı
st.sidebar.markdown(f"**Hesaplanan Aylık Nakit Akışı (k):** ${k_aylik:,.2f}")
st.sidebar.markdown(f"**Girdiğiniz/Yansıyan Yıllık Nakit Akışı:** ${k_yillik:,.2f}")

# ----------------------------------------------------
st.sidebar.markdown("---") 
# --- VADE SEÇİMİ BÖLÜMÜ ---
st.sidebar.subheader("3. Vade Seçimi")
vade_tipi = st.sidebar.radio(
    "Vade Birimi:",
    ('Ay', 'Yıl'),
    index=1 # Varsayılan olarak Yıl seçili
)

if vade_tipi == 'Ay':
    t_girdi = st.sidebar.slider("Vade Süresi", min_value=12, max_value=720, value=480, step=12, help="Ay cinsinden süre.")
    t_aylik_max = t_girdi
    vade_etiketi = f"{t_girdi} Ay"
else: # Yıl
    t_girdi = st.sidebar.slider("Vade Süresi", min_value=1, max_value=60, value=40, step=1, help="Yıl cinsinden süre.")
    t_aylik_max = t_girdi * 12
    vade_etiketi = f"{t_girdi} Yıl ({t_aylik_max} Ay)"
    
# ----------------------------------------------------


# --- HESAPLAMA MOTORU ---

# Zaman dizisi oluşturma (Her ay için bir nokta)
t_aylik = np.linspace(0, t_aylik_max, t_aylik_max + 1)

# FORMÜL: S(t) = S0*e^(r*t) + (k/r)*(e^(r*t) - 1)
# Tüm değişkenler aylık olarak ayarlanmıştır.
if r_aylik == 0:
    # r=0 ise, S(t) = S0 + k*t
    S_t = S0 + k_aylik * t_aylik
else:
    S_t = S0 * np.exp(r_aylik * t_aylik) + (k_aylik / r_aylik) * (np.exp(r_aylik * t_aylik) - 1)

# Cepten Çıkan/Giren Ana Para (Faizsiz)
invested_cash = S0 + (k_aylik * t_aylik)

# Sonuç Değerleri
final_balance = S_t[-1]
total_invested = invested_cash[-1]
interest_gained = final_balance - total_invested

# --- GÖRSELLEŞTİRME ---

## Finansal Sonuçlar 💰

st.subheader("Finansal Sonuçlar")
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Birikim", f"${final_balance:,.2f}")
col2.metric("Cepten Çıkan Ana Para", f"${total_invested:,.2f}")
col3.metric("Kazanılan Faiz (Kaldıraç)", f"${interest_gained:,.2f}", delta_color="normal")


## Sermayenin Zaman İçindeki Değişimi 📊

st.subheader("Sermayenin Zaman İçindeki Değişimi")
fig, ax = plt.subplots(figsize=(10, 5))

# Toplam Bakiye Eğrisi
ax.plot(t_aylik, S_t, label='Sürekli Model (Toplam Para)', color='#1f77b4', linewidth=3)

# Ana Para Doğrusu
ax.plot(t_aylik, invested_cash, label='Yatırılan Ana Para', color='green', linestyle='--', linewidth=2)

# Aradaki Alanı Boyama (Faiz Getirisi)
ax.fill_between(t_aylik, invested_cash, S_t, color='#1f77b4', alpha=0.2, label='Bileşik Faiz Etkisi')

# Grafik Başlığına Vade Bilgisini Ekleme
ax.set_title(f"Sermaye Değişimi (Vade: {vade_etiketi}, Yıllık Faiz: %{r_yillik_percent:.2f})", fontsize=14)
ax.set_xlabel("Zaman (Ay)")
ax.set_ylabel("Tutar ($)")
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)
