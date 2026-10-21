from fastapi import FastAPI
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs

app = FastAPI()

@app.get("/")
def get_waste_schedule():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # 1. Wchodzimy na stronę
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            # 2. SZUKAMY LINKU PO TEKCIE "POBIERZ HARMONOGRAM"
            # Szukamy wszystkich linków <a>
            links = page.query_selector_all("a")
            pdf_url = None
            
            for link in links:
                text = link.inner_text()
                href = link.get_attribute("href")
                if text and "POBIERZ HARMONOGRAM" in text.upper():
                    pdf_url = href
                    break
            
            if not pdf_url:
                browser.close()
                return {"error": "Nie znaleziono linku 'POBIERZ HARMONOGRAM'"}
            
            # Uzupełniamy adres URL, jeśli jest względny
            if pdf_url.startswith("/"):
                pdf_url = "https://ekosystem.wroc.pl" + pdf_url
            
            # 3. WYCIĄGAMY DANE Z ADRESU URL
            parsed_url = urlparse(pdf_url)
            params = parse_qs(parsed_url.query)
            
            schedule = []
            # Wyciągamy pary kiedy_i i co_i
            for i in range(1, 32):
                kiedy = params.get(f"kiedy_{i}")
                co = params.get(f"co_{i}")
                if kiedy and co:
                    # Formatowanie daty z 2026-10-21 na 21.10.2026
                    date_parts = kiedy[0].split('-')
                    if len(date_parts) == 3:
                        formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
                        schedule.append({
                            "date": formatted_date, 
                            "type": co[0]
                        })
            
            browser.close()
            
            if not schedule:
                return {"error": "Link znaleziony, ale nie zawiera dat wywozu"}
            
            return schedule
            
        except Exception as e:
            browser.close()
            return {"error": f"Błąd bota: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
