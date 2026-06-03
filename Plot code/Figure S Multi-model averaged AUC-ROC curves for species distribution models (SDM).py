import pandas as pd
import numpy as np
import glob
from sklearn import metrics
import matplotlib.pyplot as plt
import os
import seaborn as sns
import joblib
from matplotlib.ticker import FormatStrFormatter
import matplotlib


def evaluate_model_runs(fungi_name, data_list_PR, data_list_ROC, data_list_accuracy, csv_pattern, y_true_col,
                        y_prob_col, PR_path=None, ROC_path=None):
    csv_files = glob.glob(csv_pattern)
    if not csv_files:
        return

    all_metrics = {
        'run': [],
        'avg_precision': [],
        'auc_roc': [],
        'accuracy_at_0.5': [],
        'TP': [],
        'FN': [],
        'FP': [],
        'TN': []
    }

    fig_pr, ax_pr = plt.subplots(figsize=(12, 10))
    fig_roc, ax_roc = plt.subplots(figsize=(12, 10))
    fig_acc, ax_acc = plt.subplots(figsize=(12, 10))
    matplotlib.rcParams['font.family'] = 'Arial'

    all_y_true = []

    for i, csv_file in enumerate(csv_files):
        print(f"\n--- handling: {os.path.basename(csv_file)} ---")

        try:
            df = pd.read_csv(csv_file)

            if y_true_col not in df.columns or y_prob_col not in df.columns:
                continue

            df = df.dropna(subset=[y_true_col, y_prob_col])

            if df.empty:
                continue

            y_true = df[y_true_col]
            y_prob = df[y_prob_col]

            all_y_true.append(y_true)

            if len(np.unique(y_true)) < 2:
                continue

            avg_precision = metrics.average_precision_score(y_true, y_prob)

            auc_roc = metrics.roc_auc_score(y_true, y_prob)

            y_pred_binary = (y_prob >= 0.5).astype(int)
            accuracy = metrics.accuracy_score(y_true, y_pred_binary)

            tn, fp, fn, tp = metrics.confusion_matrix(y_true, y_pred_binary).ravel()

            all_metrics['run'].append(f'Run {i + 1}')
            all_metrics['avg_precision'].append(avg_precision)
            all_metrics['auc_roc'].append(auc_roc)
            all_metrics['accuracy_at_0.5'].append(accuracy)
            all_metrics['TP'].append(tp)
            all_metrics['FN'].append(fn)
            all_metrics['FP'].append(fp)
            all_metrics['TN'].append(tn)

            if avg_precision > 0.8 and auc_roc > 0.7 and accuracy > 0.6:
                data_list_PR.append({'Group': fungi_name, 'Value': avg_precision})
                data_list_ROC.append({'Group': fungi_name, 'Value': auc_roc})
                data_list_accuracy.append({'Group': fungi_name, 'Value': accuracy})

                precision, recall, _ = metrics.precision_recall_curve(y_true, y_prob)
                ax_pr.plot(recall, precision,
                           label=f'Run {i + 1} (AP = {avg_precision:.3f})',
                           alpha=0.8, lw=2)

                fpr, tpr, _ = metrics.roc_curve(y_true, y_prob)
                ax_roc.plot(fpr, tpr,
                            label=f'Run {i + 1} (AUC = {auc_roc:.3f})',
                            alpha=0.8, lw=2)

        except Exception as e:
            print(f"  handling {csv_file} meet error: {e}")

    total_y_true = pd.concat(all_y_true)
    no_skill = (total_y_true == 1).sum() / len(total_y_true)
    ax_pr.axhline(no_skill, linestyle='--', color='gray', label=f'No Skill (Baseline = {no_skill:.3f})')
    ax_pr.tick_params(axis='both', labelsize=18)
    # ax_pr.set_xlabel('Recall (Sensitivity)', fontsize=14)
    # ax_pr.set_ylabel('Precision', fontsize=14)
    # ax_pr.set_title('Precision-Recall (AUC-PR) Curves for 10 Model Runs', fontsize=16)
    # ax_pr.set_title('Precision-Recall Curves', fontsize=16)
    # ax_pr.legend(loc='best', fontsize=10)
    ax_pr.grid(alpha=0.5)
    ax_pr.set_xlim([0.0, 1.0])
    ax_pr.set_ylim([0.0, 1.05])

    if PR_path is not None:
        fig_pr.savefig(PR_path, dpi=300)
        plt.close(fig_pr)
    # fig_pr.show()

    ax_roc.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Guess (AUC = 0.5)')

    # ax_roc.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=14)
    # ax_roc.set_ylabel('True Positive Rate (Sensitivity)', fontsize=14)
    # ax_roc.set_title('Receiver Operating Characteristic (AUC-ROC) Curves for 10 Model Runs', fontsize=16)
    # ax_roc.set_xlabel('False Positive Rate', fontsize=14)
    # ax_roc.set_ylabel('True Positive Rate', fontsize=14)
    # ax_roc.set_title('Receiver Operating Characteristic Curves', fontsize=16)
    # ax_roc.legend(loc='lower right', fontsize=10)
    ax_roc.tick_params(axis='both', labelsize=18)
    ax_roc.grid(alpha=0.5)
    ax_roc.set_xlim([0.0, 1.0])
    ax_roc.set_ylim([0.0, 1.05])

    if ROC_path is not None:
        fig_roc.savefig(ROC_path, dpi=300)
        plt.close(fig_roc)
    # fig_roc.show()

    df_results = pd.DataFrame(all_metrics)
    print(df_results.to_string(index=False))
    summary = df_results.drop(columns='run').agg(['mean', 'std']).T
    summary.columns = ['Mean', 'StdDev (SD)']
    print(summary.to_string(float_format="%.4f"))
    print("=======================================================")

    return data_list_PR, data_list_ROC, data_list_accuracy


def draw_boxplot(data_list, y_label='Average Precision', savepath=None):
    df = pd.DataFrame(data_list)

    # 设置绘图样式
    sns.set_theme(style="white", rc={
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "axes.linewidth": 1.5,
        "grid.linestyle": "--"
    })

    plt.figure(figsize=(20, 6))

    ax = sns.boxplot(
        x='Group', y='Value', data=df, width=0.5, linewidth=2, showfliers=False,
        boxprops=dict(alpha=0.6)
    )

    sns.stripplot(
        x='Group', y='Value', data=df, size=1, jitter=0.2, linewidth=1, edgecolor='gray', alpha=0.9
    )

    plt.grid(axis='y', linestyle='--', alpha=0.7, linewidth=1.5, color='gray')
    # plt.grid(axis='x', linestyle='--', alpha=0.7, linewidth=1.5, color='gray')

    # plt.title('Comparison of Five Experimental Groups',fontsize=18, fontweight='bold', pad=15)
    plt.ylabel(y_label, fontsize=16, fontweight='bold')
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    plt.xlabel('', fontsize=16, fontweight='bold')
    plt.xticks(rotation=20)
    # plt.xticks([])
    plt.tick_params(axis='both', which='major',
                    labelsize=14, width=1.5, length=6)

    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    plt.tight_layout()
    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    # plt.show()


if __name__ == "__main__":
    white_species = ['Fomesfomentarius', 'Fomitiporiahartigii', 'Fuscoporiagilva', 'Hyphodermasetigerum',
                     'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                     'Pleurotusostreatus', 'Porodisculuspendulus', 'Trametessanguinea', 'Trametesversicolor',
                     'Tyromyceschioneus', 'Xylobolussubpileatus']
    brown_species = ['Amyloporiaxantha', 'Fomitopsispinicola', 'Gloeophyllumtrabeum', 'Laetiporusconifericola',
                     'Rhodoniaplacenta']

    y_true = 'PresAbs'

    y_pred = 'probability'
    data_list_PR = []
    data_list_ROC = []
    data_list_acc = []

    for i in range(len(brown_species)):
        csv_path = 'F:\\Fungi data\\' + brown_species[i] + '-testdata' + '\\' + brown_species[i] + '-testPixelVals*.csv'
        PR_path = '..\\Figure\\AUC-PR&ROC\\' + brown_species[i] + '_AUC_PR_Curves-new.png'
        ROC_path = '..\\Figure\\AUC-PR&ROC\\' + brown_species[i] + '_AUC_ROC_Curves-new.png'
        evaluate_model_runs(brown_species[i], data_list_PR, data_list_ROC, data_list_acc, csv_path, y_true, y_pred,
                            PR_path, ROC_path)

    for i in range(len(white_species)):
        csv_path = 'F:\\Fungi data\\' + white_species[i] + '-testdata' + '\\' + white_species[i] + '-testPixelVals*.csv'
        PR_path = '..\\Figure\\AUC-PR&ROC\\' + white_species[i] + '_AUC_PR_Curves-new.png'
        ROC_path = '..\\Figure\\AUC-PR&ROC\\' + white_species[i] + '_AUC_ROC_Curves-new.png'
        evaluate_model_runs(white_species[i], data_list_PR, data_list_ROC, data_list_acc, csv_path, y_true, y_pred,
                            PR_path, ROC_path)
    #
    joblib.dump(data_list_PR, '..\\code\\PR_data_list.txt')
    joblib.dump(data_list_ROC, '..\\code\\ROC_data_list.txt')
    joblib.dump(data_list_acc, '..\\code\\acc_data_list.txt')

    # data_list_PR = joblib.load('..\\code\\PR_data_list.txt')
    # data_list_ROC = joblib.load('..\\code\\ROC_data_list.txt')
    # PR_box_path = '..\\Figure\\PR_boxplot_20260119.png'
    # ROC_box_path = '..\\Figure\\ROC_boxplot_20260119.png'
    acc_box_path = '..\\Figure\\acc_boxplot_20260119.png'
    # draw_boxplot(data_list_PR, 'Average Precision', PR_box_path)
    # draw_boxplot(data_list_ROC, 'Area Under the ROC Curve', ROC_box_path)
    draw_boxplot(data_list_acc, 'Accuracy@0.5', acc_box_path)
