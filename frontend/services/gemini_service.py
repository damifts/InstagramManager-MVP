import json
import os
from importlib import import_module
from typing import Any


MODEL_NAME = "gemini-1.5-flash"
FALLBACK_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def _extract_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start : end + 1]


def _normalize_model_name(name: str) -> str:
    if name.startswith("models/"):
        return name.split("/", 1)[1]
    return name


def _candidate_models(genai: Any) -> list[str]:
    candidates: list[str] = []
    env_model = os.getenv("GEMINI_MODEL", "").strip()

    if env_model:
        candidates.append(_normalize_model_name(env_model))
    candidates.append(MODEL_NAME)
    candidates.extend(FALLBACK_MODELS)

    try:
        for model_info in genai.list_models():
            methods = getattr(model_info, "supported_generation_methods", []) or []
            if "generateContent" not in methods:
                continue
            model_name = _normalize_model_name(getattr(model_info, "name", ""))
            if model_name and model_name not in candidates:
                candidates.append(model_name)
    except Exception:
        # Se list_models fallisce, useremo solo i fallback statici.
        pass

    # Mantiene l'ordine ma rimuove duplicati.
    unique_candidates: list[str] = []
    for name in candidates:
        if name and name not in unique_candidates:
            unique_candidates.append(name)
    return unique_candidates


def _generate_with_fallback(genai: Any, prompt: str) -> tuple[str, str]:
    last_error: Exception | None = None
    for model_name in _candidate_models(genai):
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            if text:
                return text, model_name
        except Exception as exc:
            last_error = exc
            continue

    if last_error is not None:
        raise RuntimeError(f"Gemini non disponibile con i modelli candidati: {last_error}") from last_error
    raise RuntimeError("Gemini non disponibile: nessun modello candidato valido")


def generate_caption_and_hashtags(topic: str, audience: str, tone: str, cta: str) -> dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY non configurata nel file .env")

    try:
        genai = import_module("google.generativeai")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Pacchetto mancante: installa google-generativeai con 'uv sync'"
        ) from exc

    prompt = f"""
Sei un social media manager esperto di Instagram.
Genera una caption e hashtag in italiano.

Input:
- Topic: {topic}
- Audience: {audience}
- Tone: {tone}
- CTA: {cta}

Regole:
- Caption massimo 2200 caratteri.
- Emoji solo se coerenti con il tone.
- Hashtag tra 8 e 12, rilevanti e non ripetuti.
- Restituisci solo JSON valido con schema:
{{
  "caption": "...",
  "hashtags": ["#tag1", "#tag2"],
  "first_comment": "..."
}}
""".strip()

    genai.configure(api_key=api_key)
    text, selected_model = _generate_with_fallback(genai, prompt)

    json_block = _extract_json_block(text)
    if not json_block:
        raise RuntimeError("Gemini non ha restituito un JSON valido")

    parsed = json.loads(json_block)
    caption = str(parsed.get("caption", "")).strip()
    hashtags = parsed.get("hashtags", [])
    first_comment = str(parsed.get("first_comment", "")).strip()

    if not caption:
        raise RuntimeError("Caption generata vuota")

    normalized_hashtags = [str(tag).strip() for tag in hashtags if str(tag).strip()]

    return {
        "caption": caption,
        "hashtags": normalized_hashtags,
        "first_comment": first_comment,
        "model": selected_model,
    }
