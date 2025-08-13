#!/usr/bin/env python3

import subprocess
import os
from itertools import combinations_with_replacement
from ase.io import read

# --- Input file ---
xyz_file = "mobley_5631798-pos-1.xyz"  # Change to your actual filename
box_length = 14.0
rmax = 10.0
nbins = 200

# --- Extract base name (e.g., mobley_7378987) ---
basename = os.path.basename(xyz_file)
prefix = basename.split("-")[0]

# --- Read first frame to detect atom types ---
atoms = read(xyz_file, index=0)
atom_types = sorted(set(atom.symbol for atom in atoms))

print(f"Found atom types: {atom_types}")
print("Starting RDF calculations for all unique pairs...")

# --- Loop over all unique pairs (including A–A) ---
for a1, a2 in combinations_with_replacement(atom_types, 2):
    outfile = f"rdf_{a1}-{a2}_{prefix}.csv"
    plotfile = f"rdf_plot_{a1}-{a2}_{prefix}.png"

    cmd = [
        "python",
        "RDF_cp2k_xyz.py",
        xyz_file,
        "--pair", a1, a2,
        "--box", str(box_length),
        "--rmax", str(rmax),
        "--nbins", str(nbins),
        "--outfile", outfile,
        "--plotfile", plotfile
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

print("✅ All RDF calculations completed.")

