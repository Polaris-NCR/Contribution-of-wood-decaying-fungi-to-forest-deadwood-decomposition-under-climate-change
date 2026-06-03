import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import sys
import random
import pandas as pd
import seaborn as sns


def cal_average_above_zero(raster):
    values = raster[raster > 0]
    return np.mean(values)


def cal_average_richness(raster, condition_mask_boreal, condition_mask_tropical, condition_mask_temperate):
    # output_array = np.zeros(raster.shape, dtype=raster.dtype)
    # output_array[condition_mask_boreal] = raster[condition_mask_boreal]
    output_array = raster[condition_mask_boreal]
    # print(output_array.shape)
    richness_boreal = np.mean(output_array)
    # richness_boreal = cal_average_above_zero(output_array)
    output_array = None

    # output_array = np.zeros(raster.shape, dtype=raster.dtype)
    # output_array[condition_mask_tropical] = raster[condition_mask_tropical]
    output_array = raster[condition_mask_tropical]
    richness_tropical = np.mean(output_array)
    # richness_tropical = cal_average_above_zero(output_array)
    output_array = None

    # output_array = np.zeros(raster.shape, dtype=raster.dtype)
    # output_array[condition_mask_temperate] = raster[condition_mask_temperate]
    output_array = raster[condition_mask_temperate]
    richness_temperate = np.mean(output_array)
    # richness_temperate = cal_average_above_zero(output_array)
    output_array = None

    stock_list = [richness_boreal, richness_temperate, richness_tropical]
    return stock_list


def plot_richness(data, savepath=None):
    df = pd.DataFrame(data)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 6))
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 20
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.titlesize'] = 20
    plt.rcParams['xtick.labelsize'] = 20
    plt.rcParams['ytick.labelsize'] = 20

    sns.pointplot(
        data=df,
        x='Scenario',
        y='Richness',
        hue='Forest Type',
        markers=['o', 's', '^'],
        # linestyles=['-', '--', '-.'],
        # palette=['#A2FF9B','#55FF00','#37A800'],
        # palette=['#4DB6AC', '#00897B', '#004D40'],
        palette=['#53BD7D', '#21AD5D', '#0E600F'],
        scale=1.2,
    )

    # plt.title('Trend of Richness Changes Across Scenarios', fontsize=16, fontweight='bold')
    # plt.xlabel('Climate Scenario', fontsize=14)
    # plt.ylabel('Mean Fungal Richness', fontsize=14)
    plt.xlabel('')
    plt.ylabel('')
    plt.legend(title='Forest Type', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()

    if savepath is not None:
        # output_filename = 'forest_richness_comparison.png'
        plt.savefig(savepath, dpi=300)

    plt.show()

# CWD_path = 'F:\\Fungi data\\Deadwood.tif'
# cwd_raster = gdal.Open(CWD_path).ReadAsArray()

region_path = r"F:\Fungi data\FAO_ecozones.tif"
region_raster = gdal.Open(region_path).ReadAsArray()

condition_mask_boreal = (region_raster == 1) | (region_raster == 9)
condition_mask_tropical = (region_raster == 2) | (region_raster == 3)
condition_mask_temperate = (region_raster == 4) | (region_raster == 5) | (region_raster == 6) | (region_raster == 7) | (
        region_raster == 8)
region_raster = None

base_img = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
base_raster = gdal.Open(base_img).ReadAsArray()
condition_mask_boreal = condition_mask_boreal & (base_raster > 0)
# plt.imshow(condition_mask_boreal)
# plt.show()
condition_mask_tropical = condition_mask_tropical & (base_raster > 0)
condition_mask_temperate = condition_mask_temperate & (base_raster > 0)
base_raster = None

baseline_path = r'F:\Fungi SDM new\Competition\Total-fungi-accumulate-probability-Baseline.tif'
baseline_raster=gdal.Open(baseline_path).ReadAsArray()
richness_list = cal_average_richness(baseline_raster, condition_mask_boreal, condition_mask_tropical,
                                     condition_mask_temperate)
print(richness_list)
# baseline_raster_mask=baseline_raster[mask]
# print(baseline_raster_mask.shape)
# print(np.mean(baseline_raster_mask))

ssp245_path = r'F:\Fungi SDM new\Competition\Total-fungi-accumulate-probability-ssp245.tif'
ssp245_raster=gdal.Open(ssp245_path).ReadAsArray()
richness_list = cal_average_richness(ssp245_raster, condition_mask_boreal, condition_mask_tropical,
                                     condition_mask_temperate)
print(richness_list)
# ssp245_raster_mask=ssp245_raster[mask]
# print(np.mean(ssp245_raster_mask))

ssp585_path = r'F:\Fungi SDM new\Competition\Total-fungi-accumulate-probability-ssp585.tif'
ssp585_raster=gdal.Open(ssp585_path).ReadAsArray()
richness_list = cal_average_richness(ssp585_raster, condition_mask_boreal, condition_mask_tropical,
                                     condition_mask_temperate)
print(richness_list)
# ssp585_raster_mask=ssp585_raster[mask]
# print(np.mean(ssp585_raster_mask))