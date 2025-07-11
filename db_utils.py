import psycopg2
from psycopg2.extras import RealDictCursor 
from psycopg2 import Error
import json

# ---------------- Connection ---------------- #
def get_db_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_ouH1C8PILpJk@ep-weathered-dust-a8kx2smo-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require",
        #row_factory=
        cursor_factory=RealDictCursor

    )

# ---------------- Table Creation ---------------- #
def create_application_logs():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS application_logs1 (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    gpt_response TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Try to add the column if it doesn't exist
            cur.execute('''
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='application_logs1' AND column_name='metadata'
                    ) THEN
                        ALTER TABLE application_logs1 ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
                    END IF;
                END
                $$;
            ''')
        conn.commit()
    finally:
        conn.close()

def create_conversation_titles():  
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS conversation_titles (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
    finally:
        conn.close()


def insert_application_logs(session_id, user_query, gpt_response, model, metadata=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO application_logs1 (session_id, user_query, gpt_response, model, metadata)
                VALUES (%s, %s, %s, %s, %s)
            ''', (session_id, user_query, gpt_response, model, json.dumps(metadata or {}))
            )
        conn.commit()
    finally:
        conn.close()

def save_conversation_title(session_id: str, title: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO conversation_titles (session_id, title, created_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (session_id) DO UPDATE 
                    SET title = EXCLUDED.title;
                """, (session_id, title))
                conn.commit()
                print(f"[DB] Saved title for session: {session_id} | Title: {title}")
    except Exception as e:
        print(f"[DB] Failed to save title for {session_id} | Error: {e}")


def get_chat_history(session_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT user_query, gpt_response
                FROM application_logs1
                WHERE session_id = %s
                ORDER BY created_at
            ''', (session_id,))
            rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append({"role": "user", "content": row["user_query"]})
            messages.append({"role": "assistant", "content": row["gpt_response"]})
        return messages
    finally:
        conn.close()

def get_all_sessions():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT      
                    l.session_id, 
                    COALESCE(t.title, 'Untitled Chat') AS title,
                    MAX(l.created_at) AS last_activity
                FROM application_logs1 l
                LEFT JOIN conversation_titles t ON l.session_id = t.session_id
                GROUP BY l.session_id, t.title
                ORDER BY last_activity DESC;
            ''')
            rows = cur.fetchall()
        return rows  # List of dicts with session_id, title, last_activity
    finally:
        conn.close()


def get_conversation_title(session_id: str) -> str:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT title FROM conversation_titles WHERE session_id = %s", (session_id,))
            result = cur.fetchone()
            return result['title'] if result else None
    finally:
        conn.close()


# ---------------- Startup Init ---------------- #
try:
    create_application_logs()
    create_conversation_titles()  # Initialize title table at startup
except Exception as e:
    print(f"[Startup Error] Failed to create tables: {e}")