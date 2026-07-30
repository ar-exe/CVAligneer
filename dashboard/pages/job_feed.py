from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.state import init_session_state
from ingestion.job_ingestor import ingest_job_from_url, load_jobs, save_job
from core.database import save_job_listing
from core.embeddings import embed_job_listing
from matching.ranker import rank_jobs_for_candidate
from matching.gap_analyzer import analyze_gap


init_session_state()

st.title("Job Feed")

job_url = st.text_input("paste job listing URL")
if st.button("Add Job to Inbox"):
    job = ingest_job_from_url(job_url)
    job_emb = embed_job_listing(job)
    save_job_listing(job, job_emb)
    st.success("Successfully added Job!")
ranks = None

if st.button("Run Matching"):
    ranks = rank_jobs_for_candidate(candidate=st.session_state.candidate_profile)
    st.session_state.ranks = ranks
else:
    ranks = st.session_state.get("ranks", [])
if ranks:
    for job in ranks:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"###{job['title']}")
                st.markdown(f"**{job['company']}** - {job['job'].location}")
            with col2:
                score = job['similarity_score']
                st.metric("Match Score", f"{score:.0%}")
            if st.button("Deep Dive ->", key=f"dive_{job['job_id']}"):
                st.session_state.selected_job_id = job["job_id"]
                st.session_state.selected_job = job["job"].model_dump()
                st.session_state.selected_job_similarity = job["similarity_score"]
                st.switch_page("pages/job_deep_dive.py")






