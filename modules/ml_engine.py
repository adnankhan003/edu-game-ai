"""
Machine Learning Personalization Module.
Uses RandomForestClassifier models trained on UCI Student Performance data
to recommend quiz difficulty and predict student success.

Dataset: UCI Student Performance Dataset (Cortez & Silva, 2008)
         Preprocessed into 6 features via database/prepare_dataset.py
"""
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from flask import Blueprint, render_template, redirect, url_for, session

from models.quiz import get_user_quiz_stats, get_results_by_user, get_all_quizzes
from models.gamification import get_user_activity_stats, get_total_points
from models.course import get_all_courses

ml_bp = Blueprint('ml', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Primary: UCI-based preprocessed data  |  Fallback: original sample data
PRIMARY_DATA_PATH = os.path.join(BASE_DIR, 'database', 'ml_training_data.csv')
FALLBACK_DATA_PATH = os.path.join(BASE_DIR, 'database', 'sample_ml_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'database')
DIFFICULTY_MODEL_PATH = os.path.join(MODEL_DIR, 'difficulty_model.pkl')
SUCCESS_MODEL_PATH = os.path.join(MODEL_DIR, 'success_model.pkl')
FEATURE_META_PATH = os.path.join(MODEL_DIR, 'feature_meta.pkl')

# The 6 features used when UCI data is available
UCI_FEATURES = [
    'quiz_score_avg', 'learning_time_hrs', 'activity_level',
    'study_failures', 'parental_education', 'internet_access',
]

# The 3 original features (fallback mode)
LEGACY_FEATURES = ['quiz_score_avg', 'learning_time_hrs', 'activity_level']

# Will be set after training to indicate which feature set is in use
_active_features = None
_feature_defaults = None


def _get_data_path():
    """Return the best available training data path."""
    if os.path.exists(PRIMARY_DATA_PATH):
        return PRIMARY_DATA_PATH, True  # (path, is_uci)
    return FALLBACK_DATA_PATH, False


def train_models():
    """Train and save both ML models using the best available dataset."""
    global _active_features, _feature_defaults

    data_path, is_uci = _get_data_path()
    df = pd.read_csv(data_path)

    if is_uci:
        feature_cols = UCI_FEATURES
        source_name = "UCI Student Performance (preprocessed)"
    else:
        feature_cols = LEGACY_FEATURES
        source_name = "sample_ml_data.csv (legacy)"

    # Validate columns exist
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  [WARN] Missing columns {missing} in {data_path}, falling back to legacy features")
        feature_cols = [c for c in LEGACY_FEATURES if c in df.columns]
        is_uci = False

    features = df[feature_cols]
    _active_features = feature_cols

    # Compute default values (medians) for each feature -- used at prediction time
    _feature_defaults = {col: float(features[col].median()) for col in feature_cols}

    print(f"\n  ML Training")
    print(f"  -----------")
    print(f"  Source:     {source_name}")
    print(f"  Records:    {len(df)}")
    print(f"  Features:   {feature_cols}")

    # --- Difficulty Preference Model ---
    y_diff = df['difficulty_preference']
    X_train, X_test, y_train, y_test = train_test_split(
        features, y_diff, test_size=0.2, random_state=42
    )

    diff_model = RandomForestClassifier(n_estimators=100, random_state=42)
    diff_model.fit(X_train, y_train)
    diff_acc = accuracy_score(y_test, diff_model.predict(X_test))
    print(f"  Difficulty Model Accuracy: {diff_acc:.2%}")

    with open(DIFFICULTY_MODEL_PATH, 'wb') as f:
        pickle.dump(diff_model, f)

    # --- Success Prediction Model ---
    y_success = df['success']
    X_train, X_test, y_train, y_test = train_test_split(
        features, y_success, test_size=0.2, random_state=42
    )

    success_model = RandomForestClassifier(n_estimators=100, random_state=42)
    success_model.fit(X_train, y_train)
    success_acc = accuracy_score(y_test, success_model.predict(X_test))
    print(f"  Success Model Accuracy:    {success_acc:.2%}")

    with open(SUCCESS_MODEL_PATH, 'wb') as f:
        pickle.dump(success_model, f)

    # Save feature metadata so models know what to expect at prediction time
    meta = {
        'features': feature_cols,
        'defaults': _feature_defaults,
        'is_uci': is_uci,
    }
    with open(FEATURE_META_PATH, 'wb') as f:
        pickle.dump(meta, f)

    print(f"  Models saved to: {MODEL_DIR}\n")
    return diff_acc, success_acc


def _load_feature_meta():
    """Load feature metadata (which features the models expect)."""
    global _active_features, _feature_defaults
    if _active_features is not None:
        return
    if os.path.exists(FEATURE_META_PATH):
        with open(FEATURE_META_PATH, 'rb') as f:
            meta = pickle.load(f)
        _active_features = meta['features']
        _feature_defaults = meta['defaults']
    else:
        _active_features = LEGACY_FEATURES
        _feature_defaults = {
            'quiz_score_avg': 50, 'learning_time_hrs': 5, 'activity_level': 5,
        }


def load_model(path):
    """Load a pickled model."""
    if not os.path.exists(path):
        train_models()
    with open(path, 'rb') as f:
        return pickle.load(f)


def _build_feature_array(quiz_score_avg, learning_time_hrs, activity_level,
                         study_failures=None, parental_education=None,
                         internet_access=None):
    """
    Build a numpy feature array matching what the trained models expect.
    Extra features default to training-set medians when not provided.
    """
    _load_feature_meta()

    values = {
        'quiz_score_avg': quiz_score_avg,
        'learning_time_hrs': learning_time_hrs,
        'activity_level': activity_level,
    }
    if study_failures is not None:
        values['study_failures'] = study_failures
    if parental_education is not None:
        values['parental_education'] = parental_education
    if internet_access is not None:
        values['internet_access'] = internet_access

    row = []
    for col in _active_features:
        row.append(values.get(col, _feature_defaults.get(col, 0)))

    return np.array([row])


def predict_difficulty(quiz_score_avg, learning_time_hrs, activity_level,
                       study_failures=None, parental_education=None,
                       internet_access=None):
    """
    Predict recommended difficulty adjustment.
    Returns: (prediction, probabilities)
        prediction: 0 = easier, 1 = same level, 2 = harder
    """
    model = load_model(DIFFICULTY_MODEL_PATH)
    features = _build_feature_array(
        quiz_score_avg, learning_time_hrs, activity_level,
        study_failures, parental_education, internet_access,
    )
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    return int(prediction), probabilities.tolist()


def predict_success(quiz_score_avg, learning_time_hrs, activity_level,
                    study_failures=None, parental_education=None,
                    internet_access=None):
    """
    Predict probability of student success.
    Returns: (prediction, probability)
    """
    model = load_model(SUCCESS_MODEL_PATH)
    features = _build_feature_array(
        quiz_score_avg, learning_time_hrs, activity_level,
        study_failures, parental_education, internet_access,
    )
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    return int(prediction), probability.tolist()


def get_user_ml_features(user_id):
    """
    Extract ML features from a user's database records.

    Returns the 3 core features derived from actual user activity.
    The 3 additional UCI features (study_failures, parental_education,
    internet_access) are filled with training-set defaults at prediction
    time via _build_feature_array.
    """
    quiz_stats = get_user_quiz_stats(user_id)
    activity_stats = get_user_activity_stats(user_id)

    quiz_score_avg = quiz_stats['avg_score'] if quiz_stats['total_quizzes'] > 0 else 50
    learning_time = min(activity_stats['total_learning_time'] / 60, 20)  # cap at 20 hrs
    activity_level = min(activity_stats['total_activities'], 10)  # cap at 10

    return quiz_score_avg, learning_time, activity_level


DIFFICULTY_LABELS = {0: 'Easier', 1: 'Same Level', 2: 'Harder'}


@ml_bp.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') == 'teacher':
        return redirect(url_for('analytics.teacher_dashboard'))

    user_id = session['user_id']
    quiz_score_avg, learning_time, activity_level = get_user_ml_features(user_id)

    # Predict difficulty preference
    diff_pred, diff_probs = predict_difficulty(quiz_score_avg, learning_time, activity_level)
    diff_label = DIFFICULTY_LABELS.get(diff_pred, 'Same Level')

    # Predict success
    success_pred, success_probs = predict_success(quiz_score_avg, learning_time, activity_level)
    success_probability = round(success_probs[1] * 100, 1) if len(success_probs) > 1 else 50.0

    # Get recommended quizzes based on difficulty prediction
    all_quizzes = get_all_quizzes()
    user_results = get_results_by_user(user_id)
    completed_quiz_ids = {r['quiz_id'] for r in user_results}

    # Filter quizzes by recommended difficulty
    difficulty_map = {0: 'easy', 1: 'medium', 2: 'hard'}
    recommended_difficulty = difficulty_map.get(diff_pred, 'medium')

    recommended_quizzes = [q for q in all_quizzes if q['id'] not in completed_quiz_ids]
    # Sort: recommended difficulty first, then others
    recommended_quizzes.sort(key=lambda q: (0 if q['difficulty'] == recommended_difficulty else 1))

    # Course recommendations
    all_courses = get_all_courses()
    course_difficulty_map = {0: 'beginner', 1: 'intermediate', 2: 'advanced'}
    recommended_course_diff = course_difficulty_map.get(diff_pred, 'intermediate')
    recommended_courses = sorted(all_courses,
                                 key=lambda c: (0 if c['difficulty'] == recommended_course_diff else 1))

    return render_template('recommendations.html',
                           quiz_score_avg=round(quiz_score_avg, 1),
                           learning_time=round(learning_time, 1),
                           activity_level=activity_level,
                           diff_label=diff_label,
                           diff_probs=diff_probs,
                           success_probability=success_probability,
                           success_pred=success_pred,
                           recommended_quizzes=recommended_quizzes[:5],
                           recommended_courses=recommended_courses[:5])
