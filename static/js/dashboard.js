/**
 * Student Performance Prediction System - Dashboard & Analytics Visualizations
 */

let charts = {
  barChart: null,
  pieChart: null,
  lineChart: null,
  scatterChart: null
};

let allStudents = [];
let currentFilter = 'All';
let currentSearch = '';

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();

  // Search input handler
  const searchInput = document.getElementById('searchStudent');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.toLowerCase();
      filterAndRenderTable();
    });
  }

  // Filter dropdown handler
  const filterSelect = document.getElementById('filterPerformance');
  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => {
      currentFilter = e.target.value;
      filterAndRenderTable();
    });
  }

  // Seed sample data button
  const seedBtn = document.getElementById('seedDataBtn');
  if (seedBtn) {
    seedBtn.addEventListener('click', async () => {
      if (!confirm('This will populate standard sample student records for demonstration. Continue?')) return;
      
      seedBtn.disabled = true;
      try {
        const res = await fetch('/api/seed', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          loadDashboardData();
        } else {
          showToast(data.error || 'Failed to seed records.', 'danger');
        }
      } catch (err) {
        showToast('Error connecting to server.', 'danger');
      } finally {
        seedBtn.disabled = false;
      }
    });
  }

  // Export CSV button
  const exportBtn = document.getElementById('exportCsvBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportTableToCsv);
  }
});

async function loadDashboardData() {
  try {
    const response = await fetch('/api/dashboard-data');
    const data = await response.json();

    if (data.success) {
      allStudents = data.students || [];
      updateKPIs(data.stats);
      renderCharts(data.charts);
      filterAndRenderTable();
    }
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

function updateKPIs(stats) {
  if (!stats) return;
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('kpi_total', stats.total_students || 0);
  setEl('kpi_excellent', stats.excellent_students || 0);
  setEl('kpi_average', stats.average_students || 0);
  setEl('kpi_at_risk', stats.at_risk_students || 0);
  setEl('kpi_avg_score', (stats.avg_performance || 0) + '%');
  setEl('kpi_avg_attendance', (stats.avg_attendance || 0) + '%');
}

function renderCharts(chartData) {
  if (!chartData) return;

  // 1. Bar Chart: Previous vs Predicted Scores
  const ctxBar = document.getElementById('barChart');
  if (ctxBar) {
    if (charts.barChart) charts.barChart.destroy();
    charts.barChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: chartData.bar.labels,
        datasets: [
          {
            label: 'Previous Marks (%)',
            data: chartData.bar.prev_marks,
            backgroundColor: 'rgba(148, 163, 184, 0.65)',
            borderColor: '#94a3b8',
            borderWidth: 1,
            borderRadius: 6
          },
          {
            label: 'Predicted Score (%)',
            data: chartData.bar.predicted_scores,
            backgroundColor: 'rgba(79, 70, 229, 0.85)',
            borderColor: '#4f46e5',
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          y: { beginAtZero: true, max: 100 }
        }
      }
    });
  }

  // 2. Doughnut / Pie Chart: Performance Categories
  const ctxPie = document.getElementById('pieChart');
  if (ctxPie) {
    if (charts.pieChart) charts.pieChart.destroy();
    charts.pieChart = new Chart(ctxPie, {
      type: 'doughnut',
      data: {
        labels: chartData.pie.labels,
        datasets: [{
          data: chartData.pie.data,
          backgroundColor: [
            '#10b981', // Outstanding
            '#3b82f6', // Excellent
            '#06b6d4', // Good
            '#f59e0b', // Average
            '#f97316', // Needs Improvement
            '#ef4444'  // At Risk
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' }
        },
        cutout: '65%'
      }
    });
  }

  // 3. Line Chart: Academic Score & Attendance Distribution Trends
  const ctxLine = document.getElementById('lineChart');
  if (ctxLine) {
    if (charts.lineChart) charts.lineChart.destroy();
    charts.lineChart = new Chart(ctxLine, {
      type: 'line',
      data: {
        labels: chartData.line.labels,
        datasets: [
          {
            label: 'Predicted Score (%)',
            data: chartData.line.scores,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#4f46e5'
          },
          {
            label: 'Attendance (%)',
            data: chartData.line.attendance,
            borderColor: '#06b6d4',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            tension: 0.35,
            pointRadius: 3,
            pointBackgroundColor: '#06b6d4'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' }
        },
        scales: {
          y: { beginAtZero: true, max: 100 }
        }
      }
    });
  }

  // 4. Scatter Chart: Attendance vs Performance
  const ctxScatter = document.getElementById('scatterChart');
  if (ctxScatter) {
    if (charts.scatterChart) charts.scatterChart.destroy();
    
    // Group scatter points by risk level
    const riskPoints = chartData.scatter.filter(p => p.category === 'Fail' || p.category === 'At Risk' || p.category === 'Needs Improvement');
    const safePoints = chartData.scatter.filter(p => p.category !== 'Fail' && p.category !== 'At Risk' && p.category !== 'Needs Improvement');

    charts.scatterChart = new Chart(ctxScatter, {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'Normal / High Performers',
            data: safePoints,
            backgroundColor: 'rgba(16, 185, 129, 0.75)',
            pointRadius: 6,
            pointHoverRadius: 8
          },
          {
            label: 'At Risk / Needs Support',
            data: riskPoints,
            backgroundColor: 'rgba(239, 68, 68, 0.85)',
            pointRadius: 7,
            pointHoverRadius: 9
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const item = ctx.raw;
                return `${item.name}: Attendance ${item.x}%, Predicted ${item.y}% (${item.category})`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'Attendance Rate (%)' },
            min: 20,
            max: 100
          },
          y: {
            title: { display: true, text: 'Predicted Score (%)' },
            min: 20,
            max: 100
          }
        }
      }
    });
  }
}

function filterAndRenderTable() {
  const tbody = document.getElementById('studentTableBody');
  const countEl = document.getElementById('tableRowCount');
  if (!tbody) return;

  const filtered = allStudents.filter(student => {
    const matchesSearch = 
      student.student_name.toLowerCase().includes(currentSearch) ||
      student.student_id.toLowerCase().includes(currentSearch);

    const matchesFilter = (currentFilter === 'All') || (student.performance_level === currentFilter);

    return matchesSearch && matchesFilter;
  });

  if (countEl) countEl.textContent = `${filtered.length} students found`;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-5 text-muted">
          <i class="fas fa-user-graduate fs-1 d-block mb-2 opacity-50"></i>
          No student records matching current filters.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(s => {
    const badgeClass = getBadgeClass(s.performance_level);
    return `
      <tr>
        <td>
          <div class="d-flex align-items-center gap-2">
            <div class="avatar-sm rounded-circle bg-primary-light text-primary d-flex align-items-center justify-content-center fw-bold" style="width: 32px; height: 32px; font-size: 0.8rem;">
              ${s.student_name.charAt(0)}
            </div>
            <div>
              <strong class="d-block text-dark">${s.student_name}</strong>
              <small class="text-muted">${s.gender}, ${s.age}y</small>
            </div>
          </div>
        </td>
        <td><span class="badge bg-light text-dark border">${s.student_id}</span></td>
        <td>
          <div class="d-flex align-items-center gap-2">
            <div class="progress flex-grow-1" style="height: 6px; width: 60px;">
              <div class="progress-bar ${s.attendance >= 75 ? 'bg-success' : 'bg-danger'}" style="width: ${s.attendance}%;"></div>
            </div>
            <small class="fw-semibold">${s.attendance}%</small>
          </div>
        </td>
        <td><strong>${s.prev_marks}%</strong></td>
        <td>
          <span class="fw-bold fs-6 text-primary">${s.predicted_score}%</span>
        </td>
        <td>
          <span class="badge bg-dark">${s.predicted_grade}</span>
        </td>
        <td>
          <span class="badge ${badgeClass}">${s.performance_level}</span>
        </td>
        <td>
          <div class="d-flex gap-1">
            <button class="btn btn-sm btn-outline-custom" onclick="viewStudentDetails(${s.id})" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteStudentRecord(${s.id})" title="Delete Record">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function getBadgeClass(level) {
  switch (level) {
    case 'Outstanding': return 'badge-outstanding';
    case 'Excellent': return 'badge-excellent';
    case 'Good': return 'badge-good';
    case 'Average': return 'badge-average';
    case 'Needs Improvement': return 'badge-improvement';
    case 'Fail':
    case 'At Risk': return 'badge-risk';
    default: return 'badge-secondary';
  }
}

async function deleteStudentRecord(id) {
  if (!confirm('Are you sure you want to delete this student record?')) return;

  try {
    const res = await fetch(`/api/students/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Student record deleted.', 'success');
      loadDashboardData();
    } else {
      showToast(data.error || 'Failed to delete.', 'danger');
    }
  } catch (err) {
    showToast('Error deleting record.', 'danger');
  }
}

function viewStudentDetails(id) {
  const student = allStudents.find(s => s.id === id);
  if (!student) return;

  const modalBody = document.getElementById('studentDetailModalBody');
  if (!modalBody) return;

  let recsHtml = '';
  if (student.recommendations && student.recommendations.length > 0) {
    recsHtml = student.recommendations.map(r => `
      <li class="mb-2">
        <strong>${r.title || 'Advice'}:</strong> ${r.text || r}
      </li>
    `).join('');
  } else {
    recsHtml = '<li>Consistent study habits recommended.</li>';
  }

  modalBody.innerHTML = `
    <div class="text-center mb-3">
      <h4 class="fw-bold mb-1">${student.student_name}</h4>
      <p class="text-muted small mb-2">Student ID: <strong>${student.student_id}</strong></p>
      <span class="badge ${getBadgeClass(student.performance_level)} px-3 py-2 fs-6">
        ${student.performance_level} &bull; Grade: ${student.predicted_grade} (${student.predicted_score}%)
      </span>
    </div>

    <div class="row g-3 my-3 p-3 bg-light rounded-3">
      <div class="col-6 col-md-4"><strong>Attendance:</strong> ${student.attendance}%</div>
      <div class="col-6 col-md-4"><strong>Prev Marks:</strong> ${student.prev_marks}%</div>
      <div class="col-6 col-md-4"><strong>Study Hours:</strong> ${student.study_hours} hrs/day</div>
      <div class="col-6 col-md-4"><strong>Internal Marks:</strong> ${student.internal_marks}/100</div>
      <div class="col-6 col-md-4"><strong>Class Tests:</strong> ${student.class_test_marks}/100</div>
      <div class="col-6 col-md-4"><strong>Past Failures:</strong> ${student.past_failures}</div>
      <div class="col-6 col-md-4"><strong>Sleep:</strong> ${student.sleep_hours} hrs</div>
      <div class="col-6 col-md-4"><strong>Internet:</strong> ${student.internet_access}</div>
      <div class="col-6 col-md-4"><strong>Parental Edu:</strong> ${student.parental_edu}</div>
    </div>

    <h6 class="fw-bold mt-3"><i class="fas fa-robot text-primary me-2"></i>AI Suggestions:</h6>
    <ul class="text-muted small ps-3">
      ${recsHtml}
    </ul>
  `;

  const modalEl = document.getElementById('studentDetailModal');
  if (modalEl) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

function exportTableToCsv() {
  if (allStudents.length === 0) {
    showToast('No student records to export.', 'warning');
    return;
  }

  const headers = ['ID', 'Name', 'Student_ID', 'Gender', 'Age', 'Attendance_%', 'Prev_Marks_%', 'Study_Hours', 'Assignment_Score', 'Internal_Marks', 'Past_Failures', 'Predicted_Score_%', 'Grade', 'Performance_Level'];
  const rows = allStudents.map(s => [
    s.id,
    `"${s.student_name}"`,
    `"${s.student_id}"`,
    s.gender,
    s.age,
    s.attendance,
    s.prev_marks,
    s.study_hours,
    s.assignment_score,
    s.internal_marks,
    s.past_failures,
    s.predicted_score,
    s.predicted_grade,
    `"${s.performance_level}"`
  ]);

  let csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `student_performance_records_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Student records exported to CSV successfully!', 'success');
}
