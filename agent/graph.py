# from langchain.agents import create_react_agent
# from langchain_classic import create
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from agent.tools.search import web_search
from agent.tools.web_scraper import scrape_page
from agent.tools.search_linkedin import search_linkedin_profiles_by_company
from core.llm import get_langchain_llm
from core.models import CompanyBrief
import json

def build_research_agent():
    llm = get_langchain_llm()
    tools = [web_search, scrape_page, search_linkedin_profiles_by_company]
    system_message = SystemMessage(content="""
    You are an expert company intelligence researcher. 
    Given a company name and job URL, your goal is to produce a comprehensive research briefing.
    
    You have access to these tools:
    - web_search: search for information about the company
    - scrape_page: read full content of a webpage
    - search_linkedin_profiles_by_company: find engineers who work at the company
    
    Research process:
    1. Search for what the company builds and its core product
    2. Scrape the company's about page or homepage  
    3. Search for their tech stack and engineering practices
    4. Find engineers at the company on LinkedIn
    5. Search for their engineering blog or technical content
    
    After researching, return a JSON object with exactly these fields:
    - what_they_build (str)
    - real_tech_stack (list of strings)
    - culture_signals (list of strings)
    - engineering_blog_url (str or empty string)
    - notable_engineers (list of strings — "Name: role/profile URL")
    - talking_points (list of strings)
    - red_flags (list of strings)
    - briefing_summary (str — 3-4 sentences)
    - sources_consulted (list of URLs you visited)
    
    Return ONLY valid JSON as your final response, no other text.
    """)
    return create_agent(llm, tools, system_prompt=system_message, )

def research_company(company_name: str, job_url: str) -> CompanyBrief:
    agent = build_research_agent()
    user_message = f"""
    Research this company and job:
    Company: {company_name}
    Job URL: {job_url}
    
    Investigate what they build, their real tech stack, 
    engineering culture, and notable engineers.
    Return your findings as JSON.
    """
    
    # result = agent.invoke({
    #     "messages": [{"role": "user", "content": user_message}]
    # })
    # final_message = result['messages'][-1].content
    # parsed = json.loads(final_message)
    # return CompanyBrief(company=company_name, **parsed)
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    print(result)

    messages = result["messages"]
    print([type(m).__name__ for m in messages])
    print([getattr(m, "content", None) for m in messages])

    # Prefer the last AI message
    ai_messages = [m for m in messages if getattr(m, "type", None) == "ai"]
    if not ai_messages:
        raise ValueError(f"No AI response returned; full agent state: {result}")

    final_message = getattr(ai_messages[-1], "text", None) or getattr(ai_messages[-1], "content", "")
    if not final_message or not final_message.strip():
        raise ValueError(f"AI returned empty text; full agent state: {result}")

    parsed = json.loads(final_message)
    return CompanyBrief(company=company_name, **parsed)


import json
import re
from langchain_core.messages import AIMessage

def _message_to_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("text", "") or item.get("content", ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)

def _extract_json(text: str) -> str:
    text = text.strip()

    # Remove markdown fences if the model returns them
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    return text




import json
import re
from typing import Any

def extract_json_from_text(text: str) -> str:
    text = text.strip()

    # If the model already returned clean JSON
    if text.startswith("{") and text.endswith("}"):
        return text

    # If JSON is wrapped in code fences
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1).strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return candidate

    # Try to find the first JSON object in a larger text blob
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1].strip()
        return candidate

    raise ValueError("No JSON object found in model output.")

def format_to_company_brief(raw_report: str, company_name: str) -> dict:
    formatter_prompt = f"""
    Convert the following company research report into STRICT JSON with exactly these keys:
    - what_they_build
    - real_tech_stack
    - culture_signals
    - engineering_blog_url
    - notable_engineers
    - talking_points
    - red_flags
    - brief_summary
    - sources_consulted

    Rules:
    - Output JSON only.
    - Use empty string or empty list when unknown.
    - Do not add markdown.
    - Do not add commentary.

    Company: {company_name}

    Report:
    {raw_report}
    """
    response = get_langchain_llm().invoke(formatter_prompt)
    text = _message_to_text(response.content)
    text = extract_json_from_text(text)
    return json.loads(text)





def research_company(company_name: str, job_url: str) -> CompanyBrief:
    agent = build_research_agent()

    user_message = f"""
    Research this company and job:
    Company: {company_name}
    Job URL: {job_url}

    Investigate what they build, their real tech stack,
    engineering culture, and notable engineers.
    Return your findings as JSON.
    - brief_summary (str — 3-4 sentences)
    """

    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    messages = result["messages"]

    # Find the last AI message with actual content
    ai_messages = [m for m in messages if isinstance(m, AIMessage) and getattr(m, "content", None)]
    if not ai_messages:
        raise ValueError(f"No usable AI response returned. Full agent state: {result}")

    raw_final = _message_to_text(ai_messages[-1].content)
    raw_final = _extract_json(raw_final)

    if not raw_final.strip():
        raise ValueError(f"AI returned empty content. Full agent state: {result}")

    try:
        parsed = json.loads(raw_final)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON.\n\nRaw output:\n{raw_final}\n\nFull agent state: {result}"
        ) from e

    return CompanyBrief(company=company_name, **parsed)


def research_company(company_name: str, job_url: str) -> CompanyBrief:
    agent = build_research_agent()

    user_message = f"""
    Research this company and job:
    Company: {company_name}
    Job URL: {job_url}

    Investigate what they build, their real tech stack,
    engineering culture, and notable engineers.
    """

    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    messages = result["messages"]
    ai_messages = [m for m in messages if getattr(m, "content", None)]

    if not ai_messages:
        raise ValueError(f"No AI response returned. Full agent state: {result}")

    raw_report = _message_to_text(ai_messages[-1].content)

    parsed = format_to_company_brief(raw_report, company_name)

    # optional normalization fallback
    if "brief_summary" not in parsed and "briefing_summary" in parsed:
        parsed["brief_summary"] = parsed.pop("briefing_summary")

    return CompanyBrief(company=company_name, **parsed)