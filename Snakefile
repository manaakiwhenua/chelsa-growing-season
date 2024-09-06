from pathlib import Path

from snakemake.utils import min_version, validate

min_version("8.10")

validate(config, "config.schema.yml")

CLIMATE_ARCHIVE = Path(config.get('climate_data'))
ELEVATION_ARCHIVE = Path(config.get('elevation_data'))

DATA_D = Path(config.get('data_dir'))
LOG_D = Path(config.get('log_dir'))

YEAR_RANGE = config.get('year_range')

FROST_PERIODS = [
    range(2006,2017),
    range(1996,2017)
]

include: "rules/elevation.smk"
include: "rules/chelsa.smk"
include: "rules/clifo.smk"

rule all:
    input:
        chelsa=map(lambda period: expand(SUMMARY_TABLE_CSV, start=period[0], end=period[-1]), FROST_PERIODS),
        clifo=map(lambda period: expand(MEDIAN_CLIFO_TPS, start=period[0], end=period[-1]), FROST_PERIODS)