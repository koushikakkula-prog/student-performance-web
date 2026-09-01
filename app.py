import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import database
import ml_model

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'student-performance-ai-secret-key-2026')

# Initialize DB and ensure ML models are trained
with app.app_context():
    database.init_db()
    database.seed_sample_students(force=False)
    try:
        ml_model.get_model_and_scaler()
    except Exception as e:
        print(f"Model initialization deferred or error: {e}")

@app.route('/')
def index():
    stats = database.get_dashboard_stats()
    metrics_path = ml_model.METRICS_PATH
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            try:
                metrics = json.load(f)
            except Exception:
                metrics = {}
    return render_template('index.html', stats=stats, metrics=metrics)

@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            result = ml_model.predict_student(form_data)
            record_id = database.add_student_record(result)
            result['record_id'] = record_id
            return render_template('predict.html', result=result, form_data=form_data)
        except Exception as e:
            flash(f"Error during prediction: {str(e)}", "danger")
            return render_template('predict.html', form_data=form_data)
            
    return render_template('predict.html', result=None)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            data = request.form.to_dict()
            
        if not data:
            return jsonify({'success': False, 'error': 'No input data provided'}), 400
            
        result = ml_model.predict_student(data)
        record_id = database.add_student_record(result)
        result['record_id'] = record_id
        result['success'] = True
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    stats = database.get_dashboard_stats()
    students = database.get_all_students(limit=100)
    return render_template('dashboard.html', stats=stats, students=students)

@app.route('/api/dashboard-data')
def api_dashboard_data():
    try:
        stats = database.get_dashboard_stats()
        students = database.get_all_students(limit=500)
        
        # Prepare datasets for Chart.js
        # 1. Comparison of Previous vs Predicted Scores (Top 10 recent)
        recent_10 = list(reversed(students[:10]))
        bar_chart = {
            'labels': [s['student_name'].split()[0] for s in recent_10],
            'prev_marks': [s['prev_marks'] for s in recent_10],
            'predicted_scores': [s['predicted_score'] for s in recent_10]
        }
        
        # 2. Performance Category distribution
        pie_chart = {
            'labels': list(stats['categories'].keys()),
            'data': list(stats['categories'].values())
        }
        
        # 3. Academic progress / distribution (binned or sequential scores)
        line_chart = {
            'labels': [f"#{i+1} {s['student_id']}" for i, s in enumerate(recent_10)],
            'scores': [s['predicted_score'] for s in recent_10],
            'attendance': [s['attendance'] for s in recent_10]
        }
        
        # 4. Attendance vs Performance scatter points
        scatter_chart = [
            {
                'x': s['attendance'],
                'y': s['predicted_score'],
                'name': s['student_name'],
                'category': s['performance_level']
            }
            for s in students
        ]
        
        return jsonify({
            'success': True,
            'stats': stats,
            'students': students,
            'charts': {
                'bar': bar_chart,
                'pie': pie_chart,
                'line': line_chart,
                'scatter': scatter_chart
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/students/<int:record_id>', methods=['GET'])
def api_get_student(record_id):
    student = database.get_student_by_id(record_id)
    if student:
        return jsonify({'success': True, 'student': student})
    return jsonify({'success': False, 'error': 'Student not found'}), 404

@app.route('/api/students/<int:record_id>', methods=['DELETE'])
def api_delete_student(record_id):
    deleted = database.delete_student_record(record_id)
    if deleted:
        return jsonify({'success': True, 'message': 'Record deleted successfully'})
    return jsonify({'success': False, 'error': 'Record not found'}), 404

@app.route('/api/seed', methods=['POST'])
def api_seed():
    try:
        database.seed_sample_students(force=True)
        return jsonify({'success': True, 'message': 'Demo student records populated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/model-info')
def api_model_info():
    try:
        if not os.path.exists(ml_model.METRICS_PATH):
            metrics = ml_model.train_and_save_models()
        else:
            with open(ml_model.METRICS_PATH, 'r') as f:
                metrics = json.load(f)
        return jsonify({'success': True, 'metrics': metrics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/about')
def about():
    metrics = {}
    if os.path.exists(ml_model.METRICS_PATH):
        with open(ml_model.METRICS_PATH, 'r') as f:
            try:
                metrics = json.load(f)
            except Exception:
                metrics = {}
    return render_template('about.html', metrics=metrics)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Thank you! Your message has been received. Our team will get back to you shortly.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json(force=True, silent=True) or request.form.to_dict()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()
    
    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'Please fill all required fields.'}), 400
        
    return jsonify({
        'success': True,
        'message': f"Thank you {name}! Your message has been submitted successfully."
    })

if __name__ == '__main__':
    print("Starting Student Performance Prediction System on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
