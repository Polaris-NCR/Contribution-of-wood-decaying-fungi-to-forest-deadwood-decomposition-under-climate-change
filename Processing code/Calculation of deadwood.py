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


# # Based SDM
# Fungi_baseline = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
# Fungi_baseline_img = gdal.Open(Fungi_baseline)
# geo = Fungi_baseline_img.GetGeoTransform()
# proj = Fungi_baseline_img.GetProjection()
# # print('geo', geo)
# # print('proj', proj)
# fungus_prob = Fungi_baseline_img.ReadAsArray()
# process_mask = (fungus_prob > 0)

# CWD = AGBC * Frac * 1.21104
AGBC_path = r'F:\Fungi data\NASA-AGBC.tif'
AGBC_img = gdal.Open(AGBC_path)
AGBC_raster = AGBC_img.ReadAsArray()
print('AGBC_raster', AGBC_raster.shape)

AGBC_std_path = r'F:\Fungi data\NASA-AGBC-uncertainty.tif'
AGBC_std_img = gdal.Open(AGBC_std_path)
AGBC_std_raster = AGBC_std_img.ReadAsArray()
print('AGBC_std_raster', AGBC_std_raster.shape)

CWD_path = r'F:\Fungi data\DeadWood-2cm-clip.tif'
CWD_img = gdal.Open(CWD_path)
CWD_raster = CWD_img.ReadAsArray()
print('CWD_std_raster', CWD_raster.shape)

# Frac uncertainty ±15%
wood_frac_path = r'F:\Fungi data\Seibold_deadwood_frac.tif'
wood_frac_img = gdal.Open(wood_frac_path)
wood_frac_raster = wood_frac_img.ReadAsArray()
print('wood_frac_raster', wood_frac_raster.shape)
geo = wood_frac_img.GetGeoTransform()
proj = wood_frac_img.GetProjection()
print('geo', geo)
print('proj', proj)

wood_frac_raster_std = wood_frac_raster * 0.15

# σCWD = CWD * sqrt((σAGBC/AGBC)**2+(σfrac/frac)**2)
# (σAGBC / AGBC)^2
rel_unc_AGBC_sq = np.where(AGBC_raster > 0, (AGBC_std_raster / AGBC_raster) ** 2, 0)

# (σfrac / frac)^2
rel_unc_frac_sq = np.where(wood_frac_raster > 0, (wood_frac_raster_std / wood_frac_raster) ** 2, 0)

total_rel_unc_sq = rel_unc_AGBC_sq + rel_unc_frac_sq

# σ_C = C * sqrt( (σ_C/C)^2 )
CWD_uncertainty = CWD_raster * np.sqrt(total_rel_unc_sq)

out_path = r'F:\Fungi data\DeadWood-2cm-std.tif'

Export_image(CWD_uncertainty, geo, proj, out_path, nodata_value=0)