import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'student_records.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            attendance REAL NOT NULL,
            prev_marks REAL NOT NULL,
            study_hours REAL NOT NULL,
            assignment_score REAL NOT NULL,
            internal_marks REAL NOT NULL,
            class_test_marks REAL NOT NULL,
            past_failures INTEGER NOT NULL,
            extracurricular TEXT NOT NULL,
            internet_access TEXT NOT NULL,
            parental_edu TEXT NOT NULL,
            sleep_hours REAL NOT NULL,
            predicted_score REAL NOT NULL,
            predicted_grade TEXT NOT NULL,
            performance_level TEXT NOT NULL,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_student_record(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    recommendations_json = json.dumps(data.get('recommendations', []))
    
    cursor.execute('''
        INSERT INTO students (
            student_name, student_id, gender, age, attendance, prev_marks,
            study_hours, assignment_score, internal_marks, class_test_marks,
            past_failures, extracurricular, internet_access, parental_edu,
            sleep_hours, predicted_score, predicted_grade, performance_level,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('student_name', 'Anonymous'),
        data.get('student_id', 'STU-000'),
        data.get('gender', 'Other'),
        int(data.get('age', 18)),
        float(data.get('attendance', 75.0)),
        float(data.get('prev_marks', 70.0)),
        float(data.get('study_hours', 3.0)),
        float(data.get('assignment_score', 75.0)),
        float(data.get('internal_marks', 70.0)),
        float(data.get('class_test_marks', 70.0)),
        int(data.get('past_failures', 0)),
        data.get('extracurricular', 'No'),
        data.get('internet_access', 'Yes'),
        data.get('parental_edu', "Bachelor's"),
        float(data.get('sleep_hours', 7.0)),
        float(data.get('predicted_score', 75.0)),
        data.get('predicted_grade', 'B'),
        data.get('performance_level', 'Average'),
        recommendations_json
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_all_students(limit=500):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    students = []
    for row in rows:
        item = dict(row)
        if item.get('recommendations'):
            try:
                item['recommendations'] = json.loads(item['recommendations'])
            except Exception:
                item['recommendations'] = []
        students.append(item)
    return students

def get_student_by_id(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        if item.get('recommendations'):
            try:
                item['recommendations'] = json.loads(item['recommendations'])
            except Exception:
                item['recommendations'] = []
        return item
    return None

def delete_student_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ?', (record_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM students')
    total_students = cursor.fetchone()['count']
    
    if total_students == 0:
        conn.close()
        return {
            'total_students': 0,
            'excellent_students': 0,
            'average_students': 0,
            'at_risk_students': 0,
            'avg_performance': 0.0,
            'avg_attendance': 0.0,
            'categories': {
                'Outstanding': 0,
                'Excellent': 0,
                'Good': 0,
                'Average': 0,
                'Needs Improvement': 0,
                'Fail': 0
            },
            'recent_students': []
        }
    
    cursor.execute('SELECT AVG(predicted_score) as avg_score, AVG(attendance) as avg_att FROM students')
    row = cursor.fetchone()
    avg_score = round(row['avg_score'] or 0.0, 1)
    avg_att = round(row['avg_att'] or 0.0, 1)
    
    cursor.execute('''
        SELECT performance_level, COUNT(*) as count 
        FROM students 
        GROUP BY performance_level
    ''')
    category_counts = {
        'Outstanding': 0,
        'Excellent': 0,
        'Good': 0,
        'Average': 0,
        'Needs Improvement': 0,
        'Fail': 0
    }
    for r in cursor.fetchall():
        lvl = r['performance_level']
        if lvl in category_counts:
            category_counts[lvl] = r['count']
        elif lvl == 'At Risk':
            category_counts['Fail'] = category_counts.get('Fail', 0) + r['count']
    
    excellent_total = category_counts['Outstanding'] + category_counts['Excellent']
    average_total = category_counts['Good'] + category_counts['Average']
    at_risk_total = category_counts['Needs Improvement'] + category_counts['Fail']
    
    conn.close()
    
    return {
        'total_students': total_students,
        'excellent_students': excellent_total,
        'average_students': average_total,
        'at_risk_students': at_risk_total,
        'avg_performance': avg_score,
        'avg_attendance': avg_att,
        'categories': category_counts,
        'recent_students': get_all_students(limit=10)
    }

def seed_sample_students(force=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM students')
    count = cursor.fetchone()['count']
    
    if count > 0 and not force:
        conn.close()
        return False
        
    if force:
        cursor.execute('DELETE FROM students')
        conn.commit()
        
    sample_data = [
        ("Aarav Sharma", "STU-1001", "Male", 20, 94.5, 92.0, 6.5, 95.0, 91.0, 93.0, 0, "Yes", "Yes", "Master's", 7.5, 93.8, "O", "Outstanding", json.dumps(["Maintain consistent study habits.", "Continue strong internal exam preparation.", "Engage in peer tutoring."])),
        ("Priya Patel", "STU-1002", "Female", 19, 88.0, 85.5, 5.0, 88.0, 84.0, 86.0, 0, "Yes", "Yes", "Bachelor's", 7.0, 86.2, "A+", "Excellent", json.dumps(["Maintain consistent study habits.", "Target higher marks in competitive class tests."])),
        ("Rohan Verma", "STU-1003", "Male", 21, 78.5, 74.0, 3.5, 76.0, 72.0, 75.0, 0, "No", "Yes", "Bachelor's", 6.5, 74.8, "A", "Good", json.dumps(["Increase daily study time to 4.5+ hours.", "Participate actively in assignments."])),
        ("Ananya Iyer", "STU-1004", "Female", 20, 68.0, 65.0, 2.5, 66.0, 63.0, 64.0, 1, "No", "Yes", "High School", 6.0, 65.1, "B", "Average", json.dumps(["Improve attendance to above 75%.", "Spend more time preparing for internal examinations.", "Focus on weak subjects."])),
        ("Vikram Singh", "STU-1005", "Male", 22, 54.0, 52.0, 1.5, 55.0, 50.0, 52.0, 2, "No", "No", "High School", 5.5, 53.4, "C", "Needs Improvement", json.dumps(["Urgent: Improve attendance to at least 75%.", "Increase study hours from 1.5 to 4 hours daily.", "Attend remedial tutoring sessions."])),
        ("Kavya Nair", "STU-1006", "Female", 19, 48.0, 45.0, 1.5, 48.0, 44.0, 46.0, 2, "No", "Yes", "High School", 5.5, 45.8, "C", "Needs Improvement", json.dumps(["Academic guidance needed: Improve attendance above 75%.", "Seek peer study group support.", "Revise foundational lecture concepts."])),
        ("Siddharth Rao", "STU-1007", "Male", 20, 92.0, 89.0, 5.5, 91.0, 88.0, 90.0, 0, "Yes", "Yes", "Doctorate", 8.0, 89.4, "A+", "Excellent", json.dumps(["Maintain consistent study habits.", "Explore advanced research or honors projects."])),
        ("Meera Joshi", "STU-1008", "Female", 21, 82.0, 79.0, 4.0, 80.0, 77.0, 81.0, 0, "Yes", "Yes", "Bachelor's", 7.0, 79.6, "A", "Good", json.dumps(["Maintain consistent study habits.", "Focus on weak areas in internal exams."])),
        ("Devendra Gupta", "STU-1009", "Male", 20, 62.0, 58.0, 2.0, 60.0, 56.0, 59.0, 1, "No", "Yes", "Associate", 6.0, 58.7, "C", "Needs Improvement", json.dumps(["Improve class test preparation.", "Increase regular study hours to 3.5+ hours.", "Consult course professors for doubts."])),
        ("Sneha Kulkarni", "STU-1010", "Female", 19, 96.0, 95.0, 7.0, 97.0, 94.0, 96.0, 0, "Yes", "Yes", "Master's", 8.0, 95.7, "O", "Outstanding", json.dumps(["Outstanding performance! Keep up the brilliant momentum."])),
        ("Rahul Deshmukh", "STU-1011", "Male", 21, 72.0, 68.0, 3.0, 70.0, 67.0, 69.0, 0, "No", "Yes", "Bachelor's", 6.5, 68.9, "B", "Average", json.dumps(["Set structured revision schedules before exams.", "Improve assignment submission quality."])),
        ("Pooja Reddy", "STU-1012", "Female", 20, 35.0, 32.0, 0.8, 38.0, 30.0, 32.0, 3, "No", "Yes", "High School", 5.0, 34.6, "Fail", "Fail", json.dumps(["Critical Alert: High risk of academic failure (<40%).", "Mandatory academic counseling required.", "Schedule urgent faculty tutoring sessions."]))
    ]
    
    for row in sample_data:
        cursor.execute('''
            INSERT INTO students (
                student_name, student_id, gender, age, attendance, prev_marks,
                study_hours, assignment_score, internal_marks, class_test_marks,
                past_failures, extracurricular, internet_access, parental_edu,
                sleep_hours, predicted_score, predicted_grade, performance_level,
                recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)
    
    conn.commit()
    conn.close()
    return True
