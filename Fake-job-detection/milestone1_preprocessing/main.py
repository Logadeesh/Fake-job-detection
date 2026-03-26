# ================= TEXT CLEANING & DATASET PREPARATION =================

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------- DOWNLOAD NLTK RESOURCES (Run once) ----------------
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# ---------------- LOAD DATASET ----------------
file_path = "DataSet.csv"     # Replace with your file
text_column = "description"      # Replace with your text column

df = pd.read_csv(file_path)

# Keep only text column & remove nulls
label_column = "fraudulent"   # label column in dataset

df = df[[text_column, label_column]].dropna()

print("\n================ BEFORE CLEANING ================\n")
print(df[text_column].head(5))

# ---------------- REGEX CLEANING FUNCTION ----------------
def regex_cleaner(text):
    text = str(text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', ' ', text)

    # Remove Emails
    text = re.sub(r'\S+@\S+', ' ', text)

    # Remove Numbers
    text = re.sub(r'\d+', ' ', text)

    # Remove Special Characters / Punctuation
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Remove Extra Spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

df["clean_text"] = df[text_column].apply(regex_cleaner)

# ---------------- STOPWORD REMOVAL ----------------
stop_words = set(stopwords.words("english"))

def remove_stopwords(text):
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return " ".join(filtered_words)

df["no_stopwords"] = df["clean_text"].apply(remove_stopwords)

# ---------------- LEMMATIZATION ----------------
lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    words = text.split()
    lemmas = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(lemmas)

df["final_text"] = df["no_stopwords"].apply(lemmatize_text)

# ---------------- REMOVE EMPTY ROWS ----------------
df = df[df["final_text"].str.strip() != ""]

print("\n================ AFTER CLEANING ================\n")
print(df["final_text"].head(5))

# ---------------- SAVE CLEANED DATASET ----------------
output_path = "cleaned_job_posts.csv"
df.to_csv(output_path, index=False)

print("\n Text cleaning & dataset preparation completed successfully!")
print(f" Cleaned file saved as: {output_path}")