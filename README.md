# Machine Learning Driven Gamification Model for Personalized Education

A web-based learning platform that integrates gamification and machine learning to personalize the learning experience for students.

## Features

- **User Management** — Registration, login, profile & progress tracking
- **Course & Content** — Browse courses, read lessons, take quizzes
- **Gamification** — Points system, badges, levels, leaderboard
- **ML Personalization** — RandomForestClassifier recommends quiz difficulty and predicts student success
- **Teacher Analytics** — Student performance, engagement stats, predicted success

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **ML:** scikit-learn (RandomForestClassifier)
- **Frontend:** HTML, CSS (Jinja2 templates)

## Folder Structure

```
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
├── database/
│   ├── schema.sql          # SQLite schema
│   ├── init_db.py          # DB initialization & seed data
│   ├── prepare_dataset.py  # UCI dataset generation & preprocessing
│   ├── student_performance.csv   # Full UCI-format student records (649 students)
│   ├── ml_training_data.csv      # Preprocessed ML training data (6 features)
│   └── sample_ml_data.csv       # Legacy training data (fallback)
├── models/
│   ├── user.py             # User model
│   ├── course.py           # Course & lesson model
│   ├── quiz.py             # Quiz & results model
│   └── gamification.py     # Points, badges, levels, leaderboard
├── modules/
│   ├── auth.py             # Authentication routes
│   ├── courses.py          # Course & lesson routes
│   ├── quizzes.py          # Quiz routes
│   ├── gamification.py     # Leaderboard route
│   ├── ml_engine.py        # ML training & recommendation engine
│   └── analytics.py        # Teacher analytics dashboard
├── templates/              # HTML templates (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── courses.html
│   ├── course_detail.html
│   ├── lesson.html
│   ├── quiz.html
│   ├── quiz_result.html
│   ├── leaderboard.html
│   ├── recommendations.html
│   ├── profile.html
│   └── teacher_dashboard.html
└── static/css/
    └── style.css           # Dark theme CSS
```

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The app will:

- Create the SQLite database automatically
- Seed sample courses, lessons, quizzes, and badges
- Train the ML models on first run
- Start the server at **http://127.0.0.1:5000**

### 3. Usage

1. Open **http://127.0.0.1:5000** in your browser
2. **Register** a new account (choose Student or Teacher role)
3. **Login** with your credentials
4. **Browse courses**, read lessons, and take quizzes
5. Earn **points and badges** for quiz performance
6. Check the **leaderboard** to see your ranking
7. Visit **AI Insights** for personalized recommendations
8. Teachers can access the **Analytics Dashboard** for student performance data

## Sample Accounts

Register with any username/email/password. Select "Teacher" role to access the teacher dashboard.

## ML Model Details

The platform uses two **RandomForestClassifier** models trained on the **UCI Student Performance Dataset** (Cortez & Silva, 2008) — preprocessed into `database/ml_training_data.csv`:

1. **Difficulty Preference Model** — Predicts whether a student should attempt easier, same-level, or harder content
2. **Success Prediction Model** — Predicts the probability of a student's academic success (90.77% accuracy)

**Features used (6 total):**

| Feature              | Source                                     | Range  |
| -------------------- | ------------------------------------------ | ------ |
| `quiz_score_avg`     | Avg of G1, G2, G3 grades (scaled 0–100)    | 0–100  |
| `learning_time_hrs`  | Study time mapped to hours                 | 2–15   |
| `activity_level`     | Composite engagement score                 | 0–10   |
| `study_failures`     | Number of past academic failures           | 0–4    |
| `parental_education` | Average of mother & father education level | 0–4    |
| `internet_access`    | Whether student has internet at home       | 0 or 1 |

### Regenerate Training Data

```bash
python database/prepare_dataset.py
```

This regenerates `database/ml_training_data.csv` from `database/student_performance.csv`. The ML engine will automatically retrain on next app start if model files are deleted.
