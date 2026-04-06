# 🎧 Text2Audio Study

> Convierte tus documentos (PDF, Word, TXT) a audio para estudiar mejor. 
> Ideal para repasar material mientras haces ejercicio, viajas o descansas la vista.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

---

## ✨ Características

- 📄 **Soporta múltiples formatos**: PDF, DOC, DOCX, TXT
- 🎙️ **Dos motores de voz**:
  - **Google TTS**: 100% gratuito, calidad estándar
  - **ElevenLabs**: Calidad humana premium (requiere API key gratuita)
- 🌐 **Web app moderna**: Interfaz responsive, fácil de usar
- 🔒 **Privacidad**: Los archivos se procesan temporalmente y se eliminan automáticamente
- ⚡ **Rápido**: Procesamiento en segundos
- 🌍 **Multilenguaje**: Español, English, Português, Français, Deutsch, Italiano

---

## 🚀 Demo Online

### Opción 1: Deploy en Render.com (Gratuito)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/TU_USUARIO/text2audio-study)

1. Clic en el botón ☝️
2. Crea cuenta gratuita en Render (con GitHub)
3. ¡Listo! Tu app estará online en minutos

### Opción 2: Ejecutar localmente

```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/text2audio-study.git
cd text2audio-study

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r backend/requirements.txt

# 4. Ejecutar
uvicorn backend.main:app --reload

# 5. Abrir en navegador
# http://localhost:8000
```

---

## 📖 Guía de Uso

### 1. Subir Archivo o Pegar Texto

- **Modo Archivo**: Arrastra tu PDF/Word o haz clic para seleccionar
- **Modo Texto**: Pega directamente el texto que quieras convertir

### 2. Configurar Voz

#### Opción A: Google TTS (Gratuito)
1. Selecciona "Google TTS"
2. Elige el idioma
3. Ajusta la velocidad si lo deseas
4. ¡Listo para convertir!

#### Opción B: ElevenLabs (Calidad Premium)
1. Ve a [elevenlabs.io](https://elevenlabs.io/app/sign-up) y crea cuenta gratuita
2. Copia tu API key (empieza con `sk_`)
3. Pégala en la app y haz clic en "Validar"
4. Selecciona una voz (Rachel, Adam, Bella, etc.)
5. ¡Listo para convertir!

> 💡 **Plan gratuito de ElevenLabs**: 10,000 caracteres/mes (aprox. 10-15 minutos de audio)

### 3. Descargar Audio

- Escucha el preview directamente en el navegador
- Descarga el archivo MP3 para usarlo offline

---

## 🏗️ Arquitectura

```
text2audio-study/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── requirements.txt     # Dependencias Python
│   └── services/
│       ├── file_parser.py   # Extrae texto de PDF/DOCX
│       └── tts_service.py   # Integración TTS
├── frontend/
│   ├── index.html           # UI principal
│   └── app.js               # Lógica frontend
├── render.yaml              # Config Render.com
└── README.md                # Este archivo
```

---

## 🔧 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Verificar estado del servidor |
| `/api/extract-text` | POST | Extraer texto de archivo |
| `/api/convert-file` | POST | Archivo → Audio (completo) |
| `/api/text-to-speech` | POST | Texto → Audio |
| `/api/validate-api-key` | POST | Validar API key ElevenLabs |
| `/api/voices` | GET | Listar voces disponibles |

### Ejemplo de uso con cURL

```bash
# Extraer texto de PDF
curl -X POST -F "file=@documento.pdf" \
  https://TU_APP.onrender.com/api/extract-text

# Convertir texto a audio (Google TTS)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mundo", "engine": "gtts", "language": "es"}' \
  --output audio.mp3 \
  https://TU_APP.onrender.com/api/text-to-speech
```

---

## 💰 Costos

| Servicio | Costo | Límite |
|----------|-------|--------|
| **Hosting (Render)** | Gratis | Siempre activo, duerme tras 15 min inactivo |
| **Google TTS** | Gratis | Sin límite |
| **ElevenLabs** | Gratis | 10,000 chars/mes |

---

## 🛠️ Tecnologías

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS
- **TTS**: gTTS (Google), ElevenLabs API
- **Parsing**: PyPDF2, python-docx
- **Deploy**: Render.com (opcional)

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -am 'Add: nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

## 🐛 Troubleshooting

### Error "Backend no disponible"
- Verifica que el servidor esté corriendo: `uvicorn backend.main:app --reload`
- Si usas Render, espera 30 segundos a que el servidor inicie

### Error con archivos .doc antiguos
- Los archivos .doc (Word 97-2003) no son 100% compatibles
- Solución: Abre el archivo en Word y guárdalo como .docx o PDF

### API key de ElevenLabs inválida
- Verifica que la key empiece con `sk_`
- Asegúrate de copiarla completa desde tu dashboard de ElevenLabs
- El plan gratuito tiene límite de 10k caracteres/mes

### El audio suena robótico
- Eso es normal con Google TTS (gratuito)
- Para voz natural usa ElevenLabs (API key gratuita)

---

## 📬 Contacto

¿Preguntas o sugerencias? Abre un [Issue](https://github.com/TU_USUARIO/text2audio-study/issues)

---

<p align="center">
  Hecho con ❤️ para estudiantes
</p>