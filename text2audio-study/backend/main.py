"""
Text2Audio Study - Backend API
API FastAPI para convertir documentos a audio.
"""
import os
import shutil
import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from services.file_parser import FileParser, FileParserError
from services.tts_service import TTSService, TTSEngine, TTSError


# Configuración de directorios (relativos a este archivo)
BASE_DIR = Path(__file__).parent.parent  # carpeta raíz del proyecto
BACKEND_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Limpieza al iniciar/detener la aplicación."""
    # Startup
    yield
    # Shutdown - limpiar archivos temporales
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)


app = FastAPI(
    title="Text2Audio Study",
    description="Convierte documentos a audio para estudiar",
    version="2.0.0",
    lifespan=lifespan
)

# CORS para permitir acceso desde cualquier origen (necesario para Render/Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ MODELOS Pydantic ============

class TextToSpeechRequest(BaseModel):
    text: str
    engine: str = "edge"
    voice: Optional[str] = None
    language: str = "es"
    speed: float = 1.0


class TextToSpeechResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    filename: Optional[str] = None


# ============ RUTAS API ============

@app.get("/api/health")
async def health_check():
    """Endpoint de salud."""
    return {
        "status": "ok",
        "service": "Text2Audio Study",
        "version": "2.0.0",
        "features": {
            "file_upload": True,
            "tts_edge": True,       # Microsoft Edge TTS - gratuito, alta calidad
            "tts_gtts": True,       # Google TTS - gratuito, calidad media
            "tts_pyttsx3": True     # Windows SAPI5 - offline, calidad básica
        }
    }


@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extrae texto de un archivo (PDF, DOC, DOCX, TXT).
    No genera audio, solo extrae y devuelve el texto.
    """
    try:
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        
        text = FileParser.extract_text(file.filename, content)
        
        return {
            "success": True,
            "filename": file.filename,
            "text": text,
            "char_count": len(text),
            "estimated_duration": f"~{len(text) // 15} segundos"
        }
        
    except FileParserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/api/convert-file")
async def convert_file(
    file: UploadFile = File(...),
    engine: str = Form("edge"),
    voice: Optional[str] = Form(None),
    language: str = Form("es"),
    speed: float = Form(1.0)
):
    """
    Convierte un archivo a audio.
    Pipeline completo: archivo → texto → audio
    """
    job_id = str(uuid.uuid4())[:8]
    
    try:
        # 1. Leer y extraer texto del archivo
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        
        text = FileParser.extract_text(file.filename, content)
        
        # 2. Seleccionar motor TTS
        try:
            tts_engine = TTSEngine(engine)
        except ValueError:
            tts_engine = TTSEngine.EDGE
        
        # 3. Generar audio
        audio_bytes = TTSService.text_to_speech(
            text=text,
            engine=tts_engine,
            voice=voice,
            language=language,
            speed=speed
        )
        
        # 4. Guardar archivo de audio
        base_name = Path(file.filename).stem
        output_filename = f"{base_name}_{job_id}.mp3"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        # 5. Devolver archivo
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="audio/mpeg"
        )
        
    except FileParserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/api/text-to-speech")
async def text_to_speech_api(request: TextToSpeechRequest):
    """
    Convierte texto directo a audio.
    Útil para textos pegados manualmente o editados.
    """
    job_id = str(uuid.uuid4())[:8]
    
    try:
        # Seleccionar motor TTS
        try:
            tts_engine = TTSEngine(request.engine)
        except ValueError:
            tts_engine = TTSEngine.EDGE
        
        # Generar audio
        audio_bytes = TTSService.text_to_speech(
            text=request.text,
            engine=tts_engine,
            voice=request.voice,
            language=request.language,
            speed=request.speed
        )
        
        # Guardar archivo
        output_filename = f"audio_{job_id}.mp3"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="audio/mpeg"
        )
        
    except TTSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/api/voices")
async def list_voices():
    """
    Lista las voces disponibles para cada motor TTS.
    """
    return {
        "edge": {
            "description": "Microsoft Edge TTS - Gratuito, voces neuronales de alta calidad",
            "note": "Requiere conexión a internet. 40+ voces en español.",
            "voices": {k: v[1] for k, v in TTSService.EDGE_VOICES.items()}
        },
        "gtts": {
            "description": "Google TTS - Gratuito, calidad estándar",
            "languages": TTSService.GTTS_LANGUAGES
        },
        "pyttsx3": {
            "description": "pyttsx3 - Offline, usa voces del sistema (SAPI5)",
            "note": "Funciona sin internet. Instala voces españolas en Windows si es necesario.",
            "voices": TTSService.PYTTSX3_VOICES
        }
    }


@app.delete("/api/cleanup")
async def cleanup_old_files():
    """
    Limpia archivos temporales antiguos (>1 hora).
    """
    import time
    
    cleaned = 0
    current_time = time.time()
    max_age = 3600  # 1 hora
    
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        if directory.exists():
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        file_path.unlink()
                        cleaned += 1
    
    return {"cleaned_files": cleaned}


# ============ SERVIR FRONTEND ============

from fastapi import Request

# Si existe la carpeta frontend, servir archivos estáticos
# y manejar la ruta raíz con el index.html
if FRONTEND_DIR.exists():
    from fastapi.responses import HTMLResponse
    
    # Servir archivos estáticos desde /static/ y el frontend desde /
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend():
        """Sirve el index.html del frontend."""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return {"message": "Text2Audio Study API", "docs": "/docs", "version": "2.0.0"}
    
    @app.get("/app.js", response_class=FileResponse)
    async def serve_app_js():
        """Sirve el archivo app.js."""
        return FRONTEND_DIR / "app.js"
        
else:
    # Fallback si no existe frontend
    @app.get("/")
    async def root():
        return {
            "message": "Text2Audio Study API",
            "docs": "/docs",
            "version": "2.0.0"
        }


# ============ MAIN ============

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
