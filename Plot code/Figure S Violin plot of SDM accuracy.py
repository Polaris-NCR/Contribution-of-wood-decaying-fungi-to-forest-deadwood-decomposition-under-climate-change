import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker


def create_validation_plot(csv_file, out_path=None):

    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File not found '{csv_file}'.")
        print("Please ensure Fungi-accuracy.csv is in the same folder as this script.")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    required_cols = [GROUP_COLUMN, AUC_ROC_COLUMN, AUC_PR_COLUMN]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV file must contain the following columns: {required_cols}")
        print(f"Current columns: {df.columns.tolist()}")
        return

    unique_groups = df[GROUP_COLUMN].unique()
    if not all(group in X_AXIS_LABELS for group in unique_groups):
        print(f"Warning: The 'Fungi type' column in CSV contains unknown values: {unique_groups}")


    ordered_labels = ["Brown", "White"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    sns.boxplot(ax=ax1,
                data=df,
                x=GROUP_COLUMN,
                y=AUC_ROC_COLUMN,
                palette=PALETTE,
                order=ordered_labels,
                showfliers=False) 

    sns.swarmplot(ax=ax1,
                  data=df,
                  x=GROUP_COLUMN,
                  y=AUC_ROC_COLUMN,
                  color="0.25",
                  order=ordered_labels,
                  size=5,
                  alpha=0.7)

    ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
    ax1.set_ylabel('AUC ROC', fontsize=14)
    ax1.set_xlabel(None)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.tick_params(axis='y', labelsize=14)
    ax1.set_ylim(0.8, 1)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    ax1.set_xticklabels([X_AXIS_LABELS['Brown'], X_AXIS_LABELS['White']])

    sns.boxplot(ax=ax2,
                data=df,
                x=GROUP_COLUMN,
                y=AUC_PR_COLUMN,
                palette=PALETTE,
                order=ordered_labels,
                showfliers=False) 

    sns.swarmplot(ax=ax2,
                  data=df,
                  x=GROUP_COLUMN,
                  y=AUC_PR_COLUMN,
                  color="0.25",
                  order=ordered_labels, 
                  size=5,
                  alpha=0.7)

    ax2.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
    ax2.set_ylabel('AUC PR', fontsize=14)
    ax2.tick_params(axis='x', labelsize=14)
    ax2.tick_params(axis='y', labelsize=14)
    ax2.set_xlabel(None) 
    ax2.set_ylim(0.8, 1)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    ax2.set_xticklabels([X_AXIS_LABELS['Brown'], X_AXIS_LABELS['White']])

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if out_path is not None:
        plt.savefig(out_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    csv_path = r"/Fungi-accuracy.csv"
    out_path = "../Figure/Figure S Model Validation.png"

    GROUP_COLUMN = "Fungi type"
    AUC_ROC_COLUMN = "AUC-ROC"
    AUC_PR_COLUMN = "AUC-PR"

    X_AXIS_LABELS = {
        "Brown": "Brown rot",
        "White": "White rot"
    }

    PALETTE = {
        "Brown": "#a6cee3",
        "White": "#1f78b4" 
    }

    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.unicode_minus'] = False

    create_validation_plot(csv_path, out_path)