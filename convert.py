#!/usr/bin/env python3
import glob
import os
import csv

for filepath in glob.glob("rdf_*.xvg"):
    filename = os.path.basename(filepath)
    csv_filename = filename.replace(".xvg", ".csv")

    # Extract RDF type from filename (between rdf_ and _mobley_)
    try:
        rdf_type = filename.split("rdf_")[1].split("_mobley_")[0]
    except IndexError:
        rdf_type = "g(r)"  # fallback

    with open(filepath, "r") as f_in:
        lines = f_in.readlines()

    data_rows = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(("#", "@")):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                r_nm = float(parts[0])
                gr = float(parts[1])
                r_ang = round(r_nm * 10.0, 5)  # convert nm → Å and round
                data_rows.append([r_ang, gr])
            except ValueError:
                pass

    with open(csv_filename, "w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["r (Å)", rdf_type])
        writer.writerows(data_rows)

    print(f"Converted {filename} → {csv_filename} (column: {rdf_type})")

