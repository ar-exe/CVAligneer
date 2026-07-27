from langchain_core.tools import tool
from bs4 import BeautifulSoup
import httpx


@tool
def scrape_page(url: str) -> str:
    """Scrape the text content of a webpage.
    Use this to read company about pages,
    engineering blogs, or job listing pages in full."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = httpx.get(url=url, headers=headers, follow_redirects=True)
    # response = httpx.get(url=url, headers=headers, follow_redirects=True)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        return ""
    page = BeautifulSoup(response.text, 'html.parser')
    for tag in page(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    page = page.get_text(separator='\n', strip=True)
    # print(page)
    return page[:6000]