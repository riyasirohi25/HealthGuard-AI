import json
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config.config import CLEANED_QA, QA_MODEL_DIR

# Load all QA data
print("Loading QA datasets...")
dfs = []

medquad = pd.read_csv(CLEANED_QA / 'medquad_clean.csv')
medquad = medquad[['question', 'answer']].dropna()
dfs.append(medquad)
print(f"MedQuAD: {len(medquad)} records")

medqa = pd.read_csv(CLEANED_QA / 'medqa_clean.csv')
medqa = medqa[['question', 'answer']].dropna()
dfs.append(medqa)
print(f"MedQA: {len(medqa)} records")

df = pd.concat(dfs, ignore_index=True)
df = df.drop_duplicates(subset=['question'])
df = df[df['question'].str.len() >= 10]
df = df[df['answer'].str.len() >= 10]
df = df.reset_index(drop=True)
print(f"Total QA pairs: {len(df)}")

# Build TF-IDF index
print("Building TF-IDF index...")
vectorizer = TfidfVectorizer(
    max_features=50000,
    ngram_range=(1, 2),
    stop_words='english',
    min_df=2
)
tfidf_matrix = vectorizer.fit_transform(df['question'])
print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

def search_qa(query, top_k=3):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_indices:
        if scores[idx] > 0.01:
            results.append({
                'question': df.iloc[idx]['question'],
                'answer': df.iloc[idx]['answer'],
                'score': round(float(scores[idx]), 4)
            })
    return results

# Test it
print("\nTesting QA engine...")
test_queries = [
    "What are symptoms of diabetes?",
    "How is hypertension treated?",
    "What causes anemia?"
]
for q in test_queries:
    results = search_qa(q, top_k=1)
    if results:
        print(f"Q: {q}")
        print(f"A: {results[0]['answer'][:100]}...")
        print()

# Save
QA_MODEL_DIR.mkdir(parents=True, exist_ok=True)
with open(QA_MODEL_DIR / 'vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
with open(QA_MODEL_DIR / 'tfidf_matrix.pkl', 'wb') as f:
    pickle.dump(tfidf_matrix, f)
df.to_csv(QA_MODEL_DIR / 'qa_database.csv', index=False)

print("✅ Done! QA engine saved to models/qa_engine/")