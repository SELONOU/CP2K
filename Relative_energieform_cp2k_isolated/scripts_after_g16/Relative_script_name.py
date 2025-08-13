import glob
import csv
import os

def extract_final_energy(logfile):
    """
    Extracts the last 'SCF Done' energy value from a Gaussian log file.
    """
    energy = None
    with open(logfile, 'r') as file:
        for line in file:
            if 'SCF Done' in line:
                # Example line: SCF Done:  E(RB3LYP) = -228.456789 A.U. after xx cycles
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == '=':
                        energy = float(parts[i+1])
                        break
    return energy

def main():
    # Get all Gaussian log files in the current directory
    log_files = glob.glob("*.log")
    
    if not log_files:
        print("No log files found in the current directory.")
        return

    # Extract energies
    energies = []
    for logfile in log_files:
        energy = extract_final_energy(logfile)
        if energy is not None:
            energies.append((os.path.splitext(logfile)[0], energy))
        else:
            print(f"Warning: No energy found in {logfile}")

    if not energies:
        print("No valid energies found in log files.")
        return

    # Use the energy of the first frame as reference
    reference_name, reference_energy = energies[0]

    # Prepare CSV file
    with open('relative_energies_log_mobley_9055303.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame_names', 'Final_energy_frame_0', 'State_Final_Energy', 'Relative_energy'])

        for name, energy in energies:
            relative_energy = energy - reference_energy
            writer.writerow([name, reference_energy if name == reference_name else '', energy, relative_energy])

    print("CSV file 'relative_energies_log_mobley_9055303.csv' created successfully.")

if __name__ == '__main__':
    main()

