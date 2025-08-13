#!/usr/bin/env python3
import glob
import os
import pandas as pd

# Loop over all matching CSV files
for filepath in glob.glob("rdf_*_mobley_*.csv"):
    filename = os.path.basename(filepath)

    # Extract the type between "rdf_" and "_mobley_"
    try:
        type_name = filename.split("rdf_")[1].split("_mobley_")[0]
    except IndexError:
        print(f"Skipping {filename} (unexpected format)")
        continue

    # Read CSV
    df = pd.read_csv(filepath)

    # Ensure the second column is renamed
    if df.columns.size >= 2:
        df.columns = [df.columns[0], type_name]
    else:
        print(f"Skipping {filename} (not enough columns)")
        continue

    # Save back to the same file
    df.to_csv(filepath, index=False)

    print(f"Updated header in {filename} → second column renamed to '{type_name}'")

