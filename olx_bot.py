import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

TOKEN = os.environ.get("8868827541:AAGbRx_aLUzEtCzy0xoqy0SA4zTtbl7X7g0")
CHAT_ID = os.environ.get("6622891862")
URL_OLX = os.environ.get("https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/czestochowa/q-iphone/?search%5Bdist%5D=50&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=1500")

def wyslij_zdjecie_z_opisem(zdjecie_url, podpis):
    """Funkcja wysyłająca zdjęcie wraz z opisem na Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID, 
        "photo": zdjecie_url,
        "caption": podpis, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Błąd wysyłania zdjęcia do Telegrama: {e}")

def main():
    print("Uruchamiam sprawdzanie OLX ze zdjęciami w chmurze...")
    
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

        for oferta in oferty[:5]:
            tytul_elem = oferta.find('h4')
            link_elem = oferta.find('a')
            cena_elem = oferta.find('p', {'data-testid': 'ad-price'})
            img_elem = oferta.find('img')
            
            if tytul_elem and link_elem:
                tytul = tytul_elem.text.strip()
                href = link_elem.get('href', '')
                link = "https://www.olx.pl" + href if href.startswith("/d/") else href
                cena = cena_elem.text.strip() if cena_elem else "Brak ceny"
                
                # Pobieramy link do zdjęcia (OLX często używa atrybutu src lub data-src)
                zdjecie_url = ""
                if img_elem:
                    zdjecie_url = img_elem.get('src') or img_elem.get('data-src', '')
                
                # Przygotowujemy ładny podpis pod zdjęcie
                podpis = (
                    f"🚨 *Nowy iPhone na OLX!*\n\n"
                    f"📌 *{tytul}*\n"
                    f"💰 **Cena:** {cena}\n\n"
                    f"[🔗 Zobacz ogłoszenie]({link})"
                )
                
                # Jeśli udało się znaleźć zdjęcie, wysyłamy jako fotkę, w przeciwnym razie zwykły tekst
                if zdjecie_url and zdjecie_url.startswith("http"):
                    wyslij_zdjecie_z_opisem(zdjecie_url, podpis)
                else:
                    # Awaryjnie zwykła wiadomość tekstowa, gdyby zdjęcie nie było dostępne
                    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(url_text, json={"chat_id": CHAT_ID, "text": podpis, "parse_mode": "Markdown"})
                
        print("Wysłano powiadomienia ze zdjęciami.")

    except Exception as e:
        print(f"Błąd podczas pobierania OLX: {e}")

if __name__ == "__main__":
    main()
