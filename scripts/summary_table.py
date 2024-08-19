from datetime import datetime, timedelta
import logging
from pathlib import Path
import numpy as np
from typing import Any

from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from shapely.geometry import Point
import textwrap
import xarray as xr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore
df = pd.DataFrame.from_dict(smk.params.get('summary_table'))

geometry = [Point(*loc.split(', ',)[::-1]) for loc in list(df.location)]
gdf = GeoDataFrame(df, crs='EPSG:4326', geometry=geometry)

def sample_netcdf(row, dataset):
    lat, lon = row.geometry.y, row.geometry.x
    sampled_values = {}
    for var in dataset.data_vars:
        sampled_values[var] = dataset[var].sel(
            lat=lat, lon=lon, method='nearest'
        ).values.item()
    return pd.Series(sampled_values).replace(-1, np.nan)

def doy_to_date(doy):
    if np.isnan(doy):
        return 'Continuous'
    base_date = datetime(2001, 1, 1)
    target_date = base_date + timedelta(days=doy - 1)
    return target_date.strftime('%-d %b')


def wrap_text(text, width):
    return '\n'.join(textwrap.wrap(text, width))

def dataframe_to_pdf(df, filename, column_width=11, row_height=2):
    df_wrapped = df.copy()
    for col in df.columns:
        df_wrapped[col] = df[col].apply(lambda x: wrap_text(str(x), column_width))


    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(cellText=df_wrapped.values, colLabels=df.columns, loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, row_height)

    for (i, j), cell in table._cells.items():
        if i == 0:  # Header row
            cell.set_text_props(weight='bold', fontsize=12)
        if j in range(len(df.columns)):
            cell.set_edgecolor('black')
            cell.set_linewidth(1)
        cell.set_fontsize(8)
        cell.set_text_props(ha='center', va='center')


    with PdfPages(filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close(fig)

with xr.open_dataset(Path(smk.input[0])) as dataset:
    gdf = pd.concat([
        gdf, gdf.apply(sample_netcdf, dataset=dataset, axis=1)
    ], axis=1)
    gdf['median_frost_period'] = gdf['median_frost_period'].astype(int)
    gdf['growing_season'] = 365 - gdf['median_frost_period']

    gdf['median_first_frost'] = gdf['median_first_frost'].apply(doy_to_date)
    gdf['median_last_frost'] = gdf['median_last_frost'].apply(doy_to_date)
    
    dataframe_to_pdf(gdf.drop(columns=['location','geometry']), smk.output['pdf'])
    # gdf.geo = gdf.geometry.apply(lambda geom: geom.wkt)
    gdf.to_csv(smk.output['csv'], index=False)