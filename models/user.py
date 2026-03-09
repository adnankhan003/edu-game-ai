"""
User model — CRUD operations for user management.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from database.init_db import get_db


def create_user(username, email, password, role='student'):
    """Register a new user. Returns user id or None if duplicate."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), role)
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return user_id
    except Exception:
        conn.close()
        return None


def authenticate_user(email, password):
    """Authenticate user by email + password. Returns user row or None."""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


def get_user_by_id(user_id):
    """Fetch a single user by ID."""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def get_all_students():
    """Return all users with role='student'."""
    conn = get_db()
    students = conn.execute("SELECT * FROM users WHERE role = 'student' ORDER BY username").fetchall()
    conn.close()
    return students
