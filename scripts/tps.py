import logging
import numpy as np
from pathlib import Path
from typing import Any
import sys

import dask.array as da
import geopandas as gpd
import rasterio
from scipy.interpolate import RBFInterpolator
from scipy.spatial import distance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore

def calculate_bounds(transform, width, height):
    left = transform.c
    top = transform.f
    right = left + width * transform.a
    bottom = top + height * transform.e
    return left, bottom, right, top

points = gpd.read_file(smk.input.temperature)

use_closed_stations = smk.params.get('closed_stations', True)

if not use_closed_stations:
    points = points[points['open'] == True]

# Load the elevation data from the GeoTIFF
with rasterio.open(Path(smk.input.elevation) / smk.params.elevation_file) as src:
    elevation = src.read(1)
    transform = src.transform
    elev_meta = src.meta
    points['elevation'] = [
        v[0] for v in src.sample([(geom.x, geom.y) for geom in points.geometry])
    ]
    nodata_value = src.nodata

# Replace nodata values with 1 in the elevation column
points['elevation'] = np.where(points['elevation'] == nodata_value, 1, points['elevation'])

# Calculate bounds
bounds = calculate_bounds(elev_meta['transform'], elev_meta['width'], elev_meta['height'])
# Prepare the grid using the calculated bounds
left, bottom, right, top = bounds
grid_x, grid_y = np.meshgrid(
    np.arange(left, right, smk.params.x_res),
    np.arange(bottom, top, smk.params.y_res)
)

# Flip the grid_y array since rasters have a top-to-bottom orientation
grid_y = grid_y[::-1]

grid_x_dask = da.from_array(grid_x, chunks=(1000, 1000))
grid_y_dask = da.from_array(grid_y, chunks=(1000, 1000))

# Calculate the row and column indices for grid_y and grid_x
row_indices = ((grid_y - transform.f) / transform.e).astype(int)
col_indices = ((grid_x - transform.c) / transform.a).astype(int)

# Ensure indices are within the valid range
row_indices = np.clip(row_indices, 0, elevation.shape[0] - 1)
col_indices = np.clip(col_indices, 0, elevation.shape[1] - 1)

# Extract the corresponding elevation values for the grid
grid_elevation = elevation[row_indices, col_indices]

use_coastal_proximity = smk.params.get('coastal_proximity', True)
coastal_proximity_log = smk.params.get('coastal_proximity_log', True)

if use_coastal_proximity:

    with rasterio.open(smk.input.coastal_proximity) as src:
        prox = src.read(1)
        transform = src.transform
        elev_meta = src.meta
        if coastal_proximity_log:
            prox = np.log1p(prox)
        points['coastal_proximity'] = [
            v[0] for v in src.sample([(geom.x, geom.y) for geom in points.geometry])
        ]
    grid_proximity = prox[row_indices, col_indices]


mahalanobis = smk.params.get('mahalanobis', True)
outlier_threshold = smk.params.get('outlier_threshold', 4)

growing_season = None
last_frost = None
variables = ['Growing_Season_D', 'Last_Frost_DOY', 'First_Frost_DOY']

for band, var in enumerate(variables, start=1):
    _points = points.copy() # Copy so we can manipulate the point data without affecting other interpolations

    # Filter out points with nulls so they don't disturb the interpolation with a fill value
    _points = _points.dropna(subset=[var])

    if mahalanobis:
        _before = len(_points)
        # Mahalanobis Distance Calculation
        mean_vals = np.mean(_points[['elevation', var]], axis=0)
        cov_matrix = np.cov(_points[['elevation', var]], rowvar=False)
        inv_cov_matrix = np.linalg.inv(cov_matrix)

        # Compute Mahalanobis distance for each point
        _points['mahalanobis'] = _points.apply(
            lambda row: distance.mahalanobis(
                row[['elevation', var]], 
                mean_vals, 
                inv_cov_matrix
            ), axis=1
        )
        _points = _points[_points['mahalanobis'] <= outlier_threshold]
        print(f'Mahalanobis (threshold={outlier_threshold}): {_before} stations → {len(_points)} stations')
    
    # Prepare x, y, elevation, and z values
    x = _points.geometry.x.values
    y = _points.geometry.y.values
    elevation_values = _points['elevation'].values
    d_values = _points[var].values

    covariate_grids = (grid_x_dask.ravel(), grid_y_dask.ravel(), grid_elevation.ravel(),)
    if use_coastal_proximity:

        proximity_values = _points['coastal_proximity'].values
        y_coords = np.column_stack((x, y, elevation_values, proximity_values))
        
        if coastal_proximity_log:
            covariate_grids += (np.log1p(grid_proximity.ravel()),)
        else:
            covariate_grids += (grid_proximity.ravel(),)
    else:
        y_coords = np.column_stack((x, y, elevation_values,))

    rbf = RBFInterpolator(
        y_coords, d_values,
        neighbors=smk.params.get('neighbors', None), 
        smoothing=smk.params.get('smooth', None), 
        kernel=smk.params.get('kernel', 'thin_plate_spline'),
        epsilon=smk.params.get('epsilon', None), 
        degree=smk.params.get('degree', None)
    )

    grid_coords = np.column_stack(covariate_grids)
    # Predict temperature over the grid, including grid elevation
    grid_interp = rbf(grid_coords).reshape(grid_x.shape)

    grid_interp = np.clip(np.rint(np.ma.masked_outside(grid_interp, -1e4, 1e4)), a_min=0, a_max=365)

    if var == 'Growing_Season_D':
        growing_season = grid_interp
    elif var == 'Last_Frost_DOY':
        grid_interp = np.where((growing_season < 365) & ~(np.ma.getmask(growing_season)), grid_interp, 0)
        grid_interp = np.where(np.ma.getmask(growing_season), -1, grid_interp)
        last_frost = grid_interp
    else:
        # To produce internally consistent data, we calculate the first frost DOY by reference to the last frost, and the growing season, therefore ignoring the grid interpolation result
        grid_interp = (last_frost + growing_season) % 365

    # Update the metadata to reflect the new resolution and grid size
    if band == 1:
        output_meta = elev_meta.copy()
        output_meta.update({
            "driver": "GTiff",
            "height": grid_interp.shape[0],
            "width": grid_interp.shape[1],
            "transform": rasterio.transform.from_bounds(
                left, bottom, right, top,
                grid_interp.shape[1], grid_interp.shape[0]
            ),
            "count": len(variables),
            "dtype": 'int16',
            "nodata": -1
        })
        dst = rasterio.open(smk.output[0], "w", **output_meta)

    print(f'writing band {band} ({var})')
    dst.write(grid_interp.astype(rasterio.float32), band)
    dst.set_band_description(band, var)

dst.close()