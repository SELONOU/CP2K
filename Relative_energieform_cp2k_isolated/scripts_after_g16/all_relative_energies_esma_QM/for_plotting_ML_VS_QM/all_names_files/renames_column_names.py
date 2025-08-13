import pandas as pd
import os

# Directory containing your CSV files
directory = '.'  # or replace with the full path like 'data/csv_files/'

# Mapping of old column names to new names
rename_dict = {
    'frame_names': 'frame number',
    'State_Final_Energy': 'abs.energy of ML',
    'Relative_energy (rel.en.kcal/mol of ML)': 'E (rel.en.kcal/mol of ML)',
    'State_Final_Energy (kcal/mol)': 'abs.energy of QM',
    'Relative_energy (kcal/mol)': 'E (rel.en.kcal/mol of QM)',
}

# Process all CSV files
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath)

        # Rename columns if they exist in the file
        df.rename(columns=rename_dict, inplace=True)

        # Apply absolute values to the specified columns if they exist
        for col in ['abs.energy of ML', 'abs.energy of QM']:
            if col in df.columns:
                df[col] = df[col].abs()

        # Save changes back to the original file
        df.to_csv(filepath, index=False)

print("All CSV files processed successfully.")

