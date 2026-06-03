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


def calculate_masked_mean(raster_array):
    mask_condition = (raster_array <= 0)

    masked_raster = np.ma.masked_where(mask_condition, raster_array)

    average_by_latitude = np.ma.mean(masked_raster, axis=1).filled(np.nan)

    return average_by_latitude


folder = 'F:\\Fungi Carbon add Competition\\'

carbon_path = ['C-atm', 'C-seq']
scenario = ['Baseline', 'ssp245', 'ssp585']

for i in range(len(carbon_path)):
    for j in range(len(scenario)):
        brown_path = folder + 'Brown-fungi-' + carbon_path[i] + '-std-' + scenario[j] + '.tif'
        geo = gdal.Open(brown_path).GetGeoTransform()
        proj = gdal.Open(brown_path).GetProjection()
        brown_raster = gdal.Open(brown_path).ReadAsArray()
        white_path = folder + 'White-fungi-' + carbon_path[i] + '-std-' + scenario[j] + '.tif'
        white_raster = gdal.Open(white_path).ReadAsArray()
        out_raster = brown_raster + white_raster

        out_path = r'F:\Fungi Carbon add Competition\\' + 'Fungi-' + carbon_path[i] + '-std-' + scenario[j] + '.tif'

        Export_image(out_raster, geo, proj, out_path, nodata_value=0)
        brown_raster = None
        white_raster = None
        out_raster = None

for i in range(len(carbon_path)):
    for j in range(len(scenario)):
        brown_path = folder + 'Brown-fungi-' + carbon_path[i] + '-' + scenario[j] + '.tif'
        geo = gdal.Open(brown_path).GetGeoTransform()
        proj = gdal.Open(brown_path).GetProjection()
        brown_raster = gdal.Open(brown_path).ReadAsArray()
        white_path = folder + 'White-fungi-' + carbon_path[i] + '-' + scenario[j] + '.tif'
        white_raster = gdal.Open(white_path).ReadAsArray()
        out_raster = brown_raster + white_raster

        out_path = r'F:\Fungi Carbon add Competition\\' + 'Fungi-' + carbon_path[i] + '-' + scenario[j] + '.tif'

        Export_image(out_raster, geo, proj, out_path, nodata_value=0)
        brown_raster = None
        white_raster = None
        out_raster = None

for k in range(len(scenario)):
    print(scenario[k])
    atm_path = folder + 'Fungi-C-atm-' + scenario[k] + '.tif'
    seq_path = folder + 'Fungi-C-seq-' + scenario[k] + '.tif'

    geo = gdal.Open(atm_path).GetGeoTransform()
    proj = gdal.Open(atm_path).GetProjection()
    atm_raster = gdal.Open(atm_path).ReadAsArray()
    seq_raster = gdal.Open(seq_path).ReadAsArray()
    out_raster = atm_raster - seq_raster

    out_path = r'F:\Fungi Carbon add Competition\\' + 'Fungi-net-C-' + scenario[k] + '.tif'

    Export_image(out_raster, geo, proj, out_path, nodata_value=0)
    brown_raster = None
    white_raster = None
    out_raster = None

folder = 'F:\\Fungi Carbon add Competition\\'

carbon_path = ['C-atm', 'C-seq', 'net-C']
for i in range(len(carbon_path)):
    print(carbon_path[i])
    baseline_path = folder + 'Fungi-' + carbon_path[i] + '-Baseline.tif'
    ssp585_path = folder + 'Fungi-' + carbon_path[i] + '-ssp585.tif'
    baseline_img = gdal.Open(baseline_path).ReadAsArray()
    ssp585_img = gdal.Open(ssp585_path).ReadAsArray()
    geo = gdal.Open(baseline_path).GetGeoTransform()
    proj = gdal.Open(baseline_path).GetProjection()
    out_img = ssp585_img - baseline_img
    out_path = r'F:\Fungi Carbon add Competition\\' + 'Fungi-' + carbon_path[i] + '-ssp585-minos-baseline.tif'
    Export_image(out_img, geo, proj, out_path, nodata_value=0)
    baseline_img = None
    ssp585_img = None
    out_img = None
