"""
Course & Lesson module — browse courses, view lessons.
"""
from flask import Blueprint, render_template, redirect, url_for, session
from models.course import get_all_courses, get_course_by_id, get_lessons_by_course, get_lesson_by_id
from models.quiz import get_quizzes_by_course
from models.gamification import log_activity

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses')
def course_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    courses = get_all_courses()
    return render_template('courses.html', courses=courses)


@courses_bp.route('/courses/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    course = get_course_by_id(course_id)
    if not course:
        return "Course not found", 404

    lessons = get_lessons_by_course(course_id)
    quizzes = get_quizzes_by_course(course_id)
    return render_template('course_detail.html', course=course, lessons=lessons, quizzes=quizzes)


@courses_bp.route('/courses/<int:course_id>/lesson/<int:lesson_id>')
def view_lesson(course_id, lesson_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    course = get_course_by_id(course_id)
    lesson = get_lesson_by_id(lesson_id)
    if not lesson or not course:
        return "Lesson not found", 404

    lessons = get_lessons_by_course(course_id)
    log_activity(session['user_id'], 'lesson_view', f'Viewed lesson: {lesson["title"]}', 5)
    return render_template('lesson.html', course=course, lesson=lesson, lessons=lessons)
