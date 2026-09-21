"""
London Priority Zones Map
----------------------------
Visualizes which boroughs are flagged as priority zones (hot + low green
cover) against the rest of London, using the CSV saved by
greenspace_overlay.py.
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

BOROUGH_SHAPEFILE_PATH = "data/London_Borough_Excluding_MHW.shp"
RESULTS_CSV_PATH = "outputs/borough_heat_and_green.csv"
OUTPUT_MAP_PATH = "outputs/london_priority_zones_map.png"

boroughs = gpd.read_file(BOROUGH_SHAPEFILE_PATH)
name_col = "NAME" if "NAME" in boroughs.columns else boroughs.columns[0]

results = pd.read_csv(RESULTS_CSV_PATH)

merged = boroughs.merge(results, left_on=name_col, right_on="borough")

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Base layer: all boroughs in light grey
merged.plot(ax=ax, color="#e8e8e8", edgecolor="white", linewidth=0.8)

# Priority zones highlighted in red/orange
priority = merged[merged["priority_zone"] == True]
priority.plot(ax=ax, color="#d9432e", edgecolor="white", linewidth=0.8)

# Label priority boroughs
for idx, row in priority.iterrows():
    centroid = row.geometry.centroid
    ax.annotate(
        row["borough"],
        xy=(centroid.x, centroid.y),
        ha="center",
        fontsize=8,
        color="white",
        fontweight="bold",
    )

ax.set_title(
    "London Priority Zones for Climate Intervention\n"
    "(Above-average surface temperature + below-average green cover)",
    fontsize=13,
)
ax.set_axis_off()

plt.tight_layout()
plt.savefig(OUTPUT_MAP_PATH, dpi=200)
print(f"Priority zones map saved to {OUTPUT_MAP_PATH}")
