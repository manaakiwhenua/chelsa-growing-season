from pathlib import Path

from snakemake.utils import min_version, validate

min_version("8.10")

validate(config, "config.schema.yml")

DOWNLOAD_D = Path(config.get('download_dir'))
LOG_D = Path(config.get('log_dir'))

GROWING_SEASON = DOWNLOAD_D / 'growing-season.tif'

# TODO https://github.com/pydata/bottleneck
rule analyse_netcdf:
    output: GROWING_SEASON
    log: LOG_D / 'analyse_netcdf.log'
    conda: 'envs/netcdf.yml'
    params:
        climate_record=DOWNLOAD_D
    script: 'scripts/analysis.py'