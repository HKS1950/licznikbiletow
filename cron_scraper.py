from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import time
import re

EVENT_URL = "https://bilety.hutnikkrakow.com/zakup?p_p_id=com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_mvcRenderCommandName=%2Fticket%2Fselect%2Fseats&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_eventId=45705&_com_stellis_ticketing_ticket_sale_TicketSaleWebPortlet_backURL=%2Flista-wydarzen"

def pobierz_i_zapisz():
    teraz = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{teraz}] Rozpoczynanie pobierania danych...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--start-maximized']
        )
        
        try:
            context = browser.new_context(storage_state="state.json", viewport={'width': 1920, 'height': 1080})
        except Exception as e:
            print(f"Błąd sesji: {e}")
            browser.close()
            return

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.goto(EVENT_URL, wait_until="domcontentloaded")
        time.sleep(7)

        # Pobieramy nagłówek/tytuł meczu bezpośrednio ze strony
        nazwa_meczu = "Hutnik Kraków"
        try:
            naglowek = page.locator('.event-title, h1, h2, .event-name').first.inner_text()
            if naglowek:
                nazwa_meczu = naglowek.strip()
        except Exception:
            pass

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
            "nazwa_meczu": nazwa_meczu,
            "suma_wolnych": suma_wolnych,
            "sektory": unikalne_sektory
        }

        with open("bilety_data.json", "w", encoding="utf-8") as f:
            json.dump(wynik, f, ensure_ascii=False, indent=2)

        print(f" Zapisano! Mecz: {nazwa_meczu} | Liczba wolnych miejsc: {suma_wolnych}")
        browser.close()

if __name__ == "__main__":
    pobierz_i_zapisz()
