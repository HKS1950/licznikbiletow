import requests
from bs4 import BeautifulSoup
from datetime import datetime
import zoneinfo
import json
import re
import os
import sys

# ---------------------------------------------------------
# WKLEJ SWÓJ KLUCZ API Z SCRAPERAPI PONIŻEJ:
API_KEY = "4865682d6d2dcad82d3580c3187e1fca"
# ---------------------------------------------------------

TARGET_URL = "https://bilety.hutnikkrakow.com/zakup?p_p_id=com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_mvcRenderCommandName=%2Fticket%2Fselect%2Fseats&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_eventId=45705&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_backURL=%2Flista-wydarzen"

def pobierz_i_zapisz():
    strefa_pl = zoneinfo.ZoneInfo("Europe/Warsaw")
    teraz = datetime.now(strefa_pl).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{teraz}] Pobieranie danych przez ScraperAPI...")

    session = requests.Session()

    # Jeśli w repozytorium znajduje się state.json, dołączamy ciasteczka sesji
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                state = json.load(f)
                cookies = state.get("cookies", [])
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
            print("🔑 Pomyślnie załadowano ciasteczka sesji z state.json")
        except Exception as e:
            print(f"⚠️ Nie udało się wczytać state.json: {e}")

    # Zapytanie proxy z wymuszeniem renderowania JS
    proxy_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={TARGET_URL}&render=true"

    try:
        response = session.get(proxy_url, timeout=90)
        
        if response.status_code != 200:
            print(f"❌ Odpowiedź serwera: {response.status_code}")
            sys.exit(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        surowy_tekst = soup.get_text()

        if "LICZBA WOLNYCH MIEJSC W SEKTORACH:" in surowy_tekst:
            sektory_blok = surowy_tekst.split("LICZBA WOLNYCH MIEJSC W SEKTORACH:")[1]
            sektory_blok = sektory_blok.split("Wybierz miejsca")[0].split("Oficjalny serwis")[0]
        else:
            sektory_blok = surowy_tekst

        linie = [l.strip() for l in sektory_blok.split('\n') if l.strip()]
        pelny_string = " ".join(linie)

        pary = re.findall(r'([A-Za-z0-9ĄĆĘŁŃÓŚŹŻąćęłńóśźż]+)\s+(\d+)', pelny_string)

        suma_wolnych = 0
        unikalne_sektory = {}

        for nazwa, liczba in pary:
            if nazwa.lower() not in ['miejsc', 'sektorach', 'w', 'liczba', 'wolnych', 'zaloguj', 'rejestracja']:
                miejsca = int(liczba)
                unikalne_sektory[nazwa] = miejsca

        for wolne in unikalne_sektory.values():
            suma_wolnych += wolne

        wynik = {
            "ostatnia_aktualizacja": teraz,
            "suma_wolnych": suma_wolnych,
            "sektory": unikalne_sektory
        }

        with open("bilety_data.json", "w", encoding="utf-8") as f:
            json.dump(wynik, f, ensure_ascii=False, indent=2)

        print(f"✅ SUKCES W CHMURZE! Zapisano biletów: {suma_wolnych} o {teraz}")

    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pobierz_i_zapisz()
