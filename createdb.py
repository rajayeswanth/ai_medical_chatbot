import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    cursor = conn.cursor()

    # Drop tables in order of constraints
    cursor.execute("DROP TABLE IF EXISTS user_entities CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS user_summaries CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS user_memories CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL
    );
    """)

    # ✅ User Memories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_memories (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        session_id VARCHAR(100) NOT NULL,
        last_seen TIMESTAMP NOT NULL,
        conversation_count INT NOT NULL,
        last_conversation TEXT,
        entity_store JSONB,
        UNIQUE(user_id, session_id)
    );
    """)

    # User Summaries Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_summaries (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) REFERENCES users(user_id) ON DELETE CASCADE,
        created_at TIMESTAMP NOT NULL,
        summary TEXT NOT NULL
    );
    """)

    # User Entities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_entities (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) REFERENCES users(user_id) ON DELETE CASCADE,
        entity_name VARCHAR(100) NOT NULL,
        entity_data JSONB NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        UNIQUE(user_id, entity_name)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
