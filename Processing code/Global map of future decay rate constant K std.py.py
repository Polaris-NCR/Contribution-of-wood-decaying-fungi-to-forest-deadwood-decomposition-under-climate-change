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



fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum',
                 'Hyphodermasetigerum', 'Laetiporusconifericola', 'Lyomycescrustosus', 'Meruliustremellosus',
                 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

# GCM_list = ['ACCESS-CM2', 'BCC-CSM2-MR', 'CMCC-ESM2', 'EC-Earth3-Veg', 'FIO-ESM-2-0', 'GISS-E2-1-G',
#   'HadGEM3-GC31-LL', 'INM-CM5-0', 'IPSL-CM6A-LR', 'MIROC6', 'MPI-ESM1-2-HR', 'MRI-ESM2-0', 'UKESM1-0-LL']
GCM_list = ['ACCESS-CM2', 'CMCC-ESM2', 'EC-Earth3-Veg', 'FIO-ESM-2-0', 'GISS-E2-1-G', 'HadGEM3-GC31-LL',
            'INM-CM5-0', 'IPSL-CM6A-LR', 'MIROC6', 'MPI-ESM1-2-HR', 'MRI-ESM2-0', 'UKESM1-0-LL']

future_scenarios = ['ssp245', 'ssp585']

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

# Based SDM
Fungi_baseline = r'F:\Fungi SDM new\Amyloporiaxantha\Amyloporiaxantha-SDM-Baseline.tif'
Fungi_baseline_img = gdal.Open(Fungi_baseline)
geo = Fungi_baseline_img.GetGeoTransform()
proj = Fungi_baseline_img.GetProjection()
print('geo', geo)
print('proj', proj)

fungus_band = Fungi_baseline_img.GetRasterBand(1)
no_data_fungus = fungus_band.GetNoDataValue()
fungus_prob = fungus_band.ReadAsArray()
print('no_data_fungus', no_data_fungus)
process_mask = (fungus_prob > 0)

fungus_band = None

# cal future K rate std
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

    for j in range(len(future_scenarios)):
        print('scenario', future_scenarios[j])

        sum_raster = np.zeros(fungus_prob.shape, dtype=np.float64)
        sum_sq_raster = np.zeros(fungus_prob.shape, dtype=np.float64)

        for m in range(N):
            print('interaction', m + 1)
            a = a_samples[m]
            b = b_samples[m]
            fw_function_path = 'F:\\Fungi Fw\\' + fungi_species[i] + '_f_W_function-' + str(m + 1) + '.pkl'
            f_W_function = joblib.load(fw_function_path)

            sum_K_array = np.full(fungus_prob.shape, 0.0, dtype=np.float32)

            for k in range(len(GCM_list)):
                temp_path = 'F:\\WorldClim Future Bio\\' + GCM_list[k] + '-b1-' + future_scenarios[j] + '.tif'
                moist_path = 'F:\\WorldClim Future Bio\\' + GCM_list[k] + '-b12-' + future_scenarios[j] + '.tif'

                temp_ds = gdal.Open(temp_path)
                temp_array = temp_ds.ReadAsArray()

                temp_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)
                T_valid = temp_array[process_mask]
                K_valid = K_exponential_model(T_valid, a, b)
                rate_valid = L_loss_calculation(K_valid)
                temp_ratio[process_mask] = rate_valid / 100
                temp_valid = temp_ratio[process_mask]

                temp_ds = None
                temp_array = None
                T_valid = None
                K_valid = None
                rate_valid = None
                temp_ratio = None

                moist_ds = gdal.Open(moist_path)
                moist_array = moist_ds.ReadAsArray()

                moisture_ratio = np.full(fungus_prob.shape, 0, dtype=np.float32)
                M_valid = moist_array[process_mask]
                rate_valid_moisture = f_W_function(M_valid)
                moisture_ratio[process_mask] = rate_valid_moisture
                moisture_valid = moisture_ratio[process_mask]

                moist_ds = None
                M_valid = None
                rate_valid_moisture = None
                moisture_ratio = None

                output_K_gcm = np.full(fungus_prob.shape, 0, dtype=np.float32)

                K_gcm_valid = temp_valid * moisture_valid

                output_K_gcm[process_mask] = K_gcm_valid

                sum_K_array[process_mask] += output_K_gcm[process_mask]

                temp_valid = None
                moisture_valid = None
                K_gcm_valid = None
                output_K_gcm = None

            output_K_0 = np.full(fungus_prob.shape, 0, dtype=np.float32)

            output_K_0[process_mask] = sum_K_array[process_mask] / len(GCM_list)

            sum_K_array = None

            sum_raster += output_K_0
            np.square(output_K_0.astype(np.float64), out=output_K_0.astype(np.float64))
            sum_sq_raster += np.square(output_K_0)

            output_K_0 = None

        mean_raster = sum_raster / N
        # (Sum(X^2)/N)
        mean_sq_raster = sum_sq_raster / N

        sum_raster = None
        sum_sq_raster = None

        variance = mean_sq_raster - np.square(mean_raster)

        mean_raster = None
        mean_sq_raster = None

        variance[variance < 0] = 0

        output_K_std = np.sqrt(variance)
        output_K_std = output_K_std.astype(np.float32)

        out_K_path = r'F:\Fungi Rate K\\' + fungi_species[i] + '-decomposition-rate-std-' + future_scenarios[j] + '.tif'
        Export_image(output_K_std, geo, proj, out_K_path, nodata_value=0)

        variance = None
        output_K_std = None