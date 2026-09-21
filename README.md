# London Urban Heat Island Analysis

Mapping land surface temperature across London's 33 boroughs using Landsat 9 thermal imagery, and identifying priority zones for green infrastructure investment by combining heat data with green space coverage.

## Overview

This project uses satellite thermal imagery and open geospatial data to answer two questions:

1. **Where is London hottest?** — Land Surface Temperature (LST) varies significantly across the city, driven by land cover, urban density, and green space.
2. **Where should intervention be prioritized?** — Combining heat data with green space coverage identifies boroughs that are both disproportionately hot *and* under-greened.

## Key findings

- Mean LST across London boroughs ranged from **31.1°C (Enfield) to 42.3°C (Brent)** — an 11°C spread driven by land cover and urban density rather than geography alone.
- **8 boroughs** were flagged as priority zones (above-average heat + below-average green cover): Brent, Kingston upon Thames, Hammersmith and Fulham, Harrow, Hillingdon, Lewisham, Lambeth, and City of London.
- These priority boroughs form two distinct geographic clusters — northwest London (Hillingdon, Harrow, Brent, Hammersmith and Fulham) and south London (Lambeth, Lewisham, Kingston) — suggesting shared underlying causes within each cluster rather than isolated cases.

<img width="2000" height="2000" alt="london_priority_zones_map" src="https://github.com/user-attachments/assets/8fe94b5b-7cc1-47c4-aba6-2a2311644694" />

## Methodology

1. **Thermal data**: Landsat 9 Collection 2 Level-2 imagery (August 2026, <2% cloud cover) provided pre-calibrated surface temperature (ST_B10 band).
2. **LST conversion**: Raw digital numbers converted to Celsius using the standard USGS scale factor (0.00341802) and offset (149.0).
3. **Zonal statistics**: Mean LST computed per borough using `rasterstats`, based on official ONS/GLA borough boundaries.
4. **Green cover**: OS Open Greenspace polygons clipped to each borough to calculate % green space coverage.
5. **Priority zone classification**: A borough is flagged as a priority zone if its mean LST is above the London median *and* its green cover is below the London median.

## Data sources

| Dataset | Source | Notes |
|---|---|---|
| Landsat 9 thermal imagery | [USGS EarthExplorer](https://earthexplorer.usgs.gov) | Collection 2 Level-2, Path 201 Row 024 |
| Borough boundaries | [London Datastore](https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london) | Statistical GIS Boundary Files |
| Green space | [OS Open Greenspace](https://osdatahub.os.uk/downloads/open/OpenGreenspace) | Ordnance Survey, GB-wide |

## Tools

Python (`rasterio`, `geopandas`, `numpy`, `matplotlib`, `rasterstats`), with ArcGIS Pro used for cartographic refinement.

## Limitations

- Boroughs at the edge of the Landsat scene footprint (e.g. Enfield) may be under-sampled and should be treated with lower confidence.
- Single-date snapshot (August 2026) — does not capture seasonal or diurnal variation in surface temperature.
- Green cover is measured by area, not tree canopy density or quality — a large sports field counts the same as dense woodland.

## Scripts

- `uhi_analysis.py` — LST conversion and borough-level zonal statistics
- `greenspace_overlay.py` — green cover calculation and priority zone flagging
- `priority_zones_map.py` — final visualization

## Author

Rohan Patel — Geography BSc, Kingston University London
