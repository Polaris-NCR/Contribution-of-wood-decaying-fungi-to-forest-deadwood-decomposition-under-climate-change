import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Point
import pandas as pd
import time
from pygbif import species, occurrences
import requests
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# from matplotlib_scalebar.scalebar import ScaleBar


def get_gbif_occurrences(taxon_name, limit=1000000, request_timeout=10, total_timeout=30, output_shp=None):

    start_time = time.time()
    try:

        try:
            backbone = species.name_backbone(
                name=taxon_name,
                rank='species',
                kingdom='Fungi',
                timeout=request_timeout
            )
        except requests.exceptions.Timeout:
            return pd.DataFrame(), None

        # 总时间检查点
        if time.time() - start_time > total_timeout:
            return pd.DataFrame(), None

        if 'usageKey' not in backbone:
            return pd.DataFrame(), None

        taxon_key = backbone['usageKey']
        all_results = []
        offset = 0
        end_of_records = False

        while not end_of_records:
            if time.time() - start_time > total_timeout:
                break

            try:
                data = occurrences.search(
                    taxonKey=taxon_key,
                    limit=limit,
                    hasCoordinate=True,
                    offset=offset,
                    timeout=request_timeout
                )
            except requests.exceptions.Timeout:
                break
            except Exception as e:
                break

            # 处理结果
            if 'results' in data:
                all_results.extend(data['results'])
            end_of_records = data.get('endOfRecords', True)
            offset = data.get('offset', 0) + data.get('limit', 0)

            time.sleep(1)

        if len(all_results) == 0:
            return pd.DataFrame(), None

        df = pd.DataFrame(all_results)

        required_columns = ['decimalLongitude', 'decimalLatitude']
        if not all(col in df.columns for col in required_columns):
            return pd.DataFrame(), None


        keep_columns = [
            'species', 'decimalLongitude', 'decimalLatitude',
            'country', 'locality', 'eventDate', 'elevation',
            'kingdom', 'family', 'genus'
        ]
        df1 = df[[c for c in keep_columns if c in df.columns]]

        geometry = [
            Point(lon, lat)
            for lon, lat in zip(df1['decimalLongitude'], df1['decimalLatitude'])
        ]

        gdf = gpd.GeoDataFrame(df1, geometry=geometry, crs="EPSG:4326")

        return df, gdf 

    except Exception as e:
        return pd.DataFrame(), None


fungi_xls = pd.read_excel('Fungi Name.xls')
fungi_values = fungi_xls.values
print(fungi_values.shape)
for i in range(fungi_values.shape[0]):
    fungi_species = [fungi_values[i][1]]
    for species_name in fungi_species:
        print(f"Obtaining: {species_name}")
        species_data, gdf = get_gbif_occurrences(species_name, request_timeout=30, total_timeout=1200)

        if not species_data.empty and gdf is not None:
            save_path = 'results/' + str(species_name) + '.csv'

            species_data.to_csv(save_path, index=False)
            # gdf.to_file(
            #     shp_path,
            #     encoding='utf-8',  
            #     driver='ESRI Shapefile'
            # )
            #
            # fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={'projection': ccrs.PlateCarree()})
            # # fig = plt.figure(figsize=(12, 8))
            # # ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
            # ax.set_xlim([-180, 180])
            # ax.set_ylim([-60, 90])
            # ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())
            # # ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
            # ax.set_yticks([-60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
            # ax.coastlines()
            # gdf.plot(ax=ax, edgecolor='black', facecolor='green', linewidth=0.2, transform=ccrs.PlateCarree())
            #
            # plt.title(fungi_values[i][1])
            # fig_name = 'fig/' + str(fungi_values[i][1]) + '.png'
            # plt.savefig(fig_name, dpi=300)
            # # plt.show()
            # plt.close()

        time.sleep(1)  # API请求间隔
