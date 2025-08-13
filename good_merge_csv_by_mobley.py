import os
import glob
import pandas as pd
import shutil

# Folder containing your CSV files (adjust if needed)
input_folder = "."
output_folder = "merged_output"
os.makedirs(output_folder, exist_ok=True)

# Get all csv files matching pattern rdf_*.csv
files = glob.glob(os.path.join(input_folder, "rdf_*.csv"))

# Group files by mobley ID (e.g. mobley_2661134)
groups = {}
for f in files:
    # Extract mobley pattern: between "mobley_" and ".csv"
    basename = os.path.basename(f)
    start = basename.find("mobley_")
    if start == -1:
        continue
    mobley_id = basename[start:].split(".")[0]  # e.g. "mobley_2661134"
    groups.setdefault(mobley_id, []).append(f)

for mobley_id, file_list in groups.items():
    output_file = os.path.join(output_folder, f"rdf_{mobley_id}.csv")

    if len(file_list) == 1:
        # Only one file: copy it as merged output with new name
        shutil.copy(file_list[0], output_file)
        print(f"Copied single file {file_list[0]} → {output_file}")
    else:
        # Multiple files: merge on 'r (Å)'
        dfs = []
        for f in file_list:
            df = pd.read_csv(f)
            dfs.append(df)
        merged_df = dfs[0]
        for df in dfs[1:]:
            merged_df = pd.merge(merged_df, df, on="r (Å)", how="outer")

        # Sort columns: keep 'r (Å)' first
        cols = merged_df.columns.tolist()
        cols.remove("r (Å)")
        cols = ["r (Å)"] + sorted(cols)
        merged_df = merged_df[cols]

        merged_df.to_csv(output_file, index=False)
        print(f"Merged {len(file_list)} files into {output_file} (columns sorted)")

