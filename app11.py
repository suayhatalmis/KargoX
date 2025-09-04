#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 13:06:04 2025

@author: suayhatalmis
"""

import streamlit as st 
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(
    page_title="Kargo Fiyat Hesaplama",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS stilleri - Beyaz tema
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
    }
    .main-header { 
        text-align: center; 
        padding: 1.5rem 0; 
        margin-bottom: 1.5rem; 
    }
    .main-title { 
        font-size: 2.5rem; 
        font-weight: 800; 
        color: #2c3e50; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1); 
        margin-bottom: 0.3rem; 
    }
    .main-subtitle { 
        font-size: 1.1rem; 
        color: #6c757d; 
        font-weight: 300; 
    }
    .form-card { 
        background: rgba(255,255,255,0.95); 
        backdrop-filter: blur(10px); 
        border-radius: 15px; 
        padding: 1.5rem; 
        margin: 0.5rem 0; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
        border: 1px solid rgba(0,0,0,0.05); 
        height: fit-content;
    }

    .section-header { 
        font-size: 1.3rem; 
        font-weight: 700; 
        color: #2c3e50; 
        margin-bottom: 0.8rem; 
        padding-bottom: 0.3rem; 
        border-bottom: 2px solid #007bff; 
    }
    .info-box { 
        background: linear-gradient(135deg, #007bff, #0056b3); 
        color: white; 
        padding: 0.8rem; 
        border-radius: 10px; 
        margin: 0.5rem 0; 
        text-align: center; 
        box-shadow: 0 2px 8px rgba(0,123,255,0.3); 
    }
    .calculation-info {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 8px rgba(40,167,69,0.3);
    }
    .price-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        margin: 10px 0;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .price-header {
        padding: 12px 15px;
        color: white;
        font-weight: 600;
        text-align: center;
        font-size: 1.1rem;
    }
    .price-content {
        padding: 15px;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .price-total {
        padding: 12px 15px;
        color: white;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
    }
    /* Selectbox ve input alanlarını daraltma */
    .stSelectbox > div > div > div {
        max-width: 300px;
    }
    .stNumberInput > div > div > input {
        max-width: 150px;
    }
    .stMultiSelect > div > div > div {
        max-width: 400px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# VERİ OKUMA VE FONKSİYONLAR
# =========================
ILMESAFE_DOSYA = "ilmesafe.xlsx"

df = pd.read_excel(ILMESAFE_DOSYA, header=None)
iller_sutun = df.iloc[1, 2:].astype(str).str.strip().str.upper().values
iller_satir = df.iloc[2:, 1].astype(str).str.strip().str.upper().values
mesafe_df = df.iloc[2:, 2:]
mesafe_df.index = iller_satir
mesafe_df.columns = iller_sutun
mesafe_df = mesafe_df.apply(pd.to_numeric, errors='coerce').fillna(0)

def sehir_listesi_olustur(iller_listesi):
    """İstanbul ve Ankara'yı başa alarak şehir listesi oluşturur"""
    iller_set = set(iller_listesi)
    oncelikli_sehirler = []
    
    if "İSTANBUL" in iller_set:
        oncelikli_sehirler.append("İSTANBUL")
    if "ANKARA" in iller_set:
        oncelikli_sehirler.append("ANKARA")
    
    diger_sehirler = sorted([il for il in iller_listesi if il not in ["İSTANBUL", "ANKARA"]])
    
    return oncelikli_sehirler + diger_sehirler

def mesafe_bul(kaynak: str, hedef: str):
    kaynak = str(kaynak).strip().upper()
    hedef  = str(hedef).strip().upper()
    try:
        return mesafe_df.loc[kaynak, hedef]
    except KeyError:
        return None

def hat_belirle(mesafe: float) -> str:  
    if mesafe < 1: return "Şehiriçi"
    elif mesafe <= 200: return "Yakın Mesafe"
    elif mesafe <= 600: return "Kısa Mesafe"
    elif mesafe <= 1000: return "Orta Mesafe"
    else: return "Uzak Mesafe"

FIYAT_DOSYALAR = {
    "Yurtiçi Kargo": "yk_for_kg.xlsx",
    "Aras Kargo"   : "aras_for_kg.xlsx",
    "DHLeCommerce" : "dhl_ecommerce.xlsx",
    "Sürat Kargo"  : "surat_for_kg.xlsx",
}

EK_HIZMET_DOSYALAR = {
    "Yurtiçi Kargo":{"Telefon":28.89,"SMS":12.45},
    "Sürat Kargo"   : {"Telefon":7.00,"SMS":3.50},
    "DHLeCommerce" : {"Telefon":18.00,"SMS":4.00},
    "Aras Kargo"  : {"SMS":1.00},
}

def oku_fiyat(dosya):
    dfp = pd.read_excel(dosya, header=0)
    dfp = dfp.dropna(axis=1, how="all").dropna(axis=0, how="all")
    dfp.columns = dfp.columns.astype(str).str.strip().str.lower()
    if "kg/desi" in dfp.columns:
        dfp["kg/desi"] = pd.to_numeric(dfp["kg/desi"], errors="coerce")
    return dfp

def standard_bedel_bul(firma, hat_adi, kg_desi_deger, deger_turu_local):
    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])
    hat_col = hat_adi.strip().lower()
    mask = (dfp["kg/desi"] == kg_desi_deger)
    price = float(dfp.loc[mask, hat_col].values[0])
    return price  

def agir_tasima_bedeli(firma, deger_turu_local, kg_desi_deger):
    bedel = 0.0
    if deger_turu_local == "ağırlık":
        if firma == "Aras Kargo" and kg_desi_deger > 100: bedel = 5120
        elif firma == "Yurtiçi Kargo" and kg_desi_deger > 100: bedel = 3950
        elif firma == "Sürat Kargo" and kg_desi_deger > 100: bedel = 3500
        elif firma == "DHLeCommerce" and kg_desi_deger > 30: bedel = (kg_desi_deger - 30) * 74.99
    else:
        if firma == "DHLeCommerce" and kg_desi_deger > 50:
            ekstra_desi = kg_desi_deger - 50
            bedel = (ekstra_desi // 3) * 74.99
    return bedel

def vergileri_hesapla(firma, ara_toplam, deger_turu_local, kg_desi_deger):
    posta = 0.0
    if firma != "Aras Kargo":
        if deger_turu_local == "ağırlık" and kg_desi_deger <= 30:
            posta = ara_toplam * 0.0235
        elif deger_turu_local == "desi" and kg_desi_deger <= 100:
            posta = ara_toplam * 0.0235
    kdv=(ara_toplam+posta)*0.20
    return kdv, posta

def ek_hizmet_bedelleri(firma, kg_desi_deger, ek_hizmetler):
    kalemler = {"Adresten Alım": 0.0, "Adresten Teslim": 0.0, "Telefon": 0.0, "SMS": 0.0}
    if not ek_hizmetler:
        return kalemler

    firma_clean = firma.strip().upper()
    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])

    if any(h in ek_hizmetler for h in ["Adresten Alım", "Adresten Teslim"]):
        row = dfp.loc[dfp["kg/desi"] == kg_desi_deger].iloc[0]
        for h in ["Adresten Alım", "Adresten Teslim"]:
            col_name = h.lower()
            if h in ek_hizmetler and col_name in row.index:
                kalemler[h] = float(row[col_name]) if pd.notna(row[col_name]) else 0.0

    for h in ["Telefon", "SMS"]:
        if h in ek_hizmetler:
            for key, value in EK_HIZMET_DOSYALAR.items():
                if key.strip().upper() == firma_clean:
                    kalemler[h] = float(value.get(h, 0.0))

    return kalemler

# =========================
# BAŞLIK
# =========================
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📦 Kargo Fiyat Hesaplama</h1>
        <p class="main-subtitle">Türkiye'nin en hızlı kargo fiyat karşılaştırma platformu</p>
    </div>
""", unsafe_allow_html=True)

# =========================
# ANA LAYOUT - SOL VE SAĞ
# =========================
left_col, right_col = st.columns([1, 1])

# Şehir listelerini oluştur
nereden_listesi = sehir_listesi_olustur(iller_satir)
nereye_listesi = sehir_listesi_olustur(iller_sutun)

# SOL TARAF - FORM
with left_col:
    with st.container():
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        # Gönderi rotası
        st.markdown('<h2 class="section-header">🗺️ Gönderi Rotası</h2>', unsafe_allow_html=True)
        nereden = st.selectbox("🚀 Nereden:", nereden_listesi, key="nereden")
        nereye = st.selectbox("🎯 Nereye:", nereye_listesi, key="nereye")
        
        mesafe = mesafe_bul(nereden, nereye)
        if mesafe:
            hat = hat_belirle(mesafe)
            st.markdown(f"""
                <div class="info-box">
                    <h3>📏 Rota Bilgileri</h3>
                    <p><strong>Mesafe:</strong> {mesafe} km</p>
                    <p><strong>Hat Türü:</strong> {hat}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Mesafe bulunamadı!")
            st.stop()

        # Kargo detayları
        st.markdown('<h2 class="section-header">📦 Kargo Detayları</h2>', unsafe_allow_html=True)
        kargo_tipi = st.selectbox("Kargo tipini seçin:", ["Dosya", "Paket/Koli"])
        tasima_degeri, deger_turu = 0, "ağırlık"

        if kargo_tipi.lower() in ["paket/koli", "paket", "koli"]:
            kargo_sayisi = st.number_input("📦 Kaç adet kargo?", 1, 5, 1)
            toplam_desi, toplam_agirlik = 0, 0
            for i in range(int(kargo_sayisi)):
                with st.expander(f"📦 {i+1}. Kargo Detayları", expanded=(i==0)):
                    col1, col2 = st.columns(2)
                    with col1:
                        en = st.number_input(f"En (cm)", 0.0, step=1.0, key=f"en_{i}")
                        boy = st.number_input(f"Boy (cm)", 0.0, step=1.0, key=f"boy_{i}")
                    with col2:
                        yuk = st.number_input(f"Yükseklik (cm)", 0.0, step=1.0, key=f"yuk_{i}")
                        ag = st.number_input(f"Ağırlık (kg)", 0.0, step=0.1, key=f"ag_{i}")
                    if en>0 and boy>0 and yuk>0:
                        desi = en*boy*yuk/3000
                        toplam_desi += desi; toplam_agirlik += ag
            
            # Hesaplama bilgisi gösterimi
            if toplam_desi>0 or toplam_agirlik>0:
                tasima_degeri = int(max(toplam_desi, toplam_agirlik))
                deger_turu = "ağırlık" if toplam_agirlik>=toplam_desi else "desi"
                
                # Hesaplama temelini gösteren bilgi kutusu
                st.markdown(f"""
                    <div class="calculation-info">
                        <h4>⚖️ Hesaplama Temeli</h4>
                        <p><strong>Toplam Desi:</strong> {toplam_desi:.1f}</p>
                        <p><strong>Toplam Ağırlık:</strong> {toplam_agirlik:.1f} kg</p>
                        <p><strong>Fiyat Hesaplanacak Değer:</strong> {tasima_degeri} ({deger_turu.title()})</p>
                        <p style="font-size:0.85rem; opacity:0.9;">* Büyük olan değer baz alınır</p>
                    </div>
                """, unsafe_allow_html=True)

        elif kargo_tipi.lower()=="dosya":
            kargo_sayisi = st.number_input("📄 Kaç dosya?", 1, 5, 1)
            tasima_degeri = 0
            deger_turu = "ağırlık"
            
            # Dosya için bilgi kutusu
            st.markdown(f"""
                <div class="calculation-info">
                    <h4>📄 Dosya Hesaplama</h4>
                    <p><strong>Dosya Sayısı:</strong> {int(kargo_sayisi)}</p>
                    <p><strong>Hesaplama Temeli:</strong> Standart dosya tarifesi</p>
                </div>
            """, unsafe_allow_html=True)

        # Ek hizmetler
        st.markdown('<h2 class="section-header">⚡ Ek Hizmetler</h2>', unsafe_allow_html=True)
        ek_hizmetler = st.multiselect("Ek hizmetler:", ["Adresten Alım", "Adresten Teslim", "Telefon", "SMS"])
        
        # Hesaplama butonu
        st.markdown("<br>", unsafe_allow_html=True)
        hesapla_clicked = st.button("💰 Fiyatları Hesapla", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# SAĞ TARAF - SONUÇLAR
with right_col:
    if hesapla_clicked:
        st.markdown('<h2 style="color:#2c3e50; font-size:1.8rem; margin-bottom:1rem; text-align:center;">💰 Fiyat Karşılaştırması</h2>', unsafe_allow_html=True)
        
        standart_bedeller = {}
        for firma in FIYAT_DOSYALAR.keys():
            try:
                standart_bedeller[firma] = standard_bedel_bul(firma, hat, tasima_degeri, deger_turu)
            except Exception as e:
                st.warning(f"⚠️ {firma} fiyat hesaplanamadı: {e}")

        if standart_bedeller:
            firma_renkleri = {
                "Yurtiçi Kargo":"linear-gradient(135deg, #1976D2, #1565C0)",
                "Aras Kargo":"linear-gradient(135deg, #D32F2F, #C62828)",
                "DHLeCommerce":"linear-gradient(135deg, #F9A825, #F57F17)",
                "Sürat Kargo":"linear-gradient(135deg, #1A237E, #0D47A1)"
            }
            
            for firma, standart_bedel in standart_bedeller.items():
                agir_bedel = agir_tasima_bedeli(firma, deger_turu, tasima_degeri)
                kalemler = ek_hizmet_bedelleri(firma, tasima_degeri, ek_hizmetler)
                ek_hizmet_toplam = sum(kalemler.values())
                ara_toplam = standart_bedel + ek_hizmet_toplam + agir_bedel
                kdv, posta = vergileri_hesapla(firma, ara_toplam, deger_turu, tasima_degeri)
                genel_toplam = ara_toplam + posta + kdv
                renk = firma_renkleri.get(firma,"linear-gradient(135deg,#333,#555)")
                
                # Firma kartı
                st.markdown(f"""
                    <div class="price-card">
                        <div class="price-header" style="background:{renk};">
                            {firma}
                        </div>
                        <div class="price-content">
                            <div>💼 <strong>Standart Bedel:</strong> {standart_bedel:.2f} TL</div>
                """, unsafe_allow_html=True)
                
                if agir_bedel > 0:
                    st.markdown(f"<div>⚖️ <strong>Ağır Taşıma:</strong> {agir_bedel:.2f} TL</div>", unsafe_allow_html=True)
                
                if ek_hizmetler and ek_hizmet_toplam > 0:
                    st.markdown("<div>🔧 <strong>Ek Hizmetler:</strong></div>", unsafe_allow_html=True)
                    for h, v in kalemler.items():
                        if h in ek_hizmetler and v > 0:
                            st.markdown(f"<div>&nbsp;&nbsp;• {h}: {v:.2f} TL</div>", unsafe_allow_html=True)
                    st.markdown(f"<div><strong>Toplam Ek Hizmet:</strong> {ek_hizmet_toplam:.2f} TL</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div>🔧 <strong>Ek Hizmet:</strong> Yok</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div>📊 <strong>KDV (Posta dahil):</strong> {kdv:.2f} TL</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Fiyat gösterimi
                if firma == "Yurtiçi Kargo":
                    indirimli_fiyat = genel_toplam * 0.8
                    toplam= indirimli_fiyat+agir_bedel 
                    
                else:
                    toplam+=agir_bedel 
                    
                    st.markdown(f"""
                        <div class="price-total" style="background:linear-gradient(135deg, #28a745, #20c997);">
                            <div style="text-decoration:line-through; opacity:0.8; font-size:0.9rem;">{genel_toplam:.2f} TL</div>
                            <div>✨ İndirimli: {indirimli_fiyat:.2f} TL</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                    st.markdown(f"""
                        <div class="price-total" style="background:{renk};">
                            💰 {genel_toplam:.2f} TL
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("❌ Hiçbir firma için fiyat hesaplanamadı!")
    else:
        st.markdown("""
            <div style='text-align:center; padding:100px 20px; color:#6c757d;'>
                <h3>👈 Sol taraftan bilgileri girin</h3>
                <p style='font-size:1.1rem;'>Fiyat karşılaştırması için "Fiyatları Hesapla" butonuna basın</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<div style='text-align:center;margin-top:2rem;color:#6c757d;font-size:0.9rem;'>📦 Kargo Fiyat Hesaplama Sistemi</div>", unsafe_allow_html=True)

# =========================
# DİPNOTLAR / AÇIKLAMALAR
# =========================
st.markdown("""
    <div style="background:rgba(255,255,255,0.9); 
                padding:12px; 
                border-radius:10px; 
                margin-top:30px; 
                font-size:0.85rem; 
                color:#495057; 
                box-shadow:0 1px 3px rgba(0,0,0,0.1);
                border-left:3px solid #007bff;">
        <p style='margin:3px 0;'>* KKTC gönderileri dikkate alınmamıştır.</p>
        <p style='margin:3px 0;'>** DHL E-Commerce web sitesindeki gibi 20 kg'ın üstündeki ürünler için fiyat bilgisi sunmamaktadır.</p>
        <p style='margin:3px 0;'>*** Mesafe bilgileri şehir merkezleri arasındaki mesafe (km) baz alınarak hesaplanmıştır.</p>
        <p style='margin:3px 0;'>**** Girilen adrese bağlı olarak Adresten Alım ve Adrese Teslim hizmetleri kargo firmaları arasında değişkenlik gösterebilir.</p>
        <p style='margin:3px 0;'>***** Firmaların web sitelerinden yayınlanan Ocak 2025 tarihli fiyatlar dikkate alınmıştır. KDV (%20) ve Evrensel Posta Hizmet Bedeli (%2.35) dahildir.</p>
        <p style='margin:3px 0;'>****** Ödenecek net tutar şubede yapılacak olan ölçüm ve diğer kalemlere göre belirlenecektir.</p>
        <p style='margin:3px 0;'>******* Fiyatlara sigorta ücretleri eklenmiştir.</p>
    </div>
""", unsafe_allow_html=True)