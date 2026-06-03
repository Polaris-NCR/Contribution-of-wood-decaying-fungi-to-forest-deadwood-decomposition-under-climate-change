import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 40
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['figure.dpi'] = 300

biomes = ['Boreal', 'Temperate', 'Tropical']
means = [28.95, 12.98, 47.33]  # Pg C
errors = [14.32, 6.19, 26.33]  # SD


# colors = ['#00734C', '#55FF00', '#D1FF73']
# colors = ['#D1FF73', '#55FF00', '#00734C']
colors = ['#A6FF9B', '#55FF00', '#00734C']


fig, ax = plt.subplots(figsize=(3, 2.5)) 


bars = ax.bar(
    biomes,
    means,
    yerr=errors,     
    capsize=4,       
    color=colors,     
    edgecolor='black',
    linewidth=0.8,    
    alpha=0.8,       
    width=0.6        
)

sns.despine()

ax.set_xticklabels(biomes, fontsize=9, rotation=0)

ax.tick_params(axis='y', labelsize=9)

for bar, mean in zip(bars, means):
    height = bar.get_height()

fig.patch.set_alpha(0.0)
ax.patch.set_alpha(0.0)


plt.tight_layout()

plt.savefig('../Figure/Figure 1 panel b Insert 20251208.png', dpi=300, bbox_inches='tight', transparent=True)
plt.show()