#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
from scipy.fft import rfft, rfftfreq
import argparse
import os
import sys
import tempfile

def clean_velocity_xyz(infile):
    """
    Reads the input velocity .xyz file with extra comment lines and
    writes a temporary clean .xyz file with standard XYZ format so
    ASE can read frames properly.
    """
    clean_lines = []
    with open(infile, 'r') as f:
        lines = f.readlines()

    i = 0
    nlines = len(lines)
    while i < nlines:
        n_atoms_line = lines[i].strip()
        if not n_atoms_line.isdigit():
            print(f"Error parsing atom count at line {i}: {n_atoms_line}")
            sys.exit(1)
        n_atoms = int(n_atoms_line)
        clean_lines.append(f"{n_atoms}\n")
        i += 1

        if i < nlines:
            clean_lines.append("frame\n")
            i += 1
        else:
            print("Unexpected EOF after atom count")
            sys.exit(1)

        for _ in range(n_atoms):
            if i < nlines:
                clean_lines.append(lines[i])
                i += 1
            else:
                print("Unexpected EOF in atom block")
                sys.exit(1)

    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xyz')
    tmp.writelines(clean_lines)
    tmp.close()
    return tmp.name

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Compute VDOS from ASE trajectory and log file.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("traj", help="Velocity XYZ trajectory file (may contain extra comment lines)")
parser.add_argument("log", help="Log file with time (fs) and temperature info")
parser.add_argument("-b", "--begin", type=float, default=0.0, help="Start time in ps")
parser.add_argument("-e", "--end", type=float, default=None, help="End time in ps")
parser.add_argument("-mw", "--mass_weighted", action="store_true", help="Use mass-weighted velocities")
parser.add_argument("-a", "--atoms", nargs="+", type=int, default=None, help="Atom indices to include (e.g. -a 0 1 2)")
parser.add_argument("--plt", action="store_true", help="Show interactive plot (otherwise save to PNG)")
args = parser.parse_args()

traj_file = args.traj
log_file = args.log
mass_weighted = args.mass_weighted
atom_indices = args.atoms
start_time_ps = args.begin
end_time_ps = args.end
show_plot = args.plt

if not os.path.isfile(traj_file):
    print(f"Error: Trajectory file '{traj_file}' not found.")
    sys.exit(1)
if not os.path.isfile(log_file):
    print(f"Error: Log file '{log_file}' not found.")
    sys.exit(1)

log_data = np.loadtxt(log_file, skiprows=1)
time_ps_all = log_data[:, 1] / 1000.0

clean_xyz_file = clean_velocity_xyz(traj_file)
images = read(clean_xyz_file, index=":")

if len(images) < len(time_ps_all):
    print(f"Truncating log file: {len(time_ps_all)} → {len(images)} frames to match trajectory")
    time_ps_all = time_ps_all[:len(images)]
    log_data = log_data[:len(images), :]

start_idx = np.searchsorted(time_ps_all, start_time_ps)
end_idx = len(time_ps_all)
if end_time_ps is not None:
    end_idx = np.searchsorted(time_ps_all, end_time_ps, side='right')
if start_idx >= end_idx:
    print(f"Error: No frames between t = {start_time_ps} ps and {end_time_ps or 'end'} ps")
    os.unlink(clean_xyz_file)
    sys.exit(1)

log_data_sel = log_data[start_idx:end_idx]
time_ps = time_ps_all[start_idx:end_idx]
nsteps = len(time_ps)
temperature = log_data_sel[0, 3]
if nsteps < 2:
    print("Error: Need at least two frames in selected time window")
    os.unlink(clean_xyz_file)
    sys.exit(1)

dt_fs = (time_ps[1] - time_ps[0]) * 1000.0
print(f"Time window: {start_time_ps} → {end_time_ps or time_ps[-1]:.3f} ps | dt = {dt_fs:.3f} fs | Steps = {nsteps} | T = {temperature:.1f} K")

natoms = len(images[0])

velocities = []
with open(clean_xyz_file, 'r') as f:
    lines = f.readlines()

n_atoms = int(lines[0])
n_lines_per_frame = n_atoms + 2
n_frames = len(lines) // n_lines_per_frame

if n_frames != len(time_ps_all):
    print(f"Warning: velocity frames ({n_frames}) and log entries ({len(time_ps_all)}) mismatch")

for i in range(n_frames):
    frame_lines = lines[i * n_lines_per_frame + 2 : (i + 1) * n_lines_per_frame]
    frame_vels = []
    for line in frame_lines:
        parts = line.strip().split()
        if len(parts) != 4:
            print(f"Error: Expected format 'Atom vx vy vz', got: {line}")
            os.unlink(clean_xyz_file)
            sys.exit(1)
        vx, vy, vz = map(float, parts[1:])
        frame_vels.append([vx, vy, vz])
    velocities.append(frame_vels)

velocities = np.array(velocities)
if velocities.shape[0] < end_idx:
    print(f"Error: Not enough frames in velocity file ({velocities.shape[0]}), needed up to {end_idx}")
    os.unlink(clean_xyz_file)
    sys.exit(1)

velocities = velocities[start_idx:end_idx]
nsteps = velocities.shape[0]

if atom_indices is not None:
    velocities = velocities[:, atom_indices, :]

if mass_weighted:
    masses = images[0].get_masses()
    if atom_indices is not None:
        masses = masses[atom_indices]
    if (masses <= 0).any():
        print("Warning: Some atomic masses are zero or negative, skipping mass weighting!")
    else:
        weights = np.sqrt(masses)
        for iatom in range(len(weights)):
            velocities[:, iatom, :] *= weights[iatom]

vel_flat = velocities.reshape(nsteps, -1)
vel_flat -= vel_flat.mean(axis=0)

vacf = np.correlate(vel_flat[:, 0], vel_flat[:, 0], mode="full")
for i in range(1, vel_flat.shape[1]):
    vacf += np.correlate(vel_flat[:, i], vel_flat[:, i], mode="full")
vacf = vacf[vacf.size // 2:] / (nsteps - np.arange(nsteps))

dt_ps = dt_fs * 1e-3
frequencies = rfftfreq(nsteps, dt_ps)
vdos = np.abs(rfft(vacf))
frequencies_cm1 = frequencies * 33.356

plt.figure(figsize=(6, 4))
plt.plot(frequencies_cm1, vdos, color="royalblue", lw=1)
plt.xlim(0, 4000)
plt.xlabel("Frequency (cm$^{-1}$)")
plt.ylabel("VDOS (a.u.)")
plt.title(f"VDOS (T = {temperature:.1f} K, t = {start_time_ps}-{end_time_ps or time_ps[-1]:.2f} ps)")
plt.grid(True)
plt.tight_layout()

base_name = os.path.splitext(os.path.basename(traj_file))[0]
time_range_str = f"{start_time_ps}-{end_time_ps or 'end'}"
png_name = f"vdos_{base_name}_{time_range_str}.png"

if show_plot:
    plt.show()
else:
    plt.savefig(png_name, dpi=300)
    print(f"Saved VDOS plot to: {png_name}")

xvg_filename = f"vdos_{base_name}_{time_range_str}.xvg"
with open(xvg_filename, "w") as f:
    from datetime import datetime
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    f.write(f"# This file was created {now}\n")
    f.write("# Created by: ASE-based VDOS script\n")
    f.write("#\n")
    f.write("@    title \"Density of states\"\n")
    f.write("@    xaxis  label \"Frequency (cm^-1)\"\n")
    f.write("@    yaxis  label \"VDOS (a.u.)\"\n")
    f.write("@TYPE xy\n")
    f.write("@ view 0.15, 0.15, 0.75, 0.85\n")
    f.write("@ legend on\n")
    f.write("@ legend box on\n")
    f.write("@ legend loctype view\n")
    f.write("@ legend 0.78, 0.8\n")
    f.write("@ legend length 1\n")
    f.write("@ s0 legend \"DoS(v)\"\n")
    for freq, val in zip(frequencies_cm1, vdos):
        f.write(f"{freq:12.6f} {val:12.6f}\n")
print(f"Saved VDOS data to: {xvg_filename}")
os.unlink(clean_xyz_file)

