import sys
import os

project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from core.models import JobListing
from core.llm import get_llm_client, get_chat_model
from core.config import settings

JOBS_STORE = Path("data/saved_jobs.json")

def _infer_source(url: str) -> str:
    if "linkedin.com" in url: return "linkedin"
    if "greenhouse.io" in url: return "greenhouse"
    if "lever.co" in url: return "lever"
    if "indeed.com" in url: return "indeed"
    if "workday.com" in url: return "workday"
    return "other"


def fetch_job_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = httpx.get(url=url, headers=headers)
    response.raise_for_status()
    page = BeautifulSoup(response.text, 'html.parser')
    for tag in page(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    page = page.get_text(separator='\n', strip=True)
    # print(page)
    return page

def extract_job_info(raw_text: str, url: str) -> JobListing:
    client = get_llm_client()
    messages = [
    {
        "role": "system",
        "content": (
            """
                You are a job listing parser.
                Extract structured information from this job page text and return a JSON object with exactly these fields: title (str), company (str), location (str), description (str — the full job description), required_skills (list of strings), tech_stack (list of strings — specific tools, frameworks, libraries), experience_level (one of: "junior", "mid", "senior", "lead", or null), contract_type (str or null), salary_min (number or null), salary_max (number or null). Return only valid JSON. If a field cannot be found, use null or empty list."""
        )
    },
    {
    "role": "user",
    "content": f"Parse this page and return JSON:\n\n{str(raw_text[:6000])}"
    }]
    response = client.chat.completions.create(
    model=get_chat_model(),
    response_format={'type': 'json_object'},
    messages=messages,
    )
    content = response.choices[0].message.content
    # x = JobListing.model_validate_json(content)
    # print(json.loads(content))
    parsed = json.loads(content)
    job = JobListing(url=url, source=_infer_source(url), **parsed)
    # print(x)
    return job

def save_job(job: JobListing) -> None:
    JOBS_STORE.parent.mkdir(parents=True, exist_ok=True)

    existing_jobs = []
    if JOBS_STORE.exists():
        with JOBS_STORE.open("r", encoding="utf-8") as f:
            existing_jobs = json.load(f)

    job.saved_at = datetime.utcnow().isoformat()

    jobs_by_url = {}
    for item in existing_jobs:
        if isinstance(item, dict) and item.get("url"):
            jobs_by_url[item["url"]] = item

    jobs_by_url[job.url] = job.model_dump()

    with JOBS_STORE.open("w", encoding="utf-8") as f:
        json.dump(list(jobs_by_url.values()), f, indent=2)

def load_jobs() -> list[JobListing]:
    if not JOBS_STORE.exists():
        return []

    with JOBS_STORE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [JobListing.model_validate(item) for item in data]


def ingest_job_from_url(url: str) -> JobListing:
    raw_text = fetch_job_page(url)
    job = extract_job_info(raw_text, url)
    save_job(job)
    return job