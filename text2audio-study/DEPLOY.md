# 🚀 Guía de Deploy en Render.com

## Configuración del Web Service

### Build Command
```bash
pip install -r backend/requirements.txt
```

### Start Command
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Configuración Completa

| Campo | Valor |
|-------|-------|
| **Name** | `text2audio-study` |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |

---

## URL de la App

Una vez desplegado, tu app estará disponible en:

```
https://text2audio-study.onrender.com
```

(El nombre puede variar según elijas en la configuración)

---

## Notas

- El plan **Free** duerme la app después de 15 minutos de inactividad
- Al hacer una nueva request, tarda ~30 segundos en despertar
- El frontend se sirve automáticamente desde el backend FastAPI

---

## Comandos útiles de Git

```bash
# Ver estado
git status

# Agregar cambios
git add .

# Commitear
git commit -m "mensaje"

# Push a main
git push origin main
```
