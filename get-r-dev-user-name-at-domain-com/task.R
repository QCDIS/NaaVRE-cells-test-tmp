setwd('/app')

# retrieve input parameters

library(optparse)
library(jsonlite)
if (!requireNamespace("here", quietly = TRUE)) {
	install.packages("here", repos="http://cran.us.r-project.org")
}
library(here)
if (!requireNamespace("pacman", quietly = TRUE)) {
	install.packages("pacman", repos="http://cran.us.r-project.org")
}
library(pacman)


option_list = list(

make_option(c("--a"), action="store", default=NA, type="integer", help="my description"), 
make_option(c("--b"), action="store", default=NA, type="integer", help="my description"), 
make_option(c("--id"), action="store", default=NA, type="character", help="my description"), 
make_option(c("--param_b"), action="store", default=NA, type="integer", help="my description")

)

# set input parameters accordingly
opt = parse_args(OptionParser(option_list=option_list))


a = opt$a
b = opt$b
id <- gsub('"', '', opt$id)

param_b = opt$param_b


conf_a = 1


conf_a = 1
print(a)
print(b)
print(conf_a)
print(param_b)
print(here::here("here"))

my_func <- function(c, d) {
    print(c + d)
}



# capturing outputs
file <- file(paste0('/tmp/my_func_', id, '.json'))
writeLines(toJSON(my_func, auto_unbox=TRUE), file)
close(file)
