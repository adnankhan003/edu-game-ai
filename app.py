"""
Machine Learning Driven Gamification Model for Personalized Education
=====================================================================
Main Flask application entry point.
"""
import os
from flask import Flask
from database.init_db import init_db, seed_data
from modules.ml_engine import train_models

def create_app():
    app = Flask(__name__)
    app.secret_key = 'ml-gamification-edu-secret-key-2024'

    # Initialize database
    init_db()
    seed_data()

    # Train ML models if not already trained
    model_path = os.path.join(os.path.dirname(__file__), 'database', 'difficulty_model.pkl')
    if not os.path.exists(model_path):
        print("Training ML models...")
        train_models()

    # Register blueprints
    from modules.auth import auth_bp
    from modules.courses import courses_bp
    from modules.quizzes import quizzes_bp
    from modules.gamification import gamification_bp
    from modules.ml_engine import ml_bp
    from modules.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(gamification_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(analytics_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n  ML Gamification Education Platform")
    print("  -----------------------------------")
    print("  Running at: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
