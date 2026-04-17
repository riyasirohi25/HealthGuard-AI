import json
import re
import pandas as pd
from tqdm import tqdm
from config.config import RAW_MEDQA, CLEANED_QA

def clean_text(text):
    if not text: return None
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x20-\x7E]', '', text)
    return text.strip() if len(text.strip()) > 5 else None

all_records = []
for split in ['train.jsonl', 'dev.jsonl', 'test.jsonl']:
    filepath = RAW_MEDQA / split
    if not filepath.exists():
        print(f"Missing: {split}")
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc=split):
            try:
                item = json.loads(line)
                question = clean_text(item.get('question', ''))
                answer_key = item.get('answer_idx', item.get('answer', ''))
                options = item.get('options', {})
                answer_text = clean_text(options.get(answer_key, ''))
                if not question or not answer_text:
                    continue
                all_records.append({
                    'question': question,
                    'answer': answer_text,
                    'answer_key': answer_key,
                    'options': json.dumps(options),
                    'split': split.replace('.jsonl', '')
                })
            except: continue

print(f"Total records: {len(all_records)}")
df = pd.DataFrame(all_records).drop_duplicates(subset=['question'])
df.to_csv(CLEANED_QA / 'medqa_clean.csv', index=False)
with open(CLEANED_QA / 'medqa_clean.jsonl', 'w') as f:
    for _, row in df.iterrows():
        f.write(json.dumps(row.to_dict()) + '\n')
print("✅ Done!")