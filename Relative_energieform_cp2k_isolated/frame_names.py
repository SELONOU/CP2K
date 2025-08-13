import pandas as pd
from pathlib import Path

def reformat_frame_names_to_4_digits(csv_file):
    df = pd.read_csv(csv_file)

    if 'frame_names' not in df.columns:
        print(f"Skipped {csv_file}: no frame_names column.")
        return

    def format_frame_name(name):
        base, number = name.rsplit("_", 1)
        return f"{base}_{int(number):04d}"

    df['frame_names'] = df['frame_names'].apply(format_frame_name)

    df.to_csv(csv_file, index=False)
    print(f"✅ Updated {csv_file.name} with 4-digit frame numbers.")

# Apply to all CSV files in the current folder
for csv_file in Path('.').glob("*.csv"):
    reformat_frame_names_to_4_digits(csv_file)

