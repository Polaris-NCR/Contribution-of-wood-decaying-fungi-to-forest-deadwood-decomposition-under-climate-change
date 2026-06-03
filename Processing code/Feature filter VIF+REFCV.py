import glob
import ee
import geemap
import pandas as pd, geopandas as gpd
import numpy as np, matplotlib.pyplot as plt
import os, requests, math, random
from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold
from statsmodels.stats.outliers_influence import variance_inflation_factor
import gc
import sklearn.ensemble
import matplotlib.pyplot as plt


def select_features_vif(X, threshold=10.0):
    variables = list(X.columns)
    while True:
        if len(variables) < 2:
            break
        vif_data = pd.DataFrame()
        vif_data["feature"] = variables
        vif_data["VIF"] = [variance_inflation_factor(X[variables].values, i) for i in range(len(variables))]

        max_vif = vif_data['VIF'].max()
        if max_vif > threshold:
            feature_to_remove = vif_data.sort_values('VIF', ascending=False)['feature'].iloc[0]
            variables.remove(feature_to_remove)
        else:
            break
    print(f"VIF of BIO feature, remaining number of features: {len(variables)}")
    return variables

fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum','Hyphodermasetigerum', 'Laetiporusconifericola',
                 'Lyomycescrustosus', 'Meruliustremellosus','Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

for i in range(len(fungi_species)):
    fungi_name=fungi_species[i]
    target_dir = r"/traindata/" + fungi_name
    file_list = glob.glob(os.path.join(target_dir, f"{fungi_name}*.csv"))
    print(file_list)
    seeds = [35, 68, 43, 54, 17, 46, 76, 88, 24, 12]
    for i in range(len(file_list)):
        file = file_list[i]
        s = seeds[i]
        print('file', file)
        train_df1 = pd.read_csv(file)

        feature_names = ['Bulk', 'Clay', 'SOC', 'SWC', 'Sand', 'Treecover', 'bio01', 'bio02', 'bio03', 'bio04', 'bio05',
                        'bio06', 'bio07', 'bio08', 'bio09', 'bio10', 'bio11', 'bio12', 'bio13', 'bio14', 'bio15', 'bio16',
                        'bio17', 'bio18', 'bio19', 'elevation', 'pH']

        X_full = train_df1[feature_names]
        y = train_df1['PresAbs']

        bio_names = [f'bio{i:02d}' for i in range(1, 20)]
        bio_names_present = [name for name in bio_names if name in X_full.columns]
        X_bio = X_full[bio_names_present]
        selected_bio_features = select_features_vif(X_bio.copy(), threshold=20)
        print(f"BIO features retained after VIF filtering: {selected_bio_features}")

        other_feature_names = [name for name in X_full.columns if name not in bio_names_present]

        X_combined_for_rfecv = pd.concat([X_full[selected_bio_features], X_full[other_feature_names]], axis=1)
        print(f"Total features for RFECV: {X_combined_for_rfecv.shape[1]}")

        estimator = sklearn.ensemble.RandomForestClassifier(n_estimators=100, min_samples_leaf=20, oob_score=True,
                                                            n_jobs=-1, random_state=s)
        selector_rfecv = RFECV(estimator=estimator, step=1, cv=StratifiedKFold(10), scoring='roc_auc', n_jobs=-1,
                            min_features_to_select=1)
        selector_rfecv.fit(X_combined_for_rfecv, y)

        final_selected_features = list(X_combined_for_rfecv.columns[selector_rfecv.support_])
        print(f"RFECV filter finished.")
        print(f"Optimal number of features: {selector_rfecv.n_features_}")
        print(f"Final retained features: {final_selected_features}")

        plt.figure(figsize=(10, 6))
        plt.title('Recursive Feature Elimination with Cross-Validation (on pre-filtered data)', fontsize=14)
        plt.xlabel('Number of features selected', fontsize=12)
        plt.ylabel('Cross-validation score (AUC)', fontsize=12)

        if hasattr(selector_rfecv, 'grid_scores_'):
            scores = selector_rfecv.grid_scores_
        else:
            scores = selector_rfecv.cv_results_['mean_test_score']
        plt.plot(range(1, len(scores) + 1), scores)
        plt.axvline(x=selector_rfecv.n_features_, color='r', linestyle='--',
                    label=f'Optimal number of features ({selector_rfecv.n_features_})')
        plt.legend()
        plt.grid()
        plt.show()