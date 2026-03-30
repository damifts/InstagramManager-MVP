# Social Manager MVP

Client Streamlit + server FastAPI per workflow Instagram.

## Setup rapido (Windows + uv)

Prerequisiti:
- Python 3.10+
- uv installato

```cmd
pip install uv
uv sync
```

## Avvio

Backend:

```cmd
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

Frontend (secondo terminale):

```cmd
uv run streamlit run frontend\app.py
```

URL utili:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Configurazione .env

Parti da `.env.example` e imposta almeno:

```env
INSTAGRAM_ACCESS_TOKEN=metti_il_token_instagram
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
```

`GEMINI_API_KEY` e opzionale.

## API principali

- GET `/api/profile`
- POST `/api/createPost`
- POST `/api/PostMedia`

Payload creazione media:

```json
{
  "url_risorsa": "https://example.com/image.jpg",
  "caption": "Testo post",
  "user_id": "instagram_user_id"
}
```

Payload pubblicazione:

```json
{
  "user_id": "instagram_user_id",
  "creation_id": "instagram_creation_id"
}
```

## Git e branching

Flusso consigliato:

```cmd
git checkout main
git pull
git checkout -b feat/nome-modifica
```

Commit e push:

```cmd
git add .
git commit -m "feat: descrizione breve"
git push -u origin feat/nome-modifica
```

Naming branch:
- feat/... nuove funzionalita
- fix/... bug fix
- docs/... documentazione
- refactor/... refactoring

Per le regole complete: vedi `CONTRIBUTING.md`.

## Note utili

- Il backend usa store locale in memoria per sviluppo rapido.
- Se usi OneDrive e noti problemi con `.venv`, sposta il progetto fuori da OneDrive.
- Comando cache uv:

```cmd
uv cache clean
```
