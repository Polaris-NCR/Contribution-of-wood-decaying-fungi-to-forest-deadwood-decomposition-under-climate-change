import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import rasterio
from rasterio.plot import show
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import os
from glob import glob


plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# pd.set_option('mode.use_inf_as_null', True)
import pandas._config.config as cf
cf._global_config['mode.use_inf_as_null'] = True


def load_and_combine_species_shp(species_list, shp_dir):

    combined_gdf = pd.DataFrame()

    print(f"Loading Shapefiles of {len(species_list)} species...")

    for species_name in species_list:

        found = False
        file_path = os.path.join(shp_dir, f"{species_name}.shp")
        if os.path.exists(file_path):
            try:
                gdf = gpd.read_file(file_path)
                if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
                    gdf = gdf.to_crs("EPSG:4326")

                gdf['Longitude'] = gdf.geometry.x
                gdf['Latitude'] = gdf.geometry.y
                gdf['Species'] = species_name

                df_clean = gdf[['Species', 'Longitude', 'Latitude']].copy()
                combined_gdf = pd.concat([combined_gdf, df_clean], ignore_index=True)
                found = True
                break
            except Exception as e:
                print(f"  Loading error {file_path}: {e}")

        if not found:
            print(f"  Warning: Species {species_name} .shp file not found (in {shp_dir})")

    return combined_gdf


def preprocess_raster(tif_path):
    print(f"Processing: {tif_path}...")
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        profile = src.profile
        transform = src.transform

        reclassified = np.full(data.shape, np.nan, dtype=np.float32)

        # Boreal: 1
        reclassified[data == 1] = 1

        # Temperate: 2, 3
        reclassified[(data == 2) | (data == 3)] = 2

        # Tropical: 4, 5, 6, 7, 8
        tropical_mask = np.isin(data, [4, 5, 6, 7, 8])
        reclassified[tropical_mask] = 3

        extent = [
            transform[2],
            transform[2] + transform[0] * src.width,
            transform[5] + transform[4] * src.height,
            transform[5]
        ]

    return reclassified, extent


def plot_figure1_main(white_species, brown_species, shp_dir, tif_path):
    print("Loading shpfiles")
    white_df = load_and_combine_species_shp(white_species, shp_dir)
    brown_df = load_and_combine_species_shp(brown_species, shp_dir)

    if white_df.empty or brown_df.empty:
        print("Error: Unable to load sufficient fungal point data. Please check paths and filenames.")
        return

    print(f"  Total: White-rot {len(white_df)} points, Brown-rot {len(brown_df)} points")


    raster_data, extent = preprocess_raster(tif_path)

    fig, ax = plt.subplots(figsize=(14, 8))

    colors = ['#d1e5f0', '#e6f5d0', '#fee0b6']  # (Boreal, Temperate, Tropical)
    cmap = ListedColormap(colors)

    im = ax.imshow(raster_data, cmap=cmap, extent=extent, alpha=0.8, zorder=1)

    kde_levels = 8
    kde_thresh = 0.05  


    sns.kdeplot(
        x=brown_df['Longitude'],
        y=brown_df['Latitude'],
        cmap="GnBu", 
        fill=True,
        alpha=0.6, 
        levels=kde_levels,
        thresh=kde_thresh,
        ax=ax,
        zorder=2
    )

    sns.kdeplot(
        x=white_df['Longitude'],
        y=white_df['Latitude'],
        cmap="Blues", 
        fill=True,
        alpha=0.5, 
        levels=kde_levels,
        thresh=kde_thresh,
        ax=ax,
        zorder=3
    )

    ax.set_xlim([-180, 180])
    ax.set_ylim([-60, 90])

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')

    legend_patches_biome = [
        mpatches.Patch(color=colors[0], label='Boreal Forest'),
        mpatches.Patch(color=colors[1], label='Temperate Forest'),
        mpatches.Patch(color=colors[2], label='Tropical Forest')
    ]

    legend_patches_fungi = [
        mpatches.Patch(facecolor=plt.cm.Blues(0.8), edgecolor='none', alpha=0.6,
                       label='White-rot fungi (High density)'),
        mpatches.Patch(facecolor=plt.cm.GnBu(0.8), edgecolor='none', alpha=0.6, label='Brown-rot fungi (High density)')
    ]

    leg1 = ax.legend(handles=legend_patches_biome, loc='lower left',
                     title='Forest Biomes', frameon=False, fontsize=11, title_fontsize=12,
                     bbox_to_anchor=(0.02, 0.05))
    ax.add_artist(leg1)

    leg2 = ax.legend(handles=legend_patches_fungi, loc='lower left',
                     title='Fungal Distribution', frameon=False, fontsize=11, title_fontsize=12,
                     bbox_to_anchor=(0.02, 0.25))  

    sns.despine(left=True, bottom=True, right=True, top=True) 

    output_png = 'Figure1_Global_Distribution.png'
    output_pdf = 'Figure1_Global_Distribution.pdf'
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    white_species = [
        'Fomesfomentarius', 'Fomitiporiahartigii', 'Fuscoporiagilva', 'Hyphodermasetigerum',
        'Lyomycescrustosus', 'Meruliustremellosus', 'Phellinusrobiniae', 'Phlebiopsisflavidoalba',
        'Pleurotusostreatus', 'Porodisculuspendulus', 'Trametessanguinea', 'Trametesversicolor',
        'Tyromyceschioneus', 'Xylobolussubpileatus'
    ]
    brown_species = [
        'Amyloporiaxantha', 'Fomitopsispinicola', 'Gloeophyllumtrabeum', 'Laetiporusconifericola',
        'Rhodoniaplacenta'
    ]

    shp_dir = r"F:\Fungi data\Fungi shp"

    tif_path = r"F:\Fungi data\FAO_ecozones_expanded-resample.tif"

    if not os.path.exists(shp_dir):
        print(f"Error: Shpfile does not exist {shp_dir}")

    if not os.path.exists(tif_path):
        print(f"Error: TIF file does not exist: {tif_path}")
    else:
        plot_figure1_main(white_species, brown_species, shp_dir, tif_path)