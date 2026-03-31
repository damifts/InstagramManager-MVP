import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

try:
    from app.richieste import (
        crea_media_instagram as crea_media_instagram_api,
        profilo_instagram as profilo_instagram_api,
        pubblica_media_instagram as pubblica_media_instagram_api,
    )
except ModuleNotFoundError:
    from backend.app.richieste import (
        crea_media_instagram as crea_media_instagram_api,
        profilo_instagram as profilo_instagram_api,
        pubblica_media_instagram as pubblica_media_instagram_api,
    )


def origini_cors() -> list[str]:
    valore = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000")
    return [voce.strip() for voce in valore.split(",") if voce.strip()]


load_dotenv()


app = FastAPI(title="Instagram Manager API")


class PayloadCreaMedia(BaseModel):
    url_risorsa: str
    caption: str
    user_id: str


class PayloadPubblicaMedia(BaseModel):
    user_id: str
    creation_id: str


def errore_servizio() -> None:
    raise HTTPException(status_code=503, detail="Servizio non disponibile")


def valida_risultato(result: dict | None) -> dict:
    if not result:
        errore_servizio()
    if isinstance(result, dict) and result.get("_error"):
        raise HTTPException(
            status_code=int(result.get("status_code", 503)),
            detail=str(result.get("detail", "Errore servizio Instagram")),
        )
    return result

app.add_middleware(
    CORSMiddleware,
    allow_origins=origini_cors(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/api/")
@app.get("/api/profile")
@app.get("/profile")
def profilo_instagram():
    result = profilo_instagram_api()
    return valida_risultato(result)


@app.post("/api/createPost")
def crea_media_instagram(payload: PayloadCreaMedia):
    result = crea_media_instagram_api(payload.url_risorsa, payload.caption, payload.user_id)
    return valida_risultato(result)


@app.post("/api/PostMedia")
def pubblica_media_instagram(payload: PayloadPubblicaMedia):
    result = pubblica_media_instagram_api(payload.user_id, payload.creation_id)
    return valida_risultato(result)
