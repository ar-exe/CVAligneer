import json
import fitz
from pathlib import Path
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from dotenv import load_dotenv
from core.models import CandidateProfile
from core.llm import get_chat_model, get_embedding_model, get_llm_client

def extract_text(pdf_path: str) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n".join(page.get_text() for page in doc)

def parse_cv(pdf_path: str) -> CandidateProfile:
    text = extract_text(Path(pdf_path))
    client = get_llm_client()
    schema = CandidateProfile.model_json_schema()
    schema_json = json.dumps(schema, indent=2)
    # messages = [
    # {
    #     "role": "system",
    #     "content": (
    #         "You are a CV parser. Extract information from the CV text and return it as JSON "
    #         "matching this schema exactly. For any field you cannot find, use null for optional "
    #         "fields or an empty list for list fields. Do not invent information. Use this schema only as guidance. Return only the parsed JSON object. Do not output $defs, $ref, or schema metadata. return an empty string when any field is missing, instead of null.\n\n"
    #         "Schema:\n" + schema_json
    #     )
    # },
    # {
    # "role": "user",
    # "content": f"Parse this CV text and return JSON:\n\n{text}"
    #     }]
    messages = [
    {
        "role": "system",
        "content": (
            "Extract a candidate profile from the CV text. "
            "Return only valid JSON with these exact keys: "
            "full_name, email, location, summary, skills, experience, "
            "education, projects, publications, github_username, linkedin_url. "
            "Use empty arrays or null when information is missing. "
            "Do not include markdown or explanations."
        )
    },
    {
        "role": "user",
        "content": f"Parse this CV into JSON:\n\n{text}"
    }
]

    response = client.chat.completions.create(
    model=get_chat_model(),
    response_format={'type': 'json_object'},
    messages=messages,
    )
    content = response.choices[0].message.content
    profile = CandidateProfile.model_validate_json(json_data=content)
    return profile


import json
from pathlib import Path
from pydantic import ValidationError
import fitz

from core.models import CandidateProfile
from core.llm import get_chat_model, get_llm_client

def extract_text(pdf_path: str) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n".join(page.get_text() for page in doc)

def _normalize_cv_payload(data: dict) -> dict:
    experience = []
    for item in data.get("experience", []):
        experience.append({
            "company": item.get("company", ""),
            "role": item.get("role") or item.get("title", ""),
            "start_date": item.get("start_date", ""),
            "end_date": item.get("end_date") or None,
            "description": item.get("description", []),
            "technologies": item.get("technologies", []),
        })

    education = []
    for item in data.get("education", []):
        education.append({
            "institution": item.get("institution", ""),
            "degree": item.get("degree", ""),
            "field": item.get("field") or None,
            "start_date": item.get("start_date", ""),
            "end_date": item.get("end_date") or None,
            "grade": item.get("grade") or None,
        })

    projects = []
    for item in data.get("projects", []):
        projects.append({
            "name": item.get("name", ""),
            "description": item.get("description") or None,
            "technologies": item.get("technologies", []),
            "url": item.get("url") or None,
            "highlights": item.get("highlights", []),
        })

    publications = []
    for item in data.get("publications", []):
        publications.append({
            "title": item.get("title", ""),
            "venue": item.get("venue", ""),
            "year": item.get("year", 0),
            "summary": item.get("summary", ""),
            "url": item.get("url") or None,
        })

    return {
        "full_name": data.get("full_name", ""),
        "email": data.get("email") or None,
        "location": data.get("location") or None,
        "summary": data.get("summary") or None,
        "skills": data.get("skills", []),
        "experience": experience,
        "education": education,
        "projects": projects,
        "publications": publications,
        "github_username": data.get("github_username") or None,
        "linkedin_url": data.get("linkedin_url") or None,
    }

def parse_cv(pdf_path: str) -> CandidateProfile:
    text = extract_text(Path(pdf_path))
    client = get_llm_client()

    messages = [
        {
            "role": "system",
            "content": (
                "Extract a candidate profile from the CV. "
                "Return valid JSON only. "
                "Use exactly this structure:\n"
                "{\n"
                "  'full_name': str,\n"
                "  'email': str|null,\n"
                "  'location': str|null,\n"
                "  'summary': str|null,\n"
                "  'skills': [str],\n"
                "  'experience': [\n"
                "    {\n"
                "      'company': str,\n"
                "      'role': str,\n"
                "      'start_date': str,\n"
                "      'end_date': str|null,\n"
                "      'description': [str],\n"
                "      'technologies': [str]\n"
                "    }\n"
                "  ],\n"
                "  'education': [\n"
                "    {\n"
                "      'institution': str,\n"
                "      'degree': str,\n"
                "      'field': str|null,\n"
                "      'start_date': str,\n"
                "      'end_date': str|null,\n"
                "      'grade': str|null\n"
                "    }\n"
                "  ],\n"
                "  'projects': [\n"
                "    {\n"
                "      'name': str,\n"
                "      'description': str|null,\n"
                "      'technologies': [str],\n"
                "      'url': str|null,\n"
                "      'highlights': [str]\n"
                "    }\n"
                "  ],\n"
                "  'publications': [\n"
                "    {\n"
                "      'title': str,\n"
                "      'venue': str,\n"
                "      'year': int,\n"
                "      'summary': str,\n"
                "      'url': str|null\n"
                "    }\n"
                "  ],\n"
                "  'github_username': str|null,\n"
                "  'linkedin_url': str|null\n"
                "}\n"
                "If a value is missing, use null or an empty list. "
                "Do not add any extra fields."
            )
        },
        {
            "role": "user",
            "content": f"Parse this CV into JSON:\n\n{text}"
        }
    ]

    response = client.chat.completions.create(
        model=get_chat_model(),
        response_format={"type": "json_object"},
        messages=messages,
            max_tokens=500,

    )

    content = response.choices[0].message.content
    raw = json.loads(content)

    normalized = _normalize_cv_payload(raw)
    try:
        return CandidateProfile.model_validate(normalized)
    except ValidationError as exc:
        raise ValueError(f"CV payload still invalid after normalization: {exc}") from exc