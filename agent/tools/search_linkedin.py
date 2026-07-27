from langchain_core.tools import tool
from core.config import settings
from agent.tools.openserp import OpenSERPClient



serp_client = OpenSERPClient(settings.open_serp_url)


@tool
def search_linkedin_profiles_by_company(company_name: str, role: str = "", limit: int = 5) -> str:

    """Search The internet for LinkedIN profiles related to company and a role."""
    result = serp_client.search_linkedin_profiles_by_company(company_name, role, limit)
    return result

@tool
def search_linkedin_profiles_by_title(title: str, location: str = "", limit: int = 5) -> str:
    """Search The internet for LinkedIn based on a role and location."""
    result = serp_client.search_linkedin_profiles_by_title(role=title, location=location, limit=limit)
    return result