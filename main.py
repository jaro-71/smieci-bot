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
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            pdf_link_element = page.query_selector("a[href*='pdf']")
            
            if not pdf_link_element:
                browser.close()
                return {"error": "Nie znaleziono przycisku PDF"}
            
            pdf_url = pdf_link_element.get_attribute("href")
            if pdf_url.startswith("/"):
                pdf_url = "https://ekosystem.wroc.pl" + pdf_url
            
            parsed_url = urlparse(pdf_url)
            params = parse_qs(parsed_url.query)
            
            schedule = []
            for i in range(1, 32):
                kiedy = params.get(f"kiedy_{i}")
                co = params.get(f"co_{i}")
                if kiedy and co:
                    date_parts = kiedy[0].split('-')
                    formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
                    schedule.append({"date": formatted_date, "type": co[0]})
            
            browser.close()
            return schedule if schedule else {"error": "Brak danych w linku PDF"}
            
        except Exception as e:
            browser.close()
            return {"error": f"Błąd: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
