import dplyr
import geosphere
import lubridate
import stringr
import tidyr

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--budburst_file', action='store', type=str, required=True, dest='budburst_file')

arg_parser.add_argument('--event_file', action='store', type=str, required=True, dest='event_file')

arg_parser.add_argument('--extendedmeasurementorfact_file', action='store', type=str, required=True, dest='extendedmeasurementorfact_file')

arg_parser.add_argument('--occurrence_file', action='store', type=str, required=True, dest='occurrence_file')

arg_parser.add_argument('--temperature_file', action='store', type=str, required=True, dest='temperature_file')


args = arg_parser.parse_args()
print(args)

id = args.id

budburst_file = args.budburst_file.replace('"','')
event_file = args.event_file.replace('"','')
extendedmeasurementorfact_file = args.extendedmeasurementorfact_file.replace('"','')
occurrence_file = args.occurrence_file.replace('"','')
temperature_file = args.temperature_file.replace('"','')





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

import json
filename = "/tmp/budburst_climwin_input_file_" + id + ".json"
file_budburst_climwin_input_file = open(filename, "w")
file_budburst_climwin_input_file.write(json.dumps(budburst_climwin_input_file))
file_budburst_climwin_input_file.close()
filename = "/tmp/temp_climwin_input_file_" + id + ".json"
file_temp_climwin_input_file = open(filename, "w")
file_temp_climwin_input_file.write(json.dumps(temp_climwin_input_file))
file_temp_climwin_input_file.close()
