import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

file_path = r"/Cseq & Catm.csv"

print(f"Loading: {file_path}...")

df = pd.read_csv(file_path)

print("\nDataFrame Head:")
print(df.head())


df_long = df.melt(
    id_vars=['Fungi', 'Fungi type', 'scenario'],
    value_vars=['carbon seq', 'carbon atm'],
    var_name='Flux Type',
    value_name='Carbon Flux (Pg C)'
)

df_long.rename(columns={
    'Fungi': 'Fungus Name',
    'Fungi type': 'Fungus Type',
    'scenario': 'Scenario'
}, inplace=True)

df_long['Flux Type'] = df_long['Flux Type'].map({
    'carbon seq': 'Carbon Sequestration (seq)',
    'carbon atm': 'Carbon Emission (atm)'
})

df_long['Scenario'] = pd.Categorical(
    df_long['Scenario'],
    categories=['Baseline', 'SSP245', 'SSP585'],
    ordered=True
)

df_long['Fungus Type'] = df_long['Fungus Type'].map({
    'Brown': 'Brown-rot',
    'White': 'White-rot'
})


print(df_long.head())

sns.set(style="ticks", context="paper", font_scale=1.2)

custom_palette = {
    "Brown-rot": "#a6cee3",  # 淡蓝色
    "White-rot": "#1f78b4"   # 蓝色
}

g = sns.catplot(
    data=df_long,
    x='Scenario',
    y='Carbon Flux (Pg C)',
    hue='Fungus Type',
    col='Flux Type',
    kind='box',
    height=5,
    aspect=1.1,
    palette=custom_palette,
    legend=False,
    dodge=True,
    # sharey=False,
    width=0.4
)


g.map_dataframe(
    sns.stripplot,
    x='Scenario',
    y='Carbon Flux (Pg C)',
    hue='Fungus Type',
    dodge=True,
    jitter=0.1,
    alpha=0.7,
    palette=custom_palette, 
    marker='o',
    s=5,
    edgecolor='gray',
    linewidth=0.5
)

for ax in g.axes.flat:
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.01))
    ax.set_ylabel(ax.get_ylabel(), fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

g.set_axis_labels("", "")

g.set_titles("")

g.tight_layout()

plot_file_png = 'fungal_carbon_flux_boxplot_competition_v5.png'
plot_file_pdf = 'fungal_carbon_flux_boxplot_competition_v5.pdf'

g.savefig(plot_file_png, dpi=300, bbox_inches='tight')
g.savefig(plot_file_pdf, bbox_inches='tight')

print(f"\nSaved at: {plot_file_png} 和 {plot_file_pdf}")