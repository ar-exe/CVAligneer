import sys
import os

project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.database import get_connection, put_connection
from core.models import JobListing, CandidateProfile
from psycopg2.extras import RealDictCursor
import ast


def get_candidate_emb(candidate: CandidateProfile) -> list[float]:
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT embedding FROM candidate_profiles WHERE full_name = %s LIMIT 1;
                    """, (candidate.full_name,))
        row = cur.fetchone()['embedding']
        row = ast.literal_eval(row)
        d = [float(value) for value in row]
        # print(type(d))
        # print(d)
    put_connection(conn)
    return d

def rank_jobs_for_candidate(candidate: CandidateProfile, top_k: int = 10) -> list[dict]:
    conn = get_connection()
    candidate_emb = get_candidate_emb(candidate)
    results = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
                SELECT id, title, company, job_json, 
                1 - (embedding <=> %s::vector) AS similarity_score
                FROM job_listings
                ORDER BY similarity_score DESC
                LIMIT %s
        """, (candidate_emb, top_k))
        rows = cur.fetchall()
        # print(rows)
        for row in rows:
            result = {}
            result['job_id'] = row['id']
            result['title'] = row['title']
            result['company'] = row['company']
            result['similarity_score'] = row['similarity_score']
            result['job'] = JobListing.model_validate(row['job_json'])
            results.append(result)
        # print(results)
    conn.commit()
    put_connection(conn)
    return results