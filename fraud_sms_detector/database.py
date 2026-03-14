"""
Database module for Fraud SMS Detector.
SQLite database for storing blocked messages, scan logs, and security alerts.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'fraud_sms.db')


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS scan_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT,
            is_blocked INTEGER DEFAULT 0,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS blocked_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_unblocked INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS security_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT,
            alert_type TEXT DEFAULT 'fraud_detected',
            is_reviewed INTEGER DEFAULT 0,
            notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()


def log_scan(sender, message, label, confidence, risk_level, is_blocked=False):
    """Log a scanned message."""
    conn = get_db()
    conn.execute(
        '''INSERT INTO scan_log (sender, message, label, confidence, risk_level, is_blocked)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (sender, message, label, confidence, risk_level, int(is_blocked))
    )
    conn.commit()
    conn.close()


def block_message(sender, message, confidence, risk_level):
    """Add a message to the blocked list."""
    conn = get_db()
    conn.execute(
        '''INSERT INTO blocked_messages (sender, message, confidence, risk_level)
           VALUES (?, ?, ?, ?)''',
        (sender, message, confidence, risk_level)
    )
    conn.commit()
    conn.close()


def create_security_alert(sender, message, confidence, risk_level):
    """Create a security alert for the team."""
    conn = get_db()
    conn.execute(
        '''INSERT INTO security_alerts (sender, message, confidence, risk_level)
           VALUES (?, ?, ?, ?)''',
        (sender, message, confidence, risk_level)
    )
    conn.commit()
    conn.close()


def get_blocked_messages(limit=50):
    """Get recent blocked messages."""
    conn = get_db()
    rows = conn.execute(
        '''SELECT * FROM blocked_messages
           WHERE is_unblocked = 0
           ORDER BY blocked_at DESC LIMIT ?''',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_security_alerts(limit=50):
    """Get recent security alerts."""
    conn = get_db()
    rows = conn.execute(
        '''SELECT * FROM security_alerts
           ORDER BY notified_at DESC LIMIT ?''',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """Get dashboard statistics."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM scan_log').fetchone()[0]
    fraud = conn.execute("SELECT COUNT(*) FROM scan_log WHERE label = 'spam'").fetchone()[0]
    blocked = conn.execute('SELECT COUNT(*) FROM blocked_messages WHERE is_unblocked = 0').fetchone()[0]
    alerts = conn.execute('SELECT COUNT(*) FROM security_alerts WHERE is_reviewed = 0').fetchone()[0]
    conn.close()

    return {
        'total_scanned': total,
        'fraud_detected': fraud,
        'blocked_count': blocked,
        'pending_alerts': alerts,
        'fraud_rate': round((fraud / total * 100), 1) if total > 0 else 0
    }


def unblock_message(message_id):
    """Unblock a message by ID."""
    conn = get_db()
    conn.execute(
        'UPDATE blocked_messages SET is_unblocked = 1 WHERE id = ?',
        (message_id,)
    )
    conn.commit()
    conn.close()


def mark_alert_reviewed(alert_id):
    """Mark a security alert as reviewed."""
    conn = get_db()
    conn.execute(
        'UPDATE security_alerts SET is_reviewed = 1 WHERE id = ?',
        (alert_id,)
    )
    conn.commit()
    conn.close()


# Initialize on import
init_db()
