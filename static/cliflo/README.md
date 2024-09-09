This is data obtained from https://cliflo.niwa.co.nz by Richard Law between 26-28 August 2024.

Data represents records of variables `Tmax.C`, `Tmin.C` and `Tgmin.C` for daily periods from 1996 to 2023.

It cannot be run fully automatically, as Cliflo works on a rolling subscription basis of 2,000,000 rows. After that is exhausted, subscription must be manually renewed (at no cost); this causes a script downloading _all_ the data to fail. The other applicable limit is the maximum number of rows that can be returned in a single query. For this reason, code to download this data requests data gradually in chunks of all stations for each region/year/month.

Code is available in `download.R`, complete excluding my password information.

The total number of rows meant that this script was run three times, with slighlty overlapping ranges. Raw downloaded data is therefore available in chunks a-c, and duplicates should be removed before processing further.

Climate station data (which includes latitude/longitude location information) can be joined to the temperature record by station name.