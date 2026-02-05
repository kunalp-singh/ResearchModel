let trafficChart;

// Initialize Chart.js
function initChart() {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Packet Size (bytes)',
                data: [],
                borderColor: '#00f3ff',
                backgroundColor: 'rgba(0, 243, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8892b0' }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { labels: { color: '#e0e0e0' } }
            },
            animation: false
        }
    });
}

// Tab Switching Logic
function openTab(tabName) {
    // Hide all content
    document.querySelectorAll('.content-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Deactivate all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show target content and activate tab
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

// DDoS Monitoring Logic
function startMonitoring() {
    const resultDiv = document.getElementById('ddosResult');
    const statusText = document.getElementById('monitorStatus');
    const btn = document.getElementById('startMonitorBtn');

    resultDiv.innerHTML = '';
    statusText.innerText = "Scanning Network Traffic...";
    statusText.style.color = "#00f3ff";
    btn.disabled = true;
    btn.style.opacity = "0.5";

    // Simulate live chart updates (since backend doesn't stream yet)
    let chartInterval = setInterval(() => {
        const time = new Date().toLocaleTimeString();
        const randomPacketSize = Math.floor(Math.random() * 1500);

        if (trafficChart.data.labels.length > 20) {
            trafficChart.data.labels.shift();
            trafficChart.data.datasets[0].data.shift();
        }

        trafficChart.data.labels.push(time);
        trafficChart.data.datasets[0].data.push(randomPacketSize);
        trafficChart.update();
    }, 1000);

    fetch('/monitor', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            clearInterval(chartInterval);
            btn.disabled = false;
            btn.style.opacity = "1";
            statusText.innerText = "Scan Complete";
            statusText.style.color = "#00ff88";

            if (data.pred > 0.5) {
                resultDiv.innerHTML = `
                    <div class="alert red">
                        <h3>⚠️ DDoS ATTACK DETECTED</h3>
                        <p>Confidence Level: ${(data.pred * 100).toFixed(1)}%</p>
                        <p>Immediate Action Recommended!</p>
                    </div>`;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert green">
                        <h3>✅ Normal Traffic Detected</h3>
                        <p>Confidence Level: ${((1 - data.pred) * 100).toFixed(1)}%</p>
                        <p>Network is safe.</p>
                    </div>`;
            }
        })
        .catch(err => {
            clearInterval(chartInterval);
            btn.disabled = false;
            btn.style.opacity = "1";
            statusText.innerText = "Error";
            statusText.style.color = "#ff3333";
            resultDiv.innerHTML = `<div class="alert red">Error: ${err.message}</div>`;
        });
}

// Phishing Checker Logic
function checkPhishing() {
    const url = document.getElementById('urlInput').value;
    const resultDiv = document.getElementById('phishingResult');

    if (!url) {
        resultDiv.innerHTML = '<div class="alert red">Please enter a URL</div>';
        return;
    }

    resultDiv.innerHTML = '<p style="color:var(--primary-color)">Analyzing URL structure...</p>';

    fetch('/phishing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    })
        .then(r => r.json())
        .then(data => {
            if (data.pred > 0.5) {
                resultDiv.innerHTML = `
                <div class="alert red">
                    <h3>🚫 DANGEROUS PHISHING SITE</h3>
                    <p>Confidence Level: ${(data.pred * 100).toFixed(1)}%</p>
                    <p>Do not visit this link.</p>
                </div>`;
            } else {
                resultDiv.innerHTML = `
                <div class="alert green">
                    <h3>✅ Safe Website</h3>
                    <p>Confidence Level: ${((1 - data.pred) * 100).toFixed(1)}%</p>
                    <p>URL structure looks legitimate.</p>
                </div>`;
            }
        })
        .catch(err => {
            resultDiv.innerHTML = `<div class="alert red">Error: ${err.message}</div>`;
        });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initChart();
});
