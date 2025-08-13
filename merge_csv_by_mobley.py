#!/usr/bin/env python3
import glob
import os
import pandas as pd
from collections import defaultdict

# Gather all csv files
csv_files = glob.glob("rdf_*.csv")

# Group files by mobley pattern
groups = defaultdict(list)
for f in csv_files:
    # Extract mobley ID (e.g. mobley_2661134)
    try:
        mobley_id = f.split("mobley_")[1].split(".csv")[0]
        groups[mobley_id].append(f)
    except IndexError:
        pass

for mobley_id, files in groups.items():
    if len(files) == 1:
        print(f"Skipping {mobley_id} (only one file)")
        continue

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)

    # Merge all dataframes on 'r (Å)' column
    from functools import reduce
    df_merged = reduce(lambda left, right: pd.merge(left, right, on="r (Å)"), dfs)

    # Sort columns: r (Å) first, then alphabetically
    cols = df_merged.columns.tolist()
    cols.remove("r (Å)")
    cols_sorted = ["r (Å)"] + sorted(cols)
    df_merged = df_merged[cols_sorted]

    outname = f"rdf_mobley_{mobley_id}.csv"
    df_merged.to_csv(outname, index=False)
    print(f"Merged {len(files)} files into {outname} (columns sorted)")

