from core.models import JobListing, CandidateProfile, GapAnalysis
from core.llm import get_llm_client, get_chat_model
import json
from matching.ranker import rank_jobs_for_candidate


def _format_experience(candidate: CandidateProfile) -> str:
    parts = []
    for exp in candidate.experience:
        parts.append(f"- {exp.role} at {exp.company} ({exp.start_date} to {exp.end_date or 'Present'})")
        parts.append(f"Technologies: {', '.join(exp.technologies)}")
    return '\n'.join(parts)

def _format_projects(candidate: CandidateProfile) -> str:
    parts = []
    for proj in candidate.projects:
        parts.append(f"- {proj.name}: {proj.description}")
        parts.append(f"Technologies: {', '.join(proj.technologies)}")
    return '\n'.join(parts)

def analyze_gap(candidate: CandidateProfile, job: JobListing, similarity_score: float, github_analysis: dict = {}) -> GapAnalysis:
    client = get_llm_client()
    messages = [
        {
            "role": "system",
            "content": (
                """
                    You are an expert technical recruiter and career coach.
                    You will be given a candidate profile and a job listing.
                    Analyse the fit and return a JSON object with exactly these fields:
                    overall_fit ("strong", "moderate", or "weak"),
                    matching_skills (list of strings),
                    missing_skills (list of strings),
                    cv_improvements (list of strings — specific rewrites for the candidate's CV bullets to better match this job),
                    talking_points (list of strings — strengths the candidate should emphasise),
                    recommendation (string — one paragraph).
                    Return only valid JSON. """
            )
        },
        {
        "role": "user",
        "content": f"""
                    CANDIDATE PROFILE:
                    Name: {candidate.full_name}
                    Skills: {', '.join(candidate.skills)}
                    Experience: {_format_experience(candidate)}
                    Projects: {_format_projects(candidate)}
                    GitHub: {github_analysis.get('github_summary', '')}
                    Inferred skills: {', '.join(github_analysis.get('skills_inferred', []))}

                    JOB LISTING:
                    Title: {job.title} at {job.company}
                    Location: {job.location}
                    Required skills: {', '.join(job.required_skills)}
                    Tech stack: {', '.join(job.tech_stack)}
                    Experience level: {job.experience_level}
                    Description: {job.description[:3000]}

                    SIMILARITY SCORE: {similarity_score} (0-1 scale, higher is better)

                    Analyse the fit between this candidate and this job.
                    """
        }]

    response = client.chat.completions.create(
    model=get_chat_model(),
    response_format={'type': 'json_object'},
    messages=messages,
    )
    content = response.choices[0].message.content
    analysis = json.loads(content)

    return GapAnalysis(
        job_title=job.title,
        company=job.company,
        similarity_score=float(similarity_score),
        **analysis,
    )

def analyze_top_matches(candidate: CandidateProfile, top_k: int = 5, github_analysis: dict = {}) -> list[GapAnalysis]:
    top_matches = rank_jobs_for_candidate(candidate, top_k) #list
    gaps = []
    for match in top_matches:
        job = match["job"]
        similarity_score = match['similarity_score']
        gap = analyze_gap(candidate, job, similarity_score)
        gaps.append(gap)
    return gaps