import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False


def estimate_missing_sd_hierarchical(df):
    df_copy = df.copy()

    df_with_sd = df_copy.dropna(subset=['Wood mass loss std (%)', 'Wood mass loss (%)'])
    df_with_sd = df_with_sd[df_with_sd['Wood mass loss (%)'] > 0]
    global_avg_cv = (df_with_sd['Wood mass loss std(%)'] / df_with_sd['Wood mass loss (%)']).mean()
    print(f"Global avg_CV : {global_avg_cv:.4f}")

    for species in df_copy['Fungi species'].unique():
        species_mask = df_copy['Fungi species'] == species
        species_df = df_copy[species_mask]

        if not species_df['Wood mass loss std (%)'].isnull().any():
            continue

        species_df_known_sd = species_df.dropna(subset=['Wood mass loss std (%)', 'Wood mass loss (%)'])
        species_df_known_sd = species_df_known_sd[species_df_known_sd['Wood mass loss (%)'] > 0]

        if not species_df_known_sd.empty:
            cv_species = (species_df_known_sd['Wood mass loss std (%)'] / species_df_known_sd['Wood mass loss (%)']).mean()
            print(f"  -> Individual species '{species}' estimation, CV = {cv_species:.4f}")
            missing_mask = species_mask & df_copy['Wood mass loss std (%)'].isnull()
            df_copy.loc[missing_mask, 'Wood mass loss std (%)'] = df_copy.loc[missing_mask, 'Wood mass loss (%)'] * cv_species
            continue

        fungus_type = species_df['Fungi Type'].iloc[0]
        type_mask = df_copy['Fungi Type'] == fungus_type
        type_df_known_sd = df_copy[type_mask].dropna(subset=['Wood mass loss std (%)', 'Wood mass loss (%)'])
        type_df_known_sd = type_df_known_sd[type_df_known_sd['Wood mass loss (%)'] > 0]

        if not type_df_known_sd.empty:
            cv_type = (type_df_known_sd['Wood mass loss std (%)'] / type_df_known_sd['Wood mass loss (%)']).mean()
            print(f"  -> species '{species}', Function group '{fungus_type}' estimation, CV = {cv_type:.4f}")
            missing_mask = species_mask & df_copy['Wood mass loss std (%)'].isnull()
            df_copy.loc[missing_mask, 'Wood mass loss std (%)'] = df_copy.loc[missing_mask, 'Wood mass loss (%)'] * cv_type
            continue

        print(f"  -> All species '{species}' estimation, CV = {global_avg_cv:.4f}")
        missing_mask = species_mask & df_copy['Wood mass loss std (%)'].isnull()
        df_copy.loc[missing_mask, 'Wood mass loss std (%)'] = df_copy.loc[missing_mask, 'Wood mass loss (%)'] * global_avg_cv

    return df_copy['Wood mass loss std (%)']


def calculate_k(loss_percentage, days):
    t_years = days / 365
    remaining_fraction = 1 - loss_percentage / 100
    remaining_fraction[remaining_fraction <= 0] = 1e-9
    return -np.log(remaining_fraction) / t_years


def propagate_k_error(loss_percentage, loss_sd, days):
    t_years = days / 365
    L = loss_percentage / 100
    sigma_L = loss_sd / 100
    denominator = t_years * (1 - L)
    denominator[denominator <= 0] = 1e-9
    return sigma_L / denominator


def aggregate_k_with_error(df):
    final_results = []
    grouped = df.groupby(['Fungi species', 'Incubation temperature (°C)'])
    for (fungus_name, temp), group in grouped:
        k_values_to_agg = group['k (year^-1)']
        sigma_k_values_to_agg = group['sigma_k (year^-1)']
        if fungus_name == 'Fomes fomentarius' and temp == 22:
            wood_types = group['Degraded wood species'].unique()
            if len(wood_types) > 1:
                k_agg_list, sigma_k_agg_list = [], []
                for wood in wood_types:
                    wood_data = group[group['Degraded wood species'] == wood]
                    k_mean_wood = wood_data['k (year^-1)'].mean()
                    sigma_k_agg_wood = np.sqrt(np.sum(wood_data['sigma_k (year^-1)'] ** 2)) / len(wood_data)
                    k_agg_list.append(k_mean_wood)
                    sigma_k_agg_list.append(sigma_k_agg_wood)
                k_values_to_agg = pd.Series(k_agg_list)
                sigma_k_values_to_agg = pd.Series(sigma_k_agg_list)

        agg_k = k_values_to_agg.mean()
        agg_sigma_k = np.sqrt(np.sum(sigma_k_values_to_agg ** 2)) / len(k_values_to_agg)
        final_results.append({
            'Fungi species': fungus_name, 'Incubation temperature (°C)': temp,
            'aggregated_k': agg_k, 'aggregated_sigma_k': agg_sigma_k
        })
    return pd.DataFrame(final_results).sort_values(by=['Fungi species', 'Incubation temperature (°C)'])


def exponential_model(T, a, b):
    return a * np.exp(b * T)


def fit_and_plot_weighted_individual(df_agg):
    fungus_species = df_agg['Fungi species'].unique()
    for fungus_name in fungus_species:
        subset = df_agg[df_agg['Fungi species'] == fungus_name].copy()
        if len(subset) < 3: 
            print(f"Insufficient data points for fungus '{fungus_name}' ({len(subset)}), statistical evaluation skipped.")
            continue

        T_data, k_data = subset['Incubation temperature (°C)'], subset['aggregated_k']
        sigma_k_data = subset['aggregated_sigma_k']
        sigma_k_data[sigma_k_data <= 0] = 1e-9

        try:
            params, covariance = curve_fit(exponential_model, T_data, k_data, p0=[0.1, 0.1],
                                           sigma=sigma_k_data, absolute_sigma=True, maxfev=5000)
            a_fit, b_fit = params

            perr = np.sqrt(np.diag(covariance))
            a_se, b_se = perr
            dof = len(T_data) - len(params)

            t_a = a_fit / a_se
            p_a = stats.t.sf(np.abs(t_a), dof) * 2

            t_b = b_fit / b_se
            p_b = stats.t.sf(np.abs(t_b), dof) * 2

            k_pred = exponential_model(T_data, a_fit, b_fit)
            residuals = k_data - k_pred

            mae = np.mean(np.abs(residuals))
            rmse = np.sqrt(np.mean(residuals ** 2))

            weights = 1 / (sigma_k_data ** 2)
            ss_res_w = np.sum(weights * (residuals ** 2))
            weighted_mean = np.sum(weights * k_data) / np.sum(weights)
            ss_tot_w = np.sum(weights * ((k_data - weighted_mean) ** 2))
            r2_w = 1 - (ss_res_w / ss_tot_w)

            print(f"--- Fungi: {fungus_name} ---")
            print(f"  Model: k(T) = a * exp(b * T)")
            print(f"    a = {a_fit:.4f} (SE = {a_se:.4f}, p = {p_a:.4f})")
            print(f"    b = {b_fit:.4f} (SE = {b_se:.4f}, p = {p_b:.4f})")
            print(f"    pcov:\n{covariance}")
            print(f"    R² = {r2_w:.4f}")
            print(f"    RMSE    = {rmse:.4f}")
            print(f"    MAE     = {mae:.4f}\n")

            mean_params = np.array([a_fit, b_fit])
            N_ITERATIONS = 10
            param_samples = np.random.multivariate_normal(mean_params, covariance, size=N_ITERATIONS)
            a_samples = param_samples[:, 0]
            b_samples = param_samples[:, 1]

            plt.figure(figsize=(8, 6))
            plt.errorbar(T_data, k_data, yerr=sigma_k_data, fmt='o', color='royalblue', markersize=8, capsize=5,
                         label='Aggregated data and errors')
            T_fit = np.linspace(min(T_data) - 2, max(T_data) + 2, 200)
            k_fit = exponential_model(T_fit, a_fit, b_fit)
            plt.plot(T_fit, k_fit, label='Weighted fit curve', color='orangered', linestyle='--')

            stats_text = (
                f'Weighted $R^2$ = {r2_w:.3f}\n'
                f'RMSE = {rmse:.3f}\n'
                # f'p-value = {p_b:.3f}'
            )
            plt.text(0.2, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=16, verticalalignment='top')
            # plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=12,
            #          verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

            plt.title(f'{fungus_name}', fontsize=20)
            plt.tick_params(axis='x', labelsize=16)
            plt.tick_params(axis='y', labelsize=16)
            # plt.xlabel('Temperature (°C)', fontsize=12)
            # plt.ylabel('Annual Decomposition Rate (%/year)', fontsize=12)
            # plt.legend(loc='lower right', fontsize=10)
            # plt.grid(True, which='both', linestyle='--', linewidth=0.5)
            plt.tight_layout()
            save_path = '../Figure/Decomp K/' + fungus_name + '.png'
            plt.savefig(save_path, dpi=300)
            plt.show()

        except RuntimeError:
            print(f"Could not find optimal parameters for fungus '{fungus_name}'.")
        except Exception as e:
            print(f"Unknown error while fitting fungus '{fungus_name}': {e}")


def main(file_path, out_path=None):
    try:
        # file_path = 'wood_decay_data.xlsx'
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        return
    except Exception as e:
        return

    df['Wood mass loss (%)'] = estimate_missing_sd_hierarchical(df)

    df['k (year^-1)'] = calculate_k(df['Wood mass loss (%)'], df['Degradation time (days)'])
    df['sigma_k (year^-1)'] = propagate_k_error(df['Wood mass loss (%)'], df['Wood mass loss (%)'], df['Degradation time (days)'])

    aggregated_data = aggregate_k_with_error(df)

    if out_path is not None:
        aggregated_data.to_excel(out_path, index=False)
    fit_and_plot_weighted_individual(aggregated_data)


if __name__ == '__main__':
    file_path = r'/Decomposition Rate Data/Decomposition-rate.xlsx'
    main(file_path)
