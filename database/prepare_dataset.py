"""
UCI Student Performance Dataset - Preprocessing Script
=======================================================
Generates a realistic student performance dataset modeled after the UCI
Student Performance dataset (Cortez & Silva, 2008) and transforms it into
the feature format consumed by the ML engine.

Usage:
    python database/prepare_dataset.py

Outputs:
    database/student_performance.csv - full student records (UCI format)
    database/ml_training_data.csv    - features ready for model training
"""
import os
import random
import csv
import math

# ── Paths ─────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, 'student_performance.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'ml_training_data.csv')

# ── Constants ─────────────────────────────────────────────────────
SCHOOLS = ['GP', 'MS']
SEXES = ['F', 'M']
ADDRESSES = ['U', 'R']
FAMSIZES = ['LE3', 'GT3']
PSTATUSES = ['T', 'A']
JOBS = ['teacher', 'health', 'services', 'at_home', 'other']
REASONS = ['home', 'reputation', 'course', 'other']
GUARDIANS = ['mother', 'father', 'other']
YES_NO = ['yes', 'no']


def weighted_choice(options, weights):
    """Pick from options using weights."""
    total = sum(weights)
    r = random.random() * total
    cumulative = 0
    for opt, w in zip(options, weights):
        cumulative += w
        if r <= cumulative:
            return opt
    return options[-1]


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate_student(student_id):
    """Generate one realistic student record following UCI distributions."""
    random.seed(student_id * 7 + 42)  # reproducible per-student

    school = weighted_choice(SCHOOLS, [0.65, 0.35])
    sex = weighted_choice(SEXES, [0.53, 0.47])
    age = weighted_choice(list(range(15, 23)),
                          [0.10, 0.18, 0.22, 0.25, 0.13, 0.07, 0.03, 0.02])
    address = weighted_choice(ADDRESSES, [0.78, 0.22])
    famsize = weighted_choice(FAMSIZES, [0.35, 0.65])
    Pstatus = weighted_choice(PSTATUSES, [0.88, 0.12])
    Medu = weighted_choice([0, 1, 2, 3, 4], [0.04, 0.14, 0.22, 0.28, 0.32])
    Fedu = weighted_choice([0, 1, 2, 3, 4], [0.06, 0.18, 0.26, 0.28, 0.22])
    Mjob = weighted_choice(JOBS, [0.10, 0.06, 0.16, 0.28, 0.40])
    Fjob = weighted_choice(JOBS, [0.04, 0.04, 0.24, 0.12, 0.56])
    reason = weighted_choice(REASONS, [0.25, 0.28, 0.34, 0.13])
    guardian = weighted_choice(GUARDIANS, [0.70, 0.22, 0.08])
    traveltime = weighted_choice([1, 2, 3, 4], [0.50, 0.35, 0.10, 0.05])
    studytime = weighted_choice([1, 2, 3, 4], [0.27, 0.42, 0.20, 0.11])
    failures = weighted_choice([0, 1, 2, 3], [0.66, 0.18, 0.10, 0.06])

    schoolsup = weighted_choice(YES_NO, [0.11, 0.89])
    famsup = weighted_choice(YES_NO, [0.58, 0.42])
    paid = weighted_choice(YES_NO, [0.20, 0.80])
    activities = weighted_choice(YES_NO, [0.52, 0.48])
    nursery = weighted_choice(YES_NO, [0.82, 0.18])
    higher = weighted_choice(YES_NO, [0.88, 0.12])
    internet = weighted_choice(YES_NO, [0.66, 0.34])
    romantic = weighted_choice(YES_NO, [0.33, 0.67])

    famrel = weighted_choice([1, 2, 3, 4, 5], [0.03, 0.06, 0.18, 0.48, 0.25])
    freetime = weighted_choice([1, 2, 3, 4, 5], [0.05, 0.12, 0.40, 0.30, 0.13])
    goout = weighted_choice([1, 2, 3, 4, 5], [0.08, 0.18, 0.32, 0.28, 0.14])
    Dalc = weighted_choice([1, 2, 3, 4, 5], [0.63, 0.20, 0.10, 0.04, 0.03])
    Walc = weighted_choice([1, 2, 3, 4, 5], [0.37, 0.25, 0.20, 0.11, 0.07])
    health = weighted_choice([1, 2, 3, 4, 5], [0.10, 0.08, 0.20, 0.18, 0.44])
    absences = clamp(int(random.gauss(5.7, 8)), 0, 75)

    # ── Grade generation (correlated with student attributes) ──
    # Base ability from parental education & higher aspiration
    base = 7 + (Medu + Fedu) * 0.5
    if higher == 'yes':
        base += 2
    if internet == 'yes':
        base += 0.5
    base -= failures * 1.5
    base += studytime * 0.8
    base -= (goout - 3) * 0.4
    base -= (Dalc + Walc - 2) * 0.3
    if schoolsup == 'yes':
        base += 0.5
    base += random.gauss(0, 1.8)

    G1 = clamp(int(round(base + random.gauss(0, 1.5))), 0, 20)
    # G2 correlated with G1
    G2 = clamp(int(round(G1 * 0.85 + base * 0.15 + random.gauss(0, 1.2))), 0, 20)
    # G3 correlated with G2
    G3 = clamp(int(round(G2 * 0.75 + base * 0.25 + random.gauss(0, 1.5))), 0, 20)

    return {
        'school': school, 'sex': sex, 'age': age, 'address': address,
        'famsize': famsize, 'Pstatus': Pstatus, 'Medu': Medu, 'Fedu': Fedu,
        'Mjob': Mjob, 'Fjob': Fjob, 'reason': reason, 'guardian': guardian,
        'traveltime': traveltime, 'studytime': studytime, 'failures': failures,
        'schoolsup': schoolsup, 'famsup': famsup, 'paid': paid,
        'activities': activities, 'nursery': nursery, 'higher': higher,
        'internet': internet, 'romantic': romantic,
        'famrel': famrel, 'freetime': freetime, 'goout': goout,
        'Dalc': Dalc, 'Walc': Walc, 'health': health, 'absences': absences,
        'G1': G1, 'G2': G2, 'G3': G3,
    }


def generate_raw_dataset(n_students=649):
    """Generate the full UCI-format dataset."""
    columns = [
        'school', 'sex', 'age', 'address', 'famsize', 'Pstatus',
        'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian',
        'traveltime', 'studytime', 'failures',
        'schoolsup', 'famsup', 'paid', 'activities', 'nursery',
        'higher', 'internet', 'romantic',
        'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health',
        'absences', 'G1', 'G2', 'G3',
    ]
    rows = [generate_student(i) for i in range(n_students)]

    with open(RAW_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Generated {n_students} student records -> {RAW_PATH}")
    return rows


def preprocess(rows):
    """
    Transform raw UCI-format records into ML training features.

    Output columns:
        quiz_score_avg        - avg(G1,G2,G3) scaled to 0-100
        learning_time_hrs     - studytime mapped to realistic hours
        activity_level        - composite engagement score (0-10)
        study_failures        - number of past failures (0-4)
        parental_education    - (Medu + Fedu) / 2, scaled 0-4
        internet_access       - 1 if internet=yes else 0
        difficulty_preference - 0=easier, 1=same, 2=harder (from grade trajectory)
        success               - 1 if G3 >= 10, else 0
    """
    studytime_map = {1: 2, 2: 5, 3: 10, 4: 15}
    processed = []

    for r in rows:
        G1 = int(r['G1'])
        G2 = int(r['G2'])
        G3 = int(r['G3'])

        # Feature: quiz_score_avg (0-100)
        avg_grade = (G1 + G2 + G3) / 3.0
        quiz_score_avg = round((avg_grade / 20.0) * 100, 1)

        # Feature: learning_time_hrs
        st = int(r['studytime'])
        learning_time_hrs = studytime_map.get(st, 5)

        # Feature: activity_level (0-10) — composite
        act = 1 if r['activities'] == 'yes' else 0
        freetime = int(r['freetime'])
        goout = int(r['goout'])
        absences = int(r['absences'])
        absence_score = max(0, 10 - absences)  # fewer absences = higher score
        raw_activity = act * 2 + freetime + (5 - goout) + absence_score * 0.3
        activity_level = clamp(round(raw_activity), 0, 10)

        # Feature: study_failures (0-4)
        study_failures = clamp(int(r['failures']), 0, 4)

        # Feature: parental_education (0-4)
        parental_education = round((int(r['Medu']) + int(r['Fedu'])) / 2.0, 1)

        # Feature: internet_access (0 or 1)
        internet_access = 1 if r['internet'] == 'yes' else 0

        # Target: difficulty_preference from grade trajectory
        trend = G3 - G1
        if trend >= 2:
            difficulty_preference = 2   # improving -> suggest harder
        elif trend <= -2:
            difficulty_preference = 0   # declining -> suggest easier
        else:
            difficulty_preference = 1   # stable -> same level

        # Target: success
        success = 1 if G3 >= 10 else 0

        processed.append({
            'quiz_score_avg': quiz_score_avg,
            'learning_time_hrs': learning_time_hrs,
            'activity_level': activity_level,
            'study_failures': study_failures,
            'parental_education': parental_education,
            'internet_access': internet_access,
            'difficulty_preference': difficulty_preference,
            'success': success,
        })

    return processed


def write_training_data(processed):
    """Write ml_training_data.csv."""
    columns = [
        'quiz_score_avg', 'learning_time_hrs', 'activity_level',
        'study_failures', 'parental_education', 'internet_access',
        'difficulty_preference', 'success',
    ]
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(processed)

    print(f"[OK] Wrote {len(processed)} training rows -> {OUTPUT_PATH}")


def print_stats(processed):
    """Print dataset statistics."""
    n = len(processed)
    print(f"\n{'='*55}")
    print(f"  UCI Student Performance Dataset - Summary")
    print(f"{'='*55}")
    print(f"  Total records:            {n}")

    successes = sum(1 for r in processed if r['success'] == 1)
    print(f"  Success (pass):           {successes} ({successes*100//n}%)")
    print(f"  Failure (fail):           {n - successes} ({(n-successes)*100//n}%)")

    diff_counts = {0: 0, 1: 0, 2: 0}
    for r in processed:
        diff_counts[r['difficulty_preference']] += 1
    print(f"\n  Difficulty preference distribution:")
    print(f"    Easier (0):  {diff_counts[0]:>4} ({diff_counts[0]*100//n}%)")
    print(f"    Same   (1):  {diff_counts[1]:>4} ({diff_counts[1]*100//n}%)")
    print(f"    Harder (2):  {diff_counts[2]:>4} ({diff_counts[2]*100//n}%)")

    avg_score = sum(r['quiz_score_avg'] for r in processed) / n
    avg_time = sum(r['learning_time_hrs'] for r in processed) / n
    avg_act = sum(r['activity_level'] for r in processed) / n
    print(f"\n  Feature averages:")
    print(f"    quiz_score_avg:         {avg_score:.1f}")
    print(f"    learning_time_hrs:      {avg_time:.1f}")
    print(f"    activity_level:         {avg_act:.1f}")
    print(f"    study_failures:         {sum(r['study_failures'] for r in processed)/n:.2f}")
    print(f"    parental_education:     {sum(r['parental_education'] for r in processed)/n:.2f}")
    print(f"    internet_access:        {sum(r['internet_access'] for r in processed)/n:.1%}")
    print(f"{'='*55}\n")


def main():
    print("\n  UCI Student Performance Dataset - Preparation")
    print("  " + "-" * 50)

    # Step 1: Generate raw UCI-format data (or load existing)
    if os.path.exists(RAW_PATH):
        print(f"  Found existing dataset: {RAW_PATH}")
        rows = []
        with open(RAW_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"  Loaded {len(rows)} records from existing file.")
    else:
        print("  No existing dataset found. Generating realistic UCI dataset...")
        rows = generate_raw_dataset(649)

    # Step 2: Preprocess
    print("  Preprocessing features...")
    processed = preprocess(rows)

    # Step 3: Write training data
    write_training_data(processed)

    # Step 4: Print stats
    print_stats(processed)

    print("  Done! ML engine will use database/ml_training_data.csv for training.\n")


if __name__ == '__main__':
    main()
