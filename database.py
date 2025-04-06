import sqlite3
from contextlib import closing

def get_connection(db_name="tasks.db"):
    """Create and return a new database connection."""
    return sqlite3.connect(db_name)

def init_db():
    """Initialize the database schema for managing tasks."""
    with get_connection() as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT CHECK(status IN ('pending','processing','completed','failed')) NOT NULL,
                    result TEXT,
                    agent_role TEXT NOT NULL DEFAULT 'backend',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()