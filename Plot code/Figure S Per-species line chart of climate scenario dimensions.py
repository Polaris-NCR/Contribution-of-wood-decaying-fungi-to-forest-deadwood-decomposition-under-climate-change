import matplotlib.pyplot as plt
import rasterio
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap, BoundaryNorm
from osgeo import gdal, osr

fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum', 'Hyphodermasetigerum', 'Laetiporusconifericola',
                 'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

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


CWD_path = 'F:\\Fungi data\\Deadwood.tif'
cwd_raster = gdal.Open(CWD_path).ReadAsArray()


def cal_plot_X_Y(probability_map_path, uncertainty_map_path):
    img1 = GdalTif(probability_map_path)
    raster1 = img1.get_raster()

    Y_list1 = []
    X_mean_list1 = []
    for i in range(raster1.shape[0]):
        lat, long = img1.imagexy2geo(i, 0)
        Y_list1.append(long)
        X = raster1[i, :]
        X = np.array(X)
        X0 = cwd_raster[i, :]
        # X = X[np.where(X > 0.0)]
        X = X[np.where(X0 > 0.0)]
        mean = np.mean(X)
        X_mean_list1.append(mean)

    raster1 = None

    img2 = GdalTif(uncertainty_map_path)
    raster2 = img2.get_raster()

    Y_list2 = []
    X_mean_list2 = []

    for i in range(raster2.shape[0]):
        lat, long = img2.imagexy2geo(i, 0)
        Y_list2.append(long)
        X2 = raster2[i, :]
        X20 = cwd_raster[i, :]
        X2 = np.array(X2)
        X2 = X2[np.where(X20 > 0.0)]
        mean2 = np.mean(X2)
        X_mean_list2.append(mean2)

    raster2 = None

    X_mean_list1 = np.array(X_mean_list1)
    X_mean_list2 = np.array(X_mean_list2)
    return Y_list1, X_mean_list1, X_mean_list2


def draw(fungi_type, base_folder='F:\\Fungi SDM new\\', save_folder=None):
    total_baseline_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-Baseline.tif'
    total_baseline_std_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-std-Baseline.tif'
    Y_baseline, X1_baseline, X2_baseline = cal_plot_X_Y(total_baseline_path, total_baseline_std_path)

    total_ssp245_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-SSP245.tif'
    total_ssp245_std_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-std-SSP245.tif'
    Y_ssp245, X1_ssp245, X2_ssp245 = cal_plot_X_Y(total_ssp245_path, total_ssp245_std_path)

    total_ssp585_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-SSP585.tif'
    total_ssp585_std_path = base_folder + fungi_type + '\\' + fungi_type + '-SDM-std-SSP585.tif'
    Y_ssp585, X1_ssp585, X2_ssp585 = cal_plot_X_Y(total_ssp585_path, total_ssp585_std_path)


    font = fm.FontProperties(family='Arial', size=16)
    plt.rcParams['xtick.labelsize'] = 20
    plt.rcParams['ytick.labelsize'] = 20
    plt.plot(X1_baseline, Y_baseline, color='#ACC5F0', linewidth=1, label='Baseline')
    plt.fill_betweenx(
        Y_baseline,
        X1_baseline - X2_baseline,
        X1_baseline + X2_baseline,
        color='#ACC5F0',
        alpha=0.3,
    )

    plt.plot(X1_ssp245, Y_ssp245, color='#69AFED', linewidth=1, label='SSP245')
    plt.fill_betweenx(
        Y_ssp245,
        X1_ssp245 - X2_ssp245,
        X1_ssp245 + X2_ssp245,
        color='#69AFED',
        alpha=0.3,
    )

    plt.plot(X1_ssp585, Y_ssp585, color='#1664EE', linewidth=1, label='SSP585')
    plt.fill_betweenx(
        Y_ssp585,
        X1_ssp585 - X2_ssp585,
        X1_ssp585 + X2_ssp585,
        color='#1664EE',
        alpha=0.3,
    )

    # plt.plot(average_richness_ssp245, lats, color='#397FC7', linewidth=1, label='SSP245')
    # plt.plot(average_richness_ssp585, lats, color='#040676', linewidth=1, label='SSP585')
    # plt.title('Average Fungal Richness by Latitude', fontproperties=font, pad=20)
    # plt.xlabel('Average distribution probability', fontproperties=font)
    # plt.ylabel('Latitude (°)', fontproperties=font)
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()
    if save_folder is not None:
        outpath = save_folder + fungi_type + '-fungi-SDM-scenario-statistic.png'
        plt.savefig(outpath, dpi=300)
    plt.show()
    plt.close()


for i in range(len(fungi_species)):
    draw(fungi_species[i], save_folder='../Figure/')