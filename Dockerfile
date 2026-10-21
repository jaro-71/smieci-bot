FROM python:3.9-slim

# Instalacja zależności systemowych dla przeglądarki
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalacja bibliotek Pythona
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalacja przeglądarki Chromium i jej sterowników
RUN playwright install chromium
RUN playwright install-deps chromium

# Kopiowanie kodu aplikacji
COPY . .

# Uruchomienie serwera na porcie 10000 (wymagane przez Render)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
