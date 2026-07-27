from openai import OpenAI
from core.config import settings
from langchain_openai import ChatOpenAI

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
    elif settings.llm_provider == 'openrouter':
        return OpenAI(api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url)
    else:
        raise ValueError(f'Unknown LLM Provider: {settings.llm_provider}')
    
def get_chat_model() -> str:
    if settings.llm_provider == 'ollama':
        return settings.ollama_chat_model
    if settings.llm_provider == 'groq':
        return settings.groq_chat_model
    if settings.llm_provider == 'openrouter':
        return settings.openrouter_chat_model
    return settings.openai_chat_model

def get_ollama_client() -> OpenAI:
    return OpenAI(
                base_url=settings.ollama_base_url,
                api_key='ollama',
            )

def get_embedding_model() -> str:
    if settings.emb_model_provider == 'ollama':
        return settings.ollama_embedding_model
    return settings.openai_embedding_model

def get_langchain_llm():
    if settings.llm_provider == "groq":
        return ChatOpenAI(
            model=settings.groq_chat_model,
            base_url=settings.groq_base_url,
            api_key=settings.groq_api_key,
            temperature=0,
        )
    elif settings.llm_provider == "ollama":
        return ChatOpenAI(
            model=settings.ollama_chat_model,
            base_url=settings.ollama_base_url,
            api_key='ollama',
            temperature=0,
        )
    elif settings.llm_provider == "openrouter":
        return ChatOpenAI(
            model=settings.openrouter_chat_model,
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            temperature=0
        )
    else:
        return ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )