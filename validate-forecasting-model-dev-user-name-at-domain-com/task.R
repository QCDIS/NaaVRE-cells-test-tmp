setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)
if (!requireNamespace("dplyr", quietly = TRUE)) {
	install.packages("dplyr", repos="http://cran.us.r-project.org")
}
library(dplyr)
if (!requireNamespace("ggpubr", quietly = TRUE)) {
	install.packages("ggpubr", repos="http://cran.us.r-project.org")
}
library(ggpubr)
if (!requireNamespace("lubridate", quietly = TRUE)) {
	install.packages("lubridate", repos="http://cran.us.r-project.org")
}
library(lubridate)
if (!requireNamespace("purrr", quietly = TRUE)) {
	install.packages("purrr", repos="http://cran.us.r-project.org")
}
library(purrr)
if (!requireNamespace("stringr", quietly = TRUE)) {
	install.packages("stringr", repos="http://cran.us.r-project.org")
}
library(stringr)
if (!requireNamespace("tidyr", quietly = TRUE)) {
	install.packages("tidyr", repos="http://cran.us.r-project.org")
}
library(tidyr)


option_list = list(

make_option(c("--budburst_climwin_input_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--firstWindow_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--scenario_data_all_file"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--temp_climwin_input_file"), action="store", default=NA, type="character", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


budburst_climwin_input_file <- gsub('"', '', opt$budburst_climwin_input_file)
firstWindow_file <- gsub('"', '', opt$firstWindow_file)
id <- gsub('"', '', opt$id)
scenario_data_all_file <- gsub('"', '', opt$scenario_data_all_file)
temp_climwin_input_file <- gsub('"', '', opt$temp_climwin_input_file)






temp <- read.csv(temp_climwin_input_file)
avg_annual_budburst_dates <- read.csv(budburst_climwin_input_file)
climwin_QRobur <- load(firstWindow_file)
scenario_data_all <- read.csv(scenario_data_all_file)

scenario_data_all <- scenario_data_all %>%
  dplyr::filter(!(scenario_name %in% c("1pt5degC") & member_id %in% c("006", "007", "009", "010")))


set.seed(2804)

scenario_colours <- c("measured" = "#D53E4F", "RCP45" = "#B9A6E2" , "1pt5degC_OS" = "#FFD560",
                      "2pt0degC" = "#48d3d3", "RCP85" = "#FC8D59", "1pt5degC" = "#3288BD")




model_validation <- function(measured_temperatures,
                             climwin_output,
                             biological_data,
                             use_zScores = c("yes", "no"),
                             number_simulations,
                             scenario_data,
                             scenario = c("1pt5degC, 1pt5degC_OS, 2pt0degC, RCP85, RCP45")) {


  measured_temp <- measured_temperatures %>%
    dplyr::mutate(date = lubridate::as_date(date),
                  year = lubridate::year(date),
                  month = lubridate::month(date),
                  day = lubridate::day(date),
                  doy = lubridate::yday(date),
                  dummy = month * 100 + day) %>%
    dplyr::filter(dummy > (lubridate::month(climwin_output$start_date) * 100 + lubridate::day(climwin_output$start_date)) &
                    dummy < (lubridate::month(climwin_output$end_date) * 100 + lubridate::day(climwin_output$end_date))) %>%
    dplyr::summarise("mean_temperature" = mean(temperature),
                     "sd_KNMI_temp" = sd(temperature, na.rm = TRUE),
                     .by = "year") %>%
    dplyr::mutate(overall_mean = mean(mean_temperature),
                  overall_sd = sd(mean_temperature),
                  type = "measured",
                  scenario = NA,
                  run = NA,
                  zScore = (mean_temperature - overall_mean) / overall_sd) %>%
    dplyr::select(!c("overall_mean", "overall_sd"))



  df <- scenario_data %>%
    dplyr::filter(scenario_name == scenario)

  scenario_temp_fut <- NULL
  scenario_temp_hist <- NULL

  for (a in unique(df$member_id)) {

    scenario_temp <- df %>%
      dplyr::filter(member_id == a) %>%
      dplyr::mutate(date = lubridate::as_date(time),
                    year = lubridate::year(date),
                    dummy = lubridate::month(date) * 100 + lubridate::day(date),
                    doy = lubridate::yday(date),
                    temp_degreesC = as.numeric(TREFHT) - 273.15) %>%
      dplyr::filter(dummy > (lubridate::month(climwin_output$start_date) * 100 + lubridate::day(climwin_output$start_date)) &
                      dummy < (lubridate::month(climwin_output$end_date) * 100 + lubridate::day(climwin_output$end_date))) %>%

      dplyr::mutate("mean_temperature" = mean(temp_degreesC, na.rm = TRUE),
                    "sd_temperature" = sd(temp_degreesC, na.rm = TRUE),
                    .by = "year") %>%
      dplyr::mutate(type = "model",
                    run = a)

    scenario_temp_hist_perRun <- scenario_temp %>%
      dplyr::filter(year >= min(biological_data$year), year <= max(biological_data$year)) %>%
      dplyr::mutate(overall_mean_hist = mean(mean_temperature),
                    overall_sd_hist = sd(mean_temperature),
                    zScore = (mean_temperature - overall_mean_hist) / overall_sd_hist)

    overall_mean_hist <- unique(scenario_temp_hist_perRun$overall_mean_hist)

    scenario_temp_hist <- rbind(scenario_temp_hist, scenario_temp_hist_perRun)

    scenario_temp_fut_perRun <- scenario_temp %>%
      dplyr::filter(year > max(biological_data$year)) %>%
      dplyr::mutate(overall_mean_fut = mean(mean_temperature),
                    overall_sd_fut = sd(mean_temperature),
                    zScore = (mean_temperature - overall_mean_hist) / overall_sd_fut)

    scenario_temp_fut <- rbind(scenario_temp_fut, scenario_temp_fut_perRun)

  }


  avg_budburst <- biological_data  %>%
    dplyr::mutate(year = as.numeric(year)) %>%
    dplyr::summarise(avg_budburst_DOY_allLoc = mean(avg_bud_burst_DOY, na.rm = TRUE),
                     .by = "year")

  budburst_temp <- measured_temp %>%
    dplyr::left_join(avg_budburst, by = "year")



  m1 <- lm(avg_budburst_DOY_allLoc ~ year, data = budburst_temp)
  slope_bb_year <- m1$coefficients[2]


  if(!(use_zScores == "yes")) {

    model_for_prediction <- lm(avg_budburst_DOY_allLoc ~ mean_temperature, data = budburst_temp)

    intercept_bb_temp <- as.numeric(model_for_prediction$coefficients[1])
    slope_bb_temp <- as.numeric(model_for_prediction$coefficients[2])
    sigma_bb_temp <- sigma(model_for_prediction)
    model_coefficients_bb_temp <- model_for_prediction$coefficients
    vcov_bb_temp <- vcov(model_for_prediction)

    sim_measured_slope_pred_year <- NULL

    for (s in 1:number_simulations) {

      new_data <- data.frame(mean_temperature = budburst_temp$mean_temperature)

      residual_error <- rnorm(n = nrow(new_data), sd = sigma_bb_temp)
      predicted_bb_date <- intercept_bb_temp + slope_bb_temp * new_data$mean_temperature + residual_error
      predicted_budburst <- data.frame(budburst_temp, predicted_bb_date)

      model_pred_year <- lm(predicted_bb_date ~ year, data = predicted_budburst)
      slope_pred_year <- as.numeric(model_pred_year$coefficients[2])
      df_slope_pred_year <- data.frame(scenario = "measured", run = NA, sim = paste0("sim_", s), slope = slope_pred_year)

      sim_measured_slope_pred_year <- rbind(sim_measured_slope_pred_year, df_slope_pred_year)

    }

    sim_scenario_slope_pred_year <- NULL

    for (s in 1:number_simulations) {

      scenario_slopes_pred_year <- NULL

      for (r in unique(scenario_temp_hist$run)) {

        df <- scenario_temp_hist %>%
          dplyr::filter(run == r)

        new_data <- data.frame(mean_temperature = df$mean_temperature)

        residual_error <- rnorm(n = nrow(new_data), sd = sigma_bb_temp)
        predicted_bb_date <- intercept_bb_temp + slope_bb_temp * new_data$mean_temperature + residual_error
        predicted_budburst <- data.frame(df, predicted_bb_date)

        model_pred_year <- lm(predicted_bb_date ~ year, data = predicted_budburst)
        slope_pred_year <- as.numeric(model_pred_year$coefficients[2])
        df_slope_pred_year <- data.frame(scenario = scenario, run = r, sim = paste0("sim_", 1), slope = slope_pred_year)

        scenario_slopes_pred_year <- rbind(scenario_slopes_pred_year, df_slope_pred_year)
      }

      sim_scenario_slope_pred_year <- rbind(sim_scenario_slope_pred_year, scenario_slopes_pred_year)
    }

    slopes_combined <- rbind(sim_measured_slope_pred_year, sim_scenario_slope_pred_year)

    plot_validation <- ggplot2::ggplot(data = slopes_combined) +
      ggplot2::geom_histogram(mapping = ggplot2::aes(y = ggplot2::after_stat(density),
                                                     x = slope,
                                                     fill = scenario),
                              colour = "black",
                              alpha = 0.7,
                              position = "identity",
                              binwidth = 0.01) +
      ggplot2::scale_fill_manual(values = scenario_colours) +
      ggplot2::geom_vline(xintercept = slope_bb_year,
                          linewidth = 2) +
      ggplot2::theme_classic() +
      ggplot2::labs(x = "Slope (predicted bud burst ~ year)", y = "Density")

    plot_obs_temp <-  ggplot2::ggplot() +
      ggplot2::geom_abline(intercept = intercept_bb_temp,
                           slope = slope_bb_temp,
                           linetype = 1,
                           linewidth = 1,
                           color = "black") +
      ggplot2::geom_point(data = budburst_temp,
                          mapping = ggplot2::aes(x = mean_temperature,
                                                 y = avg_budburst_DOY_allLoc),
                          color = "black", size = 3) +
      ggplot2::ylab("Bud burst date (DOY)") +
      ggplot2::xlab("mean measured temperature") +
      ggplot2::theme_classic()

    return(tibble::lst(budburst_temp,
                       scenario_temp_hist,
                       scenario_temp_fut,
                       model_for_prediction,
                       plot_validation,
                       plot_obs_temp))

  }

  if(use_zScores == "yes") {


    model_for_prediction_zScore <- lm(avg_budburst_DOY_allLoc ~ zScore, data = budburst_temp)

    intercept_bb_temp_zScore <- as.numeric(model_for_prediction_zScore$coefficients[1])
    slope_bb_temp_zScore <- as.numeric(model_for_prediction_zScore$coefficients[2])
    sigma_bb_temp_zScore <- stats::sigma(model_for_prediction_zScore)
    model_coefficients_bb_temp_zScore <- model_for_prediction_zScore$coefficients
    vcov_bb_temp_zScore <- stats::vcov(model_for_prediction_zScore)

    sim_measured_slope_pred_year <- NULL

    for (s in 1:number_simulations) {

      new_data <- data.frame(zScore = budburst_temp$zScore)

      residual_error <- rnorm(n = nrow(new_data), sd = sigma_bb_temp_zScore)
      predicted_bb_date <- intercept_bb_temp_zScore + slope_bb_temp_zScore * new_data$zScore + residual_error
      predicted_budburst <- data.frame(budburst_temp, predicted_bb_date)

      model_pred_year <- lm(predicted_bb_date ~ year, data = predicted_budburst)
      slope_pred_year <- as.numeric(model_pred_year$coefficients[2])
      df_slope_pred_year <- data.frame(scenario = "measured", run = NA, sim = paste0("sim_", s), slope = slope_pred_year)


      sim_measured_slope_pred_year <- rbind(sim_measured_slope_pred_year, df_slope_pred_year)

    }

    sim_scenario_slope_pred_year <- NULL

    for (s in 1:number_simulations) {

      scenario_slopes_pred_year <- NULL

      for (r in unique(scenario_temp_hist$run)) {

        df <- scenario_temp_hist %>%
          dplyr::filter(run == r)

        new_data <- data.frame(zScore = df$zScore)

        residual_error <- rnorm(n = nrow(new_data), sd = sigma_bb_temp_zScore)
        predicted_bb_date <- intercept_bb_temp_zScore + slope_bb_temp_zScore * new_data$zScore + residual_error
        predicted_budburst <- data.frame(df, predicted_bb_date)

        model_pred_year <- lm(predicted_bb_date ~ year, data = predicted_budburst)
        slope_pred_year <- as.numeric(model_pred_year$coefficients[2])
        df_slope_pred_year <- data.frame(scenario = scenario, run = r, sim = paste0("sim_", s), slope = slope_pred_year)

        scenario_slopes_pred_year <- rbind(scenario_slopes_pred_year, df_slope_pred_year)

      }

      sim_scenario_slope_pred_year <- rbind(sim_scenario_slope_pred_year, scenario_slopes_pred_year)

    }

    slopes_combined <- rbind(sim_measured_slope_pred_year, sim_scenario_slope_pred_year)

    plot_validation <- ggplot2::ggplot(data = slopes_combined) +
      ggplot2::geom_histogram(mapping = ggplot2::aes(y = ggplot2::after_stat(density),
                                                     x = slope,
                                                     fill = scenario),
                              colour = "black",
                              alpha = 0.7,
                              position = "identity",
                              binwidth = 0.01) +
      ggplot2::scale_fill_manual(values = scenario_colours) +
      ggplot2::geom_vline(xintercept = slope_bb_year, linewidth = 2) +
      ggplot2::theme_classic() +
      ggplot2::labs(x = "Slope (predicted bud burst ~ year)", y = "Density")


    plot_zScore <-  ggplot2::ggplot() +
      ggplot2::geom_abline(intercept = intercept_bb_temp_zScore,
                           slope = slope_bb_temp_zScore,
                           linetype = 1,
                           linewidth = 1,
                           color = "black") +
      ggplot2::geom_point(data = budburst_temp,
                          mapping = ggplot2::aes(x = zScore,
                                                 y = avg_budburst_DOY_allLoc),
                          color = "black",
                          size = 3) +
      ggplot2::ylab("Bud burst date (DOY)") +
      ggplot2::xlab("zScore measured temperatures") +
      ggplot2::theme_classic()

    return(tibble::lst(budburst_temp,
                       scenario_temp_hist,
                       scenario_temp_fut,
                       model_for_prediction_zScore,
                       plot_validation,
                       plot_zScore))

  }

}


validation_all_zScores <- purrr::map(.x = c("1pt5degC", "1pt5degC_OS", "2pt0degC", "RCP85", "RCP45") %>%
                                       purrr::set_names(),
                                     .f = ~{

                                       output <- model_validation(measured_temperatures = temp,
                                                                  climwin_output = first_window_Qrobur,
                                                                  biological_data = avg_annual_budburst_dates %>%
                                                                    dplyr::filter(stringr::str_detect(scientificName, "Quercus robur")),
                                                                  scenario = .x,
                                                                  scenario_data = scenario_data_all,
                                                                  use_zScores = "yes",
                                                                  number_simulations = 100)

                                       return(output)

                                     },
                                     .progress = TRUE)

validation_all_zScores_file <- "/tmp/data/validation_all_zScores.Rda"
save(validation_all_zScores, file = validation_all_zScores_file)
 
validation_plot_all <- ggpubr::ggarrange(plotlist = purrr::map(.x = validation_all_zScores, "plot_validation"),
                                         nrow = 3, ncol = 2)

validation_plot_all



# capturing outputs
file <- file(paste0('/tmp/validation_all_zScores_file_', id, '.json'))
writeLines(toJSON(validation_all_zScores_file, auto_unbox=TRUE), file)
close(file)
