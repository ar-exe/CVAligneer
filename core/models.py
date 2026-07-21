from datetime import datetime
from pydantic import BaseModel, PositiveInt
from typing import Optional

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
