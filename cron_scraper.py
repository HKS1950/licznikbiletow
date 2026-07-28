from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import time
import re
import os

EVENT_URL = "https://bilety.hutnikkrakow.com/zakup?p_p_id=com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_mvcRenderCommandName=%2Fticket%2Fselect%2Fseats&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_eventId=45705&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_backURL=%2Flista-wydarzen"

def pobierz_i_zapisz():
    teraz = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{teraz}] Rozpoczynanie pobierania danych w chmurze...")

    with sync_playwright() as p:
        # Konfiguracja bezpieczna dla headless Ubuntu w GitHub Actions
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--headless=new',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Sprawdzamy czy plik sesji istnieje
        context_args = {"viewport": {'width': 1920, 'height': 1080}}
        if os.path.exists("state.json"):
            context_args["storage_state"] = "state.json"
            print("Wczytano state.json")
        else:
            print("Ostrzeżenie: brak state.json, próba otwarcia bez sesji...")

        context = browser.new_context(**context_args)
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("Łączenie ze stroną biletową...")
        page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(7)

        surowy_tekst = page.locator('body').inner_text()

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
            if nazwa.lower() not in ['miejsc', 'sektorach', 'w', 'liczba', 'wolnych']:
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

        print(f" Sukces! Zapisano wolnych miejsc: {suma_wolnych}")
        browser.close()

if __name__ == "__main__":
    pobierz_i_zapisz()
