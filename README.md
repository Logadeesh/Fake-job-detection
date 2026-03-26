# 🛡️ Fake Job Detection using NLP

A Machine Learning + NLP based web application that detects whether a job posting is **REAL, SUSPICIOUS, or FAKE** using text analysis.

---

## 🚀 Project Overview

This project uses **Natural Language Processing (NLP)** and **Machine Learning** to analyze job descriptions and identify fraudulent postings.

It is built using:
- Python
- Flask (Backend)
- HTML/CSS/JS (Frontend)
- Scikit-learn (ML Model)
- SQLite (Database)

---

## 📌 Features

✅ Detect fake job postings  
✅ Real-time prediction using trained ML model  
✅ Risk score (Fake Probability %)  
✅ Highlight suspicious keywords  
✅ Store results in database  
✅ View history of analyzed jobs  
✅ Clean and modern UI  

---

## 🧠 Project Workflow

### 🔹 Milestone 1: Data Preprocessing
- Removed URLs, emails, numbers
- Lowercasing text
- Stopword removal
- Lemmatization
- Output: `cleaned_job_posts.csv`

---

### 🔹 Milestone 2: Feature Engineering & Model
- TF-IDF Vectorization (4000 features)
- N-gram extraction (bi-grams & tri-grams)
- Logistic Regression model training
- Saved:
  - `fake_job_model.pkl`
  - `tfidf_vectorizer.pkl`

## Dataset

The dataset file (cleaned_job_posts.csv) is not included due to GitHub size limitations.

To use the project:
1. Place your dataset in the folder:
   milestone2_feature_engineering/
2. Run:
   python Feature_pipeline.py

This will generate the required model files.

### 🔹 Milestone 3: Backend (Flask API)
- Built REST APIs:
  - `/predict`
  - `/history`
  - `/stats`
- Model integration
- Database logging (SQLite)

---

### 🔹 Milestone 4: Frontend
- Interactive UI for job input
- Displays:
  - Prediction result
  - Risk score
  - Keywords
- Communicates with backend via API

---

## 📁 Project Structure
Fake-job-detection/
│
├── milestone1_preprocessing/
│ └── main.py
│
├── milestone2_feature_engineering/
│ └── Feature_pipeline.py
│ └── Cleaned_job_posts.csv
│
├── milestone3_frontend/
│ ├── templates/
│ │ └── index.html
│ └── static/
│ ├── style.css
│ └── script.js
│
├── milestone4_backend/
│ ├── app.py
│
├── models/
│ ├── fake_job_model.pkl
│ ├── tfidf_vectorizer.pkl
│ └── ngram_features.pkl
│
├── database/
│ └── jobs_database.db

👨‍💻 Author

Logadeesh

📜 License

This project is licensed under the MIT License.
