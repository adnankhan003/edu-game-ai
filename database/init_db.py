"""
Database initialization script.
Creates all tables and seeds sample data (courses, lessons, quizzes, badges).
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'education.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def get_db():
    """Return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables from schema.sql."""
    conn = get_db()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def seed_data():
    """Insert sample courses, lessons, quizzes, questions, and badges."""
    conn = get_db()
    cur = conn.cursor()

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM courses")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    # --- Courses ---
    courses = [
        ('Python Programming', 'Learn Python from basics to advanced concepts.', 'beginner', 'Programming'),
        ('Data Science Fundamentals', 'Introduction to data science with Python.', 'intermediate', 'Data Science'),
        ('Web Development with Flask', 'Build web applications using Flask framework.', 'intermediate', 'Web Development'),
        ('Machine Learning Basics', 'Understand core ML algorithms and techniques.', 'advanced', 'AI & ML'),
        ('Database Management', 'Learn SQL and database design principles.', 'beginner', 'Databases'),
    ]
    cur.executemany("INSERT INTO courses (title, description, difficulty, category) VALUES (?,?,?,?)", courses)

    # --- Lessons ---
    lessons = [
        # Python Programming (course_id=1)
        (1, 'Introduction to Python', '<h2>Welcome to Python!</h2><p>Python is a versatile, high-level programming language known for its readability. It is widely used in web development, data analysis, artificial intelligence, and more.</p><h3>Key Features</h3><ul><li>Easy to learn syntax</li><li>Interpreted language</li><li>Dynamically typed</li><li>Large standard library</li></ul><p>In this course, you will learn Python from scratch and build real-world projects.</p>', 1),
        (1, 'Variables and Data Types', '<h2>Variables in Python</h2><p>Variables are containers for storing data values. Python has no command for declaring a variable — a variable is created the moment you first assign a value to it.</p><h3>Common Data Types</h3><ul><li><strong>int</strong> — Integer numbers (e.g., 42)</li><li><strong>float</strong> — Decimal numbers (e.g., 3.14)</li><li><strong>str</strong> — Strings (e.g., "Hello")</li><li><strong>bool</strong> — Boolean (True/False)</li><li><strong>list</strong> — Ordered collection</li></ul><pre><code>name = "Alice"\nage = 25\npi = 3.14159\nis_student = True</code></pre>', 2),
        (1, 'Control Flow', '<h2>Control Flow Statements</h2><p>Control flow determines the order in which code is executed.</p><h3>If-Else</h3><pre><code>if score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelse:\n    grade = "C"</code></pre><h3>Loops</h3><pre><code>for i in range(5):\n    print(i)\n\nwhile count > 0:\n    count -= 1</code></pre>', 3),
        # Data Science (course_id=2)
        (2, 'What is Data Science?', '<h2>Data Science Overview</h2><p>Data Science is an interdisciplinary field that uses scientific methods, algorithms, and systems to extract knowledge from data.</p><h3>Key Areas</h3><ul><li>Data Collection</li><li>Data Cleaning</li><li>Exploratory Data Analysis</li><li>Machine Learning</li><li>Data Visualization</li></ul>', 1),
        (2, 'Pandas Basics', '<h2>Introduction to Pandas</h2><p>Pandas is a powerful Python library for data manipulation and analysis.</p><h3>Core Structures</h3><ul><li><strong>Series</strong> — 1D labeled array</li><li><strong>DataFrame</strong> — 2D labeled table</li></ul><pre><code>import pandas as pd\ndf = pd.read_csv("data.csv")\nprint(df.head())</code></pre>', 2),
        # Flask Web Dev (course_id=3)
        (3, 'Getting Started with Flask', '<h2>Flask Framework</h2><p>Flask is a lightweight WSGI web application framework in Python. It is designed to make getting started quick and easy.</p><h3>Minimal App</h3><pre><code>from flask import Flask\napp = Flask(__name__)\n\n@app.route("/")\ndef hello():\n    return "Hello, World!"</code></pre>', 1),
        (3, 'Templates and Forms', '<h2>Jinja2 Templates</h2><p>Flask uses the Jinja2 template engine to render HTML pages dynamically.</p><pre><code>&lt;h1&gt;Hello, {{ name }}!&lt;/h1&gt;</code></pre><p>Forms can be handled using Flask\'s request object to capture user input.</p>', 2),
        # ML Basics (course_id=4)
        (4, 'Introduction to Machine Learning', '<h2>What is Machine Learning?</h2><p>Machine Learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.</p><h3>Types of ML</h3><ul><li><strong>Supervised Learning</strong> — labeled data</li><li><strong>Unsupervised Learning</strong> — unlabeled data</li><li><strong>Reinforcement Learning</strong> — reward-based</li></ul>', 1),
        (4, 'Classification Algorithms', '<h2>Classification</h2><p>Classification is the process of predicting a discrete class label for a given observation.</p><h3>Popular Algorithms</h3><ul><li>Decision Trees</li><li>Random Forest</li><li>Support Vector Machines</li><li>K-Nearest Neighbors</li></ul>', 2),
        # Database Management (course_id=5)
        (5, 'SQL Fundamentals', '<h2>Structured Query Language</h2><p>SQL is the standard language for relational database management systems.</p><h3>Basic Commands</h3><pre><code>SELECT * FROM users;\nINSERT INTO users (name) VALUES ("Alice");\nUPDATE users SET name="Bob" WHERE id=1;\nDELETE FROM users WHERE id=1;</code></pre>', 1),
        (5, 'Database Design', '<h2>Designing Good Databases</h2><p>Good database design ensures data integrity, reduces redundancy, and improves performance.</p><h3>Normalization</h3><ul><li>1NF — Atomic values</li><li>2NF — No partial dependencies</li><li>3NF — No transitive dependencies</li></ul>', 2),
    ]
    cur.executemany("INSERT INTO lessons (course_id, title, content, order_num) VALUES (?,?,?,?)", lessons)

    # --- Quizzes ---
    quizzes = [
        (1, 'Python Basics Quiz', 'easy', 100),
        (1, 'Python Intermediate Quiz', 'medium', 100),
        (2, 'Data Science Quiz', 'medium', 100),
        (3, 'Flask Fundamentals Quiz', 'medium', 100),
        (4, 'Machine Learning Quiz', 'hard', 100),
        (5, 'SQL Basics Quiz', 'easy', 100),
    ]
    cur.executemany("INSERT INTO quizzes (course_id, title, difficulty, total_marks) VALUES (?,?,?,?)", quizzes)

    # --- Quiz Questions ---
    questions = [
        # Python Basics Quiz (quiz_id=1)
        (1, 'What is the output of print(2 ** 3)?', '5', '6', '8', '9', 'C'),
        (1, 'Which keyword is used to define a function in Python?', 'func', 'def', 'function', 'define', 'B'),
        (1, 'What data type is the result of: 3 / 2?', 'int', 'float', 'str', 'bool', 'B'),
        (1, 'Which of these is a mutable data type?', 'tuple', 'str', 'list', 'int', 'C'),
        (1, 'What does len("Hello") return?', '4', '5', '6', 'Error', 'B'),
        # Python Intermediate Quiz (quiz_id=2)
        (2, 'What is a list comprehension?', 'A loop', 'A concise way to create lists', 'A function', 'A class', 'B'),
        (2, 'Which module is used for regular expressions?', 'regex', 're', 'reg', 'expression', 'B'),
        (2, 'What does the "self" parameter refer to?', 'The class', 'The instance', 'The module', 'Nothing', 'B'),
        (2, 'What is a decorator in Python?', 'A design pattern', 'A function that modifies another function', 'A class attribute', 'A variable', 'B'),
        (2, 'Which method is called when an object is created?', '__start__', '__init__', '__new__', '__create__', 'B'),
        # Data Science Quiz (quiz_id=3)
        (3, 'What library is used for data manipulation in Python?', 'NumPy', 'Pandas', 'Matplotlib', 'Scikit-learn', 'B'),
        (3, 'What is a DataFrame?', 'A 1D array', 'A 2D labeled data structure', 'A graph', 'A neural network', 'B'),
        (3, 'Which function reads a CSV file in Pandas?', 'read_file()', 'read_csv()', 'load_csv()', 'open_csv()', 'B'),
        (3, 'What is EDA?', 'External Data Analysis', 'Exploratory Data Analysis', 'Extended Data Algorithm', 'Easy Data Access', 'B'),
        (3, 'Which plot shows distribution of data?', 'Scatter plot', 'Histogram', 'Line chart', 'Pie chart', 'B'),
        # Flask Quiz (quiz_id=4)
        (4, 'What is Flask?', 'A database', 'A web framework', 'An OS', 'A language', 'B'),
        (4, 'Which decorator defines a route in Flask?', '@route', '@app.route', '@flask.route', '@url', 'B'),
        (4, 'What template engine does Flask use?', 'Django', 'Mako', 'Jinja2', 'Chameleon', 'C'),
        (4, 'How do you run a Flask app in debug mode?', 'app.debug()', 'app.run(debug=True)', 'flask run --debug', 'Both B and C', 'D'),
        (4, 'What does url_for() do?', 'Creates a URL', 'Builds URL for a function', 'Redirects', 'Validates URL', 'B'),
        # ML Quiz (quiz_id=5)
        (5, 'What is supervised learning?', 'Learning without data', 'Learning from labeled data', 'Learning from rewards', 'Unsupervised learning', 'B'),
        (5, 'Which algorithm is used for classification?', 'Linear Regression', 'Random Forest', 'K-Means', 'PCA', 'B'),
        (5, 'What is overfitting?', 'Model performs well on all data', 'Model is too simple', 'Model memorizes training data', 'Model uses too little data', 'C'),
        (5, 'What does the train_test_split function do?', 'Trains the model', 'Splits data into train and test sets', 'Tests the model', 'Validates the model', 'B'),
        (5, 'What is a feature in ML?', 'An output', 'An input variable', 'A model', 'A dataset', 'B'),
        # SQL Quiz (quiz_id=6)
        (6, 'What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'Standard Query Logic', 'System Query Language', 'A'),
        (6, 'Which command retrieves data?', 'GET', 'SELECT', 'RETRIEVE', 'FETCH', 'B'),
        (6, 'Which clause filters rows?', 'ORDER BY', 'GROUP BY', 'WHERE', 'HAVING', 'C'),
        (6, 'What is a primary key?', 'Any column', 'A unique identifier for each row', 'A foreign key', 'An index', 'B'),
        (6, 'Which keyword removes duplicates?', 'UNIQUE', 'DISTINCT', 'REMOVE', 'FILTER', 'B'),
    ]
    cur.executemany(
        "INSERT INTO quiz_questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?,?,?,?,?,?,?)",
        questions
    )

    # --- Badges ---
    badges = [
        ('First Steps', 'Complete your first quiz', '🎯', 'first_quiz'),
        ('Quick Learner', 'Complete 3 quizzes', '⚡', 'three_quizzes'),
        ('Scholar', 'Complete 5 quizzes', '📚', 'five_quizzes'),
        ('Perfect Score', 'Score 100% on any quiz', '🌟', 'perfect_score'),
        ('High Achiever', 'Earn 500 points', '🏆', 'points_500'),
        ('Master', 'Earn 1000 points', '👑', 'points_1000'),
        ('Dedicated', 'Login 5 times', '🔥', 'login_5'),
        ('Explorer', 'View all courses', '🗺️', 'all_courses'),
    ]
    cur.executemany("INSERT INTO badges (name, description, icon, criteria) VALUES (?,?,?,?)", badges)

    conn.commit()
    conn.close()
    print("Database seeded successfully!")


if __name__ == '__main__':
    init_db()
    seed_data()
    print("Database initialized and seeded.")
