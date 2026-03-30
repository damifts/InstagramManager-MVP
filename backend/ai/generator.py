import os
from typing import Any


MODELLO_GEMINI = "gemini-pro"


def prompt_instagram(argomento: str, tono: str = "professionale") -> str:
    return f"Scrivi un post Instagram in tono {tono} su: {argomento}".strip()


def gemini_config() -> dict[str, str]:
    return {
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": MODELLO_GEMINI,
    }


def test_connessione_gemini() -> bool:
    return bool(gemini_config()["api_key"])


class ContentGenerator:
    async def generate_post(self, topic: str, social: str = "instagram", tone: str = "professionale") -> dict[str, Any]:
        if social.lower() != "instagram":
            return {"success": False, "error": "Per ora e supportato solo Instagram"}

        testo = prompt_instagram(topic, tone)
        return {
            "success": True,
            "generated_text": testo,
            "social_target": "instagram",
            "tone": tone,
            "metadata": {"char_count": len(testo), "max_chars": 2200},
        }


def get_content_generator() -> ContentGenerator:
    return ContentGenerator()
