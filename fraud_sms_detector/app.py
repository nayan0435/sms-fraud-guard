"""
Fraud SMS Detector - Flask API Server
Serves the ML model for predictions and provides security team dashboard.
"""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Add model directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model'))

from predict import predict_sms
from database import (
    log_scan, block_message, create_security_alert,
    get_blocked_messages, get_security_alerts, get_stats,
    unblock_message, mark_alert_reviewed
)

app = Flask(__name__)
CORS(app)

# Auto-block setting (can be toggled via API)
auto_block_enabled = True


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/dashboard')
def security_dashboard():
    """Security team dashboard."""
    return render_template('dashboard.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """Classify an SMS message."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message text is required'}), 400

    message = data['message']
    sender = data.get('sender', 'Unknown')

    # Get prediction
    result = predict_sms(message)

    # Log the scan
    log_scan(sender, message, result['label'], result['confidence'],
             result['risk_level'], is_blocked=False)

    # Auto-block if fraud detected and auto-block is enabled
    blocked = False
    if result['is_fraud'] and auto_block_enabled:
        block_message(sender, message, result['confidence'], result['risk_level'])
        create_security_alert(sender, message, result['confidence'], result['risk_level'])
        blocked = True

    response = {
        'label': result['label'],
        'is_fraud': result['is_fraud'],
        'confidence': result['confidence'],
        'risk_level': result['risk_level'],
        'auto_blocked': blocked,
        'sender': sender,
        'timestamp': datetime.now().isoformat()
    }

    return jsonify(response)


@app.route('/api/block', methods=['POST'])
def manual_block():
    """Manually block a message."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message text is required'}), 400

    sender = data.get('sender', 'Unknown')
    message = data['message']
    confidence = data.get('confidence', 0)
    risk_level = data.get('risk_level', 'manual')

    block_message(sender, message, confidence, risk_level)
    create_security_alert(sender, message, confidence, risk_level)

    return jsonify({'status': 'blocked', 'message': 'Message has been blocked'})


@app.route('/api/unblock/<int:message_id>', methods=['POST'])
def unblock(message_id):
    """Unblock a message."""
    unblock_message(message_id)
    return jsonify({'status': 'unblocked'})


@app.route('/api/blocked', methods=['GET'])
def blocked_list():
    """Get all blocked messages."""
    messages = get_blocked_messages()
    return jsonify(messages)


@app.route('/api/alerts', methods=['GET'])
def alerts_list():
    """Get security alerts."""
    alerts = get_security_alerts()
    return jsonify(alerts)


@app.route('/api/alerts/<int:alert_id>/review', methods=['POST'])
def review_alert(alert_id):
    """Mark alert as reviewed."""
    mark_alert_reviewed(alert_id)
    return jsonify({'status': 'reviewed'})


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get dashboard statistics."""
    return jsonify(get_stats())


@app.route('/api/autoblock', methods=['GET'])
def get_autoblock():
    """Get auto-block status."""
    return jsonify({'enabled': auto_block_enabled})


@app.route('/api/autoblock/toggle', methods=['POST'])
def toggle_autoblock():
    """Toggle auto-block on/off."""
    global auto_block_enabled
    auto_block_enabled = not auto_block_enabled
    return jsonify({'enabled': auto_block_enabled})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  FRAUD SMS DETECTOR - API SERVER")
    print("=" * 60)
    print(f"  Dashboard:    http://localhost:5000/")
    print(f"  Security:     http://localhost:5000/dashboard")
    print(f"  API endpoint: http://localhost:5000/api/predict")
    print(f"  Auto-block:   {'ON' if auto_block_enabled else 'OFF'}")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
