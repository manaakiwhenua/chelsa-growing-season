GROWING_SEASON = DATA_D / 'growing-season.nc'
MEDIAN_FROST = DATA_D / 'median_frost-{start}-{end}.nc'
SUMMARY_TABLE_CSV = DATA_D / 'median_frost-{start}-{end}.csv'
SUMMARY_TABLE_PDF = DATA_D / 'median_frost-{start}-{end}.pdf'

rule unzip_climate_data:
    output: directory(DATA_D / 'chelsa')
    log: LOG_D / 'unzip_climate_data'
    params:
        archive=CLIMATE_ARCHIVE
    shell: 'mkdir -p {output} && unzip -o -d {output} {params.archive} &> {log}'

rule calculate_frost_margins:
    input: DATA_D / 'chelsa'
    output: GROWING_SEASON
    log: LOG_D / 'calculate_frost_margins.log'
    conda: '../envs/netcdf.yml'
    params:
        var='tasmin',
        threshold_c=-2.2,
        year_range=range(*YEAR_RANGE, 1)
    script: '../scripts/calculate_frost_margins.py'

rule median_frost_doy:
    input: GROWING_SEASON
    output: MEDIAN_FROST
    log: LOG_D / 'median_frost_doy-{start}-{end}.log'
    conda: '../envs/netcdf.yml'
    params:
        start=lambda wc: int(wc.start),
        end=lambda wc: int(wc.end)
    script: '../scripts/median_frost_doy.py'

rule summary_table:
    input: MEDIAN_FROST
    output:
        csv=SUMMARY_TABLE_CSV,
        pdf=SUMMARY_TABLE_PDF
    log: LOG_D / 'summay_table-{start}-{end}.log'
    conda: '../envs/netcdf.yml'
    params:
        summary_table=config.get('summary_table')
    script: '../scripts/summary_table.py'