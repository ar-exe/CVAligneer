# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# import streamlit as st
# from ingestion.cv_parser import parse_cv
# from ingestion.github_analyzer import analyze_github
# from core.embeddings import embed_candidate_profile, embed_job_listing
# from core.database import save_candidate_profile, save_job_listing, load_all_job_listings
# from dashboard.state import init_session_state
# from ingestion.job_ingestor import ingest_job_from_url
# import tempfile
# from core.config import settings
# st.sidebar.write({
#   "emb_model_provider": settings.emb_model_provider,
#   "ollama_base_url": settings.ollama_base_url,
#   "openai_api_key_set": bool(settings.openai_api_key),
# })
# init_session_state()

# st.set_page_config(
#     page_title="CVAligneer",
#     layout="wide"
# )

# if st.session_state.profile_ready is not True:
#     st.title("Welcome to CVAligneer!")
#     st.caption("Ever had the question of whether your CV is a good match for a certain job lisitng?")
#     st.caption("CVAligneer helps you answering this question by using AI to parse your CV and the Job Listing to see how far or matching you are to this job")
#     # st.subheader("Ever")

# with st.sidebar:
#     st.title("CVAligneer")
#     st.divider()

#     st.subheader("Your Profile")
#     temp = tempfile.NamedTemporaryFile()
#     uploaded_cv = st.file_uploader("Upload your CV", type=["pdf"])
#     github_username = st.text_input("Github Username (optional but recommended :))")

#     if st.button("Parse Profile", type="primary"):
#         if uploaded_cv is not None:
#             with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
#                 temp_file.write(uploaded_cv.read())
#                 temp_path = temp_file.name
#         parsed_cv = parse_cv(temp_path)
#         github_analysis = analyze_github(github_username)
#         emb_profile = embed_candidate_profile(parsed_cv, github_analysis)
#         st.session_state.candidate_profile = parsed_cv
#         st.session_state.github_analysis = github_analysis
#         st.session_state.profile_ready=True
#         save_candidate_profile(parsed_cv, emb_profile, github_analysis)
#     else:
#         st.error("Please upload a valid PDF CV file")
#     if st.session_state.profile_ready:
#         st.success("Profile Ready")
#     st.divider()

#     st.subheader("Add a Job")
#     job_url = st.text_input("Paste job URL")

#     if st.button("Save Job"):
#         ingested_job = ingest_job_from_url(job_url)
#         emb_job = embed_job_listing(ingested_job)
#         save_job_listing(ingested_job, emb_job)
#         st.session_state.saved_jobs.append(ingested_job)
#     st.divider()

#     if st.session_state.profile_ready:
#         st.success(f"✓ {st.session_state.candidate_profile.full_name}")
#         st.info(f"{len(st.session_state.saved_jobs)} jobs saved")
#     else:
#         st.warning("Upload your CV to get started")

# if st.session_state.profile_ready is True:

#     with st.container():
#         st.subheader("Profile Summary")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.write("**Skills**")
#             st.write(", ".join(parsed_cv.skills))
#         with col2:
#             st.write("**Experiences**")
#             exp_strings = [
#                 f"{e.role} at {e.company} ({e.start_date or ''} - {e.end_date or 'present'})"
#                 for e in parsed_cv.experience
#             ]
#             st.write(", ".join(exp_strings) or "No experiences listed")


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import tempfile

from ingestion.cv_parser import parse_cv
from ingestion.github_analyzer import analyze_github
from core.embeddings import embed_candidate_profile, embed_job_listing
from core.database import save_candidate_profile, save_job_listing
from dashboard.state import init_session_state
from ingestion.job_ingestor import ingest_job_from_url

init_session_state()

st.set_page_config(
    page_title="CVAligneer",
    page_icon="⚡",
    layout="wide",
)

# ── Global styles ────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Sidebar header */
    [data-testid="stSidebar"] h1 {
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* Tighten sidebar sections */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }

    /* Profile badge pill */
    .profile-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #e8f5e9;
        color: #2e7d32;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 20px;
        margin-top: 4px;
    }

    /* Welcome hero */
    .hero-block {
        padding: 3rem 0 2rem 0;
    }
    .hero-block h1 {
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .hero-block p {
        font-size: 1.05rem;
        color: #6b7280;
        max-width: 520px;
        line-height: 1.6;
    }

    /* Step cards on welcome screen */
    .step-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        height: 100%;
    }
    .step-card .step-num {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 6px;
    }
    .step-card h3 {
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 4px 0;
    }
    .step-card p {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0;
        line-height: 1.5;
    }

    /* Profile summary section */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 6px;
    }
    .skill-chip {
        display: inline-block;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        font-size: 0.8rem;
        padding: 2px 8px;
        margin: 2px 3px 2px 0;
        color: #374151;
    }
    .exp-item {
        font-size: 0.875rem;
        padding: 6px 0;
        border-bottom: 1px solid #f3f4f6;
        color: #374151;
        line-height: 1.4;
    }
    .exp-item:last-child {
        border-bottom: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## CVAligneer")
    st.divider()

    # ── CV upload ────────────────────────────────────────────────────────────
    st.markdown("**Your profile**")
    uploaded_cv = st.file_uploader("CV (PDF)", type=["pdf"], label_visibility="collapsed")
    github_username = st.text_input(
        "GitHub username",
        placeholder="optional, but recommended",
    )

    parse_clicked = st.button("Parse profile", type="primary", use_container_width=True)

    if parse_clicked:
        if uploaded_cv is None:
            st.error("Upload a PDF CV to continue.")
        else:
            with st.spinner("Parsing your CV…"):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded_cv.read())
                    tmp_path = tmp.name

                parsed_cv = parse_cv(tmp_path)
                github_analysis = analyze_github(github_username) if github_username.strip() else {}
                emb_profile = embed_candidate_profile(parsed_cv, github_analysis)

                st.session_state.candidate_profile = parsed_cv
                st.session_state.github_analysis = github_analysis
                st.session_state.profile_ready = True

                save_candidate_profile(parsed_cv, emb_profile, github_analysis)

    if st.session_state.profile_ready:
        profile = st.session_state.candidate_profile
        st.markdown(
            f'<div class="profile-badge">✓ {profile.full_name}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Job ingestion ─────────────────────────────────────────────────────────
    st.markdown("**Add a job**")
    job_url = st.text_input(
        "Job URL",
        placeholder="https://…",
        label_visibility="collapsed",
    )
    if st.button("Save job", use_container_width=True):
        if not job_url.strip():
            st.error("Paste a job URL first.")
        else:
            with st.spinner("Fetching job listing…"):
                ingested_job = ingest_job_from_url(job_url)
                emb_job = embed_job_listing(ingested_job)
                save_job_listing(ingested_job, emb_job)
                st.session_state.saved_jobs.append(ingested_job)
                st.success("Job saved.")

    if st.session_state.saved_jobs:
        n = len(st.session_state.saved_jobs)
        st.caption(f"{n} job{'s' if n != 1 else ''} saved")

    st.divider()

    if not st.session_state.profile_ready:
        st.info("Upload your CV to get started.")


# ── Main area ─────────────────────────────────────────────────────────────────
if not st.session_state.profile_ready:
    # Welcome / onboarding screen
    st.markdown(
        """
        <div class="hero-block">
            <h1>Does your CV fit<br>the job?</h1>
            <p>CVAligneer parses your CV and the job listing, then tells you exactly
            where you match — and where you don't.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    steps = [
        ("01", "Upload your CV", "Add your PDF in the sidebar and optionally link your GitHub account."),
        ("02", "Save job listings", "Paste any job URL and CVAligneer will scrape and index it."),
        ("03", "Run the analysis", "Get a match score, gap analysis, and interview talking points."),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-num">{num}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    # Profile summary view
    profile = st.session_state.candidate_profile

    st.markdown(f"### {profile.full_name}")
    st.caption("Profile summary — head to **Job Feed** to run matching.")
    st.divider()

    col_skills, col_exp = st.columns([1, 2])

    with col_skills:
        st.markdown('<div class="section-label">Skills</div>', unsafe_allow_html=True)
        if profile.skills:
            chips = "".join(
                f'<span class="skill-chip">{s}</span>' for s in profile.skills
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No skills found.")

    with col_exp:
        st.markdown('<div class="section-label">Experience</div>', unsafe_allow_html=True)
        if profile.experience:
            items = []
            for e in profile.experience:
                period = f"{e.start_date or ''} – {e.end_date or 'present'}".strip(" –")
                items.append(
                    f'<div class="exp-item"><strong>{e.role}</strong> · {e.company}'
                    + (f' <span style="color:#9ca3af">· {period}</span>' if period else "")
                    + "</div>"
                )
            st.markdown("".join(items), unsafe_allow_html=True)
        else:
            st.caption("No experience listed.")