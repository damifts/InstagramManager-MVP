# Instagram Manager MVP

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
uv run python -m uvicorn main:app --app-dir backend --reload --reload-dir backend --host 127.0.0.1 --port 8000
```

Frontend (secondo terminale):

```cmd
uv run python -m streamlit run frontend\app.py
```

URL utili:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Configurazione .env

Parti da `.env.example` e imposta almeno:

```cmd
copy .env.example .env
```

```env
INSTAGRAM_ACCESS_TOKEN=IGAANBqYCsRBtBZAGJ6UDhsZATQ2N3l6QmYzdHJoOUtLSkkxN2ZApZAVA3TW02TTV2ekViY0FBX05IdlhpdEVxdkUyRXRZAcE1HS1FTcFAzQklHQkVZATHNBandTS1F2TFZAvV0x1bEZAFYTNrSWdlOHRQclBwdm9uanV4ZA0VEcTBxNlp4ZAwZDZD
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
```

Nota didattica: questo repository e usato per scopi formativi.
Nota sicurezza: il token sopra e presente solo come esempio didattico, non usarlo in produzione e sostituiscilo sempre con un token tuo valido.

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
- Se appare warning su `VIRTUAL_ENV` non allineato al progetto, il terminale sta puntando a una `.venv` di un altro workspace.
- Apri un terminale nuovo nella root del progetto e lancia `uv sync`.
- Per forzare l'ambiente attivo corrente usa `uv run --active ...` (solo se sei sicuro di avere attivato la `.venv` giusta).
- Per evitare watch troppo ampio con hot-reload, usa sempre `--reload-dir backend`.
- Se `GET /api/profile` restituisce `503 Service Unavailable`, nella pratica mancano variabili `.env` (soprattutto `INSTAGRAM_ACCESS_TOKEN`) oppure il token non e valido/scaduto.
- Comando cache uv:

```cmd
uv cache clean
```
