from langchain_core.tools import tool
from core.config import settings
from agent.tools.openserp import OpenSERPClient


serp_client = OpenSERPClient(settings.open_serp_url)


@tool
def web_search(query: str) -> str:
    """Search the web for information about a company, person, or technology."""
    result = serp_client.search_for_agents(query)
    return result