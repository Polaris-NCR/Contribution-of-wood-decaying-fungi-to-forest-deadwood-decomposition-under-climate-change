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
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum','Hyphodermasetigerum', 'Laetiporusconifericola',
                 'Lyomycescrustosus', 'Meruliustremellosus','Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

# parameters of f(T)
a_list = [0.7547, 0.0956, 0.0094, 0.0202, 0.0572, 0.2767, 0.0508, 0.0209, 0.0466, 0.2275, 0.0160, 0.1013, 0.4034,
          0.0373, 51.5350, 0.0321, 0.1993, 0.0652, 0.0234]
b_list = [-0.1675, 0.1237, 0.2008, 0.1401, 0.1201, 0.0742, 0.0821, 0.1200, 0.1068, 0.0956, 0.1595, 0.0996, 0.0554,
          0.0559, -0.1522, 0.1455, 0.0808, 0.1086, 0.1178]
pcov_list = [[[0.14556392, -0.01168668],
              [-0.01168668, 0.00100374]],
             [[0.00287872, - 0.00238866],
              [-0.00238866, 0.00217883]],
             [[2.32549678e-05, -2.20881636e-04],
              [-2.20881636e-04, 2.20751111e-03]],
             [[7.28644054e-05, -1.45980127e-04],
              [-1.45980127e-04, 2.94530272e-04]],
             [[0.00112006, -0.00079466],
              [-0.00079466, 0.00059425]],
             [[0.03139977, -0.00461525],
              [-0.00461525, 0.00067917]],
             [[0.00097217, -0.00121827],
              [-0.00121827, 0.00155461]],
             [[0.000213, -0.00099145],
              [-0.00099145, 0.00468166]],
             [[0.00065958, -0.00094849],
              [-0.00094849, 0.00156307]],
             [[0.00279653, -0.00083907],
              [-0.00083907, 0.00028435]],
             [[3.56823379e-05, -1.23661705e-04],
              [-1.23661705e-04, 4.63343742e-04]],
             [[0.00257383, -0.0018363],
              [-0.0018363, 0.00147361]],
             [[0.02170272, -0.00205216],
              [-0.00205216, 0.00019528]],
             [[0.00027007, -0.00036534],
              [-0.00036534, 0.00051929]],
             [[3.93741937e+02, -2.97017741e-01],
              [-2.97017741e-01, 2.30304537e-04]],
             [[7.89632819e-05, -1.48903598e-04],
              [-1.48903598e-04, 3.40904880e-04]],
             [[0.00313619, -0.00062106],
              [-0.00062106, 0.00012414]],
             [[0.00064928, -0.00045118],
              [-0.00045118, 0.00034659]],
             [[0.00091848, -0.00222401],
              [-0.00222401, 0.00598555]],
             ]
pcov_list = np.array(pcov_list)
print(pcov_list.shape)


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
fungus_band = Fungi_baseline_img.GetRasterBand(1)
fungus_prob = fungus_band.ReadAsArray()
condition_mask = (fungus_prob > 0) & (fungus_prob != 0)

temperature = temp_band.ReadAsArray()
moisture = moisture_band.ReadAsArray()

valid_mask = np.ones(fungus_prob.shape, dtype=bool)
process_mask = valid_mask & condition_mask
condition_mask = None
valid_mask = None

# cal Baseline K rate
for i in range(len(fungi_species)):
    print('species', fungi_species[i])

    N = 100

    # parameters of Temperature constrain
    a0 = a_list[i]
    b0 = b_list[i]
    mean_params = np.array([a0, b0])
    param_samples = np.random.multivariate_normal(mean_params, pcov_list[i], size=N)
    a_samples = param_samples[:, 0]
    b_samples = param_samples[:, 1]

    # output_K_list = []

    sum_raster = np.zeros(fungus_prob.shape, dtype=np.float64)
    sum_sq_raster = np.zeros(fungus_prob.shape, dtype=np.float64)

    for j in range(N):
        a = a_samples[j]
        b = b_samples[j]

        x_range = np.loadtxt(f"F:\\Fungi Fw\\'{fungi_species[i]}'-x_range-{j + 1}.txt")
        f_W_curve = np.loadtxt(f"F:\\Fungi Fw\\'{fungi_species[i]}'-f_W_curve-{j + 1}.txt", )
        f_W_function = interp1d(
            x_range,
            f_W_curve,
            bounds_error=False,
            fill_value=(f_W_curve[0], f_W_curve[-1])
        )
        f_W_function_name = os.path.join('F:\\Fungi Fw\\', f'{fungi_species[i]}_f_W_function-{j + 1}.pkl')
        joblib.dump(f_W_function, f_W_function_name)

        temp_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)
        moisture_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)

        # Temperature constrain
        T_valid = temperature[process_mask]

        K_valid = K_exponential_model(T_valid, a, b)

        if np.isinf(K_valid).any():
            print(f"Warning: INF detected in Temperature Model at loop {j}")
            K_valid[np.isinf(K_valid)] = np.nan

        rate_valid = L_loss_calculation(K_valid)

        temp_ratio[process_mask] = rate_valid / 100

        # water constrain
        M_valid = moisture[process_mask]
        rate_valid_moisture = f_W_function(M_valid)
        moisture_ratio[process_mask] = rate_valid_moisture

        # Decomposition rate
        output_K_0 = np.full(fungus_prob.shape, 0, dtype=np.float32)

        temp_valid = temp_ratio[process_mask]
        moisture_valid = moisture_ratio[process_mask]

        K_valid = temp_valid * moisture_valid
        output_K_0[process_mask] = K_valid

        invalid_locs = ~np.isfinite(output_K_0)
        if np.any(invalid_locs):
            output_K_0[invalid_locs] = 0

        K_valid = None
        T_valid = None
        moisture_ratio = None
        temp_ratio = None
        temp_valid = None
        moisture_valid = None
        M_valid = None
        rate_valid_moisture = None
        rate_valid = None

        # output_K_list.append(output_K_0)
        sum_raster += output_K_0
        np.square(output_K_0.astype(np.float64), out=output_K_0.astype(np.float64))
        sum_sq_raster += np.square(output_K_0)

        output_K_0 = None

    mean_raster = sum_raster / N
    # (Sum(X^2)/N)
    mean_sq_raster = sum_sq_raster / N

    sum_raster = None
    sum_sq_raster = None

    # Var = (Sum(X^2)/N) - (Sum(X)/N)^2
    variance = mean_sq_raster - np.square(mean_raster)

    mean_raster = None
    mean_sq_raster = None

    variance[variance < 0] = 0

    output_K_std = np.sqrt(variance)
    output_K_std = output_K_std.astype(np.float32)

    plt.imshow(output_K_std)
    plt.show()

    out_K_std_path = r'F:\Fungi Rate K\\' + fungi_species[i] + '-decomposition-rate-std-Baseline.tif'
    Export_image(output_K_std, geo, proj, out_K_std_path, nodata_value=0)

    output_K_std = None
    variance = None