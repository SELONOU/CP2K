import os
import pandas as pd
import numpy as np
from glob import glob

# Collect all merged CP2K–QM files
csv_files = glob("relative_energies_CP2K_QM_mobley_*.csv")

results = []

for file in csv_files:
    try:
        df = pd.read_csv(file)

        # Check columns
        if "Relative_energy (kcal/mol)_x" not in df.columns or "Relative_energy (kcal/mol)_y" not in df.columns:
            print(f"Skipping {file}: Missing required columns.")
            continue

        ml_values = df["Relative_energy (kcal/mol)_x"].values
        qm_values = df["Relative_energy (kcal/mol)_y"].values

        if len(ml_values) != len(qm_values):
            print(f"Skipping {file}: Column length mismatch.")
            continue

        # Compute RMSE and MAE with 2-decimal precision
        rmse = round(np.sqrt(np.mean((ml_values - qm_values) ** 2)), 2)
        mae = round(np.mean(np.abs(ml_values - qm_values)), 2)

        results.append({
            "filename": os.path.basename(file),
            "RMSE (kcal/mol)": rmse,
            "MAE (kcal/mol)": mae
        })

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("rmse_mae_summary_CP2K_QM.csv", index=False)

print("✅ RMSE and MAE results saved to 'rmse_mae_summary_CP2K_QM.csv'")

