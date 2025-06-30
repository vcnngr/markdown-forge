#!/bin/bash

echo "🚀 Installazione Text/PDF to Markdown Converter"
echo "================================================"

# Crea la struttura delle directory
echo "📁 Creazione struttura directory..."
mkdir -p static output input

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato. Installa Docker prima di continuare."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non trovato. Installa Docker Compose prima di continuare."
    exit 1
fi

# Crea il file .env se non esiste
if [ ! -f .env ]; then
    echo "⚙️ Creazione file di configurazione..."
    cp .env.example .env
    echo "📝 Modifica il file .env con le tue API keys:"
    echo "   - ANTHROPIC_API_KEY per Claude"
    echo "   - OPENAI_API_KEY per GPT-4"
    echo "   - GEMINI_API_KEY per Gemini"
    echo ""
fi

# Build e avvio
echo "🔨 Building Docker container..."
docker-compose build

echo "🚀 Avvio del servizio..."
docker-compose up -d

echo ""
echo "✅ Installazione completata!"
echo ""
echo "🌐 Accedi all'interfaccia web: http://localhost:8000"
echo "📚 Documentazione API: http://localhost:8000/docs"
echo "🔍 Stato servizio: docker-compose ps"
echo "📋 Log: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
echo ""
echo "⚠️  Ricorda di configurare almeno una API key nel file .env"

