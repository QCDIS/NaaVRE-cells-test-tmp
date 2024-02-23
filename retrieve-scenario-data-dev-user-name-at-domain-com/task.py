import dplyr
import httr
import lubridate
import purrr
import readr
import stringr
import tidyr

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')



args = arg_parser.parse_args()
print(args)

id = args.id





dir.create("/tmp/data")

master_branch <- httr::GET("https://api.github.com/repos/matt-long/bio-pop-ToE/git/trees/master?recursive=1")

file_path <- tibble::tibble(path = purrr::map_chr(httr::content(master_branch)$tree, "path")) %>%
  tidyr::separate_wider_delim(path, delim = '/', names = c('base', 'folder', 'filename'),
                              too_few = "align_end", too_many = "drop") %>%
  dplyr::filter(folder == 'data', stringr::str_detect(filename, '.csv'))

scenario_data_all <- tibble::tibble()

for (i in seq(1, nrow(file_path))){

  path <- paste0('https://raw.githubusercontent.com/matt-long/bio-pop-ToE/master/notebooks/data/', file_path$filename[i])

  df <- readr::read_csv(httr::content(httr::GET(path)))

  file_name <- file_path$filename[i]

  df1 <- df %>%
    dplyr::mutate(scenario_name = stringr::str_extract(file_name, pattern = "1pt5degC(?=\\.)|1pt5degC_OS|2pt0degC|RCP85|RCP45"),
                  member_id = as.character(member_id))

  scenario_data_all <- bind_rows(scenario_data_all, df1)

}

scenario_data_all <- scenario_data_all %>%
  dplyr::filter(time >= as.POSIXct("1985-01-01", tz = "UTC"))

scenario_data_all_file <- "/tmp/data/scenario_temperatures.csv"
write.csv(scenario_data_all, file = scenario_data_all_file, row.names = FALSE)

import json
filename = "/tmp/scenario_data_all_file_" + id + ".json"
file_scenario_data_all_file = open(filename, "w")
file_scenario_data_all_file.write(json.dumps(scenario_data_all_file))
file_scenario_data_all_file.close()
