from langchain_core.tools import tool
from core.config import settings
from agent.tools.openserp import OpenSERPClient
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from core.models import JobListing, CandidateProfile
from core.llm import get_llm_client, get_chat_model, get_embedding_model, get_ollama_client
from core.config import settings


@tool
def scrape_page(url: str) -> str:
    """Scrape the text content of a webpage.
    Use this to read company about pages,
    engineering blogs, or job listing pages in full."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = httpx.get(url=url, headers=headers)
    page = BeautifulSoup(response.text, 'html.parser')
    for tag in page(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    page = page.get_text(separator='\n', strip=True)
    # print(page)
    return page