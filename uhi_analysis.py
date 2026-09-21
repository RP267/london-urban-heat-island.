"""
London Urban Heat Island (UHI) Analysis
-----------------------------------------
Converts a Landsat Collection 2 Level-2 thermal band (ST_B10) into
Land Surface Temperature (LST), then computes zonal statistics per
London borough so you can compare average heat across the city.

Requirements:
    pip install rasterio geopandas numpy matplotlib rasterstats

Inputs you need before running this:
    1. A Landsat 8/9 Collection 2 Level-2 scene covering London
       -> specifically the ST_B10.TIF file (already-scaled surface temp band)
    2. The London borough boundary shapefile from the London Datastore
       ("Statistical GIS Boundary Files for London")

Usage:
    python uhi_analysis.py
"""

import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from rasterstats import zonal_stats
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# CONFIG — update these paths to match your downloaded files
# ---------------------------------------------------------------------------
THERMAL_BAND_PATH = "data/LC09_L2SP_201024_20260814_20260815_02_T1_ST_B10.TIF"   # Collection 2 Level-2 thermal band
BOROUGH_SHAPEFILE_PATH = "data/London_Borough_Excluding_MHW.shp"
OUTPUT_LST_PATH = "outputs/london_lst_celsius.tif"
OUTPUT_MAP_PATH = "outputs/london_uhi_map.png"

# ---------------------------------------------------------------------------
# STEP 1 — Convert the raw thermal band (Kelvin, scaled) to LST in Celsius
# ---------------------------------------------------------------------------
# Landsat Collection 2 Level-2 ST_B10 is already surface temperature, but
# stored as a scaled integer. The official scale factor and offset convert
# it directly to Kelvin (see USGS Landsat Collection 2 Level-2 Science
# Product Guide).

SCALE_FACTOR = 0.00341802
ADD_OFFSET = 149.0


def convert_to_lst_celsius(thermal_band_path, output_path):
    with rasterio.open(thermal_band_path) as src:
        raw = src.read(1).astype(np.float64)
        profile = src.profile

        # Landsat uses 0 as a "no data" fill value for this product
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


# ---------------------------------------------------------------------------
# STEP 2 — Zonal statistics: average LST per borough
# ---------------------------------------------------------------------------

def compute_borough_stats(lst_raster_path, borough_shapefile_path):
    boroughs = gpd.read_file(borough_shapefile_path)

    # Reproject boroughs to match the raster's CRS if needed
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


# ---------------------------------------------------------------------------
# STEP 3 — Choropleth map of borough-level heat
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lst_array, profile = convert_to_lst_celsius(THERMAL_BAND_PATH, OUTPUT_LST_PATH)
    boroughs = compute_borough_stats(OUTPUT_LST_PATH, BOROUGH_SHAPEFILE_PATH)
    plot_borough_heat_map(boroughs, OUTPUT_MAP_PATH)
