import logging
import numpy as np
from pathlib import Path
from typing import Any

import xarray as xr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore
t_range = range(smk.params.get('start'), smk.params.get('end') + 1, 1)

frost_vars = ['first_frost', 'last_frost']

with xr.open_dataset(Path(smk.input[0])) as data:
    data_vars = {}

    for frost in frost_vars:
        # Potentially subset to a narrower period
        frost_da = data[frost].sel(time=slice(f'{t_range[0]}-01-01', f'{t_range[-1]}-12-31'))
        # Calculate median over period
        median_frost_doy = np.nanmedian(
            data[frost].values, axis=0
        )
        da = xr.DataArray(
            median_frost_doy,
            coords={
                'lat': data.coords['lat'],
                'lon': data.coords['lon']
            },
            dims=['lat', 'lon'],
            name=f'median_{frost}'
        )
        data_vars[f'median_{frost}'] = da
    
    data_vars['median_frost_period'] = data_vars[f'median_{frost_vars[1]}'] - data_vars[f'median_{frost_vars[0]}']
    
    ds = xr.Dataset(data_vars)
    ds.to_netcdf(Path(smk.output[0]), format='NETCDF4')