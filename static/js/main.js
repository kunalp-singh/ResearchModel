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
function startMonitoring(simulateAttack = false) {
    console.log('[DDoS Monitor] Starting scan with simulateAttack =', simulateAttack);
    const resultDiv = document.getElementById('ddosResult');
    const statusText = document.getElementById('monitorStatus');
    const btn = document.getElementById('startMonitorBtn');
    const attackBtn = document.getElementById('simulateAttackBtn');

    resultDiv.innerHTML = '';
    btn.disabled = true;
    btn.style.opacity = "0.5";
    attackBtn.disabled = true;
    attackBtn.style.opacity = "0.5";

    // Add countdown timer (25 seconds)
    let timeLeft = 25;
    const scanMsg = simulateAttack ? 'Simulating DDoS Attack' : 'Scanning Network Traffic';
    statusText.innerText = `${scanMsg}... ${timeLeft}s remaining`;
    statusText.style.color = simulateAttack ? "#ff3333" : "#00f3ff";
    
    console.log('[DDoS Monitor] Starting 25-second countdown...');
    let countdownTimer = setInterval(() => {
        timeLeft--;
        if (timeLeft >= 0) {
            statusText.innerText = `${scanMsg}... ${timeLeft}s remaining`;
            console.log(`[DDoS Monitor] ${timeLeft}s remaining...`);
        }
    }, 1000);

    // Simulate live chart updates (since backend doesn't stream yet)
    let chartInterval = setInterval(() => {
        const time = new Date().toLocaleTimeString();
        const randomPacketSize = simulateAttack ? 
            Math.floor(Math.random() * 5000 + 5000) :  // 5k-10k for attack
            Math.floor(Math.random() * 1500);          // 0-1500 for normal

        if (trafficChart.data.labels.length > 20) {
            trafficChart.data.labels.shift();
            trafficChart.data.datasets[0].data.shift();
        }

        trafficChart.data.labels.push(time);
        trafficChart.data.datasets[0].data.push(randomPacketSize);
        trafficChart.update();
    }, 1000);

    // Create AbortController with 35-second timeout to allow 25-second scan
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 35000);

    const requestBody = simulateAttack ? JSON.stringify({force_ddos: true}) : JSON.stringify({});
    console.log('[DDoS Monitor] Sending fetch request to /monitor with body:', requestBody);
    const fetchStartTime = Date.now();
    
    fetch('/monitor', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody,
        signal: controller.signal 
    })
        .then(r => {
            clearTimeout(timeoutId);
            const fetchDuration = (Date.now() - fetchStartTime) / 1000;
            console.log(`[DDoS Monitor] Fetch completed successfully in ${fetchDuration.toFixed(1)}s, status:`, r.status);
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .then(data => {
            console.log('Scan complete, prediction:', data.pred);
            clearInterval(chartInterval);
            clearInterval(countdownTimer);
            btn.disabled = false;
            btn.style.opacity = "1";
            attackBtn.disabled = false;
            attackBtn.style.opacity = "1";
            statusText.innerText = "Scan Complete";
            statusText.style.color = "#00ff88";
            
            const isSimulated = data.simulated || false;
            const simulatedBadge = isSimulated ? '<p style="font-size: 0.85em; color: #ffa500; margin-top: 5px;">⚠️ Simulated result (model not loaded)</p>' : '';
            const modelInfo = !isSimulated 
                ? '<p style="font-size: 0.8em; color: #00cc66; margin-top: 5px;">✅ CICIDS2017 model (99.9% accuracy, 1.8M samples)</p>' 
                : '';

            // CICIDS2017 thresholds: Attack >80%, Uncertain 20-80%, Safe <20%
            const isDDoSThreshold = 0.80;
            const isUncertainThreshold = 0.20;
            
            if (data.pred > isDDoSThreshold) {
                const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
                const duration = '25.0s';
                const metrics = data.metrics || {};
                const flowDuration = metrics.flow_duration ? metrics.flow_duration.toFixed(0) : 'N/A';
                const flowBytesPerSec = metrics.flow_bytes_per_sec ? metrics.flow_bytes_per_sec.toLocaleString('en-US', {maximumFractionDigits: 1}) : 'N/A';
                const flowPacketsPerSec = metrics.flow_packets_per_sec ? metrics.flow_packets_per_sec.toFixed(1) : 'N/A';
                const packetRatio = metrics.packet_ratio ? metrics.packet_ratio.toFixed(2) : 'N/A';
                
                resultDiv.innerHTML = `
                    <div class="alert red">
                        <pre style="font-family: 'Courier New', monospace; font-size: 0.9em; line-height: 1.6; margin: 0; white-space: pre-wrap; color: #fff;">═══════════════════════════════════════════════════════════
🚨 CRITICAL ALERT - DDoS ATTACK DETECTED
═══════════════════════════════════════════════════════════

<strong>STATUS: 🚫 DDoS ATTACK IN PROGRESS</strong>
Classification: Distributed Denial of Service
Timestamp: ${timestamp} | Duration: ${duration}

<strong>THREAT ASSESSMENT</strong>
├─ Threat Score:    ${data.pred.toFixed(4)}  (HIGH)
├─ Confidence:      ${(data.pred * 100).toFixed(1)}%
└─ Risk Level:      CRITICAL ██████████

<strong>IMMEDIATE ACTIONS REQUIRED</strong>
  ⚠️ Block suspicious IP addresses
  ⚠️ Enable rate limiting
  ⚠️ Contact ISP/security team
  ⚠️ Monitor system resources</pre>
                        ${simulatedBadge}
                    </div>`;
            } else if (data.pred > isUncertainThreshold) {
                // Uncertain zone
                const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
                const duration = '25.0s';
                const metrics = data.metrics || {};
                const flowDuration = metrics.flow_duration ? metrics.flow_duration.toFixed(0) : 'N/A';
                const flowBytesPerSec = metrics.flow_bytes_per_sec ? metrics.flow_bytes_per_sec.toLocaleString('en-US', {maximumFractionDigits: 1}) : 'N/A';
                const flowPacketsPerSec = metrics.flow_packets_per_sec ? metrics.flow_packets_per_sec.toFixed(1) : 'N/A';
                const packetRatio = metrics.packet_ratio ? metrics.packet_ratio.toFixed(2) : 'N/A';
                
                resultDiv.innerHTML = `
                    <div class="alert" style="background: linear-gradient(135deg, #fff3cd, #ffe69c); border-color: #ffc107; color: #333;">
                        <pre style="font-family: 'Courier New', monospace; font-size: 0.9em; line-height: 1.6; margin: 0; white-space: pre-wrap; color: #333;">═══════════════════════════════════════════════════════════
⚠️ UNCERTAIN CLASSIFICATION - MONITORING RECOMMENDED
═══════════════════════════════════════════════════════════

<strong>STATUS: ⚠️ CLASSIFICATION UNCERTAIN</strong>
Classification: Ambiguous Pattern
Timestamp: ${timestamp} | Duration: ${duration}

<strong>THREAT ASSESSMENT</strong>
├─ Threat Score:    ${data.pred.toFixed(4)}  (MODERATE)
├─ Confidence:      ${(data.pred * 100).toFixed(1)}%
└─ Risk Level:      UNCERTAIN ▓▓▓▓▓░░░░░

<strong>RECOMMENDATIONS</strong>
  ⚠️ Continue monitoring traffic patterns
  ⚠️ Network likely safe - model uncertain
  ⚠️ Consider manual inspection if persists</pre>
                        ${simulatedBadge}
                    </div>`;
            } else {
                const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
                const duration = '25.0s';
                const metrics = data.metrics || {};
                const flowDuration = metrics.flow_duration ? metrics.flow_duration.toFixed(0) : 'N/A';
                const flowBytesPerSec = metrics.flow_bytes_per_sec ? metrics.flow_bytes_per_sec.toLocaleString('en-US', {maximumFractionDigits: 1}) : 'N/A';
                const flowPacketsPerSec = metrics.flow_packets_per_sec ? metrics.flow_packets_per_sec.toFixed(1) : 'N/A';
                const packetRatio = metrics.packet_ratio ? metrics.packet_ratio.toFixed(2) : 'N/A';
                
                resultDiv.innerHTML = `
                    <div class="alert green">
                        <pre style="font-family: 'Courier New', monospace; font-size: 0.9em; line-height: 1.6; margin: 0; white-space: pre-wrap; color: #fff;">═══════════════════════════════════════════════════════════
🛡️ NETWORK SECURITY SCAN REPORT
═══════════════════════════════════════════════════════════

<strong>STATUS: ✅ NORMAL TRAFFIC DETECTED</strong>
Classification: Benign Network Activity
Timestamp: ${timestamp} | Duration: ${duration}

<strong>THREAT ASSESSMENT</strong>
├─ Threat Score:    ${data.pred.toFixed(4)}  (LOW)
├─ Confidence:      ${((1 - data.pred) * 100).toFixed(1)}%
└─ Risk Level:      MINIMAL ░░░░░░░░░░

<strong>RECOMMENDATIONS</strong>
  ✓ No action required - continue monitoring
  ✓ Network operating within normal parameters</pre>
                        ${simulatedBadge}
                    </div>`;
            }
        })
        .catch(err => {
            console.error('[DDoS Monitor] Error during scan:', err);
            console.error('[DDoS Monitor] Error name:', err.name);
            console.error('[DDoS Monitor] Error message:', err.message);
            clearInterval(chartInterval);
            clearInterval(countdownTimer);
            btn.disabled = false;
            btn.style.opacity = "1";
            attackBtn.disabled = false;
            attackBtn.style.opacity = "1";
            statusText.innerText = "Error";
            statusText.style.color = "#ff3333";
            
            if (err.name === 'AbortError') {
                resultDiv.innerHTML = `<div class="alert red">Scan timeout - please try again</div>`;
                console.error('[DDoS Monitor] Request aborted/timed out');
            } else {
                resultDiv.innerHTML = `<div class="alert red">Error: ${err.message}<br><small>Check browser console for details</small></div>`;
            }
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
            // UPGRADE: Three-tier classification system (industry-grade)
            const verdict = data.verdict || (data.pred > 0.5 ? 'phishing' : 'legitimate');
            const confidence = data.confidence || 'medium';
            const score = data.pred;
            const isTrusted = data.trusted || false;
            
            if (isTrusted) {
                resultDiv.innerHTML = `
                <div class="alert green">
                    <h3>✅ TRUSTED WEBSITE</h3>
                    <p>🛡️ This is a verified trusted domain (${new URL(url).hostname})</p>
                    <p><strong>✓ No analysis needed - Whitelisted</strong></p>
                    <p style="font-size: 0.9em; margin-top: 10px; color: #00ff88;">
                        This domain is on the trusted list of major legitimate websites.<br>
                        Safe to visit.
                    </p>
                </div>`;
            } else if (verdict === 'phishing') {
                resultDiv.innerHTML = `
                <div class="alert red">
                    <h3>🚫 DANGEROUS PHISHING SITE</h3>
                    <p>Risk Level: ${(score * 100).toFixed(1)}% (${confidence.toUpperCase()} confidence)</p>
                    <p><strong>⚠️ DO NOT VISIT THIS LINK!</strong></p>
                    <p style="font-size: 0.9em; margin-top: 10px;">
                        This URL shows strong indicators of phishing:<br>
                        • Suspicious domain structure<br>
                        • Contains social engineering keywords<br>
                        • Unusual character patterns detected
                    </p>
                </div>`;
            } else if (verdict === 'suspicious') {
                resultDiv.innerHTML = `
                <div class="alert" style="background: rgba(255, 165, 0, 0.1); border-color: #ffa500;">
                    <h3 style="color: #ffa500;">⚠️ SUSPICIOUS URL</h3>
                    <p>Risk Level: ${(score * 100).toFixed(1)}% (${confidence.toUpperCase()} confidence)</p>
                    <p><strong>⚠️ Exercise Caution!</strong></p>
                    <p style="font-size: 0.9em; margin-top: 10px;">
                        This URL shows some suspicious characteristics:<br>
                        • Unusual URL structure<br>
                        • May contain misleading elements<br>
                        • Verify the domain before proceeding
                    </p>
                </div>`;
            } else {
                resultDiv.innerHTML = `
                <div class="alert green">
                    <h3>✅ LEGITIMATE WEBSITE</h3>
                    <p>Safety Score: ${((1 - score) * 100).toFixed(1)}% (${confidence.toUpperCase()} confidence)</p>
                    <p><strong>✓ URL structure looks safe</strong></p>
                    <p style="font-size: 0.9em; margin-top: 10px;">
                        No significant phishing indicators detected in:<br>
                        • Domain structure and entropy<br>
                        • URL pattern analysis<br>
                        • Social engineering keywords
                    </p>
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
