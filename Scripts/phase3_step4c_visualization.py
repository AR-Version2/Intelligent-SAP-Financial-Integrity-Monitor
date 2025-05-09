# -*- coding: utf-8 -*-
"""phase3_step4c_visualization.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1E75-6D7--8C9NApMsHQpV5XhyJjZIupr
"""

# prompt: mount google drive

from google.colab import drive
drive.mount('/content/drive')

# --- IMPORTS ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE # t-SNE is computationally expensive
import joblib # Required if you needed to load scaler, but not strictly for viz itself
import traceback
import os
import datetime

# --- Colab Specific - Mount Google Drive ---
# Make sure you have run this in a previous cell in Colab:
# from google.colab import drive
# drive.mount('/content/drive')

# --- Configuration ---
# Base directory on Google Drive
drive_base_path = "/content/drive/MyDrive/SAP Financial Doc Anomaly Detection"

# Input Directory (Where previous outputs are located)
input_directory = drive_base_path

# Directory to save the output plots
PLOT_TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # Timestamp for plot filenames and folder
plot_output_dir = os.path.join(drive_base_path, f"Phase3_Viz_Output_{PLOT_TIMESTAMP}")

# --- Input Filenames (Using confirmed names and timestamps) ---
engineered_features_filename = "sap_engineered_features__20250428_205234.csv"
scaled_features_filename = "phase3_step3_scaled_features_20250428_230602.npy"
identifiers_filename = "phase3_step3_identifiers_20250428_230602.csv"
num_features_filename = "phase3_step3_num_features_20250428_230602.txt"
results_filename = "phase3_step4a_baseline_results_20250428_230602.csv"

# Construct full paths
input_engineered_path = os.path.join(input_directory, engineered_features_filename)
scaled_features_path = os.path.join(input_directory, scaled_features_filename)
identifiers_path = os.path.join(input_directory, identifiers_filename)
num_features_path = os.path.join(input_directory, num_features_filename)
results_path = os.path.join(input_directory, results_filename)

# --- Visualization Parameters ---
TSNE_SAMPLE_SIZE = 50000 # Keep sampling for t-SNE unless you have ample time/GPU
TSNE_PERPLEXITY = 30
PCA_N_COMPONENTS = 2
TSNE_N_COMPONENTS = 2

SAVE_PLOTS = True
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7) # Default figure size

# --- Helper Functions ---
def print_separator(title=""): print("\n" + "="*30 + f" {title} " + "="*30)

def save_plot(plt_obj, filename_base, output_dir):
    """Saves the current matplotlib plot with timestamp."""
    if SAVE_PLOTS:
        try:
            # Use consistent timestamp for all plots in this run
            filename = f"{filename_base}_{PLOT_TIMESTAMP}.png"
            path = os.path.join(output_dir, filename)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir); print(f"   * Created plot directory: {output_dir}")
            plt_obj.savefig(path, bbox_inches='tight', dpi=150); print(f"   * Plot saved: {filename}")
        except Exception as e: print(f"   * WARNING: Could not save plot {filename_base}. Error: {e}")
    plt_obj.close()

# --- 1. Load Required Data ---
print_separator("[Phase 3 Step 4c] Loading Data for Visualization")
scaled_features_array = None; df_identifiers = None; df_results = None; numerical_feature_names = None; df_engineered_viz = None

try:
    print(f"Loading scaled features from: {scaled_features_path}")
    scaled_features_array = np.load(scaled_features_path)
    print(f"  Loaded scaled features: {scaled_features_array.shape}")

    print(f"Loading identifiers from: {identifiers_path}")
    df_identifiers = pd.read_csv(identifiers_path)
    print(f"  Loaded identifiers: {df_identifiers.shape}")

    print(f"Loading baseline results from: {results_path}")
    df_results = pd.read_csv(results_path)
    print(f"  Loaded results: {df_results.shape}")

    print(f"Loading numerical feature names from: {num_features_path}")
    with open(num_features_path, 'r') as f:
        numerical_feature_names = [line.strip() for line in f.readlines()]
    print(f"  Loaded {len(numerical_feature_names)} numerical feature names.")

    print(f"Loading original engineered features from: {input_engineered_path}")
    df_engineered_viz = pd.read_csv(input_engineered_path, low_memory=False)
    print(f"  Loaded original engineered features: {df_engineered_viz.shape}")

except FileNotFoundError as fnf_error: print(f"CRITICAL ERROR: Input file not found: {fnf_error}. Check paths and timestamps in config."); exit()
except Exception as e: print(f"CRITICAL ERROR loading data: {e}"); traceback.print_exc(); exit()

# --- 2. Prepare Data for Plotting ---
print_separator("[Phase 3 Step 4c] Preparing Data for Plotting")

# Basic validation
if not (scaled_features_array.shape[0] == len(df_identifiers) == len(df_results) == len(df_engineered_viz)):
    print("CRITICAL ERROR: Row counts mismatch between loaded files. Check timestamps and file integrity.")
    print(f"Shapes: Scaled={scaled_features_array.shape}, Identifiers={df_identifiers.shape}, Results={df_results.shape}, Engineered={df_engineered_viz.shape}")
    exit()
if not (scaled_features_array.shape[1] == len(numerical_feature_names)):
     print("CRITICAL ERROR: Scaled features columns count mismatch with feature names file.")
     exit()

# --- Create DataFrames needed for different plots ---

# 2a. Data for Dimensionality Reduction Plots (Scaled Features + Labels)
# Merge results onto identifiers using 'original_index'
df_plot_data_scaled = pd.merge(df_identifiers, df_results, on='original_index', how='left', suffixes=('', '_res'))
# Check if merge worked by verifying label columns exist and have expected count
labels_loaded_ok = True
if 'IF_Label' not in df_plot_data_scaled.columns or df_plot_data_scaled['IF_Label'].isnull().any():
    print("Warning: IF_Label column missing or contains NaNs after merge.")
    labels_loaded_ok = False
if 'LOF_Label' not in df_plot_data_scaled.columns or df_plot_data_scaled['LOF_Label'].isnull().any():
    print("Warning: LOF_Label column missing or contains NaNs after merge.")
    labels_loaded_ok = False
if not labels_loaded_ok:
    print("Warning: Proceeding with visualization, but label coloring might be affected.")


# 2b. Data for Interpretable Distribution Plots (Original Features + Labels)
# Merge results with original features using 'original_index'
df_engineered_viz = df_engineered_viz.reset_index().rename(columns={'index':'original_index'}) # Ensure original index exists
df_plot_data_unscaled = pd.merge(df_engineered_viz, df_results[['original_index', 'IF_Label', 'LOF_Label']], on='original_index', how='left')
print(f"Created df_plot_data_unscaled shape: {df_plot_data_unscaled.shape}")


# 2c. Select data subset for t-SNE if TSNE_SAMPLE_SIZE is set
data_for_tsne = scaled_features_array
labels_for_tsne = df_plot_data_scaled # Use the df with labels corresponding to scaled data

if TSNE_SAMPLE_SIZE is not None and TSNE_SAMPLE_SIZE < len(scaled_features_array):
    print(f"Sampling {TSNE_SAMPLE_SIZE} data points for t-SNE...")
    # Ensure indices are unique and within bounds
    if TSNE_SAMPLE_SIZE > len(scaled_features_array):
        print(f"Warning: Sample size {TSNE_SAMPLE_SIZE} > data size {len(scaled_features_array)}. Using full dataset for t-SNE.")
        indices = np.arange(len(scaled_features_array)) # Use all indices
    else:
        indices = np.random.choice(len(scaled_features_array), TSNE_SAMPLE_SIZE, replace=False)

    data_for_tsne = scaled_features_array[indices]
    # Select corresponding labels using the same indices from the merged scaled df
    labels_for_tsne = df_plot_data_scaled.iloc[indices].copy()
    print(f"  Sampled data shape for t-SNE: {data_for_tsne.shape}")
    print(f"  Sampled labels shape for t-SNE: {labels_for_tsne.shape}")
else:
    print("Using full dataset for t-SNE.")


# --- 3. Dimensionality Reduction ---
print_separator("[Phase 3 Step 4c] Performing Dimensionality Reduction")

# 3a. PCA
print("Running PCA...")
pca = PCA(n_components=PCA_N_COMPONENTS, random_state=42)
pca_available = False
try:
    pca_result = pca.fit_transform(scaled_features_array)
    df_plot_data_scaled['PCA1'] = pca_result[:, 0]
    df_plot_data_scaled['PCA2'] = pca_result[:, 1]
    print(f"  PCA finished. Explained variance ratio: {pca.explained_variance_ratio_.sum():.3f}")
    pca_available = True
except Exception as e: print(f"ERROR running PCA: {e}"); traceback.print_exc()

# 3b. t-SNE (Potentially on sample)
print("\nRunning t-SNE...")
tsne_available = False
if data_for_tsne is not None:
    # Use n_jobs=-1 for potentially faster computation on multi-core CPUs (might not use GPU in sklearn)
    tsne = TSNE(n_components=TSNE_N_COMPONENTS, perplexity=TSNE_PERPLEXITY, random_state=42, n_jobs=-1, verbose=1)
    try:
        print(f"  Fitting t-SNE on {data_for_tsne.shape[0]} samples (this may take time)...")
        tsne_result_sample = tsne.fit_transform(data_for_tsne)
        # Add t-SNE results ONLY to the sampled labels dataframe
        labels_for_tsne['TSNE1'] = tsne_result_sample[:, 0]
        labels_for_tsne['TSNE2'] = tsne_result_sample[:, 1]
        print("  t-SNE finished.")
        tsne_available = True
    except Exception as e: print(f"ERROR running t-SNE: {e}"); traceback.print_exc()
else: print("Skipping t-SNE as no data was prepared for it.")


# --- 4. Generate Visualizations ---
print_separator("[Phase 3 Step 4c] Generating Visualizations")

# Ensure plot output directory exists
if SAVE_PLOTS and not os.path.exists(plot_output_dir):
    os.makedirs(plot_output_dir)
    print(f"Created plot directory: {plot_output_dir}")


# 4a. PCA Plots (Using df_plot_data_scaled)
if pca_available:
    print("Generating PCA plots...")
    if 'IF_Label' in df_plot_data_scaled.columns:
        plt.figure(figsize=(11, 8));
        sns.scatterplot(x='PCA1', y='PCA2', hue='IF_Label', data=df_plot_data_scaled, palette={1: '#4477AA', -1: '#EE6677'}, s=5, alpha=0.5, legend='full')
        plt.title('PCA Visualization (Colored by Isolation Forest Label: -1=Anomaly)'); save_plot(plt, "pca_if_labels", plot_output_dir)
    else: print("  Skipping PCA plot for IF (labels not found).")

    if 'LOF_Label' in df_plot_data_scaled.columns:
        plt.figure(figsize=(11, 8));
        sns.scatterplot(x='PCA1', y='PCA2', hue='LOF_Label', data=df_plot_data_scaled, palette={1: '#228833', -1: '#CCBB44'}, s=5, alpha=0.5, legend='full')
        plt.title('PCA Visualization (Colored by LOF Label: -1=Anomaly)'); save_plot(plt, "pca_lof_labels", plot_output_dir)
    else: print("  Skipping PCA plot for LOF (labels not found).")
else: print("Skipping PCA plots as PCA failed or was skipped.")


# 4b. t-SNE Plots (Using labels_for_tsne)
if tsne_available:
    print("\nGenerating t-SNE plots (using sampled data if configured)...")
    if 'IF_Label' in labels_for_tsne.columns:
        plt.figure(figsize=(11, 8));
        sns.scatterplot(x='TSNE1', y='TSNE2', hue='IF_Label', data=labels_for_tsne, palette={1: '#4477AA', -1: '#EE6677'}, s=10, alpha=0.7, legend='full')
        plt.title(f't-SNE Visualization (Sample={data_for_tsne.shape[0]}, Colored by IF Label: -1=Anomaly)'); save_plot(plt, "tsne_if_labels", plot_output_dir)
    else: print("  Skipping t-SNE plot for IF (labels not found in sample).")

    if 'LOF_Label' in labels_for_tsne.columns:
        plt.figure(figsize=(11, 8));
        sns.scatterplot(x='TSNE1', y='TSNE2', hue='LOF_Label', data=labels_for_tsne, palette={1: '#228833', -1: '#CCBB44'}, s=10, alpha=0.7, legend='full')
        plt.title(f't-SNE Visualization (Sample={data_for_tsne.shape[0]}, Colored by LOF Label: -1=Anomaly)'); save_plot(plt, "tsne_lof_labels", plot_output_dir)
    else: print("  Skipping t-SNE plot for LOF (labels not found in sample).")
else: print("Skipping t-SNE plots as t-SNE failed or was skipped.")


# 4c. Feature Distribution Comparison Plots (Using df_plot_data_unscaled)
print("\nGenerating Feature Distribution Comparison Plots...")
if df_plot_data_unscaled is not None:
    features_to_plot = [
        'FE_LogAmount', 'FE_AmountDeviationFromUserMean', 'FE_AmountDeviationFromAccountMean',
        'FE_UserPostingFrequency', 'FE_AccountPostingFrequency', #'FE_PostingHour' # FE_PostingHour might not exist if CPUDT/CPUTM failed
        ]
    # Check if FE_PostingHour exists before adding
    if 'FE_PostingHour' in df_plot_data_unscaled.columns:
         features_to_plot.append('FE_PostingHour')

    features_to_plot = [f for f in features_to_plot if f in df_plot_data_unscaled.columns] # Filter existing

    for feature in features_to_plot:
        if df_plot_data_unscaled[feature].isnull().all():
            print(f"  Skipping distribution plot for '{feature}' - all values are NaN.")
            continue

        # Plot for IF
        if 'IF_Label' in df_plot_data_unscaled.columns:
            plt.figure(figsize=(12, 6));
            try: # Add try-except around plotting in case of issues with specific feature distribution
                 sns.histplot(data=df_plot_data_unscaled[df_plot_data_unscaled['IF_Label']==1], x=feature, color="#4477AA", label='Normal (IF)', kde=True, element="step", stat="density", common_norm=False)
                 sns.histplot(data=df_plot_data_unscaled[df_plot_data_unscaled['IF_Label']==-1], x=feature, color="#EE6677", label='Anomaly (IF)', kde=True, element="step", stat="density", common_norm=False)
                 plt.title(f'Distribution of {feature} (IF: Anomaly vs Normal)'); plt.legend()
                 if 'Frequency' in feature or 'Amount' in feature: plt.xscale('symlog')
                 save_plot(plt, f"hist_compare_if_{feature}", plot_output_dir)
            except Exception as e: print(f"  WARNING: Failed to plot IF distribution for {feature}. Error: {e}"); plt.close()


        # Plot for LOF
        if 'LOF_Label' in df_plot_data_unscaled.columns:
            plt.figure(figsize=(12, 6));
            try: # Add try-except
                 sns.histplot(data=df_plot_data_unscaled[df_plot_data_unscaled['LOF_Label']==1], x=feature, color="#228833", label='Normal (LOF)', kde=True, element="step", stat="density", common_norm=False)
                 sns.histplot(data=df_plot_data_unscaled[df_plot_data_unscaled['LOF_Label']==-1], x=feature, color="#CCBB44", label='Anomaly (LOF)', kde=True, element="step", stat="density", common_norm=False)
                 plt.title(f'Distribution of {feature} (LOF: Anomaly vs Normal)'); plt.legend()
                 if 'Frequency' in feature or 'Amount' in feature: plt.xscale('symlog')
                 save_plot(plt, f"hist_compare_lof_{feature}", plot_output_dir)
            except Exception as e: print(f"  WARNING: Failed to plot LOF distribution for {feature}. Error: {e}"); plt.close()

else:
    print("Skipping distribution comparison plots (merged unscaled data not available).")


print(f"\n--- Script phase3_step4c_visualization.py ({PLOT_TIMESTAMP}) Complete ---")
if SAVE_PLOTS: print(f"Plots saved to: {plot_output_dir}")