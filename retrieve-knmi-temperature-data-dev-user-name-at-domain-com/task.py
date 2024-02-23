import dplyr
import httr
import jsonlite
import lubridate
import purrr
import readr
import stringr
import tidyr

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_knmi_edr_api_key', action='store', type=str, required=True, dest='param_knmi_edr_api_key')

args = arg_parser.parse_args()
print(args)

id = args.id


param_knmi_edr_api_key = args.param_knmi_edr_api_key



dir.create("/tmp/data")



retrieve_knmi_edr_data <- function(bbox,
                                   variable = c("mean temperature", "max temperature",
                                                "min temperature", "precipitation"),
                                   start_date,
                                   start_time = "00:00:00",
                                   end_date,
                                   end_time = "23:59:59",
                                   knmi_edr_key = param_knmi_edr_api_key) {

  knmi_var_lookup <- tibble::tibble(
    collection = c("Tg1", "Tx1", "Tn1", "Rd1"),
    parameter = c("temperature", "temperature", "temperature", "precipitation"),
    var_name = c("mean temperature", "max temperature", "min temperature", "precipitation")
  )

  if(!(variable %in% knmi_var_lookup$var_name)) {

    stop("The weather variable you provided does not exist. Select one of: 'mean temperature', 'max temperature', 'min temperature', or 'precipitation'.")

  }

  if(!any(class(start_date) == "Date", class(end_date) == "Date")) {

    stop("Please provide dates as 'yyyy-mm-dd'.")

  }

  repeat({ # If retrieving data from KNMI EDR API fails, try again

    edr_get <- httr::GET(url = paste0("https://api.dataplatform.knmi.nl/edr/collections/",
                                      knmi_var_lookup |> dplyr::filter(var_name == variable) |> dplyr::pull("collection"),
                                      "/cube?bbox=", paste(bbox, collapse = "%2C"),
                                      "&z=0",
                                      "&parameter-name=",
                                      knmi_var_lookup |> dplyr::filter(var_name == variable) |> dplyr::pull("parameter"),
                                      "&datetime=",
                                      start_date, "T",
                                      stringr::str_replace_all(string = start_time,
                                                               pattern = ":",
                                                               replacement = "%3A"), "Z%2F",
                                      end_date, "T",
                                      stringr::str_replace_all(string = end_time,
                                                               pattern = ":",
                                                               replacement = "%3A"), "Z"),
                         httr::add_headers(Authorization = knmi_edr_key))

    edr_data <- jsonlite::fromJSON(txt = rawToChar(x = edr_get$content))

    if(is.null(edr_data$domain)) message(paste0("KNMI EDR API failed to fulfill request with starting date ",
                                                start_date, ". Will try again."))

    if(!is.null(edr_data$domain)) break()

  })

  return(edr_data)

}




bbox <- c(5.824436777442551, 52.032393019069225, 5.870356194968013, 52.046647934312794)

temp <- purrr::map(.x = 1988:2023,
                        .f = ~{

                          period1 <- retrieve_knmi_edr_data(bbox = bbox,
                                                            variable = "mean temperature",
                                                            start_date = lubridate::make_date(.x - 1, 12, 1),
                                                            start_time = "00:00:00",
                                                            end_date = lubridate::make_date(.x, 3, 1),
                                                            end_time = "23:59:59")

                          period2 <- retrieve_knmi_edr_data(bbox = bbox,
                                                            variable = "mean temperature",
                                                            start_date = lubridate::make_date(.x, 3, 2),
                                                            start_time = "00:00:00",
                                                            end_date = lubridate::make_date(.x, 5, 31),
                                                            end_time = "23:59:59")

                          data1 <- tidyr::expand_grid(date = period1$domain$axes$t$values,
                                                      y = period1$domain$axes$y$values,
                                                      x = period1$domain$axes$x$values) |>
                            dplyr::mutate(temperature = period1$ranges$temperature$values)

                          data2 <- tidyr::expand_grid(date = period2$domain$axes$t$values,
                                                      y = period2$domain$axes$y$values,
                                                      x = period2$domain$axes$x$values) |>
                            dplyr::mutate(temperature = period2$ranges$temperature$values)

                          data <- dplyr::bind_rows(data1, data2)

                          return(data)

                        },
                        .progress = TRUE) |>
  purrr::list_c()


temperature_file <- "/tmp/data/Tg1_seasonalTemperature_Dec1987_to_June2023.csv"
write.csv(temp, temperature_file, row.names = FALSE)

import json
filename = "/tmp/temperature_file_" + id + ".json"
file_temperature_file = open(filename, "w")
file_temperature_file.write(json.dumps(temperature_file))
file_temperature_file.close()
