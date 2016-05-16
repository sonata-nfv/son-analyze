#' A client to the Prometheus Api
#' @name prometheus
NULL


#' Create a query on an time instant
#'
#' @param endpoint A url to the Prometheus Api
#' @param query A Prometheus query
#' @param time A lubridate instant time
#' @return A list containing all the information for a http request
#' @export
instantQuery <- function (endpoint, query, time) {
  params <- list(query = query, time = as.double(lubridate::with_tz(time, "UTC")))
  return(list(url = endpoint, path = "api/v1/query", params = params))
}


#' Create a query on an time interval
#'
#' @param endpoint A url to the Prometheus Api
#' @param query A Prometheus query
#' @param interval A lubridate interval (Prometheus works with the UTC timezone)
#' @param step the Prometheus sampling step
#' @return A list containing all the information for a http request
#' @examples
#' rangeQuery("http://localhost:9090", "container_cpu_usage_seconds_total{id=~'/docker/1234'}",
#'            interval = lubridate::as.interval(lubridate::hours(-1), lubridate::now()),
#'            step = "5s")
#' @export
rangeQuery <- function (endpoint, query, interval, step="30s") {
  interval <- lubridate::int_standardize(interval)
  start <- as.double(lubridate::with_tz(lubridate::int_start(interval), "UTC"))
  end <- as.double(lubridate::with_tz(lubridate::int_end(interval), "UTC"))
  params <- list(query = query, start = start, end = end, step = step)
  return(list(url = endpoint, path = "api/v1/query_range", params = params))
}


#' Run a query to the Prometheus Api
#'
#' @param url A list containing the GET parameters
#' @return a list of named lists \code{l}, each element is a hit returned by Prometheus.
#'   \code{l[[1]]$metricName}: the name of the queried metric
#'   \code{l[[1]]$id}: the value of the id label (NULL if not present)
#'   \code{l[[1]]$labels}: a named list containing the raw labels (minus \code{__name__}
#'     and \code{id})
#'   \code{l[[1]]$df}: a data frame containing the timestamps and the corresponding metric values
#' @examples
#' \dontrun{
#' r <- query(rangeQuery("http://172.17.0.5:9090",
#'                       "container_cpu_usage_seconds_total{id=~'/docker/1234'}",
#'                       interval = lubridate::as.interval(lubridate::hours(-1), lubridate::now()),
#'                       step = "5s"))
#' with(r[[1]], {
#'   x <- xts::xts(df$Value, order.by = df$Timestamp)
#'   plot(x, main = "")
#'   title(main = metricName, sub = id)
#' })
#' }
#' ## End(Not run)
#' @export
query <- function (url) {
  buildDf <- function (timestamp, value, deltaInSeconds) {
    return(data.frame(Timestamp = timestamp, Value = value, DeltaInSeconds = deltaInSeconds))
  }
  headers <- httr::add_headers(Accept = "application/json", `Accept-Charset` = "UTF-8")
  resp <- httr::GET(url$url, headers, path = url$path, query = url$params)
  rawJson <- httr::content(resp, as = "text", encoding = "UTF-8")
  j <- rjson::fromJSON(rawJson)
  if (j$status != "success") {
    warning(paste0("The GET request to Prometheus failed with the message: ", rawJson, " ."))
    return(buildDf(c(), c(), c()))
  }
  if (length(j$data$result) == 0) {
    warning("The GET request to Prometheus returned an empty result")
    return(buildDf(c(), c(), c()))
  }
  trans <- function(elt) {
    labels <- elt$metric[-c(match("__name__", names(elt$metric)), match("id", names(elt$metric)))]
    rawTime <- as.POSIXct(sapply(elt$values, function(x) { return(unlist(x[1])) }),
                          tz="UTC", origin="1970-01-01")
    metric <- as.double(sapply(elt$values, function(x) { return(unlist(x[2])) }))
    deltaInSeconds <- diff(as.double(rawTime))
    return(list(metricName = elt$metric[["__name__"]], id = elt$metric$id,
                labels = labels,
                df = buildDf(rawTime, metric, c(0, deltaInSeconds))))
  }
  return(lapply(j$data$result, trans))
}


#' Filter result from Prometheus by a label
#'
#' @param l A list resulting from a query to Prometheus
#' @param labelName A \code{character}
#' @param regex A \code{character}
#' @return A list containing the elements from \code{l} that contain the label \code{labelName} matching the regexp \code{regex}
#' @examples
#' \dontrun{
#' filterByLabel(r, "cpu", "^cpu")
#' }
#' @export
filterByLabel <- function(l, labelName, regex) {
  someFilter <- function(elt) {
    return(grep(regex, elt$labels[labelName]))
  }
  return(Filter(someFilter, l))
}
