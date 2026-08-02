import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
from app.utils.logger import app_logger

def get_llm(temperature: float = 0.7, model_name: Optional[str] = None) -> BaseChatModel:
    model = model_name or settings.DEFAULT_MODEL
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        app_logger.info(f"Initializing ChatGoogleGenerativeAI with model: {model}")
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature,
        )
    else:
        app_logger.error("No GEMINI_API_KEY found in settings or environment")
        raise ValueError("GEMINI_API_KEY is not configured. Please set it in Backend/.env file.")
