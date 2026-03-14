"""
SMS Fraud Detection Model - Training Script
Trains a TF-IDF + Multinomial Naive Bayes classifier on the SMS Spam Collection dataset.
"""

import os
import re
import urllib.request
import zipfile
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__))


def download_dataset():
    """Download the SMS Spam Collection dataset."""
    os.makedirs(DATA_DIR, exist_ok=True)
    dataset_path = os.path.join(DATA_DIR, 'SMSSpamCollection')

    if os.path.exists(dataset_path):
        print("Dataset already exists.")
        return dataset_path

    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
    zip_path = os.path.join(DATA_DIR, 'smsspamcollection.zip')

    print("Downloading SMS Spam Collection dataset...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        os.remove(zip_path)
        print("Dataset downloaded successfully.")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Creating a built-in sample dataset instead...")
        create_sample_dataset(dataset_path)

    return dataset_path


def create_sample_dataset(path):
    """Create a built-in sample dataset if download fails."""
    spam_messages = [
        "WINNER!! As a valued network customer you have been selected to receive a £900 prize reward!",
        "Congratulations! You've won a $1000 Walmart gift card. Click here to claim.",
        "URGENT: Your account has been compromised. Click link to verify now!",
        "Free entry in 2 a weekly competition to win FA Cup final tickets!",
        "You have won £1000 cash prize! Call 09050000 to claim your prize now!",
        "SIX chances to win CASH! From 100 to 20000 pounds txt> CSH11 and send to 87575.",
        "CONGRATULATIONS ur awarded 500 of CD vouchers. Just collect ur vouchers from here.",
        "Had your mobile 11 months or more? U R entitled to Update to the latest models FREE!",
        "Your free ringtone is waiting to be collected. Simply text the password MIX to 85069.",
        "You are a winner U have been selected 2 receive £900 prize. Call 09061701461.",
        "SMS SERVICES for just £2.50 per message sent. Text STOP to 87239 to opt out.",
        "Please call our customer service representative on 0800 169 6031 between 10am-9pm",
        "Win £1000 every week in our weekly competition! Text WIN to 80086 now!",
        "URGENT! We are trying to contact u. Todays draw shows that you have won a £800 prize.",
        "Congrats! 1 year special cinema pass for 2 is yours. Collect at any store & sign up.",
        "Your mobile number has been selected to receive a £350 award! Call 09066382422 now!",
        "Free message: Thanks for subscribing to FantasyTV. Your pin is 6718.",
        "IMPORTANT - You could be ENTITLED to a Government refund. Find out if you qualify.",
        "YOU ARE SELECTED TO RECEIVE A £900 PRIZE! To claim call 09061701461.",
        "Dear winner, you have been selected for a cash prize. Call 09061790121 from any phone.",
        "Alert: Your bank account has unusual activity. Verify at www.fakebank-verify.com now!",
        "FINAL WARNING: Your account will be suspended. Click here immediately to verify.",
        "You've been chosen to receive a FREE iPhone 15! Just pay shipping. Click now!",
        "Your package delivery failed. Pay $1.99 fee to reschedule: bit.ly/fakeshipping",
        "ALERT: Suspicious login detected on your account. Reset password immediately at fakeurl.com",
        "You owe $500 in unpaid taxes. Pay now or face legal action. Call 1-800-FAKE-IRS",
        "Congratulations! Your email won $5,000,000 in the Microsoft Lottery! Send details to claim.",
        "NOTICE: Your SSN has been compromised. Call immediately to protect your identity: 1-800-SCAM",
        "FREE Netflix Premium for 1 year! Click here to activate your free subscription now!",
        "Your Apple ID has been locked. Verify your identity at apple-id-verify-fake.com",
    ]

    ham_messages = [
        "Hey, are we still meeting for dinner tonight at 7?",
        "I'll be there in 10 minutes. Traffic is bad today.",
        "Can you pick up some milk on your way home?",
        "Happy birthday! Hope you have a great day!",
        "The meeting has been rescheduled to 3pm tomorrow.",
        "Thanks for your help yesterday, really appreciated it!",
        "Running late, will be there in 20 mins.",
        "Good morning! Don't forget about the team lunch today.",
        "Just finished the report. I'll email it to you now.",
        "Let me know when you're free to chat about the project.",
        "Mom says dinner is ready. Come home soon!",
        "Got your message. Will call you back after the meeting.",
        "Are you coming to the party this weekend?",
        "The doctor's appointment is confirmed for Monday at 2pm.",
        "Can you send me the address? I'll meet you there.",
        "Just saw your email. I'll review the document tonight.",
        "Sorry I missed your call. What's up?",
        "Let's grab coffee tomorrow morning before work.",
        "The kids are doing well at school. Teacher said great progress!",
        "Reminder: Your dentist appointment is tomorrow at 10am.",
        "Hey! I just got back from vacation. Let's catch up soon.",
        "Thanks for the birthday gift! I love it.",
        "Can you help me move this Saturday? I'll buy pizza!",
        "The weather looks great this weekend. Want to go hiking?",
        "I left my keys at your place. Can I pick them up later?",
        "Practice is cancelled tonight due to rain.",
        "Your prescription is ready for pickup at the pharmacy.",
        "Looking forward to seeing you at the wedding next month!",
        "The plumber is coming between 2-4pm today. Can you be home?",
        "Great job on the presentation today! The client loved it.",
        "Do you have the notes from yesterday's class?",
        "I'm at the store. Do we need anything else?",
        "Lunch was great! We should go there again sometime.",
        "Safe travels! Text me when you land.",
        "Happy anniversary! 10 years and counting!",
        "Can you water my plants while I'm away this week?",
        "The game starts at 8. Want to watch it together?",
        "Just wanted to check in. How are you feeling today?",
        "The car is fixed. You can pick it up after 5pm.",
        "Thanks for babysitting last night. The kids had a blast!",
    ]

    with open(path, 'w', encoding='utf-8') as f:
        for msg in ham_messages:
            f.write(f"ham\t{msg}\n")
        for msg in spam_messages:
            f.write(f"spam\t{msg}\n")

    print(f"Sample dataset created with {len(ham_messages)} ham + {len(spam_messages)} spam messages.")


def preprocess_text(text):
    """Clean and preprocess SMS text."""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' url ', text)
    text = re.sub(r'\b\d{5,}\b', ' longnum ', text)
    text = re.sub(r'£|\$|€', ' currency ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' num ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_data(dataset_path):
    """Load and preprocess the dataset."""
    df = pd.read_csv(dataset_path, sep='\t', header=None, names=['label', 'message'],
                     encoding='latin-1', on_bad_lines='skip')

    print(f"\nDataset loaded: {len(df)} messages")
    print(f"Distribution:\n{df['label'].value_counts()}\n")

    df['cleaned'] = df['message'].apply(preprocess_text)
    df['is_spam'] = (df['label'] == 'spam').astype(int)

    return df


def train_model(df):
    """Train the TF-IDF + Multinomial Naive Bayes model."""
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned'], df['is_spam'], test_size=0.2, random_state=42, stratify=df['is_spam']
    )

    print(f"Training set: {len(X_train)} | Test set: {len(X_test)}")

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Train Multinomial Naive Bayes
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_tfidf, y_train)

    # Evaluate
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"MODEL EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe (Ham)', 'Fraud (Spam)']))
    print(f"Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"{'='*50}\n")

    return model, vectorizer


def save_model(model, vectorizer):
    """Save the trained model and vectorizer."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_path = os.path.join(MODEL_DIR, 'sms_fraud_model.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")


def main():
    print("=" * 60)
    print("  SMS FRAUD DETECTION MODEL - TRAINING")
    print("=" * 60)

    # Step 1: Download/load dataset
    dataset_path = download_dataset()

    # Step 2: Load and preprocess data
    df = load_data(dataset_path)

    # Step 3: Train model
    model, vectorizer = train_model(df)

    # Step 4: Save model
    save_model(model, vectorizer)

    # Step 5: Quick test
    print("\n--- Quick Test ---")
    test_messages = [
        "URGENT: You have won £1000! Call 09050000 to claim now!",
        "Hey, are we still meeting for dinner tonight?",
        "Congratulations! Your account has been selected for a $500 reward. Click here!",
        "Can you pick up the kids from school today?",
        "ALERT: Your bank account has been compromised. Verify now at fakebank.com",
    ]

    from predict import predict_sms
    for msg in test_messages:
        result = predict_sms(msg)
        status = "🚨 FRAUD" if result['label'] == 'spam' else "✅ SAFE"
        print(f"{status} ({result['confidence']:.1f}%) | {msg[:60]}...")

    print("\nTraining complete! Model is ready for deployment.")


if __name__ == '__main__':
    main()
