from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import re

app = FastAPI()

@app.get("/")
def get_waste_schedule():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    with sync_playwright() as p:
        # Uruchamiamy przeglądarkę w trybie "headless" (bez okna)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Wchodzimy na stronę i czekamy, aż załaduje się główna treść
            page.goto(url, wait_until="networkidle")
            
            # Czekamy dodatkowe 2 sekundy, aby JavaScript dorysował tabelę
            page.wait_for_timeout(2000)
            
            # Pobieramy cały kod HTML strony po wykonaniu skryptów JS
            content = page.content()
            
            # Wyciąganie danych za pomocą Regex (szukamy dat i typów odpadów)
            data = []
            # Szukamy wzorców daty (dd.mm.rrrr) i tekstu obok niej
            # To jest uproszczony parser, który wyciąga daty z tabeli
            rows = re.findall(r'<td>(\d{1,2}\.\d{1,2}\.\d{4})</td>\s*<td>([^<]+)</td>', content)
            
            for date, waste_type in rows:
                data.append({"date": date, "type": waste_type.strip()})
            
            browser.close()
            return data if data else {"error": "Nie znaleziono danych w tabeli"}
            
        except Exception as e:
            browser.close()
            return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
