import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
from scipy.fft import rfft, rfftfreq
import argparse
import os
import sys

# --- Argument Parser ---
parser = argparse.ArgumentParser(
    description="Compute VDOS from ASE trajectory and log file.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument("traj", help="ASE-readable trajectory file (e.g. .traj, .extxyz)")
parser.add_argument("log", help="Log file with time (ps) and temperature info")
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

# --- Validate files ---
if not os.path.isfile(traj_file):
    print(f"Error: Trajectory file '{traj_file}' not found.")
    sys.exit(1)
if not os.path.isfile(log_file):
    print(f"Error: Log file '{log_file}' not found.")
    sys.exit(1)

# --- Read log file ---
log_data = np.loadtxt(log_file, skiprows=1)
time_ps_all = log_data[:, 1]/1000

# --- Determine frame range ---
start_idx = np.searchsorted(time_ps_all, start_time_ps)
end_idx = len(time_ps_all)
if end_time_ps is not None:
    end_idx = np.searchsorted(time_ps_all, end_time_ps, side='right')
if start_idx >= end_idx:
    print(f"Error: No frames between t = {start_time_ps} ps and {end_time_ps or 'end'} ps")
    sys.exit(1)

log_data = log_data[start_idx:end_idx]
time_ps = log_data[:, 1]/1000
dt_fs = (time_ps[1] - time_ps[0])*1000 
nsteps = len(time_ps)
temperature = log_data[0, 3]



print(f"Time window: {start_time_ps} → {end_time_ps or time_ps[-1]:.3f} ps | dt = {dt_fs:.3f} fs | Steps = {nsteps} | T = {temperature:.1f} K")

# --- Read trajectory ---
images = read(traj_file, index=":")
if len(images) != len(np.loadtxt(log_file, skiprows=1)):
    print("Warning: trajectory and log file may be inconsistent in frame count.")
images = images[start_idx:end_idx]

# --- Velocities ---
natoms = len(images[0])
velocities = np.array([img.get_velocities() for img in images])

# --- Atom selection ---
if atom_indices is not None:
    velocities = velocities[:, atom_indices, :]
    print(f"Using atom indices: {atom_indices}")

# --- Mass weighting ---
if mass_weighted:
    masses = images[0].get_masses()
    if atom_indices is not None:
        masses = masses[atom_indices]
    weights = np.sqrt(masses[:, np.newaxis])
    velocities *= weights[np.newaxis, :, :]
    print("Applied mass weighting")

# --- Flatten and remove drift ---
vel_flat = velocities.reshape(nsteps, -1)
vel_flat -= vel_flat.mean(axis=0)

# --- VACF ---
vacf = np.correlate(vel_flat[:,0], vel_flat[:,0], mode="full")
for i in range(1, vel_flat.shape[1]):
    vacf += np.correlate(vel_flat[:,i], vel_flat[:,i], mode="full")
vacf = vacf[vacf.size // 2:] / (nsteps - np.arange(nsteps))

# --- FFT → VDOS ---
dt_ps = dt_fs * 1e-3
frequencies = rfftfreq(nsteps, dt_ps)
vdos = np.abs(rfft(vacf))
frequencies_cm1 = frequencies * 33.356

# --- Plot ---
plt.figure(figsize=(6,4))
plt.plot(frequencies_cm1, vdos, color="royalblue", lw=1)
plt.xlim(0, 4000)
plt.xlabel("Frequency (cm$^{-1}$)")
plt.ylabel("VDOS (a.u.)")
plt.title(f"VDOS (T = {temperature:.1f} K, t = {start_time_ps}-{end_time_ps or time_ps[-1]:.2f} ps)")
plt.grid(True)
plt.tight_layout()

# --- Save or Show ---
base_name = os.path.splitext(os.path.basename(traj_file))[0]
png_name = f"vdos_{base_name}_{start_time_ps}-{end_time_ps or 'end'}.png"
if show_plot:
    plt.show()
else:
    plt.savefig(png_name, dpi=300)
    print(f"Saved VDOS plot to: {png_name}")
    
# --- Write to XVG format (GROMACS-style) ---
xvg_filename = f"vdos_{base_name}_{start_time_ps}-{end_time_ps or 'end'}.xvg"

with open(xvg_filename, "w") as f:
    from datetime import datetime
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    # Header
    f.write(f"# This file was created {now}\n")
    f.write("# Created by: ASE-based VDOS script\n")
    f.write("#\n")
    f.write("@    title \"Density of states\"\n")
    f.write("@    xaxis  label \"E (cm\\S-1\\N)\"\n")
    f.write("@    yaxis  label \"S(n)\"\n")
    f.write("@TYPE xy\n")
    f.write("@ view 0.15, 0.15, 0.75, 0.85\n")
    f.write("@ legend on\n")
    f.write("@ legend box on\n")
    f.write("@ legend loctype view\n")
    f.write("@ legend 0.78, 0.8\n")
    f.write("@ legend length 1\n")
    f.write("@ s0 legend \"DoS(v)\"\n")

    # Data
    for freq, val in zip(frequencies_cm1, vdos):
        f.write(f"{freq:12.6f} {val:12.6f}\n")

print(f"Saved VDOS data to: {xvg_filename}")


