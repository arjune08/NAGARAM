/* UrbanPulse AI — Premium Chart.js Engine v3.0 (Tamil Nadu) */

/* ─── Global Design Tokens ─── */
const C = {
  cyan:    '#00d4ff',
  violet:  '#a78bfa',
  indigo:  '#818cf8',
  emerald: '#34d399',
  amber:   '#fbbf24',
  rose:    '#fb7185',
  blue:    '#60a5fa',
  muted:   '#3d5c7a',
  text:    '#7ba4c7',
  bg:      '#0a1628',
  bgCard:  '#060f1f',
};

/* Chart.js Defaults */
Chart.defaults.font.family  = "'Inter', sans-serif";
Chart.defaults.font.size    = 12;
Chart.defaults.color        = C.text;
Chart.defaults.borderColor  = 'rgba(0,212,255,0.06)';
Chart.defaults.animation.duration = 1000;
Chart.defaults.animation.easing   = 'easeOutCubic';

/* Shared tooltip style */
const TOOLTIP = {
  backgroundColor:  '#0d1c32',
  borderColor:      'rgba(0,212,255,0.18)',
  borderWidth:      1,
  padding:          { top: 10, right: 14, bottom: 10, left: 14 },
  titleColor:       '#e8f4ff',
  bodyColor:        C.text,
  cornerRadius:     10,
  displayColors:    true,
  boxWidth:         10,
  boxHeight:        10,
  boxPadding:       4,
};
Chart.defaults.plugins.tooltip = Object.assign(Chart.defaults.plugins.tooltip, TOOLTIP);
Chart.defaults.plugins.legend.labels.color   = C.text;
Chart.defaults.plugins.legend.labels.boxWidth = 10;
Chart.defaults.plugins.legend.labels.padding  = 14;
Chart.defaults.plugins.legend.labels.usePointStyle = true;

/* Gradient helper */
function gradFill(ctx, color1, color2, h = 200) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0,   color1);
  g.addColorStop(1,   color2);
  return g;
}

/* ─── City Health Trend ─── */
function initCityHealthChart(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];
  const data   = [64, 67, 65, 70, 73, 76, 79, 81.4];
  new Chart(el, {
    type: 'line',
    data: {
      labels: months,
      datasets: [{
        label: 'City Health Score',
        data,
        borderColor: C.cyan,
        backgroundColor: ctx => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 180);
          g.addColorStop(0, 'rgba(0,212,255,0.22)');
          g.addColorStop(1, 'rgba(0,212,255,0)');
          return g;
        },
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: C.cyan,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.45,
      }, {
        label: 'TN State Avg',
        data: [60, 61, 63, 63, 65, 67, 68, 69],
        borderColor: C.violet,
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [5, 4],
        pointRadius: 2,
        tension: 0.45,
        fill: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: { min: 55, max: 100, grid: { color: 'rgba(0,212,255,0.05)' }, ticks: { font: { size: 11 } } },
      },
      plugins: { legend: { display: true, position: 'top', align: 'end' } },
    },
  });
}

/* ─── Risk Donut ─── */
function initRiskDonutChart(id) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low', 'Minimal'],
      datasets: [{
        data: [4, 9, 16, 11, 4],
        backgroundColor: [C.rose, C.amber, C.cyan, C.blue, C.muted],
        borderWidth: 0,
        hoverOffset: 12,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: { position: 'right', labels: { font: { size: 11 }, padding: 10 } },
        tooltip: { callbacks: { label: c => ` ${c.label}: ${c.raw} assets` } },
      },
    },
  });
}

/* ─── Complaint Category Bar ─── */
function initComplaintBar(id, labels, data) {
  const el = document.getElementById(id);
  if (!el) return;
  const colors = [C.cyan, C.amber, C.rose, C.violet, C.emerald, C.blue];
  new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Reports',
        data,
        backgroundColor: labels.map((_, i) => colors[i % colors.length] + 'bb'),
        borderColor:     labels.map((_, i) => colors[i % colors.length]),
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(0,212,255,0.04)' }, beginAtZero: true },
      },
      plugins: { legend: { display: false } },
    },
  });
}

/* ─── TN Sustainability Radar ─── */
function initSustainabilityRadar(id) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: 'radar',
    data: {
      labels: ['Air Quality', 'Water Access', 'Mobility', 'Clean Energy', 'Green Cover', 'Waste Mgmt', 'Resilience'],
      datasets: [{
        label: 'TN Cities (2026)',
        data: [68, 72, 58, 61, 44, 77, 63],
        backgroundColor: 'rgba(0,212,255,0.10)',
        borderColor: C.cyan,
        borderWidth: 2,
        pointBackgroundColor: C.cyan,
        pointRadius: 4,
      }, {
        label: 'UN SDG 11 Target',
        data: [85, 85, 85, 85, 85, 85, 85],
        backgroundColor: 'rgba(52,211,153,0.05)',
        borderColor: C.emerald,
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointRadius: 0,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        r: {
          min: 0, max: 100,
          grid: { color: 'rgba(0,212,255,0.07)' },
          angleLines: { color: 'rgba(0,212,255,0.07)' },
          ticks: { stepSize: 25, font: { size: 10 }, color: C.muted },
          pointLabels: { font: { size: 11 }, color: C.text },
        },
      },
      plugins: { legend: { position: 'bottom' } },
    },
  });
}

/* ─── Resource Utilization Horizontal Bar ─── */
function initResourceChart(id, labels, alloc, avail) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Deployed', data: alloc, backgroundColor: C.cyan + 'bb', borderRadius: 4 },
        { label: 'Available', data: avail, backgroundColor: C.emerald + '88', borderRadius: 4 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: { grid: { color: 'rgba(0,212,255,0.04)' } },
        y: { grid: { display: false } },
      },
      plugins: { legend: { position: 'top', align: 'end' } },
    },
  });
}

/* ─── TN City SDG Comparison ─── */
function initCityCompareChart(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const cities = ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Trichy'];
  const scores = [78, 74, 69, 65, 71];
  new Chart(el, {
    type: 'bar',
    data: {
      labels: cities,
      datasets: [{
        label: 'SDG 11 Score',
        data: scores,
        backgroundColor: [C.cyan + 'cc', C.violet + 'cc', C.emerald + 'cc', C.amber + 'cc', C.blue + 'cc'],
        borderColor: [C.cyan, C.violet, C.emerald, C.amber, C.blue],
        borderWidth: 1.5,
        borderRadius: 8,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: { min: 50, max: 100, grid: { color: 'rgba(0,212,255,0.04)' }, ticks: { font: { size: 11 } } },
      },
      plugins: { legend: { display: false } },
    },
  });
}

/* ─── Sparkline (mini inline chart) ─── */
function initSparkline(id, data, color) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{ data, borderColor: color || C.cyan, borderWidth: 2, pointRadius: 0, fill: false, tension: 0.4 }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { x: { display: false }, y: { display: false } },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 800 },
    },
  });
}
