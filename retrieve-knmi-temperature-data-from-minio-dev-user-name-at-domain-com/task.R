setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)
if (!requireNamespace("aws.s3", quietly = TRUE)) {
	install.packages("aws.s3", repos="http://cran.us.r-project.org")
}
library(aws.s3)


option_list = list(

make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--param_s3_access_key_id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--param_s3_endpoint"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--param_s3_prefix"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--param_s3_secret_access_key"), action="store", default=NA, type="character", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


id <- gsub('"', '', opt$id)

param_s3_access_key_id = opt$param_s3_access_key_id
param_s3_endpoint = opt$param_s3_endpoint
param_s3_prefix = opt$param_s3_prefix
param_s3_secret_access_key = opt$param_s3_secret_access_key





dir.create("/tmp/data")

Sys.setenv(
    "AWS_ACCESS_KEY_ID" = param_s3_access_key_id,
    "AWS_SECRET_ACCESS_KEY" = param_s3_secret_access_key,
    "AWS_S3_ENDPOINT" = param_s3_endpoint
    )

temperature_file <- "/tmp/data/Tg1_seasonalTemperature_Dec1987_to_June2023.csv"
save_object(region="", bucket="naa-vre-user-data", object=paste0(param_s3_prefix, "/vl-veluwe-proto-dt/knmi_temperature_data/Tg1_seasonalTemperature_Dec1987_to_June2023.csv"), file=temperature_file)



# capturing outputs
file <- file(paste0('/tmp/temperature_file_', id, '.json'))
writeLines(toJSON(temperature_file, auto_unbox=TRUE), file)
close(file)
