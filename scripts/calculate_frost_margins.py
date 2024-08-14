import gc
import logging
from pathlib import Path
from typing import List, Any

import xarray as xr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore
var: str = smk.params.get('var', 'tasmin')
frost_c: float = smk.params.get('threshold_c', -2.2)
frost_k: float = frost_c + 273.15
year_range: range = smk.params.get('year_range', range(1996, 2017, 1))

def find_first_last_below_threshold(group: xr.DataArray, no_frost: int = -1) -> xr.Dataset:
    """
    Find the first and last days of the year where the temperature is below the frost threshold.

    Locations with no frost are recorded with a value of -1.
    Locations with no temperature data (marine) are recorded with nan.

    Parameters:
        group (xr.DataArray): The xarray data array containing temperature data.
        no_frost (int): The value used to represent the absence of frost
    Returns:
        xr.Dataset: Dataset containing the first and last frost days.
    """
    below_threshold: xr.DataArray = (group <= frost_k).compute()
    
    first_frost_index: xr.DataArray = below_threshold.argmax(dim='time').where(below_threshold.any(dim='time'), other=no_frost)
    first_frost_date: xr.DataArray = group.time.isel(time=first_frost_index.astype(int))
    first_frost: xr.DataArray = first_frost_date.dt.dayofyear.where(first_frost_index != no_frost, other=no_frost)

    del first_frost_index, first_frost_date#, no_frost
    gc.collect()

    # Reverse the time dimension
    reverse_below_threshold: xr.DataArray = below_threshold.isel(time=slice(None, None, -1))
    last_frost_index: xr.DataArray = reverse_below_threshold.argmax(dim='time')
    last_frost_index: xr.DataArray = xr.where(below_threshold.any(dim='time'), len(group.time) - 1 - last_frost_index, no_frost)
    
    last_frost_date: xr.DataArray = group.time.isel(time=last_frost_index.clip(min=0).astype(int))
    last_frost: xr.DataArray = last_frost_date.dt.dayofyear.where(last_frost_index != no_frost, other=no_frost)

    last_frost: xr.DataArray = last_frost.assign_coords(time=first_frost.time)

    first_frost: xr.DataArray = first_frost.drop_vars('time')
    last_frost: xr.DataArray = last_frost.drop_vars('time')

    del reverse_below_threshold, below_threshold, last_frost_index, last_frost_date
    gc.collect()

    return xr.Dataset({
        'first_frost': first_frost.astype('int16'),
        'last_frost': last_frost.astype('int16')
    })

output_path: Path = Path(smk.output[0])

def process_year(year: int, output_path: Path, var: str) -> None:
    annual_temperature_data = Path(smk.input[0]).glob(f'*daily_{year}*.nc')
    # Data is daily, but organised into monthly files
    # Collect them into annual (calendar) virtual files
    with xr.open_mfdataset(annual_temperature_data, chunks='auto') as data:
        results: xr.DataArray = data[var].resample(time='YS-JAN').map(find_first_last_below_threshold)
        all_nan_mask: xr.DataArray = data[var].isnull().all(dim='time')
        results = results.where(~all_nan_mask)
        year_output_path: Path = output_path.with_name(f"{output_path.stem}_{year}.nc")
        results.to_netcdf(year_output_path, format='NETCDF4')
        logger.info(f"Processed and saved data for year {year}")

    del data, all_nan_mask
    gc.collect()

def combine_intermediate_files(output_path: Path) -> None:
    intermediate_data: List[Path] = list(Path(output_path.parent).glob('*_[0-9]*.nc'))
    with xr.open_mfdataset(intermediate_data, chunks='auto') as data:
        data.to_netcdf(output_path)
        logger.info(f"Combined intermediate files into {output_path}")

def main():
    for year in year_range:
        process_year(year, output_path, var)
    combine_intermediate_files(output_path)

if __name__ == "__main__":
    main()