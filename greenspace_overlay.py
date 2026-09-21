import geopandas as gpd
import pandas as pd


BOROUGH_SHAPEFILE_PATH = "data/London_Borough_Excluding_MHW.shp"
GREENSPACE_SHAPEFILE_PATH = "data/GB_GreenspaceSite.shp"
OUTPUT_CSV_PATH = "outputs/borough_heat_and_green.csv"

# borough mean LST results from the previous script output
LST_RESULTS = {
    "Brent": 42.29,
    "Kingston upon Thames": 41.54,
    "Ealing": 41.41,
    "Richmond upon Thames": 41.33,
    "Merton": 41.28,
    "Hounslow": 41.04,
    "Hammersmith and Fulham": 41.00,
    "Sutton": 40.18,
    "Southwark": 39.83,
    "Harrow": 39.58,
    "Wandsworth": 39.46,
    "Hillingdon": 39.43,
    "Lewisham": 39.39,
    "Greenwich": 38.87,
    "Lambeth": 38.77,
    "City of London": 38.71,
    "Kensington and Chelsea": 38.31,
    "Croydon": 38.28,
    "Barnet": 38.04,
    "Camden": 37.83,
    "Barking and Dagenham": 37.74,
    "Westminster": 37.60,
    "Newham": 37.46,
    "Bromley": 37.17,
    "Redbridge": 37.17,
    "Bexley": 37.06,
    "Tower Hamlets": 36.42,
    "Islington": 35.48,
    "Hackney": 34.95,
    "Havering": 32.22,
    "Haringey": 31.47,
    "Waltham Forest": 31.36,
    "Enfield": 31.15,
}

print("Loading borough boundaries...")
boroughs = gpd.read_file(BOROUGH_SHAPEFILE_PATH)
name_col = "NAME" if "NAME" in boroughs.columns else boroughs.columns[0]

print("Loading greenspace data (this is a big file, may take a minute)...")
greenspace = gpd.read_file(GREENSPACE_SHAPEFILE_PATH, mask=boroughs)

if greenspace.crs != boroughs.crs:
    greenspace = greenspace.to_crs(boroughs.crs)

print(f"Loaded {len(greenspace)} greenspace polygons within London's extent")


boroughs["borough_area_km2"] = boroughs.geometry.area / 1_000_000

green_pct = []
for idx, row in boroughs.iterrows():
    borough_geom = row.geometry
    clipped = greenspace.clip(borough_geom)
    green_area_km2 = clipped.geometry.area.sum() / 1_000_000
    pct = (green_area_km2 / row["borough_area_km2"]) * 100
    green_pct.append(pct)
    print(f"{row[name_col]}: {pct:.1f}% green cover")

boroughs["green_pct"] = green_pct

boroughs["lst_mean"] = boroughs[name_col].map(LST_RESULTS)

result = boroughs[[name_col, "lst_mean", "green_pct"]].copy()
result.columns = ["borough", "mean_lst_celsius", "green_cover_pct"]

lst_median = result["mean_lst_celsius"].median()
green_median = result["green_cover_pct"].median()

result["priority_zone"] = (
    (result["mean_lst_celsius"] > lst_median)
    & (result["green_cover_pct"] < green_median)
)

result = result.sort_values("mean_lst_celsius", ascending=False)

print("\n--- Full results ---")
print(result.to_string(index=False))

print("\n--- Priority zones (hot + low green cover) ---")
print(result[result["priority_zone"]][["borough", "mean_lst_celsius", "green_cover_pct"]].to_string(index=False))

result.to_csv(OUTPUT_CSV_PATH, index=False)
print(f"\nSaved full results to {OUTPUT_CSV_PATH}")
