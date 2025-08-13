import os
import re
import csv

HARTREE_TO_KCAL_MOL = 627.509474  # conversion factor

def extract_final_energy(log_path):
    """
    Extracts the last SCF Done energy from a Gaussian .log file.
    """
    energy = None
    with open(log_path, 'r') as f:
        for line in f:
            if 'SCF Done' in line:
                match = re.search(r'SCF Done:\s+E\(\w+\)\s+=\s+(-?\d+\.\d+)', line)
                if match:
                    energy = float(match.group(1))
    return energy

def get_frame_number(file_name):
    """
    Extracts frame number and returns it as an integer.
    """
    match = re.search(r'_frame_(\d+)', file_name)
    return int(match.group(1)) if match else None

def main():
    directory = '.'  # current directory
    log_files = [f for f in os.listdir(directory) if f.endswith('.log')]
    
    # Sort files by frame number
    log_files.sort(key=lambda f: get_frame_number(f) if get_frame_number(f) is not None else float('inf'))
    
    energies = []
    frame0_energy_kcal = None

    for log_file in log_files:
        log_path = os.path.join(directory, log_file)
        energy_hartree = extract_final_energy(log_path)
        if energy_hartree is None:
            continue  # skip if energy couldn't be extracted

        energy_kcal = energy_hartree * HARTREE_TO_KCAL_MOL
        frame_number = get_frame_number(log_file)
        frame_name = re.sub(r'\.log$', '', log_file)
        frame_name = re.sub(r'_frame_(\d+)', lambda m: f"_frame_{int(m.group(1)):04d}", frame_name)

        if frame_number == 0:
            frame0_energy_kcal = energy_kcal

        energies.append((frame_name, energy_kcal))

    if frame0_energy_kcal is None:
        print("Frame 0 energy not found. Check if mobley_..._frame_0.log exists and is correctly formatted.")
        return

    # Write to CSV
    with open('relative_energies_log_mobley_2661134.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame_names', 'Final_energy_frame_0 (kcal/mol)', 'State_Final_Energy (kcal/mol)', 'Relative_energy (kcal/mol)'])
        for frame_name, energy_kcal in energies:
            rel_energy = energy_kcal - frame0_energy_kcal
            writer.writerow([frame_name, frame0_energy_kcal, energy_kcal, rel_energy])

    print("✅ Done: Output written to relative_energies.csv (in kcal/mol)")

if __name__ == '__main__':
    main()

