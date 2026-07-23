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
from core.models import JobListing, CandidateProfile
from core.llm import get_llm_client, get_chat_model, get_embedding_model, get_ollama_client
from core.config import settings


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
    page = BeautifulSoup(response.text, 'html.parser')
    for tag in page(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    page = page.get_text(separator='\n', strip=True)
    # print(page)
    return page

def embed_text(text: str) -> list[float]:
    client = get_ollama_client()
    response = client.embeddings.create(
        model=get_embedding_model(),
        input=text
    )
    return response.data[0].embedding

def _profile_to_str(profile: CandidateProfile, github_analysis: dict) -> str:
    parts = []
    parts.append(f"Name: {profile.full_name}")
    parts.append(f"Skille: {profile.skills}")

    for exp in profile.experience:
        parts.append(f"Experience: {exp.role} at {exp.company}. {' '.join(exp.description)}")
    for proj in profile.projects:
        parts.append(f"Project: {proj.name}. {proj.description}")

    if github_analysis:
        parts.append(f"Github: {github_analysis.get('github_summary', '')}")
        parts.append(f"Inferred Skills: {', '.join(github_analysis.get('skills_inferred', []))}")

    return '\n'.join(parts)

def embed_candidate_profile(profile: CandidateProfile, github_analysis: dict = {}) -> list[float]:
    string = _profile_to_str(profile, github_analysis)
    embed = embed_text(string)
    return embed

def embed_job_listing(job: JobListing) -> list[float]:
    text = f"{job.title} at {job.company}. {job.location}. Required Skills: {', '.join(job.required_skills)}. Tech Stack: {', '.join(job.tech_stack)}. Experience Level: {job.experience_level}. Description: {job.description[:2000]}"
    embed = embed_text(text)
    return embed