import os
import asyncio
from pathlib import Path
from typing import Optional, Literal
import PyPDF2
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import anthropic
import openai
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Markdown Forge - Text/PDF to Markdown Converter", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class AIConverter:
    def __init__(self):
        # Inizializza i client delle API
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_client = None
        
        # Leggi i modelli dal file .env con fallback ai default
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # Leggi le configurazioni avanzate
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "120"))
        
        # Inizializza i client solo se le API key sono presenti
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    timeout=self.request_timeout
                )
                print(f"✅ Claude configurato con modello: {self.claude_model}")
            except Exception as e:
                print(f"❌ Errore configurazione Claude: {e}")
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    timeout=self.request_timeout
                )
                print(f"✅ OpenAI configurato con modello: {self.openai_model}")
            except Exception as e:
                print(f"❌ Errore configurazione OpenAI: {e}")
        
        if os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_client = genai.GenerativeModel(self.gemini_model)
                print(f"✅ Gemini configurato con modello: {self.gemini_model}")
            except Exception as e:
                print(f"❌ Errore configurazione Gemini: {e}")
                self.gemini_client = None

    async def convert_with_claude(self, text: str, task: str = "improve") -> str:
        """Converte testo usando Claude"""
        if not self.anthropic_client:
            raise HTTPException(400, "Claude API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        try:
            message = self.anthropic_client.messages.create(
                model=self.claude_model,  # Usa il modello dal .env
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise HTTPException(500, f"Errore Claude ({self.claude_model}): {str(e)}")

    async def convert_with_openai(self, text: str, task: str = "improve") -> str:
        """Converte testo usando OpenAI"""
        if not self.openai_client:
            raise HTTPException(400, "OpenAI API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,  # Usa il modello dal .env
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                timeout=self.request_timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(500, f"Errore OpenAI ({self.openai_model}): {str(e)}")

    async def convert_with_gemini(self, text: str, task: str = "improve") -> str:
        """Converte testo usando Gemini"""
        if not self.gemini_client:
            raise HTTPException(400, "Gemini API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        try:
            # Configurazione di generazione per Gemini
            generation_config = {
                'temperature': 0.1,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': self.max_tokens,
            }
            
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise HTTPException(500, "Gemini non ha restituito contenuto")
                
            return response.text
        except Exception as e:
            raise HTTPException(500, f"Errore Gemini ({self.gemini_model}): {str(e)}")

    def _get_prompt(self, text: str, task: str) -> str:
        """Genera il prompt basato sul task richiesto"""
        base_prompt = f"""
Dato il seguente testo, convertilo in un file Markdown ben formattato.

ISTRUZIONI:
- Crea una struttura gerarchica con titoli e sottotitoli appropriati
- Usa la formattazione Markdown corretta (grassetto, corsivo, liste, ecc.)
- Organizza il contenuto in sezioni logiche
- Mantieni tutte le informazioni importanti
"""

        if task == "improve":
            base_prompt += """
- Migliora la chiarezza e leggibilità del testo
- Correggi eventuali errori grammaticali
- Ottimizza la struttura per una migliore comprensione
"""
        elif task == "structure":
            base_prompt += """
- Concentrati principalmente sulla strutturazione del contenuto
- Mantieni il testo originale il più possibile invariato
- Aggiungi solo la formattazione Markdown necessaria
"""

        base_prompt += f"""

TESTO DA CONVERTIRE:
{text}

OUTPUT: Fornisci solo il contenuto Markdown, senza spiegazioni aggiuntive.
"""
        return base_prompt

    def get_available_providers(self) -> dict:
        """Restituisce i provider disponibili con i loro modelli"""
        return {
            "claude": {
                "available": bool(self.anthropic_client),
                "model": self.claude_model
            },
            "openai": {
                "available": bool(self.openai_client),
                "model": self.openai_model
            },
            "gemini": {
                "available": bool(self.gemini_client),
                "model": self.gemini_model
            }
        }

def extract_text_from_pdf(file_content: bytes) -> str:
    """Estrae testo da un file PDF"""
    try:
        from io import BytesIO
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        max_pages = int(os.getenv("PDF_MAX_PAGES", "500"))
        
        for i, page in enumerate(pdf_reader.pages):
            if i >= max_pages:
                break
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise HTTPException(400, f"Errore nell'estrazione del PDF: {str(e)}")

# Inizializza il converter
converter = AIConverter()

@app.get("/", response_class=HTMLResponse)
async def serve_web_interface():
    """Serve l'interfaccia web principale"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Interfaccia web non trovata</h1><p>Assicurati che il file static/index.html esista</p>",
            status_code=404
        )

@app.get("/health")
async def health_check():
    """Verifica lo stato delle API configurate"""
    providers = converter.get_available_providers()
    
    status = {
        "claude": providers["claude"]["available"],
        "openai": providers["openai"]["available"],
        "gemini": providers["gemini"]["available"]
    }
    
    return {
        "status": "healthy",
        "apis_configured": status,
        "models": {
            "claude": providers["claude"]["model"],
            "openai": providers["openai"]["model"],
            "gemini": providers["gemini"]["model"]
        },
        "settings": {
            "max_tokens": converter.max_tokens,
            "request_timeout": converter.request_timeout,
            "pdf_max_pages": os.getenv("PDF_MAX_PAGES", "500")
        }
    }

@app.post("/convert/text")
async def convert_text(
    text: str = Form(...),
    provider: Literal["claude", "openai", "gemini"] = Form("claude"),
    task: Literal["improve", "structure"] = Form("improve"),
    filename: str = Form("output.md")
):
    """Converte testo in Markdown - restituisce il contenuto direttamente per la web UI"""
    
    # Validazione lunghezza testo
    max_length = int(os.getenv("MAX_TEXT_LENGTH", "100000"))
    if len(text) > max_length:
        raise HTTPException(400, f"Testo troppo lungo. Massimo {max_length} caratteri.")
    
    try:
        if provider == "claude":
            result = await converter.convert_with_claude(text, task)
        elif provider == "openai":
            result = await converter.convert_with_openai(text, task)
        elif provider == "gemini":
            result = await converter.convert_with_gemini(text, task)
        else:
            raise HTTPException(400, "Provider non valido")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Errore nella conversione: {str(e)}")

@app.post("/convert/pdf")
async def convert_pdf(
    file: UploadFile = File(...),
    provider: Literal["claude", "openai", "gemini"] = Form("claude"),
    task: Literal["improve", "structure"] = Form("improve"),
    filename: str = Form("output.md")
):
    """Converte PDF in Markdown - restituisce il contenuto direttamente per la web UI"""
    
    # Validazione file
    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    if file.size and file.size > max_size_mb * 1024 * 1024:
        raise HTTPException(400, f"File troppo grande. Massimo {max_size_mb}MB.")
    
    try:
        # Verifica che sia un PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Il file deve essere un PDF")
        
        # Leggi il contenuto del file
        content = await file.read()
        
        # Estrai il testo dal PDF
        text = extract_text_from_pdf(content)
        
        if not text.strip():
            raise HTTPException(400, "Impossibile estrarre testo dal PDF o PDF vuoto")
        
        # Converti con l'AI scelta
        if provider == "claude":
            result = await converter.convert_with_claude(text, task)
        elif provider == "openai":
            result = await converter.convert_with_openai(text, task)
        elif provider == "gemini":
            result = await converter.convert_with_gemini(text, task)
        else:
            raise HTTPException(400, "Provider non valido")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Errore nella conversione PDF: {str(e)}")

@app.get("/models")
async def get_models():
    """Restituisce i modelli configurati per ogni provider"""
    return converter.get_available_providers()

if __name__ == "__main__":
    import uvicorn
    
    # Leggi configurazioni dal .env
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Avvio Markdown Forge su {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        reload=debug,
        log_level="info" if not debug else "debug"
    )
