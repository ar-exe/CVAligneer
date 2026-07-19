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
    messages = [
    {
        "role": "system",
        "content": (
            "You are a CV parser. Extract information from the CV text and return it as JSON "
            "matching this schema exactly. For any field you cannot find, use null for optional "
            "fields or an empty list for list fields. Do not invent information. Use this schema only as guidance. Return only the parsed JSON object. Do not output $defs, $ref, or schema metadata. return an empty string when any field is missing, instead of null.\n\n"
            "Schema:\n" + schema_json
        )
    },
    {
    "role": "user",
    "content": f"Parse this CV text and return JSON:\n\n{text}"
        }]

    response = client.chat.completions.create(
    model=get_chat_model(),
    response_format={'type': 'json_object'},
    messages=messages,
    )
    content = response.choices[0].message.content
    profile = CandidateProfile.model_validate_json(json_data=content)
    return profile
