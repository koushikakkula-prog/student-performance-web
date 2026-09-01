import json
from app import app

def run_tests():
    client = app.test_client()

    # 1. Test GET /
    res = client.get('/')
    assert res.status_code == 200, f"Index failed: {res.status_code}"
    print("[OK] GET / (Home page) OK")

    # 2. Test GET /predict
    res = client.get('/predict')
    assert res.status_code == 200, f"Predict page failed: {res.status_code}"
    print("[OK] GET /predict (Prediction form) OK")

    # 3. Test POST /api/predict
    sample = {
        'student_name': 'Test API Student',
        'student_id': 'STU-API-01',
        'gender': 'Male',
        'age': 20,
        'attendance': 90,
        'prev_marks': 85,
        'study_hours': 5,
        'assignment_score': 90,
        'internal_marks': 88,
        'class_test_marks': 85,
        'past_failures': 0,
        'extracurricular': 'Yes',
        'internet_access': 'Yes',
        'parental_edu': "Master's",
        'sleep_hours': 7
    }
    res = client.post('/api/predict', json=sample)
    assert res.status_code == 200, f"API Predict failed: {res.status_code}"
    data = json.loads(res.data)
    assert data['success'] is True
    assert 'predicted_score' in data
    assert 'predicted_grade' in data
    assert 'performance_level' in data
    print(f"[OK] POST /api/predict OK (Predicted: {data['predicted_score']}%, Grade: {data['predicted_grade']}, Level: {data['performance_level']})")

    # 4. Test GET /dashboard
    res = client.get('/dashboard')
    assert res.status_code == 200, f"Dashboard page failed: {res.status_code}"
    print("[OK] GET /dashboard (Dashboard page) OK")

    # 5. Test GET /api/dashboard-data
    res = client.get('/api/dashboard-data')
    assert res.status_code == 200, f"Dashboard data API failed: {res.status_code}"
    dash_data = json.loads(res.data)
    assert dash_data['success'] is True
    assert 'stats' in dash_data
    assert 'charts' in dash_data
    print(f"[OK] GET /api/dashboard-data OK ({dash_data['stats']['total_students']} students in dataset)")

    # 6. Test Static / Information Routes
    for route in ['/how-it-works', '/about', '/contact']:
        res = client.get(route)
        assert res.status_code == 200, f"{route} failed: {res.status_code}"
        print(f"[OK] GET {route} OK")

    # 7. Test Contact API
    res = client.post('/api/contact', json={'name': 'Aarav', 'email': 'aarav@test.com', 'message': 'Hello!'})
    assert res.status_code == 200
    print("[OK] POST /api/contact OK")

    print("\n==========================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS RATE!")
    print("==========================================")

if __name__ == '__main__':
    run_tests()
