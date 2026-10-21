from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

@app.get("/")
def debug_links():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)
            
            # Pobieramy absolutnie wszystkie linki <a> z całej strony
            links = page.query_selector_all("a")
            all_urls = []
            
            for link in links:
                href = link.get_attribute("href")
                text = link.inner_text()
                if href:
                    all_urls.append({"text": text, "url": href})
            
            browser.close()
            
            if not all_urls:
                return {"error": "Bot nie znalazł żadnego linku na stronie. Możliwa blokada Anti-Bot."}
            
            return {"found_links": all_urls}
            
        except Exception as e:
            browser.close()
            return {"error": f"Błąd debugowania: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
