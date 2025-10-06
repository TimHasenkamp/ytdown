# Verwende ein offizielles Python-Runtime als Basis
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis in den Container
WORKDIR /app

# Installiere System-Abhängigkeiten, einschließlich ffmpeg für die Videoverarbeitung
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Kopiere die Anforderungen in das Container-Image
COPY requirements.txt requirements.txt

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes in den Container
COPY . .

# Setze Umgebungsvariablen für Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Exponiere den Port, auf dem die App läuft
EXPOSE 8000

# Starte die Flask-App mit Gunicorn (erhöhter Timeout für große Downloads)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "900", "--workers", "2", "app:app"]
