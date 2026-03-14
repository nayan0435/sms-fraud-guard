#  SMS Fraud Guard — AI-Powered SMS Fraud Detection & Auto-Block System

A complete **machine learning-based SMS fraud detection system** with a web dashboard and a native Android app that automatically intercepts, classifies, and blocks fraudulent SMS messages in real-time.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Kotlin](https://img.shields.io/badge/Kotlin-Android-purple?logo=kotlin)
![ML](https://img.shields.io/badge/ML-scikit--learn-orange?logo=scikit-learn)

---

## Features

- **AI-Powered Detection** — TF-IDF + Naive Bayes classifier trained on 5,574+ SMS messages
- **Real-Time Scanning** — Classify any SMS as fraud or safe with confidence score
- **Auto-Block** — Automatically block detected fraud messages
- **Push Notifications** — Instant alerts when fraud SMS is detected on your phone
- **Security Team Dashboard** — Live monitoring portal with alerts, stats, and blocked message logs
- **Android App** — Native Kotlin app with SMS interception via BroadcastReceiver



## 🏗️ Architecture

```
📱 Android App          →    🌐 Flask API Server    →    🧠 ML Model
(SMS Interception)           (REST API + Database)       (TF-IDF + NaiveBayes)
                                     ↓
                             🔒 Security Dashboard
                             (Real-time Monitoring)
```

---

## 📂 Project Structure

```
├── fraud_sms_detector/          # Python Backend
│   ├── app.py                   # Flask API server
│   ├── database.py              # SQLite database
│   ├── requirements.txt         # Python dependencies
│   ├── model/
│   │   ├── train_model.py       # ML training script
│   │   └── predict.py           # Prediction module
│   ├── templates/
│   │   ├── index.html           # User dashboard
│   │   └── dashboard.html       # Security team dashboard
│   └── static/
│       ├── style.css            # Dark theme CSS
│       └── script.js            # Frontend logic
│
└── FraudSMSGuard/               # Android App (Kotlin)
    └── app/src/main/
        ├── AndroidManifest.xml
        └── java/com/fraudsmsguard/app/
            ├── MainActivity.kt
            ├── SmsReceiver.kt           # SMS interceptor
            ├── SmsMonitorService.kt     # Background monitoring
            ├── NotificationHelper.kt    # Push notifications
            ├── BlockedMessagesActivity.kt
            └── SettingsActivity.kt
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/sms-fraud-guard.git
cd sms-fraud-guard
```

### 2. Install dependencies
```bash
cd fraud_sms_detector
pip install -r requirements.txt
```

### 3. Train the ML model
```bash
cd model
python train_model.py
```

### 4. Start the server
```bash
cd ..
python app.py
```

### 5. Open in browser
- **User Dashboard:** http://localhost:5000/
- **Security Dashboard:** http://localhost:5000/dashboard

---

## 📱 Android App Setup

1. Open `FraudSMSGuard/` in **Android Studio**
2. Build & install on your phone
3. Grant SMS permissions
4. In Settings → set server URL to your PC's IP (e.g., `http://192.168.1.X:5000`)
5. Enable **SMS Monitoring** and **Auto-Block**
6. Every incoming SMS is now automatically scanned! 🎉

---

## 🧠 ML Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | ~97%+ |
| Precision (Spam) | ~100% |
| Recall (Spam) | ~90%+ |
| F1-Score | ~95%+ |

Trained on the [SMS Spam Collection Dataset](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection) from UCI Machine Learning Repository.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Classify an SMS message |
| `GET` | `/api/stats` | Get dashboard statistics |
| `GET` | `/api/blocked` | Get blocked messages list |
| `POST` | `/api/block` | Manually block a message |
| `POST` | `/api/autoblock/toggle` | Toggle auto-block on/off |
| `GET` | `/api/alerts` | Get security alerts |
| `POST` | `/api/unblock/<id>` | Unblock a message |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, scikit-learn, pandas, SQLite
- **Frontend:** HTML, CSS (glassmorphism dark theme), JavaScript
- **Android:** Kotlin, BroadcastReceiver, Foreground Service
- **ML:** TF-IDF Vectorizer + Multinomial Naive Bayes

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

Made with ❤️ using Machine Learning
