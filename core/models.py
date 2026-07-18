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
    field: str
    start_date: str
    end_date: Optional[str] = None
    grade: Optional[str] = None



class Project(BaseModel):
    name: str
    description: str
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
    publications: Optional[Publication] = []
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None