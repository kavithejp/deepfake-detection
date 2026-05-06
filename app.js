const faceStatus = document.getElementById('faceStatus');
const voiceStatus = document.getElementById('voiceStatus');
const trustPercentMini = document.getElementById('trustPercentMini');
const trustPercent = document.getElementById('trustPercent');
const trustCircle = document.getElementById('trustCircle');
const trustBarFill = document.getElementById('trustBarFill');
const decisionValue = document.getElementById('decisionValue');
const logContent = document.getElementById('logContent');
const timestampEl = document.getElementById('timestamp');
const connStatus = document.getElementById('connStatus');

let lastTimestamp = null;

// --- Tab Switching Logic ---
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        const viewId = item.getAttribute('data-view');
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        views.forEach(v => {
            v.classList.remove('active');
            if(v.id === `view-${viewId}`) v.classList.add('active');
        });
        document.getElementById('view-title').innerText = viewId.replace('-', ' ').toUpperCase();
    });
});

// Update Timestamp
function updateTime() {
    const now = new Date();
    timestampEl.innerText = now.toISOString().replace('T', ' ').substring(0, 19);
}
setInterval(updateTime, 1000);

// Add Log Entry
function addLog(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerText = `> ${message}`;
    logContent.appendChild(entry);
    logContent.scrollTop = logContent.scrollHeight;
    
    // Keep logs small
    if (logContent.childElementCount > 20) logContent.removeChild(logContent.firstChild);
}

// --- Chart Initialization ---
const ctxChart = document.getElementById('trustChart').getContext('2d');
const trustChart = new Chart(ctxChart, {
    type: 'line',
    data: {
        labels: ['-5s', '-4s', '-3s', '-2s', '-1s', '0s'],
        datasets: [{
            label: 'Trust Score',
            data: [0, 0, 0, 0, 0, 0],
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointRadius: 4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
            x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        }
    }
});

function updateChart(newScore) {
    trustChart.data.datasets[0].data.shift();
    trustChart.data.datasets[0].data.push(newScore);
    trustChart.update();
}

// Update Circular Progress
function updateCircularProgress(percent) {
    if(!trustCircle) return;
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percent / 100) * circumference;
    trustCircle.style.strokeDashoffset = offset;
    trustPercent.innerText = `${percent}%`;
}

// --- Remote Data Polling ---
async function fetchLatestData() {
    try {
        const response = await fetch('/latest'); // Use relative path
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();

        if (data.error || data.message === "No detections found") {
            // Keep waiting for data
            return;
        }

        // Only update if it's a new record or first time
        if (data.timestamp !== lastTimestamp) {
            lastTimestamp = data.timestamp;
            connStatus.innerText = "ENGINE CONNECTED";
            connStatus.style.color = "#10b981";

            // Update UI Elements with Fallbacks
            updateUI(data);
            addLog(`Update: Face is ${data.face_status || 'analyzing...'}`);
        }
    } catch (error) {
        console.error("Polling Error:", error);
    }
}

function updateUI(data) {
    // Stats Cards - Safe Access
    if(faceStatus) faceStatus.innerText = data.face_status || "WAITING";
    if(voiceStatus) voiceStatus.innerText = data.voice_status || "AWAITING";
    if(trustPercentMini) trustPercentMini.innerText = `${data.trust_score || 0}%`;
    
    // Central Decision
    if(decisionValue) {
        decisionValue.innerText = data.decision || "PROCESSING...";
        decisionValue.style.color = (data.decision === "ACCESS GRANTED") ? "#10b981" : "#f43f5e";
    }
    
    // Trust Bar
    if(trustBarFill) {
        const score = data.trust_score || 0;
        trustBarFill.style.width = `${score}%`;
        trustBarFill.style.backgroundColor = score > 80 ? "#10b981" : "#f43f5e";
    }

    // Chart & Circular Progress
    updateChart(data.trust_score || 0);
    updateCircularProgress(data.trust_score || 0);
}


// Poll every 1 second
setInterval(fetchLatestData, 1000);
addLog("AIVENTRA Monitoring System Ready.");
