"""
Analytics module — Teacher dashboard with student performance,
engagement statistics, and predicted success.
"""
from flask import Blueprint, render_template, redirect, url_for, session
from models.user import get_all_students
from models.quiz import get_all_results, get_user_quiz_stats
from models.gamification import get_total_points, get_level, get_user_activity_stats
from modules.ml_engine import predict_success, get_user_ml_features

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role') != 'teacher':
        return "Access denied. Teacher role required.", 403

    students = get_all_students()
    all_results = get_all_results()

    # Build per-student analytics
    student_analytics = []
    for student in students:
        sid = student['id']
        quiz_stats = get_user_quiz_stats(sid)
        total_points = get_total_points(sid)
        level_name, level_icon, _ = get_level(total_points)
        activity_stats = get_user_activity_stats(sid)

        # ML prediction
        try:
            score_avg, learn_time, act_level = get_user_ml_features(sid)
            success_pred, success_probs = predict_success(score_avg, learn_time, act_level)
            success_prob = round(success_probs[1] * 100, 1) if len(success_probs) > 1 else 50.0
        except Exception:
            success_prob = 50.0

        student_analytics.append({
            'id': sid,
            'username': student['username'],
            'email': student['email'],
            'total_quizzes': quiz_stats['total_quizzes'],
            'avg_score': round(quiz_stats['avg_score'], 1),
            'best_score': round(quiz_stats['best_score'], 1),
            'total_points': total_points,
            'level_name': level_name,
            'level_icon': level_icon,
            'learning_time': round(activity_stats['total_learning_time'], 1),
            'active_days': activity_stats['active_days'],
            'success_probability': success_prob,
        })

    # Engagement summary
    total_students = len(students)
    active_students = sum(1 for s in student_analytics if s['total_quizzes'] > 0)
    avg_platform_score = (
        round(sum(s['avg_score'] for s in student_analytics) / total_students, 1)
        if total_students > 0 else 0
    )
    at_risk = sum(1 for s in student_analytics if s['success_probability'] < 50)

    summary = {
        'total_students': total_students,
        'active_students': active_students,
        'avg_score': avg_platform_score,
        'at_risk_count': at_risk,
        'total_quiz_attempts': len(all_results),
    }

    return render_template('teacher_dashboard.html',
                           students=student_analytics,
                           summary=summary,
                           recent_results=all_results[:20])
