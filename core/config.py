from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = 'groq'
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_chat_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    groq_api_key: str =  ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_chat_model: str = 'openai/gpt-oss-20b'
    github_token: str = ""
    class Config:
        env_file = '.env'


settings = Settings()
