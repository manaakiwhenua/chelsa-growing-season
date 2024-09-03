CLIFO_DOWNLOAD_STATIONS = 'static/clifo/all_cf_stations_*.csv'
CLIFO_DOWNLOAD_DATA = 'static/clifo/all_cf_data_*.csv'

CLEAN_CLIFO = DATA_D / 'clifo_clean.pq'
MEDIAN_CLIFO = DATA_D / 'clifo_median_frost-{start}-{end}.pq'

ELEVATION = DATA_D / 'elevation'

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
        min_period_Y=lambda wc: 0.5 * (int(wc.end) - int(wc.start)) # Records of less than this value (in years), within the start-end period, will be ignored
    script: '../scripts/median_clifo.py'

rule unzip_elevation:
    output: directory(ELEVATION)
    log: LOG_D / 'unzip_elevation.log'
    params:
        archive=ELEVATION_ARCHIVE
    shell: 'mkdir -p {output} && unzip -o -d {output} {params.archive} &> {log}'

# TODO I also think distance from the coast should be a covariate
# TODO output should have a band for each input variable
rule thin_plate_spline:
    message: 'Apply a thin plate spline spatial interpolation between stations, with a day of year or season length as the dependent variable; and elevation as a covariate'
    input:
        temperature=MEDIAN_CLIFO,
        elevation=ELEVATION
    output: MEDIAN_CLIFO_TPS
    conda: '../envs/thinplate.yml'
    log: LOG_D / 'thin_plate_spline_{start}-{end}.log'
    params:
        elevation_file='nzenvds-elevation-v10.tif',
        x_res=1000,
        y_res=1000
    script: '../scripts/tps.py'