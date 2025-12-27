// LogGuard JavaScript Application

let selectedFile = null;

// Check system status on load
document.addEventListener('DOMContentLoaded', function() {
    checkStatus();
});

// Check API status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (data.status === 'running' && data.model_loaded) {
            statusText.textContent = 'System Ready';
            statusDot.classList.remove('error');
        } else if (data.status === 'running' && !data.model_loaded) {
            statusText.textContent = 'Model Not Loaded';
            statusDot.classList.add('error');
        } else {
            statusText.textContent = 'Error';
            statusDot.classList.add('error');
        }
    } catch (error) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        statusText.textContent = 'Connection Error';
        statusDot.classList.add('error');
    }
}

// Switch between tabs
function switchTab(tabName) {
    // Update tab buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    if (tabName === 'text') {
        document.getElementById('textTab').classList.add('active');
    } else {
        document.getElementById('fileTab').classList.add('active');
    }
}

// Handle file selection
function handleFileSelect() {
    const fileInput = document.getElementById('fileUpload');
    const analyzeBtn = document.getElementById('analyzeFileBtn');
    
    if (fileInput.files.length > 0) {
        selectedFile = fileInput.files[0];
        analyzeBtn.disabled = false;
    } else {
        selectedFile = null;
        analyzeBtn.disabled = true;
    }
}

// Analyze single log line
async function analyzeSingleLine() {
    const logLine = document.getElementById('singleLog').value.trim();
    const resultDiv = document.getElementById('singleResult');
    
    if (!logLine) {
        showResult(resultDiv, 'Please enter a log line', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/analyze-line', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ log_line: logLine })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showResult(resultDiv, `Error: ${data.error}`, 'error');
            return;
        }
        
        const resultClass = data.is_anomaly ? 'warning' : 'success';
        const resultIcon = data.is_anomaly ? '⚠️' : '✅';
        const resultText = data.is_anomaly ? 'ANOMALY DETECTED' : 'Normal Log';
        
        const html = `
            <h3>${resultIcon} ${resultText}</h3>
            <p><strong>Anomaly Score:</strong> ${data.anomaly_score.toFixed(4)}</p>
            <div style="margin-top: 15px;">
                <strong>Parsed Data:</strong>
                <pre style="background: #f3f4f6; padding: 10px; border-radius: 4px; margin-top: 5px;">
Timestamp: ${data.parsed_data.timestamp}
IP Address: ${data.parsed_data.ip}
Severity: ${data.parsed_data.severity}
Status Code: ${data.parsed_data.status_code}
Response Time: ${data.parsed_data.response_time}ms</pre>
            </div>
        `;
        
        showResult(resultDiv, html, resultClass);
    } catch (error) {
        showResult(resultDiv, `Error: ${error.message}`, 'error');
    }
}

// Analyze batch text
async function analyzeBatchText() {
    const logs = document.getElementById('batchLogs').value.trim();
    
    if (!logs) {
        alert('Please enter some log lines');
        return;
    }
    
    await analyzeLogsAPI({ logs: logs });
}

// Analyze batch file
async function analyzeBatchFile() {
    if (!selectedFile) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    await analyzeLogsAPI(formData, true);
}

// Common API call for batch analysis
async function analyzeLogsAPI(data, isFormData = false) {
    const resultDiv = document.getElementById('batchResult');
    showResult(resultDiv, 'Analyzing logs...', 'success');
    
    try {
        const options = {
            method: 'POST',
        };
        
        if (isFormData) {
            options.body = data;
        } else {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch('/api/analyze', options);
        const result = await response.json();
        
        if (result.error) {
            showResult(resultDiv, `Error: ${result.error}`, 'error');
            return;
        }
        
        // Hide the result box and show dashboard instead
        resultDiv.style.display = 'none';
        displayDashboard(result);
        
    } catch (error) {
        showResult(resultDiv, `Error: ${error.message}`, 'error');
    }
}

// Display results dashboard
function displayDashboard(data) {
    const dashboard = document.getElementById('dashboard');
    
    // Update statistics
    document.getElementById('totalLogs').textContent = data.total_logs.toLocaleString();
    document.getElementById('anomalyCount').textContent = data.anomaly_count.toLocaleString();
    document.getElementById('anomalyRate').textContent = `${data.anomaly_percentage}%`;
    
    // Display severity chart
    const severityChart = document.getElementById('severityChart');
    severityChart.innerHTML = '';
    
    for (const [severity, count] of Object.entries(data.severity_counts)) {
        const item = document.createElement('div');
        item.className = `severity-item ${severity}`;
        item.innerHTML = `<span>${severity}</span><span><strong>${count}</strong></span>`;
        severityChart.appendChild(item);
    }
    
    // Display anomalies list
    const anomaliesList = document.getElementById('anomaliesList');
    anomaliesList.innerHTML = '';
    
    if (data.anomalies.length === 0) {
        anomaliesList.innerHTML = '<p style="text-align: center; color: #10b981; padding: 20px;"><strong>✅ No anomalies detected! All logs appear normal.</strong></p>';
    } else {
        data.anomalies.forEach((anomaly, index) => {
            const item = document.createElement('div');
            item.className = 'anomaly-item';
            item.innerHTML = `
                <div class="anomaly-header">
                    <span>Anomaly #${index + 1}</span>
                    <span class="anomaly-score">Score: ${anomaly.anomaly_score.toFixed(4)}</span>
                </div>
                <div class="anomaly-details">
                    <div class="detail-item">
                        <div class="detail-label">Timestamp</div>
                        <div class="detail-value">${anomaly.timestamp}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">IP Address</div>
                        <div class="detail-value">${anomaly.ip}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Severity</div>
                        <div class="detail-value">${anomaly.severity}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Status Code</div>
                        <div class="detail-value">${anomaly.status_code}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Response Time</div>
                        <div class="detail-value">${anomaly.response_time}ms</div>
                    </div>
                </div>
                <div class="anomaly-log">${anomaly.raw_log}</div>
            `;
            anomaliesList.appendChild(item);
        });
    }
    
    dashboard.style.display = 'block';
    dashboard.scrollIntoView({ behavior: 'smooth' });
}

// Show result helper
function showResult(element, message, type) {
    element.innerHTML = message;
    element.className = `result-box ${type}`;
    element.style.display = 'block';
}
