# ===============================
# MILESTONE 2 : FEATURE ENGINEERING + DATABASE
# ===============================

import pandas as pd
import sqlite3
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


# --------------------------------
# STEP 1 : LOAD DATASET
# --------------------------------

data = pd.read_csv("cleaned_job_posts.csv")

print("Dataset Loaded Successfully\n")
print(data.head())

# make sure column exists
text_data = data["clean_text"].fillna("")

# --------------------------------
# STEP 2 : TF-IDF FEATURE EXTRACTION
# --------------------------------

tfidf_vectorizer = TfidfVectorizer(
        max_features=4000,
        stop_words="english"
)

tfidf_matrix = tfidf_vectorizer.fit_transform(text_data)

pickle.dump(tfidf_vectorizer, open("tfidf_vectorizer.pkl", "wb"))

print("\nTF-IDF Feature Matrix Shape:", tfidf_matrix.shape)


# --------------------------------
# STEP 3 : N-GRAM FEATURE EXTRACTION
# --------------------------------

ngram_vectorizer = CountVectorizer(
        ngram_range=(2,3),
        max_features=120
)

ngram_matrix = ngram_vectorizer.fit_transform(text_data)

print("N-gram Feature Matrix Shape:", ngram_matrix.shape)


# --------------------------------
# STEP 4 : SPARSE MATRIX INFORMATION
# --------------------------------

print("\nSparse Matrix Type:", type(tfidf_matrix))

print("Non-zero values in matrix:", tfidf_matrix.nnz)

density = tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])

print("Matrix Density:", density)


# --------------------------------
# STEP 5 : SAVE FEATURE MATRICES
# --------------------------------

pickle.dump(tfidf_matrix, open("tfidf_features.pkl","wb"))
pickle.dump(ngram_matrix, open("ngram_features.pkl","wb"))

print("\nFeature matrices saved successfully")


# --------------------------------
# STEP 5A : MACHINE LEARNING MODEL (LOGISTIC REGRESSION)
# --------------------------------

# Make sure dataset has label column
if "fraudulent" in data.columns:

    y = data["fraudulent"]

    # Train Logistic Regression model
    model = LogisticRegression(max_iter=1000)

    model.fit(tfidf_matrix, y)

    print("\nLogistic Regression model trained successfully")

    # Save the trained model
    pickle.dump(model, open("fake_job_model.pkl", "wb"))

    print("Machine learning model saved successfully")

else:
    print("\nLabel column not found. Model training skipped.")


# --------------------------------
# STEP 6 : DATABASE CREATION
# --------------------------------

connection = sqlite3.connect("jobs_database.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
description TEXT,
label INTEGER
)
""")

connection.commit()

print("\nDatabase and table created")


# --------------------------------
# STEP 7 : INSERT SAMPLE JOB POSTS
# --------------------------------

sample_jobs = [
("urgent hiring apply now limited offer",1),
("software company hiring experienced developer",0),
("apply immediately exclusive job opportunity",1)
]

cursor.executemany(
"INSERT INTO jobs(description,label) VALUES (?,?)",
sample_jobs
)

connection.commit()

print("Sample job postings inserted")


# --------------------------------
# STEP 8 : READ DATA FROM DATABASE
# --------------------------------

cursor.execute("SELECT * FROM jobs")

print("\nAll Jobs in Database:")
print(cursor.fetchall())


# --------------------------------
# STEP 9 : QUERY FRAUD JOBS
# --------------------------------

cursor.execute("SELECT * FROM jobs WHERE label = 1")

print("\nFraudulent Jobs:")
print(cursor.fetchall())


# --------------------------------
# STEP 10 : UPDATE RECORD
# --------------------------------

cursor.execute(
"UPDATE jobs SET label = 1 WHERE description LIKE '%developer%'"
)

connection.commit()

print("\nRecord Updated")


# --------------------------------
# STEP 11 : DELETE RECORD
# --------------------------------

cursor.execute(
"DELETE FROM jobs WHERE description LIKE '%exclusive%'"
)

connection.commit()

print("Record Deleted")


# --------------------------------
# STEP 12 : CLOSE DATABASE
# --------------------------------

connection.close()

print("\nDatabase connection closed")