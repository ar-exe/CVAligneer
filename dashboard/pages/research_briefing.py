# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# import streamlit as st
# from dashboard.state import init_session_state
# from core.models import JobListing
# from agent.graph import research_company


# init_session_state()

# job_url_prefill = st.session_state.selected_job_url or ""
# if not job_url_prefill and st.session_state.selected_job:
#     try:
#         selected_job = JobListing.model_validate(st.session_state.selected_job)
#         job_url_prefill = selected_job.url or ""
#     except Exception:
#         job_url_prefill = ""

# st.title("Research Briefing")
# company_name = st.text_input("Company name")
# job_url = st.text_input("Job URL", value=job_url_prefill)

# if st.button("Research Company"):
#     if not company_name.strip():
#         st.error("Please enter a company name.")
#     else:
#         with st.status("Researching company...", expanded=True) as status:
#             status.write("Searching the web...")
#             try:
#                 briefing = research_company(company_name.strip(), job_url.strip())
#                 status.write("Analysing findings...")
#                 status.update(label="Research complete!", state="complete")
#                 st.session_state.briefing = briefing.model_dump()
#             except Exception as exc:
#                 status.update(label="Research failed", state="error")
#                 st.error(f"Company research failed: {exc}")

# if st.session_state.briefing:
#     briefing = st.session_state.briefing
#     st.write(briefing.get("brief_summary", ""))
#     st.markdown("---")
#     cols = st.columns(4)
#     with cols[0]:
#         st.subheader("Tech Stack")
#         for tech in briefing.get("real_tech_stack", []):
#             st.write(f"• {tech}")
#     with cols[1]:
#         st.subheader("Culture Signals")
#         for signal in briefing.get("culture_signals", []):
#             st.write(f"• {signal}")
#     with cols[2]:
#         st.subheader("Talking Points")
#         for point in briefing.get("talking_points", []):
#             st.write(f"• {point}")
#     with cols[3]:
#         st.subheader("Red Flags")
#         red_flags = briefing.get("red_flags") or []
#         if red_flags:
#             for flag in red_flags:
#                 st.write(f"• {flag}")
#         else:
#             st.write("No red flags identified.")

#     st.markdown("---")
#     st.subheader("Notable Engineers")
#     notable = briefing.get("notable_engineers", [])
#     if notable:
#         for engineer in notable:
#             st.write(f"• {engineer}")
#     else:
#         st.write("No notable engineers found.")

#     st.subheader("Sources consulted")
#     sources = briefing.get("sources_consulted", [])
#     if sources:
#         for source in sources:
#             st.write(source)
#     else:
#         st.write("No sources available.")


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.state import init_session_state
from core.models import JobListing
from agent.graph import research_company

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
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 8px;
    }
    .brief-summary {
        font-size: 1rem;
        line-height: 1.7;
        color: #374151;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .info-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        height: 100%;
        margin-bottom: 1rem;
    }
    .bullet-item {
        font-size: 0.875rem;
        color: #374151;
        padding: 5px 0;
        border-bottom: 1px solid #f3f4f6;
        line-height: 1.5;
    }
    .bullet-item:last-child { border-bottom: none; }

    .red-flag-item {
        font-size: 0.875rem;
        color: #b91c1c;
        padding: 5px 0;
        border-bottom: 1px solid #fef2f2;
        line-height: 1.5;
    }
    .red-flag-item:last-child { border-bottom: none; }

    .source-link {
        font-size: 0.8rem;
        color: #6b7280;
        padding: 4px 0;
        display: block;
        text-decoration: none;
        word-break: break-all;
    }
    .source-link:hover { color: #111827; }

    .engineer-item {
        font-size: 0.875rem;
        color: #374151;
        padding: 5px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .engineer-item:last-child { border-bottom: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Pre-fill job URL from session ─────────────────────────────────────────────
job_url_prefill = st.session_state.selected_job_url or ""
if not job_url_prefill and st.session_state.selected_job:
    try:
        selected = JobListing.model_validate(st.session_state.selected_job)
        job_url_prefill = selected.url or ""
    except Exception:
        job_url_prefill = ""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-eyebrow">Research</div>', unsafe_allow_html=True)
st.markdown("## Company briefing")
st.caption("Get an AI-generated snapshot of a company — culture, tech stack, and red flags — before your interview.")

st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
form_col, _ = st.columns([2, 1])
with form_col:
    company_name = st.text_input("Company name", placeholder="Acme Corp")
    job_url = st.text_input("Job URL (optional — for role context)", value=job_url_prefill, placeholder="https://…")

    research_clicked = st.button("Research company", type="primary")

if research_clicked:
    if not company_name.strip():
        st.error("Enter a company name to research.")
    else:
        with st.status("Researching…", expanded=True) as status:
            status.write("Searching the web…")
            try:
                briefing = research_company(company_name.strip(), job_url.strip())
                status.write("Analysing findings…")
                status.update(label="Done", state="complete", expanded=False)
                st.session_state.briefing = briefing.model_dump()
            except Exception as exc:
                status.update(label="Research failed", state="error", expanded=False)
                st.error(f"Research failed: {exc}")

# ── Briefing output ───────────────────────────────────────────────────────────
if not st.session_state.briefing:
    st.stop()

briefing = st.session_state.briefing
company_display = company_name.strip() if company_name.strip() else "Company"

st.divider()
st.markdown(f"### {company_display}")

# Summary
summary = briefing.get("brief_summary", "")
if summary:
    st.markdown(f'<div class="brief-summary">{summary}</div>', unsafe_allow_html=True)

# ── Four-column info grid ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="section-label">Tech stack</div>', unsafe_allow_html=True)
    items = briefing.get("real_tech_stack", [])
    if items:
        rows = "".join(f'<div class="bullet-item">· {t}</div>' for t in items)
        st.markdown(f'<div class="info-card">{rows}</div>', unsafe_allow_html=True)
    else:
        st.caption("Not found.")

with c2:
    st.markdown('<div class="section-label">Culture signals</div>', unsafe_allow_html=True)
    items = briefing.get("culture_signals", [])
    if items:
        rows = "".join(f'<div class="bullet-item">· {s}</div>' for s in items)
        st.markdown(f'<div class="info-card">{rows}</div>', unsafe_allow_html=True)
    else:
        st.caption("Not found.")

with c3:
    st.markdown('<div class="section-label">Talking points</div>', unsafe_allow_html=True)
    items = briefing.get("talking_points", [])
    if items:
        rows = "".join(f'<div class="bullet-item">· {p}</div>' for p in items)
        st.markdown(f'<div class="info-card">{rows}</div>', unsafe_allow_html=True)
    else:
        st.caption("None generated.")

with c4:
    st.markdown('<div class="section-label">Red flags</div>', unsafe_allow_html=True)
    items = briefing.get("red_flags") or []
    if items:
        rows = "".join(f'<div class="red-flag-item">⚠ {f}</div>' for f in items)
        st.markdown(f'<div class="info-card">{rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-card"><div class="bullet-item" style="color:#6b7280;">None identified.</div></div>',
            unsafe_allow_html=True,
        )

st.divider()

# ── Notable engineers + sources ───────────────────────────────────────────────
eng_col, src_col = st.columns([1, 1])

with eng_col:
    st.markdown('<div class="section-label">Notable engineers</div>', unsafe_allow_html=True)
    engineers = briefing.get("notable_engineers", [])
    if engineers:
        rows = "".join(f'<div class="engineer-item">· {e}</div>' for e in engineers)
        st.markdown(rows, unsafe_allow_html=True)
    else:
        st.caption("None found.")

with src_col:
    st.markdown('<div class="section-label">Sources consulted</div>', unsafe_allow_html=True)
    sources = briefing.get("sources_consulted", [])
    if sources:
        for source in sources:
            # Render as a clickable link if it looks like a URL
            if source.startswith("http"):
                st.markdown(
                    f'<a class="source-link" href="{source}" target="_blank">↗ {source}</a>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="source-link">{source}</div>', unsafe_allow_html=True)
    else:
        st.caption("No sources recorded.")

# ── Re-run ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Re-run research"):
    st.session_state.briefing = None
    st.rerun()