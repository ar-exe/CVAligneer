from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.cv_parser import parse_cv
from ingestion.github_analyzer import analyze_github
from ingestion.job_ingestor import ingest_job_from_url
from core.embeddings import embed_candidate_profile, embed_job_listing
from core.database import save_candidate_profile, save_job_listing, load_all_job_listings

# 1. Parse CV + GitHub
profile = parse_cv("/Users/abdelrahman-mohammed/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Abdelrahman_Mohammed_CV (8).pdf")
github  = analyze_github("ar-exe")

# 2. Embed + save candidate
embedding = embed_candidate_profile(profile, github)
pid = save_candidate_profile(profile, embedding, github)
print(f"Saved candidate: {pid}")

# 3. Ingest a real job URL
job = ingest_job_from_url("https://www.linkedin.com/jobs/view/4435584134/")

# 4. Embed + save job
job_embedding = embed_job_listing(job)
jid = save_job_listing(job, job_embedding)
print(f"Saved job: {jid}")

# 5. Load all jobs back
jobs = load_all_job_listings()
print(f"Total jobs in DB: {len(jobs)}")