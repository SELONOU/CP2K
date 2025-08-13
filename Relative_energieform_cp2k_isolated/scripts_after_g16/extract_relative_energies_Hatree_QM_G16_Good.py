import os
import re
import csv

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
    frame0_energy = None

    for log_file in log_files:
        log_path = os.path.join(directory, log_file)
        energy = extract_final_energy(log_path)
        if energy is None:
            continue  # skip if energy couldn't be extracted

        frame_number = get_frame_number(log_file)
        frame_name = re.sub(r'\.log$', '', log_file)
        frame_name = re.sub(r'_frame_(\d+)', lambda m: f"_frame_{int(m.group(1)):04d}", frame_name)

        if frame_number == 0:
            frame0_energy = energy

        energies.append((frame_name, energy))

    if frame0_energy is None:
        print("Frame 0 energy not found. Check if mobley_..._frame_0.log exists and is correctly formatted.")
        return

    # Write to CSV
    with open('relative_energies.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame_names', 'Final_energy_frame_0', 'State_Final_Energy', 'Relative_energy'])
        for frame_name, energy in energies:
            rel_energy = energy - frame0_energy
            writer.writerow([frame_name, frame0_energy, energy, rel_energy])

    print("✅ Done: Output written to relative_energies.csv")

if __name__ == '__main__':
    main()

