setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)
if (!requireNamespace("dplyr", quietly = TRUE)) {
	install.packages("dplyr", repos="http://cran.us.r-project.org")
}
library(dplyr)
if (!requireNamespace("here", quietly = TRUE)) {
	install.packages("here", repos="http://cran.us.r-project.org")
}
library(here)
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

make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--validation_all_zScores_file"), action="store", default=NA, type="character", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


id <- gsub('"', '', opt$id)
validation_all_zScores_file <- gsub('"', '', opt$validation_all_zScores_file)






load(validation_all_zScores_file)

scenario_colours <- c("measured" = "#D53E4F", "RCP45" = "#B9A6E2" , "1pt5degC_OS" = "#FFD560",
                      "2pt0degC" = "#48d3d3", "RCP85" = "#FC8D59", "1pt5degC" = "#3288BD")



forecasting_budburst <- function(scenario_temp,
                                 linear_model,
                                 use_zScores = c("yes", "no")){

  if(use_zScores == "yes"){

    model_coefficients_bb_temp_zScore <- linear_model$coefficients
    vcov_bb_temp_zScore <- stats::vcov(linear_model)

    forecasted_budburst_perRun <- NULL
    forecasted_budburst_smoothend <- NULL

    for (r in unique(scenario_temp$run)) {

      df <- scenario_temp %>%
        dplyr::filter(run == r)

      X <- stats::model.matrix(~ zScore, data = df)
      predicted <- X %*% model_coefficients_bb_temp_zScore
      varPred <- diag(X %*% vcov_bb_temp_zScore %*% t(X))
      sePred <- sqrt(varPred)

      df1 <- data.frame(df,
                        predicted_bb_date = predicted,
                        varPred = varPred,
                        sePred = sePred)

      df1$Con95Pred <- 1.96 * df1$sePred

      forecasted_budburst_perRun <- rbind(forecasted_budburst_perRun, df1)


      df2 <- df1 %>% dplyr::distinct(year, .keep_all = TRUE)

      forecasted_budburst_smoothend_window <- NULL

      for (s in (min(df2$year) + 5) : (max(df2$year) - 5)) {

        Data_s <- df2 %>% dplyr::filter(year >= (s - 5) & year <= (s + 5))

        Data_new <- data.frame(year = s,
                               scenario_name = unique(df2$scenario_name),
                               run = r,
                               mean_pred_bb_window = mean(Data_s$predicted_bb_date),
                               sd = sd(Data_s$predicted_bb_date),
                               error = (qnorm(0.95) * sd(Data_s$predicted_bb_date))/sqrt(nrow(Data_s)))

        Data_new <- Data_new[stats::complete.cases(Data_new), ]

        forecasted_budburst_smoothend_window <- rbind(forecasted_budburst_smoothend_window, Data_new)
      }

      forecasted_budburst_smoothend <- rbind(forecasted_budburst_smoothend, forecasted_budburst_smoothend_window)
  }

    return(tibble::lst(forecasted_budburst_perRun, forecasted_budburst_smoothend))

  } else {


    model_coefficients_bb_temp <- linear_model$coefficients
    vcov_bb_temp <- stats::vcov(linear_model)

    forecasted_budburst_perRun <- NULL
    forecasted_budburst_smoothend <- NULL

    for (r in unique(scenario_temp$run)) {

      df <- scenario_temp %>%
        dplyr::filter(run == r)

      X <- stats::model.matrix(~ mean_temperature, data = df)
      predicted <- X %*% model_coefficients_bb_temp
      varPred <- diag(X %*% vcov_bb_temp %*% t(X))
      sePred <- sqrt(varPred)

      df1 <- data.frame(df,
                        predicted_bb_date = predicted,
                        varPred = varPred,
                        sePred = sePred)

      df1$Con95Pred <- 1.96 * df1$sePred

      forecasted_budburst_perRun <- rbind(forecasted_budburst_perRun, df1)


      df2 <- df1 %>% dplyr::distinct(year, .keep_all = TRUE)

      forecasted_budburst_smoothend_window <- NULL

      for (s in (min(df2$year) + 5) : (max(df2$year) - 5)) {

        Data_s <- df2 %>% dplyr::filter(year >= (s - 5) & year <= (s + 5))

        Data_new <- data.frame(year = s,
                               scenario_name = unique(df2$scenario_name),
                               run = r,
                               mean_pred_bb_window = mean(Data_s$predicted_bb_date),
                               sd = sd(Data_s$predicted_bb_date),
                               error = (qnorm(0.95) * sd(Data_s$predicted_bb_date))/sqrt(nrow(Data_s)))

        Data_new <- Data_new[stats::complete.cases(Data_new), ]

        forecasted_budburst_smoothend_window <- rbind(forecasted_budburst_smoothend_window, Data_new)
      }

      forecasted_budburst_smoothend <- rbind(forecasted_budburst_smoothend, forecasted_budburst_smoothend_window)
    }

    return(tibble::lst(forecasted_budburst_perRun, forecasted_budburst_smoothend))

  }

}



future_budburst_zScores <- purrr::map(.x = validation_all_zScores,
                                      .f = ~{

                                        output <- forecasting_budburst(scenario_temp = .x$scenario_temp_fut,
                                                                       linear_model = .x$model_for_prediction,
                                                                       use_zScores = "yes")

                                        return(output)

                                      },
                                      .progress = TRUE)

forecasting_all <- purrr::map(.x = future_budburst_zScores,
                              "forecasted_budburst_smoothend") |>
  dplyr::bind_rows()

forecasting_plot <- forecasting_all %>%
  dplyr::group_by(year, scenario_name) %>%
  dplyr::summarise(mean = mean(mean_pred_bb_window, na.rm = TRUE),
                   sd = sd(mean_pred_bb_window, na.rm = TRUE),
                   error = (qnorm(0.95) * sd)/sqrt(n()),
                   CI_lower = mean - error,
                   CI_upper = mean + error) %>%
  ggplot2::ggplot() +
  ggplot2::geom_line(mapping = ggplot2::aes(y = mean,
                                            x = year,
                                            colour = scenario_name),
                     linewidth = 2) +
  ggplot2::geom_ribbon(mapping = ggplot2::aes(x = year,
                                              ymin = CI_lower,
                                              ymax = CI_upper,
                                              fill = scenario_name),
                       alpha = 0.1) +
  ggplot2::scale_color_manual(values = scenario_colours) +
  ggplot2::scale_fill_manual(values = scenario_colours) +
  ggplot2::theme_classic() +
  ggplot2::labs(x = "Year",
                y = "Predicted bud burst date (mean over scenario runs)",
                title = "Predicted bud burst dates of the future",
                colour = "Scenario",
                fill = "Scenario") +
  ggplot2::theme(legend.position = "bottom")

forecasting_plot



