import streamlit as st
import json
import os
from datetime import datetime
import zoneinfo

st.set_page_config(page_title="Licznik Biletów - Hutnik Kraków", page_icon="🎟️", layout="centered")

st.title("🎟️ Licznik Biletów – Hutnik Kraków")
st.caption("Oficjalny podgląd wolnych miejsc na stadionie")

# --- POPRAWKA DATY MECZU ---
st.info("📅 **Najbliższy mecz:** Hutnik Kraków vs. Opponent — **Sobota, 1 sierpnia**")

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

if os.path.exists("bilety_data.json"):
    with open("bilety_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    suma = data.get("suma_wolnych", 0)
    ostatnia_aktualizacja = data.get("ostatnia_aktualizacja", "Brak danych")
    ile_temu = naciagnij_czas_relatywny(ostatnia_aktualizacja)
    sektory = data.get("sektory", {})

    st.metric(label="ŁĄCZNIE WOLNYCH BIELETÓW", value=suma)
    
    if ile_temu:
        st.caption(f"🔄 Ostatnia aktualizacja: **{ostatnia_aktualizacja}** ({ile_temu})")
    else:
        st.caption(f"🔄 Ostatnia aktualizacja: **{ostatnia_aktualizacja}**")

    st.markdown("---")
    st.subheader("Miejsca w poszczególnych sektorach:")

    if sektory:
        cols = st.columns(2)
        for idx, (sektor, ilosc) in enumerate(sektory.items()):
            col = cols[idx % 2]
            col.metric(label=f"Sektor {sektor}", value=ilosc)
    else:
        st.write("Brak szczegółowych danych o sektorach.")
else:
    st.warning("Oczekiwanie na pierwsze dane z systemu lokalnego...")
