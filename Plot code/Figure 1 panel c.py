import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['figure.dpi'] = 300

COLOR_WHITE_ROT = "#0070FF"
COLOR_BROWN_ROT = "#9FD7ED"

species_params = {
    'Fomes fomentarius': [0.0956, 0.1237, 'W'],
    'Fomitiporia hartigii': [0.0094, 0.2008, 'W'],
    'Fuscoporia gilva': [0.0572, 0.1201, 'W'],
    'Hyphoderma setigerum': [0.0508, 0.0821, 'W'],
    'Lyomyces crustosus': [0.0466, 0.1068, 'W'],
    'Merulius tremellosus': [0.2275, 0.0956, 'W'],
    'Phellinus robiniae': [0.0160, 0.1595, 'W'],
    'Phlebiopsis flavidoalba': [0.1013, 0.0996, 'W'],
    'Pleurotus ostreatus': [0.4034, 0.0554, 'W'],
    'Porodisculus pendulus': [0.0373, 0.0559, 'W'],
    'Trametes sanguinea': [0.0321, 0.1455, 'W'],
    'Trametes versicolor': [0.1993, 0.0808, 'W'],
    'Tyromyces chioneus': [0.0652, 0.1086, 'W'],
    'Xylobolus subpileatus': [0.0234, 0.1178, 'W'],
    'Amyloporia xantha': [0.7547, -0.1675, 'B'],
    'Fomitopsis pinicola': [0.0202, 0.1401, 'B'],
    'Gloeophyllum trabeum': [0.2767, 0.0742, 'B'],
    'Laetiporus conifericola': [0.0209, 0.1200, 'B'],
    'Rhodonia placenta': [51.5350, -0.1522, 'B'],
}


def exponential_model(T, a, b):
    T_arr = np.asarray(T, dtype=np.float64)
    return a * np.exp(b * T_arr)


def plot_figure1_c_combined(species_params):
    T_range = np.linspace(-5, 35, 100).astype(np.float64)

    w_curves = []
    b_curves = []

    fig, ax = plt.subplots(figsize=(6, 5))


    for sp_name, params in species_params.items():
        a, b, group = params
        k_values = exponential_model(T_range, a, b)

        if group == 'W':
            color = COLOR_WHITE_ROT
            w_curves.append(k_values)
            zorder = 2
        else:
            color = COLOR_BROWN_ROT
            b_curves.append(k_values)
            zorder = 3

        ax.plot(T_range, k_values, color=color, alpha=0.15, linewidth=1.0, zorder=zorder)

    def plot_group_mean(curves, color, label, z_line, z_fill):
        if not curves:
            print(f"Error: No data for {label}, skipping plot.")
            return

        curves_np = np.array(curves, dtype=np.float64)

        mean = np.mean(curves_np, axis=0)
        std = np.std(curves_np, axis=0)
        sem = std / np.sqrt(len(curves))

        ci_upper = mean + 1.96 * sem
        ci_lower = mean - 1.96 * sem

        x_clean = np.asarray(T_range, dtype=np.float64).flatten()
        y1_clean = np.asarray(ci_lower, dtype=np.float64).flatten()
        y2_clean = np.asarray(ci_upper, dtype=np.float64).flatten()
        mean_clean = np.asarray(mean, dtype=np.float64).flatten()

        ax.plot(x_clean, mean_clean, color=color, linewidth=3, label=label, zorder=z_line)

        try:
            ax.fill_between(x_clean, y1_clean, y2_clean,
                            color=color, alpha=0.2, edgecolor='none', zorder=z_fill)
        except Exception as e:
            print(f"Error: Failed to plot shadow for {label} ({e}), but main curve is plotted.")

    print("Drawing white-rot fungal average trend...")
    plot_group_mean(w_curves, COLOR_WHITE_ROT, 'White-rot (Mean)', 4, 2)

    print("Drawing brown-rot fungal average trend...")
    plot_group_mean(b_curves, COLOR_BROWN_ROT, 'Brown-rot (Mean)', 5, 3)

    ax.set_xlabel('Temperature (°C)', fontsize=20)
    ax.set_ylabel('Decomposition Rate K (yr)', fontsize=20)
    ax.set_xlim(-5, 35)

    sns.despine()
    plt.tight_layout()

    output_file = '../Figure/Figure1 panel c 20251129.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    plot_figure1_c_combined(species_params)