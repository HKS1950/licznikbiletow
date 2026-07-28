from playwright.sync_api import sync_playwright
from datetime import datetime
import zoneinfo
import json
import time
import re
import os
import sys

EVENT_URL = "https://bilety.hutnikkrakow.com/zakup?p_p_id=com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_mvcRenderCommandName=%2Fticket%2Fselect%2Fseats&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_eventId=45705&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_backURL=%2Flista-wydarzen"

def pobierz_i_zapisz():
    strefa_pl = zoneinfo.ZoneInfo("Europe/Warsaw")
    teraz = datetime.now(strefa_pl).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{teraz}] Rozpoczynanie pobierania danych...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context_args = {
                "viewport": {'width': 1920, 'height': 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }

            if os.path.exists("state.json"):
                context_args["storage_state"] = "state.json"

            context = browser.new_context(**context_args)
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("Łączenie ze stroną biletową...")
            page.goto(EVENT_URL, wait_until="networkidle", timeout=60000)
            time.sleep(10)

            # Zapisujemy zrzut ekranu do weryfikacji
            page.screenshot(path="podglad_strony.png", full_page=True)

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

            print(f"✅ Zapisano wynik: {suma_wolnych} biletów o {teraz}")
            browser.close()

    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pobierz_i_zapisz()
