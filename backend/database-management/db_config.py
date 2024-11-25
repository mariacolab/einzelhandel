import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def close_db_connection(conn):
    if conn:
        conn.close()
