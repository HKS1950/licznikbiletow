import streamlit as st
import json
import os
from datetime import datetime
import zoneinfo

st.set_page_config(page_title="Licznik Biletów - Hutnik Kraków", page_icon="🎟️", layout="centered")

def naciagnij_czas_relatywny(data_str):
    try:
        strefa_pl = zoneinfo.ZoneInfo("Europe/Warsaw")
        teraz = datetime.now(strefa_pl)
        ostatnia = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=strefa_pl)
        
        roznica = teraz - ostatnia
        minuty = int(roznica.total_seconds() / 60)
        
        if minuty < 2:
            return "przed chwilą"
        elif minuty < 60:
            return f"{minuty} min temu"
        else:
            godziny = minuty // 60
            return f"{godziny} godz. temu"
    except:
        return ""

# Tytuł i Nagłówek
st.title("🎟️ Licznik Biletów – Hutnik Kraków")

if os.path.exists("bilety_data.json"):
    with open("bilety_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    suma = data.get("suma_wolnych", 0)
    ostatnia_aktualizacja = data.get("ostatnia_aktualizacja", "Brak danych")
    ile_temu = naciagnij_czas_relatywny(ostatnia_aktualizacja)
    sektory = data.get("sektory", {})

    # Główny licznik
    st.metric(label="ŁĄCZNIE WOLNYCH BILETÓW", value=f"{suma}")
    if ile_temu:
        st.caption(f"🔄 Ostatnia aktualizacja: {ostatnia_aktualizacja} ({ile_temu})")
    else:
        st.caption(f"🔄 Ostatnia aktualizacja: {ostatnia_aktualizacja}")

    st.markdown("---")
    st.subheader("Wolne miejsca w sektorach:")

    # Wyświetlanie sektorów w ładnej siatce
    if sektory:
        cols = st.columns(3)
        idx = 0
        for sektor, ilosc in sektory.items():
            with cols[idx % 3]:
                st.metric(label=f"Sektor {sektor}", value=ilosc)
            idx += 1
    else:
        st.info("Brak danych o poszczególnych sektorach.")
else:
    st.warning("Oczekiwanie na dane...")
