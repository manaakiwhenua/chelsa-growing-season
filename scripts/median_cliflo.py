import calendar
import glob
import logging
import numpy as np
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree
from shapely.geometry import Point


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore


start, end = smk.wildcards.get('start'), smk.wildcards.get('end')
min_period_Y = smk.params.get('min_period_Y', 1)
spatial_coincidence_threshold = smk.params.get('spatial_coincidence_threshold', 500)

days_in_year = lambda year: 365 + calendar.isleap(int(year))

cliflo = gpd.read_parquet(smk.input[0])

cliflo = cliflo[
    (cliflo['Year'] >= int(start)) & (cliflo['Year'] <= int(end))
]
cliflo['start'] = pd.to_datetime(cliflo['start'])
cliflo['end'] = pd.to_datetime(cliflo['end'])

range_start = pd.to_datetime(f'{start}-01-01')
range_end = pd.to_datetime(f'{end}-12-31')

def calculate_duration_in_range(start, end, range_start, range_end):
    intersect_start = max(start, range_start)
    intersect_end = min(end, range_end)
    if intersect_start < intersect_end:
        duration_years = (intersect_end - intersect_start).days / 365.25
        return duration_years
    else:
        return 0

cliflo['duration_in_range'] = cliflo.apply(
    lambda row: calculate_duration_in_range(row['start'], row['end'], range_start, range_end), axis=1
).round(0)

# Ignore records with insufficient record lengths
cliflo = cliflo[cliflo['duration_in_range'] >= min_period_Y]

cliflo['First_Frost_DOY'] = cliflo['First_Date'].dt.dayofyear
cliflo['Last_Frost_DOY'] = cliflo['Last_Date'].dt.dayofyear
cliflo['Frost_Period_D'] = (cliflo['Last_Frost_DOY'] - cliflo['First_Frost_DOY'] + 1).clip(lower=0)


cliflo['Growing_Season_D'] = (cliflo['Year'].apply(days_in_year) - cliflo['Frost_Period_D']).fillna(np.inf)

def median_frost_day(series, fill_value=np.nan):   
    # Calculate the median
    series = series.fillna(fill_value)
    median = series.median(skipna=True)
    
    # Determine the fraction of placeholder values
    placeholder_fraction = (series.isna().sum() / len(series))
    
    return median if placeholder_fraction < 0.5 else np.nan

group_by_cols = ['Station', 'network', 'agent', 'start', 'end', 'open', 'lat', 'lon', 'geometry', 'duration_in_range']
medians = gpd.GeoDataFrame(cliflo.groupby(group_by_cols).agg({
    'First_Frost_DOY': lambda x: median_frost_day(x, fill_value=365),
    'Last_Frost_DOY': lambda x: median_frost_day(x, fill_value=0.0),
    'Growing_Season_D': 'median',
    'Frost_Period_D': 'median'
}).reset_index(), crs="EPSG:2193")

# When first frost DOY is later than last frost DOY, that's the effect of median calculations using the fill values for no frost
# We will treat such places as having no frost, in the median case
special_cases = medians[medians['First_Frost_DOY'] > medians['Last_Frost_DOY']]
medians.loc[medians['First_Frost_DOY'] > medians['Last_Frost_DOY'], ['First_Frost_DOY', 'Last_Frost_DOY', 'Growing_Season_D', 'Frost_Period_D']] = [pd.NA, pd.NA, 365, 0]

if smk.params.get('spatial_filter', True):
    # Remove points that are nearby, preferring open stations
    coords = np.array([(geom.x, geom.y) for geom in medians.geometry])
    tree = cKDTree(coords)
    indices_to_drop = []
    for idx, coord in enumerate(coords):
        if idx in indices_to_drop:
            continue  # Skip already marked points
        # Find nearby points within the threshold distance
        nearby_indices = tree.query_ball_point(coord, r=spatial_coincidence_threshold)
        # If more than one point is nearby, apply filtering logic
        if len(nearby_indices) > 1:
            # Get the subset of points that are nearby
            nearby_points = medians.iloc[nearby_indices]
            # keep the one that has the most records in the 'duration_in_range' attribute
            longest_open_point = nearby_points.loc[nearby_points['duration_in_range'].idxmax()]
            indices_to_drop.extend(nearby_points.index.difference([longest_open_point.name]).tolist())
    # Drop the identified points
    medians = medians.drop(indices_to_drop)

medians.to_parquet(smk.output[0], index=False, compression='snappy', engine='pyarrow')

sys.exit(0)