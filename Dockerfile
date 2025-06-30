FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia l'applicazione e i file statici
COPY . .

# Crea directory
RUN mkdir -p /app/static /app/output

# Espone la porta
EXPOSE 8000

# Comando di default - usa web_app.py invece di app.py
CMD ["python", "web_app.py"]

