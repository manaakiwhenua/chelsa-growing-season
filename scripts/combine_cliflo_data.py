import glob
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smk: Any = snakemake # type: ignore

climate_stations_df = pd.concat(
    map(
        pd.read_csv(
            glob.glob(smk.params.get('station_data')),
            ignore_index=True
        )
    )
)

print(climate_stations_df)