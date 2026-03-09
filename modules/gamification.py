"""
Gamification module — leaderboard route.
"""
from flask import Blueprint, render_template, redirect, url_for, session
from models.gamification import get_leaderboard, get_total_points, get_level

gamification_bp = Blueprint('gamification', __name__)


@gamification_bp.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') == 'teacher':
        return redirect(url_for('analytics.teacher_dashboard'))

    leaders = get_leaderboard(20)

    # Add level info to each leader
    leaderboard_data = []
    for i, leader in enumerate(leaders):
        level_name, level_icon, _ = get_level(leader['total_points'])
        leaderboard_data.append({
            'rank': i + 1,
            'username': leader['username'],
            'total_points': leader['total_points'],
            'quizzes_taken': leader['quizzes_taken'],
            'avg_score': round(leader['avg_score'], 1),
            'level_name': level_name,
            'level_icon': level_icon,
            'is_current_user': leader['id'] == session['user_id']
        })

    return render_template('leaderboard.html', leaderboard=leaderboard_data)
