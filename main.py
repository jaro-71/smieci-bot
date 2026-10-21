from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import re

app = FastAPI()

@app.get("/")
def get_waste_schedule():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    with sync_//playwright() as p:
        # Uruchamiamy przeglądarkę
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # Wchodzimy na stronę i czekamy na załadowanie treści
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Czekamy chwilę na wykonanie skryptów JavaScript
            page.wait_for_timeout(3000)
            
            # KLUCZOWA ZMIANA: Pobieramy tylko widoczny tekst ze strony (to co widzi człowiek)
            # Ignorujemy cały kod HTML, bierzemy czysty tekst
            body_text = page.inner_text("body")
            
            # Szukamy wzorca: Data (dd.mm.rrrr) oraz tekst po niej
            # Szukamy wszystkich dat w tekście
            data = []
            date_pattern = r'(\d{1,2}\.\d{1,2}\.\d{4})'
            
            # Dzielimy tekst na linie, aby łatwiej przypisać datę do rodzaju odpadów
            lines = body_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Jeśli linia zawiera datę
                match = re.search(date_pattern, line)
                if match:
                    date_val = match.group(1)
                    # Usuwamy datę z linii, aby został sam rodzaj odpadów
                    waste_type = line.replace(date_val, '').strip()
                    
                    # Odrzucamy linie, które są tylko datą lub mają dziwne znaki
                    if waste_type and len(waste_type) < 50:
                        if not any(item['date'] == date_val for item in data):
                            data.append({"date": date_val, "type": waste_type})
            
            browser.close()
            
            if not data:
                return {"error": "Nie znaleziono dat w tekście strony", "debug_text": body_text[:200]}
            
            return data
            
        except Exception as e:
            browser.close()
            return {"error": f"Błąd bota: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
