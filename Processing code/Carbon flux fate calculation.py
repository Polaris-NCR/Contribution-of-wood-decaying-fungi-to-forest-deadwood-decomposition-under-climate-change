import os
import pickle
import joblib
import matplotlib.pyplot as plt
import rasterio
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
import geopandas as gpd
from matplotlib import font_manager
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import ListedColormap, BoundaryNorm
from osgeo import gdal, osr
import matplotlib.font_manager as fm
from scipy.interpolate import interp1d


def Export_image(output_data, geotransform, projection, output_filepath, nodata_value=0):
    driver = gdal.GetDriverByName("GTiff")

    rows, cols = output_data.shape
    output_dataset = driver.Create(
        output_filepath,
        cols,
        rows,
        1,
        gdal.GDT_Float32
    )

    output_dataset.SetGeoTransform(geotransform)
    output_dataset.SetProjection(projection)

    output_band = output_dataset.GetRasterBand(1)

    if nodata_value is not None:
        output_band.SetNoDataValue(float(nodata_value))

    output_band.WriteArray(output_data)

    output_band.FlushCache()
    output_dataset = None


def cal_carbon_stock(raster, area):
    pixels_mask = (raster > 0)
    pixels_to_sum = raster[pixels_mask]
    total_sum = np.sum(pixels_to_sum) * area * 1e-9
    return total_sum


# Based SDM
Fungi_baseline = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
Fungi_baseline_img = gdal.Open(Fungi_baseline)
geo = Fungi_baseline_img.GetGeoTransform()
proj = Fungi_baseline_img.GetProjection()

area = geo[1] * abs(geo[5]) * 111.32 * 111.32

fungus_prob = Fungi_baseline_img.ReadAsArray()
process_mask = (fungus_prob > 0)

Forest_needle_path = r'F:\Fungi data\Forest_Needleleaf-1km.tif'
Forest_broad_path = r'F:\Fungi data\Forest_Broadleaf-1km.tif'
Forest_needle_raster = gdal.Open(Forest_needle_path).ReadAsArray()
Forest_broad_raster = gdal.Open(Forest_broad_path).ReadAsArray()

sdm_positive = (fungus_prob > 0)
is_conif = (Forest_needle_raster == 1)
is_broad = (Forest_broad_raster == 1)
conditions = [
    (sdm_positive) & (is_conif),  
    (sdm_positive) & (is_broad), 
    (sdm_positive) & (~is_conif) & (~is_broad) 
]

# Lignin content: coniferous 0.32, broadleaf 0.22, mixed forest 0.27
choices = [0.32, 0.22, 0.27]


Cseq_list = []
for i in range(len(choices)):
    seq_num = choices[i] * 0.8 + (1 - choices[i]) * 0.25
    Cseq_list.append(seq_num)
print(Cseq_list)

# Lignin_arr = np.select(conditions, choices, default=0.0)
# Lignin_arr[fungus_prob == 0] = 0
Cseq_arr = np.select(conditions, Cseq_list, default=0.0)
Cseq_arr[fungus_prob == 0] = 0

Forest_needle_raster = None
Forest_broad_raster = None

# plt.imshow(Cseq_arr)
# plt.show()

fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum', 'Hyphodermasetigerum', 'Laetiporusconifericola',
                 'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']
white_species = ['Fomesfomentarius', 'Fomitiporiahartigii', 'Fuscoporiagilva', 'Hyphodermasetigerum',
                 'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Trametessanguinea', 'Trametesversicolor',
                 'Tyromyceschioneus', 'Xylobolussubpileatus']
brown_species = ['Amyloporiaxantha', 'Fomitopsispinicola', 'Gloeophyllumtrabeum', 'Laetiporusconifericola',
                 'Rhodoniaplacenta']
scenario_lists = ['Baseline', 'ssp245', 'ssp585']

Cseq = np.full(fungus_prob.shape, 0, dtype=np.float32)
Catm = np.full(fungus_prob.shape, 0, dtype=np.float32)

Baseline_carbon_seq = []
Baseline_carbon_atm = []
ssp245_carbon_seq = []
ssp585_carbon_seq = []
ssp245_carbon_atm = []
ssp585_carbon_atm = []
# Export Cseq & Cflux
for j in range(len(scenario_lists)):
    Cseq_brown = np.full(fungus_prob.shape, 0, dtype=np.float32)
    Catm_brown = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for k in range(len(brown_species)):
        # carbon_path = 'F:\\Fungi Carbon\\' + brown_species[k] + '-carbon-' + scenario_lists[j] + '.tif'
        carbon_path = 'F:\\Fungi Carbon add Competition\\' + brown_species[k] + '-carbon-' + scenario_lists[j] + '.tif'
        print(carbon_path)
        carbon_raster = gdal.Open(carbon_path).ReadAsArray()
        carbon_seq = carbon_raster * Cseq_arr
        carbon_atm = carbon_raster - carbon_seq
        carbon_seq_num = cal_carbon_stock(carbon_seq, area)
        carbon_seq_atm = cal_carbon_stock(carbon_atm, area)
        print('carbon_seq_num', carbon_seq_num)
        print('carbon_seq_atm', carbon_seq_atm)
        if scenario_lists[j] == 'Baseline':
            Baseline_carbon_seq.append(carbon_seq_num)
            Baseline_carbon_seq.append(carbon_seq_atm)
        elif scenario_lists[j] == 'ssp245':
            ssp245_carbon_seq.append(carbon_seq_num)
            ssp245_carbon_atm.append(carbon_seq_atm)
        else:
            ssp585_carbon_seq.append(carbon_seq_num)
            ssp585_carbon_atm.append(carbon_seq_atm)
        Cseq_brown += carbon_seq / 100
        Catm_brown += carbon_atm / 100
        carbon_seq = None
        carbon_atm = None
    # Cseq_brown_outpath = 'F:\\Fungi Carbon\\' + 'Brown-fungi-C-seq-' + scenario_lists[j] + '.tif'
    # Catm_brown_outpath = 'F:\\Fungi Carbon\\' + 'Brown-fungi-C-atm-' + scenario_lists[j] + '.tif'
    Cseq_brown_outpath = 'F:\\Fungi Carbon add Competition\\' + 'Brown-fungi-C-seq-' + scenario_lists[j] + '.tif'
    Catm_brown_outpath = 'F:\\Fungi Carbon add Competition\\' + 'Brown-fungi-C-atm-' + scenario_lists[j] + '.tif'
    Export_image(Cseq_brown, geo, proj, Cseq_brown_outpath, nodata_value=0)
    Export_image(Catm_brown, geo, proj, Catm_brown_outpath, nodata_value=0)
    Cseq_brown = None
    Catm_brown = None

for m in range(len(scenario_lists)):
    Cseq_white = np.full(fungus_prob.shape, 0, dtype=np.float32)
    Catm_white = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for n in range(len(white_species)):
        # carbon_path = 'F:\\Fungi Carbon\\' + white_species[n] + '-carbon-' + scenario_lists[m] + '.tif'
        carbon_path = 'F:\\Fungi Carbon add Competition\\' + white_species[n] + '-carbon-' + scenario_lists[m] + '.tif'
        print(carbon_path)
        carbon_raster = gdal.Open(carbon_path).ReadAsArray()
        carbon_seq = carbon_raster * 0.25
        carbon_atm = carbon_raster - carbon_seq
        carbon_seq_num = cal_carbon_stock(carbon_seq, area)
        carbon_seq_atm = cal_carbon_stock(carbon_atm, area)
        print('carbon_seq_num', carbon_seq_num)
        print('carbon_seq_atm', carbon_seq_atm)
        if scenario_lists[j] == 'Baseline':
            Baseline_carbon_seq.append(carbon_seq_num)
            Baseline_carbon_seq.append(carbon_seq_atm)
        elif scenario_lists[j] == 'ssp245':
            ssp245_carbon_seq.append(carbon_seq_num)
            ssp245_carbon_atm.append(carbon_seq_atm)
        else:
            ssp585_carbon_seq.append(carbon_seq_num)
            ssp585_carbon_atm.append(carbon_seq_atm)
        Cseq_white += carbon_seq / 100
        Catm_white += carbon_atm / 100
        carbon_seq = None
        carbon_atm = None
    # Cseq_brown_outpath = 'F:\\Fungi Carbon\\' + 'White-fungi-C-seq-' + scenario_lists[m] + '.tif'
    # Catm_brown_outpath = 'F:\\Fungi Carbon\\' + 'White-fungi-C-atm-' + scenario_lists[m] + '.tif'
    Cseq_brown_outpath = 'F:\\Fungi Carbon add Competition\\' + 'White-fungi-C-seq-' + scenario_lists[m] + '.tif'
    Catm_brown_outpath = 'F:\\Fungi Carbon add Competition\\' + 'White-fungi-C-atm-' + scenario_lists[m] + '.tif'
    Export_image(Cseq_white, geo, proj, Cseq_brown_outpath, nodata_value=0)
    Export_image(Catm_white, geo, proj, Catm_brown_outpath, nodata_value=0)
    Cseq_white = None
    Catm_white = None