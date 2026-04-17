import os
import re
import json
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
from config.config import RAW_MEDQUAD, CLEANED_QA

def clean_text(text):
    if not text: return None
    text = str(text).strip()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x20-\x7E]', '', text)
    return text.strip() if len(text.strip()) > 5 else None

def parse_medquad_xml(filepath):
    records = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        doc_id = root.get('id', '')
        source = root.get('source', '')
        focus = root.findtext('Focus', default='')
        for qa_pair in root.findall('.//QAPair'):
            question = clean_text(qa_pair.findtext('Question', default=''))
            answer = clean_text(qa_pair.findtext('Answer', default=''))
            if not question or not answer or len(answer) < 20:
                continue
            records.append({
                'id': f"{doc_id}_{qa_pair.get('pid', '')}",
                'source': source,
                'focus': clean_text(focus),
                'question': question,
                'answer': answer
            })
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return records

all_records = []
for root_dir, dirs, files in tqdm(os.walk(RAW_MEDQUAD), desc="Scanning"):
    for fname in files:
        if fname.endswith('.xml'):
            records = parse_medquad_xml(os.path.join(root_dir, fname))
            all_records.extend(records)

print(f"Total QA pairs extracted: {len(all_records)}")

df = pd.DataFrame(all_records)
df = df.drop_duplicates(subset=['question', 'answer'])
df = df[df['question'].str.len() >= 10]
df = df[df['answer'].str.len() >= 20]
df = df.reset_index(drop=True)

print(f"Final records: {len(df)}")

df.to_csv(CLEANED_QA / 'medquad_clean.csv', index=False)
with open(CLEANED_QA / 'medquad_clean.jsonl', 'w') as f:
    for _, row in df.iterrows():
        f.write(json.dumps(row.to_dict()) + '\n')

print("✅ Done! Files saved to data/cleaned/qa_datasets/")