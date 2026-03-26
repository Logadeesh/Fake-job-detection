from flask import Flask, render_template, request, jsonify
import pickle
import sqlite3
import numpy as np
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

app = Flask(__name__, template_folder="../milestone3_frontend/templates",
            static_folder="../milestone3_frontend/static")

# Load trained model and vectorizer
model = pickle.load(open("../models/fake_job_model.pkl", "rb"))
vectorizer = pickle.load(open("../models/tfidf_vectorizer.pkl", "rb"))

# Preload top features from model coefficients
feature_names = vectorizer.get_feature_names_out()
coefs = model.coef_[0]
top_fake_idx = np.argsort(coefs)[-8:][::-1]
top_real_idx = np.argsort(coefs)[:8]
TOP_FAKE_WORDS = [feature_names[i] for i in top_fake_idx]
TOP_REAL_WORDS = [feature_names[i] for i in top_real_idx]

# Text cleaning (mirrors main.py pipeline)
try:
    import nltk
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
except:
    stop_words = set()
    lemmatizer = None

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    words = [w for w in words if w not in stop_words]
    if lemmatizer:
        words = [lemmatizer.lemmatize(w) for w in words]
    return " ".join(words)

def get_db():
    conn = sqlite3.connect("../database/jobs_database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    raw_description = data.get("description", "")

    # Clean text through the same NLP pipeline
    cleaned = clean_text(raw_description)

    # TF-IDF transform
    features = vectorizer.transform([cleaned])

    # Prediction
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    # Classes: 'f' = False = fraudulent=False = REAL job
    #          't' = True  = fraudulent=True  = FAKE job
    classes = list(model.classes_)
    if 't' in classes:
        fake_prob = float(probability[classes.index('t')])
        is_fake = (prediction == 't')
    elif 1 in classes:
        fake_prob = float(probability[classes.index(1)])
        is_fake = (prediction == 1)
    else:
        fake_prob = float(probability[1])
        is_fake = bool(prediction)

    real_prob = 1.0 - fake_prob
    score = int(fake_prob * 100)

    # Find which trained words appear in this text
    word_set = set(cleaned.split())
    matched_fake = [w for w in TOP_FAKE_WORDS if w in word_set]
    matched_real = [w for w in TOP_REAL_WORDS if w in word_set]

    # Word count of original
    word_count = len(raw_description.split())

    # Log to SQLite
    try:
        conn = get_db()
        cur = conn.cursor()
        label = 1 if is_fake else 0
        cur.execute(
            "INSERT INTO jobs (description, label) VALUES (?, ?)",
            (raw_description[:500], label)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        pass

    # Verdict
    # Convert real probability to percentage
    real_score = int(real_prob * 100)

    # New strict logic
    if real_score >= 70:
         verdict = "REAL"
         result_text = "Highly Likely Legitimate Job"

    elif score >= 60:
         verdict = "FAKE"
         result_text = "Likely Fake Job Post"

    else:
         verdict = "SUSPICIOUS"
         result_text = "Suspicious — Proceed Carefully"

    return jsonify({
        "verdict": verdict,
        "result": result_text,
        "score": score,
        "fake_probability": score,
        "real_probability": int(real_prob * 100),
        "word_count": word_count,
        "matched_fake_keywords": matched_fake[:5],
        "matched_real_keywords": matched_real[:5],
        "cleaned_preview": cleaned[:120] + "..." if len(cleaned) > 120 else cleaned,
    })

@app.route("/history", methods=["GET"])
def history():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, description, label FROM jobs ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify([])

@app.route("/stats", methods=["GET"])
def stats():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM jobs")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) as fake FROM jobs WHERE label = 1")
        fake = cur.fetchone()[0]
        conn.close()
        return jsonify({
            "total": total,
            "fake": fake,
            "real": total - fake,
            "top_fake_words": TOP_FAKE_WORDS[:6],
            "top_real_words": TOP_REAL_WORDS[:6],
        })
    except:
        return jsonify({"total": 0, "fake": 0, "real": 0})

if __name__ == "__main__":
    app.run(debug=True)