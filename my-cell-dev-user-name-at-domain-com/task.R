setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)


option_list = list(

make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--my_input"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--my_other_input"), action="store", default=NA, type="integer", help="my description"), 
make_option(c("--param_something"), action="store", default=NA, type="character", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


id <- gsub('"', '', opt$id)
my_input <- gsub('"', '', opt$my_input)
my_other_input = opt$my_other_input

param_something = opt$param_something


conf_something_else = 'my other value'


conf_something_else = 'my other value'
print('Hello')



# capturing outputs
file <- file(paste0('/tmp/my_output_', id, '.json'))
writeLines(toJSON(my_output, auto_unbox=TRUE), file)
close(file)
