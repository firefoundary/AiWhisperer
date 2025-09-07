import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FILE_1 = RAW_DIR / "Prompt_Examples.csv"
FILE_2 = RAW_DIR / "prompt_examples_dataset.csv"
COMBINED_FILE = PROCESSED_DIR / "combined_prompts.csv"

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Replace commas with semicolons to avoid CSV column split
    text = text.replace(',', ';')
    # Remove newlines and carriage returns
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Strip leading/trailing whitespace
    return text.strip()

def format_prompt_examples(df):
    df_out = pd.DataFrame()
    df_out['user_input'] = df['original_prompt'].astype(str).apply(clean_text)
    # Use V1_Prompt fallback to Base_Prompt if missing
    df_out['optimized_prompt'] = df.apply(
        lambda row: clean_text(row['V1_Prompt']) if pd.notna(row['V1_Prompt']) else clean_text(row['Base_Prompt']), axis=1)
    df_out['category'] = "general"
    df_out['source'] = "Prompt_Examples"
    return df_out[df_out['user_input'].str.len() > 5]

def format_prompt_examples_dataset(df):
    df_out = pd.DataFrame()
    df_out['user_input'] = df.apply(
        lambda row: clean_text(row['bad_prompt']) if pd.notna(row['bad_prompt']) else clean_text(row['task_description']), axis=1)
    df_out['optimized_prompt'] = df['good_prompt'].astype(str).apply(clean_text)
    df_out['category'] = df['prompt_type'].fillna('general').astype(str)
    df_out['source'] = "prompt_examples_dataset"
    return df_out[df_out['user_input'].str.len() > 5]

if FILE_1.exists():
    df1 = pd.read_csv(FILE_1)
    df1_out = format_prompt_examples(df1)
else:
    df1_out = pd.DataFrame()

if FILE_2.exists():
    df2 = pd.read_csv(FILE_2)
    df2_out = format_prompt_examples_dataset(df2)
else:
    df2_out = pd.DataFrame()

combined_df = pd.concat([df1_out, df2_out], ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=['user_input', 'optimized_prompt'])

if not combined_df.empty:
    combined_df.to_csv(COMBINED_FILE, index=False)
    print(f"✅ Combined file saved to {COMBINED_FILE} with {len(combined_df)} clean examples.")
else:
    print("⚠️ No valid data found in either file.")
