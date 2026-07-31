# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# import streamlit as st
# from dashboard.state import init_session_state
# from matching.gap_analyzer import analyze_gap
# from core.models import JobListing, GapAnalysis


# init_session_state()

# if st.session_state.selected_job is None:
#     st.warning("No job selected. Please go back to Job Feed and choose a job first.")
#     st.stop()

# profile = st.session_state.candidate_profile
# job = JobListing.model_validate(st.session_state.selected_job)
# similarity_score = st.session_state.selected_job_similarity or 0.0
# if st.button("Run Deep Analysis"):
#     analysis = analyze_gap(candidate=profile, job=job, similarity_score=similarity_score)


# st.header(f"{job.title} at {job.company}")
# st.divider()
# st.subheader(f"Overall Fit {analysis.overall_fit}")
# st.subheader(f"Similarity Score {analysis.similarity_score}")
# st.divider()
# col1, col2 = st.columns([3, 1])

# with col1:
#     st.subheader("Matching Skills:")
#     matching = analysis.matching_skills
#     for skill in matching:
#         st.write(f"✓ {skill}")

# with col2:
#     st.subheader("Missing Skills:")
#     missing = analysis.missing_skills
#     for skill in missing:
#         st.write(f"✗ {skill}")

# st.divider()

# st.subheader("CV Improvements")
# if analysis.cv_improvements:
#     for improvement in analysis.cv_improvements:
#         st.write(f"• {improvement}")

# st.subheader("Talking Points")
# if analysis.talking_points:
#     for point in analysis.talking_points:
#         st.write(f"• {point}")

# st.subheader("Recommendation")
# if analysis.recommendation:
#     st.write(analysis.recommendation)



from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.state import init_session_state
from matching.gap_analyzer import analyze_gap
from core.models import JobListing

init_session_state()

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .page-eyebrow {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 6px;
    }
    .job-heading {
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
        color: #111827;
    }
    .job-subheading {
        font-size: 1rem;
        color: #6b7280;
        margin: 0 0 1.5rem 0;
    }

    /* Fit score block */
    .fit-block {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 0.25rem;
    }
    .fit-score-num {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    .fit-score-label {
        font-size: 0.85rem;
        color: #6b7280;
    }
    .fit-high { color: #16a34a; }
    .fit-mid  { color: #d97706; }
    .fit-low  { color: #dc2626; }

    /* Skill pills */
    .skill-match {
        display: inline-block;
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 3px 9px;
        margin: 3px 4px 3px 0;
    }
    .skill-missing {
        display: inline-block;
        background: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 3px 9px;
        margin: 3px 4px 3px 0;
    }

    /* Section labels */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 8px;
    }

    /* Bullet items */
    .bullet-item {
        font-size: 0.9rem;
        color: #374151;
        padding: 6px 0;
        border-bottom: 1px solid #f3f4f6;
        line-height: 1.5;
    }
    .bullet-item:last-child { border-bottom: none; }

    /* Recommendation card */
    .rec-card {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-size: 0.9rem;
        color: #0c4a6e;
        line-height: 1.6;
    }

    /* Back link */
    .back-link {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Guard ─────────────────────────────────────────────────────────────────────
if st.session_state.selected_job is None:
    st.warning("No job selected. Go back to Job Feed and pick a job.")
    if st.button("← Back to Job Feed"):
        st.switch_page("pages/job_feed.py")
    st.stop()

profile = st.session_state.candidate_profile
job = JobListing.model_validate(st.session_state.selected_job)
similarity_score = st.session_state.selected_job_similarity or 0.0

# ── Header ────────────────────────────────────────────────────────────────────
if st.button("← Job feed"):
    st.switch_page("pages/job_feed.py")

st.markdown('<div class="page-eyebrow">Deep dive</div>', unsafe_allow_html=True)
st.markdown(f'<p class="job-heading">{job.title}</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="job-subheading">{job.company}'
    + (f" &nbsp;·&nbsp; {job.location}" if job.location else "")
    + "</p>",
    unsafe_allow_html=True,
)

# ── Run analysis ──────────────────────────────────────────────────────────────
if st.session_state.gap_analysis is None:
    if st.button("Run deep analysis", type="primary"):
        with st.spinner("Analysing gap…"):
            analysis = analyze_gap(
                candidate=profile, job=job, similarity_score=similarity_score
            )
            st.session_state.gap_analysis = analysis.model_dump()
        st.rerun()
    st.caption("Run the analysis to see your match breakdown, skill gaps, and talking points.")
    st.stop()

# ── Restore analysis from session state ───────────────────────────────────────
from core.models import GapAnalysis  # noqa: E402 — deferred to avoid unused import on stop
analysis = GapAnalysis.model_validate(st.session_state.gap_analysis)

st.divider()

# ── Scores ────────────────────────────────────────────────────────────────────
pct = int(round(similarity_score * 100))
fit_class = "fit-high" if pct >= 70 else ("fit-mid" if pct >= 45 else "fit-low")

score_col, fit_col, spacer = st.columns([1, 1, 3])

with score_col:
    st.markdown('<div class="section-label">Similarity score</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fit-block">'
        f'<span class="fit-score-num {fit_class}">{pct}%</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

with fit_col:
    st.markdown('<div class="section-label">Overall fit</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fit-block">'
        f'<span class="fit-score-num" style="font-size:1.8rem; color:#111827;">'
        f"{analysis.overall_fit}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Skills grid ───────────────────────────────────────────────────────────────
match_col, miss_col = st.columns(2)

with match_col:
    st.markdown('<div class="section-label">Matching skills</div>', unsafe_allow_html=True)
    if analysis.matching_skills:
        pills = "".join(
            f'<span class="skill-match">✓ {s}</span>' for s in analysis.matching_skills
        )
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.caption("No direct skill matches found.")

with miss_col:
    st.markdown('<div class="section-label">Skills to develop</div>', unsafe_allow_html=True)
    if analysis.missing_skills:
        pills = "".join(
            f'<span class="skill-missing">✗ {s}</span>' for s in analysis.missing_skills
        )
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.caption("No skill gaps identified.")

st.divider()

# ── CV improvements + talking points ─────────────────────────────────────────
imp_col, talk_col = st.columns(2)

with imp_col:
    st.markdown('<div class="section-label">CV improvements</div>', unsafe_allow_html=True)
    if analysis.cv_improvements:
        items = "".join(
            f'<div class="bullet-item">· {item}</div>' for item in analysis.cv_improvements
        )
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.caption("No improvements suggested.")

with talk_col:
    st.markdown('<div class="section-label">Interview talking points</div>', unsafe_allow_html=True)
    if analysis.talking_points:
        items = "".join(
            f'<div class="bullet-item">· {point}</div>' for point in analysis.talking_points
        )
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.caption("No talking points generated.")

st.divider()

# ── Recommendation ────────────────────────────────────────────────────────────
if analysis.recommendation:
    st.markdown('<div class="section-label">Recommendation</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="rec-card">{analysis.recommendation}</div>',
        unsafe_allow_html=True,
    )

# ── Re-run option ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Re-run analysis"):
    st.session_state.gap_analysis = None
    st.rerun()