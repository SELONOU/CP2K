import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# Get all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)

        # Updated columns based on your CSV
        frame_col = 'frame number'  # Frame number
        qm_col = 'E (rel.en.kcal/mol of QM)'  # QM relative energy
        ml_col = 'Relative_energy'  # ML relative energy

        # Skip if required columns are not present
        if not all(col in df.columns for col in [frame_col, qm_col, ml_col]):
            print(f"Skipping {csv_file}: required columns not found.")
            continue

        # Extract only the last digits after 'frame_' and pad to 4 digits
        df['Frame_Display'] = df[frame_col].apply(
            lambda x: re.search(r'frame_([0-9]+)', str(x)).group(1).zfill(4)
            if re.search(r'frame_([0-9]+)', str(x)) else str(x)
        )

        # Plot with clear background
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
        ax.plot(df['Frame_Display'], df[qm_col], label='QM Relative Energy (kcal/mol)', color='blue')
        ax.plot(df['Frame_Display'], df[ml_col], label='ML Relative Energy (kcal/mol)', color='red')

        # Set axis labels and title with bold font
        ax.set_xlabel('Frame Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Relative Energy (kcal/mol)', fontsize=12, fontweight='bold')
        ax.set_title('Relative Energies: QM vs ML', fontsize=14, fontweight='bold')
        ax.legend(frameon=False)

        # Improve x-axis: show fewer ticks, rotate labels for clarity
        ax.set_xticks(df['Frame_Display'][::max(1, len(df)//15)])
        ax.tick_params(axis='x', rotation=45, labelsize=8)

        # Ensure X and Y axis lines are clearly visible
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_color('black')
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)

        # Hide top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Save the plot in the same directory as the CSV
        output_file = os.path.splitext(csv_file)[0] + '_plot.png'
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"Plot saved as: {output_file}")

    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

