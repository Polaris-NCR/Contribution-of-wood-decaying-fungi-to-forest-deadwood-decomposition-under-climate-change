import matplotlib.pyplot as plt
import rasterio
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap, BoundaryNorm
from osgeo import gdal, osr


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
        x = trans + col * trans[1] + row * trans[2]
        y = trans[3] + col * trans[4] + row * trans[5]
        return x, y

    def geo2imagexy(self, x, y):
        """
        Converts geographic coordinates (x, y) to image coordinates (row, col).
        """
        trans = self.dataset.GetGeoTransform()
        a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
        b = np.array([x - trans, y - trans[3]])
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

def calculate_valid_mean(raster_array):
    masked_array = np.ma.masked_less_equal(raster_array, 0)

    mean_values = np.ma.mean(masked_array, axis=1)

    return mean_values.filled(0)


baseline_path = r'F:\Fungi SDM new\Aggregate\Aggregate-SDM-Baseline.tif'
ssp245_path = r'F:\Fungi SDM new\Aggregate\Aggregate-SDM-SSP245.tif'
ssp585_path = r'F:\Fungi SDM new\Aggregate\Aggregate-SDM-SSP585.tif'

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

plt.rcParams['font.sans-serif'] = ['Arial']  # 使用 Arial 字体
plt.rcParams['axes.unicode_minus'] = False
font = fm.FontProperties(family='Arial', size=16)
plt.plot(average_richness_baseline, lats, color='#F1B656', linewidth=1, label='Baseline')
plt.plot(average_richness_ssp245, lats, color='#397FC7', linewidth=1, label='SSP245')
plt.plot(average_richness_ssp585, lats, color='#040676', linewidth=1, label='SSP585')
# plt.title('Average Fungal Richness by Latitude', fontproperties=font, pad=20)
# plt.xlabel('Carbon Emission (Pg C)', fontproperties=font)
plt.xticks(fontname='Arial', fontsize=16)
plt.yticks(fontname='Arial', fontsize=16)
plt.ylabel('Latitude (°)', fontproperties=font)

# plt.grid(linestyle='--', alpha=0.7)
ax=plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(top=False, right=False)

# 限制 x 轴范围，使其更具可读性
# plt.xlim(0, 10)
max_val = np.nanmax(average_richness_ssp585) if not np.all(np.isnan(average_richness_ssp585)) else 1
plt.xlim(0, max_val + 1)
plt.ylim([-60, 80])  # 设置与地图相同的纬度范围
# plt.legend(prop={'size': 20, 'family': 'Arial'})
legend = plt.legend(fontsize=16)
legend.set_frame_on(False)
plt.tight_layout()
# plt.savefig('..\Figure\Figure 2 panel c 20251118.png', dpi=300)
# plt.savefig('..\Figure\Figure 2 panel c 20251122.png', dpi=300)
# plt.savefig('..\Figure\Figure 2 panel c 20251130.png', dpi=300)
plt.show()