import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from rasterstats import zonal_stats
import matplotlib.pyplot as plt


THERMAL_BAND_PATH = "data/LC09_L2SP_201024_20260814_20260815_02_T1_ST_B10.TIF"  
BOROUGH_SHAPEFILE_PATH = "data/London_Borough_Excluding_MHW.shp"
OUTPUT_LST_PATH = "outputs/london_lst_celsius.tif"
OUTPUT_MAP_PATH = "outputs/london_uhi_map.png"

SCALE_FACTOR = 0.00341802
ADD_OFFSET = 149.0


def convert_to_lst_celsius(thermal_band_path, output_path):
    with rasterio.open(thermal_band_path) as src:
        raw = src.read(1).astype(np.float64)
        profile = src.profile

       
        nodata_mask = raw == 0

        kelvin = raw * SCALE_FACTOR + ADD_OFFSET
        celsius = kelvin - 273.15
        celsius[nodata_mask] = np.nan

        profile.update(dtype=rasterio.float32, nodata=np.nan)

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(celsius.astype(np.float32), 1)

    print(f"LST raster written to {output_path}")
    print(f"Min: {np.nanmin(celsius):.1f}°C  Max: {np.nanmax(celsius):.1f}°C  "
          f"Mean: {np.nanmean(celsius):.1f}°C")
    return celsius, profile


def compute_borough_stats(lst_raster_path, borough_shapefile_path):
    boroughs = gpd.read_file(borough_shapefile_path)

    with rasterio.open(lst_raster_path) as src:
        raster_crs = src.crs
    if boroughs.crs != raster_crs:
        boroughs = boroughs.to_crs(raster_crs)

    stats = zonal_stats(
        boroughs,
        lst_raster_path,
        stats=["mean", "min", "max", "std"],
        nodata=np.nan,
        geojson_out=False,
    )

    boroughs["lst_mean"] = [s["mean"] for s in stats]
    boroughs["lst_min"] = [s["min"] for s in stats]
    boroughs["lst_max"] = [s["max"] for s in stats]
    boroughs["lst_std"] = [s["std"] for s in stats]

    ranked = boroughs.sort_values("lst_mean", ascending=False)
    name_col = "NAME" if "NAME" in boroughs.columns else boroughs.columns[0]

    print("\nBoroughs ranked by average surface temperature (hottest first):")
    print(ranked[[name_col, "lst_mean"]].to_string(index=False))

    return boroughs



def plot_borough_heat_map(boroughs_gdf, output_path, name_col="NAME"):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    boroughs_gdf.plot(
        column="lst_mean",
        cmap="inferno",
        legend=True,
        legend_kwds={"label": "Mean Land Surface Temperature (°C)"},
        ax=ax,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_title("London Urban Heat Island — Mean LST by Borough", fontsize=14)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"\nMap saved to {output_path}")


if __name__ == "__main__":
    lst_array, profile = convert_to_lst_celsius(THERMAL_BAND_PATH, OUTPUT_LST_PATH)
    boroughs = compute_borough_stats(OUTPUT_LST_PATH, BOROUGH_SHAPEFILE_PATH)
    plot_borough_heat_map(boroughs, OUTPUT_MAP_PATH)
