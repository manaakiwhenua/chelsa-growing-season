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

clifo = gpd.read_parquet(smk.input[0])

print(clifo)

clifo = clifo[
    (clifo['Year'] >= int(start)) & (clifo['Year'] <= int(end))
]
# Convert 'start' and 'end' columns to datetime
clifo['start'] = pd.to_datetime(clifo['start'])
clifo['end'] = pd.to_datetime(clifo['end'])
# Define the range within which to check the duration
range_start = pd.to_datetime(f'{start}-01-01')
range_end = pd.to_datetime(f'{end}-12-31')

# Function to calculate duration within the specified range
def calculate_duration_in_range(start, end, range_start, range_end):
    # Determine the intersection of the two ranges
    intersect_start = max(start, range_start)
    intersect_end = min(end, range_end)
    if intersect_start < intersect_end:
        duration_years = (intersect_end - intersect_start).days / 365.25
        return duration_years
    else:
        return 0

# Calculate the duration in years
# Apply the function to filter rows
clifo['duration_in_range'] = clifo.apply(
    lambda row: calculate_duration_in_range(row['start'], row['end'], range_start, range_end), axis=1
).round(0)

clifo = clifo[clifo['duration_in_range'] >= min_period_Y]
# clifo = clifo.drop(columns=['duration_in_range'])

print(clifo)


clifo['First_Frost_DOY'] = clifo['First_Date'].dt.dayofyear
clifo['Last_Frost_DOY'] = clifo['Last_Date'].dt.dayofyear
clifo['Frost_Period_D'] = (clifo['Last_Frost_DOY'] - clifo['First_Frost_DOY'] + 1).clip(lower=0)


clifo['Growing_Season_D'] = (clifo['Year'].apply(days_in_year) - clifo['Frost_Period_D']).fillna(np.inf)#.fillna(clifo['Year'].apply(days_in_year))

print(clifo[['First_Frost_DOY','Last_Frost_DOY','Frost_Period_D','Growing_Season_D']])

def median_frost_day(series, fill_value=np.nan):   
    # Calculate the median

    series = series.fillna(fill_value)
    median = series.median(skipna=True)
    
    # Determine the fraction of placeholder values
    placeholder_fraction = (series.isna().sum() / len(series))
    
    # If more than 50% of the values are placeholders, return NaN
    if placeholder_fraction > 0.5:
        return np.nan
    else:
        return median

medians = gpd.GeoDataFrame(clifo.groupby(['Station', 'network', 'agent', 'start', 'end', 'open', 'lat', 'lon', 'geometry', 'duration_in_range']).agg({
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

    # Create a KDTree for efficient spatial queries
    tree = cKDTree(coords)

    # List to keep track of indices to drop
    indices_to_drop = []

    # Iterate over points and find nearby points
    for idx, coord in enumerate(coords):
        if idx in indices_to_drop:
            continue  # Skip already marked points
        
        # Find nearby points within the threshold distance
        nearby_indices = tree.query_ball_point(coord, r=spatial_coincidence_threshold)
        
        # If more than one point is nearby, apply filtering logic
        if len(nearby_indices) > 1:
            # Get the subset of points that are nearby
            nearby_points = medians.iloc[nearby_indices]
                        
            # keep the one that has the most records in the 'duration_in_rangend' attribute
            longest_open_point = nearby_points.loc[nearby_points['duration_in_range'].idxmax()]
            indices_to_drop.extend(nearby_points.index.difference([longest_open_point.name]).tolist())
        
        
    # Drop the identified points
    medians = medians.drop(indices_to_drop)

medians.to_parquet(smk.output[0], index=False, compression='snappy', engine='pyarrow')

sys.exit(0)