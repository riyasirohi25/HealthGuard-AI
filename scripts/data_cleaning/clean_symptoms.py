import pandas as pd
import numpy as np
import re
import json
from tqdm import tqdm
from config.config import RAW_SYMPTOM, CLEANED_SYMPTOM

df = pd.read_csv(RAW_SYMPTOM / 'dataset.csv')
df_desc = pd.read_csv(RAW_SYMPTOM / 'symptom_Description.csv')
df_prec = pd.read_csv(RAW_SYMPTOM / 'symptom_precaution.csv')
df_sev  = pd.read_csv(RAW_SYMPTOM / 'Symptom-severity.csv')

print(f"Original shape: {df.shape}")

df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
df_desc.columns = [c.strip().lower().replace(' ', '_') for c in df_desc.columns]
df_prec.columns = [c.strip().lower().replace(' ', '_') for c in df_prec.columns]
df_sev.columns  = [c.strip().lower().replace(' ', '_') for c in df_sev.columns]

def clean_disease_name(name):
    if pd.isna(name): return None
    name = str(name).strip().lower()
    name = re.sub(r'[^a-z0-9 _-]', '', name)
    return re.sub(r'\s+', ' ', name).strip()

def clean_symptom(sym):
    if pd.isna(sym): return None
    sym = str(sym).strip().lower().replace('_', ' ')
    sym = re.sub(r'\s+', ' ', sym).strip()
    return sym if sym else None

df['disease'] = df['disease'].apply(clean_disease_name)
df_desc['disease'] = df_desc['disease'].apply(clean_disease_name)
df_prec['disease'] = df_prec['disease'].apply(clean_disease_name)

symptom_cols = [c for c in df.columns if 'symptom' in c]
for col in symptom_cols:
    df[col] = df[col].apply(clean_symptom)

df = df.dropna(subset=['disease']).drop_duplicates()

sev_lookup = {}
for _, row in df_sev.iterrows():
    sym = clean_symptom(str(row.iloc[0]))
    try: weight = float(row.iloc[1])
    except: weight = 0.0
    if sym: sev_lookup[sym] = weight

records = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    disease = row['disease']
    symptoms = [row[c] for c in symptom_cols if row[c] and row[c] not in ['nan','none','']]
    if not symptoms: continue
    severity_scores = [sev_lookup.get(s, 0.0) for s in symptoms]
    records.append({
        'disease': disease,
        'symptoms': symptoms,
        'symptoms_text': ', '.join(symptoms),
        'symptom_count': len(symptoms),
        'avg_severity': round(np.mean(severity_scores), 3),
        'max_severity': max(severity_scores)
    })

df_clean = pd.DataFrame(records)
df_clean = df_clean.merge(df_desc, on='disease', how='left')

prec_cols = [c for c in df_prec.columns if 'precaution' in c]
df_prec['precautions'] = df_prec[prec_cols].apply(
    lambda row: [str(x).strip() for x in row if pd.notna(x) and str(x).strip()], axis=1)
df_clean = df_clean.merge(df_prec[['disease','precautions']], on='disease', how='left')

disease_list = sorted(df_clean['disease'].unique())
disease2id = {d: i for i, d in enumerate(disease_list)}
df_clean['disease_id'] = df_clean['disease'].map(disease2id)

print(f"Final records: {len(df_clean)}")
print(f"Unique diseases: {df_clean['disease'].nunique()}")

df_clean.to_csv(CLEANED_SYMPTOM / 'symptoms_diseases_clean.csv', index=False)
with open(CLEANED_SYMPTOM / 'disease2id.json', 'w') as f:
    json.dump(disease2id, f, indent=2)
with open(CLEANED_SYMPTOM / 'symptom_severity.json', 'w') as f:
    json.dump(sev_lookup, f, indent=2)
with open(CLEANED_SYMPTOM / 'all_symptoms.json', 'w') as f:
    json.dump(sorted(sev_lookup.keys()), f, indent=2)

print("✅ Done! Files saved to data/cleaned/symptom_disease/")