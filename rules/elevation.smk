ELEVATION = DATA_D / 'elevation'

rule unzip_elevation:
    output: directory(ELEVATION)
    log: LOG_D / 'unzip_elevation.log'
    params:
        archive=ELEVATION_ARCHIVE
    shell: 'mkdir -p {output} && unzip -o -d {output} {params.archive} &> {log}'
