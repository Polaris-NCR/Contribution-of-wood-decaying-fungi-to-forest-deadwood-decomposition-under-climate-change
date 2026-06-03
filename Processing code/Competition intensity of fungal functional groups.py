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


fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum',
                 'Hyphodermasetigerum', 'Laetiporusconifericola', 'Lyomycescrustosus', 'Meruliustremellosus',
                 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

white_species = ['Fomesfomentarius', 'Fomitiporiahartigii', 'Fuscoporiagilva', 'Hyphodermasetigerum',
                 'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Trametessanguinea', 'Trametesversicolor',
                 'Tyromyceschioneus', 'Xylobolussubpileatus']
brown_species = ['Amyloporiaxantha', 'Fomitopsispinicola', 'Gloeophyllumtrabeum', 'Laetiporusconifericola',
                 'Rhodoniaplacenta']

scenario_lists = ['Baseline', 'SSP245', 'SSP585']

SDM_folder = 'F:\\Fungi SDM new\\'

Fungi_baseline = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
Fungi_baseline_img = gdal.Open(Fungi_baseline)
geo = Fungi_baseline_img.GetGeoTransform()
proj = Fungi_baseline_img.GetProjection()
print('geo', geo)
print('proj', proj)
fungus_prob = Fungi_baseline_img.ReadAsArray()
process_mask = (fungus_prob > 0)

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(brown_species)):
        print(brown_species[j])
        SDM_path = SDM_folder + brown_species[j] + '\\' + brown_species[j] + '-SDM-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-Brown-fungi-SDM-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(fungi_species)):
        print(fungi_species[j])
        SDM_path = SDM_folder + fungi_species[j] + '\\' + fungi_species[j] + '-SDM-std-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-Total-fungi-SDM-std-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(white_species)):
        print(white_species[j])
        SDM_path = SDM_folder + white_species[j] + '\\' + white_species[j] + '-SDM-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-White-fungi-SDM-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(fungi_species)):
        print(fungi_species[j])
        SDM_path = SDM_folder + fungi_species[j] + '\\' + fungi_species[j] + '-SDM-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-Total-fungi-SDM-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(brown_species)):
        print(brown_species[j])
        SDM_path = SDM_folder + brown_species[j] + '\\' + brown_species[j] + '-SDM-std-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-Brown-fungi-SDM-std-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None

for i in range(len(scenario_lists)):
    print(scenario_lists[i])
    output_raster = np.full(fungus_prob.shape, 0, dtype=np.float32)
    for j in range(len(white_species)):
        print(white_species[j])
        SDM_path = SDM_folder + white_species[j] + '\\' + white_species[j] + '-SDM-std-' + scenario_lists[i] + '.tif'
        SDM_raster = gdal.Open(SDM_path).ReadAsArray()
        output_raster += SDM_raster
        SDM_raster = None
    output_raster = np.where(fungus_prob > 0, output_raster, 0)
    output_path = 'F:\\Fungi SDM new\\Competition\\' + 'Competition-White-fungi-SDM-std-' + scenario_lists[i] + '.tif'
    Export_image(output_raster, geo, proj, output_path, nodata_value=0)
    output_raster = None