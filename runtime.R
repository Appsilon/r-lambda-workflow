library(jsonlite)

HANDLER <- Sys.getenv("_HANDLER")
args <- commandArgs(trailingOnly = TRUE)
EVENT_DATA <- args[1]

HANDLER_split <- strsplit(HANDLER, ".", fixed = TRUE)[[1]]
file_name <- paste0(HANDLER_split[1], ".R")
function_name <- HANDLER_split[2]
source(file_name)
params <- fromJSON(EVENT_DATA)
output <- tryCatch(
  list(result = do.call(function_name, params)),
  error = function(e) {
    list(error = e$message)
  }
)

toJSON(output)
