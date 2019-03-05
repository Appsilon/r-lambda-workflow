library(jsonlite)

HANDLER <- Sys.getenv("_HANDLER")
args = commandArgs(trailingOnly = TRUE)
EVENT_DATA <- args[1]

HANDLER_split <- strsplit(HANDLER, ".", fixed = TRUE)[[1]]
file_name <- paste0(HANDLER_split[1], ".r")
function_name <- HANDLER_split[2]
source(file_name)
params <- fromJSON(EVENT_DATA)
toJSON(do.call(function_name, params))
