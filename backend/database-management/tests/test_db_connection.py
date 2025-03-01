import os
import psycopg2
import pytest

def get_db_connection():
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB', 'microservices_db_test')
    db_host = 'postgres-test'
    db_port = 5432
    return psycopg2.connect(
        user=db_user,
        password=db_password,
        database=db_name,
        host=db_host,
        port=db_port
    )

def test_connection():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1;')
    result = cursor.fetchone()
    assert result[0] == 1, "Datenbankverbindung funktioniert nicht korrekt."
    cursor.close()
    conn.close()
