import json
import base64
import httpx
from core.llm import get_llm_client, get_chat_model
from core.config import settings

def fetch_repos(username: str) -> list[dict]:
    url = f"https://api.github.com/users/{username}/repos"
    response = httpx.get(url, headers = {"Authorization": f"Bearer {settings.github_token}"}, params={"sort": "updated", "per_page": 10})
    response.raise_for_status() # Raise an exception for bad status codes
    repos = response.json()
    # print(json.dumps(repos, indent=2))
    return json.dumps(repos, indent=2)

def fetch_readme(username: str, repo_name: str) -> str:
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    response = httpx.get(url, headers = {"Authorization": f"Bearer {settings.github_token}"})
    if response.status_code == 404:
        return ""
    response.raise_for_status()
    readme = response.json()
    readme = base64.b64decode(readme["content"]).decode("utf-8")
    # print(readme)
    return readme

def analyze_github(username: str) -> dict:
    repos = fetch_repos(username=username)
    parsed_repos = json.loads(repos)
    print(f"Total repositories fetched: {len(parsed_repos)}")
    summaries = []
    for i in range(len(parsed_repos)):
        summary = {}
        summary['name'] = parsed_repos[i].get('name')
        summary['description'] = parsed_repos[i].get('description')
        summary['language'] = parsed_repos[i].get('language')
        summary['stars'] = parsed_repos[i].get('stargazers_count')
        summary['topics'] = parsed_repos[i].get('topics')
        summary['readme'] = fetch_readme(username=username, repo_name=summary['name'])
        summaries.append(summary)
    

    messages = [
    {
        "role": "system",
        "content": (
            """
                You are a developer profile parser. Extract information from the input text and return only a single JSON object with these exact fields:

                - primary_languages: list of strings
                - technical_domains: list of strings
                - notable_projects: list of strings
                - skills_inferred: list of strings
                - github_summary: a 2-3 sentence paragraph about this developer

                Requirements:
                - Return only valid JSON, no extra text, no markdown, no explanations.
                - Use exact field names.
                - If a field cannot be inferred, return an empty list for list fields and an empty string for `github_summary`.
                - Do not invent any information.
                - Keep `github_summary` short and factual.

                Example output shape:
                {
                "primary_languages": ["Python", "JavaScript"],
                "technical_domains": ["computer vision", "NLP", "data pipelines"],
                "notable_projects": ["Project A: one-sentence description", "Project B: one-sentence description"],
                "skills_inferred": ["machine learning", "API design", "cloud deployment"],
                "github_summary": "A concise 2-3 sentence paragraph describing the developer."
                } """
        )
    },
    {
    "role": "user",
    "content": f"Parse this text and return JSON:\n\n{str(summaries)}"
    }]
    client = get_llm_client()
    response = client.chat.completions.create(
    model=get_chat_model(),
    response_format={'type': 'json_object'},
    messages=messages,
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    print(data)