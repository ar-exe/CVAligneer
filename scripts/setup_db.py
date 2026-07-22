import sys
import os

project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.connection import get_connection, put_connection
from psycopg2.extras import RealDictCursor


def create_candidate_profiles_table():
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            create table if not exists candidate_profiles (
                id uuid primary key default gen_random_uuid(),
                full_name text not null,
                profile_json jsonb not null,
                github_analysis jsonb,
                embedding vector(768),
                created_at timestamptz default now(),
                updated_at timestamptz default now()
                    );
                    """)
    conn.commit()
    put_connection(conn)

def create_job_listings_table():
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            create table if not exists job_listings (
                id uuid primary key default gen_random_uuid(),
                url text unique not null,
                source text,
                title text,
                company text,
                location text,
                job_json jsonb not null,
                embedding vector(768),
                saved_at timestamptz default now()
            );
                    """)
    conn.commit()
    put_connection(conn)

if __name__ == "__main__":
    conn = get_connection()
    conn.rollback()
    put_connection(conn)
    create_candidate_profiles_table()
    create_job_listings_table()