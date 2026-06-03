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


class GdalTif(object):
    """
    A class to handle GeoTIFF files using GDAL.
    """

    def __init__(self, tif_path):
        self.tif_path = tif_path
        self.dataset = self._read_tif(tif_path)

    @staticmethod
    def _read_tif(tif_path):
        """
        Reads a GDAL geographic data file.
        :param tif_path: Path to the TIF image.
        :return: GDAL dataset object.
        """
        dataset = gdal.Open(tif_path)
        if dataset is None:
            print(f"{tif_path} could not be opened.")
        return dataset

    def get_image_size(self):
        """Gets the size of the image (bands, width, height)."""
        bands = self.dataset.RasterCount
        width = self.dataset.RasterXSize
        height = self.dataset.RasterYSize
        return bands, width, height

    def get_raster(self):
        """Reads the raster data as a NumPy array."""
        return self.dataset.ReadAsArray()

    def get_geo_trans(self):
        """
        Gets the affine transformation matrix.
        :return: A 6-parameter tuple describing the relationship between
                 raster coordinates and geographic coordinates.
        """
        return self.dataset.GetGeoTransform()

    def get_projection(self):
        """Gets the projection information of the data."""
        return self.dataset.GetProjection()

    def get_srs_pair(self):
        """
        Gets the projected and geographic reference systems.
        :return: A tuple of (projected_srs, geographic_srs).
        """
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(self.dataset.GetProjection())
        geosrs = prosrs.CloneGeogCS()
        return prosrs, geosrs

    def imagexy2geo(self, row, col):
        """
        Converts image coordinates (row, col) to geographic coordinates (x, y).
        """
        trans = self.dataset.GetGeoTransform()
        x = trans[0] + col * trans[1] + row * trans[2]
        y = trans[3] + col * trans[4] + row * trans[5]
        return x, y

    def geo2imagexy(self, x, y):
        """
        Converts geographic coordinates (x, y) to image coordinates (row, col).
        """
        trans = self.dataset.GetGeoTransform()
        a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
        b = np.array([x - trans[0], y - trans[3]])
        return np.linalg.solve(a, b)[::-1]

    def geo_to_lonlat(self, x, y):
        """
        Converts projected coordinates to longitude/latitude.
        """
        prosrs, geosrs = self.get_srs_pair()
        ct = osr.CoordinateTransformation(prosrs, geosrs)
        coords = ct.TransformPoint(x, y)
        return coords[:2]

    def lonlat2geo(self, lon, lat):
        """
        Converts longitude/latitude to projected coordinates.
        """
        prosrs, geosrs = self.get_srs_pair()
        ct = osr.CoordinateTransformation(geosrs, prosrs)
        coords = ct.TransformPoint(lon, lat)
        return coords[:2]


fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum',
                 'Hyphodermasetigerum', 'Laetiporusconifericola', 'Lyomycescrustosus', 'Meruliustremellosus',
                 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

GCM_list = ['ACCESS-CM2', 'BCC-CSM2-MR', 'CMCC-ESM2', 'EC-Earth3-Veg', 'FIO-ESM-2-0', 'GISS-E2-1-G', 'HadGEM3-GC31-LL',
            'INM-CM5-0', 'IPSL-CM6A-LR', 'MIROC6', 'MPI-ESM1-2-HR', 'MRI-ESM2-0', 'UKESM1-0-LL']

scenario_lists = ['Baseline', 'SSP245', 'SSP585']

future_scenarios = ['ssp245', 'ssp585']

# parameters of f(T)
a_list = [0.7547, 0.0956, 0.0094, 0.0202, 0.0572, 0.2767, 0.0508, 0.0209, 0.0466, 0.2275, 0.0160, 0.1013, 0.4034,
          0.0373, 51.5350, 0.0321, 0.1993, 0.0652, 0.0234]
b_list = [-0.1675, 0.1237, 0.2008, 0.1401, 0.1201, 0.0742, 0.0821, 0.1200, 0.1068, 0.0956, 0.1595, 0.0996, 0.0554,
          0.0559, -0.1522, 0.1455, 0.0808, 0.1086, 0.1178]


def K_exponential_model(T, a, b):
    """
    f(T)=a*e^bT ->K
    :param T: Tem
    :param a:
    :param b:
    :return:
    """
    return a * np.exp(b * T)


def L_loss_calculation(K):
    """
    L=1-Mt/M0=1-e^(-kt)
    loss=1-L=e^(-kt)
    :param K:
    :return:
    """
    return np.exp((-K))


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


Baseline_b1_path = r'F:\wc2.1_30s_bio\Baseline-b1.tif'
Baseline_b12_path = r'F:\wc2.1_30s_bio\Baseline-b12.tif'

Baseline_MAT_img = gdal.Open(Baseline_b1_path)
temp_band = Baseline_MAT_img.GetRasterBand(1)

Baseline_MAP_img = gdal.Open(Baseline_b12_path)
moisture_band = Baseline_MAP_img.GetRasterBand(1)

# Based SDM
Fungi_baseline = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
Fungi_baseline_img = gdal.Open(Fungi_baseline)
geo = Fungi_baseline_img.GetGeoTransform()
proj = Fungi_baseline_img.GetProjection()
print('geo', geo)
print('proj', proj)

# cal Baseline K rate
for i in range(len(fungi_species)):
    print('species', fungi_species[i])
    # # image of SDM
    # SDM_path = 'F:\\Fungi SDM new\\' + fungi_species[i] + '\\' + fungi_species[i] + '-SDM-Baseline.tif'
    # SDM_img = gdal.Open(SDM_path)
    # SDM_raster = SDM_img.ReadAsArray()

    # parameters of Temperature constrain
    a = a_list[i]
    b = b_list[i]

    # parameters of water constrain
    fw_function_path = 'F:\\Fungi Fw\\' + fungi_species[i] + '_f_W_function.pkl'
    f_W_function = joblib.load(fw_function_path)
    # x_range = np.loadtxt(f"F:\\Fungi Fw\\'{fungi_species[i]}'-x_range.txt")
    # f_W_curve = np.loadtxt(f"F:\\Fungi Fw\\'{fungi_species[i]}'-f_W_curve.txt", )
    # f_W_function = interp1d(
    #     x_range,
    #     f_W_curve,
    #     bounds_error=False,
    #     fill_value=(f_W_curve[0], f_W_curve[-1])
    # )
    # f_W_function_name = os.path.join('F:\\Fungi Fw\\', f'{fungi_species[i]}_f_W_function.pkl')
    # joblib.dump(f_W_function, f_W_function_name)

    fungus_band = Fungi_baseline_img.GetRasterBand(1)

    no_data_fungus = fungus_band.GetNoDataValue()
    no_data_temp = temp_band.GetNoDataValue()
    no_data_moisture = moisture_band.GetNoDataValue()
    # print('no_data_fungus', no_data_fungus)
    # print('no_data_temp', no_data_temp)

    fungus_prob = fungus_band.ReadAsArray()
    temperature = temp_band.ReadAsArray()
    moisture = moisture_band.ReadAsArray()

    temp_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)
    moisture_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)

    valid_mask = np.ones(fungus_prob.shape, dtype=bool)

    if no_data_fungus is not None:
        valid_mask = valid_mask & (fungus_prob != no_data_fungus)

    # if no_data_temp is not None:
    #     valid_mask = valid_mask & (temperature != no_data_temp)
    # if no_data_moisture is not None:
    #     valid_mask = valid_mask & (moisture != no_data_moisture)

    condition_mask = (fungus_prob > 0)

    process_mask = valid_mask & condition_mask

    # Temperature constrain
    T_valid = temperature[process_mask]

    K_valid = K_exponential_model(T_valid, a, b)
    rate_valid = L_loss_calculation(K_valid)

    # temp_ratio[process_mask] = rate_valid
    temp_ratio[process_mask] = rate_valid / 100
    # print('min', np.min(temp_ratio), 'mean', np.mean(temp_ratio), 'max', np.max(temp_ratio))

    # water constrain
    M_valid = moisture[process_mask]
    rate_valid_moisture = f_W_function(M_valid)
    moisture_ratio[process_mask] = rate_valid_moisture
    # print('min', np.min(moisture_ratio), 'mean', np.mean(moisture_ratio), 'max', np.max(moisture_ratio))

    # Decomposition rate
    output_K = np.full(fungus_prob.shape, 0, dtype=np.float32)

    temp_valid = temp_ratio[process_mask]
    moisture_valid = moisture_ratio[process_mask]

    K_valid = temp_valid * moisture_valid

    output_K[process_mask] = K_valid

    out_K_path = r'F:\Fungi Rate K\\' + fungi_species[i] + '-decomposition-rate-Baseline.tif'
    Export_image(output_K, geo, proj, out_K_path, nodata_value=0)

    output_K = None