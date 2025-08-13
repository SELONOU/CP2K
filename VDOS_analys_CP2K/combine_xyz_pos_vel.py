#!/usr/bin/env python3

import sys

if len(sys.argv) != 4:
    print("Usage: python combine_xyz_pos_vel.py pos.xyz vel.xyz output_combined.xyz")
    sys.exit(1)

pos_file, vel_file, out_file = sys.argv[1:]

with open(pos_file, 'r') as f_pos, open(vel_file, 'r') as f_vel, open(out_file, 'w') as f_out:
    pos_lines = f_pos.readlines()
    vel_lines = f_vel.readlines()

    n_atoms = int(pos_lines[0].strip())
    nlines_per_frame = n_atoms + 2
    n_frames = len(pos_lines) // nlines_per_frame

    if len(pos_lines) != len(vel_lines):
        print("Error: Files don't have the same number of lines")
        sys.exit(1)

    for i in range(n_frames):
        # Write atom count and comment
        f_out.write(pos_lines[i * nlines_per_frame])
        f_out.write("Combined positions and velocities\n")

        # Combine atom lines
        for j in range(n_atoms):
            pos_parts = pos_lines[i * nlines_per_frame + 2 + j].split()
            vel_parts = vel_lines[i * nlines_per_frame + 2 + j].split()

            if pos_parts[0] != vel_parts[0]:
                print(f"Warning: Atom mismatch at frame {i}, atom {j}")

            atom = pos_parts[0]
            x, y, z = pos_parts[1:4]
            vx, vy, vz = vel_parts[1:4]
            f_out.write(f"{atom} {x} {y} {z} {vx} {vy} {vz}\n")

