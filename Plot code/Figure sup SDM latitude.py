import matplotlib.pyplot as plt
import rasterio
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap, BoundaryNorm
from osgeo import gdal, osr

fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum',
                 'Hyphodermasetigerum', 'Laetiporusconifericola', 'Lyomycescrustosus', 'Meruliustremellosus',
                 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']


def calculate_valid_mean(raster_array):
    masked_array = np.ma.masked_less_equal(raster_array, 0)

    mean_values = np.ma.mean(masked_array, axis=1)

    return mean_values.filled(0)


for i in range(len(fungi_species)):
    print('fungi', fungi_species[i])
    baseline_path = 'F:\\Fungi SDM new\\' + fungi_species[i] + '\\' + fungi_species[i] + '-SDM-Baseline.tif'
    ssp245_path = 'F:\\Fungi SDM new\\' + fungi_species[i] + '\\' + fungi_species[i] + '-SDM-SSP245.tif'
    ssp585_path = 'F:\\Fungi SDM new\\' + fungi_species[i] + '\\' + fungi_species[i] + '-SDM-SSP585.tif'

    raster_baseline = gdal.Open(baseline_path).ReadAsArray()
    raster_ssp245 = gdal.Open(ssp245_path).ReadAsArray()
    raster_ssp585 = gdal.Open(ssp585_path).ReadAsArray()

    # average_richness_baseline = np.ma.mean(raster_baseline, axis=1)
    # average_richness_ssp245 = np.ma.mean(raster_ssp245, axis=1)
    # average_richness_ssp585 = np.ma.mean(raster_ssp585, axis=1)
    average_richness_baseline = calculate_valid_mean(raster_baseline)
    average_richness_ssp245 = calculate_valid_mean(raster_ssp245)
    average_richness_ssp585 = calculate_valid_mean(raster_ssp585)

    src = rasterio.open(baseline_path)
    lats = np.linspace(src.bounds.top, src.bounds.bottom, raster_baseline.shape[0])

    raster_baseline = None
    raster_ssp245 = None
    raster_ssp585 = None

    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.unicode_minus'] = False
    font = fm.FontProperties(family='Arial', size=16)
    # plt.plot(average_richness_baseline, lats, color='#F1B656', linewidth=1, label='Baseline')
    # plt.plot(average_richness_ssp245, lats, color='#397FC7', linewidth=1, label='SSP245')
    # plt.plot(average_richness_ssp585, lats, color='#040676', linewidth=1, label='SSP585')
    plt.plot(average_richness_baseline, lats, color='#F1B656', linewidth=1)
    plt.plot(average_richness_ssp245, lats, color='#397FC7', linewidth=1)
    plt.plot(average_richness_ssp585, lats, color='#040676', linewidth=1)
    # plt.title('Average Fungal Richness by Latitude', fontproperties=font, pad=20)
    # plt.xlabel('Carbon Emission (Pg C)', fontproperties=font)
    plt.xticks(fontname='Arial', fontsize=16)
    plt.yticks(fontname='Arial', fontsize=16)
    plt.ylabel('Latitude (°)', fontproperties=font)

    # plt.grid(linestyle='--', alpha=0.7)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(top=False, right=False)

    # plt.xlim(0, np.max(average_richness_ssp585) + 0.1)
    max_val = np.nanmax(average_richness_ssp585) if not np.all(np.isnan(average_richness_ssp585)) else 1
    plt.xlim(0, max_val + 0.1)
    plt.ylim([-60, 80])
    # legend = plt.legend(fontsize=16)
    # legend.set_frame_on(False)
    plt.tight_layout()
    outpath = '..\Figure\SDM results\\' + fungi_species[i] + '-latitude-statistics.png'
    plt.savefig(outpath, dpi=300)
    # plt.show()
    plt.close()
