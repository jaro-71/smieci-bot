from fastapi import FastAPI
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs

app = FastAPI()

@app.get("/")
def get_waste_schedule():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    with sync_playwright() as p:
        # Uruchamiamy przeglądarkę z trybem "slow_mo", aby nie być zbyt agresywnym dla serwera
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # 1. Wchodzimy na stronę i czekamy, aż sieć będzie spokojna (networkidle)
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 2. CZEKAMY NA POJAWIENIE SIĘ LINKU PDF (max 15 sekund)
            # Szukamy dowolnego linku <a>, który w href ma 'download' i 'pdf'
            try:
                page.wait_for_selector("a[href*='download'][href*='pdf']", timeout=15000)
            except:
                # Jeśli nie znalazł, spróbujmy poszukać dowolnego linku z 'download'
                try:
                    page.wait_for_selector("a[href*='download']", timeout=5000)
                except:
                    browser.close()
                    return {"error": "Przycisk PDF nie pojawił się na stronie w określonym czasie"}
            
            # Pobieramy element linku
            pdf_link_element = page.query_selector("a[href*='download']")
            pdf_url = pdf_link_element.get_attribute("href")
            
            if not pdf_url:
                browser.close()
                return {"error": "Znaleziono element, ale nie ma on adresu URL"}
            
            if pdf_url.startswith("/"):
                pdf_url = "https://ekosystem.wroc.pl" + pdf_url
            
            # 3. WYCIĄGAMY DANE Z URL
            parsed_url = urlparse(pdf_url)
            params = parse_qs(parsed_url.query)
            
            schedule = []
            for i in range(1, 32):
                kiedy = params.get(f"kiedy_{i}")
                co = params.get(f"co_{i}")
                if kiedy and co:
                    date_parts = kiedy[0].split('-')
                    if len(date_parts) == 3:
                        formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
                        schedule.append({"date": formatted_date, "type": co[0]})
            
            browser.close()
            return schedule if schedule else {"error": "Link znaleziony, ale nie zawiera dat w parametrach"}
            
        except Exception as e:
            browser.close()
            return {"error": f"Krytyczny błąd bota: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
