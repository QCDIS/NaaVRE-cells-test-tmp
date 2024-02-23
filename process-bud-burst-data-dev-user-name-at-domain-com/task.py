import dplyr
import lubridate
import stringr

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--event_file', action='store', type=str, required=True, dest='event_file')

arg_parser.add_argument('--extendedmeasurementorfact_file', action='store', type=str, required=True, dest='extendedmeasurementorfact_file')

arg_parser.add_argument('--occurrence_file', action='store', type=str, required=True, dest='occurrence_file')


args = arg_parser.parse_args()
print(args)

id = args.id

event_file = args.event_file.replace('"','')
extendedmeasurementorfact_file = args.extendedmeasurementorfact_file.replace('"','')
occurrence_file = args.occurrence_file.replace('"','')






event <- read.csv(event_file)
occ <- read.csv(occurrence_file)
mof <- read.csv(extendedmeasurementorfact_file)

d_bb <- dplyr::left_join(event, mof, by = "eventID")

d_bb <-
  occ %>%
  dplyr::select("eventID", "organismID", "scientificName") %>%
  dplyr::right_join(d_bb, by = "eventID", relationship = "many-to-many")



crit_measType <- "bud burst stage (PO:0025532) of the tree crown"

crit_measValue <- 1



d_bb_crown <-
  d_bb %>%
  dplyr::filter(measurementType == crit_measType) %>%
  dplyr::mutate(DOY = lubridate::yday(eventDate))

min_bb <- d_bb_crown %>%
  dplyr::filter(measurementValue >= crit_measValue) %>%
  dplyr::summarise(min_DOY_above_criterion = min(DOY),
                   min_value = measurementValue[DOY == min_DOY_above_criterion],
                   .by = c("year", "organismID"))

d_bb_crown2 <- dplyr::left_join(d_bb_crown,
                                min_bb,
                                by = c("year", "organismID"))

max_bb <- d_bb_crown2 %>%
  dplyr::filter(measurementValue < crit_measValue & DOY < min_DOY_above_criterion,
                .by = c("year", "organismID")) %>%
  dplyr::summarise(max_DOY_below_criterion = max(DOY),
                   max_value = measurementValue[DOY == max_DOY_below_criterion],
                   .by = c("year", "organismID"))

min_max_bb <- dplyr::left_join(min_bb,
                               max_bb,
                               by = c("year", "organismID"))


match_criterion <- min_max_bb %>%
  dplyr::filter(min_value == crit_measValue) %>%
  dplyr::mutate(bud_burst_date = min_DOY_above_criterion + lubridate::make_date(year, 1, 1) - 1) %>%
  dplyr::rename("bud_burst_DOY" = "min_DOY_above_criterion")

interpolated <- min_max_bb %>%
  dplyr::filter(min_value != crit_measValue) %>%
  dplyr::mutate(diff_date = min_DOY_above_criterion - max_DOY_below_criterion,
                diff_value = min_value - max_value,
                value_per_day = diff_value / diff_date,
                days_to_reach_criterion = (crit_measValue - max_value) / value_per_day,
                interpolated_DOY = max_DOY_below_criterion + days_to_reach_criterion,
                interpolated_value  = max_value + days_to_reach_criterion * value_per_day) %>%
  dplyr::mutate(bud_burst_date = round(interpolated_DOY) + lubridate::make_date(year, 1, 1) - 1) %>%
  dplyr::rename("bud_burst_DOY" = "interpolated_DOY")

bud_burst_dates <- dplyr::bind_rows(match_criterion %>%
                                      dplyr::select("year", "organismID", "bud_burst_date", "bud_burst_DOY"),
                                    interpolated %>%
                                      dplyr::select("year", "organismID", "bud_burst_date", "bud_burst_DOY")) %>%
  dplyr::left_join(d_bb_crown %>%
                     dplyr::select("year", "organismID", "verbatimLocality", "scientificName") %>%
                     dplyr::distinct(),
                   by = c("year", "organismID")) %>%
  dplyr::arrange(year, organismID)

budburst_file <- "/tmp/data/annual_budburst_per_tree.csv"
write.csv(bud_burst_dates, budburst_file, row.names = FALSE)

import json
filename = "/tmp/budburst_file_" + id + ".json"
file_budburst_file = open(filename, "w")
file_budburst_file.write(json.dumps(budburst_file))
file_budburst_file.close()
