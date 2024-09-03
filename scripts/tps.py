import logging
import numpy as np
from pathlib import Path
from typing import Any

import dask.array as da
import geopandas as gpd
import rasterio
from scipy.interpolate import Rbf

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

print(points)

# Load the elevation data from the GeoTIFF
with rasterio.open(Path(smk.input.elevation) / smk.params.elevation_file) as src:
    elevation = src.read(1)  # Read the first band
    transform = src.transform
    elev_meta = src.meta
    # Use sample points to get corresponding elevation values
    points['elevation'] = [
        v[0] for v in src.sample([(geom.x, geom.y) for geom in points.geometry])
    ]
    nodata_value = src.nodata

points = points[points['elevation'] != nodata_value]
print(points)

# Prepare x, y, elevation, and z values
x = points.geometry.x.values
y = points.geometry.y.values
elevation_values = points['elevation'].values
z = points['Frost_Period_D'].values  # Column containing dependent variable

# Calculate bounds
bounds = calculate_bounds(elev_meta['transform'], elev_meta['width'], elev_meta['height'])
# Prepare the grid using the calculated bounds
left, bottom, right, top = bounds
grid_x, grid_y = np.meshgrid(
    np.arange(left, right, smk.params.x_res),
    np.arange(bottom, top, smk.params.y_res)
)

# Make sure to flip the grid_y array since rasters typically have a top-to-bottom order
grid_y = grid_y[::-1]

print(grid_x)
print(grid_y)

grid_x_dask = da.from_array(grid_x, chunks=(1000, 1000))
grid_y_dask = da.from_array(grid_y, chunks=(1000, 1000))

print(grid_x_dask)
print(grid_y_dask)


# Extract the corresponding elevation values for the grid
# Calculate the row and column indices for grid_y and grid_x
row_indices = ((grid_y - transform.f) / transform.e).astype(int)
col_indices = ((grid_x - transform.c) / transform.a).astype(int)

# Ensure indices are within the valid range
row_indices = np.clip(row_indices, 0, elevation.shape[0] - 1)
col_indices = np.clip(col_indices, 0, elevation.shape[1] - 1)

# Extract the corresponding elevation values for the grid
grid_elevation = elevation[row_indices, col_indices]

print(grid_elevation)

z = points['Frost_Period_D'].values  # Column containing dependent variable
print(z)

# Fit the TPS model with x, y, and elevation as inputs
tps = Rbf(x, y, elevation_values, z, function='thin_plate', smooth=5, epsilon=2)

# Predict temperature over the grid, including grid elevation
grid_interp = tps(grid_x_dask.ravel(), grid_y_dask.ravel(), grid_elevation.ravel()).reshape(grid_x.shape)

print(grid_interp)
print(grid_interp.shape)

# Update the metadata to reflect the new resolution and grid size
output_meta = elev_meta.copy()
output_meta.update({
    "driver": "GTiff",
    "height": grid_interp.shape[0],
    "width": grid_interp.shape[1],
    "transform": rasterio.transform.from_bounds(
        left, bottom, right, top,
        grid_interp.shape[1], grid_interp.shape[0]
    ),
    "count": 1,
    "dtype": 'float32'
})

# Save the GeoTIFF
with rasterio.open(smk.output[0], "w", **output_meta) as dst:
    dst.write(grid_interp.astype(np.float32), 1)