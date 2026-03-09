"""
Authentication module — register, login, logout, profile routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import create_user, authenticate_user, get_user_by_id
from models.gamification import (
    get_total_points, get_level, get_user_badges, log_activity, get_user_activity_stats
)
from models.quiz import get_results_by_user, get_user_quiz_stats

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        user_id = create_user(username, email, password, role)
        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists.', 'error')
            return render_template('register.html')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            log_activity(user['id'], 'login', 'User logged in')
            flash(f'Welcome back, {user["username"]}!', 'success')
            if user['role'] == 'teacher':
                return redirect(url_for('analytics.teacher_dashboard'))
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') == 'teacher':
        return redirect(url_for('analytics.teacher_dashboard'))

    user_id = session['user_id']
    user = get_user_by_id(user_id)
    total_points = get_total_points(user_id)
    level_name, level_icon, next_threshold = get_level(total_points)
    badges = get_user_badges(user_id)
    recent_results = get_results_by_user(user_id)[:5]
    quiz_stats = get_user_quiz_stats(user_id)
    activity_stats = get_user_activity_stats(user_id)

    return render_template('dashboard.html',
                           user=user,
                           total_points=total_points,
                           level_name=level_name,
                           level_icon=level_icon,
                           next_threshold=next_threshold,
                           badges=badges,
                           recent_results=recent_results,
                           quiz_stats=quiz_stats,
                           activity_stats=activity_stats)


@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') == 'teacher':
        return redirect(url_for('analytics.teacher_dashboard'))

    user_id = session['user_id']
    user = get_user_by_id(user_id)
    total_points = get_total_points(user_id)
    level_name, level_icon, next_threshold = get_level(total_points)
    badges = get_user_badges(user_id)
    all_results = get_results_by_user(user_id)
    quiz_stats = get_user_quiz_stats(user_id)
    activity_stats = get_user_activity_stats(user_id)

    return render_template('profile.html',
                           user=user,
                           total_points=total_points,
                           level_name=level_name,
                           level_icon=level_icon,
                           next_threshold=next_threshold,
                           badges=badges,
                           all_results=all_results,
                           quiz_stats=quiz_stats,
                           activity_stats=activity_stats)
