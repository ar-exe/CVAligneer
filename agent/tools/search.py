from langchain_core.tools import tool
from core.config import settings
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def web_search(query: str) -> str:
    search = DuckDuckGoSearchRun()
    result = search.invoke('Top AI Research Papers Ever 2026')
    return result