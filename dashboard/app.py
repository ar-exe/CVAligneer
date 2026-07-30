from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from ingestion.cv_parser import parse_cv
from ingestion.github_analyzer import analyze_github
from core.embeddings import embed_candidate_profile, embed_job_listing
from core.database import save_candidate_profile, save_job_listing, load_all_job_listings
from dashboard.state import init_session_state
from ingestion.job_ingestor import ingest_job_from_url
import tempfile
from core.config import settings
st.sidebar.write({
  "emb_model_provider": settings.emb_model_provider,
  "ollama_base_url": settings.ollama_base_url,
  "openai_api_key_set": bool(settings.openai_api_key),
})
init_session_state()

st.set_page_config(
    page_title="CVAligneer",
    layout="wide"
)

if st.session_state.profile_ready is not True:
    st.title("Welcome to CVAligneer!")
    st.caption("Ever had the question of whether your CV is a good match for a certain job lisitng?")
    st.caption("CVAligneer helps you answering this question by using AI to parse your CV and the Job Listing to see how far or matching you are to this job")
    # st.subheader("Ever")

with st.sidebar:
    st.title("CVAligneer")
    st.divider()

    st.subheader("Your Profile")
    temp = tempfile.NamedTemporaryFile()
    uploaded_cv = st.file_uploader("Upload your CV", type=["pdf"])
    github_username = st.text_input("Github Username (optional but recommended :))")

    if st.button("Parse Profile", type="primary"):
        if uploaded_cv is not None:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(uploaded_cv.read())
                temp_path = temp_file.name
        parsed_cv = parse_cv(temp_path)
        github_analysis = analyze_github(github_username)
        emb_profile = embed_candidate_profile(parsed_cv, github_analysis)
        st.session_state.candidate_profile = parsed_cv
        st.session_state.github_analysis = github_analysis
        st.session_state.profile_ready=True
        save_candidate_profile(parsed_cv, emb_profile, github_analysis)
    else:
        st.error("Please upload a valid PDF CV file")
    if st.session_state.profile_ready:
        st.success("Profile Ready")
    st.divider()

    st.subheader("Add a Job")
    job_url = st.text_input("Paste job URL")

    if st.button("Save Job"):
        ingested_job = ingest_job_from_url(job_url)
        emb_job = embed_job_listing(ingested_job)
        save_job_listing(ingested_job, emb_job)
        st.session_state.saved_jobs.append(ingested_job)
    st.divider()

    if st.session_state.profile_ready:
        st.success(f"✓ {st.session_state.candidate_profile.full_name}")
        st.info(f"{len(st.session_state.saved_jobs)} jobs saved")
    else:
        st.warning("Upload your CV to get started")

if st.session_state.profile_ready is True:

    with st.container():
        st.subheader("Profile Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Skills**")
            st.write(", ".join(parsed_cv.skills))
        with col2:
            st.write("**Experiences**")
            exp_strings = [
                f"{e.role} at {e.company} ({e.start_date or ''} - {e.end_date or 'present'})"
                for e in parsed_cv.experience
            ]
            st.write(", ".join(exp_strings) or "No experiences listed")