# 🚀 Text/PDF to Markdown Converter

Applicazione completa per convertire testi e file PDF in Markdown strutturato utilizzando AI (Claude, OpenAI, Gemini).

## ✨ Caratteristiche

### 🎯 **Funzionalità principali**
- ✅ **Interfaccia Web moderna** con drag & drop
- ✅ **Supporto PDF completo** con estrazione automatica del testo  
- ✅ **3 provider AI**: Claude, OpenAI GPT-4, Google Gemini
- ✅ **Due modalità di conversione**:
  - `improve`: Migliora e struttura il contenuto
  - `structure`: Solo formattazione Markdown
- ✅ **API REST** per integrazioni
- ✅ **CLI** per automazioni
- ✅ **Docker containerizzato** per deployment facile

### 🖥️ **Interfaccia Web**
- **Drag & drop** per file PDF
- **Editor di testo** integrato
- **Preview in tempo reale** del Markdown
- **Download diretto** dei file convertiti
- **Copia negli appunti** con un click
- **Stato API in tempo reale**
- **Design responsive** per mobile

### 🔧 **Modalità di utilizzo**
1. **Web Browser** - Interfaccia grafica completa
2. **API REST** - Per integrazioni e automazioni
3. **CLI** - Script da linea di comando

## 🚀 Quick Start

### Installazione automatica (Linux/Mac):
```bash
# Scarica e avvia tutto automaticamente
curl -sSL https://raw.githubusercontent.com/vcnngr/markdown-forge/main/install.sh | bash

```

### Installazione manuale:

1. **Clone e setup:**
   ```bash
   git clone https://github.com/vcnngr/markdown-forge
   cd markdown-forge
   chmod +x install.sh
   ./install.sh
   ```

2. **Configura le API keys:**
   ```bash
   cp .env.example .env
   nano .env  # Aggiungi le tue API keys
   ```

3. **Avvia il servizio:**
   ```bash
   docker-compose up -d
   ```

4. **Accedi all'interfaccia web:**
   ```
   http://localhost:8000
   ```

## 🌐 Utilizzo Web Interface

### **Upload PDF:**
1. Vai su http://localhost:8000
2. Clicca sul tab "📁 PDF Upload"
3. Trascina il PDF o clicca "Seleziona File"
4. Scegli provider AI e modalità
5. Clicca "🚀 Converti in Markdown"
6. Scarica o copia il risultato

### **Conversione Testo:**
1. Tab "📄 Testo"
2. Incolla o scrivi il tuo testo
3. Configura le opzioni
4. Converti e scarica

## 🔌 API REST

### **Converti testo:**
```bash
curl -X POST "http://localhost:8000/convert/text" \
  -F "text=Il tuo testo qui" \
  -F "provider=claude" \
  -F "task=improve" \
  -F "filename=output.md"
```

### **Converti PDF:**
```bash
curl -X POST "http://localhost:8000/convert/pdf" \
  -F "file=@documento.pdf" \
  -F "provider=openai" \
  -F "task=structure" \
  -F "filename=documento.md"
```

### **Verifica stato API:**
```bash
curl http://localhost:8000/health
```

## 💻 Utilizzo CLI

```bash
# Testo
python cli.py input.txt -o output.md -p claude -t improve

# PDF
python cli.py documento.pdf -o documento.md -p gemini -t structure

# Opzioni disponibili
python cli.py --help
```

## ⚙️ Configurazione

### **File .env:**
```bash
# Configura almeno una delle seguenti API
ANTHROPIC_API_KEY=sk-ant-xxxxx        # Claude
OPENAI_API_KEY=sk-xxxxx               # GPT-4
GEMINI_API_KEY=xxxxx                  # Gemini
```

### **Parametri disponibili:**

#### **Provider AI:**
- `claude` - Claude 3 Sonnet (Anthropic) - Consigliato
- `openai` - GPT-4 (OpenAI) - Alternativa potente
- `gemini` - Gemini Pro (Google) - Opzione gratuita

#### **Modalità conversione:**
- `improve` - Migliora il testo, corregge errori, ottimizza struttura
- `structure` - Solo formattazione Markdown, mantiene testo originale

## 📊 Gestione e Monitoraggio

### **Comandi Docker:**
```bash
# Stato del servizio
docker-compose ps

# Log in tempo reale
docker-compose logs -f

# Restart
docker-compose restart

# Stop completo
docker-compose down

# Aggiornamento
git pull && docker-compose up --build -d
```

### **Directory struttura:**
```
markdown-forge/
├── static/           # File interfaccia web
├── output/           # File convertiti
├── input/            # File di input (opzionale)
├── web_app.py        # App principale con web UI
├── cli.py            # Script linea di comando
├── docker-compose.yml
└── .env              # Configurazione API keys
```

## 🔍 Troubleshooting

### **Problemi comuni:**

**❌ "API key non configurata"**
- Verifica il file `.env`
- Riavvia il container: `docker-compose restart`

**❌ "Errore nell'estrazione del PDF"**
- Verifica che il PDF non sia protetto da password
- Prova con un PDF diverso per testare

**❌ "Errore di connessione"**
- Controlla la connessione internet
- Verifica che le API keys siano valide

**❌ Interfaccia web non accessibile**
```bash
# Verifica che il container sia avviato
docker-compose ps

# Controlla i log
docker-compose logs web-app
```

### **Reset completo:**
```bash
docker-compose down
docker-compose up --build -d
```

## 🆕 Features Avanzate

- **Batch processing** via API
- **Webhook support** per integrazioni
- **Rate limiting** automatico
- **Caching** dei risultati
- **Supporto multi-lingua**
- **Template personalizzati** per Markdown

## 📈 Performance

- **Velocità**: ~5-15 secondi per documento medio
- **Dimensioni PDF**: Supporta fino a 50MB
- **Concorrenza**: Fino a 10 richieste simultanee
- **Memoria**: ~512MB RAM per container

---

**🎉 Buona conversione con Text/PDF to Markdown Converter!**

Per supporto: [GitHub Issues](https://github.com/vcnngr/markdown-forge/issues)