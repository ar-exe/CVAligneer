from openai import OpenAI
from core.config import settings

def get_llm_client() -> OpenAI:
    if settings.llm_provider == 'ollama':
        return OpenAI(
            base_url=settings.ollama_base_url,
            api_key='ollama',
        )
    elif settings.llm_provider == 'openai':
        return OpenAI(api_key=settings.openai_api_key)
    elif settings.llm_provider == 'groq':
        return OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)
    else:
        raise ValueError(f'Unknown LLM Provider: {settings.llm_provider}')
    
def get_chat_model() -> str:
    if settings.llm_provider == 'ollama':
        return settings.ollama_chat_model
    if settings.llm_provider == 'groq':
        return settings.groq_chat_model
    return settings.openai_chat_model

def get_embedding_model() -> str:
    if settings.llm_provider == 'ollama':
        return settings.ollama_embedding_model
    return settings.openai_embedding_model