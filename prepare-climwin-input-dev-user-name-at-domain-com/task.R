setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)
if (!requireNamespace("dplyr", quietly = TRUE)) {
	install.packages("dplyr", repos="http://cran.us.r-project.org")
}
library(dplyr)
if (!requireNamespace("geosphere", quietly = TRUE)) {
	install.packages("geosphere", repos="http://cran.us.r-project.org")
}
library(geosphere)
if (!requireNamespace("lubridate", quietly = TRUE)) {
	install.packages("lubridate", repos="http://cran.us.r-project.org")
}
library(lubridate)
if (!requireNamespace("stringr", quietly = TRUE)) {
	install.packages("stringr", repos="http://cran.us.r-project.org")
}
library(stringr)
if (!requireNamespace("tidyr", quietly = TRUE)) {
	install.packages("tidyr", repos="http://cran.us.r-project.org")
}
library(tidyr)


option_list = list(

make_option(c("--budburst_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--event_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--extendedmeasurementorfact_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--occurrence_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--temperature_file"), action="store", default=NA, type="character", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


budburst_file <- gsub('"', '', opt$budburst_file)
event_file <- gsub('"', '', opt$event_file)
extendedmeasurementorfact_file <- gsub('"', '', opt$extendedmeasurementorfact_file)
id <- gsub('"', '', opt$id)
occurrence_file <- gsub('"', '', opt$occurrence_file)
temperature_file <- gsub('"', '', opt$temperature_file)







event <- read.csv(event_file)
occ <- read.csv(occurrence_file)
mof <- read.csv(extendedmeasurementorfact_file)

bud_burst_dates <- read.csv(budburst_file)

temp <- read.csv(temperature_file) %>%
  dplyr::rename("Longitude" = "x",
                "Latitude" = "y")




budburst <- dplyr::right_join(occ %>%
                                dplyr::select("eventID", "organismID", "scientificName"),
                              event, by = "eventID", relationship = "many-to-many") %>%
  dplyr::right_join(bud_burst_dates, by = c("year", "scientificName", "organismID", "verbatimLocality")) %>%
  dplyr::filter(verbatimLocality == "Hoge Veluwe")

lon_lat_temp <- temp %>%
  dplyr::distinct(Longitude, Latitude)

trees <- budburst %>%
  dplyr::distinct(organismID, .keep_all = TRUE) %>%
  dplyr::filter(!is.na(decimalLongitude))

tree_coords <- trees %>%
  dplyr::select("decimalLongitude", "decimalLatitude")



distance <- as.data.frame(geosphere::distm(tree_coords, lon_lat_temp))

distance$minPos <- apply(distance, 1, which.min)

lon_lat_temp$Pos <- 1:nrow(lon_lat_temp)

budburst1 <- dplyr::left_join(distance, lon_lat_temp, by = c("minPos" = "Pos")) %>%
  dplyr::select("tempLon" = "Longitude",
                "tempLat" = "Latitude") %>%
  dplyr::bind_cols(trees, .) %>%
  dplyr::select("organismID", "tempLon", "tempLat") %>%
  dplyr::right_join(budburst, by = "organismID")



temp_locations <- budburst1 %>%
  dplyr::distinct(tempLon, tempLat) %>%
  tidyr::drop_na() %>%
  dplyr::mutate(locID = paste0("loc", 1:dplyr::n()))

temp <-
  temp %>%
  dplyr::left_join(temp_locations, by = c("Latitude" = "tempLat",
                                          "Longitude" = "tempLon"))


avg_annual_budburst_dates <-
  budburst1 %>%
  dplyr::left_join(temp_locations, by = c("tempLat", "tempLon")) %>%
  dplyr::summarise(avg_bud_burst_DOY = mean(bud_burst_DOY, na.rm = TRUE),
                   .by = c("locID", "year", "scientificName")) %>%
  dplyr::mutate(avg_bud_burst_date = avg_bud_burst_DOY + lubridate::make_date(year, 1, 1) - 1)


budburst_climwin_input_file <- "/tmp/data/budburst_climwin_input.csv"
write.csv(avg_annual_budburst_dates, file = budburst_climwin_input_file,
          row.names = FALSE)

temp_climwin_input_file <- "/tmp/data/temp_climwin_input.csv"
write.csv(temp, file = temp_climwin_input_file,
          row.names = FALSE)



# capturing outputs
file <- file(paste0('/tmp/budburst_climwin_input_file_', id, '.json'))
writeLines(toJSON(budburst_climwin_input_file, auto_unbox=TRUE), file)
close(file)
file <- file(paste0('/tmp/temp_climwin_input_file_', id, '.json'))
writeLines(toJSON(temp_climwin_input_file, auto_unbox=TRUE), file)
close(file)
