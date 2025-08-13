#!/usr/bin/env python3

#import numpy as np
#import matplotlib.pyplot as plt
#from ase.io import read
#import argparse

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Fix for X11 connection issues
import matplotlib.pyplot as plt
from ase.io import read
import argparse

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Compute RDF between two atom types from CP2K XYZ trajectory")
parser.add_argument("xyz_file", help="CP2K-style .xyz trajectory file")
parser.add_argument("--pair", nargs=2, default=["C", "H"], help="Atomic symbols of the pair to compute RDF (e.g., C H)")
parser.add_argument("--rmax", type=float, default=5.0, help="Maximum distance (Å) for RDF")
parser.add_argument("--nbins", type=int, default=200, help="Number of histogram bins")
parser.add_argument("--box", type=float, default=14.0, help="Length of cubic box in Å (for NVT)")
parser.add_argument("--outfile", default="rdf.csv", help="CSV output for RDF")
parser.add_argument("--plotfile", default="rdf_plot.png", help="Output image for RDF plot")
args = parser.parse_args()

# --- Constants ---
volume = args.box ** 3
r_max = args.rmax
n_bins = args.nbins
dr = r_max / n_bins
r_edges = np.linspace(0, r_max, n_bins + 1)
r_centers = 0.5 * (r_edges[1:] + r_edges[:-1])
rdf = np.zeros(n_bins)

# --- Load trajectory ---
atoms_list = read(args.xyz_file, index=":")
n_frames = len(atoms_list)
first_frame = atoms_list[0]

# --- Select atom indices ---
indices_a = [i for i, atom in enumerate(first_frame) if atom.symbol == args.pair[0]]
indices_b = [i for i, atom in enumerate(first_frame) if atom.symbol == args.pair[1]]
n_a = len(indices_a)
n_b = len(indices_b)

print(f"Computing RDF for {args.pair[0]}–{args.pair[1]} in a box of size {args.box} Å (volume = {volume} Å³)")
print(f"Found {n_a} atoms of type {args.pair[0]} and {n_b} of type {args.pair[1]}")

# --- Accumulate histogram ---
for atoms in atoms_list:
    pos = atoms.get_positions()
    for i in indices_a:
        for j in indices_b:
            if i == j:
                continue
            rij = pos[j] - pos[i]
            rij = rij - args.box * np.round(rij / args.box)  # Apply minimum image convention
            dist = np.linalg.norm(rij)
            if dist < r_max:
                bin_idx = int(dist / dr)
                rdf[bin_idx] += 1

# --- Normalize RDF ---
shell_volumes = (4/3) * np.pi * (r_edges[1:]**3 - r_edges[:-1]**3)
number_density = n_b / volume  # density of "B" atoms
normalization = n_frames * n_a * number_density * shell_volumes
rdf_normalized = rdf / normalization

# --- Save RDF to CSV ---
with open(args.outfile, "w") as f:
    f.write("r (Å),g(r)\n")
    for r, g in zip(r_centers, rdf_normalized):
        f.write(f"{r:.5f},{g:.5f}\n")

print(f"RDF written to {args.outfile}")

# --- Plot RDF ---
plt.figure(figsize=(8, 5))
plt.plot(r_centers, rdf_normalized, label=f"{args.pair[0]}–{args.pair[1]}")
plt.xlabel("r (Å)", fontsize=14)
plt.ylabel("g(r)", fontsize=14)
plt.title(f"Radial Distribution Function of {args.pair[0]}–{args.pair[1]}", fontsize=16)
#plt.title("Radial Distribution Function of O O", fontsize=16)
plt.grid(True)
plt.tight_layout()
plt.savefig(args.plotfile, dpi=300)
print(f"RDF plot saved to {args.plotfile}")

