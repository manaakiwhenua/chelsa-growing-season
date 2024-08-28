install.packages("devtools")
install.packages("dplyr")
devtools::install_github("alpha-beta-soup/clifro@dates-debug", force=TRUE)
install.packages("lubridate")

library(lubridate)
library(dplyr)

richard.cfuser = clifro::cf_user(
  username="lawr@landcareresearch.co.nz",
  password="**********"
)

regions = c('Kaitaia','Whangarei','Auckland','Tauranga','Rotorua','Taupo','Hamilton','New Plymouth','Masterton','Gisborne','Napier','Palmerston North','Wellington','Wanganui','Westport','Hokitika','Milford Sound','Nelson','Blenheim','Kaikoura','Mt Cook','Christchurch','Lake Tekapo','Timaru','Dunedin','Manapouri','Queenstown','Alexandra','Invercargill')
# Subsets used for A-C chunks:
# regions = c('Kaitaia','Whangarei','Auckland','Tauranga','Rotorua','Taupo','Hamilton','New Plymouth','Masterton','Gisborne','Napier','Palmerston North','Wellington','Wanganui','Westport','Hokitika')
# regions = c('Milford Sound','Nelson','Blenheim','Kaikoura','Mt Cook','Christchurch','Lake Tekapo','Timaru','Dunedin','Manapouri')
# regions = c('Queenstown','Alexandra','Invercargill')

station_file <- "/home/users/lawr/Downloads/all_cf_stations.csv"
temperature_file <- "/home/users/lawr/Downloads/all_cf_data.csv"

# cf. https://cliflo.niwa.co.nz/pls/niwp/wgenf.choose_datatype?cat=cat1&sub1=temp
temp.dt = clifro::cf_datatype(4, 2, 1)

all_cf_data <- data.frame()
all_cf_stations <- data.frame()

start_year <- 1996
end_year <- 2023

for (region in regions) {
  temp.dt.stations = clifro::cf_find_station(
    region,
    search="region",
    status="all",
    datatype=temp.dt
  )
  cf_stations <- dplyr::as_data_frame(temp.dt.stations[, c("name", "network", "agent", "start", "end", "open", "lat", "lon")])
  all_cf_stations <- dplyr::bind_rows(all_cf_stations, cf_stations)
  for (year in start_year:end_year) {
    for (month in 1:12) {
      start_date <- paste0(year, "-", sprintf("%02d", month), "-01 00")
      end_date <- sprintf("%d-%02d-%02d 23", year, month, as.integer(format(as.Date(paste0(year, "-", month, "-01")) + months(1) - lubridate::days(1), "%d")))      
      
      cf_data <- tryCatch({
        # Attempt to query the data
        cf_data <- clifro::cf_query(
          user = richard.cfuser, 
          datatype = temp.dt, 
          station = temp.dt.stations, 
          start_date = start_date,
          end_date = end_date
        )
        
        # Check if the result is empty
        if (nrow(cf_data) == 0) {
          stop("Empty data returned")
        }
        
        # Convert to data frame and select relevant columns
        cf_data <- dplyr::as_data_frame(cf_data[, c("Station", "Date.local", "Tmax.C", "Tmin.C", "Tgmin.C")])
        cf_data$Date.local <- as.Date(cf_data$Date.local)
        
        # Return the processed data
        cf_data
        
      }, error = function(e) {
        # Handle the error by printing a message and returning NULL
        message(paste("Error in region:", region, "year:", year, "month:", month, "-", e$message))
        return(NULL)
      })
      
      # Only bind the data if cf_data is not NULL
      if (!is.null(cf_data)) {
        all_cf_data <- dplyr::bind_rows(all_cf_data, cf_data)
      }
    }
  }
}

write.csv(all_cf_stations, station_file)
write.csv(all_cf_data, temperature_file)
