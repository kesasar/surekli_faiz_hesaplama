import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        width: 350px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Gerçek Tarihsel Kıyaslama", layout="centered")
st.title("📅 Gerçek Tarihsel Verilerle: Altın mı, Faiz mi?")
st.markdown("""
Bu simülasyon **tahmini değil, gerçek geçmiş verileri** kullanır.
Yahoo Finance üzerinden **Altın (ONS)** ve **Dolar/TL** verileri çekilerek, geçmişte yaptığınız yatırımların bugün ne kadar edeceği hesaplanır.
""")

# --- YAN MENÜ ---
st.sidebar.header("Yatırım Parametreleri")

# 1. Tarih Seçimi
start_date = st.sidebar.date_input("Başlangıç Tarihi", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("Bitiş Tarihi", value=pd.to_datetime("today"))

# 2. Para Girişi
S0 = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=100000, step=5000)
k_aylik = st.sidebar.number_input("Aylık Düzenli Ekleme (TL)", value=5000, step=500)

# 3. Kıyaslanacak Faiz Oranı
st.sidebar.markdown("---")
faiz_orani = st.sidebar.slider("Kıyaslanacak Ortalama Mevduat Faizi (Yıllık %)", 0, 100, 30, 
                               help="Banka faizleri sürekli değiştiği için, bu dönem için 'ortalama' bir oran giriniz.")

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data
def get_data(start, end):
    try:
        # İki veriyi tek listede istiyoruz, böylece tarihleri otomatik eşleşiyor
        tickers = ["GC=F", "TRY=X"]
        
        # Veriyi indir
        raw_data = yf.download(tickers, start=start, end=end, progress=False)
        
        # Sadece 'Close' (Kapanış) fiyatlarını al
        if "Close" in raw_data.columns:
            df = raw_data["Close"].copy()
        else:
            df = raw_data.copy()

        # GC=F -> Altın Ons, TRY=X -> Dolar/TL
        
        # Veri setinde bu sütunlar var mı kontrol et
        if "GC=F" in df.columns and "TRY=X" in df.columns:
            df = df[["GC=F", "TRY=X"]] # Sıralamayı garantiye al
            df.columns = ["Ons_USD", "USD_TRY"] # İsimleri basitleştir
        else:
            # Hata vermemek için boş dön
            st.error("Veri kaynağından beklenen semboller (GC=F, TRY=X) alınamadı.")
            return pd.DataFrame()

        # Eksik günleri (haftasonu vs.) önceki günün verisiyle doldur
        df = df.ffill()
        
        # Gram Altın (TL) Hesabı: (Ons * Dolar) / 31.1035
        df['Gram_TL'] = (df['Ons_USD'] * df['USD_TRY']) / 31.1035
        
        return df.dropna()
        
    except Exception as e:
        st.error(f"Veri işleme hatası: {e}")
        return pd.DataFrame()

# --- SİMÜLASYON MOTORU ---

if st.button("Simülasyonu Başlat"):
    with st.spinner('Piyasa verileri indiriliyor ve hesaplanıyor...'):
        df = get_data(start_date, end_date)

    if not df.empty:
        # Hesaplama Değişkenleri
        
        # 1. Altın Portföyü (Gram olarak tutacağız, sonra TL'ye çevireceğiz)
        total_grams = 0
        gold_balance_history = []
        
        # 2. Faiz Portföyü (TL olarak büyüyecek)
        faiz_balance = S0
        faiz_balance_history = []
        
        # 3. Cepten Çıkan Ana Para
        invested_cash = S0
        invested_history = []
        
        # Faiz Günlük Çarpanı (Bileşik Faiz Mantığı)
        # Yıllık %30 ise günlük etkiyi hesaplıyoruz
        daily_rate = (faiz_orani / 100) / 365
        
        # Aylık ekleme kontrolü için ay değişkeni
        current_month = df.index[0].month
        
        # --- İLK GÜN YATIRIMI ---
        initial_price = df['Gram_TL'].iloc[0]
        
        # Başlangıç parasıyla altın al
        total_grams += S0 / initial_price
        
        # --- GÜNLÜK DÖNGÜ ---
        for date, row in df.iterrows():
            price = row['Gram_TL']
            
            # --- AYLIK EKLEME KONTROLÜ ---
            # Eğer ay değiştiyse (yeni aya girdiysek) ekleme yap
            if date.month != current_month:
                # Altına ekle (o günkü fiyattan gram al)
                total_grams += k_aylik / price
                
                # Faize ekle (kasaya para giriyor)
                faiz_balance += k_aylik
                
                # Cepten çıkana ekle
                invested_cash += k_aylik
                
                # Ayı güncelle
                current_month = date.month
            
            # --- FAİZİN GÜNLÜK İŞLEYİŞİ ---
            # Her gün para, günlük faiz oranı kadar büyür
            faiz_balance = faiz_balance * (1 + daily_rate)
            
            # --- KAYIT TUTMA (GRAFİK İÇİN) ---
            # O anki toplam altın değeri (Gram * Fiyat)
            gold_value = total_grams * price
            
            gold_balance_history.append(gold_value)
            faiz_balance_history.append(faiz_balance)
            invested_history.append(invested_cash)

        # Hesaplanan listeleri DataFrame'e ekle
        df['Altın_Bakiye'] = gold_balance_history
        df['Faiz_Bakiye'] = faiz_balance_history
        df['Ana_Para'] = invested_history
        
        # --- SONUÇLAR VE METRİKLER ---
        final_gold = df['Altın_Bakiye'].iloc[-1]
        final_faiz = df['Faiz_Bakiye'].iloc[-1]
        final_invested = df['Ana_Para'].iloc[-1]
        
        # Kazananı Belirle
        diff = final_gold - final_faiz
        winner = "ALTIN" if final_gold > final_faiz else "MEVDUAT FAİZİ"
        
        st.markdown("---")
        st.subheader("🏁 Sonuç Tablosu")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Yatırılan Para", f"{final_invested:,.0f} TL")
        
        # Faiz Metriği
        faiz_kar_orani = (final_faiz / final_invested - 1) * 100
        c2.metric("Mevduat Faizi Sonucu", f"{final_faiz:,.0f} TL", 
                  delta=f"%{faiz_kar_orani:.1f} Getiri")
        
        # Altın Metriği
        altin_kar_orani = (final_gold / final_invested - 1) * 100
        c3.metric("Gerçek Altın Sonucu", f"{final_gold:,.0f} TL", 
                  delta=f"%{altin_kar_orani:.1f} Getiri", delta_color="normal")
        
        # Sonuç Mesajı
        if final_gold > final_faiz:
             st.success(f"Bu dönemde **ALTIN** yatırımı daha kârlı oldu. Aradaki fark: **{abs(diff):,.0f} TL**")
        else:
             st.info(f"Bu dönemde **FAİZ** yatırımı daha kârlı oldu. Aradaki fark: **{abs(diff):,.0f} TL**")

        # --- GRAFİK ÇİZİMİ ---
        st.subheader("📈 Zaman İçindeki Gerçek Değişim")
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Çizgiler
        ax.plot(df.index, df['Altın_Bakiye'], label='Altın (Gerçek Piyasa)', color='gold', linewidth=2.5)
        ax.plot(df.index, df['Faiz_Bakiye'], label=f'Mevduat (Ort. %{faiz_orani})', color='blue', linewidth=2.5)
        ax.plot(df.index, df['Ana_Para'], label='Yatırılan Ana Para', color='gray', linestyle='--', alpha=0.7)
        
        # Kazanan alanı boyama
        if final_gold > final_faiz:
            ax.fill_between(df.index, df['Faiz_Bakiye'], df['Altın_Bakiye'], color='gold', alpha=0.15, label='Altın Farkı')
        else:
            ax.fill_between(df.index, df['Altın_Bakiye'], df['Faiz_Bakiye'], color='blue', alpha=0.15, label='Faiz Farkı')
            
        ax.set_title("Altın vs Faiz (Gerçek Tarihsel Veri)", fontsize=12)
        ax.set_ylabel("Portföy Değeri (TL)")
        ax.set_xlabel("Yıl")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        
        # Y eksenini binlik ayraçlı yap (100,000 gibi)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        st.pyplot(fig)
        
        # Bilgi Notu
        st.caption(f"Veriler Yahoo Finance (GC=F, TRY=X) üzerinden anlık çekilmiştir. Son Hesaplanan Gram Altın: {df['Gram_TL'].iloc[-1]:.2f} TL")
        
    else:
        st.warning("Veri çekilemedi veya seçilen tarih aralığında veri yok.")

else:
    st.info("👈 Soldaki parametreleri ayarlayıp 'Simülasyonu Başlat' butonuna basın.")
