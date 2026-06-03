import glob
import os
import arcpy

clip_vector = r"E:\land.shp"
resample_resolution = 0.00833333333333
resample_method = "BILINEAR"
raster_pixel_type = "64_BIT"
sr = arcpy.Describe("F:\wc2.1_30s_bio\wc2.1_30s_bio_1.tif").spatialReference

fungi_species = ['Amyloporiaxantha', 'Fomesfomentarius', 'Fomitiporiahartigii', 'Fomitopsispinicola',
                 'Fuscoporiagilva', 'Gloeophyllumtrabeum',
                 'Hyphodermasetigerum', 'Laetiporusconifericola', 'Lyomycescrustosus', 'Meruliustremellosus',
                 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
                 'Pleurotusostreatus', 'Porodisculuspendulus', 'Rhodoniaplacenta', 'Trametessanguinea',
                 'Trametesversicolor', 'Tyromyceschioneus', 'Xylobolussubpileatus']

scenarios = ["Baseline", "SSP245", "SSP585"]
out_type = ["-", "-std-"]

# SDM
for i in range(len(fungi_species)):
    input_folder = r"F:\\Fungi SDM new\\" + fungi_species[i]
    workspace = r"F:\\Fungi SDM new\\" + fungi_species[i]
    print(fungi_species[i], workspace)

    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = workspace

    for j in range(len(scenarios)):
        for k in range(len(out_type)):
            image_list = glob.glob(
                os.path.join(workspace, fungi_species[i] + "-SDM" + out_type[k] + scenarios[j] + "-0000000000*.tif"))

            ras_list = ";".join(image_list)
            print(ras_list)

            mosaic_name = fungi_species[i] + "-SDM" + out_type[k] + scenarios[j] + "-merge.tif"
            mosaic_path = os.path.join(input_folder, mosaic_name)
            print('mosaic_path', mosaic_path)
            resample_path = input_folder + "\\" + fungi_species[i] + "-SDM" + out_type[k] + scenarios[
                j] + "-resample.tif"
            clip_path = input_folder + "\\" + fungi_species[i] + "-SDM" + out_type[k] + scenarios[j] + ".tif"
            print(clip_path)

            print('image merge')

            arcpy.MosaicToNewRaster_management(
                ras_list,  # input_rasters
                input_folder,  # output_location
                mosaic_name,  # raster_dataset_name_with_extension
                sr,  # coordinate_system_for_raster
                raster_pixel_type,  # pixel_type
                None,  # cellsize
                1,  # number_of_bands
                "LAST",
                "FIRST"
            )
            print('image resample')

            arcpy.Resample_management(
                mosaic_path,  # in_raster
                resample_path,  # out_raster
                resample_resolution,  # cell_size
                resample_method  # resampling_type
            )

            print("image clip")
            arcpy.Clip_management(
                resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
                clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
            print('finish')

out_type2 = ["", "-uncertainty"]

input_folder = r"F:\\AGB carbon\\"
workspace = r"F:\\AGB carbon\\"

arcpy.env.overwriteOutput = True
arcpy.env.workspace = workspace

for j in range(len(out_type2)):
    image_list = glob.glob(os.path.join(workspace, "NASA-AGBC" + out_type2[j] + "-0000000000*.tif"))
    print(image_list)
    # ras_list = [image1_path, image2_path]
    ras_list = ";".join(image_list)
    print(ras_list)

    mosaic_name = "NASA-AGBC" + out_type2[j] + "-merge.tif"
    mosaic_path = os.path.join(input_folder, mosaic_name)
    print('mosaic_path', mosaic_path)
    resample_path = "NASA-AGBC" + out_type2[j] + "-resample.tif"
    print('resample path', resample_path)
    clip_path = "NASA-AGBC" + out_type2[j] + ".tif"
    print('clip path', clip_path)

    print('image merge')

    arcpy.MosaicToNewRaster_management(
        ras_list,  # input_rasters
        input_folder,  # output_location
        mosaic_name,  # raster_dataset_name_with_extension
        sr,  # coordinate_system_for_raster
        raster_pixel_type,  # pixel_type
        None,  # cellsize
        1,  # number_of_bands
        "LAST",
        "FIRST"
    )
    print('image resample')

    arcpy.Resample_management(
        mosaic_path,  # in_raster
        resample_path,  # out_raster
        resample_resolution,  # cell_size
        resample_method  # resampling_type
    )

    print("image clip")
    arcpy.Clip_management(
        resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
        clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
    print('finish')

input_folder = r"F:\\AGB carbon\\"
workspace = r"F:\\AGB carbon\\"

arcpy.env.overwriteOutput = True
arcpy.env.workspace = workspace

image_list = ["F:\AGB carbon\FAO_ecozones_expanded.tif", "F:\AGB carbon\Pan_deadwood_frac_modified.tif"]
input_folder = r"F:\\AGB carbon\\"
workspace = r"F:\\AGB carbon\\"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = workspace

mosaic_path = "F:\AGB carbon\FAO_ecozones_expanded.tif"
resample_path = "F:\AGB carbon\FAO_ecozones_expanded-resample.tif"
print('resample path', resample_path)
clip_path = "F:\AGB carbon\FAO_ecozones.tif"
print('clip path', clip_path)
arcpy.Resample_management(
    mosaic_path,  # in_raster
    resample_path,  # out_raster
    resample_resolution,  # cell_size
    resample_method  # resampling_type
)
print("image clip")
arcpy.Clip_management(
    resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
    clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
print('finish')

mosaic_path = "F:\AGB carbon\Pan_deadwood_frac_modified.tif"
resample_path = "F:\AGB carbon\Seibold_deadwood_frac-resample.tif"
print('resample path', resample_path)
clip_path = "F:\AGB carbon\Seibold_deadwood_frac.tif"
print('clip path', clip_path)
arcpy.Resample_management(
    mosaic_path,  # in_raster
    resample_path,  # out_raster
    resample_resolution,  # cell_size
    resample_method  # resampling_type
)
print("image clip")
arcpy.Clip_management(
    resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
    clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
print('finish')

mosaic_path = "F:\AGB carbon\Seibold_deadwood_2cm_tha.tif"
resample_path = "F:\AGB carbon\Seibold_deadwood_2cm_tha-resample.tif"
print('resample path', resample_path)
clip_path = "F:\AGB carbon\Seibold_deadwood_2cm.tif"
print('clip path', clip_path)
arcpy.Resample_management(
    mosaic_path,  # in_raster
    resample_path,  # out_raster
    resample_resolution,  # cell_size
    resample_method  # resampling_type
)
print("image clip")
arcpy.Clip_management(
    resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
    clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
print('finish')

# WorldClim Bio1 & Bio12
GCM_list = ['ACCESS-CM2', 'BCC-CSM2-MR', 'CMCC-ESM2', 'EC-Earth3-Veg', 'FIO-ESM-2-0', 'GISS-E2-1-G', 'HadGEM3-GC31-LL',
            'INM-CM5-0', 'IPSL-CM6A-LR', 'MIROC6', 'MPI-ESM1-2-HR', 'MRI-ESM2-0', 'UKESM1-0-LL']
scenario_list = ['ssp245', 'ssp585']
band_list = [1, 12]
for i in range(len(GCM_list)):
    for j in range(len(scenario_list)):
        for k in range(len(band_list)):
            mosaic_path = 'F:\\WorldClim Future Bio\\' + GCM_list[i] + '-b' + str(band_list[k]) + '-' + scenario_list[
                j] + '-2081-2100.tif'
            print(mosaic_path)
            resample_path = 'F:\\WorldClim Future Bio\\' + GCM_list[i] + '-b' + str(band_list[k]) + '-' + scenario_list[
                j] + '-2081-2100-resample.tif'
            # print('resample path', resample_path)
            clip_path = 'F:\\WorldClim Future Bio\\' + GCM_list[i] + '-b' + str(band_list[k]) + '-' + scenario_list[
                j] + '.tif'

            print('image resample')
            arcpy.Resample_management(
                mosaic_path,  # in_raster
                resample_path,  # out_raster
                resample_resolution,  # cell_size
                resample_method  # resampling_type
            )
            print("image clip")
            arcpy.Clip_management(
                resample_path, "-180 -55.902230032401 180.000000335276 83.6236001622701",
                clip_path, "#", "0", "NONE", "MAINTAIN_EXTENT")
            print('finish')