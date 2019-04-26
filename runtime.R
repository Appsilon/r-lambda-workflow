output <- tryCatch(
  {
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
      list(out = do.call(function_name, params), quit_status = 0),
      error = function(e) {
        list(out = e$message, quit_status = 100)
      }
    )

    list(out = output$out, quit_status = output$quit_status)
  },
  error = function(e) {
    list(out = e$message, quit_status = 100)
  }
)

output$out
quit(status = output$quit_status)
