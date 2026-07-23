
# import psycopg2
# from config import settings

# def get_connection():
#     return psycopg2.connect(settings.database_url)
import sys
import os

project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from psycopg2.pool import ThreadedConnectionPool
from core.config import settings
_pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.supabase_url,
    options="-c statement_timeout=60s"
)


def get_connection():
    return _pool.getconn()

def put_connection(conn):
    _pool.putconn(conn)