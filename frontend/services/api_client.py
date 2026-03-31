import os
from typing import Any

import httpx


DEFAULT_API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def call_api(method: str, api_base: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=20.0) as client:
        response = client.request(method=method, url=f"{api_base}{path}", json=payload)
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"raw": response.text}


def call_profile_with_fallback(api_base: str) -> dict[str, Any]:
    paths = ["/api/profile", "/profile", "/api/", "/"]
    last_exc: Exception | None = None
    for path in paths:
        try:
            return call_api("GET", api_base, path)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                last_exc = exc
                continue
            raise
    if last_exc:
        raise RuntimeError("Endpoint profilo non trovato. Verifica Backend URL e avvio del server.") from last_exc
    raise RuntimeError("Impossibile contattare il backend")


def get_profile(api_base: str) -> dict[str, Any]:
    return call_profile_with_fallback(api_base)


def create_media(api_base: str, url_risorsa: str, caption: str, user_id: str) -> dict[str, Any]:
    payload = {
        "url_risorsa": url_risorsa,
        "caption": caption,
        "user_id": user_id,
    }
    return call_api("POST", api_base, "/api/createPost", payload)


def publish_media(api_base: str, user_id: str, creation_id: str) -> dict[str, Any]:
    payload = {
        "user_id": user_id,
        "creation_id": creation_id,
    }
    return call_api("POST", api_base, "/api/PostMedia", payload)
