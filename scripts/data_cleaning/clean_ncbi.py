import re
import json
import pandas as pd
from tqdm import tqdm
from config.config import RAW_NCBI, CLEANED_QA

def parse_ncbi_file(filepath):
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        sentences = re.split(r'\n\n+', content.strip())
        for block in sentences:
            if not block.strip():
                continue
            lines = block.strip().split('\n')
            if len(lines) < 2:
                continue
            text = lines[0].strip()
            entities = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 4:
                    entities.append({
                        'start': parts[0],
                        'end': parts[1],
                        'mention': parts[2],
                        'type': parts[3]
                    })
            if text and entities:
                records.append({
                    'text': text,
                    'entities': json.dumps(entities),
                    'entity_count': len(entities)
                })
    except Exception as e:
        print(f"Error: {e}")
    return records

all_records = []
for fname in RAW_NCBI.glob('*.txt'):
    print(f"Processing {fname.name}...")
    records = parse_ncbi_file(fname)
    all_records.extend(records)
    print(f"  Got {len(records)} records")

print(f"Total records: {len(all_records)}")
df = pd.DataFrame(all_records).drop_duplicates(subset=['text'])
df.to_csv(CLEANED_QA / 'ncbi_clean.csv', index=False)
print("✅ Done!")