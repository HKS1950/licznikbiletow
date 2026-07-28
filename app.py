import streamlit as st
import json
import os
from datetime import datetime
import zoneinfo

st.set_page_config(
    page_title="Licznik Biletów - Hutnik Kraków", 
    page_icon="🎟️", 
    layout="centered"
)

# Ukrywamy domyślny nagłówek Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

# 1. KARTA MECZU (GÓRNA)
st.markdown("""
    <div style="
        background-color: #ffffff;
        border-left: 6px solid #0056b3;
        border-right: 6px solid #0056b3;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 8px;">
            <img src="https://bilety.hutnikkrakow.com/documents/20121/0/logo_hutnik.png" width="38" style="vertical-align: middle;">
            <span style="font-size: 24px; font-weight: 800; color: #0056b3;">Hutnik Kraków vs Świt Szczecin</span>
        </div>
        <div style="font-size: 16px; color: #555555; font-weight: 500;">
            🗓️ Sobota, 2 sierpnia 2026 r. | ⏰ godz. 17:00
        </div>
    </div>
""", unsafe_allow_html=True)

# Odczyt danych z pliku
suma = 0
ostatnia_aktualizacja = "Brak danych"

if os.path.exists("bilety_data.json"):
    try:
        with open("bilety_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            suma = data.get("suma_wolnych", 0)
            ostatnia_aktualizacja = data.get("ostatnia_aktualizacja", "Brak danych")
    except Exception:
        pass

# 2. GLÓWNY NIEBIESKI BANER LICZNIKA
st.markdown(f"""
    <div style="
        background-color: #0066cc;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 102, 204, 0.25);
        margin-bottom: 20px;
    ">
        <div style="font-size: 15px; font-weight: 700; letter-spacing: 1.5px; opacity: 0.9; margin-bottom: 10px;">
            POZOSTAŁO WOLNYCH BILETÓW
        </div>
        <div style="font-size: 96px; font-weight: 900; line-height: 1; text-shadow: 0 2px 10px rgba(0,0,0,0.15);">
            {suma}
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. CZAS SYNCHRONIZACJI
st.markdown(f"""
    <div style="text-align: center; color: #666666; font-size: 14px; margin-bottom: 25px;">
        🕒 Ostatnia synchronizacja danych: <b>{ostatnia_aktualizacja}</b>
    </div>
""", unsafe_allow_html=True)

# 4. PRZYCISK ODŚWIEŻANIA
if st.button("🔄 Odśwież stan biletów"):
    st.rerun()
