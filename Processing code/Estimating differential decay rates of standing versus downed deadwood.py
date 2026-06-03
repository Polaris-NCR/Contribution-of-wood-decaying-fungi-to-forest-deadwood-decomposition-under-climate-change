from osgeo import gdal
import numpy as np
import sys


def reclassify_raster(input_filepath, output_filepath):

    dataset = gdal.Open(input_filepath, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"Error: Can not open '{input_filepath}'")
        return

    band = dataset.GetRasterBand(1)

    nodata_value = band.GetNoDataValue()

    print("Reading raster data...")
    data = band.ReadAsArray()

    print("Reclassifying...")
    output_data = data.astype(np.float32)


    condition_1 = np.logical_or(data == 1, data == 9)
    output_data[condition_1] = 0.875

    condition_2 = np.logical_or(data == 2, data == 3)
    output_data[condition_2] = 1.0

    condition_3 = np.logical_or.reduce((
        data == 4,
        data == 5,
        data == 6,
        data == 7,
        data == 8
    ))
    output_data[condition_3] = 0.85

    print(f"Saving to '{output_filepath}'...")

    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    driver = gdal.GetDriverByName("GTiff")

    rows, cols = data.shape
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
    dataset = None

    print("Reclassification completed!")


def reclassify_raster_std(input_filepath, output_filepath):

    dataset = gdal.Open(input_filepath, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"Error: Can not open '{input_filepath}'")
        return

    band = dataset.GetRasterBand(1)

    nodata_value = band.GetNoDataValue()

    print("Reading raster data...")
    data = band.ReadAsArray()

    print("Reclassifying...")
    output_data = data.astype(np.float32)

    condition_1 = np.logical_or(data == 1, data == 9)
    output_data[condition_1] = 0.175

    condition_2 = np.logical_or(data == 2, data == 3)
    output_data[condition_2] = 0

    condition_3 = np.logical_or.reduce((
        data == 4,
        data == 5,
        data == 6,
        data == 7,
        data == 8
    ))
    output_data[condition_3] = 0.15

    print(f"Saving to '{output_filepath}'...")

    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    driver = gdal.GetDriverByName("GTiff")

    rows, cols = data.shape
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
    dataset = None

    print("Reclassification completed!")


if __name__ == "__main__":
    INPUT_RASTER_std = "F:\Fungi data\FAO_ecozones.tif"
    OUTPUT_RASTER_std = "F:\Fungi data\Standing_wood_decay_rate_rectify_std.tif"

    gdal.AllRegister()
    reclassify_raster_std(INPUT_RASTER_std, OUTPUT_RASTER_std)