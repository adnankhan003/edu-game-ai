"""
Quiz model — CRUD for quizzes, questions, and results.
"""
from database.init_db import get_db


def get_quizzes_by_course(course_id):
    """Return all quizzes for a course."""
    conn = get_db()
    quizzes = conn.execute("SELECT * FROM quizzes WHERE course_id = ?", (course_id,)).fetchall()
    conn.close()
    return quizzes


def get_quiz_by_id(quiz_id):
    """Return a single quiz."""
    conn = get_db()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    conn.close()
    return quiz


def get_questions_by_quiz(quiz_id):
    """Return all questions for a quiz."""
    conn = get_db()
    questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    conn.close()
    return questions


def save_quiz_result(user_id, quiz_id, score, total):
    """Save a quiz result and return the id."""
    percentage = round((score / total) * 100, 2) if total > 0 else 0
    conn = get_db()
    conn.execute(
        "INSERT INTO quiz_results (user_id, quiz_id, score, total, percentage) VALUES (?,?,?,?,?)",
        (user_id, quiz_id, score, total, percentage)
    )
    conn.commit()
    conn.close()
    return percentage


def get_results_by_user(user_id):
    """Return all quiz results for a user."""
    conn = get_db()
    results = conn.execute(
        """SELECT qr.*, q.title as quiz_title, c.title as course_title
           FROM quiz_results qr
           JOIN quizzes q ON qr.quiz_id = q.id
           JOIN courses c ON q.course_id = c.id
           WHERE qr.user_id = ?
           ORDER BY qr.completed_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return results


def get_all_results():
    """Return all quiz results (for teacher dashboard)."""
    conn = get_db()
    results = conn.execute(
        """SELECT qr.*, q.title as quiz_title, c.title as course_title, u.username
           FROM quiz_results qr
           JOIN quizzes q ON qr.quiz_id = q.id
           JOIN courses c ON q.course_id = c.id
           JOIN users u ON qr.user_id = u.id
           ORDER BY qr.completed_at DESC"""
    ).fetchall()
    conn.close()
    return results


def get_user_quiz_stats(user_id):
    """Return aggregate quiz stats for a user."""
    conn = get_db()
    stats = conn.execute(
        """SELECT COUNT(*) as total_quizzes,
                  COALESCE(AVG(percentage), 0) as avg_score,
                  COALESCE(MAX(percentage), 0) as best_score,
                  COALESCE(MIN(percentage), 0) as worst_score
           FROM quiz_results WHERE user_id = ?""",
        (user_id,)
    ).fetchone()
    conn.close()
    return stats


def get_all_quizzes():
    """Return all quizzes with course info."""
    conn = get_db()
    quizzes = conn.execute(
        """SELECT q.*, c.title as course_title
           FROM quizzes q JOIN courses c ON q.course_id = c.id
           ORDER BY q.id"""
    ).fetchall()
    conn.close()
    return quizzes
