CLIFO_DOWNLOAD_STATIONS = 'static/clifo/all_cf_stations_*.csv'
CLIFO_DOWNLOAD_DATA = 'static/clifo/all_cf_data_*.csv'

CLEAN_CLIFO = DATA_D / 'clifo_clean.pq'
MEDIAN_CLIFO = DATA_D / 'clifo_median_{start}-{end}.pq'

COASTAL_PROXIMITY = 'static/coastal_proximity.tif'

MEDIAN_CLIFO_TPS = DATA_D / 'clifo_tps-{start}-{end}.tif'

rule clean_clifo_data:
    message: 'Clean downloaded (pre-existing) Cliflo data; removing duplicates; doing some interpolation for small gaps in the temperature record; group by station and calculate the first and last date of frost for eacgh year'
    output: CLEAN_CLIFO
    log: LOG_D / 'clean_clifo_data.log'
    conda: '../envs/pandas.yml'
    params:
        stations=CLIFO_DOWNLOAD_STATIONS,
        record=CLIFO_DOWNLOAD_DATA,
        max_fill_days=3,
        interp='akima', # https://en.wikipedia.org/wiki/Akima_spline
        threshold=-2.2 # degC
    script: '../scripts/clean_clifo.py'

rule median_clifo_data:
    message: 'Calculate median frost dates, and therefore season lengths, appropriately ignoring invalid data'
    input: CLEAN_CLIFO
    output: MEDIAN_CLIFO
    log:  LOG_D / 'median_clifo_data_{start}-{end}.log'
    conda: '../envs/pandas.yml'
    params:
        min_period_Y=lambda wc: 6/18 * (int(wc.end) - int(wc.start)), # Records of less than this value (in years), within the start-end period, will be ignored
        spatial_filter=True, # Whether to filter out stations that are spatially co-incident
        spatial_coincidence_threshold=6e3 # Stations within this distance of other stations will be dropped, when their "open" status is False
    script: '../scripts/median_clifo.py'


# TODO I also think distance from the coast should be a covariate
# TODO output should have a band for each input variable
rule thin_plate_spline:
    message: 'Apply a thin plate spline spatial interpolation between stations, with a day of year or season length as the dependent variable; and elevation as a covariate'
    input:
        temperature=MEDIAN_CLIFO,
        elevation=ELEVATION,
        coastal_proximity=COASTAL_PROXIMITY
    output: MEDIAN_CLIFO_TPS,
    conda: '../envs/thinplate.yml'
    log: LOG_D / 'thin_plate_spline_{start}-{end}.log'
    params:
        elevation_file='nzenvds-elevation-v10.tif',
        x_res=256*4,
        y_res=256*4,
        smooth=5, # Values greater than zero increase the smoothness of the approximation. 0 is for interpolation (default), the function will always go through the nodal points in this case.
        epsilon=None, # Adjustable constant for gaussian or multiquadrics functions - defaults to approximate average distance between nodes (which is a good start).
        mahalanobis=True, # Whether to apply Mahalanobis outlier detection (considers the relationship between the dependent variable and the elevation covariate)
        outlier_threshold=4, # Threshold (Mahalanobis distance)
        coastal_proximity=True, # Whether to consider coastal_proximity
        coastal_proximity_log=False, # Whether to apply a log(1 + x) transformation to coastal proximity
        closed_stations=True, # Whether to include closed stations
    script: '../scripts/tps.py'