import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Pobieramy dane z tzw. "Secrets" na GitHubie (bezpieczny schowek na hasła)
TOKEN = os.environ.get("8868827541:AAGbRx_aLUzEtCzy0xoqy0SA4zTtbl7X7g0")
CHAT_ID = os.environ.get("6622891862")
URL_OLX = os.environ.get("https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/czestochowa/q-iphone/?search%5Bdist%5D=50&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=1500")

def wyslij_powiadomienie(tekst):
    """Funkcja wysyłająca wiadomość na Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": tekst, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Błąd wysyłania do Telegrama: {e}")

def main():
    print("Uruchamiam sprawdzanie OLX w chmurze...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page.goto(URL_OLX, timeout=60000)
            page.wait_for_selector('div[data-cy="l-card"]', timeout=15000)
            html = page.content()
            browser.close()
            
        soup = BeautifulSoup(html, "html.parser")
        oferty = soup.select('div[data-cy="l-card"]')
        
        if not oferty:
            print("Brak ofert na stronie.")
            return

        # Dla uproszczenia w chmurze – wysyłamy np. 3 pierwsze znalezione ogłoszenia
        # (Możemy też dopisać plik historii, ale na początek zobaczmy, czy zadziała)
        licznik = 0
        for oferta in oferty[:5]:
            tytul_elem = oferta.find('h4')
            link_elem = oferta.find('a')
            cena_elem = oferta.find('p', {'data-testid': 'ad-price'})
            
            if tytul_elem and link_elem:
                tytul = tytul_elem.text.strip()
                href = link_elem.get('href', '')
                link = "https://www.olx.pl" + href if href.startswith("/d/") else href
                cena = cena_elem.text.strip() if cena_elem else "Brak ceny"
                
                wiadomosc = (
                    f"🚨 *Oferta z OLX (GitHub)*\n\n"
                    f"📌 *{tytul}*\n"
                    f"💰 **Cena:** {cena}\n\n"
                    f"[🔗 Zobacz ogłoszenie]({link})"
                )
                wyslij_powiadomienie(wiadomosc)
                licznik += 1
                
        print( "Wysłano powiadomienia o ofertach.")

    except Exception as e:
        print(f"Błąd podczas pobierania OLX: {e}")

if __name__ == "__main__":
    main()
