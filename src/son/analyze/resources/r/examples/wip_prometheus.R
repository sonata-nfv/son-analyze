encodeDate <- function(elt) {
  s <- elt
  if (typeof(elt) != "character") {
    s <- as.character(as.double(elt))
  }
  return(URLencode(s))
}

InstantQuery <- function (endpoint, query, time) {
  params <- paste0("query=", URLencode(query), "&time=", encodeDate(time))
  query <- paste0(endpoint, "/api/v1/query?", params)
  return (query)
}

RangeQuery <- function (endpoint, query, interval, step="30s") {
  interval <- lubridate::int_standardize(interval)
  start <- lubridate::int_start(interval)
  end <- lubridate::int_end(interval)
  params <- paste0("query=", URLencode(query), "&start=", encodeDate(start),
                   "&end=", encodeDate(end), "&step=", URLencode(step))
  query <- paste0(endpoint, "/api/v1/query_range?", params)
  return (query)
}

query <- function (url) {
  print(url)
  resp = httr::GET(url, httr::add_headers(Accept = "application/json", `Accept-Charset` = "UTF-8"))
  t <- httr::content(resp, as = "text", encoding = "UTF-8")
  j <- rjson::fromJSON(t)
  # return (j)
  rawTime <- as.POSIXct(sapply(j$data$result[[1]]$values,
                               function(x) { return(unlist(x[1])) }),
                        tz="UTC", origin="1970-01-01")
  metric <- as.double(sapply(j$data$result[[1]]$values, function(x) { return(unlist(x[2])) }))
  # return(xts::xts(df, order.by=rawTime))
  df <- data.frame(Timestamp = rawTime, Cpu = metric, Other = replicate(length(rawTime), "toto"))
  return(som::normalize(df, byrow = FALSE))
}


r <- query(RangeQuery("http://172.17.0.5:9090", "container_cpu_user_seconds_total{image='son-analyze:latest'}",
                      interval = lubridate::as.interval(lubridate::hours(-1), lubridate::now(tzone = "UTC")),
                      step = "10s"))
# r <- query(RangeQuery("http://172.17.0.5:9090", "container_cpu_user_seconds_total{image='son-analyze:latest'}",
#                       interval = lubridate::interval(as.POSIXct(1460712195.21918, tz = "UTC", origin = "1970-01-01"),
#                                                      as.POSIXct(1460712922.91521, tz = "UTC", origin = "1970-01-01")),
#                       step = "10s"))

# rawTime <- as.POSIXct(sapply(r$data$result[[1]]$values, function(x) { unlist(x[1]) }), tz="UTC", origin="1970-01-01")
# metric <- sapply(r$data$result[[1]]$values, function(x) { return(unlist(x[2])) })
# qxts <- xts::xts(metric, order.by=rawTime)

plot(xts::xts(r$Cpu, order.by=r$Timestamp))
