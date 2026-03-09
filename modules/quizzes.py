"""
Quiz module — take quizzes, submit answers, view results.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.quiz import get_quiz_by_id, get_questions_by_quiz, save_quiz_result
from models.course import get_course_by_id
from models.gamification import award_points, check_and_award_badges, log_activity

quizzes_bp = Blueprint('quizzes', __name__)


@quizzes_bp.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    questions = get_questions_by_quiz(quiz_id)
    course = get_course_by_id(quiz['course_id'])
    return render_template('quiz.html', quiz=quiz, questions=questions, course=course)


@quizzes_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    questions = get_questions_by_quiz(quiz_id)
    score = 0
    total = len(questions)
    answers = {}

    for q in questions:
        user_answer = request.form.get(f'q_{q["id"]}', '')
        correct = q['correct_option']
        is_correct = user_answer.upper() == correct.upper()
        if is_correct:
            score += 1
        answers[q['id']] = {
            'user_answer': user_answer,
            'correct_answer': correct,
            'is_correct': is_correct
        }

    percentage = save_quiz_result(user_id, quiz_id, score, total)

    # Award points based on performance
    points_earned = int(percentage / 10) * 5  # 0-50 points
    if percentage == 100:
        points_earned += 20  # bonus for perfect score
    award_points(user_id, points_earned, f'Quiz: {quiz["title"]} ({percentage}%)')

    # Log activity
    log_activity(user_id, 'quiz_attempt', f'Completed quiz: {quiz["title"]}', 10)

    # Check badges
    check_and_award_badges(user_id)

    course = get_course_by_id(quiz['course_id'])
    return render_template('quiz_result.html',
                           quiz=quiz,
                           course=course,
                           questions=questions,
                           answers=answers,
                           score=score,
                           total=total,
                           percentage=percentage,
                           points_earned=points_earned)
