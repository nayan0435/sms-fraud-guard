/**
 * SMS Fraud Guard - Frontend Logic
 */

// Sample messages for testing
const SAMPLES = {
    fraud1: {
        sender: '+91 9876500001',
        message: 'WINNER!! As a valued customer you have been selected to receive a ₹50000 prize reward! To claim your prize call 09050000 NOW!'
    },
    fraud2: {
        sender: '+1 800-555-0000',
        message: 'ALERT: Your bank account has been compromised! Verify your account immediately at www.fakebank-verify.com to prevent suspension.'
    },
    fraud3: {
        sender: '+91 7777700000',
        message: 'Your package delivery failed. Pay ₹199 fee to reschedule delivery. Click here: bit.ly/fakeshipping123'
    },
    safe1: {
        sender: '+91 9876543210',
        message: 'Hey! Are we still meeting for dinner tonight at 7pm? Let me know if you want me to pick you up.'
    },
    safe2: {
        sender: '+91 8765432100',
        message: 'The team meeting has been rescheduled to 3pm tomorrow. Please update your calendar. Thanks!'
    },
    safe3: {
        sender: '+91 9988776655',
        message: 'Mom says dinner is ready. Come home soon! Dad is waiting too.'
    }
};

/**
 * Load a sample message into the input fields
 */
function loadSample(key) {
    const sample = SAMPLES[key];
    if (sample) {
        document.getElementById('senderInput').value = sample.sender;
        document.getElementById('messageInput').value = sample.message;
        // Auto-scroll to scanner
        document.querySelector('.scanner-card').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Scan a message via the API
 */
async function scanMessage() {
    const sender = document.getElementById('senderInput').value.trim() || 'Unknown';
    const message = document.getElementById('messageInput').value.trim();

    if (!message) {
        alert('Please enter an SMS message to scan.');
        return;
    }

    const btn = document.getElementById('scanBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    // Show loading state
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    btn.disabled = true;

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, sender })
        });

        const result = await response.json();
        displayResult(result);
        loadStats();
        loadBlockedMessages();
    } catch (error) {
        console.error('Scan failed:', error);
        alert('Failed to scan message. Make sure the server is running.');
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        btn.disabled = false;
    }
}

/**
 * Display scan result
 */
function displayResult(result) {
    const panel = document.getElementById('resultPanel');
    const content = document.getElementById('resultContent');

    const isFraud = result.is_fraud;
    const className = isFraud ? 'result-fraud' : 'result-safe';
    const icon = isFraud ? '🚨' : '✅';
    const label = isFraud ? 'FRAUD DETECTED' : 'MESSAGE IS SAFE';

    let blockedHtml = '';
    if (result.auto_blocked) {
        blockedHtml = `
            <div class="blocked-badge">
                🚫 Auto-blocked & reported to security team
            </div>
        `;
    }

    content.innerHTML = `
        <div class="${className}">
            <div class="result-label">${icon} ${label}</div>
            <div class="result-details">
                <div class="result-detail">
                    <span>Confidence:</span>
                    <span>${result.confidence.toFixed(1)}%</span>
                </div>
                <div class="result-detail">
                    <span>Risk Level:</span>
                    <span>${result.risk_level.toUpperCase()}</span>
                </div>
                <div class="result-detail">
                    <span>Sender:</span>
                    <span>${escapeHtml(result.sender)}</span>
                </div>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${result.confidence}%"></div>
            </div>
            ${blockedHtml}
        </div>
    `;

    panel.style.display = 'block';
}

/**
 * Load stats from API
 */
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();

        animateValue('totalScanned', stats.total_scanned);
        animateValue('fraudDetected', stats.fraud_detected);
        animateValue('blockedCount', stats.blocked_count);
        document.getElementById('fraudRate').textContent = stats.fraud_rate + '%';
    } catch (e) {
        console.error('Failed to load stats:', e);
    }
}

/**
 * Load blocked messages
 */
async function loadBlockedMessages() {
    try {
        const res = await fetch('/api/blocked');
        const messages = await res.json();
        const container = document.getElementById('blockedList');

        if (messages.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">✅</span>
                    <p>No blocked messages yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = messages.map(msg => `
            <div class="blocked-item">
                <span class="blocked-item-icon">🚫</span>
                <div class="blocked-item-content">
                    <div class="blocked-item-sender">${escapeHtml(msg.sender || 'Unknown')}</div>
                    <div class="blocked-item-message">${escapeHtml(msg.message)}</div>
                    <div class="blocked-item-time">${formatTime(msg.blocked_at)}</div>
                </div>
                <span class="blocked-item-confidence">${msg.confidence.toFixed(1)}%</span>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load blocked messages:', e);
    }
}

/**
 * Toggle auto-block
 */
async function toggleAutoBlock() {
    try {
        const res = await fetch('/api/autoblock/toggle', { method: 'POST' });
        const data = await res.json();
        document.getElementById('autoBlockToggle').checked = data.enabled;
    } catch (e) {
        console.error('Failed to toggle auto-block:', e);
    }
}

/**
 * Animate number counter
 */
function animateValue(elementId, endValue) {
    const el = document.getElementById(elementId);
    const start = parseInt(el.textContent) || 0;
    if (start === endValue) return;

    const duration = 500;
    const startTime = Date.now();

    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = Math.round(start + (endValue - start) * eased);
        el.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Format timestamp
 */
function formatTime(ts) {
    const d = new Date(ts);
    return d.toLocaleString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        day: 'numeric',
        month: 'short'
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadStats();
    loadBlockedMessages();

    // Auto-block toggle
    document.getElementById('autoBlockToggle').addEventListener('change', toggleAutoBlock);

    // Enter key to scan
    document.getElementById('messageInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            scanMessage();
        }
    });

    // Load auto-block status
    fetch('/api/autoblock')
        .then(res => res.json())
        .then(data => {
            document.getElementById('autoBlockToggle').checked = data.enabled;
        });
});
