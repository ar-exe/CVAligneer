from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    llm_provider: str = 'openrouter'
    ollama_base_url: str = "http://192.168.1.4:11434/"
    ollama_chat_model: str = "qwen3.5:9b"
    emb_model_provider: str = "ollama"
    ollama_embedding_model: str = "nomic-embed-text:latest"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    groq_api_key: str =  ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_chat_model: str = 'openai/gpt-oss-120b'
    # groq_chat_model: str = 'llama-3.1-8b-instant'
    github_token: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    open_serp_url: str = ""
    serpapi_key: str = ""
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_chat_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    # openrouter_chat_model: str = "google/gemma-4-26b-a4b-it:free"
    class Config:
        env_file = Path(__file__).resolve().parents[1] / ".env"



settings = Settings()
