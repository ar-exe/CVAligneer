from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.state import init_session_state
from matching.gap_analyzer import analyze_gap
from core.models import JobListing, GapAnalysis


init_session_state()

if st.session_state.selected_job is None:
    st.warning("No job selected. Please go back to Job Feed and choose a job first.")
    st.stop()

profile = st.session_state.candidate_profile
job = JobListing.model_validate(st.session_state.selected_job)
similarity_score = st.session_state.selected_job_similarity or 0.0
if st.button("Run Deep Analysis"):
    analysis = analyze_gap(candidate=profile, job=job, similarity_score=similarity_score)


st.header(f"{job.title} at {job.company}")
st.divider()
st.subheader(f"Overall Fit {analysis.overall_fit}")
st.subheader(f"Similarity Score {analysis.similarity_score}")
st.divider()
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Matching Skills:")
    matching = analysis.matching_skills
    for skill in matching:
        st.write(f"✓ {skill}")

with col2:
    st.subheader("Missing Skills:")
    missing = analysis.missing_skills
    for skill in missing:
        st.write(f"✗ {skill}")

st.divider()

st.subheader("CV Improvements")
if analysis.cv_improvements:
    for improvement in analysis.cv_improvements:
        st.write(f"• {improvement}")

st.subheader("Talking Points")
if analysis.talking_points:
    for point in analysis.talking_points:
        st.write(f"• {point}")

st.subheader("Recommendation")
if analysis.recommendation:
    st.write(analysis.recommendation)


