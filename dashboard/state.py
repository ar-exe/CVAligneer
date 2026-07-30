import streamlit as st

def init_session_state():
    defaults = {
        "candidate_profile": None,
        "github_analysis": {},
        "profile_ready": False,
        "saved_jobs": [],
        "gap_analyses": [],
        "selected_job_url": None,
        "selected_job": None,
        "selected_job_similarity": None,
        "job": None,
        "briefing": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value