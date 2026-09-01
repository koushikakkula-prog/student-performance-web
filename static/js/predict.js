/**
 * Student Performance Prediction System - Prediction Form & Result Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictionForm');
  const resultContainer = document.getElementById('resultContainer');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const loadingText = document.getElementById('loadingText');

  // 1. Sync Range Sliders with Value Display Badges
  const sliders = [
    { slider: 'attendance', display: 'val_attendance', suffix: '%' },
    { slider: 'prev_marks', display: 'val_prev_marks', suffix: '%' },
    { slider: 'study_hours', display: 'val_study_hours', suffix: ' hrs' },
    { slider: 'assignment_score', display: 'val_assignment_score', suffix: '/100' },
    { slider: 'internal_marks', display: 'val_internal_marks', suffix: '/100' },
    { slider: 'class_test_marks', display: 'val_class_test_marks', suffix: '/100' },
    { slider: 'sleep_hours', display: 'val_sleep_hours', suffix: ' hrs' },
    { slider: 'age', display: 'val_age', suffix: ' yrs' }
  ];

  sliders.forEach(item => {
    const el = document.getElementById(item.slider);
    const disp = document.getElementById(item.display);
    if (el && disp) {
      el.addEventListener('input', (e) => {
        disp.textContent = e.target.value + item.suffix;
      });
    }
  });

  // 2. Preset Profile Loaders for Quick 1-Click Testing
  const presets = {
    achiever: {
      student_name: "Aarav Sharma",
      student_id: "STU-8821",
      gender: "Male",
      age: 20,
      attendance: 94,
      prev_marks: 92,
      study_hours: 6.5,
      assignment_score: 95,
      internal_marks: 92,
      class_test_marks: 94,
      past_failures: 0,
      extracurricular: "Yes",
      internet_access: "Yes",
      parental_edu: "Master's",
      sleep_hours: 7.5
    },
    average: {
      student_name: "Rahul Verma",
      student_id: "STU-5420",
      gender: "Male",
      age: 21,
      attendance: 72,
      prev_marks: 68,
      study_hours: 3.0,
      assignment_score: 70,
      internal_marks: 65,
      class_test_marks: 68,
      past_failures: 0,
      extracurricular: "No",
      internet_access: "Yes",
      parental_edu: "Bachelor's",
      sleep_hours: 6.5
    },
    risk: {
      student_name: "Vikram Mehta",
      student_id: "STU-2091",
      gender: "Male",
      age: 22,
      attendance: 35,
      prev_marks: 32,
      study_hours: 0.8,
      assignment_score: 35,
      internal_marks: 28,
      class_test_marks: 30,
      past_failures: 3,
      extracurricular: "No",
      internet_access: "No",
      parental_edu: "High School",
      sleep_hours: 4.5
    }
  };

  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.getAttribute('data-preset');
      const data = presets[type];
      if (!data) return;

      for (const [key, val] of Object.entries(data)) {
        const input = document.getElementById(key);
        if (input) {
          input.value = val;
          input.dispatchEvent(new Event('input'));
        }
      }
      showToast(`Loaded "${btn.textContent.trim()}" preset values!`, 'info');
    });
  });

  // 3. Handle Form Submission via AJAX with Animated Multi-step Loading
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      // Collect form values
      const formData = new FormData(form);
      const payload = Object.fromEntries(formData.entries());

      // Show AI loading overlay with stepped status updates
      if (loadingOverlay) {
        loadingOverlay.classList.add('active');
      }

      const steps = [
        "Normalizing student academic indicators...",
        "Executing Random Forest & Ensemble ML Models...",
        "Calculating grading boundaries & risk scores...",
        "Generating personalized AI study suggestions..."
      ];

      for (let i = 0; i < steps.length; i++) {
        if (loadingText) loadingText.textContent = steps[i];
        await new Promise(r => setTimeout(r, 350));
      }

      try {
        const response = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
          renderResultCard(data);
          showToast(`Performance prediction complete for ${data.student_name}!`, 'success');
          // Smooth scroll to results
          setTimeout(() => {
            const resEl = document.getElementById('resultCardWrapper');
            if (resEl) {
              resEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }, 200);
        } else {
          showToast(data.error || 'Prediction failed. Please check your inputs.', 'danger');
        }
      } catch (err) {
        showToast('Server connection error. Please try again.', 'danger');
      } finally {
        if (loadingOverlay) {
          loadingOverlay.classList.remove('active');
        }
      }
    });
  }

  // 4. Render Dynamic Result Card
  function renderResultCard(res) {
    if (!resultContainer) return;

    let suggestionsHtml = '';
    if (res.recommendations && res.recommendations.length > 0) {
      res.recommendations.forEach(item => {
        suggestionsHtml += `
          <div class="suggestion-card">
            <div class="suggestion-icon ${item.type}">
              <i class="fas ${item.icon}"></i>
            </div>
            <div>
              <strong class="d-block mb-1 text-dark">${item.title}</strong>
              <p class="mb-0 text-muted small">${item.text}</p>
            </div>
          </div>
        `;
      });
    }

    const html = `
      <div id="resultCardWrapper" class="result-card mt-4">
        <div class="row align-items-center mb-4">
          <div class="col-md-7">
            <span class="badge ${res.badge_class} mb-2">${res.performance_level}</span>
            <h3 class="fw-bold mb-1">${res.student_name}</h3>
            <p class="text-muted mb-0 small">
              <i class="fas fa-id-badge me-1"></i> Student ID: <strong>${res.student_id}</strong> &bull; 
              <i class="fas fa-clock me-1"></i> Evaluated: Just now
            </p>
          </div>
          <div class="col-md-5 text-md-end mt-3 mt-md-0">
            <button class="btn btn-outline-custom btn-sm me-2" onclick="window.print()">
              <i class="fas fa-print me-1"></i> Print Report
            </button>
            <a href="/dashboard" class="btn btn-primary-custom btn-sm">
              <i class="fas fa-chart-pie me-1"></i> View Dashboard
            </a>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- Circular Progress Meter -->
          <div class="col-md-4 text-center">
            <div class="score-circle" style="--percent: ${res.predicted_score};">
              <div class="score-circle-inner">
                <div class="score-number">${res.predicted_score}%</div>
                <div class="score-unit">Predicted Score</div>
              </div>
            </div>
            <div class="d-flex justify-content-center gap-2">
              <span class="badge bg-dark px-3 py-2">Grade: <strong class="fs-6">${res.predicted_grade}</strong></span>
              <span class="badge ${res.badge_class} px-3 py-2">${res.performance_level}</span>
            </div>
          </div>

          <!-- Academic Factors Breakdown -->
          <div class="col-md-8">
            <h6 class="fw-bold text-muted mb-3 text-uppercase small">Key Performance Indicators</h6>
            
            <div class="mb-3">
              <div class="d-flex justify-content-between small fw-bold mb-1">
                <span>Predicted Performance</span>
                <span>${res.predicted_score}%</span>
              </div>
              <div class="progress" style="height: 10px; border-radius: 6px;">
                <div class="progress-bar bg-primary" role="progressbar" style="width: ${res.predicted_score}%;"></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between small fw-bold mb-1">
                <span>Attendance Rate</span>
                <span>${res.attendance}%</span>
              </div>
              <div class="progress" style="height: 10px; border-radius: 6px;">
                <div class="progress-bar ${res.attendance >= 75 ? 'bg-success' : 'bg-warning'}" role="progressbar" style="width: ${res.attendance}%;"></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between small fw-bold mb-1">
                <span>Previous Semester Score</span>
                <span>${res.prev_marks}%</span>
              </div>
              <div class="progress" style="height: 10px; border-radius: 6px;">
                <div class="progress-bar bg-info" role="progressbar" style="width: ${res.prev_marks}%;"></div>
              </div>
            </div>

            <div class="row g-2 mt-2 pt-2 border-top small text-muted">
              <div class="col-6 col-sm-3">
                <i class="fas fa-book-open text-primary me-1"></i> Study: <strong>${res.study_hours}h/day</strong>
              </div>
              <div class="col-6 col-sm-3">
                <i class="fas fa-file-alt text-info me-1"></i> Assign: <strong>${res.assignment_score}</strong>
              </div>
              <div class="col-6 col-sm-3">
                <i class="fas fa-pen-fancy text-secondary me-1"></i> Internal: <strong>${res.internal_marks}</strong>
              </div>
              <div class="col-6 col-sm-3">
                <i class="fas fa-triangle-exclamation text-danger me-1"></i> Failures: <strong>${res.past_failures}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Recommendations Section -->
        <div class="border-top pt-4">
          <h5 class="fw-bold mb-3 d-flex align-items-center gap-2">
            <i class="fas fa-robot text-primary"></i> Personalized AI Academic Guidance
          </h5>
          <div class="suggestions-list">
            ${suggestionsHtml}
          </div>
        </div>
      </div>
    `;

    resultContainer.innerHTML = html;
  }
});
