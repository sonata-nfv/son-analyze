isIntegrationRun <- function() {
  return (Sys.getenv(x = "INTEGRATION_TEST") != "")
}

fetch <- function(fixturePath, query, silent = TRUE) {
  if (isIntegrationRun()) {
    son.analyze::query(query, silent = silent)
  } else {
    path <- paste0('/var/tmp/son.analyze/tests/fixtures/', fixturePath)
    son.analyze::query(file = path, silent = silent)
  }
}

sonQuery <- function(query, past = -1, step = "5s") {
  return(son.analyze::rangeQuery("http://sp.int2.sonata-nfv.eu:9090",
                                 query,
                                 interval = lubridate::as.interval(lubridate::hours(past), lubridate::now()),
                                 step = step))
}
