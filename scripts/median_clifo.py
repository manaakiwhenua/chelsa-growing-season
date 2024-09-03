import calendar
import glob
import logging
import numpy as np
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore


start, end = smk.wildcards.get('start'), smk.wildcards.get('end')
min_period_Y = smk.params.get('min_period_Y', 1)

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
)
clifo = clifo[clifo['duration_in_range'] >= min_period_Y]
clifo = clifo.drop(columns=['duration_in_range'])

print(clifo)


clifo['First_Frost_DOY'] = clifo['First_Date'].dt.dayofyear#.fillna(365.0)
clifo['Last_Frost_DOY'] = clifo['Last_Date'].dt.dayofyear#.fillna(0.0)
clifo['Frost_Period_D'] = (clifo['Last_Frost_DOY'] - clifo['First_Frost_DOY'] + 1)

clifo['Growing_Season_D'] = (clifo['Year'].apply(days_in_year) - clifo['Frost_Period_D']).fillna(np.inf)#.fillna(clifo['Year'].apply(days_in_year))

clifo['Frost_Period_D'] = clifo['Frost_Period_D'].fillna(0.0)

def median_frost_day(series):   
    # Calculate the median
    median = series.median(skipna=True)
    
    # Determine the fraction of placeholder values
    placeholder_fraction = (series.isna().sum() / len(series))
    
    # If more than 50% of the values are placeholders, return NaN
    if placeholder_fraction > 0.5:
        return np.nan
    else:
        return median

medians = gpd.GeoDataFrame(clifo.groupby(['Station', 'network', 'agent', 'start', 'end', 'open', 'lat', 'lon', 'geometry']).agg({
    'First_Frost_DOY': median_frost_day,
    'Last_Frost_DOY': median_frost_day,
    'Growing_Season_D': 'median',
    'Frost_Period_D': 'median'
}).reset_index(), crs="EPSG:2193")

medians.to_parquet(smk.output[0], index=False, compression='snappy', engine='pyarrow')

sys.exit(0)