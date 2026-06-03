import matplotlib.pyplot as plt
import numpy as np

y_data = [0, 1, 2, 3, 4, 5, 6, 7, 8]

labels = [
    'Tropical Baseline',
    'Tropical SSP245',
    'Tropical ssp585',
    'Temperate Baseline',
    'Temperate SSP245',
    'Temperate ssp585',
    'Boreal Baseline',
    'Boreal SSP245',
    'Boreal ssp585',
]
# net color
colors = [
    '#fee090',  # Light Orange
    '#f46d43',  # Red-Orange
    '#d73027',  # Dark Red
    '#fee090',  # Light Orange
    '#f46d43',  # Red-Orange
    '#d73027',  # Dark Red
    '#fee090',  # Light Orange
    '#f46d43',  # Red-Orange
    '#d73027',  # Dark Red
]

# seq color
# colors = [
#     '#a8ddb5',  # Light Green
#     '#41ab5d',  # Medium Green
#     '#006d2c',  # Dark Green
#     '#a8ddb5',  # Light Green
#     '#41ab5d',  # Medium Green
#     '#006d2c',  # Dark Green
#     '#a8ddb5',  # Light Green
#     '#41ab5d',  # Medium Green
#     '#006d2c',  # Dark Green
# ]

# [tropical baseline ssp245 ssp585, temperate baseline ssp245 ssp585, boreal baseline ssp245 ssp585,]
#  net carbon
x_centers = [0.074526795, 0.0587531, 0.046412887, 0.027088273, 0.026757182, 0.023595738, 0.045719004, 0.05089614,
             0.047765017]
x_errors = [0.036957888, 0.024477477, 0.021724727, 0.002999408, 0.004142789, 0.003565561, 0.006727826, 0.010083749,
            0.007974332]

# #  atm carbon
x_centers = [0.115031138, 0.091031374, 0.072037215, 0.043686941, 0.043572287, 0.038559445, 0.072719091, 0.08267936,
             0.078645106]
x_errors = [0.056493903, 0.038276713, 0.03401712, 0.005064125, 0.00707152, 0.005744153, 0.011568363, 0.017613159,
            0.012780468]

# #  seq carbon
# x_centers = [0.040504343, 0.032278274, 0.025624328, 0.016598669, 0.016815104, 0.014963707, 0.027000087, 0.03178322,
#              0.030880089]
# x_errors = [0.019536015, 0.002064717, 0.004840537, 0.013799237, 0.00292873, 0.007529411, 0.012292393, 0.002178592,
#             0.004806136]

fig, ax = plt.subplots(figsize=(8, 4.5))

for i in range(len(x_centers)):
    ax.errorbar(x_centers[i], y_data[i],
                xerr=x_errors[i],
                fmt='o',
                markersize=12,
                capsize=0,
                color=colors[i],
                ecolor=colors[i],
                elinewidth=3,
                markeredgecolor='none',
                zorder=10)

for i in range(len(x_centers)):
    left_x = x_centers[i] - x_errors[i]
    right_x = x_centers[i] + x_errors[i]
    ax.plot([left_x, left_x], [y_data[i] - 0.1, y_data[i] + 0.1],
            color=colors[i], linewidth=3, zorder=10)
    ax.plot([right_x, right_x], [y_data[i] - 0.1, y_data[i] + 0.1],
            color=colors[i], linewidth=3, zorder=10)

# ax.set_xticks([0.03, 0.06, 0.09, 0.12])  # C net
# ax.set_xticks([0.02, 0.04, 0.06, 0.08])  # C seq
ax.set_xticks([0.05, 0.10, 0.15, 0.20])  # C atm
ax.tick_params(axis='x', labelsize=22, direction='out')
ax.set_yticks(y_data)
ax.set_yticklabels('')
ax.yaxis.tick_right()
ax.tick_params(axis='y', which='both', length=5, pad=5)
ax.set_ylim(-0.8, 8.8)
# ax.set_xlim(0.01, 0.12)  # net carbon release
# ax.set_xlim(0, 0.08)  # C seq
ax.set_xlim(0.02, 0.2)  # C atm

plt.tight_layout(rect=[0, 0, 0.95, 1])
# plt.savefig(r'E:\Figure\net carbon emission 20251227.png', dpi=300)
# plt.savefig(r'E:\Figure\C retention 20251227.png', dpi=300)
plt.savefig(r'E:\Figure\C emission 20251227.png', dpi=300)
plt.show()