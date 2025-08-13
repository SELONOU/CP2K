import os
import pandas as pd
import numpy as np
from glob import glob

# Get all target merged CSV files
csv_files = glob("relative_energies_CP2K_QM_mobley_*.csv")

results = []

for file in csv_files:
    try:
        df = pd.read_csv(file)

        # Check if required columns exist
        if "Relative_energy (kcal/mol)_x" not in df.columns or "Relative_energy (kcal/mol)_y" not in df.columns:
            print(f"Skipping {file}: Missing required columns.")
            continue

        ml = df["relative_energies_ML_on_cp2k"].values
        qm = df["Relative_energy (kcal/mol)"].values

        if len(ml) != len(qm):
            print(f"Skipping {file}: Column length mismatch.")
            continue

        # Compute RMSE and MAE
        rmse = np.sqrt(np.mean((ml - qm) ** 2))
        mae = np.mean(np.abs(ml - qm))

        # Round to 2 decimal places
        rmse = round(rmse, 2)
        mae = round(mae, 2)

        results.append({
            "filename": os.path.basename(file),
            "RMSE (kcal/mol)": rmse,
            "MAE (kcal/mol)": mae
        })

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Create DataFrame and save
results_df = pd.DataFrame(results)
results_df.to_csv("rmse_mae_summary_2_digits_CP2K_QM.csv", index=False)

print("✅ Results saved to 'rmse_mae_summary_2_digits_CP2K_QM.csv'")

