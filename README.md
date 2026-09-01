# Student Performance Prediction System 🎓🤖

A modern, responsive full-stack web application powered by **Machine Learning** and **Python Flask** that predicts student academic performance based on academic, behavioral, and attendance-related factors.

---

## 🌟 Key Features

1. **Real-Time AI Performance Prediction**:
   - Predicts final percentage score, letter grade (**O**, **A+**, **A**, **B**, **C**, **F**), and standardized academic category.
   - Evaluates 15 multidimensional parameters including attendance, previous semester marks, study hours, internal exams, assignments, past failures, sleep hours, parental education, and internet access.
2. **Personalized AI Action Guidance**:
   - Generates customized study advice based on detected vulnerabilities (e.g. low attendance, sleep deprivation, backlog risk).
3. **Interactive Analytics Dashboard**:
   - Dynamic KPI summary cards (Total Students, Top Achievers, Average, At-Risk, Average Performance).
   - **Chart.js Visualizations**:
     - **Bar Chart**: Previous Marks vs. Predicted Score Comparison
     - **Doughnut / Pie Chart**: Academic Category Distribution
     - **Line / Area Chart**: Academic Progress & Score Trajectory
     - **Scatter Plot**: Attendance (%) vs. Predicted Performance (%) with risk quadrant
4. **Student Records Table**:
   - Live search by Name or Student ID.
   - Filtering by performance level (Outstanding, Excellent, Good, Average, Needs Improvement, At Risk).
   - Detailed evaluation modal.
   - 1-Click Export to CSV and Print-Ready Student Report Cards.
5. **Multi-Model Machine Learning Ensemble**:
   - Trained on **Random Forest Regressor**, **Decision Tree Regressor**, and **Linear Regression**.
   - Persistence and automated selection of the best-performing model.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed

### 2. Installation
Open a terminal in the project directory:

```bash
# Install required dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📊 Grading & Classification Scale

| Percentage Range | Grade | Performance Level | Status |
| :--- | :---: | :--- | :--- |
| **90% – 100%** | **O** | Outstanding | Top Tier Academic Performer |
| **80% – 89%** | **A+** | Excellent | Strong Academic Performer |
| **70% – 79%** | **A** | Good | Consistent Performer |
| **60% – 69%** | **B** | Average | Moderate Academic Performance |
| **40% – 59%** | **C** | Needs Improvement | Attention Required |
| **Below 40%** | **Fail** | Fail | Critical Academic Alert |

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Modern Glassmorphism & Custom Design System), JavaScript (ES6+), Bootstrap 5.3, Font Awesome 6
- **Backend**: Python 3.12, Flask, Jinja2 Templates, RESTful JSON Endpoints
- **Machine Learning**: Scikit-Learn (Random Forest, Decision Trees, Linear Regression), Pandas, NumPy, Joblib
- **Visualization**: Chart.js 4.4
- **Database**: SQLite3 (`student_records.db`)

---

## 📂 Project Structure

```
student performance web/
├── app.py                     # Flask web server and API endpoints
├── ml_model.py                # Machine learning pipeline, dataset generation & inference
├── database.py                # SQLite database helper and operations
├── requirements.txt           # Python dependencies
├── test_app.py                # Automated test suite
├── models/
│   ├── best_model.joblib      # Serialized best ML model
│   ├── scaler.joblib          # StandardScaler object
│   └── metrics.json           # Model benchmarks & feature importances
├── static/
│   ├── css/
│   │   └── style.css          # Custom modern stylesheet
│   └── js/
│       ├── main.js            # General UI interactions & toasts
│       ├── predict.js         # Form validation & prediction handler
│       └── dashboard.js       # Chart.js visualizations & student table
└── templates/
    ├── base.html              # Shared layout template
    ├── index.html             # Landing page with hero & workflow
    ├── predict.html           # Prediction form & dynamic result card
    ├── dashboard.html         # Analytics dashboard with charts & table
    ├── how_it_works.html      # Technical workflow explanation
    ├── about.html             # Project details and tech stack
    └── contact.html           # Inquiries & FAQ accordion
```

---

## 🧪 Testing

To run the automated verification test suite:

```bash
python test_app.py
```
