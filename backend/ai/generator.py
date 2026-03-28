import os
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
from app.richieste import richiesteClass

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY non trovata nel file .env")

client = genai.Client(api_key=api_key)


# =====================================================
# MODELLO POST
# =====================================================

class InstagramPost:
    def __init__(self, caption: str, hashtags: str, cta: str):
        self.caption = caption
        self.hashtags = hashtags
        self.cta = cta

    def full_caption(self):
        return f"{self.caption}\n\n{self.hashtags}\n\n{self.cta}"

    def to_dict(self):
        return {
            "caption": self.caption,
            "hashtags": self.hashtags,
            "cta": self.cta
        }

    def __str__(self):
        return self.full_caption()


# =====================================================
# CONTENT GENERATOR (Gemini)
# =====================================================

class ContentGenerator:

    SYSTEM_PROMPT = """Sei un social media manager esperto.
Dato un prompt dell'utente, crea un post Instagram.
Rispondi SOLO in questo formato, senza testo aggiuntivo o emoticon:

CAPTION: <testo della caption>
HASHTAGS: <lista hashtag separati da spazi>
CALL-TO-ACTION: <frase di invito all'azione>"""

    def __init__(self):
        self.chat = client.chats.create(
            model="gemini-2.5-flash-lite",
            config=GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT
            )
        )

    def generate_post(self, user_prompt: str) -> InstagramPost:
        response = self.chat.send_message(user_prompt)
        text = response.text.strip()

        lines = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                lines[key.strip().upper()] = value.strip()

        return InstagramPost(
            caption=lines.get("CAPTION", ""),
            hashtags=lines.get("HASHTAGS", ""),
            cta=lines.get("CALL-TO-ACTION", "")
        )

    def publish_post(self, post: InstagramPost, image_url: str):

        # Recupero utente Instagram
        user_data = richiesteClass.retriveUserReq()
        if not user_data:
            return {"error": "Errore nel recupero utente"}

        user_id = user_data.get("id") or user_data.get("user_id")
        if not user_id:
            return {"error": "User ID non trovato"}

        # Creo media container
        media = richiesteClass.CreateMediaReq(
            url_risorsa=image_url,
            caption=post.full_caption(),
            user_id=user_id
        )

        if not media:
            return {"error": "Errore creazione media"}

        media_id = media.get("id")
        if not media_id:
            return {"error": "Media ID non trovato"}

        # Pubblico
        published = richiesteClass.PostMediaReq(
            user_id=user_id,
            media_id=media_id
        )

        if not published:
            return {"error": "Errore pubblicazione"}

        return published


