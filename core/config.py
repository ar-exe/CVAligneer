from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    llm_provider: str = 'groq'
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_chat_model: str = "llama3.1"
    emb_model_provider: str = "ollama"
    ollama_embedding_model: str = "nomic-embed-text:latest"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    groq_api_key: str =  ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_chat_model: str = 'llama-3.1-8b-instant'
    github_token: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    class Config:
        env_file = Path(__file__).resolve().parents[1] / ".env"



settings = Settings()
