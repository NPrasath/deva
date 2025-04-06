import sqlite3
from datetime import datetime

DATABASE_FILE = "database.db"

def _get_connection():
    """Helper function to get a SQLite connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Create the tasks table if it doesn't already exist."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            agent_role TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def add_task(description, agent_role):
    """Insert a new task with 'PENDING' status."""
    now = datetime.utcnow().isoformat()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (description, agent_role, status, result, created_at, updated_at)
        VALUES (?, ?, 'PENDING', '', ?, ?)
        """,
        (description, agent_role, now, now),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_next_task(agent_role):
    """
    Fetch the oldest task with 'PENDING' status for the given agent_role.
    Returns a dictionary with task details or None if no tasks are found.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE agent_role = ? AND status = 'PENDING'
        ORDER BY created_at ASC
        LIMIT 1
        """,
        (agent_role,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_task_status(task_id, status, result):
    """Update the status and result of a task."""
    now = datetime.utcnow().isoformat()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks
        SET status = ?, result = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, result, now, task_id),
    )
    conn.commit()
    conn.close()

def get_task_details(task_id):
    """Retrieve all details for a specific task by ID."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_completed_task_results():
    """
    Return a list of dictionaries with details of all tasks
    whose status is 'COMPLETED'.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status = 'COMPLETED'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]