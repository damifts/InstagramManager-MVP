"""
Gemini AI Configuration and Setup
Issue #15, #6: BE Gemini Setup e Model AI per GUI

TODO: Team AI (Andrea, Filippo)
- Ottenere API key da Google AI Studio
- Configurare GEMINI_API_KEY in .env
- Scegliere modello (gemini-pro, gemini-pro-vision)
- Testare con script test_gemini.py
"""

import os
from typing import Optional, Dict, Any, ListS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configurazione Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-pro-vision")

# Temperature e parametri
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024


class GeminiConfig:
    """
    Configurazione centralizzata per Gemini AI
    
    Issue #15: Setup Gemini
    TODO:
    - Validare API key all'avvio
    - Gestire rate limits
    - Configurare safety settings
    - Logging chiamate API
    """
    
    def __init__(self):
        """
        Inizializza configurazione Gemini
        
        Raises:
            ValueError: Se API key non configurata
        """
        if not GEMINI_API_KEY:
            raise ValueError(
                "❌ GEMINI_API_KEY non configurata!\n"
                "💡 Aggiungi GEMINI_API_KEY nel file .env\n"
                "🔗 Ottieni key da: https://makersuite.google.com/app/apikey"
            )
        
        # Configura Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Modello testo
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # Modello vision per immagini (issue #16)
        self.vision_model = genai.GenerativeModel(GEMINI_VISION_MODEL)
        
        # Generation config
        self.generation_config = {
            "temperature": DEFAULT_TEMPERATURE,
            "max_output_tokens": DEFAULT_MAX_TOKENS,
            "top_p": 0.95,
            "top_k": 40
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    
    def get_model(self, use_vision: bool = False) -> genai.GenerativeModel:
        """
        Restituisce modello Gemini appropriato
        
        Args:
            use_vision: True per modello vision (immagini)
            
        Returns:
            GenerativeModel: Modello Gemini
        """
        return self.vision_model if use_vision else self.model
    
    
    def update_temperature(self, temperature: float):
        """
        Aggiorna temperature per generazione
        
        Args:
            temperature: Valore 0.0-1.0 (più alto = più creativo)
        """
        self.generation_config["temperature"] = temperature
    
    
    def update_max_tokens(self, max_tokens: int):
        """
        Aggiorna max tokens output
        
        Args:
            max_tokens: Numero massimo token
        """
        self.generation_config["max_output_tokens"] = max_tokens


# Singleton instance
_gemini_config: Optional[GeminiConfig] = None


def get_gemini_config() -> GeminiConfig:
    """
    Restituisce singleton GeminiConfig
    
    Returns:
        GeminiConfig: Configurazione Gemini
        
    TODO: Gestire reinizializzazione in caso di errori
    """
    global _gemini_config
    
    if _gemini_config is None:
        _gemini_config = GeminiConfig()
    
    return _gemini_config


