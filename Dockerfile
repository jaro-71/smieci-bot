FROM python:3.9-slim

# Instalujemy tylko niezbędne podstawowe narzędzia
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Kopiujemy listę bibliotek
COPY requirements.txt .

# Instalujemy lekkie biblioteki (fastapi, requests, beautifulsoup4)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji
COPY . .

# Uruchamiamy serwer na porcie 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
