from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

app = FastAPI()

@app.get("/")
def get_waste_schedule():
    url = "https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=6823&ulica=391"
    
    try:
        # Używamy lekkiego zapytania HTTP
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parsujemy HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. SZUKAMY ELEMENTU PO ID "printPDF"
        pdf_element = soup.find(id="printPDF")
        
        pdf_url = None
        if pdf_element and pdf_element.has_attr('href'):
            pdf_url = pdf_element['href']
        else:
            # Jeśli nie ma id="printPDF", szukamy zapasowo po tekście w linkach
            for a in soup.find_all('a', href=True):
                if "POBIERZ HARMONOGRAM" in a.text.upper() or ("download" in a['href'] and "pdf" in a['href']):
                    pdf_url = a['href']
                    break
        
        if not pdf_url:
            return {"error": "Nie znaleziono elementu id='printPDF' ani linku do PDF w kodzie HTML. Strona prawdopodobnie generuje ten przycisk dynamicznie przez JavaScript."}
        
        # Uzupełniamy adres URL, jeśli jest względny
        if pdf_url.startswith("/"):
            pdf_url = "https://ekosystem.wroc.pl" + pdf_url
        
        # 2. WYCIĄGAMY DANE Z URL
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
        
        if not schedule:
            return {"error": "Link znaleziony, ale nie zawiera danych w parametrach URL"}
            
        return schedule
        
    except Exception as e:
        return {"error": f"Błąd bota: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
