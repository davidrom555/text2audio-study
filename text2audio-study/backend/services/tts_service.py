"""
Servicio de Text-to-Speech (TTS).
Soporta: Edge TTS (gratuito, alta calidad), gTTS (gratuito) y pyttsx3 (offline)
"""
import io
import os
import tempfile
import asyncio
from typing import Optional, Literal
from enum import Enum
import requests
from gtts import gTTS


class TTSError(Exception):
    """Excepción personalizada para errores de TTS."""
    pass


class TTSEngine(Enum):
    """Motores de TTS disponibles."""
    EDGE = "edge"           # Microsoft Edge TTS - gratuito, alta calidad
    GTTS = "gtts"           # Google TTS - gratuito, calidad media
    PYTTSX3 = "pyttsx3"     # Windows SAPI5 - offline, calidad básica


class TTSService:
    """Servicio de conversión texto a audio."""
    
    # Voces disponibles para Edge TTS (Microsoft)
    # Voces en español recomendadas
    EDGE_VOICES = {
        # Español (España) - Alta calidad
        "es-es-elvira": ("es-ES-ElviraNeural", "Español - Elvira (Femenina)"),
        "es-es-alvaro": ("es-ES-AlvaroNeural", "Español - Álvaro (Masculina)"),
        "es-es-arnau": ("es-ES-ArnauNeural", "Español - Arnau (Masculina)"),
        "es-es-dario": ("es-ES-DarioNeural", "Español - Darío (Masculina)"),
        "es-es-eli": ("es-ES-EliNeural", "Español - Eli (Femenina)"),
        "es-es-estrella": ("es-ES-EstrellaNeural", "Español - Estrella (Femenina)"),
        "es-es-irene": ("es-ES-IreneNeural", "Español - Irene (Femenina)"),
        "es-es-lia": ("es-ES-LiaNeural", "Español - Lia (Femenina)"),
        "es-es-nil": ("es-ES-NilNeural", "Español - Nil (Masculina)"),
        "es-es-saul": ("es-ES-SaulNeural", "Español - Saúl (Masculina)"),
        "es-es-teo": ("es-ES-TeoNeural", "Español - Teo (Masculina)"),
        "es-es-triana": ("es-ES-TrianaNeural", "Español - Triana (Femenina)"),
        "es-es-vera": ("es-ES-VeraNeural", "Español - Vera (Femenina)"),
        
        # Español (México) - Alta calidad
        "es-mx-dalia": ("es-MX-DaliaNeural", "Español (MX) - Dalia (Femenina)"),
        "es-mx-jorge": ("es-MX-JorgeNeural", "Español (MX) - Jorge (Masculina)"),
        "es-mx-beatriz": ("es-MX-BeatrizNeural", "Español (MX) - Beatriz (Femenina)"),
        "es-mx-candela": ("es-MX-CandelaNeural", "Español (MX) - Candela (Femenina)"),
        "es-mx-carlota": ("es-MX-CarlotaNeural", "Español (MX) - Carlota (Femenina)"),
        "es-mx-cecilio": ("es-MX-CecilioNeural", "Español (MX) - Cecilio (Masculina)"),
        "es-mx-gerardo": ("es-MX-GerardoNeural", "Español (MX) - Gerardo (Masculina)"),
        "es-mx-larissa": ("es-MX-LarissaNeural", "Español (MX) - Larissa (Femenina)"),
        "es-mx-liberto": ("es-MX-LibertoNeural", "Español (MX) - Liberto (Masculina)"),
        "es-mx-luciano": ("es-MX-LucianoNeural", "Español (MX) - Luciano (Masculina)"),
        "es-mx-marina": ("es-MX-MarinaNeural", "Español (MX) - Marina (Femenina)"),
        "es-mx-nuria": ("es-MX-NuriaNeural", "Español (MX) - Nuria (Femenina)"),
        "es-mx-pelayo": ("es-MX-PelayoNeural", "Español (MX) - Pelayo (Masculina)"),
        "es-mx-renata": ("es-MX-RenataNeural", "Español (MX) - Renata (Femenina)"),
        "es-mx-yago": ("es-MX-YagoNeural", "Español (MX) - Yago (Masculina)"),
        
        # Español (Argentina)
        "es-ar-elena": ("es-AR-ElenaNeural", "Español (AR) - Elena (Femenina)"),
        "es-ar-tomas": ("es-AR-TomasNeural", "Español (AR) - Tomás (Masculina)"),
        
        # Español (Colombia)
        "es-co-salome": ("es-CO-SalomeNeural", "Español (CO) - Salomé (Femenina)"),
        "es-co-gonzalo": ("es-CO-GonzaloNeural", "Español (CO) - Gonzalo (Masculina)"),
        
        # Español (Chile)
        "es-cl-catalina": ("es-CL-CatalinaNeural", "Español (CL) - Catalina (Femenina)"),
        "es-cl-lorenzo": ("es-CL-LorenzoNeural", "Español (CL) - Lorenzo (Masculina)"),
        
        # Inglés
        "en-us-jenny": ("en-US-JennyNeural", "English (US) - Jenny"),
        "en-us-guy": ("en-US-GuyNeural", "English (US) - Guy"),
        "en-us-aria": ("en-US-AriaNeural", "English (US) - Aria"),
        "en-gb-sonia": ("en-GB-SoniaNeural", "English (UK) - Sonia"),
        "en-gb-ryan": ("en-GB-RyanNeural", "English (UK) - Ryan"),
    }
    
    # Idiomas para gTTS
    GTTS_LANGUAGES = {
        "es": "Español",
        "en": "English",
        "pt": "Português",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
    }
    
    # Voces disponibles para pyttsx3 (SAPI5 en Windows)
    PYTTSX3_VOICES = {
        "default": "Voz por defecto del sistema",
        "spanish": "Español (si está instalado)",
        "english": "English (if installed)",
    }
    
    @classmethod
    def text_to_speech(
        cls,
        text: str,
        engine: TTSEngine = TTSEngine.EDGE,
        voice: Optional[str] = None,
        language: str = "es",
        speed: float = 1.0
    ) -> bytes:
        """
        Convierte texto a audio.
        
        Args:
            text: Texto a convertir
            engine: Motor TTS a usar (edge, gtts o pyttsx3)
            voice: ID de voz a usar
            language: Código de idioma (para gTTS)
            speed: Velocidad de reproducción (0.5 - 2.0)
        
        Returns:
            bytes: Audio en formato MP3
        """
        if not text or len(text.strip()) < 10:
            raise TTSError("El texto es demasiado corto (mínimo 10 caracteres)")
        
        if len(text) > 5000:
            text = text[:5000]
        
        try:
            if engine == TTSEngine.EDGE:
                return cls._edge_tts(text, voice, speed)
            elif engine == TTSEngine.PYTTSX3:
                try:
                    return cls._pyttsx3_tts(text, voice, language, speed)
                except TTSError as e:
                    # En Render/Linux, pyttsx3 no funciona. Fallback a Edge TTS
                    if "Error en pyttsx3" in str(e):
                        return cls._edge_tts(text, voice, speed)
                    raise
            else:
                return cls._gtts_tts(text, language, speed)
        except TTSError:
            raise
        except Exception as e:
            raise TTSError(f"Error en conversión TTS: {str(e)}")
    
    @classmethod
    def _edge_tts(cls, text: str, voice: Optional[str], speed: float) -> bytes:
        """Genera audio usando Microsoft Edge TTS (gratuito)."""
        try:
            import edge_tts

            # Seleccionar voz por defecto si no se especifica
            if not voice or voice not in cls.EDGE_VOICES:
                voice = "es-es-elvira"  # Voz por defecto en español

            voice_id = cls.EDGE_VOICES[voice][0]

            # Ajustar velocidad (Edge TTS usa porcentaje: -100% a +100%)
            # speed 1.0 = 0%, 0.5 = -50%, 2.0 = +100%
            rate_percent = int((speed - 1.0) * 100)
            rate_str = f"{rate_percent:+d}%"

            # Crear comunicador
            communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)

            # Usar un buffer en memoria
            mp3_buffer = io.BytesIO()

            # Ejecutar async usando asyncio.new_event_loop() para evitar conflictos
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                async def save_audio():
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            mp3_buffer.write(chunk["data"])

                loop.run_until_complete(save_audio())
            finally:
                loop.close()

            mp3_buffer.seek(0)
            return mp3_buffer.read()

        except ImportError:
            raise TTSError("edge-tts no está instalado. Ejecuta: pip install edge-tts")
        except Exception as e:
            raise TTSError(f"Error en Edge TTS: {str(e)}")
    
    @classmethod
    def _gtts_tts(cls, text: str, language: str, speed: float) -> bytes:
        """Genera audio usando gTTS (Google TTS gratuito)."""
        try:
            # gTTS solo soporta ciertos idiomas
            if language not in cls.GTTS_LANGUAGES:
                language = "es"  # Default a español
            
            # Crear TTS
            tts = gTTS(text=text, lang=language, slow=(speed < 0.8))
            
            # Guardar a buffer
            mp3_buffer = io.BytesIO()
            tts.write_to_fp(mp3_buffer)
            mp3_buffer.seek(0)
            
            return mp3_buffer.read()
            
        except Exception as e:
            raise TTSError(f"Error en gTTS: {str(e)}")
    
    @classmethod
    def _pyttsx3_tts(cls, text: str, voice: Optional[str], language: str, speed: float) -> bytes:
        """Genera audio usando pyttsx3 (SAPI5 en Windows - offline)."""
        try:
            import pyttsx3

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                temp_path = tmp.name

            try:
                # Inicializar motor con driver específico para Windows
                try:
                    engine = pyttsx3.init('sapi5')  # Usar SAPI5 explícitamente en Windows
                except Exception as e:
                    # Si falla SAPI5, intentar con el motor por defecto
                    engine = pyttsx3.init()

                # Ajustar velocidad (palabras por minuto, default ~200)
                base_rate = 200
                engine.setProperty('rate', int(base_rate * speed))

                # Guardar a archivo
                engine.save_to_file(text, temp_path)
                engine.runAndWait()

                # Leer archivo
                with open(temp_path, 'rb') as f:
                    wav_data = f.read()

                # Convertir WAV a MP3
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_wav(io.BytesIO(wav_data))
                    mp3_buffer = io.BytesIO()
                    audio.export(mp3_buffer, format="mp3", bitrate="192k")
                    mp3_buffer.seek(0)
                    return mp3_buffer.read()
                except ImportError:
                    # Si pydub no está disponible, devolver WAV
                    return wav_data

            finally:
                # Limpiar
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

        except ImportError:
            raise TTSError("pyttsx3 no está instalado. Ejecuta: pip install pyttsx3")
        except Exception as e:
            raise TTSError(f"Error en pyttsx3: {str(e)}. En Windows, asegúrate de que tienes voces instaladas en Configuración → Hora e idioma → Voz.")
    
    @classmethod
    def get_available_voices(cls, engine: TTSEngine) -> dict:
        """Obtiene las voces disponibles para un motor."""
        if engine == TTSEngine.EDGE:
            return {k: v[1] for k, v in cls.EDGE_VOICES.items()}
        elif engine == TTSEngine.GTTS:
            return cls.GTTS_LANGUAGES
        elif engine == TTSEngine.PYTTSX3:
            return cls.PYTTSX3_VOICES
        return {}
