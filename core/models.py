from datetime import datetime
from pydantic import BaseModel, PositiveInt
from typing import Optional
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
class WorkExperience(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: Optional[str] = None
    description: list[str]
    technologies: list[str]



class Education(BaseModel):
    institution: str
    degree: str
    field: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    grade: Optional[str] = None



class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: list[str]
    url: Optional[str] = None
    highlights: list[str]




class Publication(BaseModel):
    title: str
    venue: str
    year: int
    summary: str
    url: Optional[str] = None


class CandidateProfile(BaseModel):
    full_name: str
    email: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str]
    experience: list[WorkExperience]
    education: list[Education]
    projects: list[Project]
    publications: list[Publication] = []
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None

class JobListing(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: str
    url: str
    salary_min: Optional[float] = 0.0
    salary_max: Optional[float] = 0.0
    contracr_type: Optional[str] = None
    date_posted: Optional[str] = None
    source: str = 'manual'
    saved_at: str = ""
    required_skills: list[str] = []
    tech_stack: list[str] = []
    experience_level: Optional[str] = None

class GapAnalysis(BaseModel):
    job_title: str
    company: str
    similarity_score: float
    overall_fit: str
    matching_skills: list[str]
    missing_skills: list[str]
    cv_improvements: list[str]
    talking_points: list[str]
    recommendation: str

class CompanyBrief(BaseModel):
    company: str
    what_they_build: str
    real_tech_stack: list[str]
    culture_signals: list[str]
    engineering_blog_url: Optional[str]
    notable_engineers: list[str]
    talking_points: list[str]
    red_flags: Optional[list[str]]
    brief_summary: str
    sources_consulted: list[str]

class CompanyBrief(BaseModel):
    model_config = ConfigDict(
        extra="ignore",          # ignore unexpected keys from the LLM
        populate_by_name=True,   # allow aliases / field names
        str_strip_whitespace=True
    )

    company: str
    what_they_build: str = ""
    real_tech_stack: list[str] = Field(default_factory=list)
    culture_signals: list[str] = Field(default_factory=list)
    engineering_blog_url: Optional[str] = None
    notable_engineers: list[str] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    brief_summary: str = Field(default="", alias="briefing_summary")
    sources_consulted: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: Any):
        if not isinstance(data, dict):
            return data

        data = dict(data)

        # Accept common field-name variants from the model
        alias_map = {
            "briefing_summary": "brief_summary",
            "brief summary": "brief_summary",
            "what_they_build": "what_they_build",
            "real_techstack": "real_tech_stack",
            "real_tech_stack": "real_tech_stack",
            "engineering_blog": "engineering_blog_url",
        }

        for old_key, new_key in alias_map.items():
            if old_key in data and new_key not in data:
                data[new_key] = data.pop(old_key)

        # Fill missing optional / list fields safely
        defaults = {
            "what_they_build": "",
            "engineering_blog_url": None,
            "brief_summary": "",
            "real_tech_stack": [],
            "culture_signals": [],
            "notable_engineers": [],
            "talking_points": [],
            "red_flags": [],
            "sources_consulted": [],
        }

        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default

        return data
    