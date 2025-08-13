#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
import argparse
import csv

# --- Argument Parser ---
# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Track a specific interatomic distance over time from CP2K XYZ trajectory")
parser.add_argument("xyz_file", help="CP2K-style .xyz trajectory file")
parser.add_argument("--dt", type=float, default=0.5, help="Time step in fs")
parser.add_argument("--i", type=int, required=True, help="Index of first atom (0-based)")
parser.add_argument("--j", type=int, required=True, help="Index of second atom (0-based)")
parser.add_argument("--outfile", required=True, help="CSV output file for distances")
parser.add_argument("--plotfile", required=True, help="Plot output image file")
args = parser.parse_args()

# --- Load Trajectory ---
atoms_list = read(args.xyz_file, index=":")
n_steps = len(atoms_list)
time_fs = np.arange(n_steps) * args.dt
distances = []

# --- Compute distances over time ---
for atoms in atoms_list:
    dist = atoms.get_distance(args.i, args.j)
    distances.append(dist)

# --- Save to CSV ---
with open(args.outfile, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Time (fs)", f"Distance_{args.i}-{args.j} (Å)"])
    for t, d in zip(time_fs, distances):
        writer.writerow([t, d])

print(f"Distance saved to: {args.outfile}")

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(time_fs, distances, label=f"Atom {args.i} – Atom {args.j}")
plt.xlabel("Time (fs)", fontsize=14)
plt.ylabel("Distance (Å)", fontsize=14)
plt.title(f"Distance between atom {args.i} and atom {args.j} over time", fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(args.plotfile, dpi=300)
print(f"Plot saved to: {args.plotfile}")

