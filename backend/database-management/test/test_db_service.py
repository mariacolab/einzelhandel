from db_config import get_db_connection

def initialize_database():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash BYTEA NOT NULL,
                    salt BYTEA NOT NULL
                );
            """)
            conn.commit()
    finally:
        close_db_connection(conn)