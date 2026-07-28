import streamlit as st
import json
import os
import base64

# Ustawienia strony
st.set_page_config(
    page_title="Licznik Biletów - Hutnik Kraków",
    page_icon="⚽",
    layout="centered"
)

# Funkcja do zamiany pliku obrazu na format wbudowany (base64) dla HTML
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return None

# Próba wczytania pliku logo.png lub logo.jpg
logo_base64 = get_base64_image("logo.png") or get_base64_image("logo.jpg")

if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 28px; vertical-align: middle; margin-right: 8px; margin-bottom: 3px;">'
else:
    logo_html = '⚽ '

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f6;
    }
    
    /* Sekcja z meczem - teraz w pełni symetryczna! */
    .match-box {
        background-color: #ffffff;
        border-left: 6px solid #00529b;
        border-right: 6px solid #00529b;
        padding: 18px 20px;
        border-radius: 12px;
        margin-top: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        text-align: center;
    }

    .match-teams {
        font-size: 1.35rem;
        font-weight: 800;
        color: #00529b;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .match-details {
        font-size: 0.95rem;
        color: #495057;
        font-weight: 500;
    }

    /* Główna karta licznika */
    .ticket-card {
        background: linear-gradient(135deg, #00529b 0%, #0072ce 100%);
        border-radius: 20px;
        padding: 35px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 25px rgba(0, 82, 155, 0.25);
        margin-bottom: 20px;
    }
    
    .ticket-title {
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.9;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    .ticket-count {
        font-size: 5.2rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
        text-shadow: 0 3px 12px rgba(0,0,0,0.25);
    }

    /* Przyciski i elementy interfejsu */
    .stButton>button {
        width: 100%;
        background-color: #00529b;
        color: white;
        border-radius: 12px;
        padding: 12px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #003a6e;
        color: white;
    }
    
    .time-info {
        text-align: center;
        color: #6c757d;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Baner meczowy
st.markdown(f"""
    <div class="match-box">
        <div class="match-teams">{logo_html} Hutnik Kraków vs Świt Szczecin</div>
        <div class="match-details">📅 Sobota, 2 sierpnia 2026 r. | ⏰ godz. 17:00</div>
    </div>
""", unsafe_allow_html=True)

DATA_FILE = "bilety_data.json"

def wczytaj_dane():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

dane = wczytaj_dane()

if dane:
    wolne = dane.get("suma_wolnych", 0)
    ostatnia_aktualizacja = dane.get("ostatnia_aktualizacja", "Brak danych")

    # Karta Licznika
    st.markdown(f"""
        <div class="ticket-card">
            <div class="ticket-title">Pozostało Wolnych Biletów</div>
            <div class="ticket-count">{wolne}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="time-info">🕒 Ostatnia synchronizacja danych: <b>{ostatnia_aktualizacja}</b></div>', unsafe_allow_html=True)

else:
    st.warning("Trwa wczytywanie danych...")

if st.button("🔄 Odśwież stan biletów"):
    st.rerun()