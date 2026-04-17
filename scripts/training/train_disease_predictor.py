import json
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config.config import CLEANED_SYMPTOM, DISEASE_MODEL_DIR

# Load data
df = pd.read_csv(CLEANED_SYMPTOM / 'symptoms_diseases_clean.csv')
with open(CLEANED_SYMPTOM / 'all_symptoms.json') as f:
    all_symptoms = json.load(f)
with open(CLEANED_SYMPTOM / 'disease2id.json') as f:
    disease2id = json.load(f)

id2disease = {v: k for k, v in disease2id.items()}

# Build feature matrix
def symptoms_to_vector(symptoms_str, all_symptoms):
    vec = np.zeros(len(all_symptoms))
    if pd.isna(symptoms_str):
        return vec
    syms = [s.strip() for s in str(symptoms_str).split(',')]
    for s in syms:
        if s in all_symptoms:
            vec[all_symptoms.index(s)] = 1
    return vec

print("Building feature matrix...")
X = np.array([symptoms_to_vector(row, all_symptoms) for row in df['symptoms_text']])
y = df['disease_id'].values

print(f"X shape: {X.shape}, y shape: {y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print("Training Random Forest...")
clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")

# Save model
save_path = DISEASE_MODEL_DIR
save_path.mkdir(parents=True, exist_ok=True)

with open(save_path / 'model.pkl', 'wb') as f:
    pickle.dump(clf, f)
with open(save_path / 'all_symptoms.json', 'w') as f:
    json.dump(all_symptoms, f)
with open(save_path / 'disease2id.json', 'w') as f:
    json.dump(disease2id, f)
with open(save_path / 'id2disease.json', 'w') as f:
    json.dump(id2disease, f)

print(f"✅ Done! Model saved to models/disease_predictor/")
print(f"Final accuracy: {acc:.4f}")