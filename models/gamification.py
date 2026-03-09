"""
Gamification model — Points, badges, levels, leaderboard.
"""
from database.init_db import get_db


# ─── Points ─────────────────────────────────────────────
def award_points(user_id, points, reason=''):
    """Award points to a user."""
    conn = get_db()
    conn.execute(
        "INSERT INTO points (user_id, points, reason) VALUES (?,?,?)",
        (user_id, points, reason)
    )
    conn.commit()
    conn.close()


def get_total_points(user_id):
    """Get total points for a user."""
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(points), 0) as total FROM points WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row['total']


# ─── Levels ─────────────────────────────────────────────
LEVEL_THRESHOLDS = [
    (0, 'Beginner', '🌱'),
    (100, 'Learner', '📖'),
    (300, 'Intermediate', '⚡'),
    (600, 'Advanced', '🔥'),
    (1000, 'Expert', '🎓'),
    (1500, 'Master', '👑'),
    (2500, 'Legend', '🏆'),
]


def get_level(total_points):
    """Return (level_name, icon, next_threshold) based on total points."""
    current_level = LEVEL_THRESHOLDS[0]
    next_threshold = LEVEL_THRESHOLDS[1][0] if len(LEVEL_THRESHOLDS) > 1 else None
    for i, (threshold, name, icon) in enumerate(LEVEL_THRESHOLDS):
        if total_points >= threshold:
            current_level = (name, icon)
            next_threshold = LEVEL_THRESHOLDS[i + 1][0] if i + 1 < len(LEVEL_THRESHOLDS) else None
    return current_level[0], current_level[1], next_threshold


# ─── Badges ─────────────────────────────────────────────
def get_all_badges():
    """Return all badge definitions."""
    conn = get_db()
    badges = conn.execute("SELECT * FROM badges").fetchall()
    conn.close()
    return badges


def get_user_badges(user_id):
    """Return badges earned by a user."""
    conn = get_db()
    badges = conn.execute(
        """SELECT b.*, ub.earned_at FROM user_badges ub
           JOIN badges b ON ub.badge_id = b.id
           WHERE ub.user_id = ? ORDER BY ub.earned_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return badges


def award_badge(user_id, badge_criteria):
    """Award a badge by criteria string, if not already earned."""
    conn = get_db()
    badge = conn.execute("SELECT id FROM badges WHERE criteria = ?", (badge_criteria,)).fetchone()
    if badge:
        existing = conn.execute(
            "SELECT id FROM user_badges WHERE user_id = ? AND badge_id = ?",
            (user_id, badge['id'])
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO user_badges (user_id, badge_id) VALUES (?,?)",
                (user_id, badge['id'])
            )
            conn.commit()
    conn.close()


def check_and_award_badges(user_id):
    """Check all badge criteria and award any earned badges."""
    conn = get_db()

    # Count quizzes completed
    quiz_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM quiz_results WHERE user_id = ?", (user_id,)
    ).fetchone()['cnt']

    if quiz_count >= 1:
        award_badge(user_id, 'first_quiz')
    if quiz_count >= 3:
        award_badge(user_id, 'three_quizzes')
    if quiz_count >= 5:
        award_badge(user_id, 'five_quizzes')

    # Perfect score
    perfect = conn.execute(
        "SELECT COUNT(*) as cnt FROM quiz_results WHERE user_id = ? AND percentage = 100",
        (user_id,)
    ).fetchone()['cnt']
    if perfect > 0:
        award_badge(user_id, 'perfect_score')

    # Points-based badges
    total_pts = get_total_points(user_id)
    if total_pts >= 500:
        award_badge(user_id, 'points_500')
    if total_pts >= 1000:
        award_badge(user_id, 'points_1000')

    conn.close()


# ─── Leaderboard ────────────────────────────────────────
def get_leaderboard(limit=20):
    """Return top users by total points."""
    conn = get_db()
    leaders = conn.execute(
        """SELECT u.id, u.username,
                COALESCE(SUM(p.points), 0) as total_points,
                COUNT(DISTINCT qr.id) as quizzes_taken,
                COALESCE(AVG(qr.percentage), 0) as avg_score
           FROM users u
           LEFT JOIN points p ON u.id = p.user_id
           LEFT JOIN quiz_results qr ON u.id = qr.user_id
           WHERE u.role = 'student'
           GROUP BY u.id
           ORDER BY total_points DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return leaders


# ─── Activity Tracking ─────────────────────────────────
def log_activity(user_id, activity_type, details='', duration=0):
    """Log a user activity."""
    conn = get_db()
    conn.execute(
        "INSERT INTO user_activity (user_id, activity_type, details, duration_minutes) VALUES (?,?,?,?)",
        (user_id, activity_type, details, duration)
    )
    conn.commit()
    conn.close()


def get_user_activity_stats(user_id):
    """Get activity statistics for a user."""
    conn = get_db()
    stats = conn.execute(
        """SELECT
              COALESCE(SUM(duration_minutes), 0) as total_learning_time,
              COUNT(*) as total_activities,
              COUNT(DISTINCT DATE(created_at)) as active_days
           FROM user_activity WHERE user_id = ?""",
        (user_id,)
    ).fetchone()
    conn.close()
    return stats
