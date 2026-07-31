# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# import streamlit as st
# from dashboard.state import init_session_state
# from ingestion.job_ingestor import ingest_job_from_url, load_jobs, save_job
# from core.database import save_job_listing
# from core.embeddings import embed_job_listing
# from matching.ranker import rank_jobs_for_candidate
# from matching.gap_analyzer import analyze_gap


# init_session_state()

# st.title("Job Feed")

# job_url = st.text_input("paste job listing URL")
# if st.button("Add Job to Inbox"):
#     job = ingest_job_from_url(job_url)
#     job_emb = embed_job_listing(job)
#     save_job_listing(job, job_emb)
#     st.success("Successfully added Job!")
# ranks = None

# if st.button("Run Matching"):
#     ranks = rank_jobs_for_candidate(candidate=st.session_state.candidate_profile)
#     st.session_state.ranks = ranks
# else:
#     ranks = st.session_state.get("ranks", [])
# if ranks:
#     for job in ranks:
#         with st.container(border=True):
#             col1, col2 = st.columns([3, 1])
#             with col1:
#                 st.markdown(f"###{job['title']}")
#                 st.markdown(f"**{job['company']}** - {job['job'].location}")
#             with col2:
#                 score = job['similarity_score']
#                 st.metric("Match Score", f"{score:.0%}")
#             if st.button("Deep Dive ->", key=f"dive_{job['job_id']}"):
#                 st.session_state.selected_job_id = job["job_id"]
#                 st.session_state.selected_job = job["job"].model_dump()
#                 st.session_state.selected_job_similarity = job["similarity_score"]
#                 st.switch_page("pages/job_deep_dive.py")







from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.state import init_session_state
from ingestion.job_ingestor import ingest_job_from_url
from core.database import save_job_listing
from core.embeddings import embed_job_listing
from matching.ranker import rank_jobs_for_candidate

init_session_state()

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .job-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.15s;
    }
    .job-card:hover {
        border-color: #d1d5db;
    }
    .job-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #111827;
        margin: 0 0 2px 0;
    }
    .job-meta {
        font-size: 0.85rem;
        color: #6b7280;
        margin: 0;
    }
    .score-ring {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .score-value {
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1;
    }
    .score-label {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-top: 2px;
    }
    .score-high  { color: #16a34a; }
    .score-mid   { color: #d97706; }
    .score-low   { color: #dc2626; }

    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 12px;
    }
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #9ca3af;
    }
    .empty-state p {
        margin: 0;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## Job feed")

if not st.session_state.profile_ready:
    st.warning("Parse your CV first — head back to the home page.")
    st.stop()

st.caption("Add job listings below, then run matching to see how you rank.")

# ── Add job (inline, no sidebar duplication) ──────────────────────────────────
with st.expander("Add a job listing", icon="➕"):
    job_url = st.text_input("Job URL", placeholder="https://…", label_visibility="collapsed")
    if st.button("Save job", type="primary"):
        if not job_url.strip():
            st.error("Paste a job URL first.")
        else:
            with st.spinner("Fetching job listing…"):
                job = ingest_job_from_url(job_url)
                job_emb = embed_job_listing(job)
                save_job_listing(job, job_emb)
                st.session_state.saved_jobs.append(job)
                st.success(f"'{job.title}' saved.")

st.divider()

# ── Run matching ──────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([2, 5])
with col_btn:
    run_matching = st.button("Run matching", type="primary", use_container_width=True)
with col_info:
    if st.session_state.ranks:
        n = len(st.session_state.ranks)
        st.caption(f"Showing {n} ranked job{'s' if n != 1 else ''}. Re-run to refresh.")

if run_matching:
    if not st.session_state.profile_ready:
        st.error("No profile found. Parse your CV first.")
    else:
        with st.spinner("Ranking jobs…"):
            ranks = rank_jobs_for_candidate(candidate=st.session_state.candidate_profile)
            st.session_state.ranks = ranks

ranks = st.session_state.get("ranks", [])

# ── Job cards ─────────────────────────────────────────────────────────────────
if not ranks:
    st.markdown(
        """
        <div class="empty-state">
            <p>No results yet — add some jobs and hit <strong>Run matching</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="section-label">Ranked results</div>', unsafe_allow_html=True)

    for job in ranks:
        score = job["similarity_score"]
        pct = int(round(score * 100))

        if pct >= 70:
            score_class = "score-high"
        elif pct >= 45:
            score_class = "score-mid"
        else:
            score_class = "score-low"

        location = getattr(job["job"], "location", None) or "Location not listed"

        with st.container():
            # Card wrapper via columns — Streamlit doesn't support custom card HTML
            # with interactive buttons inside, so we use a container + border trick.
            left, right = st.columns([5, 1])

            with left:
                st.markdown(
                    f"""
                    <div style="padding: 0.1rem 0;">
                        <p class="job-title">{job['title']}</p>
                        <p class="job-meta">{job['company']} &nbsp;·&nbsp; {location}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with right:
                st.markdown(
                    f"""
                    <div class="score-ring">
                        <span class="score-value {score_class}">{pct}%</span>
                        <span class="score-label">match</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            btn_col, spacer = st.columns([2, 5])
            with btn_col:
                if st.button("Deep dive →", key=f"dive_{job['job_id']}"):
                    st.session_state.selected_job_id = job["job_id"]
                    st.session_state.selected_job = job["job"].model_dump()
                    st.session_state.selected_job_similarity = job["similarity_score"]
                    st.session_state.gap_analysis = None  # reset stale analysis
                    st.switch_page("pages/job_deep_dive.py")

            st.divider()