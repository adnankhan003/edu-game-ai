"""
Course & Lesson model — CRUD operations.
"""
from database.init_db import get_db


def get_all_courses():
    """Return all courses."""
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses ORDER BY id").fetchall()
    conn.close()
    return courses


def get_course_by_id(course_id):
    """Return a single course."""
    conn = get_db()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()
    return course


def get_lessons_by_course(course_id):
    """Return all lessons for a course, ordered."""
    conn = get_db()
    lessons = conn.execute(
        "SELECT * FROM lessons WHERE course_id = ? ORDER BY order_num", (course_id,)
    ).fetchall()
    conn.close()
    return lessons


def get_lesson_by_id(lesson_id):
    """Return a single lesson."""
    conn = get_db()
    lesson = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    conn.close()
    return lesson
