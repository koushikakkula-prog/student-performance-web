import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'best_model.joblib')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'metrics.json')

PARENTAL_EDU_MAP = {
    "High School": 1,
    "Associate": 2,
    "Bachelor's": 3,
    "Master's": 4,
    "Doctorate": 5
}

FEATURE_COLUMNS = [
    'attendance',
    'prev_marks',
    'study_hours',
    'assignment_score',
    'internal_marks',
    'class_test_marks',
    'past_failures',
    'sleep_hours',
    'extracurricular_num',
    'internet_access_num',
    'parental_edu_num',
    'age'
]

def generate_synthetic_dataset(n_samples=2500, random_state=42):
    """
    Generate realistic synthetic student dataset with authentic correlations.
    """
    np.random.seed(random_state)
    
    # 1. Base academic aptitude factor
    aptitude = np.random.normal(70, 14, n_samples)
    aptitude = np.clip(aptitude, 30, 98)
    
    # 2. Features influenced by aptitude and random variation
    attendance = np.clip(aptitude * 0.7 + np.random.normal(25, 10, n_samples), 35, 100)
    study_hours = np.clip((aptitude / 15.0) + np.random.normal(1.2, 1.0, n_samples), 0.5, 10.0)
    prev_marks = np.clip(aptitude * 0.85 + np.random.normal(8, 6, n_samples), 30, 99)
    assignment_score = np.clip(aptitude * 0.8 + (attendance * 0.15) + np.random.normal(5, 5, n_samples), 30, 100)
    internal_marks = np.clip(aptitude * 0.82 + (study_hours * 2.0) + np.random.normal(4, 5, n_samples), 25, 100)
    class_test_marks = np.clip(aptitude * 0.78 + (study_hours * 2.2) + np.random.normal(5, 6, n_samples), 25, 100)
    
    # Past failures (more likely if low previous marks / low attendance)
    fail_prob = np.clip(1.0 - (prev_marks / 100.0) * 0.9, 0.05, 0.85)
    past_failures = np.random.binomial(3, fail_prob)
    
    sleep_hours = np.clip(np.random.normal(7.0, 1.1, n_samples), 4.0, 10.0)
    age = np.random.randint(17, 25, n_samples)
    
    extracurricular_num = np.random.choice([0, 1], size=n_samples, p=[0.45, 0.55])
    internet_access_num = np.random.choice([0, 1], size=n_samples, p=[0.12, 0.88])
    parental_edu_num = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.20, 0.25, 0.35, 0.15, 0.05])
    
    # Target formula: Final Academic Percentage
    # Weighted combination of continuous indicators + realistic educational dynamics
    final_score = (
        0.28 * internal_marks +
        0.22 * prev_marks +
        0.18 * class_test_marks +
        0.14 * assignment_score +
        0.10 * attendance +
        1.2 * study_hours -
        2.5 * past_failures +
        0.5 * (parental_edu_num - 3) +
        0.8 * internet_access_num +
        0.5 * extracurricular_num +
        np.random.normal(0, 1.8, n_samples)
    )
    final_score = np.clip(final_score, 20.0, 99.5)
    
    df = pd.DataFrame({
        'attendance': np.round(attendance, 1),
        'prev_marks': np.round(prev_marks, 1),
        'study_hours': np.round(study_hours, 1),
        'assignment_score': np.round(assignment_score, 1),
        'internal_marks': np.round(internal_marks, 1),
        'class_test_marks': np.round(class_test_marks, 1),
        'past_failures': past_failures,
        'sleep_hours': np.round(sleep_hours, 1),
        'extracurricular_num': extracurricular_num,
        'internet_access_num': internet_access_num,
        'parental_edu_num': parental_edu_num,
        'age': age,
        'final_percentage': np.round(final_score, 1)
    })
    
    return df

def train_and_save_models():
    """
    Train Linear Regression, Decision Tree, and Random Forest models.
    Select and persist the best performing model.
    """
    df = generate_synthetic_dataset(n_samples=3000)
    
    X = df[FEATURE_COLUMNS]
    y = df['final_percentage']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42),
        "Decision Tree Regressor": DecisionTreeRegressor(max_depth=8, random_state=42),
        "Linear Regression": LinearRegression()
    }
    
    results = {}
    best_model_name = None
    best_r2 = -1.0
    best_model_obj = None
    
    for name, model in models.items():
        if name == "Linear Regression":
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
        r2 = float(r2_score(y_test, preds))
        mae = float(mean_absolute_error(y_test, preds))
        mse = float(mean_squared_error(y_test, preds))
        rmse = float(np.sqrt(mse))
        
        results[name] = {
            'r2_score': round(r2, 4),
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'rmse': round(rmse, 2),
            'accuracy_percentage': round(max(0, min(100, r2 * 100)), 2)
        }
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model_obj = model
            
    # Feature importances for Random Forest
    rf_model = models["Random Forest Regressor"]
    feature_importances = dict(zip(FEATURE_COLUMNS, [round(float(val), 4) for val in rf_model.feature_importances_]))
    
    # Save artifacts
    joblib.dump(best_model_obj, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    metrics_data = {
        'best_model': best_model_name,
        'models_comparison': results,
        'feature_importances': feature_importances,
        'features': FEATURE_COLUMNS,
        'dataset_size': len(df)
    }
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics_data, f, indent=4)
        
    return metrics_data

def get_model_and_scaler():
    """
    Load saved model and scaler, training on-the-fly if not found.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        train_and_save_models()
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler

def get_performance_category(score):
    """
    Categorize score based on defined grading scale:
    90–100% = Outstanding (O)
    80–89% = Excellent (A+)
    70–79% = Good (A)
    60–69% = Average (B)
    50–59% = Needs Improvement (C)
    Below 50% = At Risk (F)
    """
    if score >= 90.0:
        return {"level": "Outstanding", "grade": "O", "badge_class": "badge-outstanding", "color": "#10B981", "status_text": "Top Tier Academic Performer"}
    elif score >= 80.0:
        return {"level": "Excellent", "grade": "A+", "badge_class": "badge-excellent", "color": "#3B82F6", "status_text": "Strong Academic Performer"}
    elif score >= 70.0:
        return {"level": "Good", "grade": "A", "badge_class": "badge-good", "color": "#06B6D4", "status_text": "Consistent Performer"}
    elif score >= 60.0:
        return {"level": "Average", "grade": "B", "badge_class": "badge-average", "color": "#F59E0B", "status_text": "Moderate Academic Performance"}
    elif score >= 40.0:
        return {"level": "Needs Improvement", "grade": "C", "badge_class": "badge-improvement", "color": "#F97316", "status_text": "Attention Required"}
    else:
        return {"level": "Fail", "grade": "Fail", "badge_class": "badge-risk", "color": "#EF4444", "status_text": "Critical Academic Alert - Fail"}

def generate_ai_suggestions(data, predicted_score):
    """
    Generate targeted AI-based actionable suggestions based on input criteria.
    """
    suggestions = []
    
    attendance = float(data.get('attendance', 75))
    study_hours = float(data.get('study_hours', 3))
    internal_marks = float(data.get('internal_marks', 70))
    assignment_score = float(data.get('assignment_score', 75))
    class_test_marks = float(data.get('class_test_marks', 70))
    past_failures = int(data.get('past_failures', 0))
    sleep_hours = float(data.get('sleep_hours', 7))
    internet_access = data.get('internet_access', 'Yes')
    extracurricular = data.get('extracurricular', 'No')

    # Specific weak area checks
    if attendance < 75.0:
        suggestions.append({
            "type": "warning",
            "icon": "fa-user-clock",
            "title": "Improve Attendance",
            "text": f"Current attendance is {attendance}%. Raise it above 75% to meet mandatory college criteria and ensure you don't miss core concepts."
        })
    else:
        suggestions.append({
            "type": "success",
            "icon": "fa-calendar-check",
            "title": "Attendance Health",
            "text": f"Great attendance ({attendance}%). Continue attending lectures regularly for strong concept reinforcement."
        })

    if study_hours < 3.0:
        suggestions.append({
            "type": "warning",
            "icon": "fa-book-open-reader",
            "title": "Increase Daily Study Hours",
            "text": f"Currently studying {study_hours} hrs/day. Increasing this to 3.5 - 5.0 hours of focused study will significantly boost performance."
        })
    else:
        suggestions.append({
            "type": "success",
            "icon": "fa-brain",
            "title": "Study Consistency",
            "text": f"Devoting {study_hours} hrs/day is commendable. Maintain consistent study habits with active recall techniques."
        })

    if internal_marks < 65.0 or class_test_marks < 65.0:
        suggestions.append({
            "type": "warning",
            "icon": "fa-pen-to-square",
            "title": "Internal Exam & Test Preparation",
            "text": "Spend more time preparing for internal examinations and weekly class tests by solving previous semester question papers."
        })

    if past_failures > 0:
        suggestions.append({
            "type": "danger",
            "icon": "fa-triangle-exclamation",
            "title": "Focus on Weak Subjects",
            "text": f"{past_failures} past backlog(s) detected. Prioritize foundational concept revisions and seek 1-on-1 faculty tutoring."
        })

    if sleep_hours < 6.0:
        suggestions.append({
            "type": "info",
            "icon": "fa-bed",
            "title": "Sleep & Cognitive Recovery",
            "text": f"Sleeping {sleep_hours} hrs is below recommended levels. Target 7-8 hours of sleep for optimal memory retention and stress reduction."
        })
    elif sleep_hours > 9.0:
        suggestions.append({
            "type": "info",
            "icon": "fa-bed",
            "title": "Balance Rest & Study",
            "text": "Ensure your extended sleep schedule leaves ample structured time for active revision and assignments."
        })

    if assignment_score < 70.0:
        suggestions.append({
            "type": "warning",
            "icon": "fa-file-signature",
            "title": "Coursework Submissions",
            "text": "Dedicate more effort to assignment solutions and submit coursework early to secure maximum internal marks."
        })

    if extracurricular.lower() in ['no', 'false']:
        suggestions.append({
            "type": "info",
            "icon": "fa-volleyball",
            "title": "Extracurricular Balance",
            "text": "Consider joining sports, clubs, or tech societies to foster critical soft skills and combat study fatigue."
        })

    if predicted_score >= 85.0:
        suggestions.append({
            "type": "success",
            "icon": "fa-award",
            "title": "Aim for Academic Honors",
            "text": "You are on track for top honors! Explore research papers, competitive coding, or student mentorship programs."
        })

    return suggestions

def predict_student(data):
    """
    Main prediction routine taking input dict, generating predicted score, grade,
    performance category, and customized AI recommendations.
    """
    model, scaler = get_model_and_scaler()
    
    # Feature extraction and encoding
    attendance = float(data.get('attendance', 75.0))
    prev_marks = float(data.get('prev_marks', 70.0))
    study_hours = float(data.get('study_hours', 3.0))
    assignment_score = float(data.get('assignment_score', 75.0))
    internal_marks = float(data.get('internal_marks', 70.0))
    class_test_marks = float(data.get('class_test_marks', 70.0))
    past_failures = int(data.get('past_failures', 0))
    sleep_hours = float(data.get('sleep_hours', 7.0))
    
    extracurricular_str = str(data.get('extracurricular', 'No')).strip().capitalize()
    extracurricular_num = 1 if extracurricular_str in ['Yes', 'Y', '1', 'True'] else 0
    
    internet_access_str = str(data.get('internet_access', 'Yes')).strip().capitalize()
    internet_access_num = 1 if internet_access_str in ['Yes', 'Y', '1', 'True'] else 0
    
    parental_edu_str = str(data.get('parental_edu', "Bachelor's")).strip()
    parental_edu_num = PARENTAL_EDU_MAP.get(parental_edu_str, 3)
    
    age = int(data.get('age', 20))
    
    feature_df = pd.DataFrame([[
        attendance,
        prev_marks,
        study_hours,
        assignment_score,
        internal_marks,
        class_test_marks,
        past_failures,
        sleep_hours,
        extracurricular_num,
        internet_access_num,
        parental_edu_num,
        age
    ]], columns=FEATURE_COLUMNS)
    
    # If linear regression was selected, use scaler
    if isinstance(model, LinearRegression):
        features_scaled = scaler.transform(feature_df)
        pred_raw = model.predict(features_scaled)[0]
    else:
        pred_raw = model.predict(feature_df)[0]
        
    predicted_score = round(float(np.clip(pred_raw, 10.0, 99.8)), 1)
    category_info = get_performance_category(predicted_score)
    suggestions = generate_ai_suggestions(data, predicted_score)
    
    return {
        'student_name': data.get('student_name', 'Student'),
        'student_id': data.get('student_id', 'STU-000'),
        'gender': data.get('gender', 'Other'),
        'age': age,
        'attendance': attendance,
        'prev_marks': prev_marks,
        'study_hours': study_hours,
        'assignment_score': assignment_score,
        'internal_marks': internal_marks,
        'class_test_marks': class_test_marks,
        'past_failures': past_failures,
        'extracurricular': extracurricular_str,
        'internet_access': internet_access_str,
        'parental_edu': parental_edu_str,
        'sleep_hours': sleep_hours,
        'predicted_score': predicted_score,
        'predicted_grade': category_info['grade'],
        'performance_level': category_info['level'],
        'badge_class': category_info['badge_class'],
        'status_text': category_info['status_text'],
        'theme_color': category_info['color'],
        'recommendations': suggestions
    }

if __name__ == '__main__':
    print("Training models...")
    metrics = train_and_save_models()
    print("Models trained successfully!")
    print(json.dumps(metrics, indent=2))
