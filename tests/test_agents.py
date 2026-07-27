from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.graph import research_company

briefing = research_company(
    company_name="Anthropic",
    job_url="https://www.linkedin.com/jobs/search-results/?currentJobId=4444648694&trk=d_flagship3_company_posts&refId=%2B9KaYSLI5nSLPC57kjUyPw%3D%3D&trackingId=vaFXB9czCPmbcd%2BfyfmWmg%3D%3D&keywords=jobs&origin=COMPANY_PAGE_JOBS_CLUSTER_EXPANSION&originToLandingJobPostings=4444648694%2C4444657186%2C4444642242%2C4444653180%2C4444658215%2C4444645196%2C4444645197%2C4444664198%2C4444655155%2C4444652204&geoId=103644278&f_C=74126343"
)
print(briefing)
print(briefing.brief_summary)
print(briefing.real_tech_stack)
print(briefing.talking_points)