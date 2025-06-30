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

app = FastAPI(title="Text/PDF to Markdown Converter", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class AIConverter:
    def __init__(self):
        # Inizializza i client delle API
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_client = None
        
        if os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        if os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_client = genai.GenerativeModel('gemini-pro')

    async def convert_with_claude(self, text: str, task: str = "improve") -> str:
        """Converte testo usando Claude"""
        if not self.anthropic_client:
            raise HTTPException(400, "Claude API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        message = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text

    async def convert_with_openai(self, text: str, task: str = "improve") -> str:
        """Converte testo usando OpenAI"""
        if not self.openai_client:
            raise HTTPException(400, "OpenAI API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )
        
        return response.choices[0].message.content

    async def convert_with_gemini(self, text: str, task: str = "improve") -> str:
        """Converte testo usando Gemini"""
        if not self.gemini_client:
            raise HTTPException(400, "Gemini API key non configurata")
        
        prompt = self._get_prompt(text, task)
        
        response = self.gemini_client.generate_content(prompt)
        return response.text

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

def extract_text_from_pdf(file_content: bytes) -> str:
    """Estrae testo da un file PDF"""
    try:
        from io import BytesIO
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise HTTPException(400, f"Errore nell'estrazione del PDF: {str(e)}")

# Inizializza il converter
converter = AIConverter()

@app.get("/", response_class=HTMLResponse)
async def serve_web_interface():
    """Serve l'interfaccia web principale"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Verifica lo stato delle API configurate"""
    status = {
        "claude": bool(converter.anthropic_client),
        "openai": bool(converter.openai_client),
        "gemini": bool(converter.gemini_client)
    }
    return {"status": "healthy", "apis_configured": status}

@app.post("/convert/text")
async def convert_text(
    text: str = Form(...),
    provider: Literal["claude", "openai", "gemini"] = Form("claude"),
    task: Literal["improve", "structure"] = Form("improve"),
    filename: str = Form("output.md")
):
    """Converte testo in Markdown - restituisce il contenuto direttamente per la web UI"""
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
    try:
        # Verifica che sia un PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Il file deve essere un PDF")
        
        # Leggi il contenuto del file
        content = await file.read()
        
        # Estrai il testo dal PDF
        text = extract_text_from_pdf(content)
        
        if not text.strip():
            raise HTTPException(400, "Impossibile estrarre testo dal PDF")
        
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
    
    except Exception as e:
        raise HTTPException(500, f"Errore nella conversione PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




