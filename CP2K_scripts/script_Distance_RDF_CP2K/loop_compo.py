#!/usr/bin/env python3

import subprocess
import os
from ase.io import read

# --- Input XYZ file ---
xyz_file = "mobley_3269565-pos-1.xyz"

# --- Extract base name (e.g., 'mobley_6091882') from file ---
basename = os.path.basename(xyz_file)
prefix = basename.split("-")[0]  # 'mobley_6091882'

# --- Read first frame and get atom types ---
atoms = read(xyz_file, index=0)
n_atoms = len(atoms)
symbols = atoms.get_chemical_symbols()

# --- Loop over all unique atom index pairs ---
for i in range(n_atoms - 1):
    for j in range(i + 1, n_atoms):
        elem_i = symbols[i]
        elem_j = symbols[j]

        outfile = f"dist_{elem_i}{i}_{elem_j}{j}_{prefix}.csv"
        plotfile = f"plot_{elem_i}{i}_{elem_j}{j}_{prefix}.png"

        cmd = [
            "python",
            "Track_specific_pair_cp2k_xyz.py",
            xyz_file,
            "--i", str(i),
            "--j", str(j),
            "--dt", "0.5",
            "--outfile", outfile,
            "--plotfile", plotfile
        ]

        print("Running:", " ".join(cmd))
        subprocess.run(cmd)

