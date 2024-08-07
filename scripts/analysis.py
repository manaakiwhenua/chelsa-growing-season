# import numpy as np
# import pandas as pd
from pathlib import Path 
import xarray as xr

smk = snakemake # type: ignore


data : xr.Dataset = xr.open_mfdataset(
    Path(smk.params['climate_record']).glob('*.nc'),
    chunks='auto'
)
print(data)
print(data.attrs)
print(data.isel({'lat':15, 'lon': 3}).tas.data.compute())
