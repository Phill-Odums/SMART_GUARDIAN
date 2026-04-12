// Charts initialization for the dashboard
let mainChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // Only run if we are on the dashboard
    if (document.getElementById('stats-chart-container')) {
        fetchAndRenderStats();
        // Refresh EVERYTHING every 15 seconds (to match the user's previous interval for cards)
        setInterval(fetchAndRenderStats, 15000);
    }
});

async function fetchAndRenderStats() {
    try {
        const response = await fetch('/get_stats');
        const data = await response.json();

        // Update summary cards (moved from inline script in dashboard.html for efficiency)
        if (data.summary) {
            updateSummaryCards(data.summary);
        }

        // Render Chart
        renderMainChart(data);

    } catch (error) {
        console.error("Failed to load statistics:", error);
    }
}

function updateSummaryCards(s) {
    // Active cameras
    const camEl = document.getElementById('stat-active-cameras');
    if (camEl) animateCount(camEl, s.active_cameras ?? 0);

    // Total detections
    const detEl = document.getElementById('stat-total-detections');
    if (detEl) animateCount(detEl, s.total_detections ?? 0);

    // Alerts triggered
    const altEl = document.getElementById('stat-alerts-triggered');
    if (altEl) animateCount(altEl, s.alerts_triggered ?? 0);

    // Flash red icon if there are alerts
    const iconBox = document.getElementById('stat-alerts-icon');
    if (iconBox) {
        if ((s.alerts_triggered ?? 0) > 0) {
            iconBox.classList.add('animate-pulse');
        } else {
            iconBox.classList.remove('animate-pulse');
        }
    }

    // Uptime
    const uptimeEl = document.getElementById('stat-uptime');
    if (uptimeEl) uptimeEl.textContent = s.uptime ?? '--';
}

function animateCount(el, target, suffix = '') {
    const duration = 600;
    const start = performance.now();
    const from = parseInt(el.textContent.replace(/[^0-9]/g, '')) || 0;
    
    function step(now) {
        const t = Math.min((now - start) / duration, 1);
        const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        el.textContent = Math.round(from + (target - from) * ease).toLocaleString() + suffix;
        if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

function renderMainChart(data) {
    const container = document.getElementById('stats-chart-container');
    if (!container) return;

    // Remove existing canvas if it exists to avoid duplication
    let canvas = document.getElementById('mainChart');
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'mainChart';
        container.appendChild(canvas);
    }

    const ctx = canvas.getContext('2d');

    // Setup Chart.js global defaults for our dark glass theme
    Chart.defaults.color = '#94a3b8'; // text-slate-400
    Chart.defaults.font.family = "'Outfit', sans-serif";

    if (mainChart) {
        mainChart.destroy();
    }

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: data.datasets || []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { 
                        boxWidth: 12, 
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 25, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: true,
                    intersect: false,
                    mode: 'index'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.05)', 
                        drawBorder: false 
                    },
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    grid: { 
                        display: false, 
                        drawBorder: false 
                    }
                }
            },
            interaction: { 
                mode: 'index', 
                intersect: false 
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 6
                }
            }
        }
    });
}
