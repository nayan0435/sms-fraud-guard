"""
SMS Fraud Detection - Prediction Module
Loads the trained model and provides prediction functions.
"""

import os
import re
import joblib

MODEL_DIR = os.path.dirname(__file__)

# Load model and vectorizer
_model = None
_vectorizer = None


def _load_model():
    """Lazy-load the trained model and vectorizer."""
    global _model, _vectorizer
    if _model is None:
        model_path = os.path.join(MODEL_DIR, 'sms_fraud_model.pkl')
        vectorizer_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "Model not found. Please run train_model.py first."
            )

        _model = joblib.load(model_path)
        _vectorizer = joblib.load(vectorizer_path)


def preprocess_text(text):
    """Clean and preprocess SMS text (must match training preprocessing)."""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' url ', text)
    text = re.sub(r'\b\d{5,}\b', ' longnum ', text)
    text = re.sub(r'£|\$|€', ' currency ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' num ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_sms(message):
    """
    Classify an SMS message as spam/ham.

    Args:
        message (str): The SMS text to classify.

    Returns:
        dict: {
            'label': 'spam' or 'ham',
            'confidence': float (0-100),
            'risk_level': 'high', 'medium', or 'low',
            'is_fraud': bool
        }
    """
    _load_model()

    cleaned = preprocess_text(message)
    features = _vectorizer.transform([cleaned])

    prediction = int(_model.predict(features)[0])
    probabilities = _model.predict_proba(features)[0]
    confidence = float(max(probabilities)) * 100

    label = 'spam' if prediction == 1 else 'ham'
    is_fraud = bool(prediction == 1)

    # Determine risk level
    if is_fraud:
        if confidence >= 90:
            risk_level = 'high'
        elif confidence >= 70:
            risk_level = 'medium'
        else:
            risk_level = 'low'
    else:
        risk_level = 'none'

    return {
        'label': label,
        'confidence': round(confidence, 2),
        'risk_level': risk_level,
        'is_fraud': is_fraud
    }


if __name__ == '__main__':
    # Quick test
    test_msgs = [
        "WINNER! You've won a £1000 prize! Call now!",
        "Hey, want to grab lunch tomorrow?",
        "URGENT: Verify your bank account immediately at fakeurl.com",
        "Mom says dinner is at 7pm tonight",
    ]
    for msg in test_msgs:
        result = predict_sms(msg)
        print(f"{'🚨 FRAUD' if result['is_fraud'] else '✅ SAFE'} "
              f"[{result['confidence']:.1f}%] [{result['risk_level']}] | {msg}")
