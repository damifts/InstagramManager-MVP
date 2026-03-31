import os

import httpx

BASE_URL = "https://graph.instagram.com/v24.0"
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def token_accesso() -> str:
    return os.getenv("INSTAGRAM_ACCESS_TOKEN", "")


def headers_autorizzazione(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-type": "application/json",
    }


def errore_upstream(detail: str, status_code: int = 503) -> dict:
    return {
        "_error": True,
        "status_code": status_code,
        "detail": detail,
    }


def esegui_richiesta(metodo: str, url: str, **kwargs):
    try:
        response = httpx.request(metodo, url, timeout=DEFAULT_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        dettaglio = "Errore Instagram API"
        try:
            data = exc.response.json()
            dettaglio = data.get("error", {}).get("message") or dettaglio
        except Exception:
            pass
        return errore_upstream(dettaglio, status_code=exc.response.status_code)
    except httpx.RequestError as exc:
        return errore_upstream(f"Errore di rete verso Instagram: {exc}", status_code=503)


def profilo_instagram():
    token = token_accesso()
    if not token:
        return errore_upstream("INSTAGRAM_ACCESS_TOKEN non configurato", status_code=503)
    url = f"{BASE_URL}/me"
    params = {
        "fields": "user_id,username,profile_picture_url,followers_count",
        "access_token": token,
    }
    return esegui_richiesta("GET", url, params=params)


def crea_media_instagram(url_risorsa: str, caption: str, user_id: str):
    token = token_accesso()
    if not token:
        return errore_upstream("INSTAGRAM_ACCESS_TOKEN non configurato", status_code=503)
    if not url_risorsa.strip():
        return errore_upstream("url_risorsa mancante", status_code=400)
    if not user_id.strip():
        return errore_upstream("user_id mancante", status_code=400)
    url = f"{BASE_URL}/{user_id}/media"
    payload = {"image_url": url_risorsa, "caption": caption}
    return esegui_richiesta("POST", url, headers=headers_autorizzazione(token), json=payload)


def pubblica_media_instagram(user_id: str, media_id: str):
    token = token_accesso()
    if not token:
        return errore_upstream("INSTAGRAM_ACCESS_TOKEN non configurato", status_code=503)
    if not user_id.strip():
        return errore_upstream("user_id mancante", status_code=400)
    if not media_id.strip():
        return errore_upstream("creation_id mancante", status_code=400)
    url = f"{BASE_URL}/{user_id}/media_publish"
    payload = {"creation_id": media_id}
    return esegui_richiesta("POST", url, headers=headers_autorizzazione(token), params=payload)
