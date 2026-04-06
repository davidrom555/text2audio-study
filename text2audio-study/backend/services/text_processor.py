"""
Utilidades para procesamiento de texto.
"""
import re


class TextProcessor:
    """Procesador de texto para optimizar TTS."""
    
    @staticmethod
    def split_into_chunks(text: str, max_chars: int = 4000) -> list:
        """
        Divide el texto en chunks para procesamiento por lotes.
        Respeta párrafos y oraciones.
        """
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Separar por párrafos
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # Si el párrafo cabe completo
            if len(current_chunk) + len(paragraph) + 2 <= max_chars:
                current_chunk += paragraph + "\n\n"
            else:
                # Guardar chunk actual si tiene contenido
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Si el párrafo es muy largo, dividir por oraciones
                if len(paragraph) > max_chars:
                    sentences = re.split(r'(?<=[.!?]) +', paragraph)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_chars:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk.strip():
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + " "
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Agregar último chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def clean_for_tts(text: str) -> str:
        """Limpia el texto para mejorar la calidad del TTS."""
        # Eliminar URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Eliminar caracteres especiales que no se pronuncian
        text = re.sub(r'[#*•·◦○●■□▲△▼▽►◄▻◅▸◂▹◃▴▾▵▿]', '', text)
        
        # Normalizar espacios múltiples
        text = re.sub(r' +', ' ', text)
        
        # Eliminar líneas con solo números de página
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Eliminar referencias tipo [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        return text.strip()
    
    @staticmethod
    def estimate_duration(char_count: int, wpm: int = 150) -> str:
        """Estima la duración del audio en formato legible."""
        # Asumimos ~5 caracteres por palabra en promedio
        words = char_count // 5
        seconds = (words / wpm) * 60
        
        if seconds < 60:
            return f"~{int(seconds)} segundos"
        else:
            minutes = int(seconds / 60)
            remaining_secs = int(seconds % 60)
            if remaining_secs > 0:
                return f"~{minutes}:{remaining_secs:02d} minutos"
            return f"~{minutes} minutos"