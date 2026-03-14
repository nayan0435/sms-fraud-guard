# Fraud SMS Detection & Auto-Block System (Mobile App)

A complete system with a **native Android app** that monitors every incoming SMS, classifies it as fraud/safe using an ML model, **auto-blocks fraud messages**, and **sends notifications** to both the user and a spam security team.

## Architecture

```
┌─────────────────┐       API Call        ┌──────────────────────┐
│   Android App   │ ──────────────────▶   │   Flask API Server   │
│  (Kotlin/Java)  │ ◀──────────────────   │  (ML Model hosted)   │
│                 │     Prediction         │                      │
│ • SMS Receiver  │                        │ • TF-IDF + NaiveBayes│
│ • Auto-Block    │                        │ • /predict endpoint  │
│ • Notifications │                        │ • /report endpoint   │
│ • Dashboard     │                        │ • Security Dashboard │
└─────────────────┘                        └──────────────────────┘
                                                     │
                                              Notification
                                                     ▼
                                           ┌──────────────────┐
                                           │ Security Team     │
                                           │ Web Dashboard     │
                                           │ + Email Alerts    │
                                           └──────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| ML Model | Python, scikit-learn, TF-IDF + Multinomial Naive Bayes |
| Backend API | Flask, Flask-Mail |
| Database | SQLite (blocked messages, reports) |
| Android App | Kotlin, Retrofit, BroadcastReceiver |
| Security Dashboard | Flask-served HTML/CSS/JS (dark themed) |
| Notifications | Android NotificationManager + Email alerts |

---

## Proposed Changes

### 1. ML Model & Backend API (`fraud_sms_detector/`)

#### [NEW] `model/train_model.py`
- Download SMS Spam Collection dataset (5,574 messages)
- Preprocess text (lowercase, remove punctuation/numbers)
- TF-IDF vectorization → Multinomial Naive Bayes
- Evaluate (accuracy, precision, recall, F1) — targeting >95%
- Save model + vectorizer as `.pkl` files

#### [NEW] `model/predict.py`
- `predict_sms(message)` → returns `{label, confidence, risk_level}`

#### [NEW] `app.py` — Flask API Server
- `POST /api/predict` — Classify SMS text, return fraud/safe + confidence
- `POST /api/report` — Log blocked message to DB + notify security team
- `GET /api/stats` — Return total scanned, blocked, fraud rate
- `GET /api/blocked` — Return all blocked messages
- `GET /dashboard` — Security team web dashboard

#### [NEW] `database.py` — SQLite database
- Tables: `blocked_messages`, `scan_log`, `security_alerts`

#### [NEW] `notifications.py` — Email notification service
- Send email alerts to security team when fraud detected
- Configurable email settings

#### [NEW] `templates/dashboard.html` — Security Team Dashboard
- Real-time stats (total scanned, fraud %, blocked count)
- Table of all blocked/flagged messages
- Dark-themed premium UI with glassmorphism

#### [NEW] `requirements.txt`

---

### 2. Android App (`FraudSMSGuard/`)

> [!IMPORTANT]
> The Android app requires **Android Studio** to build and install. The user will need to open the project in Android Studio, connect their phone (or use an emulator), and run the app.

#### [NEW] `app/src/main/AndroidManifest.xml`
- Permissions: `RECEIVE_SMS`, `READ_SMS`, `READ_PHONE_STATE`, `INTERNET`, `POST_NOTIFICATIONS`
- Register `SmsReceiver` BroadcastReceiver
- Register `SmsMonitorService` foreground service

#### [NEW] `app/src/main/java/.../MainActivity.kt`
- Request runtime permissions for SMS access
- Dashboard UI: stats cards, recent scans, blocked list
- Toggle for auto-block ON/OFF
- Settings for API server URL

#### [NEW] `app/src/main/java/.../SmsReceiver.kt`
- `BroadcastReceiver` listening for `SMS_RECEIVED`
- Extract sender number + message body
- Send to API for classification
- If fraud: trigger auto-block + notification

#### [NEW] `app/src/main/java/.../SmsMonitorService.kt`
- Foreground service to keep monitoring active
- Shows persistent notification "SMS Guard Active"

#### [NEW] `app/src/main/java/.../ApiService.kt`
- Retrofit interface for API calls (`/predict`, `/report`)

#### [NEW] `app/src/main/java/.../NotificationHelper.kt`
- Show notification when fraud SMS detected
- Notification includes sender, preview, and "View Details" action

#### [NEW] `app/src/main/java/.../BlockedMessagesActivity.kt`
- Full list of blocked messages with details
- Option to unblock/whitelist a number

#### [NEW] `app/src/main/res/layout/` — XML Layouts
- `activity_main.xml` — Main dashboard
- `activity_blocked.xml` — Blocked messages list
- `item_message.xml` — Message list item

#### [NEW] `app/src/main/res/values/` — Colors, styles, strings (dark theme)

---

## How It Works (User Flow)

1. **Install & Grant Permission** → User installs the app, grants SMS permission
2. **SMS Arrives** → `SmsReceiver` intercepts the incoming SMS
3. **ML Classification** → Message sent to Flask API → returns fraud/safe + confidence
4. **If Safe** → Message is left alone, logged as "scanned"
5. **If Fraud** → Message is auto-blocked, user gets a notification ("⚠️ Fraud SMS blocked from +91XXXX"), and the security team dashboard is updated + email alert sent
6. **Dashboard** → User can view stats and blocked messages in the app
7. **Security Team** → Monitors all reports via web dashboard

## Verification Plan

### Automated
- Model training outputs accuracy >95% with classification report
- Flask API returns correct predictions for test SMS messages

### Manual
1. Run Flask server, verify `/api/predict` works via browser/curl
2. Open Android app in emulator, grant permissions
3. Send test SMS to emulator → verify classification + notification
4. Check security dashboard shows the blocked message
