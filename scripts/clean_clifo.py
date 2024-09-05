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

stations = glob.glob(smk.params.stations)
record = glob.glob(smk.params.record)
max_fill_days = smk.params.get('max_fill_days', 1)
interp = smk.params.get('interp', 'time')
threshold = smk.params.get('threshold', 0)

stations_df = pd.concat((pd.read_csv(f) for f in stations), ignore_index=True)
# Drop unnamed counter column
stations_df = stations_df.drop(stations_df.columns[0], axis=1)
stations_df = stations_df.drop_duplicates(['name','network','agent'])
stations_df = stations_df.sort_values(by=['start', 'name'])

record_df = pd.concat((pd.read_csv(f) for f in record), ignore_index=True)
# Drop unnamed counter column
record_df = record_df.drop(record_df.columns[0], axis=1)
record_df = record_df.drop_duplicates()
record_df['Date.local'] = pd.to_datetime(record_df['Date.local'])
record_df = record_df.sort_values(by=['Station', 'Date.local'])

# Interpolation function
# Only interpolate small gaps
# Control gap size with `max_fill_days` param
# Control interpolation method with `interp` param
def interpolate_station(df):
    station_name = df['Station'].iloc[0]
    df = df.set_index('Date.local').asfreq('D')
    for column in ['Tmax.C', 'Tmin.C', 'Tgmin.C']:
        # Round to 1 decimal place
        df[column] = df[column].round(1)
        if max_fill_days > 0:
            if df[column].notna().sum() >= 2:
                df[column] = df[column].interpolate(method=interp, limit=max_fill_days)
            else:
                logging.warning(f"Not enough data to interpolate {column} for station {station_name}")
    df = df.reset_index()  # Reset the index to include 'Date.local' back as a column
    df['Station'] = station_name  # Reassign the station name to the 'Station' column
    
    return df

grouped = record_df.groupby('Station')
interpolated_df = grouped.apply(interpolate_station, include_groups=True).reset_index(drop=True)
interpolated_df['Year'] = interpolated_df['Date.local'].dt.year


# Function to find the first and last date when the temperature first reaches the threshold
def find_first_last_dates(df):
    year = df['Date.local'].min().year
    df = df[df['Tmin.C'] <= threshold]

    if df.empty:
        # placeholder_start, placeholder_end = pd.Na, pd.NA
        placeholder_start, placeholder_end = pd.Timestamp(f"{year}-12-31"), pd.Timestamp(f"{year}-01-01")
        return pd.Series({
            'First_Date': placeholder_start,
            'Last_Date': placeholder_end
        })
    
    # Find the first and last dates
    first_date = df['Date.local'].min()
    last_date = df['Date.local'].max()
    
    return pd.Series({'First_Date': first_date, 'Last_Date': last_date})


# Group by Station and Year, and apply the function
result_df = interpolated_df.groupby(['Station', 'Year']).apply(find_first_last_dates).reset_index()

result_df['First_Date'] = pd.to_datetime(result_df['First_Date'], errors='coerce')
result_df['Last_Date'] = pd.to_datetime(result_df['Last_Date'], errors='coerce')
print(result_df)

joined_df = pd.merge(result_df, stations_df, left_on='Station', right_on='name', how='left')

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    joined_df,
    geometry=gpd.points_from_xy(joined_df.lon, joined_df.lat),
    crs="EPSG:4326"  # Specify the coordinate reference system
).to_crs(epsg='2193')

# Write to GeoParquet file with spatial partitioning
gdf.to_parquet(smk.output[0], index=False, compression='snappy', engine='pyarrow')

sys.exit(0)