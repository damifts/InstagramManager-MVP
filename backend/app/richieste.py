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


def esegui_richiesta(metodo: str, url: str, **kwargs):
    try:
        response = httpx.request(metodo, url, timeout=DEFAULT_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return None


def profilo_instagram():
    token = token_accesso()
    if not token:
        return None
    url = f"{BASE_URL}/me"
    params = {
        "fields": "user_id,username,profile_picture_url,followers_count",
        "access_token": token,
    }
    return esegui_richiesta("GET", url, params=params)


def crea_media_instagram(url_risorsa: str, caption: str, user_id: str):
    token = token_accesso()
    if not token:
        return None
    url = f"{BASE_URL}/{user_id}/media"
    payload = {"image_url": url_risorsa, "caption": caption}
    return esegui_richiesta("POST", url, headers=headers_autorizzazione(token), json=payload)


def pubblica_media_instagram(user_id: str, media_id: str):
    token = token_accesso()
    if not token:
        return None
    url = f"{BASE_URL}/{user_id}/media_publish"
    payload = {"creation_id": media_id}
    return esegui_richiesta("POST", url, headers=headers_autorizzazione(token), params=payload)
