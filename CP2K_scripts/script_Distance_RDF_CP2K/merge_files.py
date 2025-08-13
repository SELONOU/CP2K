#!/usr/bin/env python3
import glob
import os
import pandas as pd
from collections import defaultdict

# Find all rdf_*.csv files
files = glob.glob("rdf_*_mobley_*.csv")

# Group files by their mobley ID
groups = defaultdict(list)
for f in files:
    # Extract mobley ID (everything after "_mobley_" without .csv)
    mobley_id = f.split("_mobley_")[1].replace(".csv", "")
    groups[mobley_id].append(f)

# Process each group
for mobley_id, flist in groups.items():
    dfs = []
    for filepath in flist:
        df = pd.read_csv(filepath)
        dfs.append(df)

    # Merge all dataframes on the 'r (Å)' column
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on="r (Å)")

    # Save to new file
    output_file = f"rdf_mobley_{mobley_id}.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"Merged {len(flist)} files into {output_file}")

