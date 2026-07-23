import sys
import os

project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.connection import get_connection, put_connection
from psycopg2.extras import RealDictCursor
import json

from core.models import JobListing, CandidateProfile
from core.config import settings

import pandas as pd
from supabase import create_client


def get_supabase_client():
    return create_client(settings.supabase_url, settings.supabase_key)

def save_candidate_profile(profile: CandidateProfile, embedding: list[float], github_analysis: dict = {}) -> str:
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO candidate_profiles 
                (full_name, profile_json, github_analysis, embedding)
                values (%s, %s, %s, %s)
                ON CONFLICT (full_name) DO NOTHING
                RETURNING id;
            """, (profile.full_name, json.dumps(profile.model_dump()), json.dumps(github_analysis), embedding))
            result = cur.fetchone()
            if result:
                profile_id = result['id']
            else:
                # URL already exists
                cur.execute("""
                    SELECT id
                    FROM candidate_profiles
                    WHERE full_name = %s;
                """, (profile.full_name,))
                profile_id = cur.fetchone()['id']
        conn.commit()
        return profile_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def save_job_listing(job: JobListing, embedding: list[float]) -> str:
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO job_listings
                    (url, source, title, company, location, job_json, embedding)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                RETURNING id;
            """, (
                job.url,
                job.source,
                job.title,
                job.company,
                job.location,
                json.dumps(job.model_dump()),
                embedding
            ))

            result = cur.fetchone()

            if result:
                job_id = result["id"]
            else:
                # URL already exists
                cur.execute("""
                    SELECT id
                    FROM job_listings
                    WHERE url = %s;
                """, (job.url,))

                job_id = cur.fetchone()["id"]

        conn.commit()
        return job_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def load_all_job_listings() -> list[JobListing]:
    conn = get_connection()
    try:
        df = pd.read_sql("""
                        SELECT * FROM job_listings
                        """, conn)
        put_connection(conn)
        payload = df.iloc[:]['job_json']
        jobs = [JobListing.model_validate_json(json.dumps(job_json_str)) for job_json_str in payload]
        # print(jobs)
        return jobs
    except Exception:
            conn.rollback()
            raise
    
    finally:
        conn.close()

# def load_all_job_listings() -> list[JobListing]:
#     conn = get_connection()
#     try:
#         with conn.cursor(cursor_factory=RealDictCursor) as cur:
#             cur.execute("SELECT job_json FROM job_listings ORDER BY saved_at DESC;")
#             rows = cur.fetchall()
#         return [JobListing.model_validate(row["job_json"]) for row in rows]
#     finally:
#         put_connection(conn)