// Charts initialization for the dashboard
document.addEventListener('DOMContentLoaded', async () => {

    // Add Chart.js to the page dynamically if we are on the dashboard
    if (document.getElementById('stats-chart-container')) {
        await injectChartJS();
        fetchAndRenderStats();
    }
});

function injectChartJS() {
    return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = "https://cdn.jsdelivr.net/npm/chart.js";
        script.onload = resolve;
        document.head.appendChild(script);
    });
}

async function fetchAndRenderStats() {
    try {
        const response = await fetch('/get_stats');
        const data = await response.json();

        // Update summary cards if data exists
        if (data.summary) {
            // This assumes IDs or classes would be added to the HTML blocks
            console.log("Stats fetched:", data.summary);
        }

        // Render Chart
        renderMainChart(data);

    } catch (error) {
        console.error("Failed to load statistics:", error);
    }
}

function renderMainChart(data) {
    const container = document.getElementById('stats-chart-container');
    if (!container) return;

    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'mainChart';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    // Setup Chart.js global defaults for our dark glass theme
    Chart.defaults.color = '#94a3b8'; // text-slate-400
    Chart.defaults.font.family = "'Outfit', sans-serif";

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { boxWidth: 12, usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 25, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false }
                },
                x: {
                    grid: { display: false, drawBorder: false }
                }
            },
            interaction: { mode: 'index', intersect: false }
        }
    });
}
