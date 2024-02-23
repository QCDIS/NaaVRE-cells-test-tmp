import climwin
import dplyr
import lubridate
import stringr

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--budburst_climwin_input_file', action='store', type=str, required=True, dest='budburst_climwin_input_file')

arg_parser.add_argument('--temp_climwin_input_file', action='store', type=str, required=True, dest='temp_climwin_input_file')


args = arg_parser.parse_args()
print(args)

id = args.id

budburst_climwin_input_file = args.budburst_climwin_input_file.replace('"','')
temp_climwin_input_file = args.temp_climwin_input_file.replace('"','')





temp <- read.csv(temp_climwin_input_file)

avg_annual_budburst_dates <- read.csv(budburst_climwin_input_file)




temp <- temp %>%
  dplyr::mutate(date = lubridate::as_date(date),
                year = lubridate::year(date),
                month = lubridate::month(date),
                day = lubridate::day(date),
                doy = lubridate::yday(date),
                dummy = month * 100 + day,
                factor_date = as.factor(paste(day, month, year, sep = "/")))

avg_annual_budburst_dates <- avg_annual_budburst_dates %>%
  dplyr::mutate(date_info = paste(year, floor(avg_bud_burst_DOY)),
                date = strptime(date_info, "%Y %j"),
                date = as.factor(format(as.Date(date), "%d/%m/%Y"))) %>%
  dplyr::mutate(DOY = lubridate::yday(as.Date(avg_bud_burst_date))) |>
  dplyr::filter(!is.na(date), !is.na(locID))







find_climate_window <- function(biological_data = NULL,
                                climate_data,
                                range,
                                reference_day,
                                window_number = c("first", "second"),
                                first_window = NULL) {

  if(window_number == "first") {

    if(is.null(biological_data)) {

      stop("If you want to find a first climate window, provide the biological data as `biological_data`.")

    }

    baseline <- lm(DOY ~ year, data = biological_data)

  } else if(window_number == "second") {

    if(is.null(first_window)) {

      stop("If you want to find a second climate window, provide the output of the first iteration of `find_climate_window()` as `first_window`.")

    }

    biological_data <- first_window$biological_data

    baseline_data <- first_window$best_window[[1]]$BestModelData %>%
      dplyr::rename("first_window" = "climate",
                    "DOY" = "yvar")

    baseline <- lm(DOY ~ year + first_window, data = baseline_data)

  }

  best_window <- climwin::slidingwin(baseline = baseline,
                                     xvar = list(Temp = climate_data$temperature),
                                     cdate = climate_data$factor_date,
                                     bdate = biological_data$date,
                                     type = "absolute",
                                     refday = reference_day,
                                     spatial = list(biological_data$locID, climate_data$locID),
                                     range = range,
                                     func = "lin",
                                     stat = "mean")


  reference_year <- dplyr::if_else(condition = lubridate::leap_year(max(climate_data$year)),
                                   true = max(climate_data$year) - 1,
                                   false = max(climate_data$year))

  start_date <- lubridate::make_date(year = reference_year,
                                     month = reference_day[2],
                                     day = reference_day[1]) - best_window$combos[1,]$WindowOpen

  end_date <- lubridate::make_date(year = reference_year,
                                   month = reference_day[2],
                                   day = reference_day[1]) - best_window$combos[1,]$WindowClose

  return(tibble::lst(best_window, biological_data, baseline, range, reference_day, climate_data, start_date, end_date))

}


first_window_Qrobur <- find_climate_window(biological_data = avg_annual_budburst_dates %>%
                                             dplyr::filter(stringr::str_detect(scientificName, "Quercus robur")),
                                           climate_data = temp,
                                           window_number = "first",
                                           reference_day = c(31, 5),
                                           range = c(181, 0))

first_window_Qrobur$start_date
first_window_Qrobur$end_date

firstWindow_file <- "/tmp/data/climwin_outputs_Qrobur.rda"
save(first_window_Qrobur, file = firstWindow_file)

import json
filename = "/tmp/firstWindow_file_" + id + ".json"
file_firstWindow_file = open(filename, "w")
file_firstWindow_file.write(json.dumps(firstWindow_file))
file_firstWindow_file.close()
