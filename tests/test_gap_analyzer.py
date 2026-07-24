from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.cv_parser import parse_cv
from matching.gap_analyzer import analyze_top_matches

profile = parse_cv("/Users/abdelrahman-mohammed/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Abdelrahman_Mohammed_CV (8).pdf")
analyses = analyze_top_matches(profile, top_k=3)

for analysis in analyses:
    print(f"\n{'='*50}")
    print(f"{analysis.job_title} at {analysis.company}")
    print(f"Fit: {analysis.overall_fit} (score: {analysis.similarity_score})")
    print(f"Missing: {analysis.missing_skills}")
    print(f"Recommendation: {analysis.recommendation}")